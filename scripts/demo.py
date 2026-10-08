"""End-to-end demonstration of the ADIF pipeline as built so far.

Run from the repository root::

    python -m scripts.demo                      # built-in sample file
    python -m scripts.demo --file my_export.csv # your own manufacturer export

Pipeline exercised: ingestion (M1) → schema analysis (M2) → alias lookup (M3)
→ fuzzy matching (M4) → semantic matching (M5) → cascade arbitration (M7).

**This is a demonstration, not an evaluation.** Two things make it so, and both
are printed in the banner rather than buried here:

*The CDM is a test fixture.* Six invented fields, not the canonical model. The
real CDM is derived from ESPR Annex III, EPCIS 2.0 and UNTP through the
procedure in ``cdm/EXTRACTION.md``, which is not finished.

*The thresholds are invented.* Config ships them as ``null`` on purpose
(decisions.md D11); this script supplies values so the cascade will run at all.
They are not derived from a grid search and no number produced here is a
result.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from src.analyser.profile import analyse_frame
from src.cdm.registry import CdmRegistry
from src.config import AdifConfig, load_config
from src.ingestion.errors import IngestionError
from src.ingestion.loader import load_tabular
from src.matching.arbitration import run_cascade
from src.matching.stage3_semantic import MiniLMEmbedder, SemanticIndex, StubEmbedder
from src.matching.stage4_value import SignatureLibrary

FIXTURE_SCHEMA = "tests/fixtures/cdm_test.schema.json"
FIXTURE_ALIASES = "tests/fixtures/aliases_test.yaml"

# DEMONSTRATION VALUES ONLY. Never copy these into config/default.yaml.
DEMO_FUZZY_THRESHOLD = 85.0
DEMO_SEMANTIC_THRESHOLD = 99.0

SAMPLE = pd.DataFrame(
    {
        "Design_Code": ["TOP-A", "TOP-A"],
        "Style_No": ["0012345678905", "0012345678912"],
        "baseColour": ["Navy", "Red"],
        "SIZE": ["M", "L"],
        "Fabric_Compostion": ["80% Cotton 20% Polyester", "100% Cotton"],
        "origin": ["LK", "LK"],
        "made in": ["Sri Lanka", "Sri Lanka"],
        "internal_ref_zz": ["A1", "A2"],
    }
)


def reject_if_sealed(path: Path, cfg: AdifConfig) -> None:
    """Refuse to read anything inside the sealed evaluation directory.

    The freeze discipline (project.md §11) is only credible if held-out data is
    genuinely untouched during development. A convenience script pointed at it
    by accident is exactly how that gets broken, so the refusal is enforced
    here rather than left to the operator's memory.
    """
    sealed = Path(cfg.paths.heldout_dir).resolve()
    if sealed in path.resolve().parents:
        sys.exit(
            f"REFUSED: '{path}' is inside the sealed evaluation directory "
            f"({sealed}).\nHeld-out schemas are opened by the evaluation "
            f"harness after the freeze commit, never by a demo script."
        )


def build_config(use_real_model: bool) -> AdifConfig:
    cfg = load_config("config/default.yaml")
    cfg.matching.stages.fuzzy.threshold = DEMO_FUZZY_THRESHOLD
    cfg.matching.stages.semantic.threshold = DEMO_SEMANTIC_THRESHOLD
    if not use_real_model:
        cfg.matching.stages.semantic.enabled = True
    return cfg


def main() -> int:
    parser = argparse.ArgumentParser(description="ADIF pipeline demonstration")
    parser.add_argument("--file", type=Path, help="A .csv, .xlsx or flat .json export")
    parser.add_argument(
        "--real-model",
        action="store_true",
        help="Use all-MiniLM-L6-v2 from the local cache instead of the stub embedder",
    )
    args = parser.parse_args()

    cfg = build_config(args.real_model)

    if args.file:
        reject_if_sealed(args.file, cfg)
        try:
            loaded = load_tabular(args.file, cfg)
        except IngestionError as exc:
            print(f"Could not read that file:\n  {exc}")
            return 1
        frame, origin = loaded.frame, str(args.file)
        detail = f"{loaded.source_format}, encoding={loaded.encoding}, delimiter={loaded.delimiter!r}"
    else:
        frame, origin = SAMPLE, "built-in sample"
        detail = "in-memory DataFrame"

    if args.real_model:
        embedder = MiniLMEmbedder(
            cfg.matching.stages.semantic.model,
            str(cfg.paths.embedding_cache),
            cfg.matching.stages.semantic.model_revision,
        )
    else:
        embedder = StubEmbedder()

    registry = CdmRegistry.load(FIXTURE_SCHEMA, FIXTURE_ALIASES, cfg.normalisation)
    analysis = analyse_frame(frame, cfg)
    signatures = (
        SignatureLibrary.load(cfg.matching.stages.value.signatures)
        if cfg.matching.stages.value.enabled
        else None
    )
    result = run_cascade(
        analysis, registry, cfg, SemanticIndex(registry, embedder), signatures
    )

    print("=" * 86)
    print("ADIF pipeline demonstration — NOT AN EVALUATION")
    print(f"  CDM        : {FIXTURE_SCHEMA}  (test fixture, {len(registry.fields)} invented fields)")
    print(f"  Thresholds : fuzzy={DEMO_FUZZY_THRESHOLD} semantic={DEMO_SEMANTIC_THRESHOLD}  (invented, not grid-searched)")
    print(f"  Embedder   : {embedder.name}")
    print(f"  Input      : {origin}  ({detail})")
    print(f"  Rows/cols  : {analysis.row_count} x {analysis.column_count}")
    print("=" * 86)

    print(f"\n{'source column':<24}{'CDM field':<22}{'stage':<10}{'score':>8}  note")
    print("-" * 86)
    for record in result.records:
        note = (
            "CONFLICT — demoted"
            if record.conflict_flagged
            else ("needs review" if record.review_required else "")
        )
        print(
            f"{record.raw_header[:23]:<24}{record.target_field:<22}"
            f"{record.deciding_stage.value:<10}{record.raw_score:>8.1f}  {note}"
        )

    print(f"\nstage hits          : {result.stage_hits}")
    print(f"stage fall-throughs : {result.stage_fallthroughs}")
    print(f"unmapped columns    : {result.unmapped_columns() or 'none'}")
    print(f"mandatory not filled: {result.unpopulated_mandatory(registry) or 'none'}")

    for record in result.records:
        if record.conflict_flagged and record.notes:
            print(f"\nconflict detail     : {record.raw_header} — {record.notes}")

    print(
        "\nAll fourteen modules are implemented. What is still provisional:\n"
        "  - the CDM is a test fixture, not the canonical model\n"
        "  - the embedder is a stub until all-MiniLM-L6-v2 is cached\n"
        "  - no confidence is reported until a calibrator is fitted\n"
        "\nFor validation, ADID identifiers, JSON-LD output and the review UI, "
        "run the API:\n  uvicorn src.api.main:app --reload   "
        "then open http://127.0.0.1:8000/review"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
