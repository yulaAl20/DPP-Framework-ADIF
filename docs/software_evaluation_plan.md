# Evaluating the software artefact (not the matching model)

Metrics 1 to 4 evaluate the **matching model**. This plan evaluates the **software
as an artefact**: does it do what was specified, how well, and can the intended
users actually use it. It follows the usual Design Science split between
*technical* verification and *human* evaluation. **[CITE]** the frameworks you use;
three to check against your own literature review: Hevner, March, Park & Ram
(2004), MIS Quarterly, for the evaluation guideline; Venable, Pries-Heje &
Baskerville (2016), FEDS, European Journal of Information Systems, for choosing
when and how to evaluate; Brooke (1996) for the System Usability Scale. I have not
verified these citations.

## 1. Evaluation questions

| # | Question | Method | Evidence |
|---|---|---|---|
| E1 | Does it implement the stated functional requirements? | Automated tests plus a requirement-to-test trace | Test suite; trace table (below) |
| E2 | Does it meet the non-functional requirements? | Measurement on stated hardware | `docs/nfr_verification.md` |
| E3 | Does it work end to end on a realistic file? | Scripted scenario on the demo data | Screenshots and run output |
| E4 | Does it fail safely on bad input? | Negative tests | Table of cases and outcomes |
| E5 | Can intended users do the task with it, and faster or better than without it? | Small task-based user study | Times, error counts, SUS scores |
| E6 | Do experts judge it relevant and credible? | Structured expert walkthrough | Completed rubric |

## 2. E1: functional verification

1. Run the suite: `python -m pytest -q`. Record the count passed and skipped, the
   date and the commit. (At the time of writing: all pass, one deliberate skip while held-out files exist.)
2. Build a **requirement trace**: one row per FR in your requirements document,
   with the test or the demo step that covers it, and a status of covered,
   demonstrated only, or not covered. A gap is a finding, not an embarrassment. A
   starting point is the FR numbers cited in the source docstrings
   (`grep -rn "FR-" src`).
3. Re-run the acceptance tests with the **real** model cached, as
   `docs/nfr_verification.md` asks: `pytest tests/acceptance/test_nfr.py -v`.

## 3. E2: non-functional verification

| NFR | What to record | Status |
|---|---|---|
| NFR-1 offline | Real-model demo run with Wi-Fi off; the no-network acceptance test with the model cached | Demo done; record date, screenshot |
| NFR-3 hardware | i5-1135G7, 4 cores / 8 threads, 11.8 GB, no discrete GPU | Done (D37) |
| NFR-4 performance | End-to-end wall-clock for 50 columns x 1,000 rows **with the real model**, and for the 44,446-row file including file loading. The 0.16 s stub figure is not the headline | To do |
| NFR-5 determinism | Run the same evaluation twice; compare the metric sections of the two records, and hash the saved outputs | To do |
| NFR-6 externalised tunables | The acceptance test | Passing |
| NFR-8 Windows and Linux | Suite passes on both | Recorded; re-run on current commit |
| NFR-9 second machine | Clean install from `docs/setup.md` | To do |
| NFR-10 / NFR-11 | Docstring test; `docs/licences.md` complete | Check |

For NFR-4, time the **whole request** (upload through DPP), not only the cascade
stage times in the run records: the run records exclude file loading.

## 4. E3: end-to-end scenario

Use `demo/` (see `demo/README.md`). Script the scenario and capture each step:
upload, review table, correct one mapping, confirm and store the template,
generate a DPP, show the validation report, upload the next-season file and show
template reuse. This is the demonstration for Chapter 4. Mark it clearly as a
demonstration, not a measurement.

## 5. E4: negative and robustness tests

Each case is a file you create or already have. Record what the system did.

| Case | Expected behaviour |
|---|---|
| Malformed CSV (the Kaggle file, line 6044) | Observed: raw parser error. Record as a limitation |
| File over 25 MB or over 100,000 rows | Clear refusal (FR-1.7) |
| Nested JSON | 409/422 with a scope message |
| Latin-1 or semicolon-delimited CSV | Read correctly (FR-1.4, FR-1.5) |
| Empty file; header only; duplicate headers | Clear error, no crash |
| No family-level column mapped, then DPP | 422 with the explanation |
| Upload before thresholds are set | 409, not a guess |

## 6. E5: user study (the main evidence of usefulness)

**Before you recruit anyone, check whether your university requires ethics
approval or an exemption for usability testing with people, and get it.**

- **Participants:** 3 to 8 people close to the intended user: textile or
  merchandising students, SME staff, or anyone who handles product data. State
  honestly who they are. At this size the results are descriptive, not statistical.
- **Task:** map one realistic export (use a fresh file, not the demo file; a third
  invented export built the same way as `demo/`) to the CDM and produce one DPP record.
- **Design:** each participant does the task twice, once **with** the tool
  (proposals, review table) and once **without** it (a spreadsheet plus
  `CDM_FIELDS.txt`), on two different files of similar size. Alternate which
  condition goes first across participants.
- **Measures per participant:** time to complete; number of columns mapped
  incorrectly against your gold standard; number of corrections made in the tool
  (the app already logs reviewer edits, FR-8.8); and the System Usability Scale,
  completed after the tool condition.
- **Also collect:** think-aloud notes, any point where they stopped or asked for
  help, and one open question: "What would stop you using this at work?"
- **Report:** per participant, then medians. Say plainly that n is small.

### System Usability Scale

Ten statements, each answered 1 (strongly disagree) to 5 (strongly agree):

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

**Scoring:** for odd items subtract 1 from the answer; for even items subtract the
answer from 5. Add the ten results and multiply by 2.5, giving 0 to 100. A common
reference point is that about 68 is average **[CITE the source of that benchmark]**.

## 7. E6: expert walkthrough

Show the demo to your supervisor and, if you can, one or two practitioners (a
merchandiser, a compliance or IT person at a manufacturer). Give each a short
rubric rated 1 to 5 with a comment: relevance to the problem, correctness of the
DPP output, clarity of the review screen, realism of the data model, and what is
missing. Keep the completed forms as evidence.

## 8. Suggested order and time

1. E1 trace and NFR-4, NFR-5, NFR-9 measurements (one to two days)
2. E4 negative tests (half a day)
3. Ethics check, then recruit for E5 and run the sessions (one to two weeks)
4. E6 walkthroughs, then write up (two to three days)

## 9. What to say it does not show

The study is small and uses invented exports; the user study samples people near
the author; performance is for one machine. State these in Chapter 6 next to the
results.
