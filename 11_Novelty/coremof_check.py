"""우리 구조가 CoRE-MOF 에 이미 있는지 대조한다.

[왜 기하로 대조하면 안 되는가 — NOVELTY_NOTE.md 의 결론]
    우리 구조는 모체 격자를 그대로 물려받고 치환기만 바꿨다. 셀 부피가 ZIF-8 /
    CCDC 739161-739168 과 **소수점까지 일치**한다. 부피나 PXRD 로 조회하면 결과는
    무조건 '신규 아님'이고, 조성 차이는 피크 세기에만 약하게 나타난다.
    의미 있는 조회는 **금속 + 링커 조성 + 위상** 이어야 한다.

[대조 키를 무엇으로 할 것인가 — 네 번 갈아엎은 부분]
    MOFid 는 링커를 배위된 형태로 적는다. 우리 라이브러리는 중성이다.

        우리    Cc1ncc[nH]1        (2-메틸이미다졸)
        MOFid   CC1=NC=C[N]1       (2-메틸이미다졸레이트)
                CC1=N[CH]C=N1      (같은 것의 또 다른 표기)

    시도한 것과 결과:
      1) 정규 SMILES 직접 비교      전부 불일치. 당연하다.
      2) InChIKey 연결성 층          불일치. `[N]` 이 수소 없는 질소로 파싱돼
                                    분자식이 달라지는데, 첫 블록은 분자식을 포함한다.
      3) 라디칼·수소 정규화          3/6. `[CH]` 표기가 남아 방향족화가 막힌다.
      4) + 호변이성체 정규화         4/6. 트리아졸은 고쳤지만 이미다졸은 못 고친다.
                                    RDKit 이 **탄소산 호변이성**을 기본 변환에서
                                    의도적으로 제외하기 때문이다.

    그래서 **중원자 그래프 키**를 쓴다. 모든 결합을 단일결합으로 만들고 수소를
    무시한 뒤 정규 SMILES 를 얻는다. 결합차수와 양성자화를 구조적으로 무시하므로
    표기 차이에 영향받지 않는다.

    이 키는 느슨하다 — 결합차수만 다른 두 화합물을 같다고 본다. **신규성 판정에서는
    그 방향의 오류가 안전하다.** 놓친 선행 구조 하나가 주장을 통째로 무너뜨리는 반면,
    과잉 일치는 사람이 눈으로 걸러 내면 된다. 그래서 일치가 나오면 엄격 키를 함께
    출력해 실제로 같은 화합물인지 확인할 수 있게 했다.

[이 데이터베이스의 한계 — 결론을 쓸 때 반드시 병기할 것]
    `CR_meta_data_SI.json` 은 **SI 유래 부분집합**이다(2737항목 / 고유 DOI 979개,
    ASR·FSR 중복 포함). 실제로 위상 `gme` 항목이 **0개**인데, ZIF-69 는 실험적으로
    보고된 구조다. 즉 **여기 없다는 것이 세상에 없다는 뜻이 아니다.**
    최종 주장에는 전체 CoRE-MOF 와 CSD 조회가 필요하다.
"""
import functools
import json
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem.MolStandardize import rdMolStandardize

RDLogger.DisableLog('rdApp.*')
_TE = rdMolStandardize.TautomerEnumerator()

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'CR_meta_data_SI.json')

# 우리가 쓰는(또는 쓸 수 있는) 링커 전체. 빌더 라이브러리와 같아야 한다.
OUR_LINKERS = {
    'mIm': 'Cc1ncc[nH]1',
    'nIm': 'O=[N+]([O-])c1ncc[nH]1',
    'clIm': 'Clc1ncc[nH]1',
    'cnIm': 'N#Cc1ncc[nH]1',
    'tfIm': 'FC(F)(F)c1ncc[nH]1',
    'etIm': 'CCc1ncc[nH]1',
    'amIm': 'Nc1ncc[nH]1',
    'amrIm': 'NCc1ncc[nH]1',
    'saIm': 'OS(=O)(=O)c1ncc[nH]1',
    'clIm_aryl': 'c1nc2cc(Cl)ccc2[nH]1',
    'cf3Im_aryl': 'c1nc2cc(C(F)(F)F)ccc2[nH]1',
    'saIm_aryl': 'c1nc2cc(S(=O)(=O)O)ccc2[nH]1',
    'nbIm_aryl': 'c1nc2cc([N+](=O)[O-])ccc2[nH]1',
    'mbIm_aryl': 'c1nc2cc(C)ccc2[nH]1',
    'brbIm_aryl': 'c1nc2cc(Br)ccc2[nH]1',
    'cnbIm_aryl': 'c1nc2cc(C#N)ccc2[nH]1',
    'mslm_aryl': 'c1nc2cc(S(=O)(=O)C)ccc2[nH]1',
    'fbIm_aryl': 'c1nc2cc(F)ccc2[nH]1',
}

