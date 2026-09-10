#!/usr/bin/env python
"""T-NF 앞단 ② — PACMAN DDEC6 전하 (2026-09-10 신설).

`charge_v3.py` 와 **호출이 같습니다**(`pmcharge.predict(charge_type='DDEC6',
digits=6, atom_type=True, neutral=True, keep_connect=False)` → `fix_tags` →
`net_charge` 5e-5 관문). 다른 것은 **입력 관문**뿐입니다.

    ⚠️ `charge_v3.py` 는 `relax_v3_judged.json` 의 `pass` 만 통과시킵니다.
       그 판정은 ZIF-69 v3 용이고 비-ZIF 골격을 ②③ 로 항상 떨어뜨립니다
       (`REUSE_V3_SCRIPTS_FOR_NONZIF69_20260910.md` §1-1·§1-2·§3).
       그래서 여기서는 그 관문을 쓰지 않고 **`relax_tnf.py` 가 실제로 이완본을
       썼는지**(= xtb 가 0단계로 죽지 않았는지)만 봅니다. 등록문 §1 앞단에
       이완 통과 문턱이 없으므로 새 문턱을 만들지도 않습니다(CLAUDE.md §2).

    ⚠️ 기존 러너는 한 줄도 고치지 않았습니다. `charge_anchor_zif93.py`(08-21) 와
       같은 형태의 **새 얇은 래퍼**입니다.

출력 자리: 기본 `charged_v3/<tag>_DDEC6.cif` (배정 지시 그대로).
`REUSE_...md` §3(나) 는 "다른 계열을 같은 서랍에 넣지 말라" 고 권고합니다 —
실측으로 `charged_v3` 를 glob 하는 러너는 지금 **한 건도 없지만**(전부 태그를
직접 지정), 계열을 가르고 싶으면 `--out-dir charged_tnf` 로 바꾸십시오.

사용:
    python charge_tnf.py --tag zif71 --cif relax_tnf/zif71_relaxed.cif
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from charge_v2 import fix_tags, net_charge, NET_Q_TOL   # noqa: E402

RESULT = os.path.join(HERE, 'charged_tnf.json')


def main(argv=None):
    ap = argparse.ArgumentParser(description='T-NF 앞단 PACMAN DDEC6 전하')
    ap.add_argument('--tag', required=True)
    ap.add_argument('--cif', required=True, help='이완본 (relax_tnf/<tag>_relaxed.cif)')
    ap.add_argument('--out-dir', default=os.path.join(HERE, 'charged_v3'))
    ap.add_argument('--out', default=RESULT)
    a = ap.parse_args(argv)

    src = a.cif if os.path.isabs(a.cif) else os.path.join(HERE, a.cif)
    outdir = a.out_dir if os.path.isabs(a.out_dir) else os.path.join(HERE, a.out_dir)
    if not os.path.exists(src):
        print(f'  [구조없음] {src}  — 이완이 이완본을 쓰지 않았습니다.', flush=True)
        return 2
    os.makedirs(outdir, exist_ok=True)
    final = os.path.join(outdir, a.tag + '_DDEC6.cif')

    if os.path.exists(final):
        q, n = net_charge(final)
        flag = f'  <-- 순전하 {NET_Q_TOL} 초과' if abs(q) > NET_Q_TOL else ''
        print(f'  [이미있음] {a.tag:<10} 원자 {n:<5} 순전하 {q:+.6f}{flag}', flush=True)
        _record(a.out, a.tag, final, q, n, cached=True)
        return 0

    from PACMANCharge import pmcharge      # noqa: E402  (없는 기기에서는 여기서 터집니다)
    work = os.path.join(outdir, a.tag + '.cif')
    shutil.copy(src, work)                 # predict() 는 입력 CIF 를 덮어씁니다
    try:
        pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                         atom_type=True, neutral=True, keep_connect=False)
    except Exception as e:                                  # noqa: BLE001
        print(f'  [전하실패] {a.tag}: {type(e).__name__}: {e}', flush=True)
        os.path.exists(work) and os.remove(work)
        return 1
    pac = work.replace('.cif', '_pacman.cif')
    if not os.path.exists(pac):
        print(f'  [출력없음] {a.tag}', flush=True)
        os.path.exists(work) and os.remove(work)
        return 1
    shutil.move(pac, final)
    t = open(final, encoding='utf-8').read()
    t = re.sub(r'^data_\S+', f'data_{a.tag}_DDEC6', t, count=1, flags=re.M)
    open(final, 'w', encoding='utf-8').write(t)
    fix_tags(final)                        # RASPA 2.0.41 구 태그
    os.path.exists(work) and os.remove(work)

    q, n = net_charge(final)
    flag = f'  <-- 순전하 {NET_Q_TOL} 초과' if abs(q) > NET_Q_TOL else ''
    print(f'  [ok] {a.tag:<10} 원자 {n:<5} 순전하 {q:+.6f}{flag}  -> {final}', flush=True)
    _record(a.out, a.tag, final, q, n, cached=False)
    return 0


def _record(path, tag, final, q, n, cached):
    rows = {}
    if os.path.exists(path):
        try:
            rows = {r['tag']: r for r in json.load(open(path, encoding='utf-8'))}
        except Exception:                                   # noqa: BLE001
            rows = {}
    rows[tag] = {'tag': tag, 'cif': final, 'net_charge': q, 'atoms': n,
                 'cached': cached, 'net_q_tol': NET_Q_TOL,
                 'ok': abs(q) <= NET_Q_TOL,
                 'source': 'relax_tnf (GFN-FF, 셀 고정)',
                 'series': 'T-NF (TNF_REGISTRATION_20260910.md)'}
    json.dump([rows[k] for k in sorted(rows)],
              open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    sys.exit(main())
