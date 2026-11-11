# -*- coding: utf-8 -*-
"""등록 L (L-0) 점검(등록 밖 · 다른 시험)의 측정 — 흩뜨린 출발(`e24k_symcheck_hkhome.py`)의 이완본을 `e24k_gate.measure`(같은 코드)로 재고
등록 절차 이완본과 에너지 · 비틀림 · 여유를 나란히 적음. 판정 없음 · L-1 진행 표지는 등록 절차 이완본의 것만(`results_e24k_me37_gate_hkhome.json`).
실행: czeromof 파이썬 — `python e24k_symcheck_measure.py [seed …]` → results_e24k_symcheck_hkhome.json"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import e24k_gate as K   # noqa: E402  (os.chdir(HERE) 포함)
from ase.io import read   # noqa: E402


def last_e(tag):
    p = os.path.join('relax_tnf', tag, 'opt.log')
    rows = [ln.split() for ln in open(p) if ln.startswith('FIRE:')]
    return {'steps_logged': len(rows), 'energy_eV': float(rows[-1][3]), 'fmax_eV_A': float(rows[-1][4])}


def main():
    seeds = [int(x) for x in sys.argv[1:]] or [1]
    par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions()
    b = [r for r in json.load(open('e24k_candidates/e24k_build.json', encoding='utf-8'))['rows'] if r['name'] == 'E24k_ZnDia_Me37_open'][0]
    relax = {r['tag']: r for r in json.load(open('results_e24k_symcheck_relax_hkhome.json', encoding='utf-8'))}
    reg = json.load(open(K.OUT, encoding='utf-8'))['rows']['e24k_me37_open']
    out = {'test': '등록 L (L-0) 점검 — 대칭 깨기(등록 밖 · 다른 시험)', 'assign': 'ASSIGN_NOON_20261112.md §L(점검은 HKHOME 이 덧붙임 — CLAUDE.md §0 "나쁜 결과를 보면 검사기부터")',
           'machine': 'hkhome', 'made': time.strftime('%F %T'), 'rattle_stdev_A': 0.03, 'registered_run': {'tag': 'e24k_me37_open', **last_e('e24k_me37_open'),
           'min_margin_A': reg['gate0b']['min_margin_A'], 'worst_pair': reg['gate0b']['worst_pair'], 'max_framework_disp_A': reg['max_framework_disp_A'],
           'twist_with_methyl_deg': reg['after']['carboxylate_twist_deg']['with_methyl'], 'gate_all_pass': reg['gate_all_pass']}, 'rows': {},
           'note': '기계적 사실뿐. 흩뜨린 빌드본은 모체 원자와 0.3 Å 짝짓기가 그대로 됨(흩뜨림 0.03 Å). 에너지는 FIRE 기록의 마지막 줄(GFN-FF · eV · fmax 0.05 에서 멈춘 값).'}
    for sd in seeds:
        tag = f'e24k_me37_open_rattle{sd}'
        row = K.measure(tag, f'e24k_candidates/E24k_ZnDia_Me37_open_rattle{sd}.cif', f'relax_tnf/{tag}_relaxed.cif', 4, b, relax, par, P)
        row['seed'] = sd
        row.update(last_e(tag))
        row['energy_minus_registered_run_eV'] = row['energy_eV'] - out['registered_run']['energy_eV']
        out['rows'][tag] = row
    json.dump(out, open('results_e24k_symcheck_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    r0 = out['registered_run']
    print(f"등록 절차 이완본: E {r0['energy_eV']:.6f} eV · fmax {r0['fmax_eV_A']} · 여유 {r0['min_margin_A']:+.3f} · 비틀림 {r0['twist_with_methyl_deg']}", flush=True)
    for tag, row in out['rows'].items():
        print(f"{tag}: E {row['energy_eV']:.6f} eV(등록 절차 대비 {row['energy_minus_registered_run_eV']:+.4f} eV) · fmax {row['fmax_eV_A']} · 여유 {row['gate0b']['min_margin_A']:+.3f} "
              f"{row['gate0b']['worst_pair']} · 비틀림 {row['after']['carboxylate_twist_deg']['with_methyl']} · 변위 {row['max_framework_disp_A']} · 관문 전부 {row['gate_all_pass']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
