# T-RT-1c 등록 — **실온도(323 K) 절대 작업 용량, 니트로 앙상블 `nbIm050e1~e5`** (2026-09-19 15:0x, 종합자; **자료 0건**; 사용자 지시 09-19 "C. 등록 문서 신설 … 1C 는 laptop2 가 즉시 착수")

**왜**: 323 K 승자 지표가 T-RT-1(`REALTEMP_VERDICT_20260919.md`, 세 앙상블 + 모체)과 T-RT-1b(술포닐)로 닫혔고 **네 앙상블이 323 K 에서도 한 덩어리**입니다.
298 K 에서 덩어리의 **아래 경계**를 이루는 것이 니트로였는데(WC §8: saIm0583e 아래로만 갈림, 나머지와 못 가름) 323 K 값이 없습니다. 경계가 온도에 따라 움직이는지가 남은 질문입니다.
**REALTEMP_WC_1B_REGISTRATION_20260918.md 를 그대로 물려받고, 대상과 298 K 분모만 바꿉니다**(1B 는 T-RT-1 §1·§3·§5·§6 을 물려받음 — 세 겹 상속, 아래는 다른 점만).
**결과를 본 뒤 자·문턱·예측을 고치지 않습니다.**

## 1. 조건 — 1B §1 과 완전히 같음
    러너 `run_humid_wc_v3w_323.py`, P_H2O 11,114.1 Pa 고정, ads 323 K·0.15 bar / tsa 373 K·0.15 bar / vsa 323 K·0.05 bar. 파일 관문 md5 8e8ec933… 래퍼가 검사.
    HWC_323_TARGETS=nbIm050e2,nbIm050e4,nbIm050e5,nbIm050e1,nbIm050e3  HWC_323_WORKERS=12  HWC_323_RESULT=humid_wc_323_nbIm050e_laptop2.json  HWC_323_MACHINE=laptop2
    CIF `charged_v3/nbIm050e{1..5}_DDEC6.cif`(§AI 와 같은 파일, 관문 통과분). 실행 폴더 `humid_wc_runs_v3w_323/`(laptop2 에는 아직 없음 — 착수 전 확인).
    **기기: laptop2**(물리 6코어 기기, §AI·§AK ⑥ 과 같이 워커 12 — 그 기기의 실측 배분). ASSIGN §AL 의 laptop2 배정 경계("이완·전하·GCMC/WC 만") 안입니다.

## 2. 대상 — 5종 · 15작업, 순서 = 298 K ads 상자 분자 수 내림차순(T-RT-1 §2 규약; 5종이라 순서 효과 작음)
    nbIm050e2 (0.979) · e4 (0.978) · e5 (0.961) · e1 (0.928) · e3 (0.872)   (298 K ads CO₂+물, `humid_working_capacity_w2_nbIm050e_laptop2.json`)
    소요: 1B 실측 15h43m(술포닐, 데스크탑 8워커, 견적 30~40 h 의 절반). 니트로는 298 K 물이 0.07~0.16 으로 술포닐(0.66~1.52)보다 훨씬 적어 더 빠를 것 — **10~18 h**(laptop2 12워커, 6코어 기기라 벽시계는 8워커 기기와 비슷). 첫 ads 완주로 갱신.

## 3. 관측량과 자 — T-RT-1 §3 그대로, 대상만 nbIm050e
    Q1 온도 효과(짝) — d1_k = WC_TSA,323(e_k) − WC_TSA,298(e_k), R_k = 비. 정본 짝 SD 형, SE 형·단위(±)·R 평균 ± SD 병기.
        **298 K 분모(고정)** — 전부 `v3w_humid_wc/humid_working_capacity_w2_nbIm050e_laptop2.json`, laptop2, 열 working_capacity.tsa:
            nbIm050e1 0.6761±0.0125 · e2 0.6713±0.0172 · e3 0.6810±0.0178 · e4 0.7000±0.0146 · e5 0.6758±0.0226
            VSA 분모(working_capacity.vsa): 0.4487 / 0.4473 / 0.4677 / 0.4691 / 0.4489
            흡착 A_298·잔류 t_298(loadings.ads/tsa CO2): e1 0.8261/0.1499 · e2 0.8170/0.1458 · e3 0.8020/0.1210 · e4 0.8438/0.1437 · e5 0.8166/0.1408
        기기: 323 K·298 K **둘 다 laptop2** — 기기 항 없음(1B 와 같은 구도).
    Q2 앙상블 순위(323 K) — nbIm050e 대 saIm050e·saIm0583e·sa50nb50e(T-RT-1, 랩탑)·mslm050e(1B, 데스크탑), SD 형(정본)·SE 형·단위, 문턱 1.5. base(T-RT-1, 랩탑 0.1914) 대 nbIm050e 는 nbIm050e SD 분모.
        기기: 상대가 랩탑·데스크탑 — 기기 항은 §AG(laptop2 대 데스크탑 0.06 단위 → 없음)·T-RT-1 Q4(랩탑 base = T-T1 데스크탑 base, |d| 0.00001) 로 두 쌍이 확인됨. 병기.
        T-RT-1·1B 의 Q2 판정은 이 결과로 바뀌지 않습니다(다른 등록) — **덧붙이는** 방식.
    Q3 TSA 대 VSA(323 K, 짝) — d3_k, 비 Q_k, 298 K 비 Q_298 = 1.507 / 1.501 / 1.456 / 1.492 / 1.505 와의 짝 차 ΔQ_k → 짝 SD 형.
    Q4 없음 — base 는 T-RT-1 Q4 가 맡았음(일치).

