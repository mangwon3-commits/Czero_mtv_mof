# Caspar — MAGI-007 baseline recompute (raw JSON only) · 2026-11-04 · HKHOME

Script `baseline_recompute.py` → `baseline_recompute.json` (machine-readable; every row, seed, md5). Repo read-only; HEAD at run 4c64fb91 (2578c3a2→4c64fb91 touched only `COMMS/desktop.md`; no raw file changed). All raw JSON on the working tree equal their origin-branch copies that `e24i_judge.py` / `e24i_hwc_table.py` read (md5 compared).
Conventions: per-run ± = RASPA 95 % CI — **checked from blocks: printed ± / (2.776·SEM₅) = 1.0000 for CO₂ and N₂ in all 12 local `.data`**. S_mix = (N_CO₂/N_N₂)/(0.15/0.85), relative ± in quadrature. Mean ± = ±̄/√k.

## 1. Dry S_mix (0.15/0.85 · 1 bar · 298 K)

| row | version | k | seeds (unique) | S_mix | ±̄/√k | seed SD | SD/√k | N_CO₂ | completion evidence |
|---|---|---|---|---|---|---|---|---|---|
| −CN | verdict (s1–3) | 3 | 1790405420/435/450 ✓ | **141.531** | 5.468 | 5.255 | 3.034 | 3.2564 | run dirs on HKHOME: `Simulation finished` ×2 each, rc 0, .data seed+loadings = JSON |
| −CN | ranking (s1–6) | 6 | + 1790668500/514/529 ✓ | **139.774** | 3.986 | 4.402 | 1.797 | 3.2485 | s4–6 same; same CIF md5 8fd4fc85 in all 6 run dirs |
| −CN | s4–6 only | 3 | | 138.017 | 5.806 | 3.402 | 1.964 | | old3→new3 −3.51 = −0.44 (±̄/√3 units) |
| −Br | verdict (s1–3, laptop2) | 3 | 1790405437/452/467 ✓ | **128.016** | 5.049 | 4.430 | 2.558 | 2.8372 | JSON only (status ok · rc 0 · ff md5) — run dirs on laptop2 |
| −Br | ranking (s1–6) | 6 | + 1790668519/534/549 ✓ | **127.922** | 2.935 | 2.833 | 1.157 | 2.8358 | s4–6 run dirs on HKHOME: ×2 markers, rc 0, match |
| −C₂H₅ (blocked) | both | 3 | 1790406907/922/937 ✓ | **114.624** | 6.921 | 8.007 | 4.623 | 1.4781 | JSON only (final · judge ok · rc 0 · not-found 0); n_expected = n_blocked = 24 = 4 spheres × 6 cells, CO₂@1.65 & N₂@1.82 |
| −Cl | both | 3 | 1790406914/929/944 ✓ | **111.150** | 2.946 | 4.700 | 2.713 | 2.9840 | JSON only (Junseok) |
| −CH₃ | both | 3 | 1790405418/433/448 ✓ | **108.668** | 3.870 | 0.917 | 0.529 | 2.8378 | JSON only (laptop2) |
| parent e22_parent | both | 3 | 1790330550/565/581 ✓ | **75.435** | 2.144 | 0.415 | 0.240 | 2.8317 | run dirs on HKHOME ×2 markers, match |
| mslm050 | — | 6 **realizations** (8 runs) | all 8 unique | **39.711** | 0.375 | 3.387 (between-realization) | | | JSON only; e0 = mslm050_DDEC6.cif ×3 seeds (38.760, seed SD 0.52), e1–e5 = mslm050e1…e5_DDEC6.cif ×1 |

No seed collision among the 30 S_mix rows. Every row: status ok, rc 0, ff_md5 8e8ec933, stored S_mix/± reproduced to 1e-6.
**Verdict §26-2 reproduced exactly** (141.53 ± 5.47 · 5.25 / 128.02 ± 5.05 · 4.43 / 111.15 · 108.67 · 114.62 · 75.43). **SMIX §G reproduced exactly** (139.8 ± 4.0 · 4.4 / 127.9 ± 2.9 · 2.8 / rest identical). The CN/Br gap between the versions comes **only from adding s4–s6** (same CIF, same protocol); the ± ruler is the same (±̄/√k), only k changes.

