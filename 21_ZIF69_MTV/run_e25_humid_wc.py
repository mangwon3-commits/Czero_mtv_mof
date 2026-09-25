# -*- coding: utf-8 -*-
"""E-25 — 형판 Zn(bib)(bdtdc)(우리 앞단) 습윤 TSA 작업 용량. 등록 ASSIGN_MAGI5B §laptop 7차(a688385b). laptop(Melchior).

`run_humid_wc_v3w.py`(→ run_humid_wc.run_one)를 **수정 없이** import 하고, 바꾸는 것은 **작업 착수 시각 하나**뿐:
  run_humid_wc.main 은 ProcessPoolExecutor.map 으로 9작업 중 8개를 **같은 순간에** 띄운다. RASPA 씨앗 = 착수 시각(초)이고
  (이 기기 실측: E-21 seed 1790314458 = 14:34:18 · E-22g 1790333265 = 19:47:45), 대상 셋 e22_parent_h{1,2,3} 은
  **바이트 동일 사본**(md5 f15ce100)이라 같은 초에 뜨면 ads_h1 · ads_h2 · ads_h3 가 **같은 씨앗·같은 입력 = 같은 출력** — 씨앗 반복 3 이 1 이 된다.
  그래서 작업 i 는 **착수 기준 시각 T0 + i × STAGGER** 이전에는 시작하지 않는다(i ≥ 워커여도 — 빈 워커가 일찍 나도 T0 + i×15 까지 기다림).
  입력 파일·사이클·힘장·조건·결과 파일은 러너 그대로(§1 고정값). 결과 = v3w_humid_wc/$HWC_V3W_RESULT.
E25_DRY=1: RASPA 대신 대역(착수 시각만 찍음) · 결과는 스크래치로 — 간격이 실제로 먹는지 먼저 본다.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ff_gate                    # noqa: E402
import run_humid_wc_v3w as V      # noqa: E402  env(HWC_V3W_*)로 hw 전역을 정함
hw = V.hw

STAGGER = float(os.environ.get('E25_STAGGER', '15'))
JOBS = [(t, lab, p, T, ps) for t in hw.TARGETS for lab, p, T, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
T0 = time.time()                  # fork 로 워커에 물려짐
_orig = hw.run_one


# 반환코드 기록(종합자 판정 전 관문 — 러너는 check=False 로 버림): hw 가 쓰는 subprocess.run 을 감싸 cwd 가 있는 호출(= RASPA)의
# returncode 를 실행 폴더의 e25_returncode.txt 에 남긴다. 시간초과(예외)면 파일이 안 생김 → 감사에서 '없음' = 실패.
_real_run = hw.subprocess.run


def _run_rec(args, *a, **k):
    cp = _real_run(args, *a, **k)
    if k.get('cwd'):
        with open(os.path.join(k['cwd'], 'e25_returncode.txt'), 'w') as f:
            f.write(f'{cp.returncode}\n')
    return cp


hw.subprocess.run = _run_rec


def _dry(job):
    d = os.path.join(os.environ['E25_DRY_DIR'], f'{job[1]}_{job[0]}'); os.makedirs(d, exist_ok=True)
    hw.subprocess.run(['bash', '-c', 'exit 0' if job[1] != 'vsa' else 'exit 7'], cwd=d)   # 반환코드 기록 길 시험(vsa 는 7)
    return job[0], job[1], None, 'dry@' + time.strftime('%H:%M:%S')


def staggered(job):
    i = JOBS.index(job)
    wait = T0 + i * STAGGER - time.time()
    if wait > 0:
        time.sleep(wait)
    return (_dry if os.environ.get('E25_DRY') else _orig)(job)


hw.run_one = staggered

if __name__ == '__main__':
    ok, md5 = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {md5} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    if os.environ.get('E25_DRY'):
        hw.RESULT = os.environ['E25_DRY_RESULT']
    print(f'E-25 습윤 작업 용량(형판) — 착수 간격 {STAGGER:.0f} s · 작업 {len(JOBS)}', flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:12s} {getattr(hw, k)}', flush=True)
    missing = [t for t in hw.TARGETS if not os.path.exists(os.path.join(hw.CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print(f'  !! charged_v3 에 없음: {missing}', flush=True)
        sys.exit(1)
    sys.exit(hw.main())
