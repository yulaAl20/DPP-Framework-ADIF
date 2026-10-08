# Next steps — doing the rest on your own

**Updated 2026-10-08.** Everything here is runnable with the software as it
stands. Work top to bottom: each step depends on the one before it.

At any point, `python -m scripts.freeze --check` tells you where you are.

---

## STEP 1 — Gold standards for the three dev schemas

**Why only you can do this.** Ground truth written by whoever wrote the matcher
measures whether the matcher agrees with itself. Your thesis will state that
ground truth was hand-written by the researcher from the rulebook; that sentence
has to be true. Anchoring makes "I draft, you check" useless — people accept
around 95% of supplied annotations without re-deriving them.

**Time:** about 3–4 hours total. 51 rows.

### 1.1 Read the rulebook

`goldstandard/RULEBOOK.md`. Fifteen minutes. It is what makes your decisions
defensible at the viva: "why did `has_batch_no` score as a miss?" has a written
answer.

### 1.2 Fill the worksheets, smallest first

```
goldstandard\manufacturer_a.worksheet.csv            7 rows
goldstandard\manufacturer_b_erpnext.worksheet.csv   22 rows
goldstandard\manufacturer_c_odoo.worksheet.csv      22 rows
```

Open in Excel. Two columns to fill: `cdm_field` and `rationale`.

For each row, read the **sample values** and ask *what does this column
contain?* Copy a field name from `goldstandard/CDM_FIELDS.txt` (copy-paste, do
not retype — a typo becomes a permanent false negative), or `NO_MAPPING`. One
clause of rationale on every row.

**Do not run the matcher first.** The worksheet shows what each column
contains, never what the system thinks it is.

The cases where the rulebook earns its place are the ones where the name points
one way and the contents point another — a boolean flag whose name sounds like a
value, a column holding a unit rather than a quantity, free text that resembles
an identifier. R3.1 to R3.4 cover these.

### 1.3 Convert each one

```powershell
python -m scripts.build_gold_standard goldstandard\manufacturer_a.worksheet.csv --rater GDYDA
```

It refuses on typo'd field names, blank decisions, and two columns claiming one
field. The error names the line and the rule.

### 1.4 Also do the drift variants

`manufacturer_a_drift`, `manufacturer_b_erpnext_drift`,
`manufacturer_c_odoo_drift`. Generate worksheets first:

```powershell
python -m scripts.make_gold_worksheet data\dev\manufacturer_a_drift.csv
```

These are what Metric 4 (template reuse on drift) is measured against. Without
them you cannot report it. **Do not look at the perturbation logs while
deciding** — they name the renamed columns, which is an answer key.

---

## STEP 2 — Derive the thresholds

```powershell
python -m eval.grid_search --schemas data\dev --gold goldstandard --real-model
```

Takes a few minutes. Prints the best macro-F1 and writes
`config/thresholds.yaml`.

**Then copy the two derived values into `config/default.yaml`** by hand, under
`matching.stages.fuzzy.threshold` and `matching.stages.semantic.threshold`.
Replace `null`. Add a comment with the date.

**Record them in methodology.md's Results section, dated** — D11 requires it,
and the section currently says "Nothing yet."

If it refuses:
- *"REFUSED: ... sealed evaluation directory"* — you pointed it at
  `data/heldout`. Use `data/dev`.
- *"REFUSED: ... stub embedder"* — `--real-model` is missing, or the model cache
  is not found.
- *"No gold standard for X"* — Step 1 is incomplete.

---

## STEP 3 — Fit the calibrator

```powershell
python -m eval.fit_calibration --schemas data\dev --gold goldstandard --real-model
```

Writes `config/calibrator.json`. Fits across **all four ablation conditions** by
default, so every stage the ablation will use has observations.

It warns when a stage has fewer than 30 observations. **If you see that warning,
report the confidence curve for that stage with the caveat** — a logistic fit on
ten points is unstable, and saying so is better than an examiner finding it.

The in-sample ECE it prints is **not Metric 3**. Metric 3 is computed on the
held-out schemas in Step 7.

---

## STEP 4 — Git, then the freeze

You have no repository yet. Build one with an increment-structured history:

```powershell
python -m scripts.init_repo --dry-run
python -m scripts.init_repo --name "G.D.Y.D. Alwis" --email "your@email"
```

That produces ~18 commits in project.md §9's increment order, so `git log` reads
as a development narrative — useful for Chapter 4 — rather than one opaque
"initial commit". All timestamps are real; the script has no option to set dates,
because §11 makes the commit history the evidence that the freeze preceded the
held-out schemas, and `src/provenance.py` stamps commit hashes into every run
record. Invented dates would void both.

