"""ZIF-69 −SO₃H 계열의 구조 안정성 — UFF4MOF 이완 후 기공이 살아남는가.

[왜 필요한가]
    ZIF-69 + SO₃H 100% 가 Q_st 31.07, 선택도 102, 로딩 2.16 으로 목표권에 처음
    들어왔다. 그런데 그건 **정적 강체 골격** 계산이다. 벤조환 24개 전부에 부피 큰
    술폰산을 매달았을 때 골격이 그 형태를 유지하는지는 별개 문제다.

[판정 기준 — 18_PoreNarrowing/risk_screen.py 와 동일하게 유지]
    같은 기준을 써야 ZIF-8 계열과 직접 비교된다.
      * PLD > 3.3 A (CO2 운동직경) — 창구가 열려 있는가
      * LCD 감소 < 20% (모체 대비) — 공동이 무너지지 않았는가
      * 접근가능부피 비소멸
      * 최소 원자간 거리 > 0.7 A — 구조 파손 여부

[MIGRATION.md 3-6: 이완 전/후 지표를 갈라 써야 한다]
    빈 골격의 UFF 에너지 최소점은 닫힌 상이라, 자유 이완을 걸면 열린 게이트가
    스스로 닫힌다(ZIF-8 실측 PLD 3.95 -> 3.24). 그래서
      * PLD / 접근가능부피  -> 이완 **전**(as-built) 값으로 판정
      * LCD 감소율 / 최소거리 -> 이완 **후** 값으로 판정

[MIGRATION.md 3-2: 황 원자 타입]
    lammps-interface 가 4배위 황에 UFF 어디에도 없는 'S_3' 를 붙여 KeyError 로
    죽는다. 술폰산의 황은 6가 사면체라 S_3+6 이 정답이고, 18_PoreNarrowing 의
    래퍼가 그 별칭을 등록한다. **이 계열은 전부 술폰산이므로 반드시 래퍼를 쓴다.**
"""
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from ase.io import read, write

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, 'structures')
BASE_SRC = os.path.join(HERE, '..', '05_MTV_Ligand_Library', 'ZIF69_base.cif')
WORK = os.path.join(HERE, 'lmp')
# 18_PoreNarrowing 의 S_3+6 패치 래퍼를 그대로 쓴다(중복 구현하지 않는다).
IFACE = os.path.join(HERE, '..', '18_PoreNarrowing', 'lammps_iface_patched.py')

# 이 스크립트는 LAMMPS 때문에 lammps_mof 환경에서 도는데 Zeo++ 는 czeromof 에만
# 있다. PATH 에 없으면 조용히 실패해 LCD/PLD 가 0 으로 기록된다(MIGRATION.md 3-1).
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')

CO2_KINETIC = 3.3
PROBE_R = CO2_KINETIC / 2
LCD_DROP_LIMIT = 20.0
MIN_DIST_LIMIT = 0.7
AV_FLOOR = 20.0


