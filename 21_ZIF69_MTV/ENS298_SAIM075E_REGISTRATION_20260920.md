# 298 K 습윤 WC 앙상블 — `saIm075e1~e5` (랩탑) — 등록 (2026-09-20 00:07, 데스크탑 세션; **자료 0건** — saIm075e 298 K 습윤 WC 실현 0건; 사용자 승인 2026-09-20 "do it")

## 1. 왜
술폰산 사다리의 298 K 앙상블은 25/50/58 % 까지다(WC §7~§10). 75 % 는 **모체 saIm075(seed=0)가 관문 탈락**(risk_results_v3 pass False — 공극)이라 사다리에서 빠졌지만,
실현 e1~e5 는 관문 통과(risk_results_v3ens075 5/5, relax_v3_judged pass 5/5). 사다리 꼭대기가 덩어리에 남는지, 물이 너무 붙어 떨어지는지가 처음 읽힌다.
**이 결과를 saIm075 모체 단독 값처럼 인용하지 않는다** — 모체는 관문 밖이다.

## 2. 조건 — §AK(saIm025e) 와 완전히 같음
    `run_humid_wc_v3w.py`, CLAUDE.md §1 고정값, 파일 관문 md5 8e8ec933 선행.
    HWC_V3W_TARGETS=saIm075e1,…,e5  HWC_V3W_WORKERS=8  HWC_V3W_RESULT=humid_working_capacity_w2_saIm075e_laptop.json  (15작업, 두 물결 8+7)
    소요 물이 많은 계(saIm0583e RH90 물 0.7~1.9 보다 더) → **14~22 h**. 09-20 06:00 착수 → 09-20 20:00 ~ 09-21 04:00. 윈도우 업데이트 일시중지 10-23 까지(랩탑 실측) 안.
    전하 CIF `charged_v3/saIm075e{1..5}_DDEC6.cif` 는 사슬이 착수 전 5/5 확인(없으면 멈추고 보고 — 데스크탑이 PACMAN 으로 만들어 푸시).
## 3. 판정 (결과 전 고정 — RULER §7 두 식 병기, 문턱 1.5)
    예측   saIm0583e(0.8247) 와 **못 가름이거나 아래(부호 −)** — 사다리는 58 % 에서 정체·감소. base 위. RH90 물 로딩은 saIm0583e 보다 큼(단조).
    반증   saIm0583e 위로 갈림(≥ +1.5 배치 단위) — 그러면 사다리가 계속 오르는 것이고 "58 % 최적" 서술을 물린다.
    결측·자 규칙은 ENS298_MSLM025E 등록 §3 과 같음.
## 4. 절차 (랩탑, Melchior)
    사슬 `.claude_work_wc298_laptop_chain.sh`: 1D 드라이버·simulate 0 이 3분 연속 → 전하 CIF 5/5 → 착수. 로그 `wc298_laptop_chain.log`.
    기동(지금, 1D 가 도는 채로): cd ~/mof_project && git merge origin/master && setsid nohup bash .claude_work_wc298_laptop_chain.sh > .claude_work_wc298_laptop.out 2>&1 < /dev/null &
## 5. 진행 기록
    [2026-09-20 00:07] 등록(자료 0건). ASSIGN §AU.
