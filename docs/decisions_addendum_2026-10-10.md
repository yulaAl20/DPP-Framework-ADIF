# decisions.md — addendum, entries D31 onward

Append to the end of your `decisions.md`, after D30. **Renumber** if your file
already uses these numbers. Anything marked **[FILL IN]** is something only you
can record.

---

### D31 — Held-out schema construction and disclosure
- **Date:** 2026-10-10, after tag `freeze-v1.0` (commit `d857668`).
- **H1 (Kaggle):** `styles.csv` from the Fashion Product Images Dataset, downloaded unopened; SHA-256 of the zip recorded in D18.
- **H2 (`heldout_h2_dolibarr.csv`, 5 rows x 26 columns) and H3 (`heldout_h3_techpack.csv`, 5 rows x 23 columns):** compiled by an AI assistant (Claude).
  - Headers follow Dolibarr product-table and extrafield naming (H2) and typical buyer tech-pack vocabulary (H3), **from the assistant's recollection of those sources, not copied from a live Dolibarr instance or a specific buyer's document.**
  - All values are invented. Barcodes pass the GTIN-13 check digit.
  - The assistant knew the CDM and the system. Headers were taken from source vocabulary rather than chosen to match or avoid CDM fields, and the matcher was not run on these files before the answer keys were committed.
- **Drifted variants:** `scripts.perturb_schema --level drift --seed 7`. One column dropped and five renamed in each (H2: `weight_units` dropped; H3: `Main Label` dropped).
- **To do before citing:** check the H2 header list against a Dolibarr instance or its documentation and record any difference. **[FILL IN]**
- **Provenance note:** `data/heldout/PROVENANCE.md`.

### D32 — Kaggle file repaired outside the frozen system
- `styles.csv` contains rows with an unquoted comma in the last column (`productDisplayName`), giving 11 fields against a 10-column header. A strict reader fails first at source line 6044 (`pandas.errors.ParserError`).
- The loader is frozen, and the file was not edited by hand. `scripts/repair_kaggle_styles.py` re-joins surplus fields into the last column and writes a **new** file; rows with too few fields would stop the script (none occurred).
- **Result:** 44,446 data rows, 10 columns, **22 rows repaired** (first at line 6044).
- **SHA-256 of extracted `styles.csv`:** `CD86BD2D71B4065ED91786A52AA6CCC0EED343949791C663BE9AF35F105A128C`
- **SHA-256 of repaired `kaggle_styles.csv`:** `E0ABD709EC0000596452695626DAF904AC87F3C86FA6F8E6ACC8EBBB01DBB338`
- The original extracted file was moved out of `data/heldout` so the harness does not load it. The zip hash in D18 is unchanged.
- **Finding for the limitations section:** the system's loader surfaces this as a raw parser error, not a user-facing ingestion message. Deferred to a post-evaluation version.

### D33 — Ground truth and second rating for the held-out schemas
- **Primary rater:** YulaniA. Answer keys written from `goldstandard/RULEBOOK.md` and `CDM_FIELDS.txt` only, before any run on these schemas. Drift keys derived mechanically with `scripts.derive_drift_gold` (every column resolved; no hand decisions).
- **Answer-key sizes (columns / mapped):** H2 26/8, H2 drift 25/8, H3 23/12, H3 drift 22/12, Kaggle 10/2.
- **Second rater:** LiviruM, independent, given only the blank sheet, the rulebook, `CDM_FIELDS.txt` and the CDM schema. Never shown the answer keys, perturbation logs or matcher output.
- **Sampling:** seeded (2026), reproducible via `scripts.second_rater sample`.
  - The first H2 draw (`--fraction 0.25`) gave 6 of 26 columns (23%), below the 25% target, and was **redrawn at 0.3 (8 of 26, 31%) before any sheet was given to the rater**.
- **Pre-adjudication agreement:** H2 8/8, H3 6/6, Kaggle 3/3 = **17/17 (100%)**, against the 90% target. Agreement files: `goldstandard/*.agreement.json`.
- **Caveat to state:** 17 sampled rows (about 29% of the 59 base-schema columns), one second rater.

### D34 — Evaluation run
- **Commit:** `ef89aa757a446426ad85da4cc4cdbc08cbe4385f` (after the answer keys were committed; tag `freeze-v1.0` precedes it).
- **Config hash:** `3faa492b...84695f8` (see the run records' provenance block).
- **Commands (RUNBOOK step 12):** `eval.run_ablation` (ladder), `eval.run_ablation --conditions semantic_only`, `eval.run_template_reuse` (gold template), `eval.run_template_reuse --template-from cascade`.
- **Run records (all `[EVALUATION]`):** `runs/eval_20261010T071102Z.json`, `runs/eval_20261010T071120Z.json`, `runs/template_reuse_20261010T071134Z.json`, `runs/template_reuse_20261010T071150Z.json`.
- **Ordering note:** the Kaggle second-rater result (3/3) was obtained **after** this run. The Kaggle answer key was not changed after the run, and agreement was 100%, so the run stands as recorded.

### D35 — Defect found after freeze: stored ablation deltas
- The `ablation_deltas` list inside an ablation run record pairs consecutive entries of the whole metrics list, so it compares different schemas (for example `fuzzy_only -> fuzzy_only`). The console output printed the correct per-schema deltas, but the stored list must not be cited.
- **Decision:** the frozen code is not changed. Deltas are recomputed from the saved `metrics` by `eval/summarise_run.py` (read-only analysis, outside the frozen system). The per-condition metrics themselves are unaffected.
- Fix deferred to a post-evaluation version; list as a limitation.

### D36 — Reporting rules for the evaluation
1. **Template reuse:** with a reviewer-corrected template, reuse on unchanged columns is 100% by construction; it is **not** reported as a result. Report reuse with the cascade-derived template, and delta-field F1, always with counts (denominators are 2 mappable new columns for H2 and 3 for H3).
2. **Metric 2 (mandatory-field match):** the Kaggle schema contains no mandatory field (coverage ceiling 0.0), so its restricted rate is vacuous. Report Metric 2 over H2, H3 and their drifted copies only, with the coverage ceiling (0.5 for H2 and H3).
3. **ECE:** pooled over conditions and schemas, so the same column is counted once per condition that maps it. State that the effective sample is smaller than the 158 pooled pairs; two bins are populated.
4. **Macro-averages:** each schema counts once. Per-schema results are always reported alongside, because the Kaggle schema has 10 columns (one column moves its F1 by 10 or more points).
5. **Review burden** is reported with the review band 0.9608 from D27.

### D37 — Environment checks
- **NFR-3 (hardware), 2026-10-10:** Intel Core i5-1135G7 @ 2.40 GHz, 4 cores / 8 threads; 11.8 GB RAM as reported by Windows; Intel Iris Xe integrated graphics only; `torch.cuda.is_available()` = `False` (CPU-only run).
- **NFR-1 (offline):** demo run with Wi-Fi off completed on the real model from the local cache. **[FILL IN date and screenshot reference]**
- **NFR-9 (second machine):** **[FILL IN after the install: machine, OS, Python version, date, deviations from `docs/setup.md`, time taken, outcome]**
- Per-schema cascade time on this machine was 0.01 to 0.4 s for the five schemas; the 44,446-row Kaggle file took 0.08 s for the full cascade (stage time only, excluding file loading).
