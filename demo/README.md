# Demonstration data

Two invented exports from a fictional knitwear manufacturer ("Demo Knit Works").
They exist to **demonstrate the app**. They are **not evaluation data** and must
never be copied into `data/dev` (tuning) or `data/heldout` (sealed). The
evaluation harness only reads the folders it is pointed at, so keeping them here
keeps them out of every run record.

All values are invented. Barcodes pass the GTIN-13 check digit.

| File | Rows x columns | Role |
|---|---|---|
| `demo_knitwear_export_spring.csv` | 10 x 19 | First upload: review, correct, confirm, save the template |
| `demo_knitwear_export_autumn.csv` | 10 x 19 | "Season two": 4 renamed headers, 1 dropped, 1 new. Upload after confirming spring, to show template reuse |

The files were **chosen to exercise every stage**, which is what a demonstration
is for. Do not report anything measured on them as a result.

## What you should see (deterministic stages, checked)

Spring, alias / fuzzy / value stages:

- **Alias hits:** `Design_Code`, `SKU`, `EAN13`, `Colour Name`, `Size Code`, `Origin`, `Batch No`, `Buyer PO`, `Factory`.
- **Fuzzy hits:** `Fabric Compostion` (typo), `Care Instr.`, `Net Weight (kg)`.
- **Value-stage rescue:** `Col_K` (an uninformative header) is recognised as an HS commodity code from its values.
- **A conflict:** `Made In` (country names) loses to `Origin` (country codes), and is flagged for review.
- **Distractors with no CDM target:** `Unit Price (USD)`, `Warehouse Bin`, `Last Updated`, `Internal Ref` should stay unmapped.

Autumn: the renamed columns (`Barcode No`, `Shade / Tone`, `Sz`, `Fibre Mix`) no
longer match by alias, so they route through the cascade and are flagged, the
dropped `Warehouse Bin` disappears, and the new `Recycled %` column appears.

**The semantic stage depends on the real embedding model.** These notes were
checked with the semantic stage off. Run the demo with `--real-model` and read the
semantic rows for yourself; if the real model maps a distractor, that is a
finding to show, not a defect to hide.

## Run it

Command line:

```powershell
python -m scripts.demo --real-model --file demo\demo_knitwear_export_spring.csv
python -m scripts.demo --real-model --file demo\demo_knitwear_export_autumn.csv
```

The web app:

```powershell
uvicorn src.api.main:app
```

Open <http://127.0.0.1:8000/review> and:

1. Upload `demo_knitwear_export_spring.csv`, with a manufacturer id such as `demoknit`.
2. Read the table: confidence, stage and "needs review" flags.
3. Change one dropdown (for example correct a distractor to no mapping), then click **Confirm mappings and save template**.
4. Click **Generate DPP for row 0**. Expect an ADID URI of the form `https://dpp.demoknit/adid/ts-1000/navy_m`, a passing validation report, mandatory match rate 1.0 and a JSON-LD document.
5. Upload `demo_knitwear_export_autumn.csv` under the same manufacturer id and show the stored template re-applying.
