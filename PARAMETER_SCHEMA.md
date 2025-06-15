# PARAMETER_SCHEMA.md

## ACTIVE PARAMETER SET: RDEE v0.1

This file tracks the official parameter list feeding into recursive survival simulation.

---

## 1 — COSMOLOGICAL PARAMETERS

- Hubble Constant (H0) — km/s/Mpc — [60, 75]
- Cosmological Constant (Λ) — 1/s² — [1e-56, 1e-52]
- Baryon-to-photon ratio — dimensionless — [1e-10, 1e-9]

---

## 2 — STELLAR PARAMETERS

- Stellar metallicity — [0.0001, 0.03]
- Stellar mass (Msun) — [0.1, 100]

---

## 3 — PLANETARY FORMATION PARAMETERS

- Planet mass (Mearth) — [0.1, 10]
- Planet distance (AU) — [0.1, 10]
- Planetary system multiplicity — [1, 20]

---

## 4 — HABITABILITY PARAMETERS

- Liquid water zone range — AU
- Stellar UV flux range — W/m²
- Tidal locking probability — [0, 1]

---

## 5 — PREBIOTIC CHEMISTRY PARAMETERS

- Prebiotic synthesis success probability — [0.001, 1.0]
- UV catalysis efficiency — [0.0, 1.0]
- Polymerization failure rate — [0.0, 1.0]

---

## 6 — EVOLUTIONARY PARAMETERS

- Evolutionary complexity threshold — [1, 10]
- Evolutionary fragility multiplier — [0.0, 1.0]
- Mass extinction frequency — events per 100 Myr

---

## 7 — SAMPLING & CONTROL PARAMETERS

- Recursive depth limit — integer
- Survival corridor sensitivity window — float

---

*This file will be updated as new physical models integrate into simulation pipeline.*
