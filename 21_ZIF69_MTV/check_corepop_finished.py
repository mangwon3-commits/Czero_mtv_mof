"""§AV 결과 행이 **완주 표지**를 가진 실행에서 나왔는지 사후 검사한다(읽기 전용).

[왜]
    `RESUME_ANY_BUG_20260921.md` 가 두 구멍을 고쳤지만, **돌고 있는 프로세스에는 반영되지
    않습니다**(CLAUDE.md §6). 09-21 14:2x 에 띄운 두 랩탑의 §AV 묶음은 **옛 코드**로 돕니다.
    이어받기 구멍은 두 기기 모두 확인된 대로 안 물렸지만(끊긴 폴더를 지웠거나 `.data` 가 없었음),
    **신규 실행 경로 구멍**(`subprocess check=False` -> 중간값이 `ok`)은 그 묶음이 끝날 때까지
    살아 있습니다. RASPA 가 한 건이라도 중간에 죽으면 표지 없이 `status='ok'` 로 남습니다.

    재기동하면 새 코드가 걸리지만 24 h 를 버립니다. **대신 끝난 뒤(또는 도는 중에) 같은 조건으로
    밖에서 검사합니다** — `run_tnf.py:178` · 고친 `run_aryl_gcmc.finished` 와 같은 조건입니다.

[무엇]
    결과 JSON 의 행마다 실행 폴더 `core_pop_runs/widom_<gas>_<name>/` 의 `.data` 를 열어
    'Simulation finished' 를 확인하고, 모드 필수값(widom -> K_H)이 행에 있는지 본다.
    **아무것도 쓰지 않고 아무것도 안 띄운다** — 도는 배치 위에서 안전하다.

사용:
    python3 check_corepop_finished.py                          # core_pop_results_laptop.json
    python3 check_corepop_finished.py --json core_pop_results_laptop2.json
"""
import argparse
import glob
import json
import os
import sys

MARK = 'Simulation finished'          # run_tnf.py:178 · run_aryl_gcmc.finished 와 같은 조건
RUNS = 'core_pop_runs'


def finished(d):
    """(표지 있음?, 사유). .data 가 없으면 (None, '.data 없음')."""
    ds = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not ds:
        return None, '.data 없음'
    if len(ds) > 1:
        return False, f'.data {len(ds)}개 — 한 폴더에 두 실행'
    try:
        with open(ds[0], errors='ignore') as fh:
            return (MARK in fh.read()), ''
    except OSError as e:                                   # noqa: BLE001
        return False, str(e)[:80]


def main():
    ap = argparse.ArgumentParser(description='§AV 완주 표지 사후 검사(읽기 전용)')
    ap.add_argument('--json', default='core_pop_results_laptop.json')
    ap.add_argument('--runs', default=RUNS)
    a = ap.parse_args()
    if not os.path.exists(a.json):
        print(f'!! 결과 파일 없음: {a.json}')
        return 2
    rows = json.load(open(a.json, encoding='utf-8')).get('rows', [])
    bad, pend, ok = [], [], 0
    for r in rows:
        name = os.path.splitext(r['file'])[0]
        for gas in ('CO2', 'N2'):
            d = os.path.join(a.runs, f'widom_{gas}_{name}')
            if not os.path.isdir(d):
                # 폴더가 지워졌으면 판정 불가 — **통과로 세지 않는다**
                pend.append((name, gas, '폴더 없음(지워짐?)'))
                continue
            fin, why = finished(d)
            if fin is True:
                ok += 1
            elif fin is None:
                pend.append((name, gas, why))
            else:
                bad.append((name, gas, why or '표지 없음'))
        # 행 자체의 필수값 — 옛 run_core_pop 은 실패를 ok 로 남길 수 있었다(RESUME_ANY_BUG §3-2)
        if r.get('status') == 'ok' and (r.get('KH_CO2') is None or r.get('KH_N2') is None):
            bad.append((name, '행', "status=ok 인데 K_H 가 비었습니다"))
    print(f'  행 {len(rows)} · 표지 확인 {ok} · 판정 불가 {len(pend)} · **불통과 {len(bad)}**')
    for n, g, w in bad:
        print(f'    !! {n:38} {g:4} {w}')
    for n, g, w in pend[:20]:
        print(f'    .. {n:38} {g:4} {w}')
    if len(pend) > 20:
        print(f'    .. (판정 불가 {len(pend) - 20}건 더)')
    if bad:
        print('  !! 불통과 행은 그 구조를 다시 도십시오(새 코드로 재기동하면 자동으로 다시 돕니다).')
    elif not pend:
        print('  전부 완주 표지 확인 — 신규 실행 경로 구멍에 물린 행 없음.')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