## 4. 예측 (자료 0건) — 틀리면 즉시 물린다
    사전 자료: T-RT-1(세 앙상블 R 0.405~0.426 · Q 1.10~1.15) 과 1B(R 0.397 · Q 1.05) 가 **이미 있습니다.** 이 예측은 그 둘 위에 섭니다(등록보다 앞선 자료라 쓸 수 있음).
    Q1  **갈림(음)**: 다섯 짝 전부 d1_k < 0. 크기: R_k ≈ (a·A_298 − t_298)/(A_298 − t_298), a = 0.47~0.53 → e1 0.35~0.43 · e2 0.36~0.43 · e3 0.38~0.45 · e4 0.36~0.43 · e5 0.36~0.43.
        반증(크기): R 평균이 [0.30, 0.47] 밖. (니트로는 물이 적어 T-T1 의 a 가 그대로 들지 안 들지가 관찰거리 — R 이 0.45 쪽으로 붙으면 그렇게 적음.)
    Q2  298 K 값 × R ≈ 0.27, 배치 SD 0.005 안팎(298 K 0.0112 × 0.4) 으로 보면
        대 saIm0583e(0.3341 ± 0.0256) **갈림(−)** · 대 saIm050e(0.3293 ± 0.0371) **경계(−1.0~−2.5)** · 대 sa50nb50e(0.3235 ± 0.0274) **경계(−1.0~−2.5)** · 대 mslm050e(0.2928 ± 0.0525) **못 가름** · base(0.1914) 대비 **위(≥ +1.5)**.
        반증: saIm0583e 와 못 가름 / mslm050e 와 갈림 / base 조건 미달 / 어느 쌍이든 부호 +.
        (자기 한계 예고: 니트로 SD 가 298 K 처럼 작으면 SD 형이 상대 SD 로만 결정돼 "경계" 두 쌍이 갈림·못 가름 어느 쪽으로도 떨어질 수 있음 — 그러면 쌍별로 적음, 정본은 SD 형.)
    Q3  **TSA > VSA 5/5**, **Q 1.0~1.2**(T-RT-1 §4 의 1.2~1.45 는 T-RT-1·1B 에서 두 번 반증됐으므로 그 실측 대역으로), ΔQ 짝 SD 형 ≤ −1.5.
    반증 조건: T-RT-1 §4 와 같음(Q1 한 짝이라도 ≥ 0 / Q3 혼재·역전 또는 ΔQ ≥ +1.5), Q2 는 위.

## 5. 자료 모양·결측 — T-RT-1 §5 그대로(n=5 짝, 결측 k 는 양쪽에서 뺌, Q2 는 같은 k 를 뺌, PARTIAL 은 완주 아님).
## 6. 말할 수 없는 것 — T-RT-1 §6 (a)(c)(d)(e)(f) 그대로. (b) 기기 항은 Q1 에 없고 Q2 에는 §AG·Q4 로 병기.

## 7. 착수 절차 — laptop2(Balthasar), 12워커
    1) `git pull`(master 에 이 문서와 ASSIGN §AM 이 있음) · `pgrep -x simulate` 0 · `humid_wc_runs_v3w_323/` 에 nbIm050e 폴더 없음 · `git status --porcelain -uno` 비어 있음(postman 교착 예방).
    2) `HWC_323_DRYRUN=1` 로 관문·사전검사·작업 목록 확인 → 착수:
       cd 21_ZIF69_MTV && HWC_323_TARGETS=nbIm050e2,nbIm050e4,nbIm050e5,nbIm050e1,nbIm050e3 HWC_323_WORKERS=12 HWC_323_RESULT=humid_wc_323_nbIm050e_laptop2.json HWC_323_MACHINE=laptop2 \
         setsid nohup ~/miniconda3/envs/czeromof/bin/python run_humid_wc_v3w_323.py > ../.claude_work_wc323_nb050e_l2.out 2>&1 < /dev/null &
    3) 감시는 일 기반(`<RESULT>.status.jsonl`·결과 파일). 머리말 관문은 첫 Output 에서 사람이 한 번(Ow-Ow ε 89.633 · Hw/Lw ZERO_POTENTIAL). 착수 직전 대상 CIF 5개의 md5 를 적어 두고 완주 시 대조(Balthasar 제안).
       완주 → JSON 은 postman 이 브랜치로 올리고 데스크탑 배달부가 master 로 반입 → 판정은 종합자(§3), 검산 Melchior·Balthasar. 보고: 착수·완주(해시 병기).

## 8. 진행 기록
    [09-19 15:0x] 등록(자료 0건). ASSIGN §AM. 사용자 지시 "1C 는 laptop2 가 즉시 착수".
