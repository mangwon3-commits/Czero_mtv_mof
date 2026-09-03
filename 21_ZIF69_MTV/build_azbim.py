#!/usr/bin/env python
"""T-B5 — azbIm(5-아자벤즈이미다졸레이트) 와 bIm(H) 대조군 구조 생성.
DESIGN_STUDY_20260903.md §2-1, §5-B T-B5. 사전 등록 문턱은 그 문서에 있다.

[왜 아릴 빌더를 그대로 못 쓰는가]
    `generate_mtv_cif_zif69_aryl` 은 9원자 이환 고리를 Kabsch 로 정합한 뒤
    **치환기 원자를 붙이는** 경로다. azbIm 은 치환기가 아니라 **고리 원자 교체**
    (Cl 이 붙은 벤조 탄소 CH → N, 부피 증가 0)라 프래그먼트 SMILES
    `c1cnc2[nH]cnc2c1` 은 RING_SMARTS_BICYCLIC(벤조 탄소 4개) 에 매칭되지 않는다.

[어떻게 만드는가 — 생산 빌더를 우회하지 않고 그 위에 얹는다]
    1) 생산 빌더로 **fbIm_aryl(−F)** 을 같은 조성·같은 시드로 만든다.
       → 자리 선택(충돌 회피 포함)·부착 탄소 식별(attachment_index 기하 판정,
         08-14 결함 수정판)이 fbIm 사다리와 **원자 단위로 동일**해진다.
    2) F 마다 결합한 벤조 탄소를 찾아
         azbIm : F 삭제, 그 탄소 C → N            (원자 −1)
         bIm   : F 를 C–F 방향 1.08 Å 의 H 로 교체 (원자 수 불변)
    3) 원소 개수 정확 일치 검사 → audit_orphans → check_substituent_clash →
       최소 원자간 거리. 하나라도 실패하면 파일을 남기지 않는다(relax_series_v3
       가 structures_v2 를 전량 스캔하므로).
    4) rebuild_index.json 에 행을 병합한다(기존 행 규약).

    같은 시드의 azbIm·bIm·fbIm 은 **같은 자리**를 치환한 것이다. 그래서 세 사다리를
    나란히 놓으면 (F 대 N 대 H) 원자 하나의 차이만 남는다.

[태그]  azbIm025 / azbIm050 / azbIm075 / azbIm100, bIm025 / bIm100.
        시드 0 = 무표기, 시드 s≥1 = 접미 e{s}  (ENSEMBLE_0583_PROTOCOL 규약).
        T-B5 의 "실현 5" 는 시드 0 + e1~e4.

[기하 주의]  C→N 교체 뒤 고리 C–N 은 빌더 좌표에서 C–C 길이(≈1.39 Å) 그대로다
        (피리딘 C–N 은 1.34 Å). 그 0.05 Å 는 GFN-FF 이완이 푼다. judge_relax_v3
        의 방향족 C–C 폭 기준은 남은 C–C 에만 걸리므로 영향 없다.

실행:  ~/miniconda3/envs/czeromof/bin/python build_azbim.py --dry-run
       ~/miniconda3/envs/czeromof/bin/python build_azbim.py --run
       (옵션 --kind az|bim|both, --fracs, --seeds)
"""
import argparse
import collections
import json
import os
import sys
import tempfile

import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, '05_MTV_Ligand_Library')
sys.path.insert(0, LIGLIB)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from mtv_cif_builder import generate_mtv_cif_zif69_aryl  # noqa: E402
from audit_orphans import audit  # noqa: E402
from check_substituent_clash import check  # noqa: E402
from rebuild_structures import fix_tags  # noqa: E402

OUT = os.path.join(HERE, 'structures_v2')
INDEX = os.path.join(HERE, 'rebuild_index.json')
BASE_CIF = os.path.join(LIGLIB, 'ZIF69_base.cif')
SITE_MAP = os.path.join(LIGLIB, 'site_map_zif69_bicyclic.json')
N_SITES = 24
BASE_EL = {'C': 240, 'H': 144, 'Cl': 24, 'N': 120, 'O': 48, 'Zn': 24}
CH_LEN = 1.08          # 방향족 C–H
CF_MAX = 1.60          # F 의 결합 탄소 탐색 반경(빌더 C–F ≈ 1.35)
MIN_DIST = 0.9         # 빌더 산출물 최소 거리 하한(relax_criteria 5_최소거리와 동일)

