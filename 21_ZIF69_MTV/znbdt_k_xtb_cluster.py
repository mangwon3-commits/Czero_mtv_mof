# -*- coding: utf-8 -*-
"""등록 K — xtb 클러스터: Zn 마디 하나를 잘라 물 붙는 에너지와 물이 있을 때 Zn–O 를 늘리는 에너지를 잰다.
등록 `ASSIGN_DURABILITY_JK_20261111.md` §K(자료 0건 · 읽는 법 · 예측 고정) · `ASSIGN_MIDNIGHT_20261111.md` §4-1(HKHOME · 부수 작업 한 프로세스).
이 파일은 자르기 + 실행 + 표지만 한다 — **값의 차 · 순위 · 판정은 적지 않는다**(종합자 · §K-5).

[K-2 자르기] `charged_v3/<tag>_DDEC6.cif` 의 좌표만 씀(전하 열은 안 씀). 결합은 공유 반지름 × 1.15 · 최소상 규약으로 잇고, 분자는 셀 이동을 들고 따라가며 편다
  (같은 원자가 두 가지 셀 이동으로 닿으면 멈춤 — CLAUDE.md §0 주기 경계 언랩).
  · Zn 하나(CIF 순서 k 번째) + 배위한 이미다졸 둘은 1-메틸이미다졸로: 고리 5 + 고리 H 3 + N1 에 붙은 CH₂(C 1 · H 2) + 끊은 C–C 방향 1.09 Å 에 H 1 = 12원자.
  · 배위한 bdtdc 둘은 링커 전체 + 먼 쪽 카복실레이트에서 **다른 Zn 에 붙어 있던 O** 에 H 하나(O→그 Zn 방향 0.97 Å) → 중성.
  · 전하 0 · 닫힌 껍질(전자 수 짝수 확인). 원자 수: 모체 71 = 1 + 12 × 2 + 23 × 2 · 치환판은 치환기만큼 더.
  · 고정 원자(격자 흉내): 두 메틸 C 와 두 먼 쪽 카복실 C — 넷의 서로 거리 여섯을 묶은 강체 틀(아래 [K-3 고정 · 최적화기]).
  · "치환 쪽" O = 치환 링커(조성이 C12H4O4S2 가 아닌 쪽)의 배위 O · "무치환 쪽" = 다른 링커의 배위 O.
    모체는 두 링커가 같으므로 **설계 구조 여섯의 치환 링커 배위 O 와 같은 자리(같은 셀 · 최소상 거리)의 O** 를 "치환 쪽" 으로 고르고 겹침 거리를 적음(여섯이 같은 O 를 가리키지 않으면 멈춤).
  · 클러스터 9 = 구조 7 × 첫 Zn + 반복 2(모체 · −CN 의 둘째 Zn).
[K-3 계산] GFN2-xTB · 기체상 · `--opt tight` · 전하 0 · 한 번에 한 프로세스 · OMP_NUM_THREADS=1 · nice 19.
  (a) 물 없는 클러스터 최적화 → E₀ · d(Zn–O) 둘 · Wiberg 결합 차수 둘.
  (b) 물 하나 · 출발 6: ZnN₂O₂ 사면체의 네 면 방향(그 면의 세 리간드 단위벡터 합 방향)으로 Zn 에서 2.2 Å(H 는 Zn 반대쪽 · 방위각은 가장 덜 부딪치는 쪽) ·
      치환 링커의 비배위 O 에 수소결합 · 무치환 링커의 비배위 O 에 수소결합(O_w 는 그 O 에서 C→O 방향 2.8 Å · 부딪치면 원뿔 위에서 비킴 — 비킨 각을 적음).
      끝 상태: d(Zn–O_w) < 2.5 Å → "Zn 배위" · 아니고 물 H···비배위 O < 2.2 Å → "비배위 O 수소결합" · 그 밖. ΔE_w = E − E₀ − E(H₂O).
      ⚠ 네 면 가운데 둘(Osub 맞은편 · Ounsub 맞은편)은 **다른 링커의 비배위 O 가 Zn 에서 약 3.0 Å 로 그 면을 막고 있어** 등록 자리(면 법선 · 2.2 Å)의
      O_w 가 그 O 에서 1.2~1.5 Å 가 됨. 그런 면은 Zn 에서 2.2 Å 를 지킨 채 **가장 조금 기울인 자리**(O_w 가 Zn 아닌 원자에서 ≥ 1.9 Å · H ≥ 1.4 Å 가 되는
      첫 5° 단계 · 그 단계에서 가장 덜 부딪치는 방위)에서 출발하고, 기울임 각과 등록 자리의 최소 거리를 상태마다 적음(`start` 칸). 막히지 않은 면은 등록 자리 그대로.
      부가 사실(값을 None 으로 만들지 않음): 물 O–H 길이 · 공유 결합 그래프가 출발과 같은지(`topology_same_as_start`) — 양성자 이동 같은 다른 화학종이 섞였는지 볼 자리.
  (c) 늘리기(완화 스캔): 가장 낮은 물 붙은 상태에서 d(Zn–O) 를 그 상태의 값 + 0.4 → 0.8 → 1.2 Å 로 묶고(앞 점의 끝 좌표에서 이어 감) 나머지 최적화 —
      치환 쪽 O · 무치환 쪽 O 각각. 물 없는 클러스터((a)의 끝)에서도 치환 쪽 O 만. 묶은 거리 달성은 |d − 목표| < 0.02 Å.
  클러스터당 최적화 16회(a 1 + b 6 + c 9) × 9 = 144회 + 물 분자 1회. 한 점 계산은 최적화 수에 안 셈.
[K-3 고정 · 최적화기 — 등록의 "직교좌표 고정" 을 이 xtb 로는 그대로 못 해서 바꾼 것(자료를 읽기 전 · 모체 시험 11-11 13:35~13:55)]
  · xtb 6.7.1 의 기본 최적화기(ANC)는 `$fix` 를 지키지 않음: 모체 (a)에서 고정 원자가 0.11~0.19 Å 움직이고 넷 사이 거리도 0.20 Å 바뀜(표지가 걸러냄).
  · `$opt engine=lbfgs`(L-ANC)는 `$fix` 를 지키지만(이동 3e-5 Å) ① 거리 묶기(`$constrain`)가 있으면 engine 지정이 무시되어 다시 안 지켜지고(0.08~0.30 Å)
    ② 같은 tight 문턱에서 20걸음 만에 멈춰 기본 최적화기보다 1 kJ/mol 쯤 위에 섬 — 기준 상태와 늘린 점의 최적화기가 다르면 그 차가 ΔE 에 섞임.
  · 그래서 **모든 최적화(a · b · c)를 기본 최적화기 + 고정 넷의 서로 거리 여섯을 자른 구조의 값으로 묶기**(`$constrain distance` · 조화 · force constant 5.0 Eh/bohr²)로 통일.
    고정 넷은 강체 틀이 됨 — 틀 전체의 이동 · 회전은 기체상 에너지에 뜻이 없음. 시험에서 넷 사이 거리 변화 3e-4 Å. 판정은 < 2e-3 Å(자료를 보기 전에 정함).
  · 묶기 에너지가 섞이지 않게 **모든 상태의 energy_Eh 는 끝 좌표에서 묶기 없이 다시 한 한 점 계산 값**.
  · 시험에서 본 것(판정 아님): 모체 물 없는 클러스터는 Zn–O 를 0.4 Å 늘린 점에서 묶기를 풀면 자른 구조에서 내려간 최소(4배위)보다 19.8 kJ/mol 낮은 다른 최소로 감
    (d(Zn–O) 2.09 · 2.12 Å · 원자 이동 최대 2.4 Å). 곧 완화 스캔 값에는 배위 모양이 바뀌는 완화가 섞일 수 있음 — 상태마다 Zn 2.5 Å 안 N · O 목록 · Zn···비배위 O 거리를 적어 둠.
[K-4 표지] xtb 정상 종료 문구 · 최적화 수렴 문구 · 고정 넷의 서로 거리 불변(< 2e-3 Å · 위 [K-3 고정 · 최적화기]) · 전하 0 · 원자 수 · xtb 판 · 묶은 거리 달성. **하나라도 빠지면 그 상태의 값은 None**(0 과 다름).
[산출] `results_znbdt_k_xtb_<기기>.json`(상태가 하나 끝날 때마다 통째로 다시 씀) · `k_xtb_runs/<클러스터>/<상태>.start.xyz · .end.xyz`. xtb 작업 폴더 · 로그는 저장소 밖
  `~/.mof_chain/k_xtb_work_<기기>/`.
[이어받기] 상태마다 입력 열쇠(출발 좌표 · 제어 입력 · 명령줄 · xtb 판의 md5)를 작업 폴더에 남기고, **열쇠가 같고 표지가 전부 통과한 상태만** 다시 쓰며 `cached` 로 표시
  (출력 파일이 있다는 것만으로는 안 씀 — CLAUDE.md §3).
env  K_MACHINE(기본 hkhome) · K_ONLY=<클러스터 이름,…> · K_STATES=a | ab | abc(기본 abc) · K_CUT_ONLY=1(자르기 · 출발 좌표만 · xtb 안 띄움)
"""
import hashlib
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import time
from collections import Counter, deque

