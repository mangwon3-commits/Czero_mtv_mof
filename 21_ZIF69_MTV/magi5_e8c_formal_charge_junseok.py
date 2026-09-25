# -*- coding: utf-8 -*-
"""MAGI-005 E-8c (Junseok) — 상위 68행(S ≥ 65.2)의 골격 형식 전하 ≠ 0 (짝이온 삭제) 판정. `ASSIGN_MAGI5B §Junseok 9차`. 계산 0.

방법(E-15b · E-16 을 기계화):
  ① CoRE 메타 슬라이스 짝짓기 — 금속 · 원자 수 · Zeo++ LCD/PLD 차 < 0.01 Å · ASR/FSR 판 → DOI · MOFid-v1 · has_OMS.
  ② MOFid-v1 SMILES 를 성분('.')으로 나눠 원소 수(암시 H 포함)와 형식 전하를 센다(rdkit 없음 — 작은 파서; 알려진 링커 셋으로 검증).
  ③ CIF 원소 수(원자 표에서 직접)를 성분 배수의 음 아닌 정수 합으로 **정확히** 맞춘다(H 까지). 안 맞으면 H 를 빼고 무거운 원자로 다시(표지).
  ④ 금속 외 무기 원자 가정: 금속 성분 안의 O(H 0)=−2 · OH=−1 · OH₂=0 · F/Cl/Br/I=−1 · 괄호 전하는 그대로. 유기 성분 전하는 SMILES 그대로.
  ⑤ 금속 산화수 흔한 집합(아래 표)으로 합 0 을 만들 수 있으면 False(균형), 못 만들면 True(순전하 — 짝이온 삭제 의심), 풀이 없으면 None.
판정문은 종합자 — 이 스크립트는 값과 근거 문자열만 낸다.
"""
import json
import os
import re
import sys
import zipfile
from collections import Counter
from itertools import product

D = '/home/mangwon/mof_project/'
OX = {'Zn': [2], 'Cd': [2], 'Co': [2, 3], 'Cu': [1, 2], 'Ni': [2], 'Mn': [2, 3], 'Fe': [2, 3], 'Mg': [2], 'Ca': [2], 'Sr': [2], 'Ba': [2],
      'Zr': [4], 'Hf': [4], 'Ti': [3, 4], 'V': [3, 4], 'Cr': [3], 'Al': [3], 'Ga': [3], 'In': [3], 'Sc': [3], 'Y': [3], 'Ag': [1],
      'Pb': [2], 'Sn': [2, 4], 'Hg': [2], 'Li': [1], 'Na': [1], 'K': [1], 'Rb': [1], 'Cs': [1], 'Pd': [2], 'Pt': [2], 'Au': [1, 3],
      'Bi': [3], 'U': [4, 6], 'Mo': [2, 3, 4, 5, 6], 'W': [4, 5, 6], 'Ru': [2, 3], 'Rh': [2, 3], 'Be': [2], 'Tl': [1, 3],
      'La': [3], 'Ce': [3, 4], 'Pr': [3], 'Nd': [3], 'Sm': [3], 'Eu': [2, 3], 'Gd': [3], 'Tb': [3], 'Dy': [3], 'Ho': [3], 'Er': [3],
      'Tm': [3], 'Yb': [3], 'Lu': [3]}
METALS = set(OX)
ORGANIC = {'B': [3], 'C': [4], 'N': [3, 5], 'O': [2], 'P': [3, 5], 'S': [2, 4, 6], 'F': [1], 'Cl': [1], 'Br': [1], 'I': [1]}
AROM = {'b': 'B', 'c': 'C', 'n': 'N', 'o': 'O', 'p': 'P', 's': 'S', 'se': 'Se', 'as': 'As'}
BOND = {'-': 1, '=': 2, '#': 3, '$': 4, ':': 1.5, '/': 1, '\\': 1}


def _link(atoms, a, b, bond):
    """결합 하나를 두 원자에 적는다. 기호 없고 둘 다 방향족이면 방향족 결합(연결 1 로 셈), 아니면 단일."""
    if bond == 1.5 or (bond is None and atoms[a]['arom'] and atoms[b]['arom']):
        atoms[a]['n_arom'] += 1
        atoms[b]['n_arom'] += 1
    else:
        o = 1 if bond is None else bond
        atoms[a]['bo'] += o
        atoms[b]['bo'] += o


