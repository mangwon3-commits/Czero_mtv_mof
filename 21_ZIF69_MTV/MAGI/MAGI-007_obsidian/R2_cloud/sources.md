---
title: MAGI-007 R2 참고 자료 (종합자)
date: 2026-11-04
tags: [MAGI-007, R2, 종합자, sources]
---

# R2 참고 자료 — 종합자가 직접 읽은 원자료 · 코드

| 질의 | 종류 | 경로 | 판본 | 읽은 범위 | 무엇을 보이는가 |
|---|---|---|---|---|---|
| A-2 · A-14 | 원자료 | `21_ZIF69_MTV/results_magi5_e3_e24i_{cn,br,cl,ch3,c2h5}_open_widom_*.json` · `results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json` | master f589c08b | ON 행 전부 | K_H(CO₂) · K_H(N₂) · ΔU 치환체 대 모체 |
| A-2 · A-14 · A-15 | 원자료 | `21_ZIF69_MTV/results_e24i_e24i_*_open_mix_*.json` · `results_e23_mix_desktop.json` | master | 행 전부 | 작동점 N_CO₂ · N_N₂ · S_mix · ± |
| A-3 | 원자료 | `21_ZIF69_MTV/results_e24i_blockpockets_hkhome.json` | master | `per_structure.e24i_c2h5_open.rows` | 막음 K_H(CO₂ ON @1.65) 8.326e-4 · K_H(N₂ @1.82) 6.553e-6 → S 127.05 |
| A-3 | 코드 | `23_SCREENING/final_ranking_smix.py` 55~72 · `final_ranking.py` 58~74 | master | 해당 행 | 차단 없는 Widom 글롭만 읽음 |
| A-4 | 코드 | `21_ZIF69_MTV/risk_screen.py` 405~425 | master | 해당 행 | PLD · AV 검사가 m0(이완 전) |
| A-5 | 자료 · 코드 | `23_SCREENING/ours_extra_20260930.json` · `final_ranking_smix.py` 69 | master | 전문 · 해당 행 | 손입력 3씨앗 문자열 · mslm050 상수 n_seed=6 |
| A-8 | 원자료 | 위 Widom 파일의 `dU_N2` · `dU_CO2` | master | ON 행 | ΔU(N₂) −18.3~−18.9 |
| §0 | 해시 | `MAGI/MAGI-007_R1_*.md` · `_evidence/` · COMMS 제출 줄 | master 1db179a4 · cc7768cf · 5e6300e8 | sha256 전부 | 넷 유효 |
| §0 | 문서 | `MAGI-007_R1_laptop_v1224.md` 대 `MAGI-007_R1_laptop.md` | master | diff · grep | 핵심어 동일 · 수치 셋 변경 |
| A-1 | 문서 | `MAGI5_E22_VERDICT_20260925.md` §21 · `results_e27b_mix323_c2h5_hkhome.json` | master | §21 · CIF 열 | 92.99 는 e24c_c2h5_100 |

Related: [note](note.md) · [R2 원문](../../MAGI-007_R2_attack.md)
