# -*- coding: utf-8 -*-
"""COREPOP-H323 — 메모리가 작은 기기(16 GB 호스트)용: 묶음에서 Zeo++ 막음이 그 기기 한도 안에 들 구조만 고름.
사용자 지시 2026-11-15 "기기 메모리가 16GB라서 그거 고려해서 .md 만들어줘" · 인계 글 `HANDOVER_COREPOP_16GB_20261115.md`.

예측식(2026-11-15 16:5x HKHOME 이 맞춤 · 값이 아니라 계산 자원 기록):
  Zeo++ `network -ha -block r 50000`(단위셀) 호출 하나의 최대 RSS 를, 그 구조의 세 탐침 중 최대로 보고 단위셀 부피 V 로 맞춤.
  ln(GB) = A + B · ln(V/Å³) · A −6.9187 · B 1.0544 · 구조 105(b01 랩탑 · b02 laptop2 · b03 · b04 HKHOME 의 가드 안 걸린 호출 351)
  r 0.97(로그-로그) · 잔차 배수 보통 ×1.17 · 가장 큰 잔차 ×1.46 · 맞춘 부피 범위 570 ~ 6,208 Å³(밖은 외삽 — 7,500 Å³ 의 In neb 는 예측보다 컸음)
고르는 규칙: 예측 × 1.46(가장 큰 잔차) ≤ 한도 이고 V ≤ 6,208 Å³ 이면 '가벼움', 아니면 '무거움'(큰 기기 몫).
  한도 = 그 기기가 비어 있을 때 MemAvailable − 5.0 GB (corepop_blocks.py 의 가드: 여유 5,000 MB 미만이면 kill).

사용:  python corepop_light_keys.py <묶음[,묶음…]> <한도 GB> [--out <키 파일>]   (예: b06,b07,b08,b09,b10 6.0)
  → 키 파일(JSON): 'keys' = 가벼운 구조(대상 목록 순서 · corepop_blocks_keys.py 가 읽는 모양) · 'heavy' = 넘길 구조 · 근거 열.
기계적 사실뿐 — 결과값 · 판정과 무관.
"""
import hashlib
import io
import json
import math
import os
import sys
import time
import zipfile

from ase.io import read

D = os.path.dirname(os.path.abspath(__file__))
A, B = -6.918700059576604, 1.0544304677782175
MARGIN = 1.46
VMAX = 6208.0
FIT = {'A': A, 'B': B, 'n_structures': 105, 'n_calls': 351, 'r_loglog': 0.97, 'resid_typical': 1.17, 'resid_max': 1.46,
       'V_range_A3': [570, 6208], 'made': '2026-11-15 16:5x HKHOME',
       'sources': ['results_corepop_blocks_laptop_b01.json', 'results_corepop_blocks_laptop2_b02.json',
                   'results_corepop_blocks_hkhome_b03.json', 'results_corepop_blocks_hkhome_b04.json(첫 판 도는 중 97호출)']}


def pred_gb(v):
    return math.exp(A + B * math.log(v))


def main():
    args = sys.argv[1:]
    out = None
    if '--out' in args:
        i = args.index('--out')
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)
    batches, cap = [b for b in args[0].split(',') if b], float(args[1])
    batch = '_'.join(batches)
    if not (1.0 <= cap <= 40.0):
        raise SystemExit(f'!! 한도 {cap} GB 가 이상함')
    T = [r for r in json.load(open(os.path.join(D, 'corepop_humid323_targets.json'), encoding='utf-8'))['rows'] if r['batch'] in batches]
    if not T:
        raise SystemExit(f'!! 묶음 {batches} 에 대상 없음')
    missing = [b for b in batches if not any(r['batch'] == b for r in T)]
    if missing:
        raise SystemExit(f'!! 대상이 없는 묶음 {missing}')
    ann = {r['key']: r for r in json.load(open(os.path.join(D, 'core_pop_annotated.json'), encoding='utf-8'))['rows']}
    zp = os.path.join(D, 'core_pop_cifs.zip')
    zf = zipfile.ZipFile(zp)
    rows = []
    for t in T:
        f = ann[t['key']]['file']
        a = read(io.StringIO(zf.read(f).decode('utf-8', 'replace')), format='cif')
        if len(a) != ann[t['key']]['NAtoms']:
            raise SystemExit(f'!! {f} 원자 수 {len(a)} ≠ NAtoms {ann[t["key"]]["NAtoms"]}')
        v = float(a.get_volume())
        p = float(pred_gb(v))
        light = bool((p * MARGIN <= cap) and (v <= VMAX))
        rows.append({'key': t['key'], 'batch': t['batch'], 'rank': t['rank'], 'file': f, 'cell_volume_A3': round(v, 1),
                     'pred_peak_GB': round(p, 2), 'pred_upper_GB': round(p * MARGIN, 2), 'light': light,
                     'why_heavy': None if light else ('맞춘 부피 범위 밖' if v > VMAX else f'예측 위쪽 {p * MARGIN:.1f} GB > 한도 {cap:.1f} GB')})
    light = [r['key'] for r in rows if r['light']]
    heavy = [r['key'] for r in rows if not r['light']]
    o = {'test': 'COREPOP-H323 — 메모리 작은 기기용 가벼운 구조 목록', 'batches': batches, 'ceiling_GB': cap, 'margin': MARGIN,
         'rule': '예측 × 1.46 ≤ 한도 · V ≤ 6,208 Å³ 이면 가벼움', 'fit': FIT, 'zip_md5': hashlib.md5(open(zp, 'rb').read()).hexdigest(),
         'made': time.strftime('%F %T'), 'keys': light, 'heavy': heavy, 'n_light': len(light), 'n_heavy': len(heavy), 'rows': rows}
    dst = out or os.path.join(D, f'corepop_light_keys_{batch}.json')
    json.dump(o, open(dst, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'묶음 {batch} · 한도 {cap:.1f} GB · 가벼움 {len(light)} · 무거움 {len(heavy)} → {dst}')
    for r in sorted(rows, key=lambda r: -r['pred_upper_GB']):
        if not r['light']:
            print(f"  무거움 {r['key']:28s} 부피 {r['cell_volume_A3']:8.0f} Å³ · 예측 {r['pred_peak_GB']:5.1f} GB (위쪽 {r['pred_upper_GB']:5.1f})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
