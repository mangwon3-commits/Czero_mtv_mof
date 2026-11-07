# -*- coding: utf-8 -*-
"""#5′ 이완본 (0a)(0b) — **슈퍼셀 전체에서** 다시 잼(접지 않음). HKHOME 11-07 21:5x. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §5-3.
왜: `run_e24j_cellrelax.py` 는 LAMMPS 슈퍼셀(2×2×3)의 복제 0 을 단위셀로 접어 쟀습니다. −NO₂ 관문 ⑤ 산출물에서는 12 복제가 똑같아
    접기가 정확했지만, e24j_cl_ovl 에서는 자기 표지가 걸렸습니다(복제 편차 0.36 · `sub_count_match` False).
    원인 확인(값은 안 봄): 이완 **전** 입력 슈퍼셀은 복제가 완전히 같고, 이완 **뒤** a · b 복제는 그대로 같으나
    **c 방향 복제 셋이 서로 다르게 이완**됐습니다(대칭 깨짐). 그래서 복제 하나는 구조를 대표하지 못합니다.
그래서: LAMMPS 가 낸 슈퍼셀을 **그대로** 잽니다. 빌드본 · 모체 기준 원자는 같은 배수로 반복한 뒤 이완 셀로 분수좌표 그대로 옮깁니다
    (셀 변형 몫 제외 — 앞 실행기와 같은 규약). 원점의 강체 이동(복제 0 의 중앙값)만 뺍니다. 측정 함수는 앞 실행기의 `measure` 그대로입니다
    (= laptop2 `e24j_measure.py` · `clash_gate.check`; 고정셀 재현 일치 확인됨). 축마다 복제 대칭 편차를 서술 열로 남깁니다.
Zeo++ · LAMMPS 를 띄우지 않습니다(이미 있는 `lmp_e24j_cr/<tag>/min_<tag>.data` 를 읽기만 함) → RASPA 와 함께 돌아도 됩니다.
앞 실행기의 `results_e24j_screen_cellrelax_hkhome.json` 은 고치지 않고 둡니다(복제 0 측정 · 자기 표지 있음). 이 파일이 그것을 갈음합니다.
(0b) 는 두 판을 나란히 냅니다(11-07 21:5x · **값 보기 전에** 정함): 표준 판 `gate0b`(clash_gate.check · 모체 0.8 Å 재짝짓기) ·
    이어받기 판 `gate0b_carry`(골격/치환기 구분 · 무리 · 부착 C · 제외 위상을 이완 전 입력에서 원자 번호로 이어받음). 셀 이완에서 골격 원자가
    0.8 Å 넘게 움직이면 표준 판은 그 원자를 치환기로 다시 분류합니다(`sub_count_match` False). HKHOME 권고는 이어받기 판을 주 판으로 —
    원자의 정체는 움직여도 안 바뀌기 때문. 이어받기 판은 고정셀 입력에서 표준 판과 같은 답을 내는지 먼저 확인합니다. 정하는 것은 종합자.
산출: results_e24j_screen_cellrelax_super_hkhome.json — 판정은 종합자. 실행: lammps_mof 파이썬(21_ZIF69_MTV 에서)."""
import json, os, socket, sys, time, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import run_e24j_cellrelax as CR   # noqa: E402  (measure · md5 · cell_change · JOBS · 폴더)
import clash_gate                 # noqa: E402
from ase.io import read, write    # noqa: E402

HOST = socket.gethostname().lower()
OUT = os.path.join(HERE, f'results_e24j_screen_cellrelax_super_{HOST}.json')


