# -*- coding: utf-8 -*-
"""MAGI-007 R1 (Melchior · 랩탑) 재현 스크립트 — R1 의 [산술] · [전문](행 직접 읽음) 수를 결과 파일에서 다시 냅니다.
입력은 전부 git 객체(origin/master f589c08b 이후)에서 `git show` 로 읽으므로 작업 트리와 무관합니다.
쓰는 법: python3 repro_r1_laptop.py <저장소 경로> [<참조, 기본 refs/remotes/origin/master>]
"""
import hashlib, json, math, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else '.'
REF = sys.argv[2] if len(sys.argv) > 2 else 'refs/remotes/origin/master'


def show(path):
    b = subprocess.run(['git', '-C', REPO, 'show', f'{REF}:{path}'], check=True, capture_output=True).stdout
    return b, hashlib.md5(b).hexdigest()[:8]


def rows(d):
    r = d.get('rows', d)
    return list(r.items()) if isinstance(r, dict) else list(enumerate(r))


print('ref', subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', REF], capture_output=True, text=True).stdout.strip())

# M-9 · §1-3: 모체 323 K 세 반복과 323/298 비
b, m = show('21_ZIF69_MTV/results_e27_mix323_laptop.json'); d = json.loads(b)
par = [r['S_mix'] for _, r in rows(d) if str(r.get('name', '')).startswith('e22_parent_s')]
mean323 = sum(par) / len(par); S298 = 75.43
ratio = mean323 / S298
print(f'[E-27 md5 {m}] 모체 323 K = {[round(x, 2) for x in par]} → 평균 {mean323:.2f} · 비 {ratio:.3f} (298 K 순위표 {S298})')

# M-10: 헨리 근사로 ΔQ 와 열린 자리 비
R = 8.314; f = 1 / 298 - 1 / 323
dQ = -math.log(ratio) / f * R / 1000
print(f'ΔQ(CO2−N2) 맞춤 = {dQ:.2f} kJ/mol')
for k, q in (('CN', 36.0), ('Br', 36.5), ('Cl', 35.9), ('CH3', 36.6), ('C2H5', 36.8)):
    print(f'  {k:5s} Q_st {q} → 비 {math.exp(-(dQ + q - 34.8) * 1000 / R * f):.3f}')
for k, s298 in (('CN', 139.8), ('Br', 127.9)):
    print(f'  {k} S_mix(323) 범위 0.60~0.66 × {s298} = {0.60 * s298:.1f}~{0.66 * s298:.1f}')

# M-7: UFF4MOF 상한 300 이완본의 PLD · AV
b, m = show('21_ZIF69_MTV/results_e24i_relax300_laptop.json'); d = json.loads(b)
for _, r in rows(d):
    nm = r.get('name') or r.get('tag') or r.get('chan_before', {}).get('chan_file_head', ['?'])[0].split('/')[-2]
    print(f"[relax300 md5 {m}] {nm:18s} PLD {r['before']['PLD']:.3f} → {r['after']['PLD']:.3f} · AV/셀 {r['after'].get('AV_per_cell')} · 루프 {r.get('outer_loops')}")

# §4 쓸 수 없는 문장 3: E-27b C2H5 의 CIF
b, m = show('21_ZIF69_MTV/results_e27b_mix323_c2h5_hkhome.json'); d = json.loads(b)
for _, r in rows(d):
    print(f"[E-27b md5 {m}] {r.get('name')} S_mix {r.get('S_mix'):.2f} · CIF {r.get('cif')}")

# §4 쓸 수 있는 문장 1: 순위표 판 비
print(f'CN/모체 {139.8 / 75.4:.3f} · CN/mslm050 {139.8 / 39.71:.3f} · Br/mslm050 {127.9 / 39.71:.3f} · 모체/mslm050 {75.4 / 39.71:.3f}')
