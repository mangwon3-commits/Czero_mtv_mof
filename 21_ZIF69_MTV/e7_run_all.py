# -*- coding: utf-8 -*-
"""E-7 전체 — ① def2-SVP 로 자세 전부 거르기 ② 자리마다 (SVP 최저 · ff_min) 두 자세 def2-TZVP 최종. §2 고정 그대로.
결과 results_e7_dft_hkhome.json 에 행마다 저장(이어받기: 같은 site·pose·basis 가 converged 면 건너뜀). 끝나면 'finished': true."""
import json, os, time
import e7_dft as D
OUT = 'results_e7_dft_hkhome.json'
P = json.load(open('e7_poses.json', encoding='utf-8'))
R = json.load(open(OUT)) if os.path.exists(OUT) else {'rows': [], 'finished': False}
have = {(r['site'], r['pose'], r['basis']) for r in R['rows'] if r.get('converged')}


def run(site, pose, basis):
    if (site, pose, basis) in have:
        return next(r for r in R['rows'] if (r['site'], r['pose'], r['basis']) == (site, pose, basis))
    d = P[site]; w = [x for x in d['poses'] if x['pose'] == pose][0]
    D.energy.cycles = []
    t = time.time()
    e, conv = D.cp_bind(d['frag_symbols'], d['frag_xyz'], w['water'], basis, d.get('dft_charge', 0))
    row = {'site': site, 'pose': pose, 'basis': basis, 'E_dft': round(e, 3), 'E_ff': w['E_ff'], 'converged': conv,
           'scf_cycles': D.energy.cycles, 'seconds': round(time.time() - t, 1)}
    R['rows'] = [r for r in R['rows'] if (r['site'], r['pose'], r['basis']) != (site, pose, basis)]   # 수렴 못 한 옛 행 교체
    R['rows'].append(row); json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    return row


for site, d in P.items():                                   # ① 거르기
    for pose in dict.fromkeys(w['pose'] for w in d['poses']):   # 같은 이름 자세 중복 제거(S5a 주개 둘)
        run(site, pose, 'def2-svp')
for site, d in P.items():                                   # ② 최종
    svp = [r for r in R['rows'] if r['site'] == site and r['basis'] == 'def2-svp' and r['converged']]
    if not svp:
        print(f'!! {site}: 수렴한 SVP 자세 없음 — 최종 단계 건너뜀', flush=True); continue
    best = min(svp, key=lambda r: r['E_dft'])['pose']
    for pose in dict.fromkeys([best, 'ff_min']):
        run(site, pose, 'def2-tzvp')
R['finished'] = True; json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('E-7 완주', flush=True)
