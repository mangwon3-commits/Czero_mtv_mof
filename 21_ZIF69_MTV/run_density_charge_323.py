"""전하 ON/OFF CO2 밀도 격자 323 K판 — 본선 포스터 Figure 3(Zn-BDT −Br*, LJ만 vs LJ + 전하)을 323 K로 맞추기 위한 실행기 (2026-11-16).

`run_density_e24i.py`(E-28e, density_v3_tpl4 를 만든 실행기)와 같은 방식으로 `run_density_map` 을 **수정 없이** import 하고
모듈 전역만 바꿉니다. 바꾼 것은 둘뿐입니다.
  ① 온도 TEMP = 323.0 K (원판 298.0). 압력 0.15 bar · CO2 단성분 · 2,000 + 5,000 사이클 · 90³ 격자 · UFF_MOF · 12 Å ·
     DDEC6 전하(charged_v3) · 셀 규칙은 원판 그대로입니다. −Br* 는 원판도 막음(BlockPockets) 없이 돌았으므로 막음 없음.
  ② 출력 폴더 density_v3_tpl4_323/ (298 K 폴더와 섞지 않음).
관문: 입력을 쓸 때마다 ExternalTemperature 323.0 · ExternalPressure 15000.0 이 정확히 한 번 있는지 확인하고, 아니면 RASPA 를 띄우지 않습니다.
완주 판정(Simulation finished 표지 · 적재 줄) · VTK gzip 은 원판 run_one 그대로입니다.

사용 (21_ZIF69_MTV 폴더에서, czeromof 환경):
    python run_density_charge_323.py                      # −Br* 전하 ON · OFF 2작업 동시
    python run_density_charge_323.py e24i_br_open e22_parent   # 모체도 같이(4작업)
    CHARGE323_DRY=1 python run_density_charge_323.py      # RASPA 없이 임시 폴더에 입력만 써서 확인
결과: density_v3_tpl4_323/<대상>__q_{on,off}/VTK/System_0/COMDensityProfile_CO2.vtk.gz · density_v3_tpl4_323/density_results.json
"""
import hashlib
import os
import sys
import tempfile

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
DRY = bool(os.environ.get('CHARGE323_DRY'))
OUTD = tempfile.mkdtemp(prefix='charge323_dry_') if DRY else os.path.join(REAL, 'density_v3_tpl4_323')
CIF_MD5 = {'e24i_br_open': '4015ec2d0cc2f00b5d9cf1040df7b26c', 'e22_parent': 'f15ce100dbbaa49714fdb2e5dabfe9ff'}
RD_MD5 = '56c591c508e3505d6b75dc8995c5fc46'


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


rd.TEMP = 323.0
rd.HERE = OUTD
rd.OUT = OUTD
rd.CHARGED = os.path.join(REAL, 'charged_v3')
rd.TARGETS = sys.argv[1:] or ['e24i_br_open']
rd.MAX_WORKERS = int(os.environ.get('CHARGE323_WORKERS', str(2 * len(rd.TARGETS))))
_real_write = rd.write_input


def write_input(d, name, na, nb, nc, charges):
    _real_write(d, name, na, nb, nc, charges)
    s = open(os.path.join(d, 'simulation.input')).read()
    lines = s.splitlines()
    t = [l for l in lines if l.split()[:1] == ['ExternalTemperature']]
    p = [l for l in lines if l.split()[:1] == ['ExternalPressure']]
    q = [l for l in lines if l.split()[:1] == ['UseChargesFromCIFFile']]
    ok = (len(t) == 1 and float(t[0].split()[1]) == 323.0 and len(p) == 1 and float(p[0].split()[1]) == 15000.0
          and len(q) == 1 and q[0].split()[1] == ('yes' if charges else 'no'))
    if not ok:
        raise SystemExit(f'  !! 입력 관문 실패 {d}: {t} {p} {q} — RASPA 안 띄움')
    if DRY:
        print(f'--- {d}/simulation.input ---\n{s}', flush=True)
        raise SystemExit(0)


rd.write_input = write_input

if __name__ == '__main__':
    if md5(rd.__file__) != RD_MD5:
        sys.exit(f'  !! run_density_map.py md5 {md5(rd.__file__)} ≠ {RD_MD5} — 착수 안 함')
    for t in rd.TARGETS:
        if t not in CIF_MD5:
            sys.exit(f'  !! 등록 대상이 아님: {t} (가능: {list(CIF_MD5)})')
        cif = os.path.join(rd.CHARGED, t + '_DDEC6.cif')
        if not os.path.exists(cif) or md5(cif) != CIF_MD5[t]:
            sys.exit(f'  !! 전하 CIF 없음 또는 md5 불일치: {cif}')
    os.makedirs(OUTD, exist_ok=True)
    if DRY:
        rd.run_one((rd.TARGETS[0], False))
    print(f'전하 ON/OFF CO2 밀도 격자 323 K — 대상 {rd.TARGETS} · 작업 {2 * len(rd.TARGETS)} · 동시 {rd.MAX_WORKERS} · 결과 {OUTD}', flush=True)
    print('  (아래 원판 안내문의 "298 K" 글자는 원판 문구일 뿐, 입력 온도는 위 관문이 323.0 으로 확인합니다)', flush=True)
    sys.exit(rd.main())