KINDS = {
    'az':  {'prefix': 'azbIm', 'group': 'CH->N (5-aza)', 'lib': 'azbIm(ring N)'},
    'bim': {'prefix': 'bIm',   'group': '-H (Cl 제거 대조)', 'lib': 'bIm(H)'},
}
DEFAULT_FRACS = {'az': [0.25, 0.50, 0.75, 1.0], 'bim': [0.25, 1.0]}


def tag_of(kind, frac, seed):
    t = f'{KINDS[kind]["prefix"]}{int(round(frac * 100)):03d}'
    return t if seed == 0 else f'{t}e{seed}'


def expected_elements(kind, k):
    el = dict(BASE_EL)
    el['Cl'] -= k
    if kind == 'az':
        el['C'] -= k
        el['N'] += k
    else:
        el['H'] += k
    return {s: n for s, n in el.items() if n > 0}


def element_counts(atoms):
    return dict(collections.Counter(atoms.get_chemical_symbols()))


def transform(atoms, kind):
    """fbIm 구조의 F 를 azbIm(C→N) 또는 bIm(F→H) 로. 바꾼 자리 수를 함께 돌려준다."""
    syms = np.array(atoms.get_chemical_symbols())
    f_idx = np.where(syms == 'F')[0]
    i, j, d, D = neighbor_list('ijdD', atoms, CF_MAX)
    partner = {}
    for a, b, dd, DD in zip(i, j, d, D):
        if syms[a] == 'F' and syms[b] == 'C':
            if a not in partner or dd < partner[a][1]:
                partner[a] = (b, dd, DD)     # DD: F→C 최소상 벡터
    if len(partner) != len(f_idx):
        raise RuntimeError(f'F {len(f_idx)}개 중 결합 탄소를 찾은 것 {len(partner)}개')
    new_syms = list(syms)
    pos = atoms.get_positions()
    delete = []
    for f, (c, dd, DD) in partner.items():
        if kind == 'az':
            new_syms[c] = 'N'
            delete.append(f)
        else:
            u = -DD / np.linalg.norm(DD)     # C→F 방향
            pos[f] = pos[c] + CH_LEN * u
            new_syms[f] = 'H'
    atoms = atoms.copy()
    atoms.set_chemical_symbols(new_syms)
    atoms.set_positions(pos)
    if delete:
        del atoms[sorted(delete, reverse=True)]
    return atoms, len(partner)


def min_distance(atoms):
    for cut in (1.3, 2.0, 4.0):
        d = neighbor_list('d', atoms, cut)
        if len(d):
            return float(d.min())
    return float('inf')


