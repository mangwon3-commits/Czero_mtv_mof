# -*- coding: utf-8 -*-
"""E-16 ① 정체 — 2017_Zn__dia_3_ASR_1 · FSR_1 을 CoRE 메타 슬라이스와 짝짓기(계산 0). 기준: Zn · 원자 수 · Zeo++ LCD/PLD 차 < 0.01 Å."""
import json
from collections import Counter

D = '/home/mangwon/mof_project/'
meta = json.load(open(D + '23_SCREENING/data/CR_meta_data_SI_slice.json', encoding='utf-8'))
ann = {r['file']: r for r in json.load(open(D + '21_ZIF69_MTV/core_pop_annotated.json', encoding='utf-8'))['rows']}
for name in ('2017_Zn__dia_3_ASR_1', '2017_Zn__dia_3_FSR_1'):
    a = ann[name + '.cif']
    print(f"\n=== {name}: formula {a.get('formula')} · NAtoms {a.get('NAtoms')} · LCD {a.get('LCD')} · PLD {a.get('PLD')} · "
          f"S {a.get('selectivity'):.1f} · pair {a.get('asr_fsr_pair')} · anion_removed {a.get('anion_removed')} · L {a.get('L')}")
    hits = []
    for k, r in meta.items():
        si, z, mt = r.get('structure_info') or {}, r.get('Zeopp') or {}, (r.get('metal') or {}).get('metal_type')
        if mt and 'Zn' in str(mt) and si.get('n_atoms') == a.get('NAtoms') and abs((z.get('LCD') or 0) - a['LCD']) < 0.01 \
                and abs((z.get('PLD') or 0) - a['PLD']) < 0.01:
            hits.append(k)
    print('  짝 후보', hits)
    for k in hits:
        r = meta[k]
        si = r.get('structure_info') or {}
        print(json.dumps({'key': k, 'reference': r.get('reference'), 'n_atoms': si.get('n_atoms'), 'extension': si.get('extension'),
                          'unmodified': si.get('unmodified'), 'space_group': si.get('space_group'), 'memo': si.get('memo'),
                          'mofid-v1': (r.get('id') or {}).get('mofid-v1'), 'common_name': (r.get('id') or {}).get('common_name'),
                          'CrystalNets': r.get('CrystalNets'), 'metal': r.get('metal'), 'water': r.get('water'),
                          'stability': r.get('stability')}, ensure_ascii=False, indent=1))
        stem = k.split('_ASR')[0].split('_FSR')[0]
        sib = sorted(s for s in meta if s.startswith(stem) and s != k)
        print('  같은 줄기', stem, '→', sib)
# CIF 원소 수(ASR 판 · FSR 판) — 조성 차
for name in ('2017_Zn__dia_3_ASR_1', '2017_Zn__dia_3_FSR_1'):
    txt = open(D + f'21_ZIF69_MTV/core_pop_cifs/{name}.cif').read() if __import__('os').path.exists(D + f'21_ZIF69_MTV/core_pop_cifs/{name}.cif') else None
    if txt is None:
        import zipfile
        txt = zipfile.ZipFile(D + '21_ZIF69_MTV/core_pop_cifs.zip').read(name + '.cif').decode()
    L = txt.splitlines()
    hdr = [l.strip() for l in L if l.strip().startswith('_atom_site_')]
    it, ic = hdr.index('_atom_site_type_symbol'), hdr.index('_atom_site_charge')
    rows = [l.split() for l in L if l.strip() and not l.strip().startswith(('_', 'loop_', '#', 'data_')) and len(l.split()) == len(hdr)]
    cnt = Counter(r[it] for r in rows)
    q = sum(float(r[ic]) for r in rows)
    qz = [float(r[ic]) for r in rows if r[it] == 'Zn']
    print(f"  CIF {name}: {dict(sorted(cnt.items()))} · 전하 합 {q:.4f} · Zn 전하 {min(qz):.3f}~{max(qz):.3f}")