import numpy as np
from ase import Atoms
from ase.data import atomic_numbers
from ase.io import read
from ase.neighborlist import natural_cutoffs, neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
MACHINE = os.environ.get('K_MACHINE', 'hkhome')
XTB = shutil.which('xtb') or os.path.join(os.path.dirname(sys.executable), 'xtb')
WORK = os.path.expanduser(f'~/.mof_chain/k_xtb_work_{MACHINE}')
RUNS = os.path.join(HERE, 'k_xtb_runs')
OUT = os.path.join(HERE, f'results_znbdt_k_xtb_{MACHINE}.json')
TAGS = ('e22_parent', 'e24i_ch3_open', 'e24i_c2h5_open', 'e24i_cl_open', 'e24i_br_open', 'e24i_cn_open', 'e24i_no2_open')
DESIGNS = TAGS[1:]
CLUSTERS = [(t, 1) for t in TAGS] + [('e22_parent', 2), ('e24i_cn_open', 2)]          # (구조, 몇 번째 Zn) — 뒤 둘이 반복
UNSUB = Counter({'C': 12, 'H': 4, 'O': 4, 'S': 2})
EH = 2625.499639                 # kJ/mol per Eh
FC = 5.0                         # 거리 묶기 force constant(Eh/bohr²)
STRETCH = (0.4, 0.8, 1.2)
ANCHOR_TOL = 2e-3                # 고정 넷의 서로 거리 불변 판정(Å · 자른 구조의 값 대비)
CUT_ONLY = bool(os.environ.get('K_CUT_ONLY'))
ONLY = [x for x in os.environ.get('K_ONLY', '').split(',') if x]
STATES = os.environ.get('K_STATES', 'abc')
ENV = dict(os.environ, OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', OMP_STACKSIZE='2G')


def md5b(b):
    return hashlib.md5(b).hexdigest()


def unit(v):
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------- 자르기
def graph(a):
    i, j, S = neighbor_list('ijS', a, natural_cutoffs(a, mult=1.15))
    nb = {k: [] for k in range(len(a))}
    for ii, jj, ss in zip(i, j, S):
        nb[int(ii)].append((int(jj), (int(ss[0]), int(ss[1]), int(ss[2]))))
    return nb


def add(o1, o2):
    return (o1[0] + o2[0], o1[1] + o2[1], o1[2] + o2[2])


def cut(tag, kzn):
    """클러스터 하나. 반환: syms, xyz(N×3), roles(이름 → 0부터 번호), info."""
    p = os.path.join(HERE, 'charged_v3', f'{tag}_DDEC6.cif')
    a = read(p)
    nb = graph(a)
    cell = a.cell.array
    sym = a.get_chemical_symbols()
    zns = [k for k in range(len(a)) if sym[k] == 'Zn']
    zn = zns[kzn - 1]

    def P(k, off):
        return a.positions[k] + np.dot(off, cell)

    lig = nb[zn]
    Ns = [(v, s) for v, s in lig if sym[v] == 'N']
    Os = [(v, s) for v, s in lig if sym[v] == 'O']
    if len(lig) != 4 or len(Ns) != 2 or len(Os) != 2:
        raise SystemExit(f'!! {tag} Zn{kzn}: 배위 원자 {[(sym[v], v) for v, s in lig]} — N 2 · O 2 가 아님')
    syms, xyz, src, roles = ['Zn'], [P(zn, (0, 0, 0))], [zn], {'zn': 0}

    def put(s, r, k=None):
        syms.append(s); xyz.append(np.array(r, float)); src.append(k)
        return len(syms) - 1

    def nbrs(k, off, excl=('Zn',)):
        return [(w, add(off, s)) for w, s in nb[k] if sym[w] not in excl]

    # 이미다졸 둘 → 1-메틸이미다졸
    for lab, (n3, off3) in zip('ab', sorted(Ns)):
        cs = [(w, o) for w, o in nbrs(n3, off3) if sym[w] == 'C']
        c2 = [(w, o) for w, o in cs if sum(sym[x] == 'N' for x, _ in nb[w]) == 2]
        c4 = [(w, o) for w, o in cs if (w, o) not in c2]
        if len(cs) != 2 or len(c2) != 1 or len(c4) != 1:
            raise SystemExit(f'!! {tag} Zn{kzn}: 이미다졸 N{n3} 의 이웃 C 가 고리 모양이 아님')
        c2, c4 = c2[0], c4[0]
        n1 = [(w, o) for w, o in nbrs(*c2) if sym[w] == 'N' and w != n3][0]
        c5 = [(w, o) for w, o in nbrs(*c4) if sym[w] == 'C' and (w, o) in nbrs(*n1)]
        if len(c5) != 1:
            raise SystemExit(f'!! {tag} Zn{kzn}: 이미다졸 고리 C5 를 못 찾음')
        c5 = c5[0]
        ring = [(n3, off3), c2, n1, c5, c4]
        roles[f'n_{lab}'] = put('N', P(n3, off3), n3)
        for w, o in ring[1:]:
            put(sym[w], P(w, o), w)
        for w, o in (c2, c5, c4):
            hs = [(x, oo) for x, oo in nbrs(w, o) if sym[x] == 'H']
            if len(hs) != 1:
                raise SystemExit(f'!! {tag} Zn{kzn}: 고리 C{w} 의 H 가 {len(hs)}개')
            put('H', P(*hs[0]), hs[0][0])
        ca = [(w, o) for w, o in nbrs(*n1) if (w, o) not in ring]
        if len(ca) != 1 or sym[ca[0][0]] != 'C':
            raise SystemExit(f'!! {tag} Zn{kzn}: N1 의 사슬 C 를 못 찾음')
        ca = ca[0]
        roles[f'cme_{lab}'] = put('C', P(*ca), ca[0])
        hs = [(x, oo) for x, oo in nbrs(*ca) if sym[x] == 'H']
        cb = [(x, oo) for x, oo in nbrs(*ca) if sym[x] == 'C']
        if len(hs) != 2 or len(cb) != 1:
            raise SystemExit(f'!! {tag} Zn{kzn}: 사슬 첫 C 가 CH₂–C 모양이 아님(H {len(hs)} · C {len(cb)})')
        for h in hs:
            put('H', P(*h), h[0])
        roles[f'h_cap_{lab}'] = put('H', P(*ca) + 1.09 * unit(P(*cb[0]) - P(*ca)), None)

    # 링커 둘 — 셀 이동을 들고 따라감
    links = []
    for o1, off1 in sorted(Os):
        seen = {o1: off1}
        q = deque([o1])
        while q:
            u = q.popleft()
            for w, o in nbrs(u, seen[u]):
                if w not in seen:
                    seen[w] = o; q.append(w)
                elif seen[w] != o:
                    raise SystemExit(f'!! {tag} Zn{kzn}: 링커가 자기 상에 닿음(원자 {w}) — 펼 수 없음')
        comp = Counter(sym[k] for k in seen)
        cnear = [w for w, o in nbrs(o1, off1) if sym[w] == 'C']
        ofree = [w for w, o in nbrs(cnear[0], seen[cnear[0]]) if sym[w] == 'O' and w != o1]
        far = [(k, [(w, add(seen[k], s)) for w, s in nb[k] if sym[w] == 'Zn']) for k in seen if sym[k] == 'O' and k != o1]
        far = [(k, z) for k, z in far if z]
        if len(cnear) != 1 or len(ofree) != 1 or len(far) != 1 or len(far[0][1]) != 1:
            raise SystemExit(f'!! {tag} Zn{kzn}: 링커 카복실레이트 모양이 등록과 다름(가까운 C {len(cnear)} · 비배위 O {len(ofree)} · 먼 쪽 Zn–O {len(far)})')
        if any(z for k in ofree for z in [[w for w, s in nb[k] if sym[w] == 'Zn']] if z):
            raise SystemExit(f'!! {tag} Zn{kzn}: 비배위 O 가 Zn 에 붙어 있음')
        ofar, (znf, offzf) = far[0][0], far[0][1][0]
        cfar = [w for w, o in nbrs(ofar, seen[ofar]) if sym[w] == 'C']
        links.append({'o': o1, 'seen': seen, 'comp': comp, 'sub': comp != UNSUB, 'cnear': cnear[0], 'ofree': ofree[0], 'ofar': ofar,
                      'cfar': cfar[0], 'h_acid': P(ofar, seen[ofar]) + 0.97 * unit(P(znf, offzf) - P(ofar, seen[ofar]))})
    return a, zn, links, syms, xyz, src, roles, put, P


def build(tag, kzn, parent_pick=None):
    a, zn, links, syms, xyz, src, roles, put, P = cut(tag, kzn)
    nsub = sum(l['sub'] for l in links)
    rule = None
    if tag == 'e22_parent':
        if nsub != 0:
            raise SystemExit('!! 모체에 치환 링커가 있음')
        pick = parent_pick[kzn]                      # 설계 여섯의 치환 링커 배위 O 자리와 겹치는 O
        d = {l['o']: np.linalg.norm(P(l['o'], l['seen'][l['o']]) - pick['pos_mean']) for l in links}
        sub = min(links, key=lambda l: d[l['o']])
        rule = {'rule': '설계 구조 여섯의 치환 링커 배위 O 와 같은 자리의 O(같은 셀 · 직교좌표)', 'overlap_A_each_design': pick['each'][sub['o']],
                'other_O_distance_A_each_design': pick['each'][[l for l in links if l is not sub][0]['o']], 'designs_agree': pick['agree']}
        if not pick['agree'] or max(rule['overlap_A_each_design'].values()) > 0.3:
            raise SystemExit(f'!! 모체 Zn{kzn}: 치환 쪽 O 를 0.3 Å 안에서 한 가지로 못 고름 — {rule}')
    else:
        if nsub != 1:
            raise SystemExit(f'!! {tag} Zn{kzn}: 치환 링커가 {nsub}개 — 하나여야 함')
        sub = [l for l in links if l['sub']][0]
    for lab, l in (('sub', sub), ('unsub', [x for x in links if x is not sub][0])):
        first = len(syms)
        idx = {}
        for k in sorted(l['seen']):
            idx[k] = put(a[k].symbol, P(k, l['seen'][k]), k)
        roles[f'o_{lab}'] = idx[l['o']]; roles[f'ofree_{lab}'] = idx[l['ofree']]; roles[f'ccarb_{lab}'] = idx[l['cnear']]
        roles[f'ofar_{lab}'] = idx[l['ofar']]; roles[f'cfar_{lab}'] = idx[l['cfar']]
        roles[f'h_acid_{lab}'] = put('H', l['h_acid'], None)
        roles[f'linker_{lab}_range'] = [first, len(syms) - 1]
    xyz = np.array(xyz)
    nel = sum(atomic_numbers[s] for s in syms)
    info = {'structure': tag, 'cif': f'charged_v3/{tag}_DDEC6.cif', 'cif_md5': md5b(open(os.path.join(HERE, 'charged_v3', f'{tag}_DDEC6.cif'), 'rb').read()),
            'zn_ordinal': kzn, 'zn_cif_index': zn, 'n_atoms': len(syms), 'composition': dict(Counter(syms)), 'charge': 0, 'n_electrons': nel,
            'closed_shell': nel % 2 == 0, 'sub_linker_composition': dict(sub['comp']), 'unsub_linker_composition': dict([x for x in links if x is not sub][0]['comp']),
            'source_cif_index': src, 'roles': roles, 'fixed_atoms_0based': [roles[x] for x in ('cme_a', 'cme_b', 'cfar_sub', 'cfar_unsub')],
            'sub_side_rule': rule or '치환 링커(조성 ≠ C12H4O4S2)의 배위 O',
            'd_ZnO_cif_A': {x: float(np.linalg.norm(xyz[roles[f'o_{x}']] - xyz[0])) for x in ('sub', 'unsub')},
            'd_ZnN_cif_A': [float(np.linalg.norm(xyz[roles[f'n_{x}']] - xyz[0])) for x in 'ab']}
    if nel % 2:
        raise SystemExit(f'!! {tag} Zn{kzn}: 전자 수 {nel} 홀수 — 닫힌 껍질 아님')
    return syms, xyz, info


def parent_picks():
    """모체의 '치환 쪽' O 를 고를 자리 — 설계 여섯에서 Zn k 의 치환 링커 배위 O 직교좌표(셀이 같음을 확인)."""
    pa = read(os.path.join(HERE, 'charged_v3', 'e22_parent_DDEC6.cif'))
    out = {}
    for kzn in (1, 2):
        pos = {}
        for t in DESIGNS:
            a, zn, links, *_r, P = cut(t, kzn)
            if np.abs(a.cell.array - pa.cell.array).max() > 1e-6:
                raise SystemExit(f'!! {t} 의 셀이 모체와 다름 — 겹침 규칙을 못 씀')
            sub = [l for l in links if l['sub']]
            if len(sub) != 1:
                raise SystemExit(f'!! {t} Zn{kzn}: 치환 링커 {len(sub)}개')
            pos[t] = P(sub[0]['o'], sub[0]['seen'][sub[0]['o']])
        a, zn, links, *_r, P = cut('e22_parent', kzn)
        each = {l['o']: {t: float(np.linalg.norm(P(l['o'], l['seen'][l['o']]) - pos[t])) for t in DESIGNS} for l in links}
        best = {t: min(each, key=lambda o: each[o][t]) for t in DESIGNS}
        out[kzn] = {'pos_mean': np.mean(list(pos.values()), axis=0), 'each': each, 'agree': len(set(best.values())) == 1}
    return out


# ---------------------------------------------------------------- 물 출발 좌표
def perp(b, ref):
    v = np.array(ref, float) - np.dot(ref, b) * b
    if np.linalg.norm(v) < 1e-6:
        v = np.cross(b, [1.0, 0.0, 0.0])
        if np.linalg.norm(v) < 1e-6:
            v = np.cross(b, [0.0, 1.0, 0.0])
    return unit(v)


def rot(v, axis, deg):
    t = np.radians(deg); k = unit(axis)
    return v * np.cos(t) + np.cross(k, v) * np.sin(t) + k * np.dot(k, v) * (1 - np.cos(t))


def mind(pts, xyz, skip=()):
    keep = [i for i in range(len(xyz)) if i not in skip]
    return float(min(np.linalg.norm(xyz[keep] - p, axis=1).min() for p in pts))


def water_starts(xyz, roles):
    zn = xyz[0]
    L = {'Na': xyz[roles['n_a']], 'Nb': xyz[roles['n_b']], 'Osub': xyz[roles['o_sub']], 'Ounsub': xyz[roles['o_unsub']]}
    u = {k: unit(v - zn) for k, v in L.items()}
    out = {}
    th, r = np.radians(104.5) / 2, 0.96
    for opp in L:                                   # 면 = 나머지 세 리간드 · 방향 = 그 셋의 단위벡터 합
        n0 = unit(sum(u[k] for k in L if k != opp))
        reg = mind([zn + 2.2 * n0], xyz, skip=(0,))  # 등록 자리(면 법선 · 2.2 Å)에서 O_w 와 가장 가까운 원자(Zn 빼고)
        pick = None
        for tilt in range(0, 65, 5):                # 등록 자리가 부딪치면(O_w < 1.9 Å 또는 H < 1.4 Å) Zn 에서 2.2 Å 를 지킨 채 가장 조금 기울임
            cands = []
            for az in ([0] if tilt == 0 else range(0, 360, 30)):
                n = n0 if tilt == 0 else unit(rot(rot(n0, perp(n0, u[opp]), tilt), n0, az))
                ow = zn + 2.2 * n
                mo = mind([ow], xyz, skip=(0,))
                if mo < 1.9:
                    continue
                best = None
                for a2 in range(0, 180, 15):        # H 둘은 Zn 반대쪽 · 방위각은 가장 덜 부딪치는 쪽
                    p = rot(perp(n, u[opp]), n, a2)
                    h = [ow + r * (np.cos(th) * n + np.sin(th) * p), ow + r * (np.cos(th) * n - np.sin(th) * p)]
                    m = mind(h, xyz)
                    if best is None or m > best[0]:
                        best = (m, a2, h)
                if best[0] >= 1.4:
                    cands.append((mo, az, ow, best))
            if cands:
                mo, az, ow, best = max(cands, key=lambda c: c[0])
                pick = (tilt, az, ow, best, mo)
                break
        if pick is None:
            raise SystemExit(f'!! Zn 면({opp} 맞은편) 출발 자리를 60° 안에서 부딪치지 않게 못 잡음')
        tilt, az, ow, best, mo = pick
        out[f'b_face_opp_{opp}'] = {'xyz': [ow] + best[2], 'start': {'kind': 'Zn 면', 'opposite_ligand': opp, 'd_Zn_Ow_A': 2.2, 'tilt_from_face_normal_deg': tilt,
                                                                    'tilt_azimuth_deg': az, 'water_azimuth_deg': best[1],
                                                                    'min_dist_Ow_to_cluster_A_at_registered_point': reg, 'registered_point_used': tilt == 0,
                                                                    'min_dist_H_to_cluster_A': best[0], 'min_dist_Ow_to_cluster_A': mo}}
    for lab in ('sub', 'unsub'):                    # 비배위 O 에 수소결합
        of, cc = xyz[roles[f'ofree_{lab}']], xyz[roles[f'ccarb_{lab}']]
        d0 = unit(of - cc)
        pick = None
        for tilt in (0, 30, 60, 90):
            for az in ([0] if tilt == 0 else range(0, 360, 45)):
                d = d0 if tilt == 0 else rot(rot(d0, perp(d0, zn - of), tilt), d0, az)
                ow = of + 2.8 * d
                h1 = ow - r * d
                p = perp(d, ow - zn)
                h2 = ow + r * (np.cos(np.radians(104.5)) * (-d) + np.sin(np.radians(104.5)) * p)
                mo, mh = mind([ow], xyz), mind([h1, h2], xyz, skip=(roles[f'ofree_{lab}'],))
                if mo >= 2.4 and mh >= 1.6:
                    pick = (tilt, az, [ow, h1, h2], mo, mh)
                    break
            if pick:
                break
        if pick is None:
            raise SystemExit(f'!! 비배위 O({lab}) 수소결합 출발 자리를 부딪치지 않게 못 잡음')
        out[f'b_hb_Ofree_{lab}'] = {'xyz': pick[2], 'start': {'kind': '비배위 O 수소결합', 'linker': lab, 'd_Ofree_Ow_A': 2.8, 'tilt_deg': pick[0], 'azimuth_deg': pick[1],
                                                               'min_dist_Ow_to_cluster_A': pick[3], 'min_dist_H_to_cluster_A': pick[4]}}
    return out


# ---------------------------------------------------------------- xtb
def write_xyz(path, syms, xyz, comment=''):
    with open(path, 'w') as f:
        f.write(f'{len(syms)}\n{comment}\n')
        for s, r in zip(syms, xyz):
            f.write(f'{s:<2s} {r[0]:16.8f} {r[1]:16.8f} {r[2]:16.8f}\n')


def read_xyz(path):
    ln = open(path).read().split('\n')
    n = int(ln[0])
    syms, xyz = [], []
    for x in ln[2:2 + n]:
        t = x.split()
        syms.append(t[0]); xyz.append([float(t[1]), float(t[2]), float(t[3])])
    return syms, np.array(xyz)


def xtb_version():
    o = subprocess.run([XTB, '--version'], capture_output=True, text=True, env=ENV)
    m = re.search(r'xtb version (\S+ \(\S+\))', o.stdout + o.stderr)
    return m.group(1) if m else None


def limits():
    try:
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ValueError, OSError):
        pass


