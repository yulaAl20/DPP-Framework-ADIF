# decisions.md — the decision log
**Last updated:** 2026-10-08

Each entry records: what was decided, what else was considered, why, **what was given up**, and what else has to change as a consequence. The "gave up" line is the one that matters at viva — a decision log that only lists benefits is a sales document, not a record.

---

## ⚠ Read this before pasting

**Entries D1–D16 are not reproduced in this file.** I do not have their text, and reconstructing them from the way they are cited elsewhere would put words into your decision log that you never wrote. A decision log with invented bodies is worse than an incomplete one.

Use this file in two parts:

1. **§A — Amendments to D1–D16.** Apply these edits to your existing entries. Each says which entry, what changes, and why. Do not rewrite the entries; append the amendment lines, so the original decision and its later revision are both visible. An examiner reading a log that was silently edited learns nothing; one reading "decided X, amended by D23 on 2026-10-05 because Y" learns how you work.
2. **§B — New entries D17–D24.** Paste these in full. Two of them (D20, D22) are written as **unresolved** and must not be pasted as settled — they are yours to decide.

---

## §A — Amendments to existing entries

| Entry | Amendment | Driver |
|---|---|---|
| **D2** (schema inventory) | **Superseded in part by D23.** The ERPNext- and Odoo-derived schemas are now *development* schemas, not held-out. The evaluation set is rebuilt from uninspected sources. Append: *"Amended 2026-10-05 by D23."* | D23 |
| **D3** (circularity guard on source material) | Unchanged and still load-bearing. Worth adding one line: the guard now also covers **held-out construction without inspecting per-column matcher output**, which is the failure D23 records. | D23 |
| **D6** (calibration method = Platt) | Unchanged. Add the implementation note: fitted **per stage**, and the calibrator **refuses to borrow another stage's curve** — an uncalibrated stage is reported as uncalibrated rather than scored against someone else's mapping. | Implementation |
| **D8** (drifted "season-two" variants) | Unchanged. Three dev drift variants now exist with machine-readable perturbation logs; held-out drift variants are built after the freeze. | Implementation |
| **D9** (ADID hierarchy) | **Amended.** The URI shape is `/adid/{family}/{colour}_{size}/{serial}` — the variant is a **single composite segment**, not two. `/adid/{family}/{colour}/{size}` was ambiguous against project.md's `/adid/{family}/{variant}/{instance}` at depth 3. Also: the conformance target is now open and points at **IEC 61406**, not GS1 Digital Link — see D17's sibling note in D22 and methodology.md §3. | Implementation; EN 18219 finding |
| **D10** (ablation ladder, three conditions) | **Amended by D19** — the ladder is at minimum **four** rungs. The exact count is open under **D20**. Append: *"Amended 2026-08-18 by D19; count open under D20."* | D19 |
| **D11** (thresholds by grid search) | Unchanged in substance; strengthened in enforcement. Add: thresholds are `null` in config and raise rather than default; the grid search **refuses** to read `heldout_dir` and **refuses** to run with the stub embedder. Both refusals are asserted by automated tests. | Implementation |
| **D12** (two separate 80% claims) | Unchanged, and now **better justified**: the textiles delegated act is verified **not adopted**, so there is no regulatory mandate to measure against. Measuring coverage against a *constructed* reference set was the only honest option, not a convenience. | sources.md verification |
| **D14** (Demonstration separate from Evaluation) | Unchanged. | |
| **D15** (Schema A = Fashion Product Images Dataset) | **Superseded in part by D23.** The dataset remains in the study but moves to the **held-out** set, under D18's download-and-seal rule. The development `manufacturer_a` schema is a different, smaller schema. Append: *"Amended 2026-10-05 by D23."* | D23 |
| **D16** (review burden statistic) | Unchanged. Add: the API now also records reviewer *actions* (accepted / retargeted / supplied / rejected), giving a manual-effort rate (FR-8.8) at no extra data-collection cost. | Implementation |

---

## §B — New entries