def fix_tags(p):
    t = open(p, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(p, 'w', encoding='utf-8').write(t)


def zeo(atoms, tag, d):
    p = os.path.join(d, tag + '.cif')
    write(p, atoms)
    fix_tags(p)
    out = {'LCD': None, 'PLD': None, 'AV': None}
    try:
        subprocess.run([NETWORK, '-ha', '-res', p + '.res', p],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        v = open(p + '.res').readline().split()
        out['LCD'], out['PLD'] = float(v[1]), float(v[2])
    except Exception as e:
        print(f'    [zeo res 실패] {tag}: {type(e).__name__}', flush=True)
    try:
        subprocess.run([NETWORK, '-ha', '-vol', f'{PROBE_R}', f'{PROBE_R}',
                        '20000', p + '.vol', p],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        m = re.search(r'(?<!N)AV_A\^3:\s*([0-9.eE+-]+)', open(p + '.vol').read())
        if m:
            out['AV'] = float(m.group(1))
    except Exception as e:
        print(f'    [zeo vol 실패] {tag}: {type(e).__name__}', flush=True)
    return out


def geom(atoms):
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    return {'min_dist': round(float(d.min()), 3), 'n_atoms': len(atoms)}


def run_one(name):
    src = BASE_SRC if name == 'base' else os.path.join(STRUCT, f'ZIF69_{name}.cif')
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    local = os.path.join(d, name + '.cif')
    shutil.copy(src, local)

    before = read(src)
    m0 = {**zeo(before, 'before', d), **geom(before)}

    r = subprocess.run(f'yes | python {IFACE} -ff UFF4MOF --minimize {name}.cif',
                       shell=True, cwd=d, capture_output=True, text=True,
                       timeout=1800)
    inp = os.path.join(d, f'in.{name}')
    if not os.path.exists(inp):
        tail = (r.stderr or r.stdout or '')[-300:]
        return name, m0, None, f'lammps-interface 실패: {tail}'

    # [ZIF-69 에서 새로 걸린 함정] lammps-interface 는 사이트마다 group 을 하나씩
    # 뱉는데(여기서는 98개) LAMMPS 상한이 32개라 'ERROR: Too many groups (max 32)'
    # 로 죽는다. ZIF-8(276원자)에서는 그룹 수가 적어 안 걸렸다.
    # 이 group 들은 '#### Atom Groupings ####' 주석이 붙은 편의용 메타데이터일 뿐,
    # 실제로 참조하는 명령이 없다(유일한 fix 가 all 을 쓴다). 그래서 제거해도
    # 이완 결과에 영향이 없다. 확인 방법:
    #     grep -vE '^group' in.<name> | grep -E '\b1-[0-9]+\b'   -> 비어 있어야 함
    lines = open(inp, encoding='utf-8').read().splitlines()
    kept = [l for l in lines if not l.startswith('group')]
    n_drop = len(lines) - len(kept)

    # [MIGRATION.md 6절] lammps-interface 는 에너지 변화 1e-6 kcal/mol 까지 반복한다.
    # 구조 안정성만 볼 거면 1e-4 로 완화해도 판정(LCD 20%, PLD 3.3 A)에 영향이 없고
    # 시간이 크게 준다. 여기는 4800원자 슈퍼셀이라 특히 크게 차이난다.
    kept = [re.sub(r'(variable\s+min_eval\s+equal\s+)1\.00e-06',
                   r'\g<1>1.00e-04', l) for l in kept]

    kept.append(f'\nwrite_data min_{name}.data nocoeff')
    open(inp, 'w', encoding='utf-8').write('\n'.join(kept) + '\n')
    if n_drop:
        print(f'    {name}: group {n_drop}개 제거(상한 32), min_eval 1e-6 -> 1e-4',
              flush=True)
    try:
        subprocess.run(['lmp_serial', '-in', f'in.{name}'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=10800)
    except subprocess.TimeoutExpired:
        return name, m0, None, 'LAMMPS 시간초과'
    dat = os.path.join(d, f'min_{name}.data')
    if not os.path.exists(dat):
        return name, m0, None, 'LAMMPS 출력 없음'

    after = read(dat, format='lammps-data', style='full')
    rep = max(1, len(after) // len(before))
    after.set_chemical_symbols(list(before.get_chemical_symbols()) * rep)
    m1 = {**zeo(after, 'after', d), **geom(after)}
    m1['supercell_rep'] = rep
    # 이완 후는 rep 배 원자수(부피도 같은 배수)이므로 단위셀 기준으로 환산해야
    # 이완 전 값과 직접 비교된다.
    if m1['AV'] is not None:
        m1['AV_per_cell'] = round(m1['AV'] / rep, 1)
    if m0['AV'] is not None:
        m0['AV_per_cell'] = round(m0['AV'], 1)
    return name, m0, m1, 'ok'


def main():
    idx = json.load(open(os.path.join(HERE, 'build_index.json'), encoding='utf-8'))
    names = [r['tag'] for r in idx]
    os.makedirs(WORK, exist_ok=True)
    print(f'구조 {len(names)}개 UFF4MOF 이완 + Zeo++\n', flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=6) as ex:
        for name, m0, m1, st in ex.map(run_one, names):
            res[name] = (m0, m1, st)
            print(f'  [{st[:28]:>28}] {name}', flush=True)

    base = res.get('base', (None, None, None))[1]
    lcd_ref = (base or {}).get('LCD') or (res.get('base', ({},))[0] or {}).get('LCD')

    print('\n' + '=' * 112)
    print(f'{"조성":<12} {"PLD(전)":>8} {"AV(전)":>9} {"LCD(전)":>8} {"LCD(후)":>8} '
          f'{"LCD감소%":>9} {"최소거리":>9}  판정')
    print('-' * 112)
    rows = []
    for n in names:
        m0, m1, st = res[n]
        if st != 'ok' or not m1:
            print(f'{n:<12} {st}')
            rows.append({'name': n, 'status': st, 'before': m0, 'after': None,
                         'pass': False})
            continue
        drop = (lcd_ref - m1['LCD']) / lcd_ref * 100 if (lcd_ref and m1['LCD']) else float('nan')
        checks = {
            'PLD': (m0['PLD'] or 0) > CO2_KINETIC,
            'LCD_drop': drop < LCD_DROP_LIMIT,
            'AV': (m0.get('AV_per_cell') or 0) > AV_FLOOR,
            'min_dist': m1['min_dist'] > MIN_DIST_LIMIT,
        }
        ok = all(checks.values())
        bad = ','.join(k for k, v in checks.items() if not v)
        print(f'{n:<12} {m0["PLD"]:>8.3f} {m0.get("AV_per_cell",0):>9.1f} '
              f'{m0["LCD"]:>8.3f} {m1["LCD"]:>8.3f} {drop:>9.1f} '
              f'{m1["min_dist"]:>9.3f}  {"통과" if ok else "탈락: " + bad}')
        rows.append({'name': n, 'status': st, 'before': m0, 'after': m1,
                     'LCD_drop_pct': round(drop, 2), 'checks': checks, 'pass': ok})

    with open(os.path.join(HERE, 'risk_results.json'), 'w', encoding='utf-8') as f:
        json.dump({'criteria': {'PLD_min': CO2_KINETIC,
                                'LCD_drop_limit_pct': LCD_DROP_LIMIT,
                                'AV_floor': AV_FLOOR,
                                'min_dist_limit': MIN_DIST_LIMIT,
                                'LCD_reference': lcd_ref},
                   'rows': rows}, f, indent=2, ensure_ascii=False)
    print('\n[OK] risk_results.json')
    print('\n주: PLD/AV 는 이완 **전**, LCD 감소·최소거리는 이완 **후** 값으로 판정했습니다'
          ' (MIGRATION.md 3-6).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
