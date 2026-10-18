# CPAM dental prevention analysis

Does the French health insurance system's restriction of periodontal treatment
reimbursement to diabetic ALD patients hold up against its own evidence and its
own accounts?

Short answer: the clinical and consistency case holds; **the economic case does
not**, and this analysis is partly a negative result.

## Read it

| | |
|---|---|
| **La note, graphique inclus** (français) | https://claude.ai/artifact/1wP2uPBSrCe7z34UBFat62 |
| The note as markdown | [`NOTE.md`](NOTE.md) |
| Source of the published page | [`out/note.html`](out/note.html) |

## The three findings

**Reimbursement, not clinical need, determines which periodontal acts happen.**
Surfaçage radiculaire (`HBGB006`) has never been reimbursed and grew 2× between
2015 and 2025 — the same as détartrage, which has always been covered. Two
near-identical acts that became reimbursable in 2019–2020 grew 58× and 445×.

**The restriction to diabetic ALD patients predates the evaluation that was meant
to inform it.** It was set by the convention of 21 June 2018. HAS reported in
December 2018, assessing DSR for "les patients ayant des parodontites
chroniques" with no population restriction. CNAM had commissioned that
evaluation in September 2017. It has never been revisited against it.

**The cost-avoidance argument fails by a factor of 110.** Five years of annual
DSR costs CPAM €929 per patient and recovers at most €13.72 in avoided
downstream reimbursement. Not because prevention doesn't work, but because CPAM
reimburses only €45 for an extraction and €60 for a prosthetic act — the real
cost of tooth loss falls on patients and complementary insurers, so there is
very little downstream CPAM spend to avoid.

## What's here

| File | What it does |
|---|---|
| `build_series.py` | Builds a tidy multi-year panel from CNAM's annual CCAM act files |
| `build_departements.py` | Builds a département-level panel of dental activity |
| `cost_model.py` | Cost-avoidance model with sourced inputs and explicit bounds |
| `NOTE.md` | The policy note (French) — the actual deliverable |
| `out/parodontie.html` | Standalone chart: reimbursed vs unreimbursed periodontal acts |
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
per code × activity × phase. Raw sums double-count: 2015 détartrage reads 41M
before aggregation and 21.6M after, and 41M is impossible on its face — one
scaling per 1.6 people in France per year.

**Don't use HAS's Table 9 as a reconciliation check.** It is tempting, and it is
wrong. HAS reports 2016 counts of 21,519,927 détartrages, 3,922 surfaçages and
441 bilans. This panel's 2016 figures are 24,104,467, 4,676 and 538 — HAS sits
at 89%, 84% and 82% of them. A consistent shortfall across three independent
codes points to HAS using régime général where the open data is explicitly
`Champ : Tous régimes`; HAS does not state its scope in that table. An earlier
version of this README claimed the 2015 détartrage figure (21.6M) reconciled
with HAS's 21.5M. That was a coincidence of comparing the wrong year against a
narrower scope, not a validation.

**Volumes of an unreimbursed act measure coding, not need.** HAS says so
explicitly in the 2018 report: "la volumétrie très faible des actes de surfaçage
et de bilan codifiés pourrait s'expliquer par leur non prise en charge par
l'assurance maladie, ce qui fait qu'ils ne sont pas codifiés par les
praticiens." Any inference from act counts has to carry that caveat.

**The département files have one row per practitioner category plus a TOTAL
row.** Summing raw rows double-counts. `build_departements.py` keeps the total
row only.

## Known gaps

- The département panel starts at 2020: 2017 and 2018 split NGAP and CCAM into
  separate columns under different labels, and forcing that join would need its
  own mapping note
- The effect size driving the cost model is Danish (Hansen et al., national
  registers, 1,251 patients, 30,133 person-years) and measures periodontal
  therapy broadly rather than the French DSR act

## Licence

Analysis code: MIT, see [`LICENSE`](LICENSE). Source data remains under CNAM's
Licence Ouverte; cite them, not this repository.
