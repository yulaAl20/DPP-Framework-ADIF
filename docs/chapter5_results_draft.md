# Chapter 5 — Evaluation results (DRAFT)

**Status of this draft.** Every number below comes from the four run records
listed in decisions.md D34, recomputed with `eval/summarise_run.py` (D35), or
from the answer keys and agreement files. Statements marked *[interpretation]*
are readings of the numbers, not measurements; edit them to your own argument.
**[CITE]** marks a place where a reference belongs. I have not supplied
citations; take them from your own literature review. **[FILL IN]** marks facts
only you can supply.

---

## 5.1 Evaluation set and procedure

The gateway was frozen at tag `freeze-v1.0` (2026-10-10) with thresholds and a
calibrator derived only on the development schemas (D25, D26). The held-out set
was added after the tag (D31) and comprises five schemas (three base schemas
and two drifted variants):

| Schema | Columns | Mappable (gold) | Source |
|---|---|---|---|
| H1 `kaggle_styles` | 10 | 2 | Kaggle Fashion Product Images metadata (MIT licence), repaired file (D32) |
| H2 `heldout_h2_dolibarr` | 26 | 8 | Dolibarr-style product export, compiled (D31) |
| H2 drift | 25 | 8 | seeded perturbation of H2 |
| H3 `heldout_h3_techpack` | 23 | 12 | buyer tech-pack lines, compiled (D31) |
| H3 drift | 22 | 12 | seeded perturbation of H3 |

Ground truth was written by the primary rater from the rulebook alone, before
any run on these schemas, and committed before the evaluation commit
(`ef89aa7`). An independent second rater (LiviruM) answered a blank, seeded
sample of 17 of the 59 base-schema columns, with 17/17 pre-adjudication
agreement (H2 8/8, H3 6/6, H1 3/3; target 90%, D33).

The ladder adds one stage at a time: fuzzy only; plus alias; plus semantic
(`full_cascade`); plus value (`full_cascade_value`). A supplementary
semantic-only condition is reported outside the ladder (D20) as the AI-only
comparison.

## 5.2 Metric 1 — field-mapping accuracy

**Table 5.1 — F1 by condition and schema**

| Schema | Fuzzy only | + Alias | + Semantic | + Value | Semantic only |
|---|---|---|---|---|---|
| H1 Kaggle | 0.400 | 0.400 | 0.400 | 0.400 | 0.000 |
| H2 Dolibarr | 0.500 | 0.500 | 0.500 | 0.556 | 0.000 |
| H2 drift | 0.375 | 0.375 | 0.375 | 0.444 | 0.000 |
| H3 tech-pack | 0.667 | 0.762 | 0.818 | 0.870 | 0.154 |
| H3 drift | 0.762 | 0.762 | 0.818 | 0.870 | 0.154 |
| **Macro-average** | **0.541** | **0.560** | **0.582** | **0.628** | **0.062** |

**Table 5.2 — macro-averaged precision, recall and MRR**

| Condition | Precision | Recall | MRR |
|---|---|---|---|
| Fuzzy only | 0.575 | 0.525 | 0.664 |
| + Alias | 0.597 | 0.542 | 0.672 |
| + Semantic | 0.602 | 0.575 | 0.666 |
| + Value | 0.610 | 0.658 | 0.674 |
| Semantic only | 0.400 | 0.033 | 0.290 |

**Per-stage contribution (delta-F1, per schema).** Adding the value stage
raised F1 by +0.056 (H2), +0.069 (H2 drift), +0.051 (H3 and H3 drift) and 0.000
on H1. Adding the semantic stage raised F1 by +0.056 on H3 and H3 drift and 0.000
elsewhere. Adding alias raised F1 by +0.095 on H3 and 0.000 elsewhere.

*[interpretation]* Gains are modest but monotone over the ladder on the two
larger schemas, and most of the macro gain comes from recall (0.525 to 0.658)
with precision nearly flat (0.575 to 0.610). The stage that adds most on H2 is
the value stage, consistent with H2 having columns whose headers carry little
meaning but whose values do. The H1 schema shows no stage effect; with 10
columns and 2 mappable, one column moves its F1 by 0.1 or more, so H1 is
reported but contributes no ladder evidence.

**Drift.** Under header drift the full system lost 0.111 F1 on H2
(0.556 to 0.444) and none on H3 (0.870 and 0.870).
*[interpretation]* Renamed headers cost H2 its direct matches; H3's renamed
headers stayed within reach of the later stages.

## 5.3 AI-only comparison

The semantic-only condition reached macro F1 0.062 (precision 0.400, recall
0.033, MRR 0.290; 0.154 on H3 and H3 drift, 0.000 elsewhere). *[interpretation]*
Embedding similarity alone, at the frozen threshold, finds almost nothing the
rules and fuzzy matching do not; the cascade's value lies in the cheap stages
doing the bulk of the work and the later stages filling gaps. Whether a
different threshold would help semantic-only was not tested; the threshold was
tuned on the cascade (D25).

## 5.4 Metric 2 — mandatory-field match

Restricted to mandatory fields the schema has data for (D36), the match rate was
0.50 on H2 and H2 drift and 1.00 on H3 and H3 drift for every ladder condition,
with a coverage ceiling of 0.50 for H2 and H3 (half of the mandatory CDM fields
appear in either schema). H1 contains no mandatory field, so its rate is
vacuous and is excluded. *[interpretation]* The ladder did not change which
mandatory fields were populated; its gains were in non-mandatory fields. The
ceiling itself is a finding: the two SME-style exports supply only half of the
mandatory attributes, so no mapper can fill the rest from that data **[CITE
ESPR Annex III as the source of the mandatory set]**.

