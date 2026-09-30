# 등록 — 최종 순위표: CoRE 모집단(우리 자) + 기존 물질 앵커 + 우리 조성을 한 자 위에 (2026-09-30 13:43, HKHOME · 자료를 보기 전에 씀)

**요청**: 사용자 "우리 최종 결과표 core 스크리닝으로 최종 순위표 내줘, 기존 ipynb 바탕으로 · 기존 물질들 전부 포함시켜서".
**왜 지금은 합친 순위가 허용되는가**: 09-20 의 `OURS_VS_CORE`·`place_ours.py` 는 CoRE **배포 값**(UFF+TraPPE 계열)과 우리 값을 섞지 않았다(다른 자). 09-21 §AV(`COREPOP_REGISTRATION_20260921.md`)가 CoRE 524종을 **우리 프로토콜**(UFF_MOF · García-Sánchez CO₂ · PACMAN DDEC6 · 298 K Widom 15,000)로 다시 계산했으므로, **Widom 축(K_H(CO₂) · 헨리 선택도)** 에서는 이제 같은 자다. 이 표는 그 축에서만 순위를 매긴다. S_mix · 물 지수 · 습윤 WC 는 우리 조성에만 있으므로 **순위 축이 아니라 병기 열**이다.

## 1. 모집단(전부 우리 자 298 K Widom · 전하 ON · 차단 없음)
| 부류 | 출처 | 수 | 표지 |
|---|---|---|---|
| CoRE 기존 물질 | `21_ZIF69_MTV/core_pop_annotated.json` (524, §AV 관문 ①~⑤ 통과: 뼈대 안정(미상 탈락) · SI 출처 · ≤ 400 원자 · UFF_MOF 표현 가능 · Widom 유한) | 524 | `CoRE` |
| 문헌 앵커 기존 물질 | 우리 자로 Widom 을 돌린 외부 물질(ZIF-93 · ZIF-90 · ZIF-71 · ZIF-68 · MUF-16 · MAF-66 · CALF-20 · IISERP-MOF16 등 — 탐색 에이전트가 파일에서 찾는 대로, **조건: 298 K · 현재 자 · 전하 ON · 차단 없음 · 완주 표지**) | 조사 중 | `앵커` |
| 우리 모체(기존 물질) | ZIF-69 `base`(`results_v3.json`) · Zn(bib)(bdtdc) `e22_parent`(`results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json`) | 2 | `모체` |
| 우리 설계 조성 | ZIF-69 치환 30(`results_v3.json`) + 혼합 3(`results_v4mix.json`) + 형판 열린 자리 치환 5(`results_magi5_e3_e24i_*_open_widom_*.json`) | 38 | `설계` |
| 제외(중복·변형) | E-22e 의 CoRE 형판 5종(524 안에 이미 있음 — 같은 물질 두 번 세지 않음) · E-22d 기하/전하 변형 2(같은 물질의 감도 시험) · 형판 4,8-전치환 계열 전부(E-22 −NO₂ 2 · E-24/E-24g/E-24h — 보류·인용 금지, `MAGI5_E22_VERDICT §25`) | — | — |

## 2. 관문(순위 전 제외 — 계산 후 바꾸지 않음)
1. **탐침 규약값**: PLD < 3.64 Å 인 행은 순위·백분위에서 제외(사용자 결정 2026-09-25 2번, `core_pop_annotated.probe_convention`). **우리 행에도 같은 자**: Widom 을 돌린 구조의 PLD(`results_v3.PLD` · E-24i/E-22 는 gate5 파일의 `before.PLD`).
2. **짝이온 삭제**: `formal_charge_nonzero == True` 제외(같은 결정 3번). `None`(미검사)은 통과시키되 표지.
3. **우리 안정성 관문 ⑤**: 설계 조성은 `risk_results_*` / `results_*gate5*` 의 `pass` 가 False 면 제외(LCD 감소 ≥ 20 %: saIm075 · saIm100 등). 기존 물질에는 걸지 않는다(실재하는 구조).
4. **Widom 건전성**: 0 < K_H < 1 mol/kg/Pa 둘 다(`screen_core.WIDOM_SANITY_MAX`).
5. 원본 노트북의 위양성 필터(dimension == 3 · PLD ≥ 3.4 · VF ≥ 0.2)는 **주 표에 걸지 않고** `dim` 열로 병기한다 — 2D 층상 골격 173종을 관문 없이 버리면 위음성이 되고(감사 §3), 우리 조성은 dim 값이 없다. 부표로 "3D 만" 을 따로 낸다.

## 3. 축과 순위 규칙(원본 노트북 → 감사 정정판)
- 축 ①(주): **헨리 선택도 S = K_H(CO₂)/K_H(N₂)**. 오차 = S·√((e_C/K_C)² + (e_N/K_N)²)(CoRE 행은 `selectivity_err` 가 없어 전파식으로; 우리 행은 저장된 `selectivity_err` 와 전파식이 같음을 검산).
- 축 ②(부): **K_H(CO₂)**("CO₂ 친화도", 원본의 `Widom[0]`) ± 저장 오차.
- 순위: `screen_core.rank()` — 내림차순 정렬 뒤 **인접 차이 ≥ 1.5 × √(e_a² + e_b²)** 일 때만 덩어리를 가른다(CLAUDE.md §2, D4 정정). 덩어리 번호가 순위이고, 덩어리 안은 동률.
- 백분위: 우리 행 각각에 대해 **"관문 통과 CoRE 풀(§2 적용 뒤) 중 우리보다 낮은 비율"**. 풀 최대보다 위면 백분위 대신 "풀 최대보다 위"(`COREPOP` 규약 (ㄷ)). 풀 정의를 문장에 항상 붙인다((ㄴ)).
- 원본 점수 0.6×선택도 + 0.4×친화도(상위 5 % 클리핑, 셀 69 `robust_scoring`)는 **참고 열**로만 재현한다(D5: 임의 가중). 순위는 이 점수로 매기지 않는다.

## 4. 병기 열(순위 축 아님)
우리 조성·모체: S_mix(작동점, 3씨앗) · 물 지수 · 건조 0.15 bar 적재 · 습윤 TSA WC — `MAGI5_DESIGN_FINAL_20260926.md` 표 값 그대로. CoRE 행: `topo` · `metal` · `dim` · `set`.

## 5. 예측(자료 보기 전)
- 헨리 선택도 상위 덩어리는 CoRE 행이 차지할 것(`GATE_SAIM100`: 우리 최고 통과 조성 saIm050 65.2 가 관문 통과 풀의 87 %; 2016_Co__sql 계열 603 등 상위는 탐침 규약값으로 빠짐). 형판 열린 자리 −C₂H₅(154) · −CN(117) · −Br(128) · −CH₃(128) 은 **90~97 % 대**, 형판 모체(87.8)는 약 90 %, ZIF-69 base(20.1)는 50~60 %.
- K_H(CO₂) 축에서는 형판 계열(0.9~1.5e-3)이 CoRE 상위 5 % 안(풀 최대 1.5e-2).
- 앵커: MUF-16 · CALF-20 은 선택도 상위, ZIF-71/90/93 은 하위(우리 자에서 ZIF 선택도 20~40).

## 6. 산출
`23_SCREENING/final_ranking.py` → `FINAL_RANKING_20260930.md`(등록 요약 · 상위 40 표 · 우리 행 전부의 위치 · K_H 축 상위 20 · 3D 부표 · 앵커 절) + `final_ranking_20260930.csv`(전체 행). 기록: SESSION_LOG · COMMS.
