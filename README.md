# CPAM dental prevention analysis

Eleven years of CNAM act-level data (2015-2025) on periodontal treatment in
France, and the case for reimbursing it beyond patients with a diabetes ALD.

The short version: HAS evaluated the act for aggressive and chronic
periodontitis; France reimburses it only for diabetics; without reimbursement
the act is not performed at all; and lifting the restriction would cost under 5%
of dental spending. The usual cost-saving argument for lifting it does **not**
hold, and this repository says so — that part is a negative result.

## Read it

| | |
|---|---|
| **La note, graphique inclus** (français) | https://claude.ai/artifact/1wP2uPBSrCe7z34UBFat62 |
| The note as markdown | [`NOTE.md`](NOTE.md) |
| Source of the published page | [`out/note.html`](out/note.html) |

## What the data shows

**A whole clinical entity sits outside the reimbursement.** HAS evaluated DSR
"dans la prise en charge des parodontites agressives et chroniques". France
reimburses it only for patients with a diabetes ALD. Aggressive periodontitis,
in HAS's own description, hits adolescents and young adults, is severe and
progresses fast — and those patients almost never hold a diabetes ALD.

**Without reimbursement the act is not performed.** Surfaçage radiculaire
(`HBGB006`) has never been reimbursed and grew 2× between 2015 and 2025 — the
same as détartrage, which has always been covered. Two near-identical acts that
became reimbursable in 2019–2020 grew 58× and 445×. Before 2019 all three were
flat or falling. The reimbursement rule doesn't only decide who pays; it decides
who gets treated.

**The restriction is conventional, not clinical, and nobody revisited it.** It
was set by the convention of 21 June 2018; CNAM had commissioned the HAS
evaluation in September 2017 and HAS reported in December 2018, on a wider
population. When a deputy asked the health ministry in July 2019 why
periodontitis care isn't reimbursed, the answer came 33 months later and
mentioned neither the HAS evaluation, nor the convention's periodontal
provisions, nor the ALD condition.

**Lifting it would cost under 5% of dental spending.** €18.6M to €185.8M a year
depending on uptake, against €3,806M reimbursed for dental acts in 2025.

**But the cost-avoidance argument fails by a factor of 110 — and that failure is
itself the argument.** Five years of annual DSR costs CPAM €929 per patient and
recovers at most €13.72 downstream. Not because prevention doesn't work, but
because CPAM reimburses only €45 for an extraction and €60 for a prosthetic act.
The real cost of tooth loss falls on patients and complementary insurers. So
withholding reimbursement isn't a saving — it's a transfer onto households, and
it lands hardest on people who can't pay €1,000 out of pocket.

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