## 2. Pairwise (d / ruler; |x| ≥ 1.5 ranks)

reg = d/√(±₁²+±₂²) with ± = ±̄/√k (registered "units") · SEM = d/√(SD₁²/k₁+SD₂²/k₂) · SD = d/√(SD₁²+SD₂²) (= batch unit, verdict-corrected "씨앗 SD 자") · SEM95 = SEM/2.776 (E24I_SEEDS_REG "95 % 척도 씨앗 산포").

| pair | d (3s) | reg | SEM | SD | SEM95 | d (6s) | reg | SEM | SD | SEM95 |
|---|---|---|---|---|---|---|---|---|---|---|
| CN − Br | 13.52 | **1.82** | 3.41 | 1.97 | 1.23 | 11.85 | **2.39** | 5.55 | 2.26 | 2.00 |
| Br − C₂H₅ | 13.39 | **1.56** | 2.53 | 1.46 | 0.91 | 13.30 | 1.77 | 2.79 | 1.57 | 1.01 |
| C₂H₅ − Cl | 3.47 | 0.46 | 0.65 | 0.37 | 0.23 | same | | | | |
| Cl − CH₃ | 2.48 | 0.51 | 0.90 | 0.52 | 0.32 | same | | | | |
| CN − parent | 66.10 | 11.25 | 21.72 | 12.54 | 7.82 | 64.34 | 14.22 | 35.49 | 14.55 | 12.78 |
| Br − parent | 52.58 | 9.59 | 20.47 | 11.82 | 7.37 | 52.49 | 14.44 | 44.44 | 18.33 | 16.01 |
| C₂H₅ − parent | 39.19 | 5.41 | 8.47 | 4.89 | 3.05 | same | | | | |
| Cl − parent | 35.72 | 9.80 | 13.11 | 7.57 | 4.72 | same | | | | |
| CH₃ − parent | 33.23 | 7.51 | 57.21 | 33.03 | 20.61 | same | | | | |

Ruler-dependent cells: Br−C₂H₅ at 3 seeds (reg 1.56 ranks, SD 1.46 tie, SEM95 0.91 tie); CN−Br at 3 seeds on SEM95 (1.23, tie). {C₂H₅, Cl, CH₃} tie on every ruler.

## 3. Henry selectivity · retention

| row | S_ON ± (raw) | S_OFF · G | S_mix/S_Henry (3s · 6s) |
|---|---|---|---|
| −CN | 116.586 ± 2.629 | 53.56 · 2.177 | 1.214 · **1.199 ± 0.044** |
| −Br | 127.600 ± 3.104 | 55.90 · 2.283 | 1.003 · 1.003 |
| −C₂H₅ unblocked (pockets in) | 154.343 ± 3.764 | 69.51 · 2.220 | 0.743 |
| −C₂H₅ **blocked** (gated) | **127.048 ± 3.989** | 66.51 · 1.910 | **0.902 ± 0.061** |
| −Cl | 110.204 ± 1.537 | 52.83 · 2.086 | 1.009 |
| −CH₃ | 128.208 ± 2.703 | 63.16 · 2.030 | 0.848 |
| parent | 87.805 ± 1.218 | 39.10 · 2.246 | 0.859 |
| mslm050 (results_v3) | 58.113 ± 1.702 | | 0.683 ± 0.021 |

## 4. Gate ⑤ (results_e24i_gate5_desktop-nvsrr9m.json · parent results_e22b_gate5_hkhome.json; LCD_ref = parent-after 5.24089)

| row | pass | LCD drop vs ref | vs own before | PLD before→after | AV/cell before→after | EDiff · loops |
|---|---|---|---|---|---|---|
| −CN | ✓ | 3.37 % | −0.71 % | 3.824→**3.270** | 78.1→**0.0** | 0.364 · 12 (cap) |
| −Br | ✓ | 6.96 % | 1.07 % | 3.819→3.308 | 71.7→16.0 | 0.956 · 12 (cap) |
| −C₂H₅ | ✓ | −2.71 % | −15.6 % (LCD grows) | 3.810→4.363 | 34.3→85.8 | 7.64 · 12 (cap) |
| −Cl | ✓ | 6.47 % | 2.64 % | 3.821→3.526 | 78.9→67.2 | 0.064 · 12 (cap) |
| −CH₃ | ✓ | 13.66 % | 2.67 % | 3.818→3.578 | 62.2→42.3 | 1.4e-6 · 2 |
| parent | ✓ | 0.00 % | 0.47 % | 3.818→3.711 | 105.7→94.7 | 0.360 · 12 (cap) |