## D17 — Cascade vs parallel weighted combination
**Date:** 2026-08-18. Resolves the first open decision in project.md §13 (blocks B3).
**Decided:** Strict fallback **cascade with early exit** — alias → fuzzy → semantic — not parallel scoring with weighted combination.
**Options considered:** (a) cascade with early exit; (b) parallel scoring of all stages with a tuned weighted combination.
**Why:** (b) would likely calibrate better, since it sees every signal for every field rather than stopping at the first acceptance. But it requires weight tuning — a second tuning surface on top of the thresholds already grid-searched under D11, on the same limited development data. It also breaks D10's ablation ladder, which attributes ΔF1 to each *added stage* and so presupposes stages that can be added in sequence. And RQ4 and Objective 4 already say "cascaded" following D13; choosing (b) would mean rewriting both.
**Gave up:** Real accuracy. A cascade cannot recover from a confident wrong alias hit — once Stage 1 accepts, the later stages never see the field. This is a genuine limitation of the design and belongs in Chapter 6 as a stated one, not omitted. FR-7.5's conflict detection catches only the subset where two columns claim the same CDM field; it does not catch a single confidently-wrong alias.
**Consequence:** Figure 1 must be redrawn. It shows name/structure/instance-based matchers running in parallel, which contradicts the design as decided and as described in Chapter 3.

---


### D18 — Held-out data checksum (Schema A, Kaggle)
- **File:** `data/heldout/styles.csv.zip`, downloaded unopened and unextracted
- **SHA-256:** `2D5C74F249C44DA1690BBDD2221E526E57D170EEA8260D03605F7446813E92C1`
- **Size:** 935,785 bytes
- **Downloaded:** 2026-10-10, using the Kaggle CLI
- **Source:** https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset
- **Path within dataset:** `fashion-dataset/styles.csv` (only the metadata table; the images and other files were not downloaded)
- **Licence:** MIT, as reported by the Kaggle CLI
- **Held-out status:** the file was hashed before any extraction or inspection, after the freeze tag `freeze-v1.0`.

---

## D19 — Value-based matching stage (M6) retained in Phase 4 scope
**Date:** 2026-08-18.
**Decided:** M6 / B11 stays in scope. The in/out decision remains at the **B10 checkpoint**, as project.md §13 specified — it is not pre-empted on timeline grounds. `stage_order` declares four stages; the toggle stays false until B11 is built.
**Options considered:** (a) cut M6 now to protect the Phase 4 window; (b) keep it and hold the decision to B10 as specified.
**Why:** M6 is the only stage that can recover a field whose *header* is uninformative but whose *values* are diagnostic — a column named `col_7` full of ISO 3166 codes. The deliberately idiosyncratic schema is exactly where header-only matching should degrade and where the value stage would show its worth; cutting it removes the ablation's most interesting rung. It is also cheaper than project.md §5 implies: FR-10.2 already requires ISO 3166 codes, fibre names (Reg. 1007/2011), units and certification identifiers as controlled vocabularies for CDM validation, and FR-6.4 reuses those same vocabularies as signatures. The genuinely new work is percentage-composition, ISO date, GTIN check-digit and currency patterns, plus the conformance scoring function.
**Gave up:** Schedule slack, and — more sharply — *evaluation* surface rather than build time. A fourth condition multiplies across schemas, metrics and drift variants, and D11's grid search must now tune a fourth threshold on the same limited development data, diluting it. The cost of this decision lands in Phase 5, not Phase 4.
**Protection retained:** project.md §9's sequencing rule is unchanged and now load-bearing — **B10 before B11**. If the window closes, what is lost is the fourth matching stage, never the evaluation harness that produces Chapter 6.
**Contingency instead of a scope cut:** pressure is absorbed through the existing M/S/C requirement grading, which exists for this purpose ("C = cut first under time pressure"). No module is dropped; individual **S** and then **C** requirements are, and each drop is logged here when made.
**Outcome:** B10 and B11 both completed. The stage is built and wired into the cascade; the config toggle is the only thing holding it off, and it is flipped per ablation condition.
**Consequence:** Figure 1's "instance-based matching" box now maps to a stage that actually exists (≈ Rahm & Bernstein's instance-based category). What remains wrong in that figure: the parallel arrangement, which contradicts D17, and the "structure-based matching" box, which corresponds to nothing implemented — nested/hierarchical input is an explicit scope exclusion.

---

