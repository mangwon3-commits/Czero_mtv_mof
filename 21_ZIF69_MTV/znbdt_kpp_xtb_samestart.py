# -*- coding: utf-8 -*-
"""등록 K″ — xtb 클러스터: 같은 물 자리에서 출발한 카복실레이트 떼기 스캔.
등록 `ASSIGN_N2_KPP_20261113.md` §2(종합자 · 자료 0건에서 씀). `znbdt_kprime_xtb_detach.py`(de1c721b)의 사본이고 바꾼 것은 등록문의 넷뿐:
  1. 계열은 **물 있음 · 치환 쪽** 만. 출발을 K 의 가장 낮은 상태로 고르지 않고 **두 상태 `b_face_opp_Nb` · `b_hb_Ofree_unsub` 를 각각** 씀
     (`k_xtb_runs/<클러스터>/<상태>.end.xyz` · K 결과 JSON 과 대조 — K′ 와 같은 검사).
  2. 상태 이름 `kpp_fNb_p04 · p08 · p12 · p16 · p12_release` · `kpp_hbU_…`. 클러스터 아홉 × 출발 둘 × 최적화 5 = 90회.
  3. 점마다 `dE_kJmol` = E(그 점 · 끝 좌표에서 묶기 없이 한 한 점 계산) − E(그 출발 상태 · K 결과 JSON 의 값). K′ 의 E_ref · 주 점 고르기 · dE_swap 은 없음.
     기하 기록(두 O–Zn · Zn···C · d(Zn–O_w) · Zn 2.5 Å 안 목록 · 풀기 끝 상태)은 K′ 그대로.
  4. 결과 `results_znbdt_kpp_xtb_<기기>.json`. K′ 와 입력이 같은 계열(K′ 의 `kp_w_sub` 가 같은 상태에서 출발한 클러스터)도 **캐시로 받지 않고 다시 돌림**
     (상태 이름이 달라 작업 폴더가 새것 — K 모듈의 열쇠 이어받기는 같은 이름의 폴더에서만 듣는다). 그 계열에는 K′ 값과의 에너지 차(Eh)를 기계적 재현 기록으로 적음.
그 밖은 K′ 그대로 — K 의 스크립트 `znbdt_k_xtb_cluster.py` 를 **무수정 import** 해 자르기(build) · xtb 호출(run_xtb) · 끝 좌표 읽기(geom) · 결합 그래프(bonds)를 씀 ·
  고정 넷 = 서로 거리 여섯 묶기(강체 틀 · force constant 5.0) · 기본 최적화기 `--opt tight` · 모든 값은 끝 좌표에서 묶기 없이 한 한 점 계산 ·
  좌표 R = d(Zn···C_카복실)(치환 쪽) 을 **출발 상태의 값 + 0.4 → 0.8 → 1.2 → 1.6 Å** 로 묶고 나머지 최적화(앞 점의 끝 좌표에서 이어 감) ·
  풀기 = +1.2 점 끝 좌표에서 R 묶기만 풀고(틀 묶기는 그대로) 최적화 → 그 카복실레이트의 O 하나가 Zn 2.3 Å 안이면 "되붙음" · 두 O 모두 2.6 Å 밖이면 "떨어진 채" · 그 사이면 "그 밖(2.3~2.6 Å)" ·
  표지(K-4 + 여섯 거리 + 묶은 R 달성 |R − 목표| < 0.02 Å) · 한 번에 한 프로세스 · OMP_NUM_THREADS=1 · nice 19.
클러스터 사이의 차(ΔΔ) · ε″ · 판정은 적지 않음(종합자 · 등록문의 읽는 법).
산출 `results_znbdt_kpp_xtb_<기기>.json` · `k_xtb_runs/<클러스터>/kpp_*.start.xyz · .end.xyz`. 작업 폴더는 K 와 같은 저장소 밖 자리.
env  K_MACHINE(기본 hkhome) · KPP_ONLY=<클러스터 이름,…> · KPP_DRY=1(xtb 안 띄움 — 출발 상태 · R · 목표만 찍음)
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
OUT = os.path.join(HERE, f'results_znbdt_kpp_xtb_{MACHINE}.json')
KP_OUT = os.path.join(HERE, f'results_znbdt_kprime_xtb_{MACHINE}.json')
STRETCH = (0.4, 0.8, 1.2, 1.6)
ONLY = [x for x in os.environ.get('KPP_ONLY', '').split(',') if x]
DRY = bool(os.environ.get('KPP_DRY'))
STARTS = (('kpp_fNb', 'b_face_opp_Nb'), ('kpp_hbU', 'b_hb_Ofree_unsub'))      # (상태 이름 머리, K 의 출발 상태) — 등록 §2 의 두 물 자리
SIDE = 'sub'                                                                   # 떼는 쪽 = 치환 쪽 카복실레이트(등록 §2-1)
KP_SERIES = 'kp_w_sub'                                                         # K′ 에서 입력이 같을 수 있는 계열(물 있음 · 치환 쪽)


def md5f(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def carb(x, roles):
    """두 카복실레이트 각각: 두 O 의 Zn 거리 · Zn···C · 붙음(O 하나 < 2.3 Å) · 떨어짐(두 O 모두 > 2.6 Å)."""
    out = {}
    for sd in ('sub', 'unsub'):
        d = [float(np.linalg.norm(x[roles[f'o_{sd}']] - x[0])), float(np.linalg.norm(x[roles[f'ofree_{sd}']] - x[0]))]
        out[sd] = {'d_Zn_O_A': d, 'd_Zn_C_A': float(np.linalg.norm(x[roles[f'ccarb_{sd}']] - x[0])), 'attached_2p3': min(d) < 2.3, 'detached_2p6': min(d) > 2.6}
    return out


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
            raise SystemExit('!! K 결과가 아홉 클러스터 완주판이 아님 — K″ 착수 안 함')
        if kres['script_md5'] != md5f(kscript):
            raise SystemExit(f"!! K 결과를 만든 스크립트({kres['script_md5'][:8]})와 지금 import 한 스크립트({md5f(kscript)[:8]})가 다름 — 착수 안 함")
    kpres = json.load(open(KP_OUT, encoding='utf-8')) if os.path.exists(KP_OUT) else None
    picks = K.parent_picks()
    todo = [(t, k) for t, k in K.CLUSTERS if (not ONLY or f'{t}_zn{k}' in ONLY) and f'{t}_zn{k}' in kres['clusters']]
    out = {'test': '등록 K″ — xtb 클러스터: 같은 물 자리(K 의 b_face_opp_Nb · b_hb_Ofree_unsub)에서 출발한 치환 쪽 카복실레이트 떼기 스캔(R = d(Zn···C_카복실) + 풀기)',
           'assign': 'ASSIGN_N2_KPP_20261113.md §2', 'machine': MACHINE, 'script': os.path.basename(__file__), 'script_md5': md5f(os.path.abspath(__file__)),
           'copy_of': {'file': 'znbdt_kprime_xtb_detach.py', 'md5': md5f(os.path.join(HERE, 'znbdt_kprime_xtb_detach.py'))},
           'k_module': {'file': 'znbdt_k_xtb_cluster.py', 'md5': md5f(kscript)},
           'k_results': {'file': os.path.basename(K.OUT), 'md5': md5f(K.OUT), 'script_md5': kres.get('script_md5'), 'finished': kres.get('finished')},
           'kprime_results': ({'file': os.path.basename(KP_OUT), 'md5': md5f(KP_OUT), 'script_md5': kpres.get('script_md5'), 'finished': kpres.get('finished')} if kpres else None),
           'started': time.strftime('%F %T'), 'xtb': {'path': K.XTB, 'version': K.VERSION}, 'method': kres.get('method'), 'optimizer': kres.get('optimizer'),
           'anchor': kres.get('anchor'), 'anchor_pair_tol_A': K.ANCHOR_TOL, 'force_constant': K.FC, 'kJ_per_Eh': K.EH, 'stretch_A': list(STRETCH),
           'starts': [{'prefix': p, 'k_state': s} for p, s in STARTS], 'side': SIDE,
           'coordinate': 'R = d(Zn···C_카복실 · 치환 쪽) · 목표 = 출발 상태의 R + 늘림 · $constrain distance(조화) · 달성 |R − 목표| < 0.02 Å',
           'dE_rule': 'dE_kJmol = (E(그 점 · 끝 좌표에서 묶기 없이 한 한 점 계산) − E(그 출발 상태 · K 결과 JSON 의 energy_Eh)) × kJ_per_Eh',
           'attached_rule': '그 카복실레이트의 O 하나가 Zn 2.3 Å 안 = 붙음 · 두 O 모두 2.6 Å 밖 = 떨어짐',
           'same_input_as_kprime': 'K′ 의 kp_w_sub 가 같은 K 상태에서 출발한 계열 — 캐시로 받지 않고 다시 돌림 · rerun_minus_kprime_Eh 는 기계적 재현 기록',
           'only_env': ONLY, 'clusters': {},
           'note': '기계적 사실뿐 — 클러스터 사이의 차(ΔΔ) · ε″ · 판정은 적지 않음(종합자 · 등록 §2 읽는 법). 표지가 하나라도 빠진 상태의 값은 None(0 과 다름). '
                   '모든 energy_Eh 는 끝 좌표에서 묶기 없이 한 한 점 계산 값.'}

    def save(final=False):
        if final:
            out['finished'] = time.strftime('%F %T')
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        os.replace(tmp, OUT)

    print(f'등록 K″ — 기기 {MACHINE} · xtb {K.VERSION} · 클러스터 {len(todo)}/{len(K.CLUSTERS)} · 출발 {[s for _, s in STARTS]} · 드라이 {DRY} · '
          f'스크립트 {out["script_md5"][:8]} · K 모듈 {out["k_module"]["md5"][:8]} · K 결과 {out["k_results"]["md5"][:8]}(완주 {kres.get("finished")})', flush=True)
    for t, k in todo:
        name = f'{t}_zn{k}'
        syms, xyz, info = K.build(t, k, picks)
        roles, fixed = info['roles'], info['fixed_atoms_0based']
        KC = kres['clusters'][name]
        if KC['n_atoms'] != info['n_atoms'] or KC['roles'] != roles or KC['cif_md5'] != info['cif_md5'] or KC['fixed_atoms_0based'] != fixed:
            raise SystemExit(f'!! {name}: K 결과의 클러스터(원자 수 · 역할 · CIF md5 · 고정 넷)와 지금 자른 것이 다름')
        K.SYMS_CUR = list(syms) + ['O', 'H', 'H']
        cd = os.path.join(K.RUNS, name)
        starts = {}
        for pre, st in STARTS:
            rec = KC['states'].get(st)
            if not rec or rec.get('energy_Eh') is None:
                starts[pre] = None
                continue
            s_, x_ = K.read_xyz(os.path.join(cd, f'{st}.end.xyz'))
            if s_ != list(syms) + ['O', 'H', 'H']:
                raise SystemExit(f'!! {name}: {st}.end.xyz 의 원소 순서가 클러스터와 다름')
            for key, a, b in (('d_Zn_Osub_A', 0, roles['o_sub']), ('d_Zn_Ounsub_A', 0, roles['o_unsub'])):      # K 결과에 적힌 거리와 같은 좌표인가
                if abs(float(np.linalg.norm(x_[a] - x_[b])) - rec['geometry'][key]) > 1e-4:
                    raise SystemExit(f'!! {name}: {st}.end.xyz 가 K 결과 JSON 의 끝 좌표와 다름({key})')
            starts[pre] = (st, s_, x_, rec['energy_Eh'])
        KPC = (kpres or {}).get('clusters', {}).get(name)
        C = {'name': name, 'structure': t, 'zn_ordinal': k, 'n_atoms': info['n_atoms'], 'roles': roles, 'fixed_atoms_0based': fixed,
             'repeat_of': (f'{t}_zn1' if k == 2 else None), 'k_lowest_water_state': KC.get('lowest_water_state'), 'series': {}, 'states': {}}
        out['clusters'][name] = C
        print(f"== {name}: 원자 {info['n_atoms']} · K 의 가장 낮은 물 상태 {KC.get('lowest_water_state')}(출발 고르기에 쓰지 않음)", flush=True)

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

        for pre, _st in STARTS:
            S = {'water': True, 'side': SIDE, 'start_state': None, 'points': [], 'release': None}
            C['series'][pre] = S
            if starts[pre] is None:
                print(f'  {pre}: K 의 출발 상태 {_st} 값이 없음 — 이 계열은 돌리지 않음(값 None)', flush=True)
                continue
            st, s_, x0, e0 = starts[pre]
            i, j = 0, roles[f'ccarb_{SIDE}']
            r0 = float(np.linalg.norm(x0[j] - x0[i]))
            same = bool(KPC and (KPC['series'].get(KP_SERIES) or {}).get('start_state') == f'K:{st}')
            S.update(start_state=f'K:{st}', start_energy_Eh=e0, R0_A=r0, start_carboxylate=carb(x0, roles), start_k_geometry=KC['states'][st].get('geometry'),
                     same_input_as_kprime_series=(KP_SERIES if same else None))
            if DRY:
                gk = KC['states'][st].get('geometry') or {}
                print(f"  {pre:<8s} 출발 K:{st} · R0 {r0:.4f} Å(원자 1–{j + 1}) · 목표 {[round(r0 + d, 4) for d in STRETCH]} · 출발 두 O–Zn "
                      f"{[round(v, 3) for v in S['start_carboxylate'][SIDE]['d_Zn_O_A']]} · C–O {np.linalg.norm(x0[roles[f'o_{SIDE}']] - x0[j]):.3f} · "
                      f"{np.linalg.norm(x0[roles[f'ofree_{SIDE}']] - x0[j]):.3f} · d(Zn–Ow) {gk.get('d_Zn_Ow_A', float('nan')):.3f} · "
                      f"K′ 같은 입력 {KP_SERIES if same else '없음'}", flush=True)
                continue
            x, p12 = x0, None
            for dx in STRETCH:
                state = f'{pre}_p{int(round(dx * 10)):02d}'
                r, e, g = point(state, s_, x, (i, j, r0 + dx), 1)
                C['states'][state].update(scan={'series': pre, 'from_state': f'K:{st}', 'side': SIDE, 'R0_A': r0, 'stretch_A': dx},
                                          dE_kJmol=((e - e0) * K.EH if e is not None else None))
                S['points'].append(state)
                cs = g['carboxylate'][SIDE] if g else None
                print(f"  {state:<20s} 표지 {r['markers_ok']} · 수렴 {r.get('converged')} · E {e} · {r['seconds']} s{' · cached' if r['cached'] else ''}"
                      + (f" · R {r['constraint']['achieved_A']:.4f}/{r0 + dx:.4f}" if r['constraint'].get('achieved_A') else '')
                      + (f" · 두 O–Zn {cs['d_Zn_O_A'][0]:.3f} {cs['d_Zn_O_A'][1]:.3f}" if cs else '')
                      + (f" · d(Zn–Ow) {g['d_Zn_Ow_A']:.3f}" if g else ''), flush=True)
                if r.get('end_xyz') is None or not r['markers_ok']:
                    break                                           # 앞 점이 빠지면 그 계열의 뒤 점은 돌리지 않음(값 None)
                x = np.array(r['end_xyz'])
                if abs(dx - 1.2) < 1e-9:
                    p12 = x
            if p12 is not None:                                     # 풀기: +1.2 점에서 R 묶기만 풂
                state = f'{pre}_p12_release'
                r, e, g = point(state, s_, p12, None, 1)
                rs = None
                if g:
                    cs = g['carboxylate'][SIDE]
                    rs = '되붙음' if cs['attached_2p3'] else ('떨어진 채' if cs['detached_2p6'] else '그 밖(2.3~2.6 Å)')
                    g['release_state'] = rs
                    g['water_within_2p5A_of_Zn'] = bool(g['d_Zn_Ow_A'] < 2.5)
                C['states'][state].update(release={'series': pre, 'side': SIDE, 'from_state': f'{pre}_p12'},
                                          dE_kJmol=((e - e0) * K.EH if e is not None else None))
                S['release'] = state
                print(f"  {state:<20s} 표지 {r['markers_ok']} · 수렴 {r.get('converged')} · E {e} · {r['seconds']} s{' · cached' if r['cached'] else ''}"
                      + (f" · {rs} · 두 O–Zn {cs['d_Zn_O_A'][0]:.3f} {cs['d_Zn_O_A'][1]:.3f} · d(Zn–Ow) {g['d_Zn_Ow_A']:.3f}" if g else ''), flush=True)
            # 등록 §2-3 의 값: 점마다 dE = E(점) − E(출발 상태 · K 값). 풀기 끝 상태의 값은 따로 적음.
            S['dE_kJmol'] = {p: C['states'][p].get('dE_kJmol') for p in S['points']}
            S['dE_release_kJmol'] = C['states'][S['release']].get('dE_kJmol') if S['release'] else None
            if same:                                                # 같은 입력의 K′ 계열과 에너지 차(Eh) — 기계적 재현 기록
                d = {}
                for p in S['points'] + ([S['release']] if S['release'] else []):
                    q = KPC['states'].get(p.replace(pre, KP_SERIES, 1)) or {}
                    ea, eb = C['states'][p].get('energy_Eh'), q.get('energy_Eh')
                    d[p] = (ea - eb) if (ea is not None and eb is not None) else None
                S['rerun_minus_kprime_Eh'] = d
            save()
        if DRY:
            continue
        save()
    if not DRY:
        n_all = sum(len(c['states']) for c in out['clusters'].values())
        n_ok = sum(1 for c in out['clusters'].values() for s in c['states'].values() if s.get('energy_Eh') is not None)
        out['counts'] = {'states_run': n_all, 'states_with_value': n_ok, 'clusters': len(out['clusters']), 'states_expected': len(todo) * len(STARTS) * (len(STRETCH) + 1)}
        save(final=True)
        print(f'저장 {OUT} · 상태 {n_all} · 값 있는 상태 {n_ok}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
