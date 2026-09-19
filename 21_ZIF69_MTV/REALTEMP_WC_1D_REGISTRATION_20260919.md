# T-RT-1d 등록 — **실온도(323 K) 절대 작업 용량, 저술폰산 앙상블 `saIm025e1~e5`** (2026-09-19 15:0x, 종합자; **자료 0건**; 사용자 지시 09-19 "C. … 1D 는 랩탑이 T-RT-1 뒤")

**왜**: WC §10(09-19 15:0x, 이의 대기)이 저술폰산 앙상블을 298 K 공동 1위 덩어리에 넣었습니다(네 앙상블과 못 가름, 니트로 위). 323 K 덩어리(T-RT-1 셋 + 1B 술포닐)에 이것만 없습니다.
**⑤ 관문 7/7 통과분**이라 다섯 실현 전부 대상입니다(탈락 실현 0 — 있었다면 그 k 를 빼고 n 을 줄여 병기했을 것).
**REALTEMP_WC_1B_REGISTRATION_20260918.md 를 그대로 물려받고, 대상과 298 K 분모만 바꿉니다**(1B → T-RT-1 §1·§3·§5·§6 세 겹 상속). 아래는 다른 점만.
**결과를 본 뒤 자·문턱·예측을 고치지 않습니다.**

## 1. 조건 — 1B §1 과 완전히 같음
    러너 `run_humid_wc_v3w_323.py`, P_H2O 11,114.1 Pa 고정, ads 323 K·0.15 bar / tsa 373 K·0.15 bar / vsa 323 K·0.05 bar. 파일 관문 md5 8e8ec933… 래퍼가 검사.
    HWC_323_TARGETS=saIm025e1,saIm025e2,saIm025e3,saIm025e4,saIm025e5  HWC_323_WORKERS=8  HWC_323_RESULT=humid_wc_323_saIm025e_laptop.json  HWC_323_MACHINE=laptop
    CIF `charged_v3/saIm025e{1..5}_DDEC6.cif`(laptop2 앞단 3c81d1a, 관문 7/7). 실행 폴더 `humid_wc_runs_v3w_323/`(랩탑에는 T-RT-1 폴더가 있음 — **태그가 다르므로 겹치지 않음**; 착수 전 saIm025e 폴더 없음 확인).
    **기기: 랩탑(Melchior)**, 8워커 — T-RT-1 이 09-18 19:52 완주해 비어 있음(사용자 지시 "T-RT-1 완주 뒤" 조건 충족).

## 2. 대상 — 5종 · 15작업, 순서 = 298 K ads 상자 분자 수 내림차순(T-RT-1 §2 규약)
    saIm025e1 (1.412) · e2 (1.342) · e3 (1.321) · e4 (1.190) · e5 (1.182)   (298 K ads CO₂+물, `humid_working_capacity_w2_saIm025e_laptop2.json`)
    소요: T-RT-1 실측 첫 ads 15.2 h(saIm0583e4, 물 2.19). 저술폰산 298 K 물 0.26~0.56 으로 술폰산 50·58 %(0.7~1.9)보다 적어 **12~20 h**(8워커, 두 물결). 첫 ads 완주로 갱신.

## 3. 관측량과 자 — T-RT-1 §3 그대로, 대상만 saIm025e
    Q1 온도 효과(짝) — d1_k = WC_TSA,323(e_k) − WC_TSA,298(e_k), R_k = 비. 정본 짝 SD 형, SE 형·단위(±)·R 평균 ± SD 병기.
        **298 K 분모(고정)** — 전부 `v3w_humid_wc/humid_working_capacity_w2_saIm025e_laptop2.json`, laptop2, 열 working_capacity.tsa(WC §10 표와 같음):
            saIm025e1 0.7009±0.0293 · e2 0.7928±0.0240 · e3 0.7964±0.0251 · e4 0.7595±0.0246 · e5 0.7697±0.0142
            VSA 분모(working_capacity.vsa): 0.4776 / 0.5395 / 0.5434 / 0.5274 / 0.5274
            흡착 A_298·잔류 t_298(loadings.ads/tsa CO2): e1 0.8478/0.1469 · e2 0.9581/0.1654 · e3 0.9661/0.1697 · e4 0.9209/0.1614 · e5 0.9246/0.1549
        ⚠ 이 짝은 **기기가 다릅니다**(323 K 랩탑, 298 K laptop2). 직접 잰 기기 항은 laptop2 대 데스크탑(§AG, 0.06 단위 → 없음)과 랩탑 대 데스크탑(T-RT-1 Q4, base |d| 0.00001)뿐 — 랩탑 대 laptop2 는 그 둘의 이음으로만 지지됨. R 표에 병기(판정 규칙 불변).
    Q2 앙상블 순위(323 K) — saIm025e 대 saIm050e·saIm0583e·sa50nb50e(T-RT-1)·mslm050e(1B)·nbIm050e(1C, 도착하면), SD 형(정본)·SE 형·단위, 문턱 1.5. base(0.1914) 대 saIm025e 는 saIm025e SD 분모.
        T-RT-1·1B·1C 의 Q2 판정은 이 결과로 바뀌지 않습니다 — **덧붙이는** 방식.
    Q3 TSA 대 VSA(323 K, 짝) — d3_k, 비 Q_k, 298 K 비 Q_298 = 1.468 / 1.470 / 1.466 / 1.440 / 1.459 와의 짝 차 ΔQ_k → 짝 SD 형.
    Q4 없음 — base 는 T-RT-1 Q4(일치).