def parse_atoms(smi):
    """원자 목록(원소 · 방향족 · 괄호 · H(명시/암시) · 전하). 암시 H: 방향족은 원자가 − (방향족 결합 수 + 그 밖 결합 차수) − 1(π),
    비방향족은 원자가 − 결합 차수 합(허용 원자가 중 가장 작은 것 ≥ 합)."""
    atoms, i, stack, prev, bond, rings = [], 0, [], None, None, {}
    n = len(smi)
    while i < n:
        ch = smi[i]
        if ch == '(':
            stack.append(prev); i += 1; continue
        if ch == ')':
            prev = stack.pop(); i += 1; continue
        if ch in BOND:
            bond = BOND[ch]; i += 1; continue
        if ch.isdigit() or ch == '%':
            if ch == '%':
                num = int(smi[i + 1:i + 3]); i += 3
            else:
                num = int(ch); i += 1
            if num in rings:
                a, b0 = rings.pop(num)
                _link(atoms, a, prev, bond if bond is not None else b0)
            else:
                rings[num] = (prev, bond)
            bond = None
            continue
        if ch == '[':
            j = smi.index(']', i)
            body = smi[i + 1:j]; i = j + 1
            m = re.match(r'(\d*)([A-Z][a-z]?|se|as|[bcnops]|\*)(@*)(H\d*)?([+-]+\d*|[+-]\d+)?(:\d+)?$', body)
            if not m:
                raise ValueError(f'괄호 원자 해석 불가 [{body}]')
            sym = m.group(2)
            arom = sym in AROM
            el = AROM.get(sym, sym)
            h = 0 if not m.group(4) else (int(m.group(4)[1:]) if len(m.group(4)) > 1 else 1)
            q = 0
            if m.group(5):
                s_ = m.group(5)
                if s_.strip('+') == '' or s_.strip('-') == '':
                    q = len(s_) * (1 if s_[0] == '+' else -1)
                else:
                    q = int(s_[1:]) * (1 if s_[0] == '+' else -1)
            atoms.append({'el': el, 'arom': arom, 'bracket': True, 'h': h, 'q': q, 'bo': 0, 'n_arom': 0})
        else:
            two = smi[i:i + 2]
            if two in ('Cl', 'Br'):
                sym, i = two, i + 2
            elif two in ('se', 'as'):
                sym, i = two, i + 2
            else:
                sym, i = ch, i + 1
            if sym not in ORGANIC and sym not in AROM and sym != '*':
                raise ValueError(f'유기 부분집합 밖 원자 {sym} in {smi}')
            atoms.append({'el': AROM.get(sym, sym), 'arom': sym in AROM, 'bracket': False, 'h': None, 'q': 0, 'bo': 0, 'n_arom': 0})
        cur = len(atoms) - 1
        if prev is not None:
            _link(atoms, prev, cur, bond)
        prev, bond = cur, None
    if rings:
        raise ValueError(f'닫히지 않은 고리 {list(rings)} in {smi}')
    for a in atoms:
        if a['bracket']:
            continue
        vs = ORGANIC.get(a['el'], [0])
        if a['arom']:
            a['h'] = max(0, vs[0] - (a['n_arom'] + a['bo']) - 1)
        else:
            s_ = a['bo'] + a['n_arom']
            a['h'] = next((v - s_ for v in vs if v >= s_), 0)
    return atoms


def parse_smiles(smi, with_radicals=False):
    """원소 수(암시 H 포함) · 형식 전하. with_radicals 면 (cnt, charge, n_radical) —
    MOFid 는 금속에서 떼어 낸 음이온 자리를 가끔 전하 대신 **라디칼**([N] · [C] 처럼 H·전하 없는 괄호 원자에 남는 원자가)로 적는다.
    그런 자리 하나를 음이온 자리 하나(−1)로 센다(Co(p-Me₂-bdp) 실례: 라디칼 둘 = bdp²⁻)."""
    atoms = parse_atoms(smi)
    cnt, charge, rad = Counter(), 0, 0
    for a in atoms:
        cnt[a['el']] += 1
        charge += a['q']
        if a['h']:
            cnt['H'] += a['h']
        if a['bracket'] and a['q'] == 0 and a['el'] in ORGANIC:
            v = ORGANIC[a['el']][0]
            used = a['bo'] + a['n_arom'] + (a['h'] or 0) + (1 if a['arom'] else 0)
            if used < v:
                rad += int(round(v - used))
    return (cnt, charge, rad) if with_radicals else (cnt, charge)