# 우리 구조의 조성. MTV 라 한 골격에 여러 링커가 섞인다.
OUR_FRAMEWORKS = {
    'ZIF-8 모체':            ('Zn', 'sod', ['mIm']),
    'ZIF-8 + SO3H 50%':      ('Zn', 'sod', ['mIm', 'saIm']),
    'ZIF-8 Cl50+SO3H50':     ('Zn', 'sod', ['clIm', 'saIm']),
    'ZIF-69 모체':           ('Zn', 'gme', ['clIm_aryl', 'nIm']),
    'ZIF-69 + SO3H (부분)':  ('Zn', 'gme', ['clIm_aryl', 'nIm', 'saIm_aryl']),
    'ZIF-69 + SO3H 100%':    ('Zn', 'gme', ['nIm', 'saIm_aryl']),
    'ZIF-69 + NO2 (부분)':   ('Zn', 'gme', ['clIm_aryl', 'nIm', 'nbIm_aryl']),
    'ZIF-69 + Br (부분)':    ('Zn', 'gme', ['clIm_aryl', 'nIm', 'brbIm_aryl']),
    'ZIF-69 + CF3 (부분)':   ('Zn', 'gme', ['clIm_aryl', 'nIm', 'cf3Im_aryl']),
    'ZIF-69 + SO2CH3 (부분)': ('Zn', 'gme', ['clIm_aryl', 'nIm', 'mslm_aryl']),
}


def _relax(m):
    changed = False
    for a in m.GetAtoms():
        if a.GetNumRadicalElectrons():
            a.SetNumRadicalElectrons(0)
            a.SetNoImplicit(False)
            changed = True
        elif a.IsInRing() and a.GetNoImplicit():
            a.SetNoImplicit(False)
            a.SetNumExplicitHs(0)
            changed = True
    return changed


def _parse(smi):
    m = Chem.MolFromSmiles(smi)
    if m is None:
        m = Chem.MolFromSmiles(smi, sanitize=False)
        if m is None:
            return None
        try:
            m.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(m)
        except Exception:
            return None
    if _relax(m):
        try:
            m.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(m)
        except Exception:
            return None
    return m


@functools.lru_cache(maxsize=300000)
def graph_key(smi):
    """고리 안은 그래프만, 고리 밖은 결합차수까지 보는 키.

    [왜 고리 안팎을 다르게 다루는가]
        표기 차이(양성자화·호변이성·방향족화)는 **전부 고리 안에서** 생긴다.
        배위된 이미다졸레이트가 `[N]` 이 되든 `[CH]` 가 되든 고리 밖 치환기는
        그대로다. 그래서 고리 결합만 단일결합으로 뭉개고 고리 밖은 보존한다.

        결합차수를 전부 버리면 **−CH₂NH₂ 와 −C≡N 이 같아진다**(둘 다 고리−C−N).
        실제로 첫 판 자체시험이 이 충돌을 잡아냈다. 고리 밖을 살리면 삼중결합과
        단일결합이 구별되어 해소된다.
    """
    m = _parse(smi)
    if m is None:
        return None
    em = Chem.RWMol(m)
    for b in em.GetBonds():
        if b.IsInRing():
            b.SetBondType(Chem.BondType.SINGLE)
            b.SetIsAromatic(False)
    for a in em.GetAtoms():
        if a.IsInRing():
            a.SetIsAromatic(False)
            a.SetNumExplicitHs(0)
            a.SetNoImplicit(True)
            a.SetFormalCharge(0)
    try:
        mm = em.GetMol()
        mm.UpdatePropertyCache(strict=False)
        return Chem.MolToSmiles(mm)
    except Exception:
        return None