## D20 — Ablation condition count — **UNRESOLVED**
**Raised:** 2026-08-18. **Still open 2026-10-08. Decide before Phase 5b.**
**Conflict:** D10 specifies **three** conditions (fuzzy-only, alias+fuzzy, full cascade). project.md §7 lists **five** config files (`exact_only`, `fuzzy_only`, `semantic_only`, `alias_fuzzy`, `full_hybrid`), and §14 Definition of Done #4 requires "all five ablation configurations execute."
**Compounded by D19:** retaining the value stage adds a rung — full cascade *with* the value stage — so the cumulative ladder is at minimum **four**, not three.
**The real question:** does `semantic_only` earn a run on top of the ladder? It is not a rung on a cumulative ladder, but it answers something the ladder cannot — whether the embedding stage alone would have sufficed, which is the sharpest available test of the most expensive and most novel-sounding component. `exact_only` is weaker: close to a strawman, and D10 explicitly rejected the single-strawman framing.
**Count the cost before deciding.** Each condition runs across every held-out schema and all four metrics, plus drift variants for the template test. Re-runs are expensive. This is a decision to make once, deliberately, not to discover mid-evaluation.
**Recommendation on file (accept or reject):** run the **four-rung ladder** — `fuzzy_only` → `alias_fuzzy` → `full_cascade` → `full_cascade_value`. Drop `exact_only`. If time allows after the main run, add `semantic_only` as a **single supplementary condition reported separately from the ladder**; do not let it into the ladder itself, because a non-cumulative rung makes ΔF1 unattributable.
**Action on deciding:** amend D10, and amend project.md §7 and §14 so the two documents stop disagreeing. Four config files currently exist in `config/ablation/`.

---

## D21 — How demoted conflict losers are counted — **UNRESOLVED**
**Raised:** 2026-10-05. **Decide before the first scored run.**
**Problem:** D24 makes conflict resolution demote a losing claimant. The loser is then either (a) left unmapped, or (b) re-offered its next-best candidate. The metric treatment differs, and the choice changes reported F1 without changing a line of matching code.
- If a demoted column is scored as a **false negative**, the cascade is penalised for correctly resolving a conflict.
- If it is scored as **not applicable**, F1 is flattered by excluding exactly the hard cases.
- If it is **re-offered its next-best candidate**, the metric is measuring a different algorithm from the one described in Chapter 3.
**Why this is not a technicality:** conflicts concentrate on the fields that matter. `colour` and `size` attract several plausible claimants in every ERP export. Whatever is decided must be stated in Chapter 3 *before* the numbers exist, or it will read as having been chosen after seeing them.
**Action:** decide, log, and encode the choice in `eval/metrics.py` so it cannot drift between runs.

---

## D22 — ADID and the batch level — **UNRESOLVED**
**Raised:** 2026-10-05. Full write-up in `cdm/ALIGNMENT.md`. **Decide before the freeze.**
**Problem:** ESPR Art. 9(2)(d) requires a delegated act to state whether a passport is at **model, batch or item** level. UNTP carries `batchNumber`; EPCIS models lots through ILMD. ADID has family, variant, instance — **batch is not one of them**. A production lot of 500 navy mediums sits between variant and instance with nowhere to live, and five CDM fields are naturally batch-scoped (`batchNumber`, `productionDate`, `productionStage`, `disposition`, `purchaseOrderReference`). Apparel manufacturing is batch-organised: dye lots, cut tickets and shipment lots are how a garment factory actually tracks goods.
**Options:** (1) state it as a limitation; (2) add a fourth optional ADID level; (3) treat batch as CDM *data* rather than ADID *identity*.
**Current state:** option 3 — **by default rather than by decision**. The batch-scoped fields simply landed in the CDM. An unlogged default is the one an examiner finds.
**Recommendation on file:** adopt **option 3 deliberately**, and state it as a scope decision rather than a limitation. D9's principle is that only what *distinguishes which item is being addressed* belongs in the path. A batch number describes provenance: two garments from different dye lots are the same variant, orderable and sellable interchangeably. By D9's own test, batch fails to earn a path segment. EN 18219:2026 reinforces this — the published standards do not define granularity at all, so there is no external schema ADID is failing to conform to.
**What option 3 gives up, and Chapter 6 must say:** an ADID cannot address "all units from lot DL-7781." For a **recall** — a realistic apparel scenario — that is a genuine functional gap, recoverable only by querying the CDM rather than by resolving an identifier. State it; do not let an examiner find it.
**Why not option 2:** a grammar change, a URI depth change, API route changes and a re-freeze, to serve a level the standards do not require and the regulation names only as one option among three.

---

