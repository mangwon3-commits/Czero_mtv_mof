# -*- coding: utf-8 -*-
"""HKHOME ⑥ — 관문 ⑤ 처리 뒤 ′2 서술 열(모체 · 열린 자리 다섯). 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §7 추가(22:0x · 순찰 2) ⑥ ·
종합자 cloud.md 11-08 11:4x ③. 방법은 −NO₂ ′2(`znbdt_no2_gate5_p2.py` · `results_znbdt_no2_gate5_p2_hkhome.json`)와 같음:
단위셀 접기(`run_e24j_cellrelax.fold` · 복제 사이 편차 · 원소 순서 기록) → Zeo++ `-ha -res` · `-ha -chan 1.65` · `-ha -chan 1.82`.

입력(이 기기에 있는 처리본 — 판마다 이완 상한을 적음):
  판 uff300(주 · 등록이 이름을 댄 것): `uff300_e24i/<tag>_after.cif`(2×2×3 초격자 · `run_e24i_relax.py` OUTER_LOOP_CAP 300) + `<tag>_before.cif`(단위셀) — 여섯 모두.
  판 g5cap12(모체만 · 대조): `lmp_e22/e22_parent/min_e22_parent.data`(E-22b 관문 ⑤ · risk_screen OUTER_LOOP_CAP 12 — −NO₂ ′2 와 같은 상한).
  ※ 다섯 설계의 상한 12 관문 ⑤ 산출물(`results_e24i_gate5_desktop-nvsrr9m.json` 의 작업 폴더)은 이 기기에 없음 — 그래서 다섯은 uff300 판만.
접기 확인: 단위셀 값과 함께 **초격자 그대로**도 `-res` · `-chan` 을 잼(접기가 맞으면 LCD · PLD 가 같아야 함 — 판별자 확인 · 서술).
**RASPA simulate 가 0 일 때만**(CLAUDE §5 · 종합자 11:4x). 산출 results_e24i_gate5_p2_hkhome.json — 값은 기록 · 판정은 종합자.
실행: lammps_mof 파이썬(21_ZIF69_MTV 에서).
"""
import json, os, re, socket, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import run_e24j_cellrelax as CR   # noqa: E402  (fold · md5 · busy · cell_change)
import risk_screen as rs          # noqa: E402
from ase.io import read, write    # noqa: E402

TAGS = ['e22_parent', 'e24i_cn_open', 'e24i_br_open', 'e24i_cl_open', 'e24i_ch3_open', 'e24i_c2h5_open']
WD = os.path.join(HERE, 'e24i_g5p2_runs')
OUT = os.path.join(HERE, f'results_e24i_gate5_p2_{socket.gethostname().lower()}.json')
DRY = bool(os.environ.get('E24I_P2_DRY'))      # 접기만(Zeo++ 안 띄움 · 산출 안 씀)


def zeo(p, stem):
    out = {}
    r = subprocess.run([rs.NETWORK, '-ha', '-res', p + '.res', p], cwd=WD, capture_output=True, text=True, timeout=900)
    v = open(p + '.res').read().split() if os.path.exists(p + '.res') else []
    out['res'] = {'rc': r.returncode, 'LCD': float(v[1]) if len(v) > 2 else None, 'PLD': float(v[2]) if len(v) > 2 else None}
    for rad in (1.65, 1.82):
        cf = os.path.join(WD, f'{stem}_r{rad:.2f}.chan')
        r = subprocess.run([rs.NETWORK, '-ha', '-chan', f'{rad:.2f}', cf, p], cwd=WD, capture_output=True, text=True, timeout=900)
        ctxt = open(cf, errors='ignore').read() if os.path.exists(cf) else ''
        mc = re.search(r'(\d+)\s+channels identified of dimensionality\s*([\d\s]*)', ctxt)
        mo = re.search(r'Identified (\d+) channels and (\d+) pockets', r.stdout + r.stderr)
        out[f'chan{rad:.2f}'] = {'rc': r.returncode, 'n_channels_chanfile': int(mc.group(1)) if mc else None,
                                 'dimensionality': mc.group(2).split() if mc else None,
                                 'channels_stdout': int(mo.group(1)) if mo else None, 'pockets_stdout': int(mo.group(2)) if mo else None,
                                 'chan_file_head': ctxt.strip().splitlines()[:3]}
    return out


