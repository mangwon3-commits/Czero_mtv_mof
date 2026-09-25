# -*- coding: utf-8 -*-
"""E-15b ② 정체 — CoRE 메타 슬라이스에서 2017_Cd__hcb_2_ASR_1 짝짓기(계산 0). 기준: Cd · 원자 126 · Zeo++ LCD/PLD 차 < 0.01 Å."""
import json

D = '/home/mangwon/mof_project/'
meta = json.load(open(D + '23_SCREENING/data/CR_meta_data_SI_slice.json', encoding='utf-8'))
LCD, PLD, NAT = 6.93233, 4.45124, 126
hits = []
for k, r in meta.items():
    si, z, mt = r.get('structure_info') or {}, r.get('Zeopp') or {}, (r.get('metal') or {}).get('metal_type')
    if mt and 'Cd' in str(mt) and si.get('n_atoms') == NAT and abs((z.get('LCD') or 0) - LCD) < 0.01 and abs((z.get('PLD') or 0) - PLD) < 0.01:
        hits.append(k)
print('짝 후보', hits)
for k in hits:
    r = meta[k]
    print(json.dumps({'key': k, 'reference': r.get('reference'), 'structure_info': r.get('structure_info'),
                      'mofid-v1': (r.get('id') or {}).get('mofid-v1'), 'common_name': (r.get('id') or {}).get('common_name'),
                      'Zeopp': {x: (r.get('Zeopp') or {}).get(x) for x in ('LCD', 'PLD', 'VF', 'dimension')},
                      'CrystalNets': r.get('CrystalNets'), 'metal': r.get('metal')}, ensure_ascii=False, indent=1))
# 같은 SI 이름 줄기의 다른 판(FSR · 원판) — 조성 대조
for k in hits:
    stem = k.split('_ASR')[0].split('_FSR')[0]
    sib = [s for s in meta if s.startswith(stem) and s != k]
    print('같은 줄기', stem, '→', sib)
    for s in sib:
        r = meta[s]
        print('   ', s, (r.get('structure_info') or {}).get('n_atoms'), (r.get('structure_info') or {}).get('extension'),
              (r.get('Zeopp') or {}).get('LCD'), (r.get('Zeopp') or {}).get('PLD'), (r.get('metal') or {}))
