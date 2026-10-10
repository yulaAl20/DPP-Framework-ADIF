# methodology.md — the chapter that writes itself
**Last updated:** 2026-10-08
**Supersedes:** the 2026-08-06 revision. Changes are listed in §0 so you can see what moved and why, rather than diffing two long documents.

---

## 0. What changed since 2026-08-06, and why

| # | Change | Driver |
|---|---|---|
| 1 | Phase 4 status: *Not started* → **complete** (14 modules, 118 automated tests) | The prototype exists |
| 2 | **ESPR Annex I → Annex III** wherever DPP *data elements* are meant | Annex III is the DPP annex (Art. 9(2)(a) refers data content "pursuant to Annex III"); Annex I is the product-parameters list. Verified against the consolidated text — see sources.md |
| 3 | Schema inventory: 3 evaluation schemas → **3 development + 3 held-out** | decisions.md **D23** — the ERPNext and Odoo schemas were contaminated during value-signature work and were reassigned to development |
| 4 | ADID URI shape corrected to a **composite variant segment** | `/adid/{family}/{colour}/{size}` and project.md's `/adid/{family}/{variant}/{instance}` were ambiguous at depth 3. Resolved in `adid/grammar.ebnf` |
| 5 | ADID conformance target is **open, and now points at IEC 61406 rather than GS1 Digital Link** | EN 18219:2026 permits five identifier schemes; ADID issues a self-issued link under the manufacturer's own domain |
| 6 | Metric 2 denominator **restricted to mandatory fields the gold standard maps**, plus a reported *coverage ceiling* | The prose already said "restricted to fields the source schema actually has data for"; the code did not. Code and prose now agree |
| 7 | Ablation ladder: 3 conditions → **4** (pending D20) | decisions.md **D19** retained the value stage, which adds a rung |
| 8 | Ground-truth rulebook: "exists in draft" → **compiled as `goldstandard/RULEBOOK.md` v1.0**, committed before any ground truth was written | project.md §11 |
| 9 | CDM figures stated concretely: **54 fields, 4 mandatory**, clause-level provenance for every field | The CDM was built |
| 10 | Layer 3 described as **four** stages under a strict cascade | decisions.md **D17**, **D19** |

Results section remains deliberately empty. Nothing in this revision adds a number that was not measured.

---

## 1. Research paradigm

Design Science Research. **Hevner et al. (2004)** for rigour (seven guidelines — full compliance table in Ch3). **Peffers et al. (2007)** DSRM for the six-phase process. Evaluation strategy: **FEDS** (Venable, Pries-Heje & Baskerville, 2016) — this study's evaluation is ex-post, summative and **artificial** (controlled schemas, not a live factory deployment). A naturalistic evaluation — practitioner review by Sri Lankan apparel exporters — remains future work and a stated limitation, not something claimed here.

Contribution type: **exaptation** (Gregor & Hevner, 2013) — established schema-matching techniques extended into the DPP compliance domain. The novelty claimed is the apparel DPP alias vocabulary, the calibrated confidence model, the template/drift mechanism and the offline SME-context packaging. **Not** the matching cascade itself.

### A claim this revision can now make, and should
The artefact was specified and built before CEN/CENELEC JTC 24 published six DPP standards on 27 May 2026, and it lands in the same architectural space as EN 18223 (shared data model container) and EN 18216 (REST over HTTPS). Independent convergence on a published standard is a **convergent-validity argument** for the design, and belongs in Ch5/Ch6 rather than being left for an examiner to notice. See sources.md and §6 below for what this does to research gap #6.

---

## 2. Six phases — status