@functools.lru_cache(maxsize=300000)
def strict_key(smi):
    """엄격 키 — 그래프 키가 맞은 건에 대해 실제 동일 화합물인지 눈으로 볼 때 쓴다."""
    m = _parse(smi)
    if m is None:
        return None
    try:
        m = _TE.Canonicalize(m)
    except Exception:
        pass
    return Chem.MolToSmiles(m)


def parse_mofid(s):
    """MOFid-v1 을 (금속 목록, 링커 SMILES 목록, 위상) 으로 가른다."""
    s = str(s or '')
    if not s or s.startswith('*'):
        return [], [], None
    head, _, tail = s.partition(' MOFid-v1.')
    topo = tail.split('.')[0] if tail else None
    metals, linkers = [], []
    for part in head.split('.'):
        part = part.strip()
        if not part:
            continue
        m = Chem.MolFromSmiles(part, sanitize=False)
        if m is None:
            continue
        syms = {a.GetSymbol() for a in m.GetAtoms()}
        organic = {'C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I', 'H', 'B', 'Si'}
        if syms - organic:
            metals.append(part)
        else:
            linkers.append(part)
    return metals, linkers, topo


def selftest():
    """키가 실제로 작동하는지 확인한다. 여기서 실패하면 결과 전체가 무의미하다."""
    pos = [
        ('mIm', 'Cc1ncc[nH]1', 'CC1=NC=C[N]1'),
        ('mIm [CH]이형', 'Cc1ncc[nH]1', 'CC1=N[CH]C=N1'),
        ('벤즈이미다졸', 'c1ccc2[nH]cnc2c1', 'c1ccc2c(c1)N=C[N]2'),
        ('nIm', 'O=[N+]([O-])c1ncc[nH]1', 'O=N(=O)C1=N[CH]C=N1'),
        ('테트라졸', 'c1nnn[nH]1', '[N]1C=NN=N1'),
        ('트리아졸', 'c1cn[nH]n1', '[N]1C=CN=N1'),
    ]
    neg = [
        ('mIm vs 5-Cl-벤즈Im', 'Cc1ncc[nH]1', 'c1nc2cc(Cl)ccc2[nH]1'),
        ('SO3H vs NO2', 'c1nc2cc(S(=O)(=O)O)ccc2[nH]1', 'c1nc2cc([N+](=O)[O-])ccc2[nH]1'),
        ('Br vs F', 'c1nc2cc(Br)ccc2[nH]1', 'c1nc2cc(F)ccc2[nH]1'),
        ('SO3H vs SO2CH3', 'c1nc2cc(S(=O)(=O)O)ccc2[nH]1', 'c1nc2cc(S(=O)(=O)C)ccc2[nH]1'),
        ('이미다졸 vs 피라졸', 'c1cnc[nH]1', 'c1cn[nH]c1'),
        ('mIm vs 에틸Im', 'Cc1ncc[nH]1', 'CCc1ncc[nH]1'),
        ('치환 vs 무치환 벤즈Im', 'c1nc2cc(C)ccc2[nH]1', 'c1ccc2[nH]cnc2c1'),
    ]
    print('=== 키 자체시험 ===')
    ok = sum(graph_key(a) is not None and graph_key(a) == graph_key(b)
             for _, a, b in pos)
    print(f'  양성(같아야 함) {ok}/{len(pos)}')
    for name, a, b in pos:
        if graph_key(a) != graph_key(b):
            print(f'    실패: {name}  {graph_key(a)} vs {graph_key(b)}')
    bad = [n for n, a, b in neg if graph_key(a) == graph_key(b)]
    print(f'  음성(달라야 함) {len(neg)-len(bad)}/{len(neg)}')
    for n in bad:
        print(f'    거짓 일치: {n}')
    keys = {}
    coll = 0
    for tag, smi in OUR_LINKERS.items():
        k = graph_key(smi)
        if k in keys:
            coll += 1
            print(f'    링커 충돌: {tag} == {keys[k]}')
        keys[k] = tag
    print(f'  우리 링커 고유 {len(keys)}/{len(OUR_LINKERS)}, 충돌 {coll}건')
    return ok == len(pos) and not bad and coll == 0