def build_one(kind, frac, seed, force=False):
    tag = tag_of(kind, frac, seed)
    out_cif = os.path.join(OUT, f'ZIF69_{tag}.cif')
    if os.path.exists(out_cif) and not force:
        return {'tag': tag, 'skipped': True}
    want = int(round(frac * N_SITES))
    comp = {'clIm_aryl': 1.0 - frac, 'fbIm_aryl': frac}
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, 'fb.cif')
        generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, tmp, seed=seed, conflict_aware=True)
        meta = json.load(open(tmp.replace('.cif', '.meta.json'), encoding='utf-8'))
        fb = read(tmp)
    if meta.get('n_substituted') != want:
        return {'tag': tag, 'built': False, 'reason': f'자리 수 {meta.get("n_substituted")} != {want}'}
    atoms, k = transform(fb, kind)
    if k != want:
        return {'tag': tag, 'built': False, 'reason': f'교체 {k} != {want}'}
    el = element_counts(atoms)
    exp = expected_elements(kind, want)
    if el != exp:
        return {'tag': tag, 'built': False, 'reason': f'원소 불일치 {el} vs {exp}'}

    write(out_cif, atoms)
    fix_tags(out_cif)
    au = audit(out_cif)
    ck = check(out_cif)
    dmin = min_distance(read(out_cif))
    ok = (len(au['orphans']) + len(au['h_orphans']) == 0 and au['detached_atoms'] == 0
          and ck['pass'] and dmin >= MIN_DIST)
    row = {'tag': tag, 'sub': KINDS[kind]['lib'], 'group': KINDS[kind]['group'],
           'frac': frac, 'built': True, 'pass': bool(ok), 'n_atoms': len(atoms),
           'seed': seed, 'orphan': len(au['orphans']), 'detached': au['detached_atoms'],
           'fused_linkers': ck.get('fused'), 'forbidden_contacts': ck.get('forbidden_contacts'),
           'min_pairwise_distance': round(dmin, 4), 'n_substituted': want,
           'conflict_aware': True, 'sites_from': 'fbIm_aryl 동일 시드',
           'chosen_sites': meta.get('chosen_sites'),
           'note': 'T-B5 (DESIGN_STUDY_20260903 §5-B). build_azbim.py: fbIm 빌드 후 '
                   + ('F 삭제 + 부착 C→N' if kind == 'az' else 'F→H 1.08 Å')}
    if not ok:
        os.remove(out_cif)
        row['reason'] = f'감사 실패 orphan={row["orphan"]} detached={row["detached"]} clash={ck["pass"]} dmin={dmin:.3f}'
    else:
        json.dump({'kind': kind, 'seed': seed, 'requested_fraction': frac,
                   'n_substituted': want, 'chosen_sites': meta.get('chosen_sites'),
                   'source_meta': meta},
                  open(out_cif.replace('.cif', '.meta.json'), 'w', encoding='utf-8'),
                  indent=2, ensure_ascii=False)
    return row


def merge_index(rows):
    old = json.load(open(INDEX, encoding='utf-8')) if os.path.exists(INDEX) else []
    by = {r['tag']: i for i, r in enumerate(old)}
    for r in rows:
        if r.get('skipped') or not r.get('built'):
            continue
        if r['tag'] in by:
            old[by[r['tag']]] = r
        else:
            old.append(r)
    json.dump(old, open(INDEX, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return len(old)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--run', action='store_true', help='실제로 만든다(없으면 아무것도 안 함)')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--kind', choices=['az', 'bim', 'both'], default='both')
    ap.add_argument('--fracs', nargs='*', type=float, default=None)
    ap.add_argument('--seeds', nargs='*', type=int, default=[0])
    ap.add_argument('--force', action='store_true', help='기존 CIF 덮어쓰기')
    a = ap.parse_args()

    kinds = ['az', 'bim'] if a.kind == 'both' else [a.kind]
    plan = [(k, f, s) for k in kinds for f in (a.fracs or DEFAULT_FRACS[k]) for s in a.seeds]
    print(f'계획 {len(plan)}건 → {OUT}')
    for k, f, s in plan:
        print(f'  {tag_of(k, f, s):12s} {KINDS[k]["group"]:20s} 자리 {int(round(f * N_SITES)):2d}/24  시드 {s}')
    if a.dry_run or not a.run:
        print('--run 이 없으므로 아무것도 만들지 않았습니다.')
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows = []
    for k, f, s in plan:
        r = build_one(k, f, s, force=a.force)
        rows.append(r)
        if r.get('skipped'):
            print(f'  [{r["tag"]}] 이미 있음 — 건너뜀(--force 로 덮어쓰기)')
        elif not r.get('built'):
            print(f'  [{r["tag"]}] 기각: {r["reason"]}')
        else:
            print(f'  [{r["tag"]}] {"채택" if r["pass"] else "기각"}  원자 {r["n_atoms"]}  '
                  f'dmin {r["min_pairwise_distance"]}  고아 {r["orphan"]}  융합 {r["fused_linkers"]}  '
                  f'금지접촉 {r["forbidden_contacts"]}' + ('' if r['pass'] else f'  ({r["reason"]})'))
    n = merge_index(rows)
    print(f'rebuild_index.json → {n}행')
    bad = [r['tag'] for r in rows if not r.get('skipped') and not (r.get('built') and r.get('pass'))]
    if bad:
        print(f'!! 실패 {len(bad)}건: {" ".join(bad)}')
        return 1
    print('다음: relax_series_v3.py (GFN-FF 셀 고정) → judge_relax_v3.py → Zeo++ (RASPA 와 동시 금지)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