| # | Phase (Peffers, 2007) | Activity in this study | Status | Notes |
|---|---|---|---|---|
| 1 | Problem identification & motivation | Structured concept-matrix literature review | Done | Chapters 1–2 drafted. **Gap #6 must be restated** — see §6 |
| 2 | Objectives of a solution | SMART objectives, RQs, CDM coverage criterion | Done | Current wording supersedes the original proposal; confirm with supervisor whether that needs a note |
| 3 | Design & development — specification | ADID / CDM / gateway architecture fixed ahead of code | **Done** | Ch3 document text still not updated to match D9, D17, D19, D23, D24 and the corrected URI. **Figure 1 must be redrawn** (it shows parallel matchers; the design is a cascade) |
| 4 | Design & development — implementation | Prototype build, M1–M14 | **Complete** | 14 modules; 118 automated tests passing; offline after setup; every run record carries provenance hashes |
| 5a | **Demonstration** | End-to-end walkthrough: one development schema → resolved DPP record | **Harness ready, run not captured** | `scripts/demo.py`. Separate activity from Evaluation (D14). Needs logs, screenshots and the output JSON-LD captured for Ch4 |
| 5b | **Evaluation** | Ablation-ladder comparison across held-out schemas | **Blocked** | Blocked on four things in order: grid-searched thresholds (D11) → fitted calibrator (D6) → freeze commit → held-out schemas and their ground truth. Do not reorder these; the ordering *is* the anti-circularity argument |
| 6 | Communication | Dissertation, research paper, viva | Not started | |

---

## 3. Framework architecture (current)

### Layer 1 — ADID (identity)
Three levels: **family** (the design, e.g. "Top A") / **variant** (one colour+size combination) / **instance** (one physical unit).

- Family has **no native GS1 identifier**. This is ADID's actual contribution — not a restatement of GS1.
- Variant = one GTIN each. A GTIN never represents a whole family.
- Instance = GTIN + serial number = SGTIN.
- **URI shape (corrected):** `https://dpp.{manufacturer}/adid/{family}/{colour}_{size}/{serial}`

The variant is a **single composite segment**, colour and size joined by an underscore, with hyphen as the intra-value separator. This resolves a real ambiguity: with `/adid/{family}/{colour}/{size}`, the path `/adid/top-a/navy/M` was indistinguishable from `/adid/{family}/{variant}/{instance}`. Path depth is now unambiguous — 1 = family, 2 = variant, 3 = instance. Formal grammar: `adid/grammar.ebnf`.

Descriptive attributes — material, origin, season, care instructions — are deliberately absent from the path. They describe an item; they do not distinguish *which item is being addressed*. Putting them in the path would mean a data correction changes the identifier and invalidates every printed QR code (decisions.md **D9**).

**Conformance — open, and the question has changed.** EN 18219:2026 permits five identifier schemes: GS1 Digital Link URI, **IEC 61406 self-issued links**, W3C DIDs, RFID/2D identifiers, and DOIs. ADID issues a URI under the manufacturer's own domain, which is structurally a self-issued link — so project.md §13's open decision ("compliant GS1 Digital Link profile vs compatible extension") may be asking the wrong question. Until EN 18219 is read, ADID claims **GS1 Digital Link *compatible* (an extension), not compliant**, and records IEC 61406 as a *candidate* scheme with no claim asserted. `GET /adid/conformance` returns this machine-readably, with `"claim": null` for EN 18219 (FR-11.7). Unverified claims are recorded as unverified rather than implied by silence.

**Batch level — unresolved (D22).** ESPR Art. 9(2)(d) names model, batch and item level; UNTP carries `batchNumber`; apparel manufacturing is batch-organised (dye lots, cut tickets, shipment lots). ADID has no batch level, and five CDM fields are naturally batch-scoped. The current state is option 3 — batch as CDM *data* rather than ADID *identity* — arrived at by default rather than by decision. **Decide it before the freeze**; an unlogged default is the one an examiner finds. Full write-up in `cdm/ALIGNMENT.md`.

### Layer 2 — CDM (data)
W3C JSON-LD. **54 fields, 4 mandatory** (`productFamily`, `productIdentifier`, `manufacturerOperatorId`, `fibreComposition`).

