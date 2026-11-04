---
title: "MAGI-007 Obsidian 금고"
date: 2026-11-05
tags: [MAGI-007, index]
aliases: [MAGI-007 금고]
---

# MAGI-007 Obsidian 금고 — 리간드 개질 토론(E · A · B 조건)의 자리별 참고 자료와 종합자 질문

**여는 법**: 이 폴더의 링크 중 `../../`·`../../../` 로 나가는 것은 저장소 문서를 가리킵니다. Obsidian 에서 그 링크까지 따라가려면 **`21_ZIF69_MTV/` (또는 저장소 뿌리)를 금고로 여십시오**. 이 폴더만 열면 묶음 안 링크와 그래프 층만 보입니다. 봉인 원본은 각 `R*_<기기>.tar.gz`(sha256 은 `COMMS/<기기>.md` 해시 줄과 같음) 이고, 풀린 폴더는 금고용 사본입니다 — 사본 중 손댄 곳은 `R3_laptop2/note.md` 의 Related 링크 넷(laptop2 00:38 정정표)뿐입니다.

## 그래프 층 (종합자가 edges.json 에서 생성 · `graph/build_graph.py`)

- [종합자](graph/seats/Synthesizer.md): 질문 17 · 합의 7 · 봉인 예측 · 결정 — 여기서 시작
- [Melchior (랩탑 · 이론)](graph/seats/Melchior.md): R1 주장 노드 · 받은 질의 · 수비 · 종합 인용
- [Balthasar (laptop2 · 실용)](graph/seats/Balthasar.md): R1 주장 노드 · 받은 질의 · 수비 · 종합 인용
- [Caspar (HKHOME · 비평)](graph/seats/Caspar.md): R1 주장 노드 · 받은 질의 · 수비 · 종합 인용
- [결정 노드](graph/decisions.md): R4 §5 권고 · 사용자 결정 · R4 뒤 ZNBDT-C1 / C2
- [간선 전체](graph/EDGES.md): 160 간선 표와 자리 사이 흐름 그림

### 질문 (R2 · 종합자 → 자리)

