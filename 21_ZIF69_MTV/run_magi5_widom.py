#!/usr/bin/env python
"""MAGI-005 E-3 — 외부 골격(예: MAF-66)의 Widom CO2/N2 (298 K) **골격 전하 ON/OFF** 얇은 드라이버 (2026-09-25).

`run_aryl_gcmc.run_one` 을 그대로 재사용한다(프로토콜 = CLAUDE.md §1 / §AV: 초기화 3,000 + 15,000, UFF_MOF, 12 Å, Ewald 1e-6, unit_cells()).
OFF 는 러너를 고치지 않고 **CIF 의 _atom_site_charge 를 전부 0 으로 쓴 사본**을 넣는다 — 골격 전하 0, 흡착질 전하·Ewald 유지
(밀도맵 q_off 의 `UseChargesFromCIFFile no` 와 물리적으로 같은 자: 골격–흡착질 정전기 0).
결과 JSON: results_magi5_e3_<tag>_widom_<host>.json  (RESULT_PATTERNS 안).
사용:  python run_magi5_widom.py --cif charged_v3/maf66_DDEC6.cif --tag maf66 [--workers 4] [--temp 298]
"""
import argparse, json, os, re, socket, sys, time
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

def zero_charge_copy(cif, out):
    txt = open(cif, encoding='utf-8').read().splitlines()
    # find atom_site loop header order
    hdr = [l.strip() for l in txt if l.strip().startswith('_atom_site_')]
    if '_atom_site_charge' not in hdr:
        raise SystemExit('CIF 에 _atom_site_charge 열이 없습니다: ' + cif)
    idx = hdr.index('_atom_site_charge')
    out_lines, in_loop, n = [], False, 0
    for l in txt:
        s = l.strip()
        if s.startswith('_atom_site_'): in_loop = True; out_lines.append(l); continue
        if in_loop and s and not s.startswith('_') and not s.startswith('loop_') and len(s.split()) >= len(hdr):
            parts = l.split(); parts[idx] = '0.000000'; out_lines.append(' '.join(parts)); n += 1; continue
        if in_loop and (s.startswith('loop_') or s == ''):
            in_loop = False
        out_lines.append(l)
    open(out, 'w', encoding='utf-8').write('\n'.join(out_lines) + '\n')
    return n

def _one(args):
    cif, gas, temp, runs = args[:4]
    # 씨앗 간격(2026-09-25 laptop 지적): 동시 착수는 초 단위 씨앗이 겹침 → 작업 순번 × 15 s
    if len(args) > 4: time.sleep(15 * int(args[4]))
    rg.TEMP = float(temp); rg.RUNS = runs
    name, g, mode, res, st = rg.run_one((cif, gas, 'widom'))
    return name, g, res, st

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cif', required=True); ap.add_argument('--tag', required=True)
    ap.add_argument('--temp', type=float, default=298.0); ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--gases', default='CO2,N2'); ap.add_argument('--charges', default='on,off')
    a = ap.parse_args()
    ok, msg = ff_gate.md5_gate(); print(f'  [파일 관문] {msg}', flush=True)
    if not ok: print('  !! 힘장 파일 관문 실패 — 아무것도 돌리지 않습니다.'); return 3
    runs = os.path.join(HERE, f'magi5_runs_{a.tag}'); os.makedirs(runs, exist_ok=True)
    cifs = {}
    if 'on' in a.charges: cifs['on'] = os.path.abspath(a.cif)
    if 'off' in a.charges:
        q0 = os.path.join(runs, os.path.basename(a.cif).replace('.cif', '_q0.cif'))
        n = zero_charge_copy(a.cif, q0); print(f'  전하 OFF 사본: {q0} ({n} 원자 전하 0)', flush=True); cifs['off'] = q0
    jobs = [(c, g, a.temp, runs, k) for k, (c, g) in enumerate((c, g) for ch, c in cifs.items() for g in a.gases.split(','))]
    print(f'  Widom {len(jobs)}작업 (tag {a.tag}, {a.temp} K, 워커 {a.workers}) — 착수 {time.strftime("%F %T")}', flush=True)
    host = socket.gethostname().lower()
    out = os.path.join(HERE, f'results_magi5_e3_{a.tag}_widom_{host}.json')
    rows = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for name, g, res, st in ex.map(_one, jobs):
            ch = 'off' if name.endswith('_q0') else 'on'
            r = rows.setdefault(ch, {'name': name, 'charges': ch, 'temp_K': a.temp})
            if res:
                r[f'KH_{g}'], r[f'KH_{g}_err'] = res[0], res[1]
                if len(res) > 3: r[f'dU_{g}'], r[f'dU_{g}_err'] = res[2], res[3]
            r[f'status_{g}'] = st
            print(f'    {name} {g}: {st}  {res}', flush=True)
    for ch, r in rows.items():
        if r.get('KH_CO2') and r.get('KH_N2'):
            r['selectivity'] = r['KH_CO2'] / r['KH_N2']
            r['selectivity_err'] = r['selectivity'] * ((r['KH_CO2_err']/r['KH_CO2'])**2 + (r['KH_N2_err']/r['KH_N2'])**2) ** 0.5
        if r.get('dU_CO2') is not None: r['Qst_CO2_rt_corrected'] = -r['dU_CO2'] + rg.R_GAS * a.temp   # 정정 2026-09-25 (laptop): R_GAS 는 kJ 단위, /1000 제거 — -r['dU_CO2'] + 8.314462618e-3 * a.temp
    meta = {'tag': a.tag, 'cif': a.cif, 'protocol': 'run_aryl_gcmc.run_one widom (CLAUDE.md §1)', 'off_method': 'CIF _atom_site_charge = 0 사본 (골격 전하 0, 흡착질 전하·Ewald 유지)',
            'ff_md5': ff_gate.FF_MD5, 'host': host, 'elapsed_s': round(time.time() - t0), 'finished': time.strftime('%F %T'), 'rows': list(rows.values())}
    json.dump(meta, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  저장 {out}  ({meta["elapsed_s"]} s)', flush=True)

if __name__ == '__main__':
    sys.exit(main())
