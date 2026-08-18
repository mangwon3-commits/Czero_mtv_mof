"""ZIF-67 치환 계열 생성 -- **분광 검증용**으로 조성을 고른다.

[이 계열의 목적은 흡착 성능이 아니다]
    ZIF-67 은 sod 이고, C2 치환기는 공동을 좁히는 대신 6원환 창구를 막습니다.
    우리가 ZIF-69(gme)로 옮긴 이유가 그것이므로 여기서 흡착 천장은 뚫리지 않습니다.

    이 계열은 **실험이 답할 수 있는 질문**을 위한 것입니다 --
    "치환 링커가 넣은 비율대로 실제로 들어가는가."
    협력 랩이 찍을 수 있는 것은 흡광도/IR/라만이고, 이들은 성능이 아니라
    구조와 조성을 봅니다.

[왜 이 두 작용기인가]
    IR 로 치환율을 정량하려면 **다른 봉우리와 겹치지 않는 표지 밴드**가 필요합니다.

    cnIm (-C≡N)  ~2230 cm-1.  2100~2300 구간에는 ZIF-67 의 어떤 모드도 없습니다.
                 **정량에 가장 좋은 표지**입니다. 겹침 보정이 필요 없습니다.
    nIm  (-NO2)  ~1350(sym) / ~1530(asym) cm-1. 강하고 두 개라 상호 확인됩니다.
                 다만 고리 모드 구간이라 겹침 보정이 필요합니다.

    -Cl 은 C-Cl 이 700~800 으로, -SO3H 는 S=O 가 1030~1200 으로 고리 모드와
    겹쳐 정량에 부적합해 뺐습니다.

[치환 개수를 씨앗 탐색으로 맞춘다 -- 2026-08-15 수정]
    첫 판은 이름과 실제가 어긋났습니다. cnIm025 가 7개, cnIm050 이 10개였습니다.

    원인은 충돌 회피 로직이 아니라 **generate_mtv_cif 의 자리 배정 방식**입니다.

        assignment = rng.choice(names, size=len(sites), p=probs)   # 734행

    이것은 확률 p 로 자리마다 독립 추첨하는 **iid 표본추출**이라, 개수가
    이항분포로 흩어집니다. 24자리 p=0.5 면 12 가 나올 확률이 16% 뿐입니다.
    **애초에 개수를 맞추도록 만들어진 코드가 아닙니다.**

    ※ 같은 증상이 ZIF-69 아릴 계열(v1)에도 있었지만 **원인은 다릅니다.**
      그쪽은 conflict_aware 분기가 n_target 을 정한 뒤 forcing_pairs 가 자리를
      더하고 배타쌍이 자리를 빼서 어긋났습니다(802~812행). 증상이 같아도
      경로가 다르므로 고치는 방법도 다릅니다.

    빌더를 고치지 않는 이유는 다른 세션이 같은 파일을 쓰고 있어서입니다.
    대신 **추첨 결과를 미리 재현해 개수가 정확한 씨앗을 찾아** 그 씨앗으로
    한 번만 짓습니다. 구조를 여러 번 지어 보고 버리는 것이 아니라, 배정만
    미리 계산하므로 비용이 없습니다. 고른 씨앗은 색인에 남겨 재현 가능합니다.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, '/home/mangwon1/mof_project/05_MTV_Ligand_Library')
from mtv_cif_builder import generate_mtv_cif                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, 'ZIF67_base.cif')
SITE_MAP = os.path.join(HERE, 'site_map_zif67_v2.json')
OUT = os.path.join(HERE, 'structures')

SERIES = [('cnIm', 'cnIm'), ('nIm', 'nIm')]
RATIOS = [25, 50, 75, 100]
MAX_SEED = 2000


def find_seed(comp, n_sites, want, lig):
    """generate_mtv_cif 의 추첨을 그대로 재현해, 개수가 맞는 씨앗을 찾는다.

    빌더는 names = list(composition.keys()) 순서를 쓰므로 dict 순서를
    똑같이 맞춰야 재현됩니다. 파이썬 3.7+ 의 dict 는 삽입 순서를 지킵니다.
    """
    names, probs = list(comp.keys()), list(comp.values())
    for seed in range(MAX_SEED):
        rng = np.random.default_rng(seed)
        a = rng.choice(names, size=n_sites, p=probs)
        if int((a == lig).sum()) == want:
            return seed
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    for p in (BASE, SITE_MAP):
        if not os.path.exists(p):
            print(f'!! 없음: {p}', flush=True)
            return 1
    n_sites = len(json.load(open(SITE_MAP)))
    print(f'자리 {n_sites}개\n', flush=True)

    index = []
    for fam, lig in SERIES:
        for pct in RATIOS:
            name = f'ZIF67_{fam}{pct:03d}'
            dst = os.path.join(OUT, name + '.cif')
            want = round(n_sites * pct / 100)
            comp = {lig: pct / 100.0}
            if pct < 100:
                comp['mIm'] = 1.0 - pct / 100.0

            seed = 0 if pct == 100 else find_seed(comp, n_sites, want, lig)
            if seed is None:
                print(f'>>> {name}  씨앗 {MAX_SEED}개 안에 정확한 개수 없음 -- 건너뜀',
                      flush=True)
                index.append({'name': name, 'ok': False,
                              'error': 'no seed with exact count'})
                continue
            print(f'>>> {name}  {comp}  목표 {want}자리  씨앗 {seed}', flush=True)
            try:
                generate_mtv_cif(BASE, SITE_MAP, comp, dst, seed=seed)
                index.append({'name': name, 'family': fam, 'pct': pct,
                              'composition': comp, 'n_target': want,
                              'seed': seed, 'cif': dst, 'ok': True})
            except Exception as e:                       # noqa: BLE001
                print(f'    실패: {type(e).__name__}: {e}', flush=True)
                index.append({'name': name, 'ok': False, 'error': str(e)})
            print(flush=True)

    with open(os.path.join(HERE, 'build_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    ok = sum(1 for r in index if r.get('ok'))
    print(f'=== 생성 {ok}/{len(index)} ===', flush=True)
    print('   개수 검증은 verify_series.py 로 따로 합니다 -- 씨앗 탐색이 맞았는지'
          ' 구조 자체에서 다시 세야 합니다.', flush=True)
    return 0 if ok == len(index) else 1


if __name__ == '__main__':
    sys.exit(main())
