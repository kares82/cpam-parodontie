"""
Builds a tidy multi-year panel of CCAM act-level activity and reimbursement,
from CNAM's "Actes techniques de la CCAM" annual open-data files.

Why aggregation matters: the source files carry one row per
code_acte x activite x phase. Summing raw rows double-counts any act that
exists in several activity/phase variants. Everything here aggregates on
Code Acte first.

Source: https://www.assurance-maladie.ameli.fr/etudes-et-donnees
Licence: Licence Ouverte / Open Licence (CNAM)

Output: cpam/out/ccam_panel.csv  (one row per year x code_acte)
"""

import re
import sys
from pathlib import Path

import pandas as pd

SRC = Path("/mnt/user-data/uploads/CCAM")
OUT = Path(__file__).resolve().parent / "out"

# Canonical column names -> regex matching the header variants across years.
# 2015 uses year-suffixed headers ("Quantité d actes en 2015") and "HSD"
# where later years say "Base de remboursement"; 2015 also says CAS where
# later years say OPTAM.
COLMAP = {
    "code_acte": r"^Code Acte$",
    "libelle": r"^Libell",
    "categorie": r"^Cat.gorie d'acte$",
    "sous_categorie": r"^Sous-cat.gorie d'acte$",
    "quantite": r"Quantit.*actes",
    "base_remb": r"(Base de remboursement|^HSD)",
    "montant_remb": r"Montants? rembours",
}

DENTAL_CATEGORIES = [
    "Chirurgie dentaire",
    "Prothèses",
    "Soins conservateurs",
    "Radiologie dentaire",
]

# Two ways of saying "this is a dental act", because neither alone spans the series:
#
#   est_dentaire_cat  - CNAM's own "Catégorie d'acte" label. Clean and official,
#                       but only present from 2018. The 2015 file puts what later
#                       years call the sous-catégorie in that column, so the four
#                       dental labels simply don't appear in it.
#   est_dentaire_code - CCAM code starts with HB, the nomenclature's dental
#                       topography. Stable across every year.
#
# They are not identical: in 2025, 373 acts are both, 76 are category-dental but
# not HB (mostly dental radiology coded LB), and 65 are HB but carry another
# category or none at all (several of those are the zero-reimbursement acts).
# Cross-year series use the code flag; single-year category totals use the label.


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from headers and rename to canonical names."""
    df = df.rename(columns={c: str(c).strip() for c in df.columns})
    rename = {}
    for canon, pattern in COLMAP.items():
        matches = [c for c in df.columns if re.search(pattern, c)]
        if not matches:
            raise KeyError(f"No column matching {pattern!r} for {canon!r}. Have: {list(df.columns)}")
        rename[matches[0]] = canon
    return df.rename(columns=rename)[list(COLMAP)]


def load_year(path: Path) -> pd.DataFrame:
    """Read one annual file, take the data sheet, aggregate to one row per act."""
    year = int(re.match(r"(\d{4})", path.name).group(1))

    xl = pd.ExcelFile(path)
    # First sheet is always the "A lire" readme; data is the last sheet.
    # Sheet name varies by year ('DATA', 'Panorama des actes CCAM', ...).
    df = pd.read_excel(xl, sheet_name=xl.sheet_names[-1])
    df = normalise_columns(df)

    for col in ("quantite", "base_remb", "montant_remb"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Collapse activity/phase variants into one row per act code.
    agg = (
        df.groupby("code_acte", as_index=False)
        .agg(
            libelle=("libelle", "first"),
            categorie=("categorie", "first"),
            sous_categorie=("sous_categorie", "first"),
            quantite=("quantite", "sum"),
            base_remb=("base_remb", "sum"),
            montant_remb=("montant_remb", "sum"),
        )
    )
    agg.insert(0, "annee", year)
    agg["n_lignes_source"] = df.groupby("code_acte").size().reindex(agg["code_acte"]).values
    return agg


def main() -> None:
    files = sorted(SRC.glob("*actes-techniques-ccam*"))
    files = [f for f in files if "(1)" not in f.name]
    if not files:
        sys.exit(f"No CCAM files found in {SRC}")

    frames = []
    for f in files:
        try:
            frames.append(load_year(f))
            print(f"  loaded {f.name}", file=sys.stderr)
        except Exception as e:  # keep going; report at the end
            print(f"  FAILED {f.name}: {type(e).__name__}: {e}", file=sys.stderr)

    panel = pd.concat(frames, ignore_index=True)
    panel["est_dentaire_cat"] = panel["categorie"].isin(DENTAL_CATEGORIES)
    panel["est_dentaire_code"] = panel["code_acte"].str.startswith("HB")

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "ccam_panel.csv"
    panel.to_csv(dest, index=False)

    print(f"\nPanel: {panel.shape[0]:,} rows, years {sorted(panel.annee.unique())}")
    print(f"Written to {dest}")


if __name__ == "__main__":
    main()