def cif_counts(name):
    p = D + f'21_ZIF69_MTV/core_pop_cifs/{name}.cif'
    txt = open(p).read() if os.path.exists(p) else zipfile.ZipFile(D + '21_ZIF69_MTV/core_pop_cifs.zip').read(name + '.cif').decode()
    L = txt.splitlines()
    hdr = [l.strip() for l in L if l.strip().startswith('_atom_site_')]
    it = hdr.index('_atom_site_type_symbol')
    rows = [l.split() for l in L if l.strip() and not l.strip().startswith(('_', 'loop_', '#', 'data_')) and len(l.split()) == len(hdr)]
    return Counter(re.sub(r'[^A-Za-z]', '', r[it]) for r in rows)


def inorganic_charge(cnt_atoms_list):
    """금속 성분 안의 비금속 원자 가정 전하 — O(H0) −2 · OH −1 · OH2 0 · 할로겐 −1."""
    return None


def component_info(smi):
    cnt, q, rad = parse_smiles(smi, with_radicals=True)
    has_metal = any(e in METALS for e in cnt)
    return {'smiles': smi, 'counts': cnt, 'charge': q - (rad if not has_metal else 0), 'radicals': rad if not has_metal else 0,
            'metal': has_metal}


def metal_component_charge(smi):
    """금속을 품은 성분: 금속 외 원자에 가정 전하(괄호 전하가 있으면 그것) — O(H0) −2 · OH −1 · OH₂ 0 · 할로겐 −1 · 그 밖 0."""
    q = 0
    for a in parse_atoms(smi):
        if a['q']:
            q += a['q']
        elif a['el'] in METALS:
            continue
        elif a['el'] == 'O':
            q += {0: -2, 1: -1}.get(a['h'] or 0, 0)
        elif a['el'] in ('F', 'Cl', 'Br', 'I'):
            q += -1
    return q


