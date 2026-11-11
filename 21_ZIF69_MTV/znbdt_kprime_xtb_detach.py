# -*- coding: utf-8 -*-
"""등록 K′ — xtb 클러스터 보완: 카복실레이트를 Zn 에서 통째로 떼는 에너지.
등록 `ASSIGN_DURABILITY_JK_20261111.md` §K′(14:3x · K′ 자료 0건) · §K-9(종합자 답: 틀 묶기 · 한 점 에너지 · 기울인 물 출발 받음) · `COMMS/cloud.md` 11-11 14:3x.
K 의 스크립트 `znbdt_k_xtb_cluster.py` 를 **무수정 import** 해 자르기(build) · xtb 호출(run_xtb) · 끝 좌표 읽기(geom) · 결합 그래프(bonds)를 그대로 씀 —
  고정 넷 = 서로 거리 여섯 묶기(강체 틀 · force constant 5.0) · 기본 최적화기 `--opt tight` · 모든 값은 끝 좌표에서 묶기 없이 한 한 점 계산 · 이어받기는 입력 열쇠가 같고 표지가 통과한 것만.
이 파일이 더하는 것(등록 §K′ 그대로):
  · 좌표 R = d(Zn···C_카복실)(두 O 를 가진 C · 이 Zn 에 붙은 쪽). R 을 **출발 상태의 값 + 0.4 → 0.8 → 1.2 → 1.6 Å** 로 묶고 나머지 최적화(앞 점의 끝 좌표에서 이어 감).
  · 계열 셋: (가) 물 있음 · 치환 쪽 카복실레이트 `kp_w_sub` · (나) 물 있음 · 무치환 쪽 `kp_w_unsub` · (다) 물 없음 · 치환 쪽 `kp_dry_sub`.
    출발은 K 의 (c) 와 같은 상태 — 물 있음 = K 의 가장 낮은 물 붙은 상태의 끝 좌표 · 물 없음 = K (a) 의 끝 좌표(`k_xtb_runs/<클러스터>/<상태>.end.xyz` · K 결과 JSON 과 대조).
  · 풀기: (가) · (나) 의 +1.2 점 끝 좌표에서 R 묶기만 풀고(틀 묶기는 그대로) 최적화 → 그 카복실레이트의 O 하나가 Zn 2.3 Å 안이면 "되붙음" ·
    두 O 모두 2.6 Å 밖이면 "떨어진 채"(물 O 가 Zn 2.5 Å 안인지 적음) · 그 사이면 "그 밖(2.3~2.6 Å)".
  · 점마다: 두 카복실레이트 각각의 두 O–Zn 거리 · d(Zn···C) · d(Zn–O_w) · Zn 2.5 Å 안 N · O 목록 · 결합 차수 · 표지(K-4 + 여섯 거리 + 묶은 R 달성 |R − 목표| < 0.02 Å).
  클러스터당 최적화 14회(3 × 4 + 풀기 2) × 9 = 126회. 한 번에 한 프로세스 · OMP_NUM_THREADS=1 · nice 19.
  · 클러스터 안에서 등록이 정한 값만 적음(클러스터 사이의 차 · 순위 · 판정은 적지 않음 — 종합자):
    E_ref(계열마다) = 그 클러스터 · 같은 물 수에서 K 와 K′ 를 통틀어 **묶기 없이 끝난 상태** 가운데 그 카복실레이트가 "붙은"(O 하나가 Zn 2.3 Å 안) 것의 가장 낮은 에너지
      — 후보: 물 없음 = K (a) · 물 있음 = K (b) 여섯 + K′ 풀기 둘. 묶은 점은 후보가 아님. 어느 상태였는지 적음.
    dE_detach(점마다) = E(점) − E_ref. 주 점은 +1.2(그 점에서 두 O 가 모두 2.6 Å 밖이 아니면 +1.6 을 주 점으로 하고 그렇게 적음).
    dE_swap = E("떨어진 채" 이고 물이 Zn 2.5 Å 안인 풀기 끝 상태) − E_ref(그런 상태가 있을 때만).
산출 `results_znbdt_kprime_xtb_<기기>.json` · `k_xtb_runs/<클러스터>/kp_*.start.xyz · .end.xyz`. 작업 폴더는 K 와 같은 저장소 밖 자리.
env  K_MACHINE(기본 hkhome) · KP_ONLY=<클러스터 이름,…> · KP_DRY=1(xtb 안 띄움 — K 결과가 있는 클러스터의 출발 상태 · R · 목표만 찍음)
"""
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for _v in ('K_ONLY', 'K_STATES', 'K_CUT_ONLY'):
    os.environ.pop(_v, None)                          # K 모듈의 선택 env 는 여기서 안 씀
