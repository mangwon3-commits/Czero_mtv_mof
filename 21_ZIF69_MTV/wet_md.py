"""물을 넣은 유연 골격 MD — SO3H 가 골격을 기계적으로 무너뜨리는가.

[왜 이 계산이 필요한가 — HYDROLYSIS.md 1절]
    지금까지 한 두 계산은 이 질문에 답할 수 없는 설계였다.
      * run_water.py 수분 경쟁 GCMC — 물은 있지만 골격이 **강체**다.
        붕괴가 안 일어나는 게 아니라 일어날 수가 없다.
      * risk_screen.py UFF4MOF 이완 — 골격은 유연하지만 **물이 한 분자도 없고**
        0 K 최소화다.
    물이 있으면서 동시에 골격이 움직이는 계산을 한 번도 안 했다. 이게 그것이다.

[문헌(1단계)이 판정불능이라 여기로 왔다 — HYDROLYSIS.md 5절]
    gme 계열 수분 안정성 보고가 정면 충돌하고(끓는 물 7일 생존 vs 상온 물에서도
    비가역 손상), 둘 다 **액상 침지**라 우리 수증기 조건에 못 쓴다. 술폰산 관능화
    ZIF 의 직접 데이터는 없다.

[이 계산이 답할 수 있는 것 / 없는 것 — 반드시 같이 읽어야 한다]
    UFF4MOF 는 **결합 토폴로지가 고정된 결합형 힘장**이다. Zn-N 이 조화 용수철이라
    늘어날 수는 있어도 **끊어질 수 없다.** 그래서
      * 답할 수 있음 — 물이 유발하는 **기계적/용매화 변형**으로 기공이 무너지는가
      * 답할 수 있음 — 물이 Zn-N 배위를 **얼마나 늘리는가**(가수분해의 전조)
      * 답할 수 없음 — 가수분해 그 자체. 술폰산 해리도 고정 전하라 표현 안 된다
    즉 여기서 '통과'는 **"물이 기계적으로는 못 무너뜨린다"** 까지이고, 절대
    "가수분해하지 않는다" 가 아니다. 그건 3단계(DFT) 몫이다.

[설계 — 건조 대조군이 핵심이다]
    같은 조성을 건조/습윤 두 번 돌린다. 이게 없으면 LCD 변화가 물 때문인지
    그냥 0 K -> 298 K 때문인지 구별할 수 없다. 판정은 **습윤 vs 건조 차이**로 한다.

[물 모델 — GCMC 와 다르다. 알고 쓰는 것이다]
    GCMC 는 5사이트(TIP5P-Ew)를 썼지만 여기서는 SPC/E(3사이트)를 쓴다. LAMMPS 에서
    더미 사이트를 UFF4MOF 혼성 스타일에 섞는 비용이 크고, **기계적 변형을 보는
    계산이라 쌍극자 세부는 2차 효과**이기 때문이다. 이 차이는 한계로 기록한다.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# [중요] risk_screen.py 의 lmp/ 를 재사용하지 **않는다.**
#
# 그쪽은 structures/*.cif 에서 만들어졌고, 그 CIF 의 전하는 빌더가 붙인 QEq 계열이다
# (Zn +1.19). 반면 이 프로젝트의 모든 GCMC 는 charged/*_DDEC6.cif 의 PACMAN/DDEC6
# 전하(Zn +0.668)로 돌았다. 물-술폰산 상호작용은 정전기가 지배하므로, λ 를 만들어 준
# 계산과 다른 전하로 MD 를 돌리면 두 결과를 나란히 놓을 수 없다.
#
# 게다가 05_MTV_Ligand_Library/ZIF69_base.cif 는 전하가 **전부 0** 이라, 거기서 나온
# lmp/base 로는 kspace 가 아예 안 돈다("Must use kspace_modify gewald for uncharged
# system"). 대조군만 정전기가 없는 비교는 비교가 아니다.
CHARGED = os.path.join(HERE, 'charged')
IFACE = os.path.join(HERE, '..', '18_PoreNarrowing', 'lammps_iface_patched.py')
WORK = os.path.join(HERE, 'wetmd')
RESULT = os.path.join(HERE, 'wet_md_results.json')
WATER_JSON = os.path.join(HERE, 'water_results.json')

LMP = shutil.which('lmp_serial') or os.path.expanduser(
    '~/miniconda3/envs/lammps_mof/bin/lmp_serial')
# Zeo++ 는 czeromof 에만 있다. PATH 에 없으면 조용히 실패해 LCD/PLD 가 0 이 된다
# (MIGRATION.md 3-1). risk_screen.py 와 같은 방식으로 절대경로를 잡는다.
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')

# [2026-08-14] 대상이 base 와 saIm025 **뿐**인 이유 — STRUCTURE_DEFECT.md 참조.
#
# 원래 base/saIm050/saIm075/saIm100 을 돌리려 했다. 그런데 계를 조립하다가
# 황 하나에 결합이 5개씩 붙는 것을 보고 원 구조를 뒤졌더니, saIm050/075/100 에서
# **인접한 두 술폰산기가 서로 관통해 있었다** (S-S 2.642 A, O-O 0.924 A).
# 겹친 쌍이 조성별로 0/2/3/6 개다. saIm025 만 깨끗하다.
#
# 겹친 구조로 MD 를 돌리면 답처럼 보이는 숫자가 나오지만 답이 아니다. 그래서
# 깨끗한 두 구조로만 돌린다. 나머지는 구조를 다시 만든 뒤에 판단한다.
#
# saIm025 로도 질문에는 답할 수 있다. 물/SO3H 비가 RH90 에서 1.50 으로
# saIm100 의 1.46 과 같기 때문이다(HYDROLYSIS.md 2절) — 술폰산 하나가 보는
# 물의 환경은 같고, 밀도만 낮다.
NAMES = [n for n in (sys.argv[1:] or ['base', 'saIm025'])]
RH = 0.90                 # 최악 조건. 여기서 안 무너지면 아래는 볼 것도 없다
TEMP = 298.0
PRESS = 1.0               # atm
DT = 0.5                  # fs. 골격 C-H 를 안 묶었으므로 1 fs 는 위험하다
NS_PUSH = 10000           # nve/limit 겹침 완화 (5 ps)
NS_NVT = 100000           # NVT 평형 (50 ps)
NS_NPT = 500000           # NPT 생산 (250 ps)
DUMP_EVERY = 10000        # 5 ps

# SPC/E
Q_OW, Q_HW = -0.8476, 0.4238
EPS_OW, SIG_OW = 0.1553, 3.166
R_OH, ANG_HOH = 1.0, 109.47
M_OW, M_HW = 15.9994, 1.00794

# 배치 시 겹침 기준 (A). 사면체 SO3 에 물을 수소결합 거리로 붙이므로
# 골격까지 2.4 는 허용한다. 그 아래는 최소화가 감당 못 한다.
D_FRAME_MIN = 2.40
D_WAT_MIN = 2.70

# 사전 등록 판정 기준 — **계산 전에 정한다.** risk_screen.py 와 같은 잣대를 쓰되,
# 기준선을 '모체'가 아니라 '같은 조성의 건조 MD' 로 바꾼다. 물의 효과만 보려면
# 그래야 한다.
LCD_DROP_LIMIT = 20.0     # 습윤 LCD 가 건조 대비 20% 이상 줄면 붕괴
PLD_MIN = 3.3             # CO2 운동직경
ZN_N_STRETCH_LIMIT = 5.0  # 평균 Zn-N 거리가 건조 대비 5% 이상 늘면 배위 약화 신호
MIN_DIST_LIMIT = 0.7


# ---------------------------------------------------------------- 데이터 파일

SECTIONS = ('Masses', 'Pair Coeffs', 'Bond Coeffs', 'Angle Coeffs',
            'Dihedral Coeffs', 'Improper Coeffs', 'Atoms', 'Velocities',
            'Bonds', 'Angles', 'Dihedrals', 'Impropers')


def read_data(path):
    """lammps-interface 가 뱉은 data 파일을 절로 쪼갠다."""
    lines = open(path, encoding='utf-8').read().splitlines()
    head, sec, cur = [], {}, None
    for ln in lines:
        s = ln.strip()
        key = s.split('#')[0].strip()
        if key in SECTIONS:
            cur = key
            sec[cur] = []
            continue
        if cur is None:
            head.append(ln)
        elif s:
            sec[cur].append(ln)
    counts, box = {}, {}
    for ln in head:
        m = re.match(r'\s*(\d+)\s+(atoms|bonds|angles|dihedrals|impropers)\s*$', ln)
        if m:
            counts[m.group(2)] = int(m.group(1))
        m = re.match(r'\s*(\d+)\s+(atom|bond|angle|dihedral|improper) types\s*$', ln)
        if m:
            counts[m.group(2) + ' types'] = int(m.group(1))
        m = re.match(r'\s*(-?[\d.eE+]+)\s+(-?[\d.eE+]+)\s+([xyz])lo \3hi\s*$', ln)
        if m:
            box[m.group(3)] = (float(m.group(1)), float(m.group(2)))
        m = re.match(r'\s*(-?[\d.eE+]+)\s+(-?[\d.eE+]+)\s+(-?[\d.eE+]+)\s+xy xz yz\s*$', ln)
        if m:
            box['tilt'] = tuple(float(m.group(i)) for i in (1, 2, 3))
    return counts, box, sec


def atoms_array(sec):
    """Atoms 절 -> (id, mol, type, q, x, y, z). atom_style full."""
    rows = []
    for ln in sec['Atoms']:
        f = ln.split('#')[0].split()
        rows.append((int(f[0]), int(f[1]), int(f[2]), float(f[3]),
                     float(f[4]), float(f[5]), float(f[6])))
    rows.sort()
    return rows


def cell_matrix(box):
    """LAMMPS 삼사정계 -> 3x3 셀 행렬."""
    lx = box['x'][1] - box['x'][0]
    ly = box['y'][1] - box['y'][0]
    lz = box['z'][1] - box['z'][0]
    xy, xz, yz = box.get('tilt', (0.0, 0.0, 0.0))
    return np.array([[lx, 0.0, 0.0], [xy, ly, 0.0], [xz, yz, lz]])


# ---------------------------------------------------------------- 물 배치

def sulfonate_sites(counts, sec, rows):
    """S 에 결합한 산소 목록. 물을 여기에 수소결합 거리로 붙인다.

    GCMC 가 말한 것이 바로 이것이다 — 물/SO3H 비가 조성과 무관하게 1.3~1.5 로
    일정했다(HYDROLYSIS.md 2절). 물이 기공을 채우는 게 아니라 술폰산에 앉는다.
    무작위로 뿌리면 우리 자신의 GCMC 결과와 어긋난 배치가 된다.
    """
    mass = {}
    for ln in sec['Masses']:
        f = ln.split('#')[0].split()
        mass[int(f[0])] = float(f[1])
    s_types = {t for t, m in mass.items() if abs(m - 32.065) < 0.5}
    o_types = {t for t, m in mass.items() if abs(m - 15.9994) < 0.5}
    if not s_types:
        return []
    pos = {r[0]: np.array(r[4:7]) for r in rows}
    typ = {r[0]: r[2] for r in rows}
    sites = []
    for ln in sec['Bonds']:
        f = ln.split('#')[0].split()
        a, b = int(f[2]), int(f[3])
        for i, j in ((a, b), (b, a)):
            if typ[i] in s_types and typ[j] in o_types:
                sites.append((j, i))   # (산소, 황)
    return sites


def place_water(rows, sites, n_want, cell, rng):
    """물 n_want 개를 배치한다. 술폰산 산소 근처를 먼저 채우고 나머지는 기공에.

    주기경계를 최소이미지로 다룬다. 실패하면 배치한 만큼만 돌려주고, 호출부가
    실제 개수를 결과에 남긴다 — 원하는 수를 못 채운 것을 조용히 넘기면 안 된다.
    """
    inv = np.linalg.inv(cell)
    frame = np.array([r[4:7] for r in rows])

    def mic(d):
        f = d @ inv
        f -= np.round(f)
        return f @ cell

    def clash(p, others, dmin):
        if len(others) == 0:
            return False
        d = mic(np.asarray(others) - p)
        return bool((np.einsum('ij,ij->i', d, d) < dmin * dmin).any())

    placed = []          # 물 산소 좌표
    mols = []            # (O, H1, H2)

    def add(o_pos):
        if clash(o_pos, frame, D_FRAME_MIN) or clash(o_pos, placed, D_WAT_MIN):
            return False
        # 임의 방향으로 H 두 개. 각 109.47도, 길이 1.0 A.
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        w = rng.normal(size=3)
        w -= w.dot(v) * v
        w /= np.linalg.norm(w)
        half = math.radians(ANG_HOH) / 2
        h1 = o_pos + R_OH * (math.cos(half) * v + math.sin(half) * w)
        h2 = o_pos + R_OH * (math.cos(half) * v - math.sin(half) * w)
        placed.append(o_pos)
        mols.append((o_pos, h1, h2))
        return True

    pos = {r[0]: np.array(r[4:7]) for r in rows}
    order = list(range(len(sites)))
    rng.shuffle(order)
    for k in order:
        if len(mols) >= n_want:
            break
        o_id, s_id = sites[k]
        d = mic(pos[o_id] - pos[s_id])
        d /= np.linalg.norm(d)
        for _ in range(12):        # 방향을 흔들어 가며 시도
            j = rng.normal(size=3) * 0.35
            u = d + j
            u /= np.linalg.norm(u)
            if add(pos[o_id] + 2.75 * u):
                break

    tries = 0
    while len(mols) < n_want and tries < n_want * 400:
        tries += 1
        f = rng.random(3)
        add(f @ cell)
    return mols


# ---------------------------------------------------------------- 계 조립

def ensure_framework(name, d):
    """charged/<name>_DDEC6.cif -> UFF4MOF LAMMPS data 파일.

    risk_screen.py 와 같은 래퍼를 쓴다(S_3 -> S_3+6 타이핑, 축퇴 이면각 제거).
    여기서는 이완을 돌리지 않고 data 파일만 받아 간다 — 이완은 MD 가 대신한다.
    """
    stem = f'{name}_DDEC6'
    out = os.path.join(d, f'data.{stem}')
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out, None
    cif = os.path.join(CHARGED, f'{stem}.cif')
    if not os.path.exists(cif):
        return None, f'전하 CIF 없음: {cif}'
    shutil.copy(cif, os.path.join(d, f'{stem}.cif'))
    # `python` 이 아니라 sys.executable 을 쓴다. 환경을 activate 하지 않고 절대경로로
    # 인터프리터를 부르면 /bin/sh 의 PATH 에 python 이 없어 조용히 실패한다.
    r = subprocess.run(f'yes | {sys.executable} {IFACE} -ff UFF4MOF '
                       f'--minimize {stem}.cif',
                       shell=True, cwd=d, capture_output=True, text=True,
                       timeout=3600)
    if not os.path.exists(out):
        return None, ('lammps-interface 실패: '
                      + (r.stderr or r.stdout or '')[-200:].replace('\n', ' '))
    # 술폰산 계열에서 lammps-interface 가 같은 원자를 두 번 넣은 이면각을 만든다
    # (risk_screen.py 240행 주석). 정의가 성립하지 않는 항이라 제거해도 왜곡이 없다.
    sys.path.insert(0, os.path.dirname(os.path.abspath(IFACE)))
    try:
        from lammps_iface_patched import clean_degenerate_topology
        clean_degenerate_topology(out)
    except Exception as e:
        print(f'    {name}: 토폴로지 정리 실패 {type(e).__name__}', flush=True)
    return out, None


def build(name, wet, d, rng):
    src, err = ensure_framework(name, d)
    if err:
        return None, err
    counts, box, sec = read_data(src)
    rows = atoms_array(sec)
    cell = cell_matrix(box)

    n_at = counts['atoms']
    nt_at, nt_b, nt_a = counts['atom types'], counts['bond types'], counts['angle types']
    ow_t, hw_t, b_t, a_t = nt_at + 1, nt_at + 2, nt_b + 1, nt_a + 1

    mols = []
    if wet:
        load = None
        for r in json.load(open(WATER_JSON, encoding='utf-8')):
            if r['name'] == name and abs(r['RH'] - RH) < 1e-6:
                load = r['H2O_molkg']
        if load is None:
            return None, f'{name} RH{int(RH*100)} 물 로딩을 water_results.json 에서 못 찾음'
        # 총 질량(g/mol) -> mol/kg 로딩을 분자 개수로 환산
        mass = {}
        for ln in sec['Masses']:
            f = ln.split('#')[0].split()
            mass[int(f[0])] = float(f[1])
        m_tot = sum(mass[r[2]] for r in rows)
        n_want = int(round(load * m_tot / 1000.0))
        sites = sulfonate_sites(counts, sec, rows)
        mols = place_water(rows, sites, n_want, cell, rng)
        if len(mols) < n_want:
            print(f'    [경고] {name}: 물 {n_want} 개 중 {len(mols)} 개만 배치됨',
                  flush=True)
        meta = {'n_water_target': n_want, 'n_water_placed': len(mols),
                'loading_molkg': load, 'n_so3h_sites': len(sites) // 3}
    else:
        meta = {'n_water_target': 0, 'n_water_placed': 0}

    # ---- 헤더
    nb, na = counts['bonds'], counts['angles']
    out = ['# ZIF-69 + water, UFF4MOF + SPC/E (wet_md.py)', '']
    out += [f'{n_at + 3 * len(mols)} atoms',
            f'{nb + 2 * len(mols)} bonds',
            f'{na + 1 * len(mols)} angles',
            f'{counts["dihedrals"]} dihedrals',
            f'{counts["impropers"]} impropers', '']
    out += [f'{nt_at + 2} atom types',
            f'{nt_b + 1} bond types',
            f'{nt_a + 1} angle types',
            f'{counts["dihedral types"]} dihedral types',
            f'{counts["improper types"]} improper types', '']
    for ax in 'xyz':
        out.append(f'{box[ax][0]:.6f} {box[ax][1]:.6f} {ax}lo {ax}hi')
    if 'tilt' in box:
        out.append('%.6f %.6f %.6f xy xz yz' % box['tilt'])
    out.append('')

    def sect(tag, body):
        out.append(tag)
        out.append('')
        out.extend(body)
        out.append('')

    sect('Masses', sec['Masses'] + [f'{ow_t} {M_OW} # Ow',
                                    f'{hw_t} {M_HW} # Hw'])
    sect('Pair Coeffs', sec['Pair Coeffs'] +
         [f'{ow_t} {EPS_OW} {SIG_OW} # Ow', f'{hw_t} 0.0 0.0 # Hw'])
    # shake 로 묶으므로 상수 자체는 판정에 영향이 없다. 묶기 전 최소화에서만 쓰인다.
    sect('Bond Coeffs', sec['Bond Coeffs'] + [f'{b_t} 553.0 {R_OH} # Ow Hw'])
    sect('Angle Coeffs', sec['Angle Coeffs'] +
         [f'{a_t} harmonic 100.0 {ANG_HOH} # Hw Ow Hw'])
    sect('Dihedral Coeffs', sec['Dihedral Coeffs'])
    sect('Improper Coeffs', sec['Improper Coeffs'])

    n_mol_max = max(r[1] for r in rows)
    atoms = list(sec['Atoms'])
    bonds = list(sec['Bonds'])
    angles = list(sec['Angles'])
    aid, bid, gid = n_at, nb, na
    for k, (o, h1, h2) in enumerate(mols):
        mid = n_mol_max + 1 + k
        o_i, h1_i, h2_i = aid + 1, aid + 2, aid + 3
        aid += 3
        atoms.append(f'{o_i} {mid} {ow_t} {Q_OW:.4f} {o[0]:.5f} {o[1]:.5f} {o[2]:.5f}')
        atoms.append(f'{h1_i} {mid} {hw_t} {Q_HW:.4f} {h1[0]:.5f} {h1[1]:.5f} {h1[2]:.5f}')
        atoms.append(f'{h2_i} {mid} {hw_t} {Q_HW:.4f} {h2[0]:.5f} {h2[1]:.5f} {h2[2]:.5f}')
        bonds.append(f'{bid + 1} {b_t} {o_i} {h1_i}')
        bonds.append(f'{bid + 2} {b_t} {o_i} {h2_i}')
        bid += 2
        angles.append(f'{gid + 1} {a_t} {h1_i} {o_i} {h2_i}')
        gid += 1

    sect('Atoms', atoms)
    sect('Bonds', bonds)
    sect('Angles', angles)
    sect('Dihedrals', sec['Dihedrals'])
    sect('Impropers', sec['Impropers'])

    path = os.path.join(d, 'data.sys')
    open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    meta.update({'n_framework_atoms': n_at, 'ow_type': ow_t, 'hw_type': hw_t,
                 'bond_type': b_t, 'angle_type': a_t,
                 'charges': 'PACMAN/DDEC6 (GCMC 와 동일)'})
    return meta, None


def write_input(name, wet, d, meta):
    shake = (f'fix wsh water shake 1.0e-6 200 0 b {meta["bond_type"]} '
             f'a {meta["angle_type"]}') if meta['n_water_placed'] else ''
    # 건조 계에는 물 그룹이 없다. `group frame all` 은 LAMMPS 문법이 아니므로
    # (all 은 키워드가 아니라 미리 정의된 그룹) 건조에서는 그냥 all 을 쓴다.
    if meta['n_water_placed']:
        grp = (f'group water type {meta["ow_type"]} {meta["hw_type"]}\n'
               f'group frame subtract all water')
        dump_grp = 'frame'
    else:
        grp = ''
        dump_grp = 'all'
    txt = f"""log log.sys
