"""새 링커 후보 3종(cf3Im_aryl, mslm_aryl, fbIm_aryl)을 ZIF-69 벤조 b2 자리에
25/50/75/100%로 치환해 구조를 만들고, 감사(orphan/detached/clash) + Zeo++
LCD/PLD/AV까지 한 번에 끝내 aryl_scan_index.json에 이어붙인다.

[왜 이 3종인가]
    외부 보고서(CCUS ZIF 링커 검토)를 프로젝트 실측 데이터와 교차검증한 결과.
    보고서가 1순위로 든 mslm은 SMILES 상 이미다졸 C2(sod, 창구 방향)에 붙는
    자리였다 -- ZIF-8에서 -SO3H로 이미 반증된 실패 패턴(Q_st 25 정체)과 같다.
    같은 화학(설폰 EWG, H-bond donor 없음)을 벤조 b2(gme, 공동 방향)로 옮긴
    버전이 mslm_aryl이다. fbIm_aryl은 -SO3H보다 훨씬 작은 EWG로, 100% 치환
    없이 목표대에 들 수 있는지를 묻는다(브리핑 8-3). cf3Im_aryl은 이미
    라이브러리에 등록만 되고 미계산이던 것 -- 소수성+EWG를 겸비한 축 3 후보다.
    보고서의 dcnlm/cnblm(니트릴 계열)은 제외한다 -- cnbIm_aryl과 같은 자리라
    빌더가 만들 수 없고(C-아릴 축과 공선), 무효화 전 밀도맵에서도 CO2가
    회피하는 접촉선호도가 나왔다(5-4절, 방향만 유효).

[조성]
    saIm_aryl 계열과 동일하게 clIm_aryl(ZIF-69 원래 치환기)과 25/50/75/100%로
    섞는다 -- 그래야 무치환/−SO₃H 계열과 apples-to-apples 비교가 된다.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, '05_MTV_Ligand_Library')
sys.path.insert(0, LIGLIB)
sys.path.insert(0, ROOT)

from mtv_cif_builder import generate_mtv_cif_zif69_aryl  # noqa: E402
from audit_orphans import audit  # noqa: E402

STRUCT = os.path.join(HERE, 'structures')
BASE_CIF = os.path.join(LIGLIB, 'ZIF69_base.cif')
SITE_MAP = os.path.join(LIGLIB, 'site_map_zif69_bicyclic.json')
INDEX_PATH = os.path.join(HERE, 'aryl_scan_index.json')

NETWORK = os.environ.get('NETWORK_BIN') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')
CO2_KINETIC = 3.3
PROBE_R = CO2_KINETIC / 2  # 1.65 A, 브리핑 2절과 동일

# (short tag, full LIGAND_LIBRARY_CBIM_ARYL key, 사람이 읽는 작용기 표기)
CANDIDATES = [
    ('cf3Im', 'cf3Im_aryl', '-CF3'),
    ('mslm',  'mslm_aryl',  '-SO2CH3'),
    ('fbIm',  'fbIm_aryl',  '-F'),
]
FRACTIONS = [0.25, 0.5, 0.75, 1.0]


def fix_tags(path):
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def zeo(cif_path):
    out = {'LCD': None, 'PLD': None, 'AV': None}
    try:
        subprocess.run([NETWORK, '-ha', '-res', cif_path + '.res', cif_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        v = open(cif_path + '.res').readline().split()
        out['LCD'], out['PLD'] = float(v[1]), float(v[2])
    except Exception as e:
        print(f'    [zeo res 실패] {cif_path}: {type(e).__name__}', flush=True)
    try:
        subprocess.run([NETWORK, '-ha', '-vol', f'{PROBE_R}', f'{PROBE_R}', '20000',
                        cif_path + '.vol', cif_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        m = re.search(r'(?<!N)AV_A\^3:\s*([0-9.eE+-]+)', open(cif_path + '.vol').read())
        if m:
            out['AV'] = float(m.group(1))
    except Exception as e:
        print(f'    [zeo vol 실패] {cif_path}: {type(e).__name__}', flush=True)
    return out


def main():
    os.makedirs(STRUCT, exist_ok=True)
    idx = json.load(open(INDEX_PATH, encoding='utf-8')) if os.path.exists(INDEX_PATH) else []
    existing_tags = {r['tag'] for r in idx}

    new_rows = []
    for short, full, group in CANDIDATES:
        for frac in FRACTIONS:
            tag = f'{short}{int(round(frac * 100)):03d}'
            if tag in existing_tags:
                print(f'  [이미있음] {tag}', flush=True)
                continue
            out_cif = os.path.join(STRUCT, f'ZIF69_{tag}.cif')
            composition = {'clIm_aryl': round(1 - frac, 6), full: frac}
            print(f'\n=== {tag} ({group}, {frac:.0%}) ===', flush=True)
            try:
                generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, composition, out_cif, seed=0)
            except Exception as e:
                print(f'  [빌드 실패] {tag}: {type(e).__name__}: {e}', flush=True)
                new_rows.append({'sub': full, 'group': group, 'frac': frac, 'tag': tag,
                                  'pass': False, 'build_error': str(e)})
                continue
            fix_tags(out_cif)

            a = audit(out_cif)
            n_orphan = len(a['orphans']) + len(a['h_orphans'])
            n_clash = len(a['clashes'])
            n_detached = a['detached_atoms']
            ok = (n_orphan == 0 and n_clash == 0 and n_detached == 0)

            row = {'sub': full, 'group': group, 'frac': frac, 'tag': tag,
                   'n_atoms': a['n'], 'orphan': n_orphan, 'detached': n_detached,
                   'clash': n_clash, 'pass': ok}

            if ok:
                z = zeo(out_cif)
                row.update(z)
                print(f'  [통과] {tag} 원자{a["n"]} LCD={z["LCD"]} PLD={z["PLD"]} AV={z["AV"]}',
                      flush=True)
            else:
                print(f'  [탈락] {tag} 고아={n_orphan} 충돌={n_clash} 분리={n_detached}',
                      flush=True)
            new_rows.append(row)

    idx.extend(new_rows)
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
    n_pass = sum(1 for r in new_rows if r.get('pass'))
    print(f'\n[OK] aryl_scan_index.json 갱신: 신규 {len(new_rows)}종 중 통과 {n_pass}종')
    return 0


if __name__ == '__main__':
    sys.exit(main())