Synthesised from **ESPR Annex III ¶1 (a)–(k)**, expanded through Art. 7(5) (substances of concern) and Art. 5(1) (sixteen product aspects); **GS1 EPCIS 2.0** event attributes; **UNTP** credential semantics; and **Regulation (EU) 1007/2011** for fibre composition. Procedure as specified: competency questions → term extraction per source → alignment table (conflict and granularity resolution) → precedence rules → alias vocabulary. Executed; written up in `cdm/EXTRACTION.md` and `cdm/ALIGNMENT.md`.

Provenance by source: **ESPR 35, UNTP 11, EPCIS 2.0 4, EU 1007/2011 1, ADIF-originated 3.** Every field carries `x-adif: {source, clause, granularity}`, so any field can be traced to a clause rather than to an assertion. Alias vocabulary: 222 entries across all 54 fields, normalised with the same function as incoming headers (otherwise Stage 1 could never fire) and rejected at load time if two fields claim the same normalised key (otherwise Stage 1's result depends on dictionary ordering — an NFR-5 reproducibility failure).

Precedence rules, applied in order where two sources describe the same concept: (1) ESPR wins on anything legally mandated; (2) EPCIS wins on event and lifecycle structure; (3) UNTP wins on verification and credential semantics; (4) where a source adds qualifying detail rather than a competing name, **keep both** (a carbon figure and its declared unit are two facts, not one).

**The mandatory set is deliberately small, and that is now defensible by citation rather than by taste.** The ESPR textiles delegated act is **not adopted** (verified — see sources.md). No binding list of mandatory DPP attributes for textiles exists. Marking all eleven Annex III points mandatory would have asserted a legal requirement that does not exist.

Two distinct "80%" claims, separately named (decisions.md **D12**) — and the separation now has a verified justification, because there is no regulatory mandate to measure against:
- **Reference attribute set coverage** (design-time) — the CDM schema covers ≥80% of a *constructed* reference attribute set, built from ESPR Annex III ¶1 and the Commission's preparatory documentation plus CIRPASS outputs. Verified once, when the CDM is built.
- **ESPR-mandatory field match rate** (runtime, Metric 2 below) — the proportion of that reference set actually populated correctly for a *given input schema*. Deliberately differently named so the two 80% figures do not read as one claim restated.

### Layer 3 — Hybrid gateway (method)
CSV / Excel / JSON ingestion → schema analysis (type inference, value sampling, duplicate-header handling) → **four-stage cascade** → calibrated confidence → reusable manufacturer templates → ADID-structured JSON-LD over a REST API.

**Strict fallback cascade with early exit** (decisions.md **D17**), not parallel weighted fusion:

1. **Stage 1 — alias lookup.** Exact match, normalised header against normalised alias. Deterministic.
2. **Stage 2 — fuzzy similarity.** RapidFuzz; `ratio`, `token_sort_ratio`, `partial_ratio`.
3. **Stage 3 — semantic similarity.** `all-MiniLM-L6-v2`, offline, revision pinned and recorded in every run (FR-5.5). Encodes the field *description*, not the field name, because the model is trained on natural language.
4. **Stage 4 — value-based matching.** Invoked **only** when every header-based stage returned nothing (FR-6.3). Scores sampled values against controlled vocabularies and patterns (ISO 3166, fibre names per Reg. 1007/2011, units, certification identifiers, percentage composition, ISO dates, GTIN check digits).

Confidence is **post-hoc Platt scaling, fitted per stage** (decisions.md **D6**; isotonic needs more data than this study has). A raw similarity score is never reported as a confidence. The calibrator refuses to borrow another stage's curve: if a stage has no fitted curve, it is reported as uncalibrated rather than silently scored against someone else's mapping.

Conflict resolution, when two columns claim one CDM field, is by **stage precedence first** (template > alias > fuzzy > semantic > value), then raw score, then source position (decisions.md **D24**). An exact match against a curated vocabulary is stronger evidence than an inference from data shape, and the cascade order already encodes that.

**The limitation this design accepts, and Ch6 must state:** a cascade cannot recover from a confident wrong alias hit. Once Stage 1 accepts, Stages 2–4 never see the field. FR-7.5's conflict detection catches only the subset where two columns claim the same CDM field; it does not catch a single confidently-wrong alias.

---

## 4. Evaluation plan

### 4.1 Schema inventory — development vs held-out (D23)

The original plan had three evaluation schemas and "scratch schemas" for threshold tuning that were never specified. It now has an explicit split, which is a methodological **strength to claim in Ch3**, not an embarrassment to bury.

**Development set** — tuning, value-signature design, calibration fitting. Opened, inspected, iterated on freely.

| Schema | Source | Columns |
|---|---|---|
| `manufacturer_a` | Small-exporter style sheet | 7 |
| `manufacturer_a_drift` | Season-two variant of the above | 6 |
| `manufacturer_b_erpnext` | ERPNext open-source ERP item field list | 22 |
| `manufacturer_b_erpnext_drift` | Season-two variant | 21 |
| `manufacturer_c_odoo` | Odoo `product.template` field list | 22 |
| `manufacturer_c_odoo_drift` | Season-two variant | 21 |

99 columns, **51 mapping decisions** in the development gold standard.

**Held-out set** — evaluation only, constructed and opened **after** the freeze commit.

| Schema | Source | Status |
|---|---|---|
| H1 | Fashion Product Images Dataset, `styles.csv` (Kaggle, paramaggarwal) | Download-and-seal per **D18**: fetch, record file SHA-256, place in `data/heldout/` **unopened**. Column list confirmed at evaluation time and reported in Ch6 — not before |
| H2 | Dolibarr product field list, or a GOTS/OEKO-TEX certification form | To be built |
| H3 | A buyer tech-pack template | To be built |

Plus season-two drifted variants of each, for the template-reuse test (D8).

**Construction rules, unchanged and load-bearing:**
- Source material for constructed schemas is **manufacturer-side documentation only** — open-source ERP field lists, buyer tech-pack templates, certification forms. **Never** ESPR / GS1 / UNTP documents (circularity guard, **D3**).
- Held-out schemas are built **without inspecting per-column matcher output**. This is the rule D23 was written because I broke.
- `data/heldout/` is declared in `config/default.yaml` as `heldout_dir` so the evaluation tooling can refuse it by path. `eval/grid_search.py` and `eval/fit_calibration.py` both exit rather than read from it, and an acceptance test asserts they do.

**Declared prior contamination, to state in Ch3 rather than leave to be found:** sources.md records prior awareness of a `masterCategory` field in `styles.csv`. That is minor, it has already occurred, and it is declared.

### 4.2 Metrics

Targets are tentative pending supervisor sign-off. All four are computed per condition per schema.

**Metric 1 — Mapping accuracy (F1)**, at field-mapping level. TP = correct canonical target proposed; FP = wrong target proposed; FN = mappable field missed. Macro-F1 across schemas. *Target: ≥ 0.85.*

**Metric 2 — ESPR-mandatory field match rate.** Proportion of mandatory CDM fields correctly populated in the output JSON-LD, **with the denominator restricted to mandatory fields the gold standard actually maps for that schema**. A schema whose source data contains no fibre composition cannot be penalised for not producing one — that is a property of the input, not of the matcher. *Target: ≥ 80% per schema.*

Reported alongside it: the **mandatory coverage ceiling** — the highest Metric 2 an unrestricted calculation could reach on that schema. Reporting the ceiling next to the score is what stops the restricted denominator looking like a thumb on the scale. A schema with a ceiling of 0.75 and a score of 0.75 is a complete success *and* a demonstration that the input schema cannot carry a compliant passport, which is itself a finding.

**Metric 3 — Confidence calibration (ECE).** 5 bins, **pooled across all schemas** (per-schema bins would be too small to interpret). Reliability diagram reported alongside the scalar. *Target: ECE ≤ 0.10.*

**Metric 4 — Template reuse rate.** Fraction of *unchanged* fields correctly auto-remapped on a **drifted** second upload, never an identical one (D8). *Target: ≥95% on unchanged fields; delta-field F1 ≥ 0.80.*

**Review burden** (decisions.md **D16**) — at the chosen acceptance threshold, the fraction of fields per schema falling below it and routed to the review UI, reported per ablation condition. This falls out of data already collected for Metric 3: no new participants, no new metrics infrastructure, no new ethics submission. A full usability study is future work. The API also records what reviewers *did* with those fields — accepted, retargeted, supplied manually, rejected — yielding a manual-effort rate (FR-8.8).

**Mean reciprocal rank** (FR-14.7) is instrumented and reported as supplementary diagnostic, not as a headline metric. It answers "when the top candidate was wrong, was the right answer nearby?", which is the difference between a tuning problem and a representation problem.

### 4.3 Baseline — ablation ladder (D10, amended by D19; count open under D20)

Each condition measured with all four metrics on every held-out schema:

| # | Condition | Config |
|---|---|---|
| a | **Fuzzy-only** — RapidFuzz alone, no alias table, no embeddings | `config/ablation/fuzzy_only.yaml` |
| b | **Alias + fuzzy** — Stages 1–2 | `config/ablation/alias_fuzzy.yaml` |
| c | **Full cascade** — Stages 1–3 with calibrated confidence | `config/ablation/full_cascade.yaml` |
| d | **Full cascade + value** — Stages 1–4 | `config/ablation/full_cascade_value.yaml` |

ΔF1 reported per step (b−a, c−b, d−c, and d−a overall), attributing gain to each **added stage** rather than lumping the whole cascade against a single strawman. The original hypothesis still holds — the gap should widen as schema heterogeneity increases — and now *which stage* does that work is visible too. `eval/metrics.py` also reports **per-stage surviving hit counts**, so a stage that fires often but loses every conflict is distinguishable from one that never fires.

**Open — D20.** project.md §7 and §14 specify **five** conditions (`exact_only`, `semantic_only` additionally); D10 specified three; D19 makes the cumulative ladder four. Four config files exist. Recommendation on file: run the four-rung ladder, drop `exact_only` (close to the strawman D10 rejected), and if time allows add `semantic_only` **as a supplementary condition reported separately from the ladder** — it answers a real question (would embeddings alone have sufficed?) but is not a rung, and each extra condition costs schemas × metrics × drift variants in scored cells. **Decide, then amend whichever document is wrong so the two stop disagreeing.**

### 4.4 Threshold selection (D11)

Stage 2, 3 and 4 acceptance thresholds and the confidence bands are set by **grid search on the development schemas, optimising macro-F1**, run after Phase 4 and before Phase 5b. Never tuned on the held-out set.

Enforcement, because a process rule that is only written down is a rule that gets broken on a tired evening:
- Every threshold in `config/default.yaml` is `null`. Reading an unset tunable raises `UnsetTunable`; it never silently defaults. An automated test asserts they are still null.
- `eval/grid_search.py` refuses to run against `heldout_dir`, and refuses to run with the **stub embedder** — deriving a semantic threshold from a hash-based placeholder would produce a number that looks derived and is not.
- The derived values are **hand-copied** into `config/default.yaml` and logged in §5 below with their date and the search range. The config file records its own SHA-256 in every run record.

**No values exist yet.** Do not write placeholder numbers into the thesis. §5 is empty for this reason, not by oversight.

### 4.5 Ground truth

**Rulebook-governed.** `goldstandard/RULEBOOK.md` v1.0 — six rules covering cardinality, distractor and uncovered-field handling, ambiguity resolution, and when a column maps to nothing. Compiled, and **committed before any ground truth written against it**. That ordering is not cosmetic: it is the evidence that the rulebook governed the decisions rather than being written afterwards to justify them. The commit history is the artefact that proves it.

Frozen and version-controlled before any run. Each gold-standard file records its `frozen_at` date and the rulebook version it was decided under.

**≥25% of entries per schema independently checked by a second rater**, using only the rulebook and the CDM field list — deliberately **not** the perturbation log, so the check is not circular. Agreement rate reported; *target ≥90% pre-adjudication*. Harness: `scripts/second_rater.py`. **Not yet booked.**

### 4.6 Freeze discipline (project.md §11)

The ordering below is the anti-circularity argument, and the git history is the only evidence of it. `scripts/freeze.py --check` performs the mechanical preconditions; it checks what can be checked mechanically and says so, rather than certifying intent.

1. CDM schema, alias vocabulary, value signatures, config and rulebook frozen.
2. **Freeze commit, tagged and dated.**
3. Held-out schemas constructed.
4. Held-out ground truth written.
5. Evaluation runs.

Current state: steps 1 and 2 pending the grid search and calibrator fit, since the config is part of what gets frozen. Nothing in `data/heldout/` yet, which is the correct state.

---

## 5. Results

_Nothing yet. This project is pre-data-collection. **Do not fill this section with placeholder, illustrative or anticipated numbers.**_

Log real results here, dated, as each run actually happens. One row per run:

> date · schema · condition · metric values · config SHA-256 · model revision · one line on anything surprising

The first entries to appear here will be the grid-search outcome (date, search range per stage, selected thresholds, macro-F1 at the optimum on the development set) and the calibration fit (observations per stage, fitted parameters, ECE on development data). Both are *development-set* results and must be labelled as such — they are not evaluation findings and must never be reported as if they were.

---

## 6. Standing corrections to Chapters 1–3

Carried here so they are not lost between document revisions.

1. **Research gap #6 must be restated.** As written it claims the key standards "have never been realised in one unified transformation architecture." EN 18223:2026 now defines exactly that container, and an examiner can disprove the gap with one search. The gap survives in a **sharper** form, because the published standards explicitly do *not* specify identifier **granularity** and do *not* specify product **attributes** ("attributes belong to sectoral acts, not JTC 24 standards"). Restated: *the standards specify the plumbing — identifiers, carriers, APIs, access control — but no apparel-sector attribute model exists, no identifier granularity is defined, and no open SME-accessible implementation targets this context.* All three are what ADIF supplies.
2. **Annex I → Annex III** wherever DPP data elements are meant (Ch1, Ch2, Ch3, research objectives doc). Both annexes are relevant; only Annex I is currently cited.
3. **Figure 1 must be redrawn.** It shows name-, structure- and instance-based matchers in **parallel**; the design is a **cascade** (D17). Its "instance-based matching" box now maps to a stage that exists (Stage 4 ≈ Rahm & Bernstein's instance-based category). Its "structure-based matching" box corresponds to nothing implemented — nested/hierarchical input is an explicit scope exclusion (project.md §2).
4. **Ch1 must not describe the EU DPP registry as forthcoming** if the reports of it going live on 20 July 2026 are correct. Unverified; the scope exclusion stands either way.
5. **FR-11.6** (support all three granularity levels so the artefact survives whichever the delegated act selects) is **not** defensive over-engineering — it is the correct response to a live legal uncertainty, and that can now be said with a citation.
6. **Vendor neutrality is mandated by the regulation, not asserted by this thesis.** ESPR Art. 10(1)(d) requires DPP data to be open-standards-based, interoperable, machine-readable, structured, searchable and transferable "without vendor lock-in". This is the strongest available support for the thesis title and currently goes uncited.