def ok_runs(z):
    return all(x['rc'] == 0 for x in z.values()) and z['res']['PLD'] is not None and \
        all(z[f'chan{r_:.2f}']['n_channels_chanfile'] is not None for r_ in (1.65, 1.82))


def one(label, tag, before_p, after, cap, src_p):
    before = read(before_p)
    a1, fl = CR.fold(after, before)
    stem = f'{tag}_{label}'
    pu = os.path.join(WD, f'{stem}_unit.cif'); write(pu, a1); rs.fix_tags(pu)
    ps = os.path.join(WD, f'{stem}_super.cif'); write(ps, after); rs.fix_tags(ps)
    row = {'variant': label, 'outer_loop_cap': cap, 'inputs': {'treated': os.path.relpath(src_p, HERE), 'treated_md5': CR.md5(src_p),
           'before_cif': os.path.relpath(before_p, HERE), 'before_cif_md5': CR.md5(before_p)},
           'fold': fl, 'cell_change_vs_before': CR.cell_change(before.cell, a1.cell),
           'unitcell_cif': os.path.relpath(pu, HERE), 'unitcell_md5': CR.md5(pu), 'supercell_cif': os.path.relpath(ps, HERE)}
    print(f"  {stem:28s} 접기 복제편차 {fl['replica_max_frac_dev_vs_r0']} · 원소순서 {fl['symbol_order_ok']} · n {fl['supercell_n']}", flush=True)
    if DRY:
        return row
    t0 = time.time()
    row['unit'] = zeo(pu, f'{stem}_unit'); row['super'] = zeo(ps, f'{stem}_super')
    row['elapsed_s'] = round(time.time() - t0, 1)
    row['status'] = 'ok' if ok_runs(row['unit']) and ok_runs(row['super']) else 'fail'
    return row


def main():
    if not DRY:
        if CR.busy():
            sys.exit(f'  !! RASPA simulate {CR.busy()}건이 돌고 있음 — Zeo++ 동시 금지(CLAUDE §5) · 착수 안 함')
        if os.path.exists(OUT):
            sys.exit(f'  !! {os.path.basename(OUT)} 이미 있음 — 덮어쓰지 않음')
    os.makedirs(WD, exist_ok=True)
    res = {'test': '관문 ⑤ 처리 뒤 1.65 · 1.82 통로 수(′2 서술 열) — 모체 · 열린 자리 다섯', 'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §7 추가(22:0x) ⑥ · cloud.md 11-08 11:4x ③',
           'method': '−NO₂ ′2 와 같음(znbdt_no2_gate5_p2.py) + 초격자 직접 측정(접기 확인 · 서술)',
           'note_cap': '−NO₂ ′2 는 관문 ⑤ 상한 12 처리본 · 여기 uff300 판은 상한 300 처리본(다섯의 상한 12 산출물은 이 기기에 없음) · 모체는 두 판 모두',
           'machine': socket.gethostname().lower(), 'rows': {}}
    for tag in TAGS:
        ap = os.path.join(HERE, 'uff300_e24i', f'{tag}_after.cif'); bp = os.path.join(HERE, 'uff300_e24i', f'{tag}_before.cif')
        res['rows'][f'{tag}/uff300'] = one('uff300', tag, bp, read(ap), 300, ap)
    dp = os.path.join(HERE, 'lmp_e22', 'e22_parent', 'min_e22_parent.data'); bp = os.path.join(HERE, 'lmp_e22', 'e22_parent', 'e22_parent.cif')
    res['rows']['e22_parent/g5cap12'] = one('g5cap12', 'e22_parent', bp, read(dp, format='lammps-data', atom_style='full'), 12, dp)
    if DRY:
        print('드라이 — 접기만 확인 · 산출 안 씀'); return 0
    ok = all(r.get('status') == 'ok' for r in res['rows'].values())
    res['status'] = 'ok' if ok else 'fail'; res['finished'] = True
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    print(f"⑥ {res['status']} · 행 {len(res['rows'])} — 값은 파일에", flush=True)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
