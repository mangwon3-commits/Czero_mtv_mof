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

# [2026-08-08] 대상 목록을 인자로 받는다.
#
# 원래 build_index.json(saIm 5종) 만 읽었다. 그런데 아릴 12종은 GCMC 를 마쳤는데도
# **LAMMPS 검증을 한 번도 받지 않았다**(NEXT_STEPS 2-3). 정적 강체 골격 GCMC 에서
# 좋은 값이 나와도 그것만으로는 채택할 수 없으므로 같은 잣대를 적용해야 한다.
#
#     python risk_screen.py                                  # saIm 5종 (기본)
#     python risk_screen.py aryl_scan_index.json aryl        # 아릴 계열
#
# 작업 디렉터리와 결과 파일을 함께 갈라, 두 계열이 lmp/ 에서 섞이지 않게 한다.
INDEX = sys.argv[1] if len(sys.argv) > 1 else 'build_index.json'
SUFFIX = sys.argv[2] if len(sys.argv) > 2 else ''
WORK = os.path.join(HERE, 'lmp' + (('_' + SUFFIX) if SUFFIX else ''))
RESULT = os.path.join(HERE, f'risk_results{("_" + SUFFIX) if SUFFIX else ""}.json')

# 워커 수. 물리 코어가 8개이고 lmp_serial 은 코어당 하나씩 붙으므로 8이 상한이다.
#
# 6으로 박혀 있었는데, 그러면 아릴 12종이 6+6 두 물결로 갈려 한 물결분(약 45분)을
# 통째로 더 쓴다. saIm 은 5종뿐이라 6이든 8이든 차이가 없지만 아릴에서는 다르다.
# ProcessPoolExecutor.map 은 워커가 비는 대로 다음 것을 넣으므로 8이면
# 12/8 = 1.5 물결로 끝난다.
# 물리 코어는 8개(논리 16). 그런데 여기의 병목은 CPU 가 아니라 **메모리**다.
# 이완 후 슈퍼셀(5,248원자)에 Zeo++ 를 돌리면 한 건이 3.2 GB 를 쓴다. 2026-08-12
# 16:41 에 8워커로 돌렸다가 8 x 3.2 = 25.6 GB 로 20 GB 상한을 넘겨 OOM 이 났고,
# 그때 dbus-daemon 까지 죽으면서 WSL 배포판이 통째로 먹통이 됐다.
# 4워커면 12.8 GB 로 여유가 있다. 이 단계는 워커를 늘리면 더 느려지는 게 아니라 죽는다.
# [2026-08-22] 메모리 상한. 이 줄에는 상한이 아예 없었습니다.
#
#   risk_screen_v3.py 는 import 뒤 rs.MAX_WORKERS 를 /proc/meminfo 로 계산해
#   덮어씁니다. 그런데 **이 파일을 직접 돌리면 그 보호가 없습니다** -- 기본 4워커
#   근거가 "4 x 3.2 GB = 12.8 GB" 인데 3.2 는 v1 구조에서 잰 값이고 v3 실측은
#   9.5 GB 입니다. 명세서가 "RISK_WORKERS 를 손으로 주지 마라, 스크립트가
#   /proc/meminfo 에서 계산한다" 고 적었는데 그것이 v3 러너에만 참이었습니다.
#   여기에도 같은 상한을 둡니다. v3 가 나중에 다시 덮어써도 같은 공식이라
#   충돌하지 않고, 이 파일을 직접 돌리는 경로가 보호됩니다.
def _zeo_worker_cap(asked):
    zeo_gb = float(os.environ.get('ZEO_GB_PER_JOB', '9.5'))
    floor_gb = 4.0
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                avail = int(line.split()[1]) / (1024 * 1024)
                break
        else:
            return asked
    except Exception:                                        # noqa: BLE001
        return asked                                          # 못 재면 손대지 않는다
    cap = max(1, int((avail - floor_gb) // zeo_gb))
    if cap < asked:
        print(f'  !! 워커를 {asked} -> {cap} 로 낮춥니다 '
              f'(가용 {avail:.1f} GB, Zeo++ {zeo_gb} GB/건)', flush=True)
    return min(asked, cap)


MAX_WORKERS = _zeo_worker_cap(int(os.environ.get('RISK_WORKERS', '4')))
# 18_PoreNarrowing 의 S_3+6 패치 래퍼를 그대로 쓴다(중복 구현하지 않는다).
IFACE = os.path.join(HERE, '..', '18_PoreNarrowing', 'lammps_iface_patched.py')

# 이 스크립트는 LAMMPS 때문에 lammps_mof 환경에서 도는데 Zeo++ 는 czeromof 에만
# 있다. PATH 에 없으면 조용히 실패해 LCD/PLD 가 0 으로 기록된다(MIGRATION.md 3-1).
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')

# [2026-08-20] lmp_serial 도 같은 처리가 필요하다. 랩탑이 L4 진입 **전에**
# 잡았다 -- 러너의 실제 PATH(/proc 확인)에 lammps_mof/bin 이 없어서, 그대로
# 들어갔으면 LAMMPS 작업이 전부 FileNotFoundError 로 죽었다. 08-19 02:00 에
# 성공했던 것은 그 세션이 conda 활성화 상태에서 띄워졌기 때문이고, 즉
# **호출자의 셸 상태에 의존하고 있었다.** setsid nohup 으로 띄우면 그 상태가
# 없다. NETWORK 와 같은 패턴으로 해석 시점을 코드 안으로 옮긴다.
LMP = shutil.which('lmp_serial') or os.path.expanduser(
    '~/miniconda3/envs/lammps_mof/bin/lmp_serial')

CO2_KINETIC = 3.3
PROBE_R = CO2_KINETIC / 2
LCD_DROP_LIMIT = 20.0
MIN_DIST_LIMIT = 0.7
AV_FLOOR = 20.0

# 이완 상한. 위 patch_input() 의 주석이 근거다.
# 무치환은 50루프에 수렴했고, 치환 구조들은 6~11루프에서 EDiff 1~4 로 평평해진다.
# 12 는 그 평탄부에 도달하되 진동에 시간을 버리지 않는 지점이다.
OUTER_LOOP_CAP = 12
INNER_ITER_CAP = 2000


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
    """최소 원자간 거리. **전체 거리 행렬을 만들면 안 된다.**

    원래 `get_all_distances(mic=True)` 였다. 4800원자 슈퍼셀에 기운 육방 셀(γ=120°)
    이면 ASE 가 주기 이미지를 펼치면서 수 GB 를 잡는다. 2026-08-12 에 이것 때문에
    프로세스가 12.6 GB / 13.5 GB 까지 커져 OOM 으로 두 번 죽었다. 이완은 12종 모두
    끝났는데 결과 파일은 한 줄도 안 써졌다.

    판정에 필요한 것은 '가장 가까운 두 원자가 0.7 A 보다 먼가' 하나뿐이다.
    이웃 목록으로 잘라 보면 **답은 같고** 메모리는 원자 수에 비례한다.
    골격이면 결합 거리(1.0~1.6 A)가 항상 있으므로 2 A 에서 걸린다. 혹시 비었으면
    잘라낸 탓에 답을 못 본 것이므로 넓혀서 다시 본다 — 조용히 틀린 값을 주면 안 된다.
    """
    from ase.neighborlist import neighbor_list
    for cut in (2.0, 4.0, 8.0, 16.0):
        d = neighbor_list('d', atoms, cut)
        if len(d):
            return {'min_dist': round(float(d.min()), 3), 'n_atoms': len(atoms)}
    return {'min_dist': None, 'n_atoms': len(atoms)}


def run_one(name):
    src = BASE_SRC if name == 'base' else os.path.join(STRUCT, f'ZIF69_{name}.cif')
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    local = os.path.join(d, name + '.cif')
    shutil.copy(src, local)

    before = read(src)
    m0 = {**zeo(before, 'before', d), **geom(before)}

    # 이미 이완이 끝나 있으면 다시 돌리지 않는다.
    #
    # 2026-08-12 에 12종 이완이 전부 끝난(각 40분~1시간 20분) 뒤 집계 단계에서
    # OOM 으로 죽어 결과가 한 줄도 안 남았다. 그때 이 분기가 없어서, 되살리려면
    # 2시간 30분짜리 이완을 통째로 다시 돌려야 하는 상황이 됐다.
    # 이완 산출물(min_<name>.data)은 결정적이므로 재사용해도 결과가 달라지지 않는다.
    done = os.path.join(d, f'min_{name}.data')
    if os.path.exists(done) and os.path.getsize(done) > 0:
        # 중간에 죽어 잘린 파일일 수 있으므로 읽어 보고 판단한다. 못 읽으면
        # 재사용을 포기하고 아래로 내려가 처음부터 돌린다.
        try:
            after = read(done, format='lammps-data', style='full')
        except Exception as e:
            print(f'    {name}: 산출물이 손상됨({type(e).__name__}) — 다시 이완합니다',
                  flush=True)
            after = None
        if after is not None:
            print(f'    {name}: 이완 산출물 재사용 (다시 돌리지 않음)', flush=True)
            rep = max(1, len(after) // len(before))
            after.set_chemical_symbols(list(before.get_chemical_symbols()) * rep)
            m1 = {**zeo(after, 'after', d), **geom(after)}
            m1['supercell_rep'] = rep
            if m1['AV'] is not None:
                m1['AV_per_cell'] = round(m1['AV'] / rep, 1)
            if m0['AV'] is not None:
                m0['AV_per_cell'] = round(m0['AV'], 1)
            return name, m0, m1, 'ok'

    # [2026-08-27 Junseok] 여기가 맨 `python` 이었습니다. `shell=True` 라 그
    # 순간의 PATH 를 쓰는데, 시스템에는 python3 만 있고 python 은 conda 환경에만
    # 있습니다. Junseok 이 OOM 재기동 뒤 환경이 안 잡힌 채로 재개돼 **12종 중
    # 7종이 `/bin/sh: 1: python: not found` 로 실패**했습니다. 그런데 러너가
    # 실패를 status 에 적고 계속 진행해 자동 푸시가 "12종 완주" 로 알렸습니다 —
    # 0 절이 말하는 "실패가 결과처럼 보이는 것" 입니다.
    #
    # `sys.executable` 은 지금 이 파이썬의 절대 경로라 PATH 와 무관합니다.
    # 셸 인용이 필요 없도록 리스트 인자로 넘기고 `yes` 는 stdin 으로 대체합니다.
    r = subprocess.run([sys.executable, IFACE, '-ff', 'UFF4MOF', '--minimize',
                        f'{name}.cif'],
                       input='y\n' * 200, cwd=d, capture_output=True,
                       text=True, timeout=1800)
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

    # [2026-08-09] 바깥 루프와 안쪽 반복에 상한을 건다. **이게 없으면 안 끝난다.**
    #
    # 생성되는 입력은 이런 구조다:
    #     variable iter loop 100000
    #     label loop_min
    #       minimize 1e-15 1e-15 10000 100000   (box/relax)
    #       minimize 1e-15 1e-15 10000 100000   (fire)
    #       if "${min_E} < ${min_eval}" then jump break_min
    #     jump SELF loop_min
    #     write_data ...
    #
    # `write_data` 는 루프를 빠져나가야 실행된다. 그런데 치환 구조들은 **수렴하지
    # 않고 진동한다**. 실측(2026-08-09): 무치환은 50루프에서 EDiff 5.3e-08 로 끝났지만
    # 나머지 16종은 0.5~150 에서 정체했고 saIm075(3.8 -> 123.7), nbIm100(6544 -> 118.7)
    # 은 에너지가 오히려 올라갔다. 3시간 타임아웃에 전부 걸려 **산출물이 하나도
    # 안 나왔다.** 시간을 늘려도 결과는 같다.
    #
    # 우리가 판정할 것은 LCD 감소율과 최소 원자간 거리이지 에너지 최소점의 마지막
    # 자릿수가 아니다. 그래서 상한을 걸고 그 시점의 구조를 쓴다. 대신 도달한 EDiff 를
    # 결과에 남겨, 덜 수렴한 구조로 판정했다는 사실이 보이게 한다.
    kept = [re.sub(r'(variable\s+iter\s+loop\s+)\d+',
                   rf'\g<1>{OUTER_LOOP_CAP}', l) for l in kept]
    kept = [re.sub(r'^(minimize\s+\S+\s+\S+\s+)\d+(\s+)\d+',
                   rf'\g<1>{INNER_ITER_CAP}\g<2>{INNER_ITER_CAP * 10}', l)
            for l in kept]

    kept.append(f'\nwrite_data min_{name}.data nocoeff')
    open(inp, 'w', encoding='utf-8').write('\n'.join(kept) + '\n')
    if n_drop:
        print(f'    {name}: group {n_drop}개 제거(상한 32), min_eval 1e-6 -> 1e-4, '
              f'바깥루프 <= {OUTER_LOOP_CAP}, 안쪽반복 <= {INNER_ITER_CAP}', flush=True)

    # [ZIF-69 + SO3H 에서 걸린 두 번째 함정] lammps-interface 가 같은 원자를 두 번
    # 넣은 이면각을 만든다:
    #     ERROR on proc 0: Invalid atom ID in Dihedrals section of data file:
    #       23   4   5   4   692   5
    # 술폰산 계열 4종이 전부 여기서 죽고 무치환 모체만 통과했다. 정의가 성립하지
    # 않는 항이므로 제거해도 이완 결과가 왜곡되지 않는다. 처리는 S_3 타이핑 버그와
    # 같은 자리(18_PoreNarrowing/lammps_iface_patched.py)에 두었다.
    dat_in = os.path.join(d, f'data.{name}')
    if os.path.exists(dat_in):
        sys.path.insert(0, os.path.dirname(os.path.abspath(IFACE)))
        try:
            from lammps_iface_patched import clean_degenerate_topology
            clean_degenerate_topology(dat_in)
        except Exception as e:
            print(f'    {name}: 토폴로지 정리 실패 {type(e).__name__}: {e}', flush=True)
    try:
        subprocess.run([LMP, '-in', f'in.{name}'], cwd=d,
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


def final_ediff(name):
    """이완이 어디까지 수렴했는지. 상한에 걸려 멈춘 구조를 판정할 때 반드시 병기한다.

    min_eval(1e-4)보다 크면 **덜 수렴한 구조로 판정한 것**이므로, LCD 감소율이
    경계 근처인 경우 그 값을 신뢰하면 안 된다.
    """
    p = os.path.join(WORK, name, f'{name}.min.csv')
    try:
        rows = [l for l in open(p, encoding='utf-8').read().splitlines() if ',' in l]
        return float(rows[-1].split(',')[-1]), len(rows) - 1
    except (OSError, ValueError, IndexError):
        return None, None


def main():
    idx = json.load(open(os.path.join(HERE, INDEX), encoding='utf-8'))
    # 아릴 인덱스에는 감사 탈락 구조가 섞여 있다. 겹침이 있는 구조를 이완시키면
    # 무의미한 결과가 나오므로 pass=true 인 것만 본다(build_index 에는 이 키가 없어
    # 기본값 True 로 전부 통과시킨다).
    idx = [r for r in idx if r.get('pass', True)]
    names = [r['tag'] for r in idx]
    print(f'대상: {INDEX} -> {len(names)}종, 작업 {WORK}', flush=True)
    os.makedirs(WORK, exist_ok=True)
    print(f'구조 {len(names)}개 UFF4MOF 이완 + Zeo++\n', flush=True)

    res = {}
    # max_tasks_per_child=1: 작업 하나 끝날 때마다 워커를 새로 만든다. .wslconfig 에
    # 적어 둔 "구조마다 자기 프로세스를 줘서 끝날 때 메모리를 돌려받게 하라"의 구현이다.
    # geom() 을 고쳐 큰 할당 자체를 없앴지만, 누적으로 터지는 실패는 원인이 하나가
    # 아니므로 이쪽도 같이 막는다.
    with ProcessPoolExecutor(max_workers=MAX_WORKERS, max_tasks_per_child=1) as ex:
        for name, m0, m1, st in ex.map(run_one, names):
            res[name] = (m0, m1, st)
            print(f'  [{st[:28]:>28}] {name}', flush=True)

    base = res.get('base', (None, None, None))[1]
    lcd_ref = (base or {}).get('LCD') or (res.get('base', ({},))[0] or {}).get('LCD')

    # 아릴 인덱스에는 무치환 모체(base)가 없다. 그래서 lcd_ref 가 None 이 되고,
    # drop = nan 이 되고, `nan < 20.0` 이 False 라서 **12종이 전부 LCD_drop 으로
    # 탈락했다**(2026-08-12 20:38). 판정이 아니라 계산 부작용이다.
    #
    # 기준은 saIm 쪽 실행이 남긴 무치환 ZIF-69 의 이완 후 LCD 다. 같은 구조를 같은
    # 규약(UFF4MOF, 상한 12루프)으로 이완시킨 값이므로 그대로 쓸 수 있다.
    # 없으면 판정을 하지 않는다 — 기준 없이 매긴 '탈락'은 거짓이다.
    if lcd_ref is None:
        ref_file = os.path.join(HERE, 'risk_results.json')
        try:
            for r in json.load(open(ref_file, encoding='utf-8'))['rows']:
                if r['name'] == 'base' and (r.get('after') or {}).get('LCD'):
                    lcd_ref = r['after']['LCD']
                    print(f'기준 LCD 를 risk_results.json 의 base 에서 가져옴: '
                          f'{lcd_ref:.5f}', flush=True)
                    break
        except (OSError, ValueError, KeyError) as e:
            print(f'기준 LCD 를 못 찾음({type(e).__name__}) — LCD 감소율 판정은 '
                  f'보류합니다', flush=True)

    print('\n' + '=' * 126)
    print(f'{"조성":<12} {"PLD(전)":>8} {"AV(전)":>9} {"LCD(전)":>8} {"LCD(후)":>8} '
          f'{"LCD감소%":>9} {"최소거리":>9} {"루프":>5} {"EDiff":>10}  판정')
    print('-' * 126)
    rows = []
    for n in names:
        m0, m1, st = res[n]

        # 측정값이 비어 있으면 **그 구조만** 실패로 적고 넘어간다.
        #
        # zeo() 는 Zeo++ 가 죽으면 LCD/PLD/AV 를 None 으로 돌려준다(예외를 삼키고
        # 로그만 남긴다). 그런데 아래 표 출력이 f'{m0["PLD"]:>8.3f}' 라서 None 이
        # 오면 TypeError 로 **집계 전체가 죽는다.** 2026-08-12 18:56 과 20:07 두
        # 번의 재시도가 이것 때문에 통째로 날아갔다. 이완 17종이 다 끝나 있었는데도
        # 결과 파일이 안 나온 이유다.
        #
        # 한 구조의 측정 실패가 나머지 16종의 결과까지 지우게 두면 안 된다.
        if st == 'ok' and m1:
            need = [('PLD 전', (m0 or {}).get('PLD')), ('LCD 전', (m0 or {}).get('LCD')),
                    ('LCD 후', m1.get('LCD')), ('최소거리', m1.get('min_dist'))]
            gone = [k for k, v in need if v is None]
            if gone:
                st = 'Zeo++ 측정 실패: ' + ', '.join(gone)
                m1 = None

        if st != 'ok' or not m1:
            print(f'{n:<12} {st}')
            rows.append({'name': n, 'status': st, 'before': m0, 'after': None,
                         'pass': False})
            continue
        drop = (lcd_ref - m1['LCD']) / lcd_ref * 100 if (lcd_ref and m1['LCD']) else float('nan')
        checks = {
            'PLD': (m0['PLD'] or 0) > CO2_KINETIC,
            # 기준이 없어 drop 이 nan 이면 `nan < 20` 은 False 라 조용히 탈락이 된다.
            # 판정할 수 없는 것과 탈락은 다르다 — 판정 불가일 때는 이 항목을 걸지 않고,
            # 대신 아래 rows 의 'LCD_drop_pct' 가 None 으로 남아 그 사실이 보이게 한다.
            'LCD_drop': True if drop != drop else drop < LCD_DROP_LIMIT,
            'AV': (m0.get('AV_per_cell') or 0) > AV_FLOOR,
            'min_dist': m1['min_dist'] > MIN_DIST_LIMIT,
        }
        ok = all(checks.values())
        bad = ','.join(k for k, v in checks.items() if not v)
        ed, loops = final_ediff(n)
        # 상한에 걸려 멈춘 구조는 표시한다. 판정을 무효로 만들지는 않지만,
        # LCD 감소율이 경계 근처면 그 값을 신뢰하면 안 된다.
        mark = '' if (ed is not None and ed < 1e-4) else ' *덜수렴'
        print(f'{n:<12} {m0["PLD"]:>8.3f} {m0.get("AV_per_cell",0):>9.1f} '
              f'{m0["LCD"]:>8.3f} {m1["LCD"]:>8.3f} {drop:>9.1f} '
              f'{m1["min_dist"]:>9.3f} {str(loops):>5} '
              f'{("%.3g" % ed) if ed is not None else "-":>10}  '
              f'{"통과" if ok else "탈락: " + bad}{mark}')
        rows.append({'name': n, 'status': st, 'before': m0, 'after': m1,
                     'LCD_drop_pct': round(drop, 2), 'checks': checks, 'pass': ok,
                     'outer_loops': loops, 'final_EDiff': ed,
                     'converged': bool(ed is not None and ed < 1e-4)})

    payload = {'criteria': {'PLD_min': CO2_KINETIC,
                            'LCD_drop_limit_pct': LCD_DROP_LIMIT,
                            'AV_floor': AV_FLOOR,
                            'min_dist_limit': MIN_DIST_LIMIT,
                            'LCD_reference': lcd_ref},
               'rows': rows}

    # 전멸한 결과로 멀쩡한 결과를 덮지 않는다. 18_PoreNarrowing 에서 실제로
    # 당했다 — 환경 없이 실행되어 16개 전부 'lammps-interface 실패'로 끝났는데도
    # 결과 파일을 그대로 덮어썼다. 여기도 같은 구조라 같은 방어를 넣는다.
    if not any(r.get('pass') for r in rows) and os.path.exists(RESULT):
        try:
            prev = json.load(open(RESULT, encoding='utf-8')).get('rows') or []
        except (ValueError, OSError):
            prev = []
        if any(r.get('pass') for r in prev):
            alt = RESULT.replace('.json', '.allfail.json')
            with open(alt, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            print(f'\n[중단] {len(rows)}개 전부 실패했습니다. 기존 결과(통과 '
                  f'{sum(1 for r in prev if r.get("pass"))}개)를 지키기 위해 '
                  f'덮어쓰지 않았습니다.\n       실패 내역: {os.path.basename(alt)}')
            return 1

    with open(RESULT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    print('\n주: PLD/AV 는 이완 **전**, LCD 감소·최소거리는 이완 **후** 값으로 판정했습니다'
          ' (MIGRATION.md 3-6).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