import znbdt_k_xtb_cluster as K   # noqa: E402  (main 은 안 부름 — 함수만)

MACHINE = K.MACHINE
OUT = os.path.join(HERE, f'results_znbdt_kprime_xtb_{MACHINE}.json')
STRETCH = (0.4, 0.8, 1.2, 1.6)
ONLY = [x for x in os.environ.get('KP_ONLY', '').split(',') if x]
DRY = bool(os.environ.get('KP_DRY'))
B_STATES = ('b_face_opp_Na', 'b_face_opp_Nb', 'b_face_opp_Osub', 'b_face_opp_Ounsub', 'b_hb_Ofree_sub', 'b_hb_Ofree_unsub')
SERIES = (('kp_w_sub', True, 'sub'), ('kp_w_unsub', True, 'unsub'), ('kp_dry_sub', False, 'sub'))


def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def carb(x, roles):
    """두 카복실레이트 각각: 두 O 의 Zn 거리 · Zn···C · 붙음(O 하나 < 2.3 Å) · 떨어짐(두 O 모두 > 2.6 Å)."""
    out = {}
    for sd in ('sub', 'unsub'):
        d = [float(np.linalg.norm(x[roles[f'o_{sd}']] - x[0])), float(np.linalg.norm(x[roles[f'ofree_{sd}']] - x[0]))]
        out[sd] = {'d_Zn_O_A': d, 'd_Zn_C_A': float(np.linalg.norm(x[roles[f'ccarb_{sd}']] - x[0])), 'attached_2p3': min(d) < 2.3, 'detached_2p6': min(d) > 2.6}
    return out


def carb_from_k(g):
    """K 결과 JSON 의 geometry 칸에서 같은 판정(붙음)."""
    return {sd: min(g[f'd_Zn_O{sd}_A'], g[f'd_Zn_Ofree_{sd}_A']) < 2.3 for sd in ('sub', 'unsub')}