## 4. 예측 (자료 0건) — 틀리면 즉시 물린다
    사전 자료: T-RT-1(R 0.405~0.426 · Q 1.10~1.15) · 1B(R 0.397 · Q 1.05) 가 이미 있습니다.
    Q1  **갈림(음)**: 다섯 짝 전부 d1_k < 0. 크기: R_k ≈ (a·A_298 − t_298)/(A_298 − t_298), a = 0.47~0.53 → e1 0.36~0.43 · e2 0.36~0.43 · e3 0.36~0.43 · e4 0.36~0.43 · e5 0.36~0.44.
        반증(크기): R 평균이 [0.30, 0.47] 밖.
    Q2  **못 가름(덩어리 유지)**: 대 saIm050e·saIm0583e·sa50nb50e·mslm050e 네 쌍 전부 |SD 형| < 1.5 (298 K 와 같은 자리). base 대비 위(≥ +1.5, saIm025e SD 분모).
        반증: 한 쌍이라도 갈림 / base 조건 미달. (298 K 에서 saIm0583e 쌍이 −0.89(SE −1.99)로 두 식 사이였으므로 323 K 에서도 그 쌍만 "두 식 사이" 가 나올 수 있음 — 그러면 그렇게 적고 정본은 SD 형.)
    Q3  **TSA > VSA 5/5**, **Q 1.0~1.2**(T-RT-1·1B 실측 대역), ΔQ 짝 SD 형 ≤ −1.5.
    반증 조건: T-RT-1 §4 와 같음(Q1 한 짝이라도 ≥ 0 / Q2 위 / Q3 혼재·역전 또는 ΔQ ≥ +1.5).

## 5. 자료 모양·결측 — T-RT-1 §5 그대로.
## 6. 말할 수 없는 것 — T-RT-1 §6 (a)(c)(d)(e)(f) 그대로. (b) 기기 항은 §3 Q1 ⚠ 대로 병기.

## 7. 착수 절차 — 랩탑(Melchior), 8워커
    1) `git pull`(master 에 이 문서와 ASSIGN §AN 이 있음) · `pgrep -x simulate` 0(T-RT-1 완주 확인) · `humid_wc_runs_v3w_323/` 에 saIm025e 폴더 없음 · `git status --porcelain -uno` 비어 있음.
    2) `HWC_323_DRYRUN=1` 로 관문·사전검사·작업 목록 확인 → 착수:
       cd 21_ZIF69_MTV && HWC_323_TARGETS=saIm025e1,saIm025e2,saIm025e3,saIm025e4,saIm025e5 HWC_323_WORKERS=8 HWC_323_RESULT=humid_wc_323_saIm025e_laptop.json HWC_323_MACHINE=laptop \
         setsid nohup ~/miniconda3/envs/czeromof/bin/python run_humid_wc_v3w_323.py > ../.claude_work_wc323_sa025e_laptop.out 2>&1 < /dev/null &
    3) 감시는 일 기반. 머리말 관문은 첫 Output 에서 사람이 한 번. 완주 → JSON 은 postman 이 올림 → 판정은 종합자(§3), 검산 Melchior·Balthasar.
    Windows 업데이트 일시중지는 10-23 까지(랩탑 실측) — 이 배치 안입니다.

## 8. 진행 기록
    [09-19 15:0x] 등록(자료 0건). ASSIGN §AN. T-RT-1 완주(09-18 19:52, 랩탑 7ed03d4)로 착수 조건 충족 — 랩탑이 pull 하는 즉시.
