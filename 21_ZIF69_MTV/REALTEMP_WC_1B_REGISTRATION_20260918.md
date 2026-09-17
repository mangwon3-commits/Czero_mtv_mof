# T-RT-1b 등록 — **실온도(323 K) 절대 작업 용량, 술포닐 앙상블 `mslm050e1~e5`** (2026-09-18 00:3x, 종합자; **자료 0건**; 사용자 승인 "권고안대로")

**왜**: T-RT-1(`REALTEMP_WC_REGISTRATION_20260916.md`, 랩탑 진행 중 15/48)은 "공동 1위 덩어리 셋 + 모체" 16종입니다. 09-18 00:2x 의 `WC_RECOMPUTE_RESULT §9` 로
**술포닐 앙상블이 그 덩어리에 들어왔습니다**(네 앙상블 대비 전부 못 가름, 예측 4/4). 덩어리를 같은 온도에서 닫으려면 술포닐도 323 K 에서 재야 합니다.
데스크탑 유휴(§AJ 완주 09-17 18:09 뒤 6시간 놀림), 등록된 미착수 배정 없음 → CLAUDE.md §9. 랩탑 T-RT-1 과 조율 불필요(다른 기기·다른 결과 파일·다른 대상).
**결과를 본 뒤 자·문턱·예측을 고치지 않습니다.** T-RT-1 등록의 §1·§3·§5·§6 을 그대로 물려받고, 아래는 다른 점만 적습니다.

## 1. 조건 — T-RT-1 §1 과 완전히 같음
    러너 `run_humid_wc_v3w_323.py`(래퍼), P_H2O 11,114.1 Pa 고정, ads 323 K·0.15 bar / tsa 373 K·0.15 bar / vsa 323 K·0.05 bar. 파일 관문 md5 8e8ec933… 래퍼가 검사.
    HWC_323_TARGETS=mslm050e1,mslm050e2,mslm050e3,mslm050e5,mslm050e4  HWC_323_WORKERS=8  HWC_323_RESULT=humid_wc_323_mslm050e_desk.json  HWC_323_MACHINE=desktop
    CIF `charged_v3/mslm050e{1..5}_DDEC6.cif`(T-SA-1 앞단, 관문 7/7 — §AJ 와 같은 파일). 실행 폴더 `humid_wc_runs_v3w_323/`(데스크탑에는 아직 없음 — 착수 전 확인).

## 2. 대상 — 5종 · 15작업, 순서 = 298 K ads 상자 분자 수 내림차순(T-RT-1 §2 규약 그대로)
    mslm050e1 (2.30) · e2 (1.99) · e3 (1.95) · e5 (1.87) · e4 (1.71)   (298 K ads CO₂+물, `humid_working_capacity_w2_mslm050e_desk.json`)
    ⚠ Melchior 가 09-17 05:35 에 "상자 분자 수는 323 K 계열에서 비용 대리 지표로 안 듣는다" 고 보고했습니다(saIm0583e1 2.19 가 e4 2.30 보다 오래). **순서 규약은 바꾸지 않되** 이 한계를 적어 둡니다 — 5종이라 순서 효과는 작습니다.
    소요: T-RT-1 실측 첫 ads 15.2 h(saIm0583e4). 술포닐은 물이 saIm 급(298 K 0.66~1.52 mol/kg)이라 같은 급으로 봅니다 → 8워커, 15작업 두 물결 **30~40 h** → 09-19 낮~저녁. 첫 ads 완주로 갱신.

## 3. 관측량과 자 — T-RT-1 §3 그대로, 대상만 mslm050e
    Q1 온도 효과(짝) — d1_k = WC_TSA,323(e_k) − WC_TSA,298(e_k), R_k = 비. 정본 짝 SD 형, SE 형·단위(±)·R 평균 ± SD 병기.
        **298 K 분모(고정)** — 전부 `v3w_humid_wc/humid_working_capacity_w2_mslm050e_desk.json`, 데스크탑, 열 working_capacity.tsa:
            mslm050e1 0.6283±0.0192 · e2 0.6852±0.0239 · e3 0.6961±0.0195 · e4 0.8518±0.0246 · e5 0.8120±0.0290
            VSA 분모(working_capacity.vsa): 0.4403 / 0.4692 / 0.4416 / 0.5280 / 0.5565
            흡착 A_298·잔류 t_298(loadings.ads/tsa CO2): e1 0.7805/0.1522 · e2 0.8595/0.1744 · e3 0.8704/0.1744 · e4 1.0557/0.2038 · e5 0.9979/0.1859
        기기: 323 K·298 K **둘 다 데스크탑** — T-RT-1 의 기기 항 ⚠ 가 이 짝에는 없습니다(§AG 로 기기 항 없음도 별도 확인됨).
    Q2 앙상블 순위(323 K) — mslm050e 대 saIm050e·saIm0583e·sa50nb50e(**T-RT-1 결과가 와야 판정 가능**), SD 형(정본)·SE 형·단위, 문턱 1.5. base 대 mslm050e 는 mslm050e SD 분모.
        T-RT-1 이 먼저 끝나면 그 판정문(Q2, 셋)에 이 넷째를 **덧붙이는** 방식 — T-RT-1 의 Q2 판정은 이 결과로 바뀌지 않습니다(다른 등록).
    Q3 TSA 대 VSA(323 K, 짝) — d3_k, 비 Q_k, 298 K 비 Q_298 = 1.427 / 1.460 / 1.576 / 1.613 / 1.459 와의 짝 차 ΔQ_k → 짝 SD 형.
    Q4 없음 — 러너·기기 대조(base)는 T-RT-1 Q4 가 맡습니다. 이 등록에는 base 가 없습니다.