def replica_map(after, before, n):
    """블록 k → 이미지(정수 3개). 블록 순서 = LAMMPS 복제 순서(원소 순서로 확인)."""
    N = len(before); fa = after.get_scaled_positions(wrap=False) * n; fb = before.get_scaled_positions(); m, R = {}, {}
    for k in range(len(after) // N):
        d = fa[k * N:(k + 1) * N] - fb; img = np.rint(np.median(d, axis=0)).astype(int); r = d - img; r -= np.rint(r)
        m[tuple(int(x) % int(nn) for x, nn in zip(img, n))] = k; R[k] = r
    return m, R


def axis_symmetry(after, before, n):
    """축마다 '그 축으로 한 칸 옮긴 복제' 대 복제 0 의 최대 편차(Å) · 0.5 Å 넘는 원자 수."""
    N = len(before); m, R = replica_map(after, before, n); cell1 = np.array(after.cell) / n[:, None]; out = {}
    for ax, name in enumerate('abc'):
        if n[ax] < 2: out[name] = None; continue
        img = [0, 0, 0]; devs = []
        for step in range(1, int(n[ax])):
            img[ax] = step; k = m[tuple(img)]
            dv = R[k] - R[0]; dv -= np.rint(dv); nd = np.linalg.norm(dv @ cell1, axis=1); devs.append(nd)
        nd = np.max(devs, axis=0)
        out[name] = {'max_dev_A': round(float(nd.max()), 4), 'n_atoms_dev_gt_0.5A': int((nd > 0.5).sum()), 'n_atoms_per_cell': N}
    return out, R[0]


def fw_match(a, par):
    """clash_gate.check 의 골격 짝짓기 그대로(대상 원자 → 모체 원자, 0.8 Å · 같은 원소)."""
    from ase.geometry import find_mic
    P = par.get_positions(); ps = par.get_chemical_symbols(); s = a.get_chemical_symbols(); X = a.get_positions(); fw = {}
    for k in range(len(a)):
        _, dl = find_mic(P - X[k], a.cell, pbc=True)
        cand = [q for q in np.argsort(dl)[:6] if dl[q] < 0.8 and ps[q] == s[k] and q not in fw.values()]
        if cand: fw[k] = int(cand[0])
    return fw


def gate0b_carry(a1, aIn, fw_unit, Nunit):
    """(0b) 이어받기 판(11-07 21:5x · 값 보기 전에 정함). 정의는 clash_gate.check 그대로(Bondi · 겹침 ≥ 0.4 Å · H 짝 안 봄 ·
    같은 무리 · 부착 C 에서 2결합 안 제외)이되, **골격/치환기 구분 · 치환기 무리 · 부착 C · 제외 위상을 이완 전 입력(같은 원자 순서)에서 이어받음.**
    이유: 셀 이완에서 골격 원자가 모체 자리에서 0.8 Å 넘게 움직이면 표준 판은 그 원자를 치환기로 다시 분류합니다(−Cl 에서 무거운 원자 11 개).
    원자의 정체는 움직여도 바뀌지 않으므로 거리는 이완본에서, 정체는 입력에서 잽니다. 위상은 입력 그래프의 골격–골격 결합만 씀(X–O 거짓 결합 배제)."""
    from ase.geometry import find_mic
    B, OV = clash_gate.BONDI, clash_gate.OVERLAP
    s = a1.get_chemical_symbols(); X1 = a1.get_positions(); XI = aIn.get_positions()
    fw = {j for j in range(len(a1)) if (j % Nunit) in fw_unit}
    sub = [j for j in range(len(a1)) if j not in fw]
    GI = clash_gate.graph(aIn); Gfw = {u: {v for v in GI[u] if v in fw} for u in fw}
    groups, seen = [], set()
    for k in sub:
        if k in seen: continue
        g, stack = set(), [k]
        while stack:
            u = stack.pop()
            if u in g: continue
            g.add(u); _, dl = find_mic(XI[sub] - XI[u], aIn.cell, pbc=True)
            stack += [sub[q] for q in range(len(sub)) if dl[q] < 1.75 and sub[q] not in g]
        seen |= g; groups.append(g)
    fwC = sorted(k for k in fw if s[k] == 'C'); worst, clashes, n_noatt = (9.9, None), 0, 0
    for g in groups:
        heavy = [u for u in g if s[u] != 'H']
        if not heavy: continue
        att = None
        for u in heavy:
            _, dl = find_mic(XI[fwC] - XI[u], aIn.cell, pbc=True); q = int(np.argmin(dl))
            if dl[q] < 2.1: att = fwC[q]; break
        excl = ({att} | Gfw[att] | {w for v in Gfw[att] for w in Gfw[v]}) if att is not None else set()
        n_noatt += att is None
        cand = [k for k in range(len(a1)) if k not in g and k not in excl and s[k] != 'H' and s[k] in B]
        for u in heavy:
            _, dl = find_mic(X1[cand] - X1[u], a1.cell, pbc=True)
            for q, d in zip(cand, dl):
                if d > 4.0: continue
                margin = d - (B[s[u]] + B[s[q]])
                if margin < worst[0]: worst = (round(float(margin), 3), f'{s[u]}{u}···{s[q]}{q} {d:.3f}')
                if -margin >= OV: clashes += 1
    return {'n_sub_atoms': len(sub), 'n_groups': len(groups), 'n_groups_without_attach_C': n_noatt, 'min_margin_A': worst[0],
            'worst_pair': worst[1], 'n_clash_pairs': clashes, 'pass_0b': clashes == 0}


def main():
    if os.path.exists(OUT):
        sys.exit(f'  !! {os.path.basename(OUT)} 이미 있음 — 덮어쓰지 않음')
    par = read(clash_gate.PARENT); t0 = time.time()
    res = {'test': '#5′ — 셀 이완본의 관문 (0a)(0b), LAMMPS 슈퍼셀 전체에서(접지 않음)', 'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §5-3',
           'supersedes': 'results_e24j_screen_cellrelax_hkhome.json(복제 0 을 단위셀로 접어 잼 — c 방향 복제 대칭이 깨져 대표 못 함)',
           'relax_record': 'results_e24j_cellrelax_hkhome.json', 'code': 'e24j_cellrelax_measure_super.py · measure = run_e24j_cellrelax.measure(= e24j_measure.py · clash_gate.check)',
           'frame_note': '빌드본 · 모체 기준 원자 = 슈퍼셀 배수로 반복 → 이완 셀로 분수좌표 그대로(셀 변형 몫 제외). 원점 강체 이동(복제 0 중앙값)만 뺌.',
           'machine': HOST, 'rows': {}, 'note': '판정은 종합자.'}
    for tag, (B0p, B1p, X) in CR.JOBS.items():
        d = os.path.join(CR.rs.WORK, tag); dat = os.path.join(d, f'min_{tag}.data')
        if not os.path.exists(dat):
            res['rows'][tag] = {'status': 'no_relaxed_data'}; print(tag, '이완 산출물 없음', flush=True); continue
        b0_path = os.path.join(CR.STAGE, 'src', B0p.replace('/', '__')); b1_path = os.path.join(CR.STAGE, 'src', B1p.replace('/', '__'))
        a0, aR = read(b0_path), read(b1_path)
        after = read(dat, format='lammps-data', atom_style='full')
        N = len(aR); rep = len(after) // N; n = np.rint(after.cell.lengths() / aR.cell.lengths()).astype(int)
        assert int(n.prod()) == rep and rep * N == len(after)
        order_ok = after.get_chemical_symbols() == list(aR.get_chemical_symbols()) * rep
        sym, r0 = axis_symmetry(after, aR, n)
        shift = np.median(r0, axis=0)                       # 단위셀 분수좌표 단위
        a1 = after.copy(); a1.set_chemical_symbols(list(aR.get_chemical_symbols()) * rep)
        a1.set_scaled_positions((after.get_scaled_positions(wrap=False) - shift / n) % 1.0)
        p1 = os.path.join(CR.OUTD, f'{tag}_cellrelaxed_super.cif'); write(p1, a1); a1r = read(p1)
        m = CR.measure(tag, a0.repeat(tuple(int(x) for x in n)), a1r, p1, X, par.repeat(tuple(int(x) for x in n)))
        g_fix = clash_gate.check(b1_path)                   # 고정셀 입력의 치환기 원자 수(짝짓기 확인 기준)
        m['sub_count_fixedcell_x_rep'] = g_fix['n_sub_atoms'] * rep
        m['sub_count_match'] = (m['gate0b']['n_sub_atoms'] == g_fix['n_sub_atoms'] * rep)
        m.pop('contacts', None)
        # (0b) 이어받기 판 — 먼저 고정셀 입력에서 표준 판(clash_gate.check)과 같은 답을 내는지 확인
        fw_unit = set(fw_match(aR, par).keys())
        chk = gate0b_carry(aR, aR, fw_unit, N)
        carry_check = {k: (chk[k], g_fix[k]) for k in ('n_sub_atoms', 'min_margin_A', 'n_clash_pairs', 'pass_0b')}
        carry_check['match'] = all(a == b for a, b in carry_check.values())
        aIn = read(os.path.join(d, f'data.{tag}'), format='lammps-data', atom_style='full')
        aIn.set_chemical_symbols(list(aR.get_chemical_symbols()) * rep)
        carry = gate0b_carry(a1r, aIn, fw_unit, N)
        m['gate0b_carry'] = carry; m['gate0b_carry_fixedcell_check'] = carry_check
        m['gate_all_pass_carry'] = m['gate0a_pass'] and carry['pass_0b']
        print(f"{tag}: (0b) 이어받기 판 — 고정셀 표준 판과 {'일치' if carry_check['match'] else '불일치!'}", flush=True)
        row = {'status': 'ok', 'substituent': X, 'supercell_n': n.tolist(), 'rep': rep, 'symbol_order_ok': bool(order_ok),
               'replica_symmetry_by_axis': sym, 'rigid_shift_unitfrac_removed': np.round(shift, 5).tolist(),
               'relaxed_data': os.path.relpath(dat, HERE), 'relaxed_data_md5': CR.md5(dat),
               'super_cif': os.path.relpath(p1, HERE), 'super_cif_md5': CR.md5(p1),
               'cell_change_per_unitcell': CR.cell_change(aR.cell, after.cell.__class__(np.array(after.cell) / n[:, None])),
               'final_EDiff_outer_loops': CR.rs.final_ediff(tag), 'super': m}
        res['rows'][tag] = row
        print(f"{tag}: 슈퍼셀 측정 ok · 원소순서 {order_ok} · 짝짓기 {m['sub_count_match']} · 축별 복제편차(Å) "
              f"{ {k: (v['max_dev_A'] if v else None) for k, v in sym.items()} } — 값은 파일에", flush=True)
    res['elapsed_s'] = round(time.time() - t0, 1); res['finished'] = True
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    ok = all(r.get('status') == 'ok' and r['symbol_order_ok'] and r['super']['gate0b_carry_fixedcell_check']['match'] for r in res['rows'].values())
    print('끝', 'ok' if ok else '!! 표지 확인 필요', flush=True)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