- [A-1 · 종합자 오류가 먼저입니다. −C₂H₅ 를 E 에 넣자는 권고 근거로 "323 K 단독 선두(E-27b 92.99)" 를 적었는데, Melchior(§4 쓸 수 …](graph/questions/A-1.md): ★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-2 · 기제가 두 층에서 다르게 읽히는데, 세 R1 이 한 층만 봤습니다. 원자료(Widom ON · results_magi5_e3_e24i_*_open_widom_*…](graph/questions/A-2.md): ★★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-3 · Caspar §4-6 재현. 23_SCREENING/final_ranking_smix.py 60행과 final_ranking.py 66행은 results_mag…](graph/questions/A-3.md): ★★★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-4 · Caspar §4-7 재현. risk_screen.py 414~421행: 'PLD': (m0［'PLD'］ …) > CO2_KINETIC · 'AV': (m0.g…](graph/questions/A-4.md): ★★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-5 · 둘 다 재현. ① ours_extra_20260930.json 은 CN "141.5 ± 5.5" · Br "128.0 ± 5.1" 을 손으로 적은 문자열(3씨앗…](graph/questions/A-5.md): ★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-6 · A 는 21:2x 사용자 결정으로 측정 사실로 닫혔습니다(ASSIGN 종합자 확정 5: 이완본 −CN · −Br 모두 N₂ 통로 0 → S_mix 정의 안 됨 …](graph/questions/A-6.md): ★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-7 · 세 자리가 모두 CO₂–H₂O 이원(N₂ 없음) 결과를 3성분으로 옮겼고, 셋 다 그 약점을 스스로 적었습니다(M §6: "N₂ 가 끼면 S_humid 가 오히…](graph/questions/A-7.md): ★ · 1. 공통 — 세 R1 에 같이 걸리는 것
- [A-8 · ΔQ 12.86 kJ/mol 과 비 0.645 · 0.635 는 재현됩니다. 그러나 "치환이 N₂ 쪽 흡착열을 바꾸지 않는다" 는 가정이 아니어도 됩니다 — 같…](graph/questions/A-8.md): ★ · 2. Melchior(랩탑) — 단계별
- [A-9 · 각주가 밝힌 대로 수치 셋이 바뀌었습니다(12.87 → 12.85 · 0.644 → 0.645 · 0.634 → 0.635). 범위 · 결론 불변이고 두 판 모…](graph/questions/A-9.md): ★ · 2. Melchior(랩탑) — 단계별
- [A-10 · −NO₂ 열린 자리는 전 치환판에서 S_ON 을 보존했고(E-22b: 87.8 → 88.9, 정전기 몫을 바닥으로 옮김) 물 지수를 10배 올렸습니다(E-22c…](graph/questions/A-10.md): ★ · 2. Melchior(랩탑) — 단계별
- [A-11 · 기록(비난 아님). 자백대로 4c64fb91 은 봉인 근거의 결과 일부를 공개 전에 냈습니다. 다른 두 R1 에 그 수가 없어 오염 흔적은 없고, E 실행 CI…](graph/questions/A-11.md): ★ · 3. Caspar(HKHOME) — 단계별
- [A-12 · build_e24i_bdtdc.py 의 sites() 결과는 자리마다 ring 번호만 갖고 4-자리와 8-자리를 가르는 속성이 없습니다(종합자가 파일을 읽음 —…](graph/questions/A-12.md): ★ · 3. Caspar(HKHOME) — 단계별
- [A-13 · 세는 양이 정의되지 않았습니다: 어느 격자(건조 ON? 습윤?) · 어느 등가면(밀도 상위 몇 %) · "접촉" 의 거리 문턱 · bib 의 어느 원자(이미다졸…](graph/questions/A-13.md): ★ · 3. Caspar(HKHOME) — 단계별
- [A-14 · A-2 의 본론입니다. 적재 표는 전부 재현되지만, 헨리 K_H(N₂)는 치환체에서 줄지 않았습니다(−1.7 ~ +16.6 %). N₂ 가 앉을 자리가 줄었다면…](graph/questions/A-14.md): ★★ · 4. Balthasar(laptop2) — 단계별
- [A-15 · (질의 없음 — 재현) — 회차 상대 ± 평균(CN 7.0 % · Br 5.6 %)에서 3씨앗 자로 낸 기대 차 1.69 단위는 종합자 재계산(1.72)과 같습…](graph/questions/A-15.md): — · 4. Balthasar(laptop2) — 단계별
- [A-16 · 전제가 바뀌었습니다: A 가 닫혀 HKHOME 이 지금부터 빕니다(21:2x). E 는 laptop2 15작업 완주(20:34) · 랩탑 6작업(mslm050 …](graph/questions/A-16.md): ★ · 4. Balthasar(laptop2) — 단계별
- [A-17 · ［미확인］ 둘(리간드 합성 · MOF 선례)이 후보② 의 "링커 합성이 가장 쉽다" 는 장점을 받칩니다. R3 에서 한 번 검색(CSD · 문헌)해 1,4-비스…](graph/questions/A-17.md): ★ · 4. Balthasar(laptop2) — 단계별

### 합의 (R4)

- [S-1 · 열린 자리 치환의 이득은 두 층이고, R1 셋은 한 층만 적었습니다.](graph/consensus/S-1.md)
- [S-2 · E(습윤 3성분): 이 모델에서 물은 CO₂ 와도 N₂ 와도 자리를 다투지 않습니다 — 세 R1 예측 일치, E 결과가 확인](graph/consensus/S-2.md)
- [S-3 · A(격자 이완): 측정 사실로 닫힘](graph/consensus/S-3.md)
- [S-4 · B(323 K): 순서 유지 · 크기는 약 0.6배 — 세 R1 방향 일치, 크기는 셋 다 조금 높게 봤습니다](graph/consensus/S-4.md)
- [S-5 · Q2: 지금 다섯 설계를 주 축(S_humid)에서 1.5 단위 넘게 이길 개질은 저장소 근거로 제시된 것이 없습니다 — 세 자리 일치](graph/consensus/S-5.md)
- [S-6 · Q3: HKHOME 이 비었으므로(A 닫힘) −C≡CH 는 착수 뒤 2~3일, bib 판은 점검⓪ 통과 뒤 3~5일](graph/consensus/S-6.md)
- [S-7 · Q4: 지금 쓸 수 있는 문장 / 쓸 수 없는 문장](graph/consensus/S-7.md)

## 자리별 봉인 묶음 (제출 해시 = 봉인 해시 · 종합자 대조 11-05 01:3x)

- **R1_laptop** (Melchior · sha256 822bfbd2): [note](R1_laptop/note.md) · [sources](R1_laptop/sources.md) · `edges.json` · [r1_predictions_melchior.csv](R1_laptop/assets/r1_predictions_melchior.csv) · [tar 원본](R1_laptop.tar.gz)
- **R1_laptop_v1224** (Melchior · sha256 ee5be14f (12:24 판 · 보존)): [note](R1_laptop_v1224/note.md) · [sources](R1_laptop_v1224/sources.md) · `edges.json` · [r1_predictions_melchior.csv](R1_laptop_v1224/assets/r1_predictions_melchior.csv) · [tar 원본](R1_laptop_v1224.tar.gz)
- **R1_laptop2** (Balthasar · sha256 038401ab): [note](R1_laptop2/note.md) · [sources](R1_laptop2/sources.md) · `edges.json` · [b1_b3_evidence_table.csv](R1_laptop2/assets/b1_b3_evidence_table.csv) · [tar 원본](R1_laptop2.tar.gz)
- **R1_hkhome** (Caspar · sha256 8e982397): [note](R1_hkhome/note.md) · [sources](R1_hkhome/sources.md) · `edges.json` · [pairwise_units.csv](R1_hkhome/assets/pairwise_units.csv) · [tar 원본](R1_hkhome.tar.gz)
- **R3_laptop** (Melchior · sha256 0c113d9f): [note](R3_laptop/note.md) · [sources](R3_laptop/sources.md) · `edges.json` · [r3_a8_dq_n2.json](R3_laptop/assets/r3_a8_dq_n2.json) · [r3_a8_dq_n2.out](R3_laptop/assets/r3_a8_dq_n2.out) · [r3_a8_dq_n2.py](R3_laptop/assets/r3_a8_dq_n2.py) · [tar 원본](R3_laptop.tar.gz)
- **R3_laptop2** (Balthasar · sha256 dbb15c1f): [note](R3_laptop2/note.md) · [sources](R3_laptop2/sources.md) · `edges.json` · [two_layers.csv](R3_laptop2/assets/two_layers.csv) · [tar 원본](R3_laptop2.tar.gz)
- **R3_hkhome** (Caspar · sha256 42a6498c): [note](R3_hkhome/note.md) · [sources](R3_hkhome/sources.md) · `edges.json` · [loadings_three_conditions.csv](R3_hkhome/assets/loadings_three_conditions.csv) · [tar 원본](R3_hkhome.tar.gz)

## 종합자 자료

- **R2_cloud**: [note](R2_cloud/note.md) · [sources](R2_cloud/sources.md) · `edges.json` — R2 질의 17건의 그래프 판
- **R4_cloud**: [note](R4_cloud/note.md) · [sources](R4_cloud/sources.md) · `edges.json` — R4 종합의 그래프 판

## 원문 (저장소 · 이 폴더 밖)

- [MAGI-007_brief.md](../MAGI-007_brief.md): 브리핑 v3 — 질문 · 규율 · 시한 · 운영 제약
- [MAGI-007_sealed_prediction_cloud.md](../MAGI-007_sealed_prediction_cloud.md): 종합자 봉인 예측(평문 · 공개 뒤)
- [MAGI-007_R1_laptop.md](../MAGI-007_R1_laptop.md): R1 Melchior
- [MAGI-007_R1_laptop2.md](../MAGI-007_R1_laptop2.md): R1 Balthasar
- [MAGI-007_R1_hkhome.md](../MAGI-007_R1_hkhome.md): R1 Caspar
- [MAGI-007_R2_attack.md](../MAGI-007_R2_attack.md): R2 종합자 질의 A-1~A-17
- [MAGI-007_R3_laptop.md](../MAGI-007_R3_laptop.md): R3 Melchior
- [MAGI-007_R3_laptop2.md](../MAGI-007_R3_laptop2.md): R3 Balthasar
- [MAGI-007_R3_hkhome.md](../MAGI-007_R3_hkhome.md): R3 Caspar
- [MAGI-007_ligand-modification.md](../MAGI-007_ligand-modification.md): R4 종합 · 결정 · §10 연락 사례 · §11 보완 단계
- [ASSIGN_ZNBDT_SUPP_20261103.md](../../ASSIGN_ZNBDT_SUPP_20261103.md): E · A · B 등록
- [MAGI_20260905.md](../../MAGI_20260905.md): 규약(§11-2 봉인 · §11-5 격리/보완)
