#!/usr/bin/env python
"""외부(비-ZIF-69) 골격 CIF 감사 — T-NF 앞단 0단계 (2026-09-10 신설).

등록문: `21_ZIF69_MTV/TNF_REGISTRATION_20260910.md`

**이 파일은 아무것도 실행하지 않습니다.** CIF 를 읽어 재고, P1 사본을 쓰고,
등록문 §0 의 슈퍼셀 예외를 계산해 표로 찍을 뿐입니다. RASPA·xtb·PACMAN·Zeo++
를 부르지 않습니다.

[무엇을 재나 — "실패가 결과처럼 보이는 것" 을 앞에서 거르기 위해]
    원소·원자수          xtb/PACMAN 이 모르는 원소가 섞여 있으면 여기서 보인다
    부분점유·무질서      MUF-16 링커 머리-꼬리 무질서, 용매 부분점유
                         (`_atom_site_occupancy` != 1) — GFN-FF 는 이것을 못 읽고
                         겹친 원자를 그대로 최적화한다
    최소 원자간 거리      < 0.9 Å 이면 겹침(무질서 잔재 또는 대칭 전개 중복)
    수소 유무            H 가 없으면 GFN-FF 이완이 무의미하고 DDEC6 도 틀어진다
    게스트 조각          금속에 닿지 않는 연결성분 = 용매/게스트 후보
                         (배위수를 세지 않으므로 **후보**일 뿐, 사람이 봐야 한다)
    수직 폭              등록문 §0 의 복제 규칙 분모. a·b·c 가 아니라 **수직 폭**이다

[수직 폭이 왜 셀 길이가 아닌가]
    RASPA 의 최소상 조건은 축 길이가 아니라 그 축에 수직인 두께에 걸린다.
    w_i = V / |a_j × a_k| 이고, 직교셀에서만 w_i = |a_i| 다. ZIF-69 v3 셀
    (26.084/26.084/19.408, γ=120°)에서 수직 폭은 22.59/22.59/19.41 이라
    2×2×2 가 나온다 — 등록문 §0 이 그 수치를 그대로 적고 있다.

사용:
    python audit_external_cif.py                       # external_cif/ 전부
    python audit_external_cif.py a.cif b.cif           # 지정한 것만
    python audit_external_cif.py --no-write            # P1 사본을 쓰지 않는다
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(HERE, 'external_cif')
RESULT = os.path.join(DEFAULT_DIR, 'audit.json')

# 등록문 §0 — 12 Å 컷오프의 최소상 조건
MIN_WIDTH = 24.0
CUTOFF = 12.0

# 공유결합 반경(Å). relax_criteria.COV 와 같은 값에 T-NF 원소를 더했다.
COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57, 'S': 1.05,
       'Cl': 1.02, 'Br': 1.20, 'Zn': 1.22, 'Co': 1.26, 'Ni': 1.24,
       'Mn': 1.39, 'Cu': 1.32, 'Mg': 1.41, 'Zr': 1.75}
METALS = {'Zn', 'Co', 'Ni', 'Mn', 'Cu', 'Mg', 'Zr', 'Cd', 'Fe', 'Cr', 'Al'}


def perp_widths(cell):
    """축마다 수직 폭 w_i = V / |a_j x a_k|."""
    c = np.asarray(cell, float)
    v = abs(float(np.linalg.det(c)))
    out = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        out.append(v / float(np.linalg.norm(np.cross(c[j], c[k]))))
    return out, v


def unitcells_for(cell):
    """등록문 §0: 축마다 수직 폭 >= 24 Å 이 되는 **최소 정수** 복제."""
    w, _ = perp_widths(cell)
    return [int(np.ceil(MIN_WIDTH / x)) for x in w], w


def raw_cif_flags(path):
    """CIF 원문에서 점유율·무질서·대칭을 본다. ase 는 이것을 조용히 버린다."""
    txt = open(path, encoding='utf-8', errors='replace').read()
    flags = {}
    hm = re.search(r'_symmetry_space_group_name_H-M\s+[\'"]?([^\'"\n]+)', txt)
    if not hm:
        hm = re.search(r'_space_group_name_H-M_alt\s+[\'"]?([^\'"\n]+)', txt)
    flags['space_group_HM'] = hm.group(1).strip() if hm else None
    it = re.search(r'_symmetry_Int_Tables_number\s+(\d+)', txt) or \
        re.search(r'_space_group_IT_number\s+(\d+)', txt)
    flags['IT_number'] = int(it.group(1)) if it else None
    flags['n_symops_listed'] = len(re.findall(
        r"^\s*'?[-+xyz0-9/,. ]+,[-+xyz0-9/,. ]+,[-+xyz0-9/,. ]+'?\s*$", txt, re.M))
    # 점유율 열이 있으면 1 이 아닌 값을 센다
    heads = [l.strip() for l in txt.splitlines() if l.strip().startswith('_atom_site')]
    flags['atom_site_columns'] = heads
    occ_idx = None
    for i, h in enumerate(heads):
        if h.startswith('_atom_site_occupancy'):
            occ_idx = i
    part = any(h.startswith('_atom_site_disorder') for h in heads)
    flags['has_disorder_column'] = part
    frac_occ = []
    if occ_idx is not None:
        started = False
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith('_atom_site'):
                started = True
                continue
            if started:
                p = s.split()
                if len(p) <= occ_idx:
                    if s == '' or s.startswith('loop_') or s.startswith('_'):
                        if frac_occ or p:
                            continue
                    continue
                try:
                    o = float(re.sub(r'\(.*\)', '', p[occ_idx]))
                except ValueError:
                    continue
                if abs(o - 1.0) > 1e-6:
                    frac_occ.append((p[0] if p else '?', o))
    flags['n_partial_occupancy'] = len(frac_occ)
    flags['partial_occupancy_examples'] = frac_occ[:10]
    flags['has_occupancy_column'] = occ_idx is not None
    return flags


def guests(atoms):
    """금속에 연결되지 않은 연결성분 = 게스트/용매 **후보**."""
    from ase.neighborlist import neighbor_list
    syms = atoms.get_chemical_symbols()
    uniq = sorted(set(syms))
    missing = [s for s in uniq if s not in COV]
    if missing:
        return None, missing
    cut = {(a, b): 1.25 * (COV[a] + COV[b]) for a in uniq for b in uniq}
    i, j = neighbor_list('ij', atoms, cut)
    n = len(atoms)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in zip(i, j):
        ra, rb = find(int(a)), find(int(b))
        if ra != rb:
            parent[ra] = rb
    comp = {}
    for x in range(n):
        comp.setdefault(find(x), []).append(x)
    out = []
    for members in comp.values():
        s = [syms[m] for m in members]
        if not any(e in METALS for e in s):
            import collections
            f = ''.join(f'{e}{c}' for e, c in sorted(collections.Counter(s).items()))
            out.append({'n': len(members), 'formula': f})
    agg = {}
    for g in out:
        agg[g['formula']] = agg.get(g['formula'], 0) + 1
    return [{'formula': k, 'count': v} for k, v in sorted(agg.items())], []


def audit(path, write_p1=True):
    from ase.io import read, write as ase_write
    row = {'file': os.path.abspath(path), 'name': os.path.basename(path)}
    row.update(raw_cif_flags(path))

    # pymatgen 으로 P1 전개(대칭 연산이 있으면). ase 도 전개하지만
    # 점유율/중복 처리가 다르므로 둘을 다 재서 어긋나면 눈에 띄게 한다.
    p1_path = None
    try:
        from pymatgen.core import Structure
        st = Structure.from_file(path, primitive=False)
        row['pmg_natoms'] = len(st)
        row['pmg_formula'] = st.composition.formula
        row['pmg_reduced_formula'] = st.composition.reduced_formula
        row['pmg_ordered'] = bool(st.is_ordered)
    except Exception as e:                                   # noqa: BLE001
        row['pmg_error'] = f'{type(e).__name__}: {e}'
        row['pmg_natoms'] = None

    try:
        atoms = read(path)
    except Exception as e:                                   # noqa: BLE001
        row['ase_error'] = f'{type(e).__name__}: {e}'
        return row, None

    import collections
    syms = atoms.get_chemical_symbols()
    cnt = collections.Counter(syms)
    row['ase_natoms'] = len(atoms)
    row['elements'] = dict(sorted(cnt.items()))
    row['has_H'] = 'H' in cnt
    row['unknown_elements_for_COV'] = [s for s in sorted(set(syms)) if s not in COV]

    cell = atoms.get_cell().array
    a, b, c, al, be, ga = atoms.cell.cellpar()
    w, vol = perp_widths(cell)
    row['cell'] = {'a': round(a, 4), 'b': round(b, 4), 'c': round(c, 4),
                   'alpha': round(al, 3), 'beta': round(be, 3),
                   'gamma': round(ga, 3), 'volume': round(vol, 2)}
    row['perp_widths'] = [round(x, 3) for x in w]

    uc, _ = unitcells_for(cell)
    row['tnf_unitcells'] = uc
    row['tnf_perp_widths_after'] = [round(w[i] * uc[i], 2) for i in range(3)]
    row['tnf_supercell_atoms'] = int(len(atoms) * uc[0] * uc[1] * uc[2])
    row['tnf_min_width_ok'] = all(w[i] * uc[i] >= MIN_WIDTH - 1e-9 for i in range(3))
    row['tnf_native_222_ok'] = all(w[i] * 2 >= MIN_WIDTH - 1e-9 for i in range(3))

    # 최소 원자간 거리 (주기경계 포함)
    from ase.neighborlist import neighbor_list
    d = neighbor_list('d', atoms, 3.0)
    row['min_interatomic_dist'] = round(float(d.min()), 4) if len(d) else None
    row['n_pairs_below_0p9'] = int((d < 0.9).sum()) if len(d) else 0

    g, missing = guests(atoms)
    row['guest_candidates'] = g
    if missing:
        row['guest_scan_skipped_missing_COV'] = missing

    if write_p1 and (row.get('IT_number') not in (1, None)
                     or (row.get('space_group_HM') or '').replace(' ', '') not in ('P1', 'P-1', '')):
        p1_path = path.replace('.cif', '_P1.cif')
        try:
            from pymatgen.core import Structure
            st = Structure.from_file(path, primitive=False)
            st.to(filename=p1_path, fmt='cif', symprec=None)
            row['p1_written'] = p1_path
            row['p1_natoms'] = len(st)
        except Exception as e:                               # noqa: BLE001
            row['p1_error'] = f'{type(e).__name__}: {e}'
    else:
        row['p1_written'] = None
        row['p1_note'] = '원본이 이미 P1'
    return row, p1_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cifs', nargs='*')
    ap.add_argument('--no-write', action='store_true')
    ap.add_argument('--out', default=RESULT)
    args = ap.parse_args()

    cifs = args.cifs or sorted(p for p in glob.glob(os.path.join(DEFAULT_DIR, '*.cif'))
                               if not p.endswith('_P1.cif'))
    if not cifs:
        print(f'  CIF 가 없습니다: {DEFAULT_DIR}')
        return 1
    rows = []
    for p in cifs:
        row, _ = audit(p, write_p1=not args.no_write)
        rows.append(row)
        print(f"\n=== {row['name']}")
        if row.get('ase_error'):
            print(f"    !! 읽기 실패: {row['ase_error']}")
            continue
        print(f"    공간군      {row['space_group_HM']} (IT {row['IT_number']})")
        print(f"    원자수      ase {row['ase_natoms']}  pymatgen {row.get('pmg_natoms')}")
        print(f"    조성        {row.get('pmg_reduced_formula')}  {row['elements']}")
        print(f"    셀          {row['cell']}")
        print(f"    수직폭      {row['perp_widths']}")
        print(f"    최소거리    {row['min_interatomic_dist']}  (<0.9 인 쌍 {row['n_pairs_below_0p9']})")
        print(f"    수소        {'있음' if row['has_H'] else '**없음**'}")
        print(f"    부분점유    {row['n_partial_occupancy']} "
              f"(점유율 열 {'있음' if row['has_occupancy_column'] else '없음'}, "
              f"무질서 열 {'있음' if row['has_disorder_column'] else '없음'})")
        if row['n_partial_occupancy']:
            print(f"                예: {row['partial_occupancy_examples'][:5]}")
        print(f"    게스트후보  {row['guest_candidates']}")
        print(f"    T-NF 복제   UnitCells {row['tnf_unitcells']} -> 폭 "
              f"{row['tnf_perp_widths_after']} -> 원자 {row['tnf_supercell_atoms']}")
        print(f"    2x2x2 로도 되나  {'예' if row['tnf_native_222_ok'] else '**아니오**'}")
        if row.get('p1_written'):
            print(f"    P1 사본     {row['p1_written']} ({row.get('p1_natoms')} 원자)")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump({'min_width_A': MIN_WIDTH, 'cutoff_A': CUTOFF, 'rows': rows},
              open(args.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'\n[OK] {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