## D23 — Schemas B and C reassigned from held-out to development
**Date:** 2026-10-05.
**Decided:** The ERPNext-derived and Odoo-derived schemas become **development** schemas. The held-out evaluation set is rebuilt from sources not yet inspected.
**Why — and this is a self-report:** while constructing them, the value-signature library was adjusted three times in response to their per-column output — a hex-colour pattern matching an HS code, a numeric-size pattern matching a weight, a carbon-footprint pattern matching any number. Every fix was a genuine bug, but each was *found by looking at data destined to be sealed*. That is tuning on the evaluation set (project.md §11), and it does not stop being so because the fixes were correct.
**Options considered:** (a) revert the fixes and seal B and C — which ships a value stage with patterns known to be broken and leaves nothing to tune signatures against; (b) reassign B and C to development and rebuild the held-out set.
**Gave up:** two ready-made held-out schemas, and roughly a day rebuilding the evaluation set from untouched sources.
**Gained, and this is the larger part:**
- A genuine tuning set. The calibration fit previously warned at ten observations per stage; three development schemas materially improve that.
- A clean tuning/evaluation split, which the original three-schema plan did **not** have — thresholds were to be grid-searched on "scratch schemas" that were never actually specified anywhere.
- Six schema files rather than three, 99 columns and 51 mapping decisions instead of roughly 50 total. Still far too few for a significance test, but a better basis for reporting a trend.
**Revised inventory (supersedes D2 and D15 in part):**
- **Development** (tuning, signature design, calibration fitting): `manufacturer_a`, `manufacturer_b_erpnext`, `manufacturer_c_odoo`, plus drift variants.
- **Held-out** (evaluation only, opened after the freeze commit): Fashion Product Images Dataset (D15, under D18's seal rule), plus two schemas to be built from Dolibarr, a GOTS/OEKO-TEX certification form, or a buyer tech-pack template — **constructed without inspecting per-column matcher output**.
**Enforcement added, so the rule is not merely written down:** `heldout_dir` is declared in `config/default.yaml`; `eval/grid_search.py` and `eval/fit_calibration.py` refuse to read from it; an acceptance test asserts those refusals. Two scripts named the path literally and had to be changed to resolve it from config — the test caught both.
**Consequence:** methodology.md's schema list is rewritten. **Chapter 3 should state the dev/held-out split explicitly — it is a methodological strength worth claiming, not an embarrassment to bury.** The contamination itself is declared, dated and traceable; that is what a decision log is for.

---

## D24 — Conflict resolution respects stage precedence
**Date:** 2026-10-05.
**Decided:** When two columns claim one CDM field, the winner is chosen by **stage precedence first** (template > alias > fuzzy > semantic > value), then raw score, then source position.
**Why:** previously the tie broke on raw score alone. Alias hits and value hits both score 100, so a column named `customs_tariff_number` — whose HS code `610910` happens to be six valid hex characters — took the `colour` field away from a column literally named `colour_name`, on nothing more than appearing earlier in the file. An exact match against a curated vocabulary is stronger evidence than an inference from data shape, and the cascade order already encodes that ranking.
**Gave up:** nothing. The previous behaviour had no justification beyond being the first thing written.
**Follow-on:** raises **D21** — how the demoted loser is counted in the metrics.

---

## Status summary

| Entry | Subject | Status |
|---|---|---|
| D1–D8 | (in your copy) | Settled; D2, D3, D6, D8 carry amendments in §A |
| D9 | ADID hierarchy | Settled; amended (composite variant segment; conformance target reopened) |
| D10 | Ablation ladder | Settled; amended by D19, count open under D20 |
| D11 | Threshold selection | Settled; enforcement strengthened |
| D12 | Two 80% claims | Settled; justification now verified |
| D13 | "Cascaded" wording in RQ4 / Obj. 4 | Settled |
| D14 | Demonstration ≠ Evaluation | Settled |
| D15 | Kaggle dataset as a study schema | Settled; amended by D23 (moved to held-out) |
| D16 | Review-burden statistic | Settled; extended with reviewer-action counts |
| **D17** | Cascade vs parallel | **Settled** |
| **D18** | Download-and-seal | **Settled**; SHA-256 still to record |
| **D19** | Value stage retained | **Settled**; built |
| **D20** | Ablation condition count | **OPEN** — decide before Phase 5b |
| **D21** | Demoted-conflict metric treatment | **OPEN** — decide before the first scored run |
| **D22** | ADID batch level | **OPEN** — decide before the freeze |
| **D23** | Dev / held-out reassignment | **Settled** |
| **D24** | Stage precedence in conflicts | **Settled** |

**Three open decisions block the freeze and the first scored run.** None of them is a coding task; all three are yours.
---

## Freeze-time decisions (2026-10-10)

### D25 — Matching thresholds derived (executes D11)
- **Date / script:** 2026-10-10, `python -m eval.grid_search --real-model`
- **Data:** 6 scratch schemas in `data/dev` (A, B, C and their drifted copies) against the frozen gold standards dated 2026-10-08. The sealed directory was not read.
- **Method:** exhaustive joint search over fuzzy × semantic × value, each 50–100 in steps of 5 (11³ = 1,331 triples), optimising macro-F1. The search ran on the complete cascade including the value stage (`config/ablation/full_cascade_value.yaml`).
- **Result:** macro-F1 0.7685 at **fuzzy = 85.0, semantic = 85.0, value = 75.0**.
- **Changes from the earlier plan:**
  - The value threshold is tuned on its own. It previously borrowed the fuzzy value.
  - The fuzzy and semantic thresholds are therefore tuned with the value stage enabled.
  - Ties go to the stricter (higher) thresholds.
- **Evidence:** `config/thresholds.yaml`, `config/grid_trace.json`.

### D26 — Calibration fitted
- **Method:** Platt scaling, one model per stage (D6), fitted on the scratch schemas pooled across the four ablation conditions: 182 observations.
- **Observations per stage:** alias 93, fuzzy 71, value 16, semantic 2.
- **Caveat:** the semantic and value fits are unstable at these sample sizes, and the script warned about both. Confidence values for those two stages are reported with that caveat.
- **In-sample ECE:** 0.0037. This is not Metric 3, which is computed on the held-out data.
- **Artefact:** `config/calibrator.json`. It is gitignored by default, so it was committed with `git add -f` as part of the frozen set.

### D27 — Review threshold rule
- **Rule (stated before results):** a mapping goes to a human when its calibrated confidence is below the lowest confidence at which accuracy on the scratch data reaches 90%.
- **Result:** `confidence.bands.review = 0.9608`.
- **Effect:** 18 of 182 pooled scratch mappings are auto-accepted, at 100% accuracy. Only value-stage mappings (and one semantic hit) clear the bar. Alias mappings (confidence 0.870) and fuzzy mappings (about 0.43) all go to review.
- **Caveats:** the figure is in-sample and rests on small counts for the stages above the threshold. The 90% target was not lowered to let the alias stage through. Review burden can be reported at 85% and 95% as a sensitivity analysis without changing this rule.
- **Used by:** the API and review screen (flagging), and the review-burden statistic in the ablation run (default).

### D28 — Development-set error analysis (full cascade, scratch schemas)
- **Per-stage accuracy:** alias 27/31 (87.1%), fuzzy 2/10 (20.0%), semantic 1/1, value 16/16.
- **Alias errors (4):**
  - `Style_No` → `productIdentifier`, gold `gtin` (R3.4, R4.1: decide on contents). The alias stage reads headers only and exits early.
  - `supplier_gln` → `manufacturerOperatorId`, gold `NO_MAPPING` (R4.3: a supplier need not be the manufacturer).
- **Fuzzy errors (8):** distractor columns that should map to nothing: `description`, `weight_uom`, `has_batch_no`, `has_serial_no`, `descript`. Several score 100, so no threshold removes them.
- **Decision:** the gold standard follows the rulebook, so it was not changed. Aliases and matchers were not changed to remove these errors. They are findings for the evaluation chapter, not defects to tune away.

### D29 — Demonstration run
- **Command:** `python -m scripts.demo --real-model --file data\dev\manufacturer_b_erpnext.csv`, plus the built-in sample.
- **Outputs:** `demo_run_b.txt`, `demo_run_sample.txt`.
- **Setup:** real 54-field CDM, thresholds from the frozen config, calibrated confidence, review band 0.9608. These runs are demonstration only and are not an evaluation.

### D30 — Freeze record
- **Tag:** `freeze-v1.0`
- **Commit:** `d8576689eca7aa0ab9759a548ceb6c32c4a33e89`
- **Check output:** READY TO FREEZE. Sealed directory empty at freeze, working tree clean, 9 gold standards present.
- **Frozen artefacts and hashes:** paste the contents of `decisions_freeze_record.json` here.
- **After this point:** no change to frozen artefacts. Held-out data may now be added to `data/heldout` (D18).
