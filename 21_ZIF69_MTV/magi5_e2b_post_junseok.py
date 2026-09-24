# -*- coding: utf-8 -*-
"""MAGI-005 E-2b 후처리 (Junseok) — '0 과 구별 안 되는 K_H' 를 표지하고, 그런 행의 비(S)를 null 로 바꾼다.

[왜]  드라이버 `magi5_e2b_junseok.py` 는 K_H(N₂) 가 **정확히 0** 일 때만 S 를 null(발산)로 적었다.
      실제 차단 실행은 0 이 아니라 1e-112 · 1e-157 같은 **수치상 0**(± 가 값보다 큼)을 냈고, 드라이버는 그 비를 그대로
      계산해 S ≈ 1e-46 · 정식 짝 ≈ 1e108 같은 **뜻 없는 유한값**을 적었다 — 실패가 결과처럼 보이는 모양(CLAUDE.md §0).
[기준] K_H − ± ≤ 0 (95 % 폭이 0 을 품음) **그리고** K_H < 1e-6 × 차단 없음 참조(laptop2) → "0 과 구별 안 됨".
[보존] 원값은 지우지 않는다 — S·S_err·S_over_ref·units_from_ref 의 원값은 `*_raw` 로 옮기고, 판단 필드만 null + 이유.
"""
import datetime
import json
import os
import sys

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
OUT = os.path.join(HERE, 'results_magi5_e2b_blockpockets_junseok.json')
REL = 1e-6


def main():
    d = json.load(open(OUT, encoding='utf-8'))
    if not d.get('final'):
        print('!! 드라이버 결과가 final 이 아님 — 후처리 안 함')
        return 1
    if d.get('postprocess'):
        print('!! 이미 후처리됨 — 다시 안 함')
        return 1
    ref = d['reference_unblocked']

    def mark(g, x):
        if not x or x.get('status') != 'ok' or x.get('KH') is None:
            return None
        kh, e = x['KH'], x.get('KH_err') or 0.0
        x['KH_over_unblocked'] = kh / ref['KH_' + g]
        x['KH_units_from_unblocked'] = round(abs(kh - ref['KH_' + g]) / max(e, ref['KH_' + g + '_err']), 2)
        x['KH_effectively_zero'] = bool(kh - e <= 0 and kh < REL * ref['KH_' + g])
        return x['KH_effectively_zero']

    for row in d['rows']:
        zc, zn = mark('CO2', row['CO2']), mark('N2', row['N2'])
        if zc is None or zn is None:
            continue
        if zc or zn:
            row['S_raw'], row['S_err_raw'] = row.get('S'), row.get('S_err')
            row['S'], row['S_err'] = (0.0 if (zc and not zn) else None), None
            row['S_note'] = ('0/0 — 두 기체 모두 완전 차단(K_H 가 0 과 구별 안 됨) → S(r) 정의 안 됨' if (zc and zn) else
                             '분모 0 — N₂ 완전 차단 → S 발산' if zn else 'CO₂ 만 완전 차단 → S = 0')
        else:
            row['S_units_from_unblocked'] = round(abs(row['S'] - ref['S']) / max(row['S_err'], ref['S_err']), 2)

    rows = {r['probe_radius_A']: r for r in d['rows']}
    c, n = rows[1.65]['CO2'], rows[1.82]['N2']
    can = d['canonical']
    if n.get('KH_effectively_zero') and not c.get('KH_effectively_zero'):
        for k in ('S', 'S_err', 'S_over_ref', 'units_from_ref'):
            can[k + '_raw'] = can.get(k)
            can[k] = None
        can['note'] = 'S 발산 — N₂@1.82 는 완전 차단(K_H 가 0 과 구별 안 됨), CO₂@1.65 는 차단 구 0(= 차단 없음)'
        can['divergent'] = True

    zero_r = [r for r in (1.50, 1.65, 1.82, 2.00) if rows[r]['CO2'].get('KH_effectively_zero') and rows[r]['N2'].get('KH_effectively_zero')]
    open_r = [r for r in (1.50, 1.65, 1.82, 2.00) if rows[r]['zeo_block'] and rows[r]['zeo_block']['n_spheres'] == 0]
    d['summary'] = (f'차단 구 0 인 반경 {open_r} → 차단 없음과 같음(같은 기기 재측 둘, 참조 laptop2 와의 거리는 행마다 *_units_from_unblocked). '
                    f'두 기체 모두 완전 차단된 반경 {zero_r} → S(r) 정의 안 됨. 정식 짝(CO₂@1.65 + N₂@1.82) 은 '
                    f'{"발산" if can.get("divergent") else "유한"}. 판정문은 종합자.')
    d['postprocess'] = {'script': 'magi5_e2b_post_junseok.py', 'time': datetime.datetime.now().strftime('%F %T'),
                        'criterion': f'K_H − ± ≤ 0 이고 K_H < {REL:g} × 차단 없음 참조(laptop2) → "0 과 구별 안 됨"',
                        'why': '드라이버는 K_H = 0 정확히일 때만 null — 수치상 0(1e-112 등)에서 뜻 없는 유한 비를 적었음. 원값은 *_raw 로 보존'}
    tmp = OUT + '.tmp'
    json.dump(d, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, OUT)
    for r in (1.50, 1.65, 1.82, 2.00):
        x = rows[r]
        print(f"  r={r:.2f} 구 {x['zeo_block']['n_spheres'] if x['zeo_block'] else '-'} · "
              f"CO₂ {x['CO2'].get('KH'):.3e} (0? {x['CO2'].get('KH_effectively_zero')}, 참조와 {x['CO2'].get('KH_units_from_unblocked')} 단위) · "
              f"N₂ {x['N2'].get('KH'):.3e} (0? {x['N2'].get('KH_effectively_zero')}, {x['N2'].get('KH_units_from_unblocked')} 단위) · "
              f"S {x.get('S')} ± {x.get('S_err')} {x.get('S_note') or ''} {('· 참조와 ' + str(x.get('S_units_from_unblocked')) + ' 단위') if x.get('S_units_from_unblocked') is not None else ''}")
    print(f"  정식 짝: S {can.get('S')} · {can.get('note')}")
    print(f"  요약: {d['summary']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