units           real
atom_style      full
boundary        p p p

pair_style      lj/cut/coul/long 12.5
bond_style      harmonic
angle_style     hybrid cosine/periodic fourier harmonic
dihedral_style  harmonic
improper_style  fourier

dielectric      1.0
special_bonds   lj/coul 0.0 0.0 1.0
pair_modify     tail yes mix arithmetic
box tilt        large
read_data       data.sys

# kspace 는 read_data **뒤**에 둔다. 삼사정계로 바뀐 뒤 다시 정의하지 않으면
# "Must redefine kspace_style after changing to triclinic box" 로 죽는다.
kspace_style    pppm 1.0e-4

{grp}

# 배치 겹침 제거. 물을 손으로 넣었으므로 이 단계 없이 적분하면 날아간다.
minimize        1.0e-4 1.0e-6 5000 50000

velocity        all create {TEMP} {abs(hash(name + str(wet))) % 90000 + 1000} dist gaussian
timestep        {DT}

# 1) 남은 국소 겹침을 변위 제한으로 흘려 보낸다 (shake 는 아직 걸지 않는다)
fix             p1 all nve/limit 0.05
fix             t1 all langevin {TEMP} {TEMP} 100.0 {abs(hash(name)) % 90000 + 1000}
run             {NS_PUSH}
unfix           p1
unfix           t1