def run_xtb(wd, syms, xyz, fixed, constraint=None, opt=True, anchor_ref=None):
    """한 번. 반환 dict(표지 · 에너지 · 끝 좌표). 열쇠가 같고 표지가 통과한 앞 실행만 다시 씀."""
    os.makedirs(wd, exist_ok=True)
    ctl = ''
    pairs = []
    if opt and fixed:                                # 고정 넷 = 강체 틀: 서로 거리 여섯을 자른 구조의 값으로 묶음(머리말 [K-3 고정 · 최적화기])
        ref = np.array(anchor_ref if anchor_ref is not None else xyz)
        pairs = [(fixed[a], fixed[b], float(np.linalg.norm(ref[fixed[a]] - ref[fixed[b]]))) for a in range(len(fixed)) for b in range(a + 1, len(fixed))]
    if opt:
        lines = ''.join(f'   distance: {i + 1}, {j + 1}, {d:.6f}\n' for i, j, d in pairs)
        if constraint:
            lines += f'   distance: {constraint[0] + 1}, {constraint[1] + 1}, {constraint[2]:.6f}\n'
        if lines:
            ctl += f'$constrain\n   force constant={FC}\n' + lines + '$end\n'
        ctl += '$opt\n   maxcycle=1500\n$end\n'
    cmd = [XTB, 'start.xyz', '--gfn', '2', '--chrg', '0', '--uhf', '0'] + (['--opt', 'tight', '--input', 'control.inp'] if opt else [])
    start_txt = f'{len(syms)}\n\n' + ''.join(f'{s:<2s} {r[0]:16.8f} {r[1]:16.8f} {r[2]:16.8f}\n' for s, r in zip(syms, xyz))
    key = md5b((start_txt + '|' + ctl + '|' + ' '.join(cmd[1:]) + '|' + str(VERSION)).encode())
    kf = os.path.join(wd, 'state.json')
    if os.path.exists(kf):
        try:
            old = json.load(open(kf))
            if old.get('key') == key and old.get('markers_ok') is True:
                old['cached'] = True
                return old
        except (ValueError, OSError):
            pass
    for f in os.listdir(wd):                         # 앞 실행의 재시작 파일이 섞이지 않게 비우고 시작
        os.remove(os.path.join(wd, f)) if os.path.isfile(os.path.join(wd, f)) else shutil.rmtree(os.path.join(wd, f))
    open(os.path.join(wd, 'start.xyz'), 'w').write(start_txt)
    if opt:
        open(os.path.join(wd, 'control.inp'), 'w').write(ctl)
    t0 = time.time()
    with open(os.path.join(wd, 'xtb.out'), 'w') as fh:
        cp = subprocess.run(cmd, cwd=wd, stdout=fh, stderr=subprocess.STDOUT, env=ENV, preexec_fn=limits)
    sec = round(time.time() - t0, 1)
    txt = open(os.path.join(wd, 'xtb.out'), errors='ignore').read()
    es = re.findall(r'\|\s*TOTAL ENERGY\s+(-?\d+\.\d+)\s+Eh', txt)
    conv = re.search(r'GEOMETRY OPTIMIZATION CONVERGED AFTER (\d+) (?:ITERATIONS|CYCLES)', txt)
    res = {'key': key, 'cached': False, 'seconds': sec, 'returncode': cp.returncode, 'normal_termination': 'normal termination of xtb' in txt,
           'opt': opt, 'converged': bool(conv) if opt else None, 'opt_iterations': int(conv.group(1)) if conv else None,
           'energy_Eh_raw': float(es[-1]) if es else None, 'n_atoms': len(syms), 'charge': 0, 'uhf': 0, 'xtb_version': VERSION,
           'fixed_atoms_0based': list(fixed) if opt else None, 'constraint': ({'i': constraint[0], 'j': constraint[1], 'target_A': constraint[2], 'force_constant': FC}
                                                                              if constraint else None)}
    end = None
    ep = os.path.join(wd, 'xtbopt.xyz')
    if opt and os.path.exists(ep):
        s2, end = read_xyz(ep)
        if s2 != list(syms):
            end = None
    if not opt:
        end = np.array(xyz)
    res['end_xyz'] = end.tolist() if end is not None else None
    ok = [res['normal_termination'], cp.returncode == 0, res['energy_Eh_raw'] is not None, end is not None]
    if opt:
        ok.append(res['converged'])
        rs = re.findall(r'add\. restraining\s+(-?\d+\.\d+)\s+Eh', txt)
        res['restraint_Eh_last'] = float(rs[-1]) if rs else None
        if end is not None:
            if pairs:                                # 강체 틀: 고정 넷의 서로 거리가 자른 구조의 값에서 안 변했는가(틀 전체의 이동 · 회전은 기체상에서 뜻 없음)
                res['anchor_pair_max_change_A'] = float(max(abs(np.linalg.norm(end[i] - end[j]) - d) for i, j, d in pairs))
                ok.append(res['anchor_pair_max_change_A'] < ANCHOR_TOL)
            if constraint:
                res['constraint']['achieved_A'] = float(np.linalg.norm(end[constraint[0]] - end[constraint[1]]))
                ok.append(abs(res['constraint']['achieved_A'] - constraint[2]) < 0.02)
        wb = {}
        wf = os.path.join(wd, 'wbo')
        if os.path.exists(wf):
            for ln in open(wf):
                t = ln.split()
                if len(t) == 3:
                    wb[(int(t[0]) - 1, int(t[1]) - 1)] = float(t[2])
        res['_wbo'] = {f'{i}-{j}': v for (i, j), v in wb.items() if i == 0 or j == 0}      # Zn 과의 것만 남김
        res['wbo_file'] = os.path.exists(wf)
    res['markers_ok'] = bool(all(ok))
    json.dump(res, open(kf, 'w'))
    return res


