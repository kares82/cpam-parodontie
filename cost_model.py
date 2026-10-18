"""
Cost-avoidance model: what does CPAM spend to avoid one extraction through
periodontal debridement (DSR), and what does it get back?

The honest version. Every input is sourced; nothing is tuned to produce a
favourable answer. Where the answer is unfavourable it is reported as such.

Inputs
------
Effect size   Hansen et al., Danish nationwide registers, 1,251 incident
              periodontitis patients, 30,133 person-years, 1997-2021.
              Five consecutive years of periodontal therapy vs none:
              0.08 fewer extracted teeth (95% CI 0.04-0.13).
              Expected-count ratio 0.82 (CI 0.68-0.97) for next-year
              extractions. Protective effect lasts ~3 years, null by 5.

Unit costs    CNAM, "Actes techniques de la CCAM", 2025, secteur libéral,
              all schemes. Derived as reimbursed amount / act quantity, so
              they are what CPAM actually pays, not the posted tariff.

Caveats that belong in any reading of the output
------------------------------------------------
1. The effect size is Danish. Danish and French periodontal care pathways,
   reimbursement rules and coding practice differ.
2. It measures periodontal therapy broadly, not the French DSR act.
3. "Extraction avoided" is not the same as "prosthesis avoided". Not every
   extracted tooth is replaced, and not every replacement is reimbursed.
   The model therefore reports a range: extraction cost alone as the floor,
   extraction plus one prosthetic act as the ceiling.
4. Reimbursed cost is not social cost. Patient out-of-pocket, complementary
   insurance, pain, time off work and tooth loss itself are all outside this.
"""

import pandas as pd

PANEL = "out/ccam_panel.csv"
YEAR = 2025

# DSR tariffs as listed in the UFSBD clinical pathway (euros, per episode)
DSR_TARIFFS = {"1 sextant": 80.0, "2 sextants": 160.0, "3+ sextants": 240.0}
DSR_CODES = {"HBJA003": "1 sextant", "HBJA171": "2 sextants", "HBJA634": "3+ sextants"}

# Hansen et al.: 5 consecutive years of therapy vs none
TEETH_SAVED_5Y = 0.08
TEETH_SAVED_5Y_LO = 0.04
TEETH_SAVED_5Y_HI = 0.13


def unit_costs(df: pd.DataFrame) -> dict:
    y = df[(df.annee == YEAR) & (df.quantite > 0)]
    av = y[y.libelle.str.contains("[Aa]vulsion", na=False)]
    pr = y[(y.categorie == "Prothèses")]
    return {
        "extraction": av.montant_remb.sum() / av.quantite.sum(),
        "prothese": pr.montant_remb.sum() / pr.quantite.sum(),
    }


def observed_dsr_mix(df: pd.DataFrame) -> tuple[float, int]:
    """Volume-weighted average DSR cost per episode, from the real 2025 mix."""
    y = df[(df.annee == YEAR) & (df.code_acte.isin(DSR_CODES))]
    q = y.set_index("code_acte").quantite
    total_q = q.sum()
    weighted = sum(q.get(c, 0) * DSR_TARIFFS[lbl] for c, lbl in DSR_CODES.items())
    return weighted / total_q, int(total_q)


def main() -> None:
    df = pd.read_csv(PANEL)
    uc = unit_costs(df)
    dsr_avg, dsr_vol = observed_dsr_mix(df)

    print(f"UNIT COSTS TO CPAM ({YEAR}, reimbursed / quantity)")
    print(f"  extraction (avulsion), mean      {uc['extraction']:8.2f} EUR")
    print(f"  prosthetic act, mean             {uc['prothese']:8.2f} EUR")
    print(f"  DSR episode, volume-weighted     {dsr_avg:8.2f} EUR   ({dsr_vol:,} episodes)")

    cost_5y = dsr_avg * 5
    print(f"\nFIVE YEARS OF ANNUAL DSR, PER PATIENT   {cost_5y:8.2f} EUR")

    print("\nCOST PER TOOTH SAVED (5 years of therapy, Hansen et al.)")
    for label, teeth in (("optimistic (CI high)", TEETH_SAVED_5Y_HI),
                         ("central estimate", TEETH_SAVED_5Y),
                         ("conservative (CI low)", TEETH_SAVED_5Y_LO)):
        print(f"  {label:<24} {teeth:.2f} teeth  ->  {cost_5y / teeth:11,.0f} EUR per tooth")

    print("\nVALUE RECOVERED PER TOOTH SAVED, TO CPAM")
    floor = uc["extraction"]
    ceiling = uc["extraction"] + uc["prothese"]
    print(f"  floor   (extraction avoided only)       {floor:8.2f} EUR")
    print(f"  ceiling (extraction + one prosthesis)   {ceiling:8.2f} EUR")

    print("\nNET POSITION PER PATIENT, 5 YEARS")
    for label, teeth in (("CI high", TEETH_SAVED_5Y_HI), ("central", TEETH_SAVED_5Y),
                         ("CI low", TEETH_SAVED_5Y_LO)):
        print(f"  {label:<9} spend {cost_5y:8.2f}  recover "
              f"{teeth*floor:7.2f}-{teeth*ceiling:7.2f}  "
              f"net {teeth*ceiling - cost_5y:+9.2f} EUR (best case)")

    ratio = cost_5y / (TEETH_SAVED_5Y * ceiling)
    print(f"\nBREAK-EVEN: DSR would need to be {ratio:,.0f}x cheaper, or "
          f"{ratio:,.0f}x more effective,\nfor direct reimbursed-cost avoidance to pay for itself.")

    print("\nWHAT THE CURRENT RESTRICTION COSTS TO LIFT (arithmetic, not forecast)")
    for extra in (100_000, 500_000, 1_000_000):
        print(f"  +{extra:>9,} DSR episodes/yr  ->  +{extra*dsr_avg/1e6:6.1f} M EUR/yr")
    print(f"\n  for scale: {YEAR} dental reimbursement, all categories, "
          f"{df[(df.annee==YEAR)&df.est_dentaire_code].montant_remb.sum()/1e6:,.0f} M EUR")


if __name__ == "__main__":
    main()