def solve(cif, comps, use_h=True):
    els = sorted(set(cif) | set(e for c in comps for e in c['counts']))
    if not use_h:
        els = [e for e in els if e != 'H']
    bounds = []
    for c in comps:
        lim = min((cif.get(e, 0) // c['counts'][e]) for e in c['counts'] if (use_h or e != 'H') and c['counts'][e] > 0)
        bounds.append(range(0, lim + 1))
    sols = []
    for ns in product(*bounds):
        if all(sum(n * c['counts'].get(e, 0) for n, c in zip(ns, comps)) == cif.get(e, 0) for e in els):
            sols.append(ns)
        if len(sols) > 3:
            break
    return sols


def achievable(metals):
    tot = {0}
    for el, k in metals.items():
        for _ in range(k):
            tot = {t + s for t in tot for s in OX.get(el, [])}
    return tot


def analyse(name, meta_rec):
    mofid = (meta_rec.get('id') or {}).get('mofid-v1') or ''
    smiles = mofid.split(' ')[0]
    cif = cif_counts(name)
    out = {'cif_counts': dict(cif), 'mofid': mofid}
    try:
        comps = [component_info(s) for s in smiles.split('.') if s]
    except ValueError as e:
        out.update(value=None, basis=f'MOFid SMILES 해석 불가: {e}')
        return out
    for c in comps:
        if c['metal']:
            c['charge_assumed'] = metal_component_charge(c['smiles'])
    sols = solve(cif, comps, use_h=True)
    hnote = ''
    if not sols:
        sols = solve(cif, comps, use_h=False)
        hnote = ' · H 는 안 맞음(무거운 원자로만 풀림)'
    if len(sols) != 1:
        out.update(value=None, basis=f'성분 배수 풀이 {len(sols)}개(0 이면 CIF 원자를 MOFid 성분으로 못 채움){hnote}',
                   components=[{'smiles': c['smiles'], 'counts': dict(c['counts']), 'charge': c['charge']} for c in comps])
        return out
    ns = sols[0]
    q_org = sum(n * c['charge'] for n, c in zip(ns, comps) if not c['metal'])
    q_inorg = sum(n * c.get('charge_assumed', 0) for n, c in zip(ns, comps) if c['metal'])
    metals = Counter()
    for n, c in zip(ns, comps):
        for e, k in c['counts'].items():
            if e in METALS:
                metals[e] += n * k
    need = -(q_org + q_inorg)
    ach = achievable(metals)
    unknown = [e for e in metals if e not in OX]
    value = None if unknown else (need not in ach)
    parts = ' + '.join(f"{n}×{c['smiles'][:40]}({c['charge'] if not c['metal'] else c.get('charge_assumed')})" for n, c in zip(ns, comps) if n)
    nrad = sum(n * c.get('radicals', 0) for n, c in zip(ns, comps))
    if nrad:
        hnote += f' · MOFid 라디칼 {nrad}자리를 음이온 자리로 셈'
    out.update(value=value, multiplicity=list(ns), q_organic=q_org, q_inorganic_assumed=q_inorg, metals=dict(metals), radicals_as_anion=nrad,
               metal_charge_needed=need, metal_charge_achievable=sorted(ach)[:12] if len(ach) < 30 else [min(ach), max(ach)],
               basis=(f"{parts} · 금속 {dict(metals)} 이 +{need} 를 내야 함 · 흔한 산화수로 가능한 합 "
                      f"{sorted(ach) if len(ach) < 12 else [min(ach), '…', max(ach)]} → {'균형(0)' if value is False else ('순전하 ' + str(need - min(ach, key=lambda t: abs(t - need))) if value else '판정 불가')}{hnote}"))
    return out


def selftest():
    for smi, want_cnt, want_q in (
            ('[O-]C(=O)c1ccc(cc1)C12CC3CC(C2)(CC(C1)(C3)c1ccc(cc1)C(=O)[O-])c1ccc(cc1)C(=O)[O-]', {'C': 31, 'H': 25, 'O': 6}, -3),
            ('C(Cn1cncc1)CCn1cncc1', {'C': 10, 'H': 14, 'N': 4}, 0),
            ('[O-]C(=O)c1cc2c(s1)cc1c(c2)sc(c1)C(=O)[O-]', {'C': 12, 'H': 4, 'O': 4, 'S': 2}, -2),
            ('Cc1nc[n-]c1', {'C': 4, 'H': 5, 'N': 2}, -1),
            ('[O-]C(=O)c1ccc(cc1)C(=O)[O-]', {'C': 8, 'H': 4, 'O': 4}, -2)):
        cnt, q = parse_smiles(smi)
        ok = dict(cnt) == want_cnt and q == want_q
        print(f"  자가시험 {'통과' if ok else '!! 실패'}: {smi[:50]} → {dict(cnt)} · {q} (기대 {want_cnt} · {want_q})")
        if not ok:
            return False
    return True


KNOWN = {'2017_Cd__hcb_2_ASR_1': True, '2024_Zn__srs_3_ASR_1': True, '2024_Zn__lig_3_ASR_1': True,
         '2017_Zn__dia_3_ASR_1': False, '2017_Zn__dia_3_FSR_1': False, '2024_Zn__srs_3_FSR_1': False}


def main():
    ann = json.load(open(D + '21_ZIF69_MTV/core_pop_annotated.json', encoding='utf-8'))['rows']
    meta = json.load(open(D + '23_SCREENING/data/CR_meta_data_SI_slice.json', encoding='utf-8'))
    top = [r for r in ann if r.get('KH_CO2') and r.get('KH_N2') and r['KH_CO2'] / r['KH_N2'] >= 65.2]
    print(f'상위 {len(top)}행 (S ≥ 65.2)', flush=True)
    rows = []
    for a in sorted(top, key=lambda r: -r['KH_CO2'] / r['KH_N2']):
        name = a['file'].replace('.cif', '')
        ext = 'ASR' if '_ASR_' in name else 'FSR'
        hits = [k for k, m in meta.items()
                if (m.get('metal') or {}).get('metal_type') and a.get('metal') and a['metal'] in str((m.get('metal') or {}).get('metal_type'))
                and (m.get('structure_info') or {}).get('n_atoms') == a.get('NAtoms')
                and abs(((m.get('Zeopp') or {}).get('LCD') or 0) - a['LCD']) < 0.01
                and abs(((m.get('Zeopp') or {}).get('PLD') or 0) - a['PLD']) < 0.01]
        pick = [h for h in hits if f'_{ext}_' in h] or hits
        row = {'name': name, 'key': a['key'], 'dim': a.get('dim'), 'S_ON': a['KH_CO2'] / a['KH_N2'], 'PLD': a['PLD'],
               'probe_convention': a['PLD'] < 3.64, 'formula': a.get('formula'), 'meta_hits': hits}
        borrowed = None
        if not pick:
            # 메타에 이 판이 없으면: 같은 계열(series)의 **조성이 같은** 형제 판 MOFid 를 빌린다(원소 수 완전 일치일 때만)
            me = cif_counts(name)
            for sib in ann:
                sn = sib['file'].replace('.cif', '')
                if sn == name or sib.get('series') != a.get('series'):
                    continue
                if cif_counts(sn) != me:
                    continue
                sh = [k for k, m in meta.items()
                      if (m.get('metal') or {}).get('metal_type') and sib.get('metal') and sib['metal'] in str((m.get('metal') or {}).get('metal_type'))
                      and (m.get('structure_info') or {}).get('n_atoms') == sib.get('NAtoms')
                      and abs(((m.get('Zeopp') or {}).get('LCD') or 0) - sib['LCD']) < 0.01
                      and abs(((m.get('Zeopp') or {}).get('PLD') or 0) - sib['PLD']) < 0.01]
                if sh:
                    pick, borrowed = sh[:1], sn
                    break
        if not pick:
            row.update(value=None, basis=f'CoRE 메타 짝 0개(금속·원자 수·LCD/PLD < 0.01 Å·{ext}) · 같은 조성 형제 판도 없음 — 판정 못 함', DOI=None)
        else:
            res = [(k, analyse(name, meta[k])) for k in pick]
            vals = {r[1].get('value') for r in res}
            k0, r0 = res[0]
            mm = meta[k0]
            row.update(meta_key=k0 if len(pick) == 1 else pick, DOI=(mm.get('reference') or {}).get('DOI'),
                       extension=(mm.get('structure_info') or {}).get('extension'), has_OMS=(mm.get('metal') or {}).get('has_OMS'),
                       mosaec=((mm.get('structure_info') or {}).get('memo') or {}).get('MOSAEC')
                       if isinstance((mm.get('structure_info') or {}).get('memo'), dict) else None)
            row.update(r0)
            if len(pick) > 1:
                if len(vals) == 1:
                    row['basis'] = f'메타 짝 {len(pick)}개 모두 같은 값 · ' + str(row['basis'])
                else:
                    row.update(value=None, basis=f'메타 짝 {len(pick)}개가 서로 다른 값 {sorted(map(str, vals))} — 판정 못 함')
            if borrowed:
                row['basis'] = f'메타에 이 판 없음 → 같은 계열·같은 조성 형제 {borrowed} 의 MOFid 로 셈 · ' + str(row['basis'])
                row['borrowed_from'] = borrowed
        if name in KNOWN:
            row['known_value'] = KNOWN[name]
            row['agrees_with_known'] = (row.get('value') == KNOWN[name])
        rows.append(row)
        print(f"  {name:<26} {str(row.get('value')):<5} · {row.get('DOI')} · {str(row.get('basis'))[:150]}", flush=True)
    c = Counter(str(r.get('value')) for r in rows)
    kn = [(r['name'], r.get('value'), r['known_value']) for r in rows if 'known_value' in r]
    out = {'test': 'MAGI-005 E-8c — 상위 68행 골격 형식 전하 ≠ 0 (짝이온 삭제) 채우기', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 9차',
           'machine': 'junseok', 'method': __doc__.strip(),
           'oxidation_states_assumed': OX, 'summary': {'True': c.get('True', 0), 'False': c.get('False', 0), 'None': c.get('None', 0), 'n': len(rows)},
           'known_check': kn, 'registered': '상위 68 중 True ≥ 3 행(계수, 기각 없음) — 판정문은 종합자', 'rows': rows}
    json.dump(out, open(D + '21_ZIF69_MTV/core_pop_formal_charge_junseok.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=list)
    print(f"\n요약 True {c.get('True', 0)} · False {c.get('False', 0)} · None {c.get('None', 0)} / {len(rows)} · 확인 행 대조 {kn}", flush=True)
    return 0


if __name__ == '__main__':
    if not selftest():
        sys.exit(1)
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        sys.exit(0)
    sys.exit(main())