def bonds(syms, xyz):
    """공유 결합 쌍(공유 반지름 × 1.15) — Zn 이 낀 쌍은 뺌(배위 결합은 거리로 따로 적음)."""
    a = Atoms(symbols=list(syms), positions=np.array(xyz))
    i, j = neighbor_list('ij', a, natural_cutoffs(a, mult=1.15))
    return sorted({(int(min(x, y)), int(max(x, y))) for x, y in zip(i, j) if syms[x] != 'Zn' and syms[y] != 'Zn'})


def geom(res, roles, nw=0):
    """끝 좌표에서 읽는 거리 · 결합 차수(표지가 빠지면 None)."""
    if not res.get('markers_ok') or res.get('end_xyz') is None:
        return None
    x = np.array(res['end_xyz'])
    wb = res.get('_wbo', {})

    def w(i):
        return wb.get(f'0-{i}', wb.get(f'{i}-0'))
    g = {'d_Zn_Osub_A': float(np.linalg.norm(x[roles['o_sub']] - x[0])), 'd_Zn_Ounsub_A': float(np.linalg.norm(x[roles['o_unsub']] - x[0])),
         'd_Zn_Na_A': float(np.linalg.norm(x[roles['n_a']] - x[0])), 'd_Zn_Nb_A': float(np.linalg.norm(x[roles['n_b']] - x[0])),
         'wbo_Zn_Osub': w(roles['o_sub']), 'wbo_Zn_Ounsub': w(roles['o_unsub']), 'wbo_note': 'None = xtb wbo 파일에 그 쌍이 없음(인쇄 문턱 미만)',
         'd_Zn_Ofree_sub_A': float(np.linalg.norm(x[roles['ofree_sub']] - x[0])), 'd_Zn_Ofree_unsub_A': float(np.linalg.norm(x[roles['ofree_unsub']] - x[0]))}
    near = sorted((float(np.linalg.norm(x[i] - x[0])), i) for i in range(1, len(x)) if SYMS_CUR[i] in ('N', 'O') and np.linalg.norm(x[i] - x[0]) < 2.5)
    inv = {v: k for k, v in roles.items() if isinstance(v, int)}
    g['Zn_NO_within_2p5A'] = [{'atom_0based': i, 'symbol': SYMS_CUR[i], 'role': inv.get(i, 'water_O' if (nw and i == len(x) - 3) else None), 'd_A': d} for d, i in near]
    g['cn_Zn_within_2p5A'] = len(near)
    if nw:
        ow, h = x[-3], x[-2:]
        g['d_Zn_Ow_A'] = float(np.linalg.norm(ow - x[0]))
        g['water_OH_A'] = [float(np.linalg.norm(hh - ow)) for hh in h]
        g['water_intact'] = bool(max(g['water_OH_A']) < 1.15)
        g['wbo_Zn_Ow'] = w(len(x) - 3)
        g['min_Hw_Ofree_sub_A'] = float(np.linalg.norm(h - x[roles['ofree_sub']], axis=1).min())
        g['min_Hw_Ofree_unsub_A'] = float(np.linalg.norm(h - x[roles['ofree_unsub']], axis=1).min())
        heavy = [i for i in range(len(x) - 3) if SYMS_CUR[i] in ('O', 'N', 'S', 'Cl', 'Br')]
        dd = [(float(np.linalg.norm(hh - x[i])), i) for hh in h for i in heavy]
        m = min(dd)
        g['min_Hw_acceptor_A'] = m[0]; g['min_Hw_acceptor_atom_0based'] = m[1]; g['min_Hw_acceptor_symbol'] = SYMS_CUR[m[1]]
        if g['d_Zn_Ow_A'] < 2.5:
            g['end_state'] = 'Zn 배위'
        elif min(g['min_Hw_Ofree_sub_A'], g['min_Hw_Ofree_unsub_A']) < 2.2:
            g['end_state'] = '비배위 O 수소결합'
            g['hb_linker'] = 'sub' if g['min_Hw_Ofree_sub_A'] <= g['min_Hw_Ofree_unsub_A'] else 'unsub'
        else:
            g['end_state'] = '그 밖'
    return g


