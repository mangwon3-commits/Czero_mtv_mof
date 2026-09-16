# §AI 등록 — **nbIm050e1~e5 습윤 TSA 작업 용량**(298 K 표준 조건, 수정 힘장, 2차 앙상블과 같은 러너) — laptop2 배정 후보 (2026-09-16 18:25, 종합자; **자료 0건**; 30분 규칙 대기)

**왜**: 승자 지표(습윤 TSA WC)의 정직한 문장 "술폰산 단일·혼합(·술포닐 n=1)은 한 덩어리, **니트로**·모체·저술폰산은 아래"(WC §7)에서 니트로는 **n=1**(생산 실현 nbIm050 0.6666, −13.6 단위 대 saIm050 0.9489)이다.
T-SA-2 가 "생산 실현은 앙상블 평균 위" 를 5/5 로 보였으므로 nbIm050 도 그 실현 하나가 앙상블을 대표하지 않을 수 있다. 앙상블 n=5 로 재면 "니트로 아래" 가 ㉨(같은 n)를 지키는 문장이 된다.
laptop2 유휴(§AG 18:21 완주), 등록된 미착수 배정 없음(T-RT-1 등록 §0 검색 기록) → CLAUDE.md §9: 종합자 권고 + 사용자 30분 무응답 시 실행.

## 1. 조건·러너 — 2차 앙상블(§AC)과 완전히 같음
    `run_humid_wc_v3w.py`(298 K·RH90 P_H2O 2,852.1 Pa → 373 K TSA / 298 K·0.05 bar VSA), §1 고정값, 파일 관문 md5 8e8ec933… 선행.
    HWC_V3W_TARGETS=nbIm050e1,nbIm050e2,nbIm050e3,nbIm050e4,nbIm050e5  HWC_V3W_WORKERS=12  HWC_V3W_RESULT=humid_working_capacity_w2_nbIm050e_laptop2.json
    CIF `charged_v3/nbIm050e{1..5}_DDEC6.cif`(09-06 앙상블, 건조 GCMC 완료 `results_v3ens_nb050.json`). 실행 폴더 laptop2 의 `humid_wc_runs_v3w/`(다른 기기 폴더와 별개; nbIm050e 폴더 기존 없음 확인 뒤 착수).
    15작업(5 × ads/tsa/vsa), 워커 12. 물이 적은 계(298 K RH90 물 0.1~0.2 mol/kg)라 saIm 계열보다 싸다 — 소요 범위 8~15 h(298 K 실측 ads 4.6~13.6 h 의 하위, 첫 ads 완주로 갱신).

## 2. 관측량·자 (결과 전 고정) — WC §7 과 같은 자
    WC_TSA(k)·WC_VSA(k) ± (단위). 앙상블 평균 ± SD(배치 단위, 정본 SD 형) · SE 형 · 단위(±) 세 값 병기. 문턱 1.5. 유지 확률 = P(χ²₄ ≥ 4·(1.5/r)²), 척도불변 사전.
    비교(㉨ n=5 끼리): nbIm050e 대 saIm050e(0.8074 ± 0.0960) · saIm0583e(0.8247 ± 0.0566) · sa50nb50e(0.7591 ± 0.0629). 모체 base 0.4892(자유도 0)는 nbIm050e SD 를 분모로.
    T-SA-2 여섯째 점: 생산 실현 nbIm050 0.6666 이 앙상블 평균 위인가(현재 5/5).

## 3. 예측 (자료 0건) — 틀리면 즉시 물린다
    nbIm050e 평균 WC_TSA ≈ 0.58~0.70(생산 실현 0.6666 이 평균 위라는 T-SA-2 대로 그 아래). 세 앙상블 대비 **전부 아래(부호 −)**.
    갈림 여부: saIm0583e·sa50nb50e 대비 SD 형 ≤ −1.5 예측(갈림). saIm050e 대비는 그 앙상블의 SD 가 커서(0.096) SD 형 −1.0~−2.0 경계 — **못 가름이 나와도 예측 실패가 아니라 자의 한계**로 적는다(SE 형·단위 병기).
    base 대비 위(+, nbIm050e SD 분모로 ≥ 1.5). T-SA-2: 평균 위(6/6 → p 0.016).
    반증: 어느 앙상블 대비라도 부호 + / base 대비 못 가름 / T-SA-2 평균 아래.

## 4. 자료 모양(⑩)
    세 쌍 각각 {갈림−, 못 가름, 갈림+}. 이름: 셋 다 갈림− = "니트로 아래(n=5)"; 일부 못 가름 = "니트로는 saIm050e 와 못 가르고 saIm0583e·sa50nb50e 아래" 식으로 쌍별로 적음(순위 없음); 어느 하나 갈림+ = 예측 반증, 문장 철회.
    결측: 상태 'timeout'/'no-output'/'물 순전하 이상'/'다른세션실행중' 은 결측 — 그 k 를 빼고 n 을 적되 n<5 면 ㉨ 로 앙상블 비교는 병기만.
    기기: laptop2 산출(§AG 로 기기 항 없음 확인, 0.06 단위) — 기기 열 병기.

## 5. 이 시험이 말할 수 없는 것
    물 크기(㉦) · 실온도(T-RT-1 별도) · 니트로의 건조 축(이미 n=5, results_v3ens_nb050.json).

## 6. 착수 절차 — laptop2(Balthasar), §AC 2차 패턴 그대로
    1) git pull master → 이 문서 확인. bgstate: RASPA 0. humid_wc_runs_v3w/{ads,tsa,vsa}_nbIm050e* 없음 확인.
    2) 파일 관문(러너가 검) → 착수: HWC_V3W_TARGETS=… HWC_V3W_WORKERS=12 HWC_V3W_RESULT=humid_working_capacity_w2_nbIm050e_laptop2.json setsid nohup python run_humid_wc_v3w.py > ../.claude_work_wc_nb050e_l2.out 2>&1 < /dev/null &
       드라이버 PID = ppid 가 매칭 집합 밖인 행(⑯), 착수 시각 date. 머리말 관문은 첫 Output 에서.
    3) 완주: 결과 JSON 을 master 에 푸시, 해시를 우편함에. 판정문은 쓰지 않음(종합자, §2 자).

## 7. 진행 기록
    [18:25] 등록(자료 0건). 사용자에게 권고(첫 줄) — 30분 무응답이면 실행하고 여기 적는다.
    [18:38] 사용자 승인("do it") → laptop2(Balthasar)에 착수 지시(SendMessage). 30분 규칙 예약 취소.
