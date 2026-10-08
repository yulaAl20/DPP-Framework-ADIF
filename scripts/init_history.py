"""Initialise the repository with a structured, truthful commit history.

    python -m scripts.init_history --dry-run     # show the plan, change nothing
    python -m scripts.init_history

Creates one commit per build increment from project.md §9, in dependency order,
so `git log` reads as the incremental development it was. Commits are dated
**now** — the increments are real, the ordering is real, the dates are real.

Why not backdate: project.md §11 makes the commit history the evidence that the
freeze predates the held-out schemas. That is the mechanism breaking the
circularity of one author writing both the alias vocabulary and the evaluation
data. A forged date forges that proof, and it is the project's strongest
methodological claim. GitHub also records push time separately from commit date,
so the discrepancy is visible to anyone who looks past the contribution graph.

If you need to account for *when* work happened, do it in the dissertation's
build narrative (docs/build_log.md) where it can be stated honestly, not in
metadata that is load-bearing evidence elsewhere.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

#: (increment, message, paths). Order is the §9 dependency order.
PLAN: list[tuple[str, str, list[str]]] = [
    ("B0", "Add project scaffolding, dependency manifests and setup scripts\n\n"
           "Repository layout follows project.md §7. Core and optional\n"
           "dependencies are split so the default install runs the full test\n"
           "suite without the ~2GB PyTorch stack.",
     [".gitignore", ".gitattributes", "README.md", "pyproject.toml",
      "requirements.txt", "requirements-optional.txt", "setup.cmd", "setup.ps1",
      "setup.sh", "docs/setup.md"]),

    ("B1", "B1: config loader, provenance capture and /health\n\n"
           "Every tunable lives in one file (NFR-6). Thresholds are null until\n"
           "derived (decisions.md D11), and reading one raises UnsetTunable\n"
           "rather than defaulting, so the pipeline cannot run on invented\n"
           "numbers. Provenance records artefact hashes for FR-14.5.",
     ["config/default.yaml", "config/ablation", "src/__init__.py",
      "src/config.py", "src/provenance.py", "src/api/__init__.py",
      "tests/__init__.py", "tests/unit/__init__.py", "tests/unit/test_config.py",
      "tests/integration/__init__.py", "tests/acceptance/__init__.py"]),

    ("B1", "B1: enforce the held-out seal as an executable test\n\n"
           "project.md §7 asks for this to be enforced by a test if possible.\n"
           "Greps src/, eval/, ui/ and scripts/ for references to the sealed\n"
           "directory; eval/run_ablation.py is the one documented exemption.",
     ["tests/acceptance/test_freeze_discipline.py"]),

    ("B2", "B2: M1 ingestion and M2 schema analysis\n\n"
           "CSV, Excel and flat JSON, with encoding detection and delimiter\n"
           "sniffing. Everything is read as text: pandas' type inference\n"
           "destroys leading zeros in GTINs and style numbers irreversibly.\n"
           "True headers are recovered before pandas mangles duplicates.",
     ["src/ingestion", "src/analyser", "tests/unit/test_ingestion.py",
      "tests/unit/test_analyser.py"]),

    ("O2", "Derive CDM v1.0 from ESPR Annex III, EPCIS 2.0 and UNTP\n\n"
           "54 fields, each carrying its source clause in x-adif. Annex III ¶1\n"
           "(a)-(k) transcribed verbatim, expanded through Art. 7(5) and\n"
           "Art. 5(1) where point (a) refers out. Alignment table and\n"
           "precedence rules in cdm/ALIGNMENT.md. Objective 2.",
     ["cdm/annex_iii_transcription.csv", "cdm/provenance.csv",
      "cdm/EXTRACTION.md", "cdm/ALIGNMENT.md", "cdm/cdm_v1.0.schema.json",
      "cdm/cdm_v1.0.context.jsonld", "cdm/aliases_v1.0.yaml",
      "scripts/build_cdm_context.py"]),

    ("B3", "B3: M3 alias lookup and M7 cascade arbitration\n\n"
           "Strict fallback cascade with early exit (decisions.md D17). The CDM\n"
           "registry normalises aliases with the same function as headers, since\n"
           "divergence there would stop Stage 1 firing at all and present as an\n"
           "algorithm failure. Colliding aliases are rejected at load.",
     ["src/cdm", "src/matching/__init__.py", "src/matching/models.py",
      "src/matching/stage1_alias.py", "src/matching/arbitration.py",
      "tests/fixtures"]),

    ("B4", "B4: M4 fuzzy and M5 semantic matching\n\n"
           "RapidFuzz with a partial-match length guard: unguarded,\n"
           "partial_ratio scored the alias 'po' at 100 against\n"
           "'fabric compostion', winning the conflict and demoting the correct\n"
           "column. Semantic stage sits behind a protocol so the suite runs\n"
           "offline without the model (NFR-1, NFR-5).",
     ["src/matching/stage2_fuzzy.py", "src/matching/stage3_semantic.py",
      "tests/unit/test_matching.py", "scripts/fetch_model.py"]),

    ("B5", "B5: M7 calibrated confidence\n\n"
           "Per-stage Platt scaling (decisions.md D6). Raw cascade scores live on\n"
           "incommensurable scales - alias is a constant 100, fuzzy an edit ratio,\n"
           "semantic a rescaled cosine - so confidence is learned from data and\n"
           "an unfitted calibrator reports nothing rather than substituting a\n"
           "raw score.",
     ["src/matching/confidence.py"]),

    ("B6", "B6: M10 validation, M11 ADID, M12 JSON-LD\n\n"
           "ADID carries family/variant/instance with the variant as a composite\n"
           "{colour}_{size} segment, resolving the depth collision between\n"
           "methodology.md and project.md FR-13.6-13.8. The family identifier is\n"
           "never derived from a GTIN (D9). The @context is generated from the\n"
           "CDM so it cannot drift.",
     ["adid", "src/identity", "src/validation", "src/serialisation"]),

    ("B7", "B7-B8: M13 REST API and M8 single-file review interface\n\n"
           "Vanilla JS, no build step: an artefact that needs npm and a bundler\n"
           "to open is one an examiner cannot run. Every response carries a\n"
           "warnings field when backed by a fixture CDM or an unfitted\n"
           "calibrator. FR-8.8 counts reviewer edits by kind for the manual-\n"
           "effort metric.",
     ["src/api/main.py", "src/review", "ui", "tests/integration/test_health.py"]),

    ("B9", "B9: M9 template store with drift reporting\n\n"
           "Reuse is measured on a drifted upload, never an identical one\n"
           "(decisions.md D8): deterministic lookup cannot fail on an identical\n"
           "file, so a 100% score there proves nothing. Reused, drifted-missing\n"
           "and new columns are counted separately.",
     ["src/templates"]),

    ("B10", "B10: M14 instrumentation and the evaluation harness\n\n"
            "Four metrics plus MRR, review burden and per-stage cost. Four\n"
            "refusals are built in: the sealed directory, the stub embedder,\n"
            "unearned EVALUATION status, and borrowed calibration curves. Each\n"
            "guards a mistake that would invalidate results silently rather than\n"
            "announcing itself.",
     ["src/instrumentation", "eval", "scripts/perturb_schema.py"]),

    ("B11", "B11: M6 value-based matching, wired into the cascade\n\n"
            "The only stage that can rescue a header carrying no information\n"
            "whose values are diagnostic. Signatures must discriminate, not\n"
            "merely be satisfiable: early drafts matched any number as a carbon\n"
            "footprint and any six hex characters as a colour, the latter\n"
            "stealing the field from a column named colour_name.",
     ["src/matching/stage4_value.py", "cdm/vocabularies"]),

    ("DATA", "Add development schemas derived from open-source ERP field lists\n\n"
             "Headers taken verbatim from ERPNext Item and Odoo product.template,\n"
             "not chosen by the researcher, since the same author wrote the alias\n"
             "vocabulary. Reassigned from held-out to development per\n"
             "decisions.md D23 after signature bugs were found by inspecting\n"
             "their output.",
     ["data/sources", "data/dev"]),

    ("GT", "Add ground-truth rulebook and annotation tooling\n\n"
           "The rulebook compiles the cardinality, distractor and ambiguity\n"
           "rules methodology.md specifies. Worksheets are blank by design: a\n"
           "gold standard written from matcher output records the system's own\n"
           "answer and relabels it truth.",
     ["goldstandard/RULEBOOK.md", "goldstandard/CDM_FIELDS.txt",
      "scripts/make_gold_worksheet.py", "scripts/build_gold_standard.py",
      "scripts/second_rater.py"]),

    ("NFR", "Verify non-functional requirements and record the evidence\n\n"
            "NFR-1 offline (sockets blocked, not merely assumed), NFR-4\n"
            "performance, NFR-5 reproducibility, NFR-6 no magic numbers, NFR-10\n"
            "docstrings. NFR-8 verified on Windows/3.12 and Linux/3.13.\n"
            "Dependency licence inventory for NFR-11.",
     ["tests/acceptance/test_nfr.py", "tests/unit/test_full_pipeline.py",
      "tests/unit/test_evaluation.py", "docs/nfr_verification.md",
      "docs/licences.md"]),

    ("TOOL", "Add demo, environment check and freeze preconditions script\n\n"
             "scripts/freeze.py enforces project.md §11 mechanically rather than\n"
             "by checklist: it refuses to tag while the sealed directory is\n"
             "non-empty, because that ordering cannot be recovered once lost.",
     ["scripts/demo.py", "scripts/check_environment.py", "scripts/freeze.py",
      "scripts/init_history.py", "src/cli.py", "docs"]),
]


def run(args: list[str], dry: bool) -> tuple[int, str]:
    """Run a git command, or print it under --dry-run."""
    if dry:
        print(f"    $ git {' '.join(args)}")
        return 0, ""
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main() -> int:
    """Create the increment commits."""
    parser = argparse.ArgumentParser(description="Initialise a structured commit history")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--author", help='Override author, e.g. "Name <email>"')
    args = parser.parse_args()

    if not Path("requirements.txt").is_file():
        print("Run this from the repository root.", file=sys.stderr)
        return 1

    code, _ = run(["rev-parse", "--git-dir"], dry=False)
    if code != 0:
        print("Initialising repository...")
        run(["init"], args.dry_run)
        run(["branch", "-M", "main"], args.dry_run)
    else:
        code, log = run(["log", "--oneline", "-1"], dry=False)
        if code == 0 and log:
            print(f"This repository already has commits (HEAD: {log}).")
            print("This script is for a fresh repository. Nothing done.")
            return 1

    made = 0
    for increment, message, paths in PLAN:
        existing = [p for p in paths if Path(p).exists()]
        if not existing:
            continue
        run(["add", "--", *existing], args.dry_run)
        if not args.dry_run:
            code, staged = run(["diff", "--cached", "--name-only"], dry=False)
            if not staged:
                continue
        commit = ["commit", "-m", message]
        if args.author:
            commit += ["--author", args.author]
        code, out = run(commit, args.dry_run)
        if code != 0 and not args.dry_run:
            print(f"  {increment}: commit failed: {out}")
            return 1
        print(f"  {increment}: {message.splitlines()[0]}")
        made += 1

    # anything the plan missed
    run(["add", "-A"], args.dry_run)
    if not args.dry_run:
        _, staged = run(["diff", "--cached", "--name-only"], dry=False)
        if staged:
            run(["commit", "-m",
                 "Add remaining project files\n\n"
                 "Files not covered by a named build increment."], args.dry_run)
            made += 1
            print("  ---: Add remaining project files")

    print(f"\n{made} commit(s) {'planned' if args.dry_run else 'created'}.")
    if not args.dry_run:
        print("\nNext:")
        print("  git log --oneline")
        print("  git remote add origin https://github.com/<you>/<repo>.git")
        print("  git push -u origin main")
        print("\nThen, once gold standards and thresholds exist:")
        print("  python -m scripts.freeze --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