Consider initialising one level up instead, at `Research\`, so `decisions.md`,
`methodology.md` and `sources.md` share the history with the code they describe.
The freeze tag then means something checkable across both.

Then check readiness and tag:

```powershell
cd adif
python -m scripts.freeze --check
python -m scripts.freeze --tag freeze-v1.0
```

`--check` refuses to tag unless every artefact exists, thresholds are derived, a
calibrator is fitted, gold standards exist, the working tree is clean, **and
`data/heldout/` is still empty.** That last one cannot be recovered once lost:
tagging after the held-out schemas exist would claim an ordering the history does
not show.

It writes `decisions_freeze_record.json` with every artefact hash. **Paste its
contents into decisions.md** with the tag name and date.

---

## STEP 5 — Add the held-out schemas

**Only after Step 4.** Unzip `heldout_package.zip` and copy the two CSVs into
`data\heldout\`. Read its README first.

---

## STEP 6 — Gold standards for the held-out schemas

Same process as Step 1. 46 rows across `heldout_d_dolibarr` (24) and
`heldout_e_certification` (22). Blank worksheets are in the package.

Schema E is the hardest — certifier vocabulary, SPACED CAPS, parenthesised
units. Expect more `NO_MAPPING` and more R4.3 ambiguity calls than the ERP
schemas. That is the point of including it.

Also download Schema A (Kaggle) if you are using it — **confirm the licence on
the dataset page first**, and write its gold standard without inspecting matcher
output.

---

## STEP 7 — Run the evaluation

```powershell
python -m eval.run_ablation --schemas data\heldout --gold goldstandard --status EVALUATION --confidence-threshold 0.8
```

Minutes, not hours. Writes a dated run record to `runs/` with every metric, the
ΔF1 ladder, and full provenance.

**`--status EVALUATION` is refused** unless the frozen CDM exists, thresholds
are derived and a calibrator is fitted. If it refuses, the message says which.
Run without the flag to get an `EXPLORATORY` record you must not cite.

Set `--confidence-threshold` to your chosen auto-accept band — that is what the
review-burden statistic (D16) is measured at.

This run record is your Chapter 5.

---

## STEP 8 — Second rater

**Why it matters:** the gold standard is one person's judgement. Independent
checking is what turns it into evidence that the rulebook constrains decisions
rather than merely recording yours. methodology.md commits you to ≥25% per
schema, agreement reported, target ≥90%.

**Who:** any classmate who can read. No domain expertise needed beyond the
rulebook. 1–2 hours for 25% of five schemas.

```powershell
python -m scripts.second_rater sample data\dev\manufacturer_b_erpnext.csv --fraction 0.25
```

Give them **exactly three things**: the blank worksheet, `RULEBOOK.md`, and
`CDM_FIELDS.txt` plus `cdm/cdm_v1.0.schema.json`.

Give them **nothing else** — not your gold standard, not the perturbation logs,
not any matcher output.

```powershell
python -m scripts.second_rater agree goldstandard\manufacturer_b_erpnext.json goldstandard\manufacturer_b_erpnext.rater2.worksheet.csv
```

Writes an `.agreement.json` you cite in Chapter 3.

**Below 90% is a finding, not a failure.** It means the rulebook
under-specifies something. Add a rule, re-check decisions that rule touches,
record it in decisions.md. A disagreement settled by one rater deferring to the
other, with no rule change, means the ambiguity is still there.

**Book them now.** It is the only task on someone else's calendar.

---

## Decisions still to log

| ID | Question | Recommendation |
|---|---|---|
| **D22** | ADID has no batch level; ESPR names model/batch/item | Option 3 — batch is CDM data, not identity. EN 18219 does not specify granularity, so nothing is non-conformant. State the recall limitation in Ch 6. |
| **D20** | D10 says 3 ablation conditions, project.md §7/§14 say 5, M6 adds a 4th | Four: `fuzzy_only` → `alias_fuzzy` → `full_cascade` → `full_cascade_value`. Amend D10 and §7/§14. |
| **D21** | Does a conflict-demoted record count as a false positive? | Yours. `eval/metrics.py` exposes it as `count_demoted_as_fp`; the default is `False`. Decide and say which you used. |

Reasoning for D22 and D20 is in `RESEARCH_FINDINGS_2026-10-06.md`.

---

## Verification still outstanding

| Item | How |
|---|---|
| Kaggle licence for Schema A | Open the dataset page; the licence renders in the browser |
| EN 18219:2026 full text | Paid CEN standard — ask your university library about CEN access |
| ISO 3166 spot-check | ISO Online Browsing Platform, against `cdm/vocabularies/signatures.yaml` |
| NFR-1 and NFR-4 with the real model | `pytest tests/acceptance/test_nfr.py -v` now that the model is cached; record figures in `docs/nfr_verification.md` |
| NFR-3 machine spec | Record your CPU, RAM and absence of GPU |
| NFR-9 clean install, second machine | Fresh venv on another machine, documented steps only |

---

## Document amendments

- **"Annex I" → "Annex III"** wherever you mean DPP data elements. Affects Ch1,
  Ch2, Ch3, methodology.md, research_objectives. Keep Annex I for sustainability
  parameters.
- **Research gap #6 must be restated.** The EN standards now exist. The gap
  survives as: the standards specify identifiers, carriers, APIs and access
  control, but no apparel attribute model, no identifier granularity, and no
  open SME implementation. Stronger than the original wording.
- **methodology.md Phase 4** still says "Not started."
- **methodology.md schema list** still says 3 schemas; it is now 3 dev + 3
  held-out (D23).
- **methodology.md Results section** is empty — fill it as each run happens.
- **Figure 1** must be redrawn: a four-stage sequential cascade, not parallel
  matchers. The "structure-based matching" box corresponds to nothing
  implemented (nested input is a scope exclusion).
- **UNTP citation**: "under development, accessed 2026-10-06", no version.
