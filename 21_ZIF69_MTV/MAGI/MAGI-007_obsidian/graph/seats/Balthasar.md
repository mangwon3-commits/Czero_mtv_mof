---
title: "Balthasar (laptop2 · 실용)"
date: 2026-11-05
tags: [MAGI-007, graph, seat, Balthasar]
aliases: [Balthasar]
---

# Balthasar — laptop2 · 실용

- R1: [그래프 판](../../R1_laptop2/note.md) · [참고 자료](../../R1_laptop2/sources.md) · [본문](../../../MAGI-007_R1_laptop2.md) · [자산 b1_b3_evidence_table.csv](../../R1_laptop2/assets/b1_b3_evidence_table.csv)
- R3: [그래프 판](../../R3_laptop2/note.md) · [참고 자료](../../R3_laptop2/sources.md) · [본문](../../../MAGI-007_R3_laptop2.md) · [자산 two_layers.csv](../../R3_laptop2/assets/two_layers.csv)

## R1 주장 노드

- **B-1** 이득의 출처
- **B-2** 물(E)
- **B-3** 격자 이완(A)
- **B-4** 323 K(B)
- **B-5** 후보 ① 열린 자리 4,8-(C≡CH)₂
- **B-6** 후보 ② bib 의 2-메틸이미다졸 판
- **B-7** 일정
- **B-8** 포스터에 지금 쓸 수 있는 문장
- **B-9** 아직 쓸 수 없는 문장
- **B-10** dissent

## R1 안의 간선

| from | → | to | 종류 | 메모 |
|---|---|---|---|---|
| B-1 | → | src:results_e24i_*_open_mix | 근거 | 열린 자리 다섯의 S_mix · 적재(원자료 재계산) |
| B-1 | → | src:results_e23_mix_desktop | 근거 | 모체 S_mix · 적재 |
| B-2 | → | src:humid_working_capacity_w2_e24i | 근거 | 습윤 이원 ads 의 물 · CO₂ 적재 |
| B-2 | → | B-1 | 인용 | N₂ 감소 기제가 물에도 남는다는 예측의 전제 |
| B-3 | → | src:results_e24i_relax300_laptop | 근거 | 이완본 통로 수 · 주머니 수 |
| B-3 | → | B-1 | 인용 | 통로 폭에 걸린 기제라 격자 이완에 민감 |
| B-4 | → | src:results_e27_mix323_laptop | 근거 | 모체 323 K / 298 K 비 |
| B-4 | → | B-1 | 인용 | 기하 기제면 온도는 비율만 낮춤 |
| B-5 | → | B-1 | 인용 | −CN 의 CO₂ +15 % 출처를 구분하는 대조 |
| B-5 | → | src:build_e24g_bdtdc | 근거 | SMILES 이미 있음 · 전 자리 치환 탈락 기록 |
| B-6 | → | src:build_e22_bdtdc | 근거 | 빌더는 6원 고리 C–H 만 찾음 → 확장 필요 |
| B-7 | → | src:MACHINE_CAPABILITIES | 근거 | rdkit · LAMMPS 는 랩탑 · HKHOME 만 |
| B-7 | → | B-5 | 인용 | ① 일정 5~7일 |
| B-7 | → | B-6 | 인용 | ② 일정 7~10일 |
| B-8 | → | src:FINAL_RANKING_SMIX_G | 근거 | 기준선 정본 |
| B-9 | → | B-2 | 인용 | E 3회 비교 기대 차 1.5 단위 근처 |
| B-9 | → | B-3 | 인용 | 이완본 −CN 통로 0 |
| B-9 | → | src:FINAL_RANKING_SMIX_G | 근거 | CoRE 기하 모체 113.7 대 이완 · PACMAN 모체 75.4 |
| B-10 | → | src:ASSIGN_ZNBDT_SUPP_A_table | 반박 | 값이 정해지지 않는 경우의 칸이 표에 없음 |
| B-10 | → | B-3 | 인용 | 통로 0 → 적재 0 근처 |