# 2) NVT 평형. 여기서부터 물은 강체(SPC/E)로 묶는다.
{shake}
fix             nvt1 all nvt temp {TEMP} {TEMP} 100.0
thermo          5000
thermo_style    custom step temp press pe ke lx ly lz vol
run             {NS_NVT}
unfix           nvt1

# 3) NPT 생산. 삼사정계이므로 tri 로 셀 전체를 푼다.
reset_timestep  0
fix             npt1 all npt temp {TEMP} {TEMP} 100.0 tri {PRESS} {PRESS} 1000.0
dump            dmp {dump_grp} custom {DUMP_EVERY} dump.frame id type xu yu zu
dump_modify     dmp sort id
run             {NS_NPT}

write_data      final.data nocoeff
"""
    open(os.path.join(d, 'in.sys'), 'w', encoding='utf-8').write(txt)


# ---------------------------------------------------------------- 측정

def frame_cif(final_data, meta, out_cif):
    """final.data 에서 **골격만** 떼어 CIF 로 쓴다. 물이 섞이면 Zeo++ 가
    물을 벽으로 세어 PLD/LCD 를 엉뚱하게 준다."""
    counts, box, sec = read_data(final_data)
    rows = atoms_array(sec)
    nf = meta['n_framework_atoms']
    mass = {}
    for ln in sec['Masses']:
        f = ln.split('#')[0].split()
        mass[int(f[0])] = float(f[1])
    sym = {}
    for ln in sec['Masses']:
        f = ln.split('#')
        t = int(f[0].split()[0])
        sym[t] = (f[1].strip().rstrip('0123456789+f') if len(f) > 1 else 'C')
    cell = cell_matrix(box)
    inv = np.linalg.inv(cell)
    a, b, c = (np.linalg.norm(cell[i]) for i in range(3))
    al = math.degrees(math.acos(cell[1].dot(cell[2]) / (b * c)))
    be = math.degrees(math.acos(cell[0].dot(cell[2]) / (a * c)))
    ga = math.degrees(math.acos(cell[0].dot(cell[1]) / (a * b)))

    def elem(t):
        m = mass[t]
        for e, mm in (('Zn', 65.38), ('S', 32.065), ('O', 15.9994),
                      ('N', 14.0067), ('C', 12.0107), ('Cl', 35.45), ('H', 1.00794)):
            if abs(m - mm) < 0.4:
                return e
        return 'C'

    L = ['data_frame', f'_cell_length_a {a:.5f}', f'_cell_length_b {b:.5f}',
         f'_cell_length_c {c:.5f}', f'_cell_angle_alpha {al:.4f}',
         f'_cell_angle_beta {be:.4f}', f'_cell_angle_gamma {ga:.4f}',
         "_symmetry_space_group_name_H-M 'P 1'", '_symmetry_Int_Tables_number 1',
         'loop_', '_symmetry_equiv_pos_as_xyz', "  'x, y, z'",
         'loop_', '_atom_site_label', '_atom_site_type_symbol',
         '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z']
    n = 0
    for r in rows:
        if r[0] > nf:
            continue
        n += 1
        e = elem(r[2])
        f = np.array(r[4:7]) @ inv
        f -= np.floor(f)
        L.append(f'{e}{n} {e} {f[0]:.6f} {f[1]:.6f} {f[2]:.6f}')
    open(out_cif, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return {'a': a, 'b': b, 'c': c, 'volume': float(abs(np.linalg.det(cell)))}


def zeo(cif, d):
    out = {'LCD': None, 'PLD': None}
    try:
        subprocess.run([NETWORK, '-ha', '-res', cif + '.res', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        v = open(cif + '.res').readline().split()
        out['LCD'], out['PLD'] = float(v[1]), float(v[2])
    except Exception as e:
        print(f'    [zeo 실패] {os.path.basename(cif)}: {type(e).__name__}', flush=True)
    return out


def zn_n_stats(final_data, meta):
    """Zn-N 배위 거리. **UFF 는 결합을 못 끊지만 늘어나는 것은 보인다.**

    가수분해의 전조를 고전 계산으로 잡을 수 있는 유일한 관측량이다. 물이 Zn 을
    끌어당기면 조화 용수철이 늘어나고, 그 평균이 건조 대비 커진다.
    """
    counts, box, sec = read_data(final_data)
    rows = atoms_array(sec)
    pos = {r[0]: np.array(r[4:7]) for r in rows}
    typ = {r[0]: r[2] for r in rows}
    mass = {}
    for ln in sec['Masses']:
        f = ln.split('#')[0].split()
        mass[int(f[0])] = float(f[1])
    zn = {t for t, m in mass.items() if abs(m - 65.38) < 0.5}
    nn = {t for t, m in mass.items() if abs(m - 14.0067) < 0.5}
    cell = cell_matrix(box)
    inv = np.linalg.inv(cell)
    ds = []
    for ln in sec['Bonds']:
        f = ln.split('#')[0].split()
        i, j = int(f[2]), int(f[3])
        if (typ[i] in zn and typ[j] in nn) or (typ[j] in zn and typ[i] in nn):
            d = pos[i] - pos[j]
            fr = d @ inv
            fr -= np.round(fr)
            ds.append(float(np.linalg.norm(fr @ cell)))
    if not ds:
        return {}
    ds = np.array(ds)
    return {'ZnN_mean': round(float(ds.mean()), 4),
            'ZnN_max': round(float(ds.max()), 4),
            'ZnN_n': len(ds)}


def min_dist(final_data, meta):
    counts, box, sec = read_data(final_data)
    rows = [r for r in atoms_array(sec) if r[0] <= meta['n_framework_atoms']]
    cell = cell_matrix(box)
    inv = np.linalg.inv(cell)
    p = np.array([r[4:7] for r in rows])
    # 전체 거리행렬은 만들지 않는다 (risk_screen.py geom() 과 같은 이유 — OOM).
    # 격자 셀로 잘라 이웃만 본다.
    best = 1e9
    fr = p @ inv
    fr -= np.floor(fr)
    grid = {}
    nb = 12
    for i, f in enumerate(fr):
        k = tuple((f * nb).astype(int) % nb)
        grid.setdefault(k, []).append(i)
    for k, idx in grid.items():
        near = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    near += grid.get(((k[0] + dx) % nb, (k[1] + dy) % nb,
                                      (k[2] + dz) % nb), [])
        for i in idx:
            for j in near:
                if j <= i:
                    continue
                d = fr[i] - fr[j]
                d -= np.round(d)
                r = float(np.linalg.norm(d @ cell))
                if r < best:
                    best = r
    return round(best, 3)


# ---------------------------------------------------------------- 실행

def run_one(job):
    name, wet = job
    tag = f'{name}_{"wet" if wet else "dry"}'
    d = os.path.join(WORK, tag)
    os.makedirs(d, exist_ok=True)
    rng = np.random.default_rng(abs(hash(tag)) % (2 ** 31))

    final = os.path.join(d, 'final.data')
    meta_p = os.path.join(d, 'meta.json')
    # 끝나 있으면 다시 돌리지 않는다 (risk_screen.py 와 같은 이유 — 이 계열은
    # 집계 단계에서 죽어 이완을 통째로 날린 전력이 있다).
    if os.path.exists(final) and os.path.getsize(final) > 0 and os.path.exists(meta_p):
        meta = json.load(open(meta_p, encoding='utf-8'))
        print(f'    {tag}: 기존 산출물 재사용', flush=True)
    else:
        meta, err = build(name, wet, d, rng)
        if err:
            return tag, name, wet, None, err
        json.dump(meta, open(meta_p, 'w', encoding='utf-8'), indent=1)
        write_input(name, wet, d, meta)
        try:
            subprocess.run([LMP, '-in', 'in.sys'], cwd=d,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=172800)
        except subprocess.TimeoutExpired:
            return tag, name, wet, None, 'LAMMPS 시간초과(48h)'
        if not os.path.exists(final):
            tail = ''
            lg = os.path.join(d, 'log.sys')
            if os.path.exists(lg):
                tail = open(lg, errors='ignore').read()[-400:].replace('\n', ' ')
            return tag, name, wet, None, f'LAMMPS 출력 없음: {tail}'

    cif = os.path.join(d, 'frame.cif')
    m = {'cell': frame_cif(final, meta, cif)}
    m.update(zeo(cif, d))
    m.update(zn_n_stats(final, meta))
    m['min_dist'] = min_dist(final, meta)
    m.update({k: meta.get(k) for k in
              ('n_water_target', 'n_water_placed', 'loading_molkg', 'n_so3h_sites')})
    return tag, name, wet, m, 'ok'


def main():
    os.makedirs(WORK, exist_ok=True)
    jobs = [(n, w) for n in NAMES for w in (False, True)]
    workers = int(os.environ.get('WETMD_WORKERS', '4'))
    print(f'{len(jobs)}작업 (건조/습윤 x {len(NAMES)}조성), 워커 {workers}, 작업 {WORK}\n',
          flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=workers, max_tasks_per_child=1) as ex:
        for tag, name, wet, m, st in ex.map(run_one, jobs):
            res[tag] = (name, wet, m, st)
            print(f'  [{st[:30]:>30}] {tag}', flush=True)

    print('\n' + '=' * 118)
    print(f'{"조성":<10} {"물":>5} {"LCD":>8} {"PLD":>8} {"LCD감소%":>9} '
          f'{"Zn-N평균":>9} {"신장%":>7} {"최소거리":>9} {"부피":>10}  판정')
    print('-' * 118)
    rows = []
    for n in NAMES:
        dry = res.get(f'{n}_dry', (None, None, None, 'x'))[2]
        for wet in (False, True):
            name, w, m, st = res.get(f'{n}_{"wet" if wet else "dry"}',
                                     (n, wet, None, 'missing'))
            if st != 'ok' or not m:
                print(f'{n:<10} {"습" if wet else "건":>5}  {st}')
                rows.append({'name': n, 'wet': wet, 'status': st, 'pass': None})
                continue
            drop = zns = float('nan')
            if wet and dry and dry.get('LCD') and m.get('LCD'):
                drop = (dry['LCD'] - m['LCD']) / dry['LCD'] * 100
            if wet and dry and dry.get('ZnN_mean') and m.get('ZnN_mean'):
                zns = (m['ZnN_mean'] - dry['ZnN_mean']) / dry['ZnN_mean'] * 100
            verdict = ''
            ok = None
            if wet:
                checks = {
                    'LCD_drop': True if drop != drop else drop < LCD_DROP_LIMIT,
                    'PLD': (m.get('PLD') or 0) > PLD_MIN,
                    'ZnN_stretch': True if zns != zns else zns < ZN_N_STRETCH_LIMIT,
                    'min_dist': (m.get('min_dist') or 0) > MIN_DIST_LIMIT,
                }
                ok = all(checks.values())
                bad = ','.join(k for k, v in checks.items() if not v)
                verdict = '통과' if ok else '탈락: ' + bad
            print(f'{n:<10} {"습" if wet else "건":>5} '
                  f'{m.get("LCD") or 0:>8.3f} {m.get("PLD") or 0:>8.3f} '
                  f'{drop:>9.1f} {m.get("ZnN_mean") or 0:>9.4f} {zns:>7.2f} '
                  f'{m.get("min_dist") or 0:>9.3f} '
                  f'{m["cell"]["volume"]:>10.0f}  {verdict}')
            r = {'name': n, 'wet': wet, 'status': st, 'pass': ok, **m}
            if wet:
                r['LCD_drop_vs_dry_pct'] = None if drop != drop else round(drop, 2)
                r['ZnN_stretch_vs_dry_pct'] = None if zns != zns else round(zns, 3)
            rows.append(r)

    payload = {
        'conditions': {'RH': RH, 'T_K': TEMP, 'P_atm': PRESS, 'dt_fs': DT,
                       'ns_push': NS_PUSH, 'ns_nvt': NS_NVT, 'ns_npt': NS_NPT,
                       'water_model': 'SPC/E (3-site)',
                       'framework_ff': 'UFF4MOF, bonded, topology fixed'},
        'criteria': {'LCD_drop_limit_pct': LCD_DROP_LIMIT, 'PLD_min': PLD_MIN,
                     'ZnN_stretch_limit_pct': ZN_N_STRETCH_LIMIT,
                     'min_dist_limit': MIN_DIST_LIMIT,
                     'baseline': '같은 조성의 건조 MD (모체가 아님)'},
        'caveat': ('결합형 힘장이라 Zn-N 이 끊어질 수 없다. 여기서 통과는 '
                   '"물이 기계적으로는 못 무너뜨린다" 까지이고, 가수분해를 '
                   '배제하지 않는다. HYDROLYSIS.md 6절 참조.'),
        'rows': rows}

    # 전멸한 결과로 멀쩡한 결과를 덮지 않는다 (risk_screen.py 와 같은 방어).
    if not any(r.get('status') == 'ok' for r in rows) and os.path.exists(RESULT):
        alt = RESULT.replace('.json', '.allfail.json')
        json.dump(payload, open(alt, 'w', encoding='utf-8'), indent=2,
                  ensure_ascii=False)
        print(f'\n[중단] 전부 실패. 기존 결과를 지켰습니다 -> {os.path.basename(alt)}')
        return 1

    json.dump(payload, open(RESULT, 'w', encoding='utf-8'), indent=2,
              ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    print('\n주: 판정 기준선은 모체가 아니라 **같은 조성의 건조 MD** 입니다.')
    print('    이 계산은 가수분해를 배제하지 못합니다 — 결합형 힘장이라 Zn-N 이 '
          '끊어질 수 없습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
