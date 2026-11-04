---
title: "MAGI-007 결정 · 사용자 결정 노드"
date: 2026-11-05
tags: [MAGI-007, graph, decision]
---

# MAGI-007 결정 노드

R4 §5 의 권고 · 사용자 결정 · 종합자 봉인 예측. 상태는 11-05 02:3x 기준.

| 노드 | 내용 · 상태 |
|---|---|
| `DEC-ZNBDT-C1` | 다음 계산 = 열린 자리 4,8-(C≡CH)₂ (R4 §5-1 · 사용자 승인 11-05 00:4x → ZNBDT-C1 등록 → 관문 (0a)(0b) 탈락 11-05 01:39, ASSIGN_ZNBDT_C1 §5) |
| `DEC-′1` | 순위표 두 개의 −C₂H₅ 행을 막음 Widom 으로 재생성 (승인 대기) |
| `DEC-′2` | 관문 ⑤ 결과에 이완 후 PLD · AV · 두 탐침 통로 수 서술 열 (승인 대기) |
| `DEC-′3` | 씨앗 SD 자 / 씨앗 SEM 자 이름 소급 표기 (승인 대기) |
| `DEC-′4` | ASSIGN §E mslm050 = e0 × 3씨앗 명시 (승인 대기) |
| `DEC-′5` | 점검⓪ 을 C R3 D-13 정의로 등록 (승인 대기) |
| `DEC-′6` | CN/Br 혼합 후순위 기록 (승인 대기) |
| `USER-21:2x-(가)` | 사용자 결정 11-04 21:2x — A(격자 이완)를 측정 사실로 닫음 · PACMAN 순전하 ∣q∣ ≤ 1e-3 |
| `SYN-sealed` | 종합자 봉인 예측(11:09 · sha256 bbbc71b7…) — 결정과 불일치(§9-10 ①) |
| `SYN-brief-§10-3` | 브리핑 v3 §10-3 — C₂H₅ 92.99 전 치환판 혼용(종합자 자백 A-1) |

## 간선 (R4)

- [S-3 A(격자 이완): 측정 사실로 닫힘](consensus/S-3.md) **근거** → [USER-21:2x-(가) 사용자 결정 11-04 21:2x — A(격자 이완)를 측정 사실로 닫음 · PACMAN 순전하 |q| ≤…](decisions.md) — A 측정 사실로 닫음
- [DEC-ZNBDT-C1 다음 계산 = 열린 자리 4,8-(C≡CH)₂ (R4 §5-1 · 사용자 승인 11-05 00:4x → Z…](decisions.md) **근거** → [S-5 Q2: 지금 다섯 설계를 주 축(S_humid)에서 1.5 단위 넘게 이길 개질은 저장소 근거로 제시된 것이 없습니다 — 세 자리 일치](consensus/S-5.md)
- [DEC-′1 순위표 두 개의 −C₂H₅ 행을 막음 Widom 으로 재생성 (승인 대기)](decisions.md) **근거** → [A-3 Caspar §4-6 재현. 23_SCREENING/final_ranking_smix.py 60행과 final_ranking.py 66행은 results_mag…](questions/A-3.md) — 순위표 재생성
- [DEC-′2 관문 ⑤ 결과에 이완 후 PLD · AV · 두 탐침 통로 수 서술 열 (승인 대기)](decisions.md) **근거** → [A-4 Caspar §4-7 재현. risk_screen.py 414~421행: 'PLD': (m0［'PLD'］ …) > CO2_KINETIC · 'AV': (m0.g…](questions/A-4.md) — 관문 ⑤ 서술 열
- [DEC-′2 관문 ⑤ 결과에 이완 후 PLD · AV · 두 탐침 통로 수 서술 열 (승인 대기)](decisions.md) **근거** → [Balthasar D-4 수용](../R3_laptop2/note.md) — N₂ 통로 수 열 제안
- [DEC-′3 씨앗 SD 자 / 씨앗 SEM 자 이름 소급 표기 (승인 대기)](decisions.md) **근거** → [Caspar C-dissent-⑧](../R1_hkhome/note.md) — 자 이름
- [DEC-′5 점검⓪ 을 C R3 D-13 정의로 등록 (승인 대기)](decisions.md) **근거** → [Caspar C-점검⓪](../R1_hkhome/note.md) — 정의 뒤 등록
- [SYN-sealed](../../MAGI-007_sealed_prediction_cloud.md) **반박** → [DEC-ZNBDT-C1 다음 계산 = 열린 자리 4,8-(C≡CH)₂ (R4 §5-1 · 사용자 승인 11-05 00:4x → Z…](decisions.md) — §9-10 ① 불일치 — 종합자 후보와 다름

## R4 뒤 (보완 단계)

- ZNBDT-C1 — [등록 · §5 판정(관문 탈락)](../../../ASSIGN_ZNBDT_C1_20261105.md)
- ZNBDT-C2 — [무극성 −CN 계산 대조(HKHOME 등록 02:06)](../../../ASSIGN_ZNBDT_C2_20261105.md) · [후속 세 건 · 밤샘 결정표](../../../ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md)
- 규약 [§11-5 라운드 중 격리 · 보완 단계](../../../MAGI_20260905.md)

Related: [종합자](seats/Synthesizer.md) · [R4 §5](../../MAGI-007_ligand-modification.md) · [INDEX](../INDEX.md)