## 4. 예측 (자료 0건) — 틀리면 즉시 물린다
    Q1  **갈림(음)**: 다섯 짝 전부 d1_k < 0. 크기: R_k ≈ (a·A_298 − t_298)/(A_298 − t_298), a = 0.47~0.53 → 실현별 **0.34~0.44**. 반증(크기): R 평균이 [0.30, 0.47] 밖.
    Q2  **못 가름(덩어리 유지)**: 세 쌍 |SD 형| < 1.5. base 는 아래(≤ −1.5, mslm050e SD 분모). 반증: 한 쌍이라도 갈림 / base > −1.5.
        (자기 한계 예고: 298 K 에서 saIm0583e 쌍이 −0.82(SE −1.84)로 두 식 사이였으므로 323 K 에서 SE 형 갈림·SD 형 못 가름이 다시 나올 수 있음 — 그 경우 "두 식 사이" 로 적고 정본은 SD 형.)
    Q3  **TSA > VSA 5/5**, Q 낮아짐(1.2~1.45), ΔQ 짝 SD 형 ≤ −1.5.
    반증 조건: T-RT-1 §4 와 같음(Q1 한 짝이라도 ≥ 0 / Q2 갈림 또는 base 조건 미달 / Q3 혼재·역전 또는 ΔQ ≥ +1.5).

## 5. 자료 모양·결측 — T-RT-1 §5 그대로(n=5 짝, 결측 k 는 양쪽에서 뺌, Q2 는 T-RT-1 과 같은 k 를 뺌, PARTIAL 은 완주 아님).
## 6. 말할 수 없는 것 — T-RT-1 §6 (a)(c)(d) 그대로. (b) 기기 항은 이 짝에는 해당 없음.

## 7. 착수 절차 — 데스크탑(종합자)
    1) `pgrep -x simulate` 0 · `humid_wc_runs_v3w_323/` 에 mslm050e 폴더 없음 · `df /mnt/c` 여유 확인.
    2) `HWC_323_DRYRUN=1` 로 관문·사전검사·작업 목록 확인 → 착수:
       HWC_323_TARGETS=… HWC_323_WORKERS=8 HWC_323_RESULT=humid_wc_323_mslm050e_desk.json HWC_323_MACHINE=desktop \
         setsid nohup ~/miniconda3/envs/czeromof/bin/python run_humid_wc_v3w_323.py > ../.claude_work_wc323_mslm050e.out 2>&1 < /dev/null &
    3) 감시는 일 기반(`<RESULT>.status.jsonl`·결과 파일). 머리말 관문은 첫 Output 에서 사람이 한 번. 완주 → JSON 커밋·푸시 → 판정(§3), 검산 Melchior·Balthasar.

## 8. 진행 기록
    [09-18 00:2x] 사용자 "권고안대로" → 등록(자료 0건).
    [09-18 00:16] DRYRUN 통과(md5 8e8ec933 일치 · 자식 대조 일치 · 기존 .data 0/15 · simulate 0 · C: 42 G). **착수 00:16**(데스크탑): 15작업 워커 8, simulate 8, 가용 메모리 12 GB.
                  드라이버 **PID 10450**(ppid 10448 = 집합 밖, 착수 90초 뒤). 머리말 관문 첫 Output ads_mslm050e1: Ow-Ow ε 89.633 · Hw-Hw/Hw-Lw ZERO_POTENTIAL — 통과.
                  결과 v3w_humid_wc_323/humid_wc_323_mslm050e_desk.json, 상태 .status.jsonl, 로그 .claude_work_wc323_mslm050e.out. 감시 일 기반. ETA 30~40 h → 09-19 낮~저녁.