SYMS_CUR = []
VERSION = None


def public(res):
    return {k: v for k, v in res.items() if k not in ('end_xyz', '_wbo', 'key')}


def main():
    global VERSION, SYMS_CUR
    try:
        os.nice(19)
    except OSError:
        pass
    VERSION = xtb_version()
    if not VERSION and not CUT_ONLY:
        raise SystemExit(f'!! xtb 가 안 돎({XTB}) — 환경을 바꾸지 않고 멈춤')
    picks = parent_picks()
    names = [f'{t}_zn{k}' for t, k in CLUSTERS]
    todo = [(t, k) for t, k in CLUSTERS if not ONLY or f'{t}_zn{k}' in ONLY]
    global RUNS, OUT
    if CUT_ONLY:                                     # 자르기만은 저장소에 아무것도 안 씀
        RUNS, OUT = os.path.join(WORK, 'cut_only_runs'), os.path.join(WORK, 'cut_only.json')
        os.makedirs(WORK, exist_ok=True)
    out = {'test': '등록 K — xtb 클러스터(Zn 마디 하나): 물 붙는 에너지 · 물이 있을 때 Zn–O 를 늘리는 에너지', 'assign': 'ASSIGN_DURABILITY_JK_20261111.md §K',
           'machine': MACHINE, 'script': os.path.basename(__file__), 'script_md5': md5b(open(os.path.abspath(__file__), 'rb').read()), 'started': time.strftime('%F %T'),
           'xtb': {'path': XTB, 'version': VERSION}, 'method': 'GFN2-xTB · 기체상 · --opt tight · --chrg 0 · --uhf 0 · OMP_NUM_THREADS=1 · nice 19 · 한 번에 한 프로세스',
           'optimizer': 'xtb 기본 최적화기(ANC) · --opt tight — 이 xtb 판은 기본 최적화기에서 $fix 를 지키지 않고(시험: 고정 원자 0.19 Å 이동), L-ANC 는 거리 묶기와 함께 못 써서 통일',
           'anchor': f'고정 넷(두 메틸 C · 두 먼 쪽 카복실 C)의 서로 거리 여섯을 자른 구조의 값으로 묶음($constrain distance · force constant {FC} Eh/bohr²) — 강체 틀',
           'anchor_pair_tol_A': ANCHOR_TOL,
           'constraint': f'Zn–O 거리 묶기도 같은 $constrain(force constant {FC}) · 모든 상태의 energy_Eh 는 끝 좌표에서 묶기 없이 한 점 계산한 값',
           'kJ_per_Eh': EH, 'stretch_A': list(STRETCH), 'clusters_planned': names, 'states_env': STATES, 'only_env': ONLY, 'clusters': {},
           'note': '기계적 사실뿐 — 클러스터 사이의 차 · 순위 · 판정은 적지 않음(종합자 · 등록 §K-5). 표지가 하나라도 빠진 상태의 값은 None(0 과 다름). '
                   'dE_w = E − E0 − E(H2O) · dE_stretch = E(늘린 점 · 한 점 계산) − E(그 스캔의 출발 상태).'}
    if os.path.exists(OUT) and not ONLY:
        prev = json.load(open(OUT, encoding='utf-8'))
        out['previous_started'] = prev.get('started')

    def save(final=False):
        if final:
            out['finished'] = time.strftime('%F %T')
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        os.replace(tmp, OUT)

    print(f'등록 K — 기기 {MACHINE} · xtb {VERSION} · 클러스터 {len(todo)}/{len(CLUSTERS)} · 상태 {STATES} · 자르기만 {CUT_ONLY}', flush=True)
    wat = None
    if not CUT_ONLY and 'b' in STATES:
        ws, wx = ['O', 'H', 'H'], np.array([[0.0, 0.0, 0.0], [0.96 * np.sin(np.radians(52.25)), 0.96 * np.cos(np.radians(52.25)), 0.0],
                                            [-0.96 * np.sin(np.radians(52.25)), 0.96 * np.cos(np.radians(52.25)), 0.0]])
        wat = run_xtb(os.path.join(WORK, 'water_ref'), ws, wx, [])
        out['water_ref'] = dict(public(wat), energy_Eh=wat['energy_Eh_raw'] if wat['markers_ok'] else None)
        print(f"  물 분자 E {out['water_ref']['energy_Eh']} · 표지 {wat['markers_ok']} · {wat['seconds']} s{' · cached' if wat['cached'] else ''}", flush=True)
        save()
    for t, k in todo:
        name = f'{t}_zn{k}'
        syms, xyz, info = build(t, k, picks)
        SYMS_CUR = list(syms) + ['O', 'H', 'H']
        roles, fixed = info['roles'], info['fixed_atoms_0based']
        cd = os.path.join(RUNS, name); os.makedirs(cd, exist_ok=True)
        C = dict(info, name=name, repeat_of=(f'{t}_zn1' if k == 2 else None), states={})
        out['clusters'][name] = C
        print(f"== {name}: 원자 {info['n_atoms']} · 전하 0 · 전자 {info['n_electrons']} · 조성 {info['composition']} · 고정(1부터) {[i + 1 for i in fixed]} · "
              f"d(Zn–O) CIF 치환 쪽 {info['d_ZnO_cif_A']['sub']:.3f} · 무치환 쪽 {info['d_ZnO_cif_A']['unsub']:.3f}", flush=True)
        write_xyz(os.path.join(cd, 'a_nowater.start.xyz'), syms, xyz, f'{name} a_nowater start (CIF cut)')
        starts = water_starts(xyz, roles)
        C['water_start_from_cif_geometry'] = {s: v['start'] for s, v in starts.items()}
        if CUT_ONLY:
            for s, v in starts.items():
                write_xyz(os.path.join(cd, f'{s}.cifstart.xyz'), syms + ['O', 'H', 'H'], np.vstack([xyz, v['xyz']]), f'{name} {s} start on CIF-cut geometry (cut-only)')
            save()
            continue

        def do(state, s_, x_, constraint=None, nw=0, ref=None):
            r = run_xtb(os.path.join(WORK, name, state), s_, x_, fixed, constraint, anchor_ref=xyz)
            write_xyz(os.path.join(cd, f'{state}.start.xyz'), s_, x_, f'{name} {state} start')
            e = None
            rec = dict(public(r))
            if r['markers_ok']:                                     # 끝 좌표에서 묶기 없이 한 점 계산 — 모든 상태의 energy_Eh 는 이 값
                sp = run_xtb(os.path.join(WORK, name, state, 'sp'), s_, np.array(r['end_xyz']), fixed, None, opt=False)
                rec['single_point'] = public(sp)
                e = sp['energy_Eh_raw'] if sp['markers_ok'] else None
            rec['energy_Eh_with_restraint'] = r['energy_Eh_raw']
            rec['energy_Eh'] = e
            if r.get('end_xyz') is not None:
                write_xyz(os.path.join(cd, f'{state}.end.xyz'), s_, np.array(r['end_xyz']), f'{name} {state} end E={e} Eh markers_ok={r["markers_ok"]}')
            g = geom(r, roles, nw) if e is not None else None
            rec['geometry'] = g
            if r.get('end_xyz') is not None:                        # 부가 사실(값을 None 으로 만들지 않음): 공유 결합 그래프가 출발과 같은가
                b0, b1 = bonds(s_, x_), bonds(s_, r['end_xyz'])
                rec['topology_same_as_start'] = b0 == b1
                if b0 != b1:
                    rec['topology_diff'] = {'broken': [list(t) for t in sorted(set(b0) - set(b1))], 'formed': [list(t) for t in sorted(set(b1) - set(b0))]}
            if ref is not None:
                rec['dE_kJmol'] = (e - ref) * EH if (e is not None and ref is not None) else None
            C['states'][state] = rec
            save()
            print(f"  {state:<26s} 표지 {r['markers_ok']} · 수렴 {r.get('converged')} · E {e} · {r['seconds']} s{' · cached' if r['cached'] else ''}"
                  + (f" · 묶음 {rec['constraint']['achieved_A']:.4f}/{constraint[2]:.4f}" if constraint and rec['constraint'].get('achieved_A') else '')
                  + (f" · {g['end_state']} d(Zn–Ow) {g['d_Zn_Ow_A']:.3f}" if g and nw else ''), flush=True)
            return r, e

        ra, e0 = do('a_nowater', syms, xyz)
        C['E0_Eh'] = e0
        if e0 is None or STATES == 'a':
            continue
        xa = np.array(ra['end_xyz'])
        starts = water_starts(xa, roles)                             # 물 출발 자리는 (a)의 끝 좌표 위에
        ew = wat['energy_Eh_raw'] if (wat and wat['markers_ok']) else None
        low = None
        for s, v in starts.items():
            r, e = do(s, syms + ['O', 'H', 'H'], np.vstack([xa, v['xyz']]), nw=1, ref=(e0 + ew) if ew is not None else None)
            C['states'][s]['start'] = v['start']
            C['states'][s]['dE_w_kJmol'] = C['states'][s].pop('dE_kJmol', None) if ew is not None else None
            if e is not None and (low is None or e < low[1]):
                low = (s, e, np.array(r['end_xyz']))
        save()
        C['lowest_water_state'] = low[0] if low else None
        if 'c' not in STATES:
            continue
        scans = [('c_dry_sub', syms, xa, e0, 'sub')]
        if low:
            scans = [('c_w_sub', syms + ['O', 'H', 'H'], low[2], low[1], 'sub'), ('c_w_unsub', syms + ['O', 'H', 'H'], low[2], low[1], 'unsub')] + scans
        for pre, s_, x0, eref, side in scans:
            i, j = 0, roles[f'o_{side}']
            d0 = float(np.linalg.norm(x0[j] - x0[i]))
            x = x0
            for dx in STRETCH:
                st = f'{pre}_p{int(round(dx * 10)):02d}'
                r, e = do(st, s_, x, constraint=(i, j, d0 + dx), nw=(1 if len(s_) > len(syms) else 0), ref=eref)
                C['states'][st].update(scan={'from_state': (low[0] if pre.startswith('c_w') else 'a_nowater'), 'side': side, 'd0_A': d0, 'stretch_A': dx})
                C['states'][st]['dE_stretch_kJmol'] = C['states'][st].pop('dE_kJmol', None)
                if r.get('end_xyz') is None or not r['markers_ok']:
                    break                                           # 앞 점이 빠지면 그 스캔의 뒤 점은 돌리지 않음(값 None)
                x = np.array(r['end_xyz'])
        save()
    n_opt = sum(1 for c in out['clusters'].values() for s in c['states'].values())
    n_ok = sum(1 for c in out['clusters'].values() for s in c['states'].values() if s.get('energy_Eh') is not None)
    out['counts'] = {'states_run': n_opt, 'states_with_value': n_ok, 'clusters': len(out['clusters'])}
    save(final=True)
    print(f'저장 {OUT} · 상태 {n_opt} · 값 있는 상태 {n_ok}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
