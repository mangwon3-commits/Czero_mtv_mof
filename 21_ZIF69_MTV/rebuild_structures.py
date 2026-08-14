"""충돌 없는 ZIF-69 치환 구조를 다시 만든다.

[왜 다시 만드는가 — STRUCTURE_DEFECT.md]
    2026-08-14, 기존 structures/*.cif 의 치환기가 서로 관통해 있는 것을 발견했다.
    saIm100 에서 O–O 0.924 Å, S–S 2.642 Å. 33개 중 24개가 결함이었고
    −SO₃H 는 25% 에서도 결함이었다.

    원인은 둘이다.
      (1) 자리를 rng.choice 로 골라, 동시에 치환기를 달 수 없는 자리쌍을 골랐다
      (2) 회전 최적화가 **순차적**이라, 먼저 놓인 치환기가 아직 없는 이웃을
          고려하지 못했다. 이쪽이 더 큰 원인이다 — −NO₂ 는 쌍별 최적이 2.90 Å 인데
          실제 구조는 1.142 Å 이었다

    mtv_cif_builder.py 에 (1) 충돌 그래프 기반 자리 선택과 (2) 회전각 동시 최적화를
    넣었다. 이 스크립트는 그걸로 다시 만들고, 새 검사기로 확인한다.

[상한이 62.5% 인 이유 — 075 와 100 은 만들어지지 않는다]
    제약이 두 종류다.
      (1) 배타쌍 6개 — 두 자리에 동시에 −SO₃H 를 달면 어떤 회전으로도 안 떨어진다
      (2) 강제쌍 18개 — 자리 i 에 −SO₃H 를 달면 자리 j 에 **남아 있는 Cl** 과
          부딪힌다. 해법은 j 도 치환해 Cl 을 없애는 것뿐이다

    (1) 과 (2) 가 같은 쌍에 동시에 걸리면 그 자리는 아예 쓸 수 없다. 두 제약을
    함께 풀면 최대 유효 치환 자리는 **15/24 = 62.5%** 다. 그래서 25% 와 50% 만
    만들어지고 **75% 와 100% 는 만들어지지 않는다.**

    이건 강체·이상화 기하에 대한 기하학적 선별이지 "화학적으로 불가능"의 증명은
    아니다. 힘장 이완이 일부 접촉을 풀어 줄 수 있다. 다만 **이 빌더로는 못 만든다**
    는 것이 사실이고, 못 만든 것을 만든 척한 결과가 지금까지의 saIm075/100 이다.

[출력]
    structures_v2/ 에 쓴다. **기존 structures/ 를 덮지 않는다** — 무엇으로 계산한
    결과인지 나중에 구별할 수 있어야 하고, 옛 결과를 재현할 수단도 남겨야 한다.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, '05_MTV_Ligand_Library')
sys.path.insert(0, LIGLIB)
sys.path.insert(0, ROOT)

from mtv_cif_builder import generate_mtv_cif_zif69_aryl  # noqa: E402
from audit_orphans import audit  # noqa: E402
from check_substituent_clash import check  # noqa: E402

OUT = os.path.join(HERE, 'structures_v2')
BASE_CIF = os.path.join(LIGLIB, 'ZIF69_base.cif')
SITE_MAP = os.path.join(LIGLIB, 'site_map_zif69_bicyclic.json')

# (태그 접두, 라이브러리 키, 표기, 만들 치환율)
#
# saIm 이 이번 작업의 대상이다. 나머지는 같은 결함을 갖고 있으므로 함께 만들어 두되,
# 재계산 우선순위는 saIm 이 먼저다(STRUCTURE_DEFECT.md 8절).
TARGETS = [
    ('saIm',  'saIm_aryl',  '-SO3H',   [0.25, 0.50, 0.75]),
]
# 나머지 계열. `python rebuild_structures.py all` 로 함께 만든다.
OTHERS = [
    ('mslm',  'mslm_aryl',  '-SO2CH3', [0.25, 0.50, 0.75]),
    ('cf3Im', 'cf3Im_aryl', '-CF3',    [0.25, 0.50, 0.75]),
    ('nbIm',  'nbIm_aryl',  '-NO2',    [0.25, 0.50, 0.75, 1.0]),
    ('brbIm', 'brbIm_aryl', '-Br',     [0.25, 0.50, 0.75, 1.0]),
    ('cnbIm', 'cnbIm_aryl', '-CN',     [0.25, 0.50, 0.75, 1.0]),
    ('mbIm',  'mbIm_aryl',  '-CH3',    [0.25, 0.50, 0.75, 1.0]),
    ('fbIm',  'fbIm_aryl',  '-F',      [0.25, 0.50, 0.75, 1.0]),
]


def fix_tags(path):
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def main():
    targets = TARGETS + (OTHERS if 'all' in sys.argv[1:] else [])
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for short, full, group, fracs in targets:
        for frac in fracs:
            tag = f'{short}{int(round(frac * 100)):03d}'
            out_cif = os.path.join(OUT, f'ZIF69_{tag}.cif')
            print(f'\n=== {tag} ({group}, {frac:.0%}) ===', flush=True)
            comp = {'clIm_aryl': round(1 - frac, 6), full: frac}
            try:
                generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, out_cif, seed=0)
            except ValueError as e:
                # 무충돌로 달성 불가능한 치환율. 조성을 조용히 낮추지 않고 남긴다.
                print(f'  [만들 수 없음] {tag}: {e}', flush=True)
                rows.append({'tag': tag, 'sub': full, 'group': group, 'frac': frac,
                             'built': False, 'reason': str(e)})
                continue
            except Exception as e:
                print(f'  [빌드 실패] {tag}: {type(e).__name__}: {e}', flush=True)
                rows.append({'tag': tag, 'sub': full, 'group': group, 'frac': frac,
                             'built': False, 'reason': f'{type(e).__name__}: {e}'})
                continue
            fix_tags(out_cif)

            # 검사 둘 다 돌린다. 서로 다른 것을 잡는다 — audit 은 고아/분리,
            # check_substituent_clash 는 치환기 관통.
            a = audit(out_cif)
            c = check(out_cif)
            ok = (len(a['orphans']) + len(a['h_orphans']) == 0
                  and a['detached_atoms'] == 0 and c['pass'])
            meta = json.load(open(out_cif.replace('.cif', '.meta.json'),
                                  encoding='utf-8'))
            rows.append({'tag': tag, 'sub': full, 'group': group, 'frac': frac,
                         'built': True, 'pass': ok,
                         'n_atoms': a['n'], 'orphan': len(a['orphans']),
                         'detached': a['detached_atoms'],
                         'fused_linkers': c['fused'],
                         'forbidden_contacts': c['forbidden_contacts'],
                         'min_pairwise_distance': meta.get('min_pairwise_distance'),
                         'n_conflict_pairs': meta.get('n_conflict_pairs'),
                         'n_substituted': meta.get('n_substituted'),
                         'worst_vdw_margin':
                             meta.get('worst_vdw_margin_after_rotation')})
            print(f'  [{"통과" if ok else "탈락"}] 융합 {c["fused"]} / '
                  f'금지접촉 {c["forbidden_contacts"]} / 고아 {len(a["orphans"])}',
                  flush=True)

    idx = os.path.join(HERE, 'rebuild_index.json')
    json.dump(rows, open(idx, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    print('\n' + '=' * 96)
    print(f'{"태그":<10} {"치환":>6} {"융합":>6} {"금지":>6} {"최소거리":>9} '
          f'{"vdW여유":>8}  판정')
    print('-' * 96)
    for r in rows:
        if not r.get('built'):
            print(f'{r["tag"]:<10} {"—":>6} {"—":>6} {"—":>6} {"—":>9} {"—":>8}  '
                  f'만들 수 없음')
            continue
        print(f'{r["tag"]:<10} {r["n_substituted"] or 0:>6} {r["fused_linkers"]:>6} '
              f'{r["forbidden_contacts"]:>6} {r["min_pairwise_distance"]:>9.3f} '
              f'{(r["worst_vdw_margin"] or 0):>8.3f}  '
              f'{"통과" if r["pass"] else "*** 탈락"}')
    n_ok = sum(1 for r in rows if r.get('pass'))
    print(f'\n{len(rows)}종 중 통과 {n_ok}종 -> {OUT}')
    print('기존 structures/ 는 건드리지 않았습니다. 재계산이 끝나기 전까지 '
          '두 벌이 공존합니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