LCD rule (< 20 %) satisfied by every row; drops recomputed = stored. The PLD and AV checks in `risk_screen.py:416,421` use the **before** structure, so CN's after-relax AV 0 / PLD 3.270 < 3.3 never enters the gate. `final_ranking_smix.py` performs no gate-⑤ join at all (no effect here since all pass); `final_ranking.py` does.
Structure/version join: every mix and Widom input is `charged_v3/e24i_<x>_open_DDEC6.cif` (single commit 3a80f01c, 09-26 15:48, before all runs); run-dir CIFs byte-identical; charged_v3 coords = `relax_tnf/<x>_relaxed.cif` (gate-⑤ input) to 5e-9 frac; no `e24_*_100` row; one ff md5; framework charge sums ≤ 3e-5 e (CN mix runs print RASPA's "NET CHARGE" warning for −1.0e-4 e: benign).

## 5. Humid TSA WC (RH90 · ads 298 K/15 kPa → TSA 373 K) · water

| row (source) | WC_TSA ±̄/√3 · SD | vs parent reg · SEM · SD | WC_VSA | ads CO₂ | ads H₂O (RH90) | dry water index (4 s) |
|---|---|---|---|---|---|---|
| −CN (junseok, 3b2c63da) | **2.4005 ± 0.0305** · 0.0475 | +2.64 · +3.89 · +2.25 | 0.783 | 3.305 | 0.161 (0.069/0.337/0.078) | 0.02756 ± 0.00187 |
| −Br (hkhome, 6a574f8f) | 2.1595 ± 0.0270 · 0.0073 | −3.52 · −27.8 · −16.1 | 0.767 | 2.943 | 0.0145 | 0.00948 ± 0.00025 |
| −Cl (junseok, f89343f1, cited) | 2.3097 ± 0.0176 · 0.0136 | +0.51 · **+2.00** · +1.16 | 0.854 | 3.110 | 0.0219 | 0.01134 ± 0.00018 |
| −Cl (laptop2, e604c423, replicate) | 2.2972 ± 0.0192 · 0.0176 | +0.12 | 0.840 | 3.098 | 0.0190 | |
| −CH₃ (laptop, 57f2e787) | 2.1705 ± 0.0264 · 0.0205 | −3.26 · −10.2 · −5.89 | 0.856 | 2.963 | 0.0256 | 0.01207 ± 0.00021 |
| −C₂H₅ blocked (junseok, a844ea51) | 1.1074 ± 0.0345 · 0.0115 | −27.1 | 0.396 | 1.543 | 0.0269 | 0.01534 ± 0.00046 (blocked 1.30 ÷ blocked 1.65; 30 = 5×6) |
| parent (laptop, 60cd67a1) | 2.2933 ± 0.0268 · 0.0039 | — | 0.992 | 2.973 | 0.0294 | 0.01470 ± 0.00027 |

WC_TSA = ads − tsa CO₂ reproduced per seed (stored to 1e-4). Audits 9/9 · rc 0 · seeds unique for the five designs; C₂H₅ CO₂ 24 / water 30 blocked in all 9. Br's 9 run dirs on HKHOME: ×2 markers, loadings = JSON, seeds = audit. Verdict §26-4 and FINAL_RANKING §B humid column (2.40 · 2.16 · 2.31 · 2.17 · 1.11 · 2.29) reproduced.

## 6. Discrepancies (computed vs doc)

1. **C₂H₅ S_Henry / retention: unblocked vs blocked.** SMIX §G retention 0.74 = 114.62/154.34 (blocked S_mix ÷ **unblocked**, pocket-inclusive S_Henry). The verdict's 0.90 = ÷ blocked 127.05. Off by 0.16 (≈ 2.6× the ±0.06). FINAL_RANKING A′/B rank C₂H₅ **#1 in 3D at 154.3 ± 3.8**. The verdict calls that value "descriptive upper bound". The gated 127.05 ± 3.99 sits level with CH₃ (128.2) and Br (127.6). The same §B row also mixes a blocked water index (0.0153) with the unblocked S_Henry. Cause (shown, code): `final_ranking.py:66-70` and `final_ranking_smix.py:60` read only `results_magi5_e3_e24i_*_widom_*.json`; neither reads `results_e24i_blockpockets_hkhome.json`.
2. **Same document, two S_mix versions.** FINAL_RANKING_20260930.md §B prints CN "141.5 ± 5.5" and Br "128.0 ± 5.1" (3-seed, hand-typed in `ours_extra_20260930.json`), plus CN dry N_CO₂ 3.26 (6-seed value: 3.25). Its own §G and SMIX §G print 139.8 ± 4.0 / 127.9 ± 2.9 (6-seed). Size: CN −1.73 (≈ 0.26 reg units, nominal: the two versions share s1–3), Br −0.08. SMIX's own note line "−CN(141.5)" is a stale hard-coded label; the count beside it is computed from the 6-seed row.
3. **Ruler names.** FOLLOWUP's d′ = 5.55 is labelled "씨앗 SD 자". It is the **SEM ruler** d/√(SD²/6+SD²/6). With the verdict-corrected "씨앗 SD 자" (undivided SD, = batch unit) it is **2.26**. FOLLOWUP also says "at 3 seeds the seed-scatter ruler was below 1.5". That holds only for SEM95 (1.23); the verdict's SD ruler (1.97) and SEM ruler (3.41) are both above 1.5. So up to three rulers share one name. SCRIPT_RELIABILITY's "씨앗 산포 자로 5.6" is also the SEM ruler.
4. **mslm050 row.** §G's "씨앗 6 · SD 3.4" is 6 realizations / between-realization SD (8 runs; within-CIF seed SD 0.52). The value is hard-coded at `final_ranking_smix.py:69` and is not read from raw. It reproduces (39.711 · 0.375 · 3.387), but only if e0's ± is ±̄/√3 (otherwise 0.404).
5. Rounding only: verdict SD-ruler CN−parent 12.55 vs 12.54; Cl humid replicate 0.49 vs 0.48. Both likely computed from rounded numbers (hypothesis).
6. Presentation, not numerical: SMIX §G orders C₂H₅ (#4) > Cl (#6) > CH₃ (#8) by point value inside one cluster. The verdict's rule order is Cl > CH₃ > C₂H₅ (water-index tiebreak). Both are ties on S_mix under every ruler. FINAL_RANKING §G says the CoRE 3D retention median is 0.97 while SMIX says 0.90 (CoRE rows not audited).
7. Gate ⑤ "pass" for five of six rows was reached at outer-loop cap 12 with EDiff 0.06–7.6 (not converged; only CH₃ converged, at 2 loops). The gate's LCD reference is the parent-after LCD, not each structure's own before LCD (CH₃: 13.66 % vs 2.67 %).

## 7. Not verifiable from raw on HKHOME
- `Simulation finished` markers for Br s1–3, Cl, CH₃ and C₂H₅ dry mix; mslm050's 8 runs; and all humid runs except Br. Their run dirs live on laptop2, Junseok and laptop. For these I relied on JSON status/judge/audit fields, which the runner code sets only after its `finished()` check.
- Parent humid (E-25): no audit/summary JSON exists in the repo. The raw rows carry no seed or marker, so seed uniqueness and the 9/9 claim rest on the E-25 verdict text.
- C₂H₅ blocked dry-mix input files (.block, CIF) are not on HKHOME. Only the JSON equations (24 = 4 × 6) and the HKHOME blockpockets block files (first line 4) were checked.
- CoRE rows and cluster numbers in SMIX §G were not recomputed (out of scope).
- E/A/B outputs (`results_znbdt_*`, `znbdt_a_zeo_runs/`, `*_uff300_DDEC6.cif`): not searched for, not encountered in any listing I ran, not opened. The only E/A/B-related name I saw was `ASSIGN_ZNBDT_SUPP_20261103.md`, as a filename in a grep hit list. I did not read it. I also did not read the new `COMMS/desktop.md` diff (2578c3a2→4c64fb91).
