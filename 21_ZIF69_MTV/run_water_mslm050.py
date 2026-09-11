"""T-SA-1 부 판정축 — **mslm050e1~e5 의 RH90** (등록 `TSA1_REGISTRATION_20260911.md`).

등록문 §31 이 *"RH90 5종(run_water_v3w **계열**)"* 이라 적었고, `run_water_v3w.py` 의
`TARGETS` 는 **saIm 계열 11종 고정**이라 `--only mslm050e1` 은 *"등록 목록에 없는 이름"* 으로
거부됩니다(그 파일 103~107행). **원본을 고치지 않고** 계열 하나를 더 만듭니다 —
`run_kh_ours.py`·`run_tmtv2w.py` 와 같은 관례입니다.

⚠️ **`V3W_SUFFIX` 는 import 시점에 읽힙니다.** 그래서 import **전에** 넣습니다 —
그러지 않으면 산출물이 `v3w_water/` 본 계열에 섞여 **남의 자료와 한 파일이 됩니다.**

⚠️ **산출 경로가 갈립니다**: `v3w_water_mslm050/` · `water_runs_v3wmslm050/`.
기존 계열과 **합치지 마십시오** — 조성이 다릅니다.

사용:  ~/miniconda3/envs/czeromof/bin/python run_water_mslm050.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('V3W_SUFFIX', '_mslm050')      # ⚠️ import 전에
import run_water_v3w as W                            # noqa: E402

W.TARGETS = [(f'mslm050e{i}', f'SO2CH3 50% 실현 {i}') for i in range(1, 6)]

if __name__ == '__main__':
    # 재료 관문 — 전하 CIF 가 없으면 착수 안 함 (데스크탑이 18:0x~20:0x 에 푸시)
    missing = [n for n, _ in W.TARGETS
               if not os.path.exists(os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'))]
    if missing:
        print(f'!! 전하 CIF 없음: {missing}\n'
              f'   데스크탑이 charged_v3/mslm050e1~5_DDEC6.cif 를 푸시한 뒤에 도십시오.',
              flush=True)
        sys.exit(3)
    print(f'T-SA-1 RH90 — 대상 {[n for n, _ in W.TARGETS]}  계열 {os.environ["V3W_SUFFIX"]}',
          flush=True)
    sys.exit(W.main())