## 받은 질의 (R2)

- [A-2 기제가 두 층에서 다르게 읽히는데, 세 R1 이 한 층만 봤습니다. 원자료(Widom ON · results_magi5_e3_e24i_*_open_widom_*…](../questions/A-2.md) **공격** → B-1 — 헨리 K_H(N₂) 불감 대 작동점 N₂ 감소
- [A-6 A 는 21:2x 사용자 결정으로 측정 사실로 닫혔습니다(ASSIGN 종합자 확정 5: 이완본 −CN · −Br 모두 N₂ 통로 0 → S_mix 정의 안 됨 …](../questions/A-6.md) **공격** → B-3 — 같음
- [A-7 세 자리가 모두 CO₂–H₂O 이원(N₂ 없음) 결과를 3성분으로 옮겼고, 셋 다 그 약점을 스스로 적었습니다(M §6: "N₂ 가 끼면 S_humid 가 오히…](../questions/A-7.md) **공격** → B-2 — 위쪽 기각 조건 없음
- [A-14 A-2 의 본론입니다. 적재 표는 전부 재현되지만, 헨리 K_H(N₂)는 치환체에서 줄지 않았습니다(−1.7 ~ +16.6 %). N₂ 가 앉을 자리가 줄었다면…](../questions/A-14.md) **공격** → B-1 — A-2 본론
- [A-15 (질의 없음 — 재현) — 회차 상대 ± 평균(CN 7.0 % · Br 5.6 %)에서 3씨앗 자로 낸 기대 차 1.69 단위는 종합자 재계산(1.72)과 같습…](../questions/A-15.md) **근거** → B-2 — 재현 — 1.69 ≈ 1.72
- [A-16 전제가 바뀌었습니다: A 가 닫혀 HKHOME 이 지금부터 빕니다(21:2x). E 는 laptop2 15작업 완주(20:34) · 랩탑 6작업(mslm050 …](../questions/A-16.md) **공격** → B-7 — A 닫힘 전제로 재산정
- [A-17 ［미확인］ 둘(리간드 합성 · MOF 선례)이 후보② 의 "링커 합성이 가장 쉽다" 는 장점을 받칩니다. R3 에서 한 번 검색(CSD · 문헌)해 1,4-비스…](../questions/A-17.md) **공격** → B-6 — [미확인] 둘
- [SYN-sealed](../../../MAGI-007_sealed_prediction_cloud.md) **인용** → B-6 — 같은 방향(bib 2-Me)
- [Melchior M-C1 첫째 후보인 열린 자리 −C≡CH 는 CN 이득이 모양에서 오는지 극성에서 오는지를 구분합니다. CN 을 넘을 확률은 0.15 로 봅니다 `［가설］`](../../R1_laptop/note.md) **인용** → B-5 — 독립 수렴 — 열린 자리 −C≡CH

## 수비 (R3 · D-k → A-k)

- **D-1** 수용 **수용** → [A-1 종합자 오류가 먼저입니다. −C₂H₅ 를 E 에 넣자는 권고 근거로 "323 K 단독 선두(E-27b 92.99)" 를 적었는데, Melchior(§4 쓸 수 …](../questions/A-1.md) — 92.99 를 쓰지 않았음 · 정정에 이견 없음
- **D-2** 수정 **수용** → [A-2 기제가 두 층에서 다르게 읽히는데, 세 R1 이 한 층만 봤습니다. 원자료(Widom ON · results_magi5_e3_e24i_*_open_widom_*…](../questions/A-2.md) — 두 층 구분을 받아 원자료로 나눔(수정)
- **D-2** 수정 **반박** → [Balthasar B-1 이득의 출처](../../R1_laptop2/note.md) — N₂ 감소의 97~132 % 가 작동점 층 — 헨리 층 자리 감소 아님
- **D-2** 수정 **인용** → [Melchior M-10 이 비에 맞춘 헨리 근사로 열린 자리 −CN · −Br 의 323/298 비를 0.60~0.66 으로 봅니다 `［산술］` · `［가설］`](../../R1_laptop/note.md) — 헨리 ΔQ 근사는 S 이득의 헨리 층 몫(46~104 %)에만 섬
- **D-2** 수정 **인용** → [Caspar C-§1-③](../../R1_hkhome/note.md) — 작동점 비 S_mix/S_Henry 1.21 과 같은 양 — r_CO₂/r_N₂
- **D-2** 수정 **반박** → [Balthasar B-4 323 K(B)](../../R1_laptop2/note.md) — B 예측이 틀릴 길 — 작동점 층의 온도 민감도(수치는 그대로)
- **D-2** 수정 **근거** → [src:results_magi5_e3_e24i_widom](../../R3_laptop2/sources.md) — Widom ON K_H(CO₂) · K_H(N₂)
- **D-2** 수정 **근거** → [src:R1_laptop2_evidence.json](../../R3_laptop2/sources.md) — 작동점 적재(원자료 재계산값)
- **D-3** 수용 **수용** → [A-3 Caspar §4-6 재현. 23_SCREENING/final_ranking_smix.py 60행과 final_ranking.py 66행은 results_mag…](../questions/A-3.md) — R1 에 154.3 · 헨리 1위 없음
- **D-4** 수용 **수용** → [A-4 Caspar §4-7 재현. risk_screen.py 414~421행: 'PLD': (m0［'PLD'］ …) > CO2_KINETIC · 'AV': (m0.g…](../questions/A-4.md) — N₂ 탐침 통로 수 열 추가 제안
- **D-5** 수용 **수용** → [A-5 둘 다 재현. ① ours_extra_20260930.json 은 CN "141.5 ± 5.5" · Br "128.0 ± 5.1" 을 손으로 적은 문자열(3씨앗…](../questions/A-5.md) — 기록에 동의
- **D-6** 수용 **수용** → [A-6 A 는 21:2x 사용자 결정으로 측정 사실로 닫혔습니다(ASSIGN 종합자 확정 5: 이완본 −CN · −Br 모두 N₂ 통로 0 → S_mix 정의 안 됨 …](../questions/A-6.md) — A 예측 채점 불가 · B-10 dissent 거둠
- **D-6** 수용 **반박** → [Balthasar B-3 격자 이완(A)](../../R1_laptop2/note.md) — 자기 기록 — −Br 의 N₂ 통로 0 을 놓침
- **D-7** 수용 **수용** → [A-7 세 자리가 모두 CO₂–H₂O 이원(N₂ 없음) 결과를 3성분으로 옮겼고, 셋 다 그 약점을 스스로 적었습니다(M §6: "N₂ 가 끼면 S_humid 가 오히…](../questions/A-7.md) — 상한 위로 나오면 물이 N₂ 빈자리를 나눠 쓴 것
- **D-7** 수용 **근거** → [src:results_znbdt_e_humid3_laptop2](../../R3_laptop2/sources.md) — [E 결과 인용] 유지비 0.995~1.034 · N₂ 비 0.971~1.001
- **D-14** 수정 **수용** → [A-14 A-2 의 본론입니다. 적재 표는 전부 재현되지만, 헨리 K_H(N₂)는 치환체에서 줄지 않았습니다(−1.7 ~ +16.6 %). N₂ 가 앉을 자리가 줄었다면…](../questions/A-14.md) — B-1 해석 수정 — 자리 감소 철회
- **D-14** 수정 **반박** → [Balthasar B-1 이득의 출처](../../R1_laptop2/note.md) — 'N₂ 가 앉을 자리를 줄였다' 철회 · 바꾼 문장
- **D-14** 수정 **근거** → [src:results_e24i_blockpockets_hkhome](../../R3_laptop2/sources.md) — 자리 감소의 모양 — 막음 −C₂H₅ K_H(N₂) 0.62배
- **D-15** 수용 **수용** → [A-15 (질의 없음 — 재현) — 회차 상대 ± 평균(CN 7.0 % · Br 5.6 %)에서 3씨앗 자로 낸 기대 차 1.69 단위는 종합자 재계산(1.72)과 같습…](../questions/A-15.md) — 1.69 와 1.72 는 같은 산술
- **D-16** 수정 **수용** → [A-16 전제가 바뀌었습니다: A 가 닫혀 HKHOME 이 지금부터 빕니다(21:2x). E 는 laptop2 15작업 완주(20:34) · 랩탑 6작업(mslm050 …](../questions/A-16.md) — 일정 다시 냄 — ① 2~3일 · ② 3~5일(수정)
- **D-16** 수정 **반박** → [Balthasar B-7 일정](../../R1_laptop2/note.md) — 기기 제약이 HKHOME 한 기기로 바뀜
- **D-16** 수정 **인용** → [Caspar C-§2-점검⓪](../../R1_hkhome/note.md) — ② 의 선행 조건
- **D-17** 수정 **수용** → [A-17 ［미확인］ 둘(리간드 합성 · MOF 선례)이 후보② 의 "링커 합성이 가장 쉽다" 는 장점을 받칩니다. R3 에서 한 번 검색(CSD · 문헌)해 1,4-비스…](../questions/A-17.md) — 문헌 검색 한 번 — 등급 올림(수정)
- **D-17** 수정 **반박** → [Balthasar B-6 후보 ② bib 의 2-메틸이미다졸 판](../../R1_laptop2/note.md) — '합성이 가장 쉽다' 를 리간드 단계로 좁힘
- **D-17** 수정 **인용** → [Melchior M-§2](../../R1_laptop/note.md) — '잴 수 없다' 의 세 이유 — 층이 달라 함께 섬
- **D-17** 수정 **근거** → [src:Zhao2013_ICA_402_25](../../R3_laptop2/sources.md) — 같은 리간드의 Zn(II) 배위고분자 · COD 1517041

## 종합에서 인용 (R4)

- [S-1 열린 자리 치환의 이득은 두 층이고, R1 셋은 한 층만 적었습니다.](../consensus/S-1.md) **근거** → B-D-2 — 잔류비 · 추가 배제비
- [S-1 열린 자리 치환의 이득은 두 층이고, R1 셋은 한 층만 적었습니다.](../consensus/S-1.md) **근거** → B-D-14 — B-1 철회
- [S-2 E(습윤 3성분): 이 모델에서 물은 CO₂ 와도 N₂ 와도 자리를 다투지 않습니다 — 세 R1 예측 일치, E 결과가 확인](../consensus/S-2.md) **근거** → B-D-7 — [E 결과 인용] N₂ 분압비
- [S-5 Q2: 지금 다섯 설계를 주 축(S_humid)에서 1.5 단위 넘게 이길 개질은 저장소 근거로 제시된 것이 없습니다 — 세 자리 일치](../consensus/S-5.md) **근거** → B-5 — −C≡CH 독립
- [S-5 Q2: 지금 다섯 설계를 주 축(S_humid)에서 1.5 단위 넘게 이길 개질은 저장소 근거로 제시된 것이 없습니다 — 세 자리 일치](../consensus/S-5.md) **근거** → B-D-17 — bib 층 맞추기 · 문헌
- [S-6 Q3: HKHOME 이 비었으므로(A 닫힘) −C≡CH 는 착수 뒤 2~3일, bib 판은 점검⓪ 통과 뒤 3~5일](../consensus/S-6.md) **근거** → B-D-16 — 일정 재산정
- [S-7 Q4: 지금 쓸 수 있는 문장 / 쓸 수 없는 문장](../consensus/S-7.md) **근거** → B-R3-§4 — 두 층 문장
- [DEC-′2 관문 ⑤ 결과에 이완 후 PLD · AV · 두 탐침 통로 수 서술 열 (승인 대기)](../decisions.md) **근거** → B-D-4 — N₂ 통로 수 열 제안

Related: [Melchior](Melchior.md) · [Caspar](Caspar.md) · [Synthesizer](Synthesizer.md) · [간선 전체](../EDGES.md) · [INDEX](../../INDEX.md)
