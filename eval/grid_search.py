"""Threshold grid search (D11, FR-14.8).

    python -m eval.grid_search --schemas data/dev --gold goldstandard --out config/thresholds.yaml

Derives the Stage 2, 3 and 4 acceptance thresholds by exhaustive search,
optimising macro-F1. This is the step that turns the ``null`` placeholders in
``config/default.yaml`` into real values.

**It refuses to read the sealed directory.** Tuning on the evaluation set is
the single most damaging thing that could happen to this study's credibility,
and it is an easy mistake to make by passing the wrong path at 2am. The refusal
is enforced in code rather than trusted to discipline.

Thresholds are searched *jointly*, not one stage at a time. In a cascade the
stages are not independent: raising the fuzzy threshold pushes more columns
down to the semantic stage, which changes what the semantic threshold should
be. Optimising them separately finds a local optimum that neither stage would
have chosen together.
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import replace
from pathlib import Path

import yaml

from eval.metrics import mapping_f1
from eval.runner import (
    build_context,
    discover_schemas,
    load_gold_standard,
    load_overlay,
    run_schema,
)
from src.config import load_config


def _refuse_sealed(path: Path) -> None:
    sealed = Path(load_config("config/default.yaml").paths.heldout_dir).resolve()
    resolved = path.resolve()
    if sealed == resolved or sealed in resolved.parents:
        raise SystemExit(
            f"REFUSED: '{path}' is the sealed evaluation directory.\n"
            f"Thresholds are derived on scratch/dev schemas only. Tuning on the "
            f"evaluation set invalidates every number this study reports (D11)."
        )



def _refuse_stub_embedder(cfg, real_model: bool, allow_stub: bool, what: str) -> None:
    """Refuse to derive real values from the stub embedder.

    The stub produces deterministic hash-derived vectors. Its similarities are
    meaningless by construction — it exists to exercise plumbing, not to rank
    anything. A threshold or calibration curve fitted on those numbers looks
    entirely plausible, writes itself into config, and silently corrupts every
    downstream result. Nothing in the output would reveal it.

    So this is a refusal, not a warning.
    """
    if not cfg.matching.stages.semantic.enabled or real_model or allow_stub:
        return
    raise SystemExit(
        f"REFUSED: the semantic stage is enabled but no real embedder is loaded.\n"
        f"The stub embedder's similarities are hash-derived noise, so {what} "
        f"derived from them would be meaningless while looking perfectly "
        f"reasonable in your config file.\n\n"
        f"Either:\n"
        f"  - cache the model (python -m scripts.fetch_model) and pass --real-model\n"
        f"  - or disable the semantic stage for this run\n"
        f"  - or pass --allow-stub if you are deliberately smoke-testing the "
        f"pipeline and will discard the output."
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Derive acceptance thresholds (D11)")
    parser.add_argument("--schemas", type=Path, default=Path("data/dev"))
    parser.add_argument("--gold", type=Path, default=Path("goldstandard"))
    parser.add_argument("--out", type=Path, default=Path("config/thresholds.yaml"))
    parser.add_argument("--start", type=float, default=50.0)
    parser.add_argument("--stop", type=float, default=100.0)
    parser.add_argument("--step", type=float, default=5.0)
    parser.add_argument("--real-model", action="store_true")
    parser.add_argument(
        "--allow-stub", action="store_true",
        help="Proceed with the stub embedder. Smoke-testing only — the "
             "output is meaningless and must be discarded.",
    )
    args = parser.parse_args()

    _refuse_sealed(args.schemas)
    _refuse_stub_embedder(
        load_config('config/default.yaml'), args.real_model,
        args.allow_stub, 'thresholds',
    )

    schemas = discover_schemas(args.schemas)

    pairs = []
    for schema in schemas:
        gold_path = args.gold / f"{schema.stem}.json"
        if not gold_path.is_file():
            raise SystemExit(
                f"No gold standard for '{schema.name}'. Expected {gold_path}.\n"
                f"Every tuning schema needs a frozen ground truth, or the search "
                f"is optimising against nothing."
            )
        pairs.append((schema, load_gold_standard(gold_path)))

    grid = [round(v, 2) for v in _frange(args.start, args.stop, args.step)]
    print(f"Searching {len(grid)}x{len(grid)} threshold pairs over {len(pairs)} schema(s)...")

    best = {"f1": -1.0}
    trace = []

    # The context — CDM registry, semantic index, signature library — does not
    # depend on any threshold. Rebuilding it inside the loop reloaded
    # all-MiniLM-L6-v2 from disk and re-encoded all 54 CDM descriptions on
    # every one of the 121 iterations, which is the same answer computed 121
    # times. Built once here and the config swapped per iteration instead;
    # stage enablement is constant across the grid, which is what makes this
    # safe.
    context = build_context(
        load_overlay(fuzzy_threshold=grid[0], semantic_threshold=grid[0],
                     value_threshold=grid[0]),
        real_model=args.real_model,
    )

    for fuzzy, semantic in itertools.product(grid, grid):
        cfg = load_overlay(fuzzy_threshold=fuzzy, semantic_threshold=semantic,
                           value_threshold=fuzzy)
        context = replace(context, cfg=cfg)
        scores = []
        for schema, gold in pairs:
            result, _ = run_schema(schema, context)
            scores.append(mapping_f1(result, gold.mappings)[2])
        macro_f1 = round(sum(scores) / len(scores), 6)
        trace.append({"fuzzy": fuzzy, "semantic": semantic, "macro_f1": macro_f1})
        if macro_f1 > best["f1"]:
            best = {"f1": macro_f1, "fuzzy": fuzzy, "semantic": semantic}

    print(f"\nBest macro-F1 {best['f1']:.4f} at "
          f"fuzzy={best['fuzzy']}, semantic={best['semantic']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(yaml.safe_dump({
        "_derived_by": "eval/grid_search.py",
        "_derived_on": [str(s.name) for s, _ in pairs],
        "_gold_frozen_at": sorted({g.frozen_at for _, g in pairs}),
        "_macro_f1": best["f1"],
        "matching": {"stages": {
            "fuzzy": {"threshold": best["fuzzy"]},
            "semantic": {"threshold": best["semantic"]},
        }},
    }, sort_keys=False), encoding="utf-8")

    (args.out.parent / "grid_trace.json").write_text(
        json.dumps(trace, indent=2), encoding="utf-8")

    print(f"\nWritten to {args.out} and {args.out.parent / 'grid_trace.json'}.")
    print("Copy these values into config/default.yaml, then record them in "
          "methodology.md's Results section with today's date (D11).")
    return 0


def _frange(start: float, stop: float, step: float):
    value = start
    while value <= stop + 1e-9:
        yield value
        value += step


if __name__ == "__main__":
    raise SystemExit(main())