## 5.5 Metric 3 — confidence calibration and review burden

Pooled over all ladder conditions and schemas, ECE was 0.054. Only two
reliability bins were populated: confidence 0.44 against accuracy 0.50 (n = 88)
and confidence 0.88 against accuracy 0.84 (n = 70).

Caveats the text must carry: the pooled pairs repeat each column once per
condition that maps it, so the effective sample is smaller than 158; calibration
for the value and semantic stages rested on 16 and 2 development observations;
and the semantic-only record's ECE of 0.029 rests on two pairs and is not
evidence of calibration.

**Review burden** (share of columns routed to a human, review band 0.9608, D27)
was 1.00 for the fuzzy-only and alias conditions, 0.98 for `full_cascade` and
0.93 for `full_cascade_value`. *[interpretation]* The calibrated confidence is
informative (accuracy rises with confidence), but on the development data
only the 18 mappings from the value stage (16) and the semantic stage (2) cleared
the 90%-accuracy review band, so the system in its frozen form still sends almost every column to a person. The value of the
gateway on this evidence is a ranked, pre-filled proposal, not autonomous
mapping.

## 5.6 Metric 4 — template reuse on a drifted upload

Each drifted schema has 5 changed columns (renamed or new) and either 20 (H2) or
17 (H3) unchanged columns.

**Table 5.3 — reuse with a template built from the system's own (uncorrected) output**

| Condition | H2: unchanged columns reused correctly | H3: unchanged columns reused correctly |
|---|---|---|
| Fuzzy only | 2/6 | 6/9 |
| + Alias | 2/6 | 6/9 |
| + Semantic | 2/6 | 7/9 |
| + Value | 3/6 | 8/9 |

(Counts are over unchanged **mappable** columns: 6 in H2 and 9 in H3.)

Delta-field F1 on the changed columns was 0.500 (H2, 2 mappable new columns)
and 0.667 (H3, 3 mappable new columns) in every condition.

With a reviewer-corrected template, reuse of unchanged columns was 6/6 and 9/9 in
every condition. That is true by construction (the system looks up an answer it
was given) and is **not** a result (D36).

*[interpretation]* The informative figure is how much of a template survives
when it was built from uncorrected system output, which rises with the
ladder (H3: 6/9 to 8/9). The delta-field F1 rests on 2 and 3 columns, so it is
reported as counts and carries no statistical weight.

## 5.7 Development-set error analysis

On the development schemas the full cascade's per-stage accuracy was alias
27/31 (87.1%), fuzzy 2/10 (20.0%), semantic 1/1 and value 16/16 (D28).
All twelve errors were retained as findings rather than corrected:

- *Alias, 4 errors (2 distinct):* `Style_No` mapped to `productIdentifier`
  where the gold standard says `gtin` (the values are check-digit-valid
  barcodes; a header-only stage cannot see this), and `supplier_gln` mapped to
  `manufacturerOperatorId` where the gold standard says `NO_MAPPING`
  (rulebook R4.3: a supplier need not be the manufacturer).
- *Fuzzy, 8 errors:* distractor columns that have no CDM target
  (`description`, `weight_uom`, `has_batch_no`, `has_serial_no`, `descript`)
  matched to similar-looking fields, several at score 100, so no threshold
  separates them.

*[interpretation]* The two failure families correspond to rulebook R3
(meaning, not resemblance): string similarity cannot tell a flag, a unit or a
label from the value it resembles. The value stage, which reads contents, was
the only stage without errors on the development data.

## 5.8 Threats to validity and limitations

State each plainly:

1. **Small evaluation set.** Five schemas (three independent), 59 base-schema
   columns, 22 of them mappable. Differences of a few F1 points are one or two
   columns.
2. **Two of three base schemas were compiled by an AI assistant that knew the
   system** (D31). Headers came from source vocabulary and the matcher was not
   run on them, but independence from the CDM is argued, not proven. Their
   headers have not been checked against a live Dolibarr instance **[FILL IN
   when done]**.
3. **One primary rater, one second rater, 17 sampled rows.** Agreement was 100%
   on that sample (D33), which is encouraging but cannot establish the key's
   accuracy on the unsampled 42 columns.
4. **Header-only drift.** Drift was simulated by renaming and dropping columns;
   it does not model value-format changes or semantic redefinition.
5. **Calibration** rests on development observations of 93 (alias), 71 (fuzzy),
   16 (value) and 2 (semantic), pooled across four conditions (D26); the review
   threshold was derived in-sample (D27).
6. **Procedure.** The Kaggle second-rater check was completed after the
   evaluation run (D34); the answer key was not changed. A post-freeze defect
   in the stored ablation deltas was worked around, not fixed (D35). The loader
   fails on a malformed export with a raw parser error (D32).
7. **Single run on one machine.** The pipeline is deterministic (seed fixed), so
   no variance across runs is reported; hardware is recorded in D37.

## 5.9 Summary

On five held-out schemas the frozen cascade reached macro F1 0.628, against
0.541 for fuzzy matching alone and 0.062 for embedding similarity alone, with
the gain concentrated in recall and in the value stage. Calibrated confidence
tracked accuracy (ECE 0.054, with the sampling caveats above) but the 90%
review rule still routes about 93% of columns to a person. Template reuse from
uncorrected output reached 3/6 and 8/9 on the two drifted schemas under the full
system. Second-rater agreement on the answer keys was 17/17. The principal
limitations are the small, partly AI-compiled evaluation set and the narrow
form of drift tested.