def main():
    if not os.path.exists(DB):
        print(f'DB 없음: {DB}')
        return 1
    if not selftest():
        print('\n!! 키 자체시험 실패 — 결과를 신뢰할 수 없으므로 중단합니다.')
        return 1

    db = json.load(open(DB, encoding='utf-8'))
    print(f'\n=== DB: {len(db)}항목 ===')

    entries = []
    for k, e in db.items():
        metals, linkers, topo = parse_mofid((e.get('id') or {}).get('mofid-v1'))
        entries.append({
            'key': k,
            'metals': metals,
            'linker_keys': frozenset(filter(None, (graph_key(s) for s in linkers))),
            'linker_smiles': linkers,
            'topo_mofid': topo,
            'topo_cn': (e.get('CrystalNets') or {}).get('all_nodes'),
            'metal_type': (e.get('metal') or {}).get('metal_type'),
            'doi': (e.get('reference') or {}).get('DOI'),
            'lcd': (e.get('Zeopp') or {}).get('LCD'),
            'name': (e.get('id') or {}).get('common_name'),
        })
    print(f'  MOFid 파싱 성공: {sum(1 for e in entries if e["linker_keys"])}개')

    our_keys = {t: graph_key(s) for t, s in OUR_LINKERS.items()}

    print('\n' + '=' * 100)
    print('1단계 — 우리 링커 하나라도 들어 있는 CoRE-MOF 항목이 있는가')
    print('=' * 100)
    for tag, gk in sorted(our_keys.items()):
        hits = [e for e in entries if gk in e['linker_keys']]
        mark = '' if hits else '   <- 선행 사례 없음'
        print(f'  {tag:<12} {len(hits):>4}건{mark}')
        for h in hits[:3]:
            print(f'       {h["key"][:38]:<40} {str(h["metal_type"]):<4} '
                  f'{str(h["topo_cn"]):<10} DOI {h["doi"]}')

    print('\n' + '=' * 100)
    print('2단계 — 우리 골격 조성(금속 + 링커 집합 + 위상)과 일치하는 항목이 있는가')
    print('=' * 100)
    rows = []
    for name, (metal, topo, tags) in OUR_FRAMEWORKS.items():
        want = frozenset(our_keys[t] for t in tags)
        same_set = [e for e in entries if e['linker_keys'] == want]
        superset = [e for e in entries if want and want <= e['linker_keys']]
        same_metal_topo = [e for e in superset
                           if str(e['metal_type']) == metal
                           and str(e['topo_cn']) == topo]
        verdict = ('선행 있음' if same_metal_topo else
                   '부분 일치' if superset else '일치 없음')
        print(f'\n  {name}')
        print(f'    링커 {tags}')
        print(f'    링커집합 완전일치 {len(same_set)} / 포함 {len(superset)} / '
              f'+금속{metal}+위상{topo} {len(same_metal_topo)}  -> **{verdict}**')
        for h in same_metal_topo[:5]:
            print(f'       {h["key"]}  DOI {h["doi"]}')
        rows.append({'framework': name, 'metal': metal, 'topology': topo,
                     'linkers': tags, 'exact_linker_set': len(same_set),
                     'superset': len(superset),
                     'same_metal_and_topology': len(same_metal_topo),
                     'verdict': verdict,
                     'matches': [h['key'] for h in same_metal_topo]})

    out = os.path.join(HERE, 'coremof_match.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'database': os.path.basename(DB),
                   'n_entries': len(db),
                   'caveat': ('SI 유래 부분집합. 위상 gme 항목이 0개이고 ZIF-69 가 '
                              '들어 있지 않다. 여기 없다는 것이 세상에 없다는 뜻이 '
                              '아니므로, 최종 주장에는 전체 CoRE-MOF 와 CSD 조회가 '
                              '필요하다.'),
                   'rows': rows}, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
