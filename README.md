# CPAM dental prevention analysis

Does the French health insurance system's restriction of periodontal treatment
reimbursement to diabetic ALD patients hold up against its own evidence and its
own accounts?

Short answer: the clinical and consistency case holds; **the economic case does
not**, and this analysis is partly a negative result.

## What's here

| File | What it does |
|---|---|
| `build_series.py` | Builds a tidy multi-year panel from CNAM's annual CCAM act files |
| `build_departements.py` | Builds a département-level panel of dental activity |
| `cost_model.py` | Cost-avoidance model with sourced inputs and explicit bounds |
| `NOTE.md` | The policy note (French) — the actual deliverable |
| `parodontie.html` | Standalone chart: reimbursed vs unreimbursed periodontal acts |
| `out/ccam_panel.csv` | 53,414 rows, one per year × act code, 2015–2025 |
| `out/dept_panel.csv` | 505 rows, one per year × département, 2020–2024 |
| `out/cost_model_output.txt` | Model output as run |
| `out/actes_parodontaux_non_rembourses_2025.csv` | The seven acts still at €0 |

## Getting the source data

Nothing here ships CNAM's files; download them yourself so the chain is clean.

1. Go to `assurance-maladie.ameli.fr/etudes-et-donnees`
2. Search `CCAM`, open **"Actes techniques de la CCAM - 2015 à 2025"**,
   download every year
3. Open **"Activité et prescriptions des chirurgiens-dentistes libéraux par
   département"**, download every year
4. Put them all in one folder and point `SRC` in both build scripts at it

Both datasets are Licence Ouverte.

## Running it

```bash
pip install pandas openpyxl xlrd
python build_series.py        # -> out/ccam_panel.csv
python build_departements.py  # -> out/dept_panel.csv
python cost_model.py          # -> stdout
```

## Three things worth knowing before you trust a number

**Aggregate on `code_acte` before summing anything.** The source carries one row
per code × activity × phase. Raw sums double-count. The 2015 détartrage figure
reconciles with HAS's published 2016 figure (21.6M vs 21.5M) only after
aggregation — that reconciliation is the check that the pipeline is right.

**Volumes of an unreimbursed act measure coding, not need.** HAS says so
explicitly in the 2018 report. Any inference from act counts has to carry that
caveat.

**The département files have one row per practitioner category plus a TOTAL
row.** Summing raw rows double-counts. `build_departements.py` keeps the total
row only.

## Known gaps

- 2016, 2017, 2021 and 2023 are missing from the CCAM series
- The département panel starts at 2020: 2017 and 2018 split NGAP and CCAM into
  separate columns under different labels, and forcing that join would need its
  own mapping note
- The effect size driving the cost model is Danish, and measures periodontal
  therapy broadly rather than the French DSR act

## Licence

Analysis code: do what you like with it. Source data remains under CNAM's
Licence Ouverte; cite them, not this repository.