def main():
    try:
        os.nice(19)
    except OSError:
        pass
    K.VERSION = K.xtb_version()
    if not K.VERSION and not DRY:
        raise SystemExit(f'!! xtb 가 안 돎({K.XTB}) — 환경을 바꾸지 않고 멈춤')
    kres = json.load(open(K.OUT, encoding='utf-8'))
    kscript = os.path.join(HERE, 'znbdt_k_xtb_cluster.py')
    if not DRY:
        if 'finished' not in kres or kres.get('only_env') or len(kres['clusters']) != len(K.CLUSTERS):
            raise SystemExit('!! K 결과가 아홉 클러스터 완주판이 아님 — K′ 착수 안 함')
        if kres['script_md5'] != md5f(kscript):
            raise SystemExit(f"!! K 결과를 만든 스크립트({kres['script_md5'][:8]})와 지금 import 한 스크립트({md5f(kscript)[:8]})가 다름 — 착수 안 함")
    picks = K.parent_picks()
    todo = [(t, k) for t, k in K.CLUSTERS if (not ONLY or f'{t}_zn{k}' in ONLY) and f'{t}_zn{k}' in kres['clusters']]
    out = {'test': '등록 K′ — xtb 클러스터 보완: 카복실레이트를 Zn 에서 통째로 떼는 에너지(R = d(Zn···C_카복실) 스캔 + 풀기)',
           'assign': 'ASSIGN_DURABILITY_JK_20261111.md §K′ · §K-9', 'machine': MACHINE, 'script': os.path.basename(__file__), 'script_md5': md5f(os.path.abspath(__file__)),
           'k_module': {'file': 'znbdt_k_xtb_cluster.py', 'md5': md5f(kscript)},
           'k_results': {'file': os.path.basename(K.OUT), 'md5': md5f(K.OUT), 'script_md5': kres.get('script_md5'), 'finished': kres.get('finished')},
           'started': time.strftime('%F %T'), 'xtb': {'path': K.XTB, 'version': K.VERSION}, 'method': kres.get('method'), 'optimizer': kres.get('optimizer'),
           'anchor': kres.get('anchor'), 'anchor_pair_tol_A': K.ANCHOR_TOL, 'force_constant': K.FC, 'kJ_per_Eh': K.EH, 'stretch_A': list(STRETCH),
           'coordinate': 'R = d(Zn···C_카복실) · 목표 = 계열 출발 상태의 R + 늘림 · $constrain distance(조화) · 달성 |R − 목표| < 0.02 Å',
           'attached_rule': '그 카복실레이트의 O 하나가 Zn 2.3 Å 안 = 붙음 · 두 O 모두 2.6 Å 밖 = 떨어짐', 'only_env': ONLY, 'clusters': {},
           'note': '기계적 사실뿐 — 클러스터 사이의 차 · 순위 · 판정은 적지 않음(종합자 · 등록 §K′ 읽는 법). 표지가 하나라도 빠진 상태의 값은 None(0 과 다름). '
                   '모든 energy_Eh 는 끝 좌표에서 묶기 없이 한 한 점 계산 값.'}

    def save(final=False):
        if final:
            out['finished'] = time.strftime('%F %T')
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        os.replace(tmp, OUT)

    print(f'등록 K′ — 기기 {MACHINE} · xtb {K.VERSION} · 클러스터 {len(todo)}/{len(K.CLUSTERS)} · 드라이 {DRY} · K 결과 {out["k_results"]["md5"][:8]}(완주 {kres.get("finished")})', flush=True)
    for t, k in todo:
        name = f'{t}_zn{k}'
        syms, xyz, info = K.build(t, k, picks)
        roles, fixed = info['roles'], info['fixed_atoms_0based']
        KC = kres['clusters'][name]
        if KC['n_atoms'] != info['n_atoms'] or KC['roles'] != roles or KC['cif_md5'] != info['cif_md5'] or KC['fixed_atoms_0based'] != fixed:
            raise SystemExit(f'!! {name}: K 결과의 클러스터(원자 수 · 역할 · CIF md5 · 고정 넷)와 지금 자른 것이 다름')
        K.SYMS_CUR = list(syms) + ['O', 'H', 'H']
        cd = os.path.join(K.RUNS, name)
        low = KC.get('lowest_water_state')
        starts = {}
        for pre, wat, side in SERIES:
            st = low if wat else 'a_nowater'
            rec = KC['states'].get(st) if st else None
            if not rec or rec.get('energy_Eh') is None:
                starts[pre] = None
                continue
            s_, x_ = K.read_xyz(os.path.join(cd, f'{st}.end.xyz'))
            if s_ != list(syms) + (['O', 'H', 'H'] if wat else []):
                raise SystemExit(f'!! {name}: {st}.end.xyz 의 원소 순서가 클러스터와 다름')
            for key, a, b in (('d_Zn_Osub_A', 0, roles['o_sub']), ('d_Zn_Ounsub_A', 0, roles['o_unsub'])):      # K 결과에 적힌 거리와 같은 좌표인가
                if abs(float(np.linalg.norm(x_[a] - x_[b])) - rec['geometry'][key]) > 1e-4:
                    raise SystemExit(f'!! {name}: {st}.end.xyz 가 K 결과 JSON 의 끝 좌표와 다름({key})')
            starts[pre] = (st, s_, x_, rec['energy_Eh'])
        C = {'name': name, 'structure': t, 'zn_ordinal': k, 'n_atoms': info['n_atoms'], 'roles': roles, 'fixed_atoms_0based': fixed,
             'repeat_of': (f'{t}_zn1' if k == 2 else None), 'k_lowest_water_state': low, 'series': {}, 'states': {}}
        out['clusters'][name] = C
        print(f"== {name}: 원자 {info['n_atoms']} · 물 있음 출발 {low} · 물 없음 출발 a_nowater", flush=True)

        def point(state, s_, x_, constraint, nw):
            r = K.run_xtb(os.path.join(K.WORK, name, state), s_, x_, fixed, constraint, anchor_ref=xyz)
            K.write_xyz(os.path.join(cd, f'{state}.start.xyz'), s_, x_, f'{name} {state} start')
            rec, e = dict(K.public(r)), None
            if r['markers_ok']:
                sp = K.run_xtb(os.path.join(K.WORK, name, state, 'sp'), s_, np.array(r['end_xyz']), fixed, None, opt=False)
                rec['single_point'] = K.public(sp)
                e = sp['energy_Eh_raw'] if sp['markers_ok'] else None
            rec['energy_Eh_with_restraint'] = r['energy_Eh_raw']
            rec['energy_Eh'] = e
            g = None
            if r.get('end_xyz') is not None:
                xe = np.array(r['end_xyz'])
                K.write_xyz(os.path.join(cd, f'{state}.end.xyz'), s_, xe, f'{name} {state} end E={e} Eh markers_ok={r["markers_ok"]}')
                b0, b1 = K.bonds(s_, x_), K.bonds(s_, xe)
                rec['topology_same_as_start'] = b0 == b1
                if b0 != b1:
                    rec['topology_diff'] = {'broken': [list(q) for q in sorted(set(b0) - set(b1))], 'formed': [list(q) for q in sorted(set(b1) - set(b0))]}
                if e is not None:
                    g = K.geom(r, roles, nw)
                    g['carboxylate'] = carb(xe, roles)
            rec['geometry'] = g
            C['states'][state] = rec
            save()
            return r, e, g

        for pre, wat, side in SERIES:
            S = {'water': wat, 'side': side, 'start_state': None, 'points': [], 'release': None}
            C['series'][pre] = S
            if starts[pre] is None:
                print(f'  {pre}: K 의 출발 상태 값이 없음 — 이 계열은 돌리지 않음(값 None)', flush=True)
                continue
            st, s_, x0, e0 = starts[pre]
            i, j = 0, roles[f'ccarb_{side}']
            r0 = float(np.linalg.norm(x0[j] - x0[i]))
            S.update(start_state=f'K:{st}', start_energy_Eh=e0, R0_A=r0, start_carboxylate=carb(x0, roles))
            if DRY:
                print(f"  {pre:<11s} 출발 K:{st} · R0 {r0:.4f} Å(원자 1–{j + 1}) · 목표 {[round(r0 + d, 4) for d in STRETCH]} · 출발 두 O–Zn "
                      f"{[round(v, 3) for v in S['start_carboxylate'][side]['d_Zn_O_A']]} · C–O {np.linalg.norm(x0[roles[f'o_{side}']] - x0[j]):.3f} · "
                      f"{np.linalg.norm(x0[roles[f'ofree_{side}']] - x0[j]):.3f}", flush=True)
                continue
            x, p12 = x0, None
            for dx in STRETCH:
                state = f'{pre}_p{int(round(dx * 10)):02d}'
                r, e, g = point(state, s_, x, (i, j, r0 + dx), 1 if wat else 0)
                C['states'][state].update(scan={'series': pre, 'from_state': f'K:{st}', 'side': side, 'R0_A': r0, 'stretch_A': dx})
                S['points'].append(state)
                cs = g['carboxylate'][side] if g else None
                print(f"  {state:<16s} 표지 {r['markers_ok']} · 수렴 {r.get('converged')} · E {e} · {r['seconds']} s{' · cached' if r['cached'] else ''}"
                      + (f" · R {r['constraint']['achieved_A']:.4f}/{r0 + dx:.4f}" if r['constraint'].get('achieved_A') else '')
                      + (f" · 두 O–Zn {cs['d_Zn_O_A'][0]:.3f} {cs['d_Zn_O_A'][1]:.3f}" if cs else '')
                      + (f" · d(Zn–Ow) {g['d_Zn_Ow_A']:.3f}" if g and wat else ''), flush=True)
                if r.get('end_xyz') is None or not r['markers_ok']:
                    break                                           # 앞 점이 빠지면 그 계열의 뒤 점은 돌리지 않음(값 None)
                x = np.array(r['end_xyz'])
                if abs(dx - 1.2) < 1e-9:
                    p12 = x
            if wat and p12 is not None:                             # 풀기: +1.2 점에서 R 묶기만 풂
                state = f'{pre}_p12_release'
                r, e, g = point(state, s_, p12, None, 1)
                rs = None
                if g:
                    cs = g['carboxylate'][side]
                    rs = '되붙음' if cs['attached_2p3'] else ('떨어진 채' if cs['detached_2p6'] else '그 밖(2.3~2.6 Å)')
                    g['release_state'] = rs
                    g['water_within_2p5A_of_Zn'] = bool(g['d_Zn_Ow_A'] < 2.5)
                C['states'][state].update(release={'series': pre, 'side': side, 'from_state': f'{pre}_p12'})
                S['release'] = state
                print(f"  {state:<16s} 표지 {r['markers_ok']} · 수렴 {r.get('converged')} · E {e} · {r['seconds']} s{' · cached' if r['cached'] else ''}"
                      + (f" · {rs} · 두 O–Zn {cs['d_Zn_O_A'][0]:.3f} {cs['d_Zn_O_A'][1]:.3f} · d(Zn–Ow) {g['d_Zn_Ow_A']:.3f}" if g else ''), flush=True)
            save()
        if DRY:
            continue
        # 클러스터 안의 등록 값: E_ref · dE_detach · dE_swap
        cand = {False: [], True: []}
        ga = KC['states']['a_nowater']
        if ga.get('energy_Eh') is not None:
            cand[False].append(('K:a_nowater', ga['energy_Eh'], carb_from_k(ga['geometry'])))
        for s in B_STATES:
            gb = KC['states'].get(s)
            if gb and gb.get('energy_Eh') is not None:
                cand[True].append((f'K:{s}', gb['energy_Eh'], carb_from_k(gb['geometry'])))
        for pre, wat, side in SERIES:
            rl = C['series'][pre].get('release')
            if rl and C['states'][rl].get('energy_Eh') is not None:
                gg = C['states'][rl]['geometry']['carboxylate']
                cand[True].append((f'K′:{rl}', C['states'][rl]['energy_Eh'], {sd: gg[sd]['attached_2p3'] for sd in ('sub', 'unsub')}))
        for pre, wat, side in SERIES:
            S = C['series'][pre]
            ok = [(e, n) for n, e, att in cand[wat] if att[side]]
            S['E_ref_candidates'] = [{'state': n, 'energy_Eh': e, 'attached': att[side]} for n, e, att in cand[wat]]
            if not ok or not S['points']:
                S['E_ref'] = None
                continue
            eref, nref = min(ok)
            S['E_ref'] = {'state': nref, 'energy_Eh': eref}
            S['dE_detach_kJmol'] = {p: ((C['states'][p]['energy_Eh'] - eref) * K.EH if C['states'][p].get('energy_Eh') is not None else None) for p in S['points']}
            g12 = (C['states'].get(f'{pre}_p12') or {}).get('geometry')
            det12 = bool(g12 and g12['carboxylate'][side]['detached_2p6'])
            S['both_O_beyond_2p6A_at_p12'] = det12 if g12 else None
            S['main_point'] = f'{pre}_p12' if det12 else f'{pre}_p16'
            S['dE_detach_main_kJmol'] = S['dE_detach_kJmol'].get(S['main_point'])
            rl = S.get('release')
            if rl and C['states'][rl].get('energy_Eh') is not None:
                gr = C['states'][rl]['geometry']
                if gr.get('release_state') == '떨어진 채' and gr.get('water_within_2p5A_of_Zn'):
                    S['dE_swap_kJmol'] = (C['states'][rl]['energy_Eh'] - eref) * K.EH
        save()
    if not DRY:
        n_all = sum(len(c['states']) for c in out['clusters'].values())
        n_ok = sum(1 for c in out['clusters'].values() for s in c['states'].values() if s.get('energy_Eh') is not None)
        out['counts'] = {'states_run': n_all, 'states_with_value': n_ok, 'clusters': len(out['clusters'])}
        save(final=True)
        print(f'저장 {OUT} · 상태 {n_all} · 값 있는 상태 {n_ok}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
