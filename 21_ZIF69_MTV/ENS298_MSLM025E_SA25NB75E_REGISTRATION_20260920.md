# 298 K 습윤 WC 앙상블 — `mslm025e1~e5` → `sa25nb75e1~e5` (laptop2) — 등록 (2026-09-20 00:07, 데스크탑 세션; **자료 0건** — 두 앙상블 모두 298 K 습윤 WC 가 한 실현도 없음; 사용자 승인 2026-09-20 "do it")

## 1. 왜
WC §10(확정 09-19 23:0x)은 다섯 앙상블(saIm050e 0.7347 · saIm0583e 0.8247 · sa50nb50e 0.7591 · mslm050e 0.7347 · saIm025e 0.7639)을 한 덩어리로, nbIm050e(0.6809)를 그 아래로 읽는다.
덩어리의 경계가 어디인지 — 술포닐 25 %(mslm025e), 술폰산 25 %+니트로 75 %(sa25nb75e) — 는 아직 실현 0건이다. 관문은 이미 통과(relax_v3_judged pass 5/5, risk_results_v3ruler pass 5/5), 전하 CIF `charged_v3/mslm025e{1..5}_DDEC6.cif` 5/5 존재, sa25nb75e 는 사슬이 착수 전 확인.

## 2. 조건 — §AI(nbIm050e)·§AK(saIm025e) 와 완전히 같음
    `run_humid_wc_v3w.py`(298 K·RH90 P_H2O 2,852.1 Pa → 373 K TSA / 298 K·0.05 bar VSA), CLAUDE.md §1 고정값, 파일 관문 md5 8e8ec933 선행(러너가 검).
    1차  HWC_V3W_TARGETS=mslm025e1,…,e5  HWC_V3W_WORKERS=12  HWC_V3W_RESULT=humid_working_capacity_w2_mslm025e_laptop2.json  (15작업)
    2차  HWC_V3W_TARGETS=sa25nb75e1,…,e5 HWC_V3W_WORKERS=12  HWC_V3W_RESULT=humid_working_capacity_w2_sa25nb75e_laptop2.json (15작업, 1차 완주 뒤 자동)
    소요 nbIm050e 가 같은 기기에서 11h15m. mslm025e 는 물이 적은 계(술포닐, 공여-H 없음) → **10~13 h**; sa25nb75e 는 니트로 75 % 라 비슷 → 09-20 04:00 착수 → 1차 ~17:00, 2차 09-21 새벽. 자 = 배치 단위(실현 SD) · 단위(±) 병기.
## 3. 판정 (결과 전 고정 — RULER §7 두 식 병기, 문턱 1.5)
    mslm025e   예측: mslm050e·saIm025e 와 **못 가름**(덩어리 안), nbIm050e 위로 **갈림 +**, base 0.4692 위. 반증: mslm050e 아래로 갈림(≤ −1.5 배치 단위) 또는 nbIm050e 와 못 가름.
    sa25nb75e  예측: sa50nb50e 와 nbIm050e **사이** — nbIm050e 아래로 안 떨어지고(부호 +) sa50nb50e 위로 안 오름. 반증: nbIm050e 아래로 갈림, 또는 sa50nb50e 위로 갈림.
    물         RH90 물 로딩 기록(mslm 계 0.1~0.8 예상). 판정 축 아님.
    결측       15작업 중 결측이 있으면 n 을 줄여 적고 "결측 k" 를 표에 남긴다(등록 §4 규칙과 같음).
## 4. 절차 (laptop2, Balthasar)
    사슬 `.claude_work_wc298_l2_chain.sh`: 1C 드라이버(run_humid_wc_v3w_323.py)·simulate 0 이 3분 연속 → `git status --porcelain -uno` 기록 → 전하 CIF 5/5 확인 → 1차 → 2차. 로그 `wc298_l2_chain.log`.
    기동(지금, 1C 가 도는 채로 — 사슬이 기다린다): cd ~/mof_project && git merge origin/master && setsid nohup bash .claude_work_wc298_l2_chain.sh > .claude_work_wc298_l2.out 2>&1 < /dev/null &
    머리말 관문은 첫 Output 에서 사람이 한 번. 결과 JSON 은 postman 이 올림. 판정 종합자, 검산 Melchior.
## 5. 진행 기록
    [2026-09-20 00:07] 등록(자료 0건). ASSIGN §AT.
