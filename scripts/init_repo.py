"""Initialise the repository with an increment-structured commit history.

    python -m scripts.init_repo --dry-run     # show the plan, change nothing
    python -m scripts.init_repo

Creates one commit per build increment, in the order project.md §9 specifies, so
`git log` reads as a development narrative rather than a single "initial commit"
dump. Useful source material for Chapter 4, and it gives the freeze tag
something meaningful to sit on top of.

**All commits carry real timestamps.** There is deliberately no option to set
commit dates. project.md §11 makes the commit history the evidence that the
freeze preceded the held-out schemas, and `src/provenance.py` stamps commit
hashes into every run record. A history with invented dates would void both.

Run this once, before the freeze (NEXT_STEPS.md Step 4).
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

#: (message, paths). Order follows project.md §9's increment sequence, so the
#: log shows the artefact being built up rather than appearing at once.
INCREMENTS: list[tuple[str, list[str]]] = [
    ("Add project scaffolding, dependency manifests and setup scripts",
     [".gitignore", ".gitattributes", "pyproject.toml", "requirements.txt",
      "requirements-optional.txt", "setup.cmd", "setup.ps1", "setup.sh"]),
    ("B1: config loader with unset-tunable guard, provenance capture",
     ["src/__init__.py", "src/config.py", "src/provenance.py",
      "config/default.yaml", "tests/__init__.py", "tests/unit/__init__.py",
      "tests/unit/test_config.py"]),
    ("Add CDM extraction record, Annex III transcription and provenance table",
     ["cdm/EXTRACTION.md", "cdm/annex_iii_transcription.csv",
      "cdm/ANNEX_III_TEMPLATE.csv", "cdm/provenance.csv", "cdm/ALIGNMENT.md"]),
    ("Freeze CDM v1.0: schema, JSON-LD context, alias vocabulary, ADID grammar",
     ["cdm/cdm_v1.0.schema.json", "cdm/cdm_v1.0.context.jsonld",
      "cdm/aliases_v1.0.yaml", "cdm/vocabularies/", "adid/grammar.ebnf"]),
    ("B2: ingestion and schema analysis (M1, M2)",
     ["src/ingestion/", "src/analyser/", "tests/unit/test_ingestion.py",
      "tests/unit/test_analyser.py"]),
    ("B3-B4: alias, fuzzy and semantic matching with cascade arbitration (M3-M5, M7)",
     ["src/cdm/", "src/matching/models.py", "src/matching/stage1_alias.py",
      "src/matching/stage2_fuzzy.py", "src/matching/stage3_semantic.py",
      "src/matching/arbitration.py", "src/matching/__init__.py",
      "tests/fixtures/", "tests/unit/test_matching.py"]),
    ("B5: per-stage Platt calibration, refusing to report raw scores as confidence",
     ["src/matching/confidence.py"]),
    ("B6: CDM validation, ADID constructor, JSON-LD serialisation (M10-M12)",
     ["src/validation/", "src/identity/", "src/serialisation/"]),
    ("B7-B8: REST API and single-file review interface (M13, M8)",
     ["src/api/", "src/review/", "ui/", "tests/integration/"]),
    ("B9: manufacturer template store with drift reporting (M9)",
     ["src/templates/"]),
    ("B10: instrumentation and evaluation harness (M14)",
     ["src/instrumentation/", "eval/", "config/ablation/", "runs/.gitkeep",
      "tests/unit/test_template_reuse.py"]),
    ("B11: value-based matching stage, wired into the cascade (M6)",
     ["src/matching/stage4_value.py", "tests/unit/test_evaluation.py",
      "tests/unit/test_full_pipeline.py"]),
    ("Add CLI, demo, environment check and support scripts",
     ["src/cli.py", "scripts/"]),
    ("Add development schemas from ERPNext and Odoo field lists, with drift variants",
     ["data/"]),
    # The rulebook must be committed BEFORE the ground truth written against it.
    # Splitting these two is not cosmetic: the freeze tag sits on top of the
    # ground-truth commit, and project.md §11 makes that ordering the evidence
    # that the rulebook governed the decisions rather than being written to
    # justify them afterwards.
    ("Add ground-truth rulebook v1.0, worksheet tooling and second-rater harness",
     ["goldstandard/RULEBOOK.md", "goldstandard/HOWTO.md",
      "goldstandard/CDM_FIELDS.txt", "goldstandard/.gitkeep",
      "docs/example/"]),
    ("Add development schema ground truth: 99 columns, 51 decisions, rulebook v1.0",
     ["goldstandard/"]),
    ("Add acceptance tests for NFR-1 offline, NFR-4 performance, NFR-5 reproducibility",
     ["tests/acceptance/"]),
    ("Add documentation: setup, verification guide, NFR record, licence inventory",
     ["README.md", "NEXT_STEPS.md", "QUICKSTART.md", "RECOVER.md", "PUSH.md", "RUNBOOK.md", "docs/"]),
]


def _git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialise the repo with an increment-structured history"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--name", help="git user.name, if not already configured")
    parser.add_argument("--email", help="git user.email, if not already configured")
    args = parser.parse_args()

    if args.dry_run:
        print("\nPlanned commits (real timestamps, in §9 increment order):\n")
        for index, (message, paths) in enumerate(INCREMENTS, 1):
            present = [p for p in paths if Path(p).exists()]
            missing = [p for p in paths if not Path(p).exists()]
            print(f"{index:2}. {message}")
            print(f"    {len(present)} path(s){'  MISSING: ' + str(missing) if missing else ''}")
        print(f"\n{len(INCREMENTS)} commits. Nothing written — drop --dry-run to apply.")
        return 0

    project_root = Path.cwd().resolve()

    if subprocess.run(["git", "rev-parse", "--git-dir"],
                      capture_output=True).returncode != 0:
        _git("init")
        print("Initialised repository")

    # `git rev-parse --git-dir` succeeds from inside ANY ancestor repository.
    # If a parent directory is already a repo — a home folder under version
    # control is the common case on Windows — the check above passes, no init
    # happens, and every commit below lands in that unrelated repository with
    # the project buried under a long path prefix. The catch-all `git add` then
    # sweeps the whole of it.
    #
    # This has actually happened. It is not a hypothetical, and it cost an
    # afternoon, so the script refuses rather than warns.
    toplevel = Path(_git("rev-parse", "--show-toplevel")).resolve()
    if toplevel != project_root:
        raise SystemExit(
            f"Refusing to run.\n\n"
            f"  This directory:   {project_root}\n"
            f"  Repository root:  {toplevel}\n\n"
            f"These must be the same. An ancestor directory is already a git\n"
            f"repository, so the commits would go into that one and would pick\n"
            f"up every unrelated file under it.\n\n"
            f"Fix one of these, then re-run:\n"
            f"  - You meant to run this somewhere else: cd to the project folder.\n"
            f"  - That ancestor repo is unwanted: remove its .git directory\n"
            f"    ({toplevel / '.git'}) only if you are certain it is not a real\n"
            f"    repository with work in it. Check `git -C \"{toplevel}\" log`\n"
            f"    and `git -C \"{toplevel}\" remote -v` FIRST.\n"
            f"  - That ancestor repo is real and wanted: this project needs to\n"
            f"    live outside it, or be added to its .gitignore."
        )

    if args.name:
        _git("config", "user.name", args.name)
    if args.email:
        _git("config", "user.email", args.email)
    if not _git("config", "user.name", check=False):
        raise SystemExit(
            "git user.name is not set. Re-run with --name 'Your Name' "
            "--email you@example.com"
        )

    made = 0
    for message, paths in INCREMENTS:
        existing = [p for p in paths if Path(p).exists()]
        if not existing:
            continue
        _git("add", "--", *existing)
        if not _git("diff", "--cached", "--name-only"):
            continue
        _git("commit", "-m", message)
        made += 1
        print(f"  {made:2}. {message}")

    # Anything the increment list did not name — a file added since, or one this
    # script does not know about. Committing it separately keeps the increment
    # commits honest about their contents.
    _git("add", "-A", "--", ".")
    if _git("diff", "--cached", "--name-only"):
        _git("commit", "-m", "Add remaining project files")
        made += 1
        print(f"  {made:2}. Add remaining project files")

    print(f"\n{made} commit(s). Review with:  git log --oneline --stat")
    print("Next: NEXT_STEPS.md Step 4 — python -m scripts.freeze --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
