"""고밀도 치환 구조의 3대 물리 위험을 GCMC 전에 걸러낸다.

기공을 좁히는 게 목적이므로 '좁아지는 것'과 '막히는 것'의 경계를 정확히
찾아야 한다. 셋 다 통과해야 GCMC로 넘긴다.

  [위험 1] 침투 한계 (PLD)
      PLD가 CO2 운동직경 3.3 A 아래면 CO2가 창구를 통과하지 못한다. 기공이
      아무리 좋아도 도달할 수 없으면 무의미하다.
      * 단, 정적 ZIF-8 자체가 PLD 3.25 A로 이미 이 기준에 걸린다. 실제로는
        유한온도에서 링커가 회전해 CO2가 드나든다. 그래서 닫힌상 하나로
        판정하면 순수 ZIF-8도 탈락하는 위양성이 난다. 닫힌상/열린상을
        괄호로 묶어 '열린상에서도 막히면 진짜 막힘'으로 판정한다.

  [위험 2] 골격 변형/붕괴
      UFF4MOF 이완 후 LCD가 순수 ZIF-8 대비 20% 넘게 줄면 공동 붕괴로 본다.
      최소 원자간 거리 < 0.7 A면 원자 겹침(구조 파손)이다. 고밀도 치환은
      치환기끼리 밀어내므로 이 위험이 실재한다 -- 실제로 -SO3H 배치에서
      산소끼리 0.73 A까지 접근했다.

  [위험 3] 접근가능 부피 급락
      3.3 A 프로브 기준 접근가능 부피는 '줄어야' 한다(그게 목적이다). 그러나
      0에 수렴하면 흡착할 공간 자체가 사라진 것이다. 감소는 통과, 소멸은 탈락.

판정 기준을 하나라도 어기면 GCMC 대상에서 제외한다.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

import numpy as np
import networkx as nx
from ase.io import read, write
from ase.neighborlist import NeighborList, natural_cutoffs
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, 'structures')
WORK = os.path.join(HERE, 'lmp')

# Zeo++ network는 czeromof 환경에만 있는데 이 스크립트는 LAMMPS 때문에
# lammps_mof 환경에서 돈다. PATH에 없으면 조용히 실패하므로 절대경로로 잡는다.
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')

CO2_KINETIC = 3.3           # A, CO2 운동직경 = PLD 하한
PROBE_R = CO2_KINETIC / 2   # Zeo++는 반지름을 받는다
LCD_DROP_LIMIT = 20.0       # %, 순수 ZIF-8 대비
MIN_DIST_LIMIT = 0.7        # A
AV_FLOOR = 20.0             # A^3/셀, 이 아래는 '사실상 소멸'


def zeo(atoms, tag, d):
    p = os.path.join(d, tag + '.cif')
    write(p, atoms)
    t = open(p).read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(p, 'w').write(t)

    out = {'LCD': None, 'PLD': None, 'AV': None, 'AV_frac': None, 'err': None}
    try:
        r = subprocess.run([NETWORK, '-ha', '-res', p + '.res', p],
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            out['err'] = f'res exit {r.returncode}: {r.stderr.strip()[:70]}'
        else:
            q = open(p + '.res').readline().split()
            out['LCD'], out['PLD'] = float(q[1]), float(q[2])
    except Exception as e:
        out['err'] = f'res {type(e).__name__}: {e}'

    # 접근가능 부피 -- CO2 프로브(반지름 1.65 A)
    try:
        r = subprocess.run([NETWORK, '-ha', '-vol', f'{PROBE_R}', f'{PROBE_R}',
                            '50000', p + '.vol', p],
                           capture_output=True, text=True, timeout=1800)
        if r.returncode == 0 and os.path.exists(p + '.vol'):
            line = open(p + '.vol').readline()
            m = re.search(r'AV_A\^3:\s*([\d.eE+-]+)', line)
            mf = re.search(r'AV_Volume_fraction:\s*([\d.eE+-]+)', line)
            if m:
                out['AV'] = float(m.group(1))
            if mf:
                out['AV_frac'] = float(mf.group(1))
        elif out['err'] is None:
            out['err'] = f'vol exit {r.returncode}'
    except Exception as e:
        out['err'] = (out['err'] or '') + f' vol {type(e).__name__}'
    return out


def geom(atoms):
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(atoms)
    s = atoms.get_chemical_symbols()
    G = nx.Graph()
    G.add_nodes_from(range(len(atoms)))
    for i in range(len(atoms)):
        for j in nl.get_neighbors(i)[0]:
            G.add_edge(i, int(j))
    cn = [sum(1 for j in G.neighbors(i) if s[j] in ('N', 'O'))
          for i in range(len(atoms)) if s[i] == 'Zn']
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    return {'min_dist': round(float(d.min()), 3), 'Zn_CN': dict(Counter(cn)),
            'n_Zn': len(cn)}


def run_one(name):
    src = os.path.join(STRUCT, name + '.cif')
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(src, os.path.join(d, name + '.cif'))

    before = read(src)
    m0 = {**zeo(before, 'before', d), **geom(before)}

    # lammps-interface가 4배위 황에 UFF에 없는 'S_3' 타입을 붙여 KeyError로 죽는다.
    # 래퍼가 이를 S_3+6(6가 사면체 황 = 술폰산)으로 별칭 등록한 뒤 호출한다.
    iface = os.path.join(HERE, 'lammps_iface_patched.py')
    subprocess.run(f'yes | python {iface} -ff UFF4MOF --minimize {name}.cif',
                   shell=True, cwd=d, capture_output=True, text=True, timeout=1200)
    inp = os.path.join(d, f'in.{name}')
    if not os.path.exists(inp):
        return name, m0, None, 'lammps-interface 실패'
    with open(inp, 'a') as f:
        f.write(f'\nwrite_data min_{name}.data nocoeff\n')
    try:
        subprocess.run(['lmp_serial', '-in', f'in.{name}'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=5400)
    except subprocess.TimeoutExpired:
        return name, m0, None, 'LAMMPS 시간초과'
    dat = os.path.join(d, f'min_{name}.data')
    if not os.path.exists(dat):
        return name, m0, None, 'LAMMPS 출력 없음'

    after = read(dat, format='lammps-data', style='full')
    rep = len(after) // len(before)
    after.set_chemical_symbols(list(before.get_chemical_symbols()) * rep)
    m1 = {**zeo(after, 'after', d), **geom(after)}
    m1['supercell_rep'] = rep
    # 이완 후는 rep^3배 슈퍼셀이 아니라 rep배 원자수다. 부피도 같은 배수이므로
    # 단위셀 기준으로 환산해야 AV를 대조군과 직접 비교할 수 있다.
    if m1['AV'] is not None:
        m1['AV_per_cell'] = round(m1['AV'] / rep, 1)
    if m0['AV'] is not None:
        m0['AV_per_cell'] = round(m0['AV'], 1)
    return name, m0, m1, 'ok'


def main():
    idx = json.load(open(os.path.join(HERE, 'narrow_index.json'), encoding='utf-8'))
    info = {r['name']: r for r in idx}
    names = [r['name'] for r in idx]
    os.makedirs(WORK, exist_ok=True)

    print(f'구조 {len(names)}개 이완 + Zeo++ (CO2 프로브 {CO2_KINETIC} A)...\n', flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=6) as ex:
        for name, m0, m1, st in ex.map(run_one, names):
            res[name] = (m0, m1, st)
            print(f'  [{st:>16}] {name}', flush=True)

    # 대조군 LCD (상별) -- 20% 기준의 분모
    ref = {}
    for ph in ('closed', 'open'):
        n = f'mIm100__{ph}'
        if n in res and res[n][1] and res[n][1]['LCD']:
            ref[ph] = res[n][1]['LCD']

    print('\n' + '=' * 118)
    print(f'{"구조":<26} {"상":<7} {"PLD 전→후":>15} {"LCD 전→후":>15} '
          f'{"ΔLCD%":>7} {"AV/셀":>9} {"최소거리":>8}  판정')
    print('-' * 118)
    rows = []
    for n in names:
        m0, m1, st = res[n]
        lab = info[n]['label']
        ph = info[n]['phase']
        if m1 is None:
            print(f'{lab:<26} {ph:<7} {st}')
            rows.append({'name': n, 'label': lab, 'phase': ph, 'status': st,
                         'pass': False, 'fail': [st]})
            continue

        # [중요] 어느 구조에서 어느 지표를 읽을지가 물리적으로 갈린다.
        #
        #   PLD / AV  -> 이완 '전'(as-built) 값을 쓴다.
        #       빈 골격의 UFF 에너지 최소점은 닫힌 상이라, 자유 이완을 걸면
        #       열린 상이 스스로 닫힌 상으로 되돌아간다(실측: PLD 3.95 -> 3.24,
        #       스윙각 24.55도 -> 0.67도). 즉 이완 후 값으로 판정하면 닫힌상과
        #       열린상이 같은 구조가 되어 괄호로 묶는 의미가 통째로 사라진다.
        #       유한온도에서 실제로 접근 가능한 창구 크기는 as-built 열린상이
        #       대표한다.
        #   LCD 감소 / 최소 원자간 거리 -> 이완 '후' 값을 쓴다.
        #       이건 애초에 '고밀도 치환이 골격을 무너뜨리는가'를 보는 항목이라
        #       힘장 이완을 거쳐야만 의미가 있다.
        fails = []
        pld_j = m0['PLD']            # 침투 한계: as-built
        av_j = m0.get('AV_per_cell')  # 접근가능 부피: as-built
        if pld_j is None or m1['LCD'] is None:
            fails.append(f'Zeo++ 실패({m0["err"] or m1["err"]})')
        else:
            if pld_j < CO2_KINETIC:
                fails.append(f'PLD {pld_j:.2f}<{CO2_KINETIC}')
            drop = (m1['LCD'] - ref.get(ph, m1['LCD'])) / ref.get(ph, m1['LCD']) * 100
            if drop < -LCD_DROP_LIMIT:
                fails.append(f'LCD {drop:+.0f}%')
            if av_j is not None and av_j < AV_FLOOR:
                fails.append(f'AV {av_j:.0f}~0')
        if m1['min_dist'] < MIN_DIST_LIMIT:
            fails.append(f'겹침 {m1["min_dist"]}A')

        drop = ((m1['LCD'] - ref.get(ph, m1['LCD'])) / ref.get(ph, m1['LCD']) * 100
                if m1['LCD'] and ph in ref else float('nan'))
        print(f'{lab:<26} {ph:<7} '
              f'{(m0["PLD"] or 0):>6.2f}→{(m1["PLD"] or 0):<8.2f} '
              f'{(m0["LCD"] or 0):>6.2f}→{(m1["LCD"] or 0):<8.2f} '
              f'{drop:>+7.1f} {(av_j if av_j is not None else float("nan")):>9.1f} '
              f'{m1["min_dist"]:>8.3f}  '
              f'{"통과" if not fails else "탈락: " + ", ".join(fails)}')
        rows.append({'name': n, 'label': lab, 'phase': ph,
                     'n_substituted': info[n]['n_substituted'],
                     'before': m0, 'after': m1,
                     'PLD_judged': pld_j, 'AV_judged_per_cell': av_j,
                     'LCD_change_pct': None if drop != drop else round(drop, 1),
                     'AV_per_cell': av_j, 'pass': not fails, 'fail': fails})

    payload = {'reference_LCD': ref, 'criteria': {
        'PLD_min': CO2_KINETIC, 'LCD_drop_max_pct': LCD_DROP_LIMIT,
        'min_dist_min': MIN_DIST_LIMIT, 'AV_floor_per_cell': AV_FLOOR},
        'rows': rows}

    # 전멸한 결과로 멀쩡한 결과를 덮지 않는다.
    #
    # 2026-08-10 17:29 에 이 스크립트가 lammps_mof 환경 없이 실행돼 16개 전부
    # 'lammps-interface 실패'로 끝났는데, 그대로 risk_results.json 을 덮어썼다.
    # 14 KB 의 기하 데이터가 3.8 KB 의 실패 목록으로 바뀌었고, 08-12 에 git 이
    # 미커밋 변경으로 잡아 주지 않았으면 모르고 지나갈 뻔했다.
    # 3-8(조용한 timeout)과 같은 종류의 사고다 — 실패가 결과처럼 보이는 것.
    dst = os.path.join(HERE, 'risk_results.json')
    if not any(r.get('pass') for r in rows) and os.path.exists(dst):
        try:
            prev = json.load(open(dst, encoding='utf-8')).get('rows') or []
        except (ValueError, OSError):
            prev = []
        if any(r.get('pass') for r in prev):
            alt = dst.replace('.json', '.allfail.json')
            with open(alt, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            print(f'\n[중단] {len(rows)}개 전부 실패했습니다. 기존 결과(통과 '
                  f'{sum(1 for r in prev if r.get("pass"))}개)를 지키기 위해 '
                  f'덮어쓰지 않았습니다.\n       실패 내역: {os.path.basename(alt)}\n'
                  f'       환경을 확인하세요 — lammps_mof 의 PATH 가 빠지면 '
                  f'전부 lammps-interface 실패로 끝납니다.')
            return 1

    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    ok = [r['name'] for r in rows if r.get('pass')]
    print(f'\n통과 {len(ok)}/{len(rows)} -> GCMC 대상')
    for n in ok:
        print(f'   {n}')
    print('\n[OK] risk_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
