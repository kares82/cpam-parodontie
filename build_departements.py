"""
Builds a département-level panel of liberal dental activity from CNAM's
"Activité et prescriptions des chirurgiens-dentistes libéraux par département".

Note on scope: this source carries ACT COUNTS and practitioner headcount, not
euros (the only money column is pharmacy prescribing). So a département cut is
a volume and density story, not a spend story. Spend stays national, from the
CCAM act-level series.

Output: cpam/out/dept_panel.csv  (one row per year x département)
"""

import re
import sys
from pathlib import Path

import pandas as pd

SRC = Path("/mnt/user-data/uploads/CCAM")
OUT = Path(__file__).resolve().parent / "out"

COLS = {
    "profession": r"^Chirurgiens-dentistes et ODF$",
    "departement": r"^DEPARTEMENT$",
    "effectifs": r"^EFFECTIFS$",
    "consultations": r"CONSULTATIONS",
    "chirurgie": r"CHIRURGIE DENTAIRE",
    "soins": r"^SOINS DENTAIRES",
    "protheses": r"^PROTHESES",
    "radiologie": r"RADIOLOGIE",
}


# Structural break: 2017 and 2018 report NGAP and CCAM activity in separate
# columns ("SOINS CONSERVATEURS (Actes NGAP)" alongside "ACTES DE SOINS
# DENTAIRES CCAM"), and the NGAP labels don't map cleanly onto the merged
# "(Actes CCAM et NGAP)" columns used from 2020. Rather than force a join across
# a definition change, the panel starts at 2020. Those earlier files stay in the
# source folder; a comparison across the break would need its own mapping note.
FIRST_YEAR = 2020


def load_year(path: Path) -> pd.DataFrame:
    year = int(re.match(r"(\d{4})", path.name).group(1))
    xl = pd.ExcelFile(path)
    # First sheet is the readme; activity is on the last sheet.
    df = pd.read_excel(xl, sheet_name=xl.sheet_names[-1])
    df = df.rename(columns={c: str(c).strip() for c in df.columns})

    rename = {}
    for canon, pat in COLS.items():
        hit = [c for c in df.columns if re.search(pat, c, re.I)]
        if not hit:
            raise KeyError(f"no column for {canon!r} in {path.name}: {list(df.columns)}")
        rename[hit[0]] = canon
    df = df.rename(columns=rename)[list(COLS)]

    # "33- Gironde" -> code 33, name Gironde
    parts = df["departement"].astype(str).str.extract(r"^\s*(\w+)\s*-\s*(.+?)\s*$")
    df["dep_code"] = parts[0]
    df["dep_nom"] = parts[1]
    df = df[df["dep_code"].notna()]

    for c in ("effectifs", "consultations", "chirurgie", "soins", "protheses", "radiologie"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Each département appears five times: once per practitioner category
    # (chirurgiens-dentistes, chirurgie orale, médecine bucco-dentaire, ODF
    # specialists) plus a TOTAL CHIRURGIE DENTAIRE row that sums them. Summing
    # the raw rows therefore double-counts. Keep the total row only.
    df["profession"] = df["profession"].astype(str).str.strip()
    df = df[df["profession"].str.upper().str.startswith("TOTAL")]

    df.insert(0, "annee", year)
    return df.drop(columns=["departement", "profession"])


def main() -> None:
    files = sorted(SRC.glob("*chirurgiens-dentistes-liberaux-par-departement*"))
    frames = []
    for f in files:
        year = int(re.match(r"(\d{4})", f.name).group(1))
        if year < FIRST_YEAR:
            print(f"  skipped {f.name} (pre-{FIRST_YEAR} column layout)", file=sys.stderr)
            continue
        try:
            frames.append(load_year(f))
            print(f"  loaded {f.name}", file=sys.stderr)
        except Exception as e:
            print(f"  FAILED {f.name}: {type(e).__name__}: {e}", file=sys.stderr)

    panel = pd.concat(frames, ignore_index=True)
    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "dept_panel.csv", index=False)
    print(f"\nPanel: {panel.shape[0]:,} rows, years {sorted(panel.annee.unique())}")


if __name__ == "__main__":
    main()
