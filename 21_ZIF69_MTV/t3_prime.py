"""T-3′ — 고리 평면성 재판정. **등록문 `T3_PRIME_20260904.md` 순서대로만 돕니다.**

    1단계  기준선   실험 ZIF CIF 23개의 6원 고리 평면성 RMSD 분포
    2단계  문턱     = 그 분포의 **최댓값** (등록문 3-3, 함수 고정)
    3단계  판별력   합성 양성 대조 — 통과 못 하면 여기서 멈추고 T-3′ 폐기
    4단계  재판정   9구조 (base + fbIm·mbIm 사다리)

지표는 `audit_probe_noshrink.py` 의 것을 **import 해서** 씁니다. 다시 구현하지
않습니다. 산출: t3_prime.json
"""
import glob
import json
import os
import sys

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit_probe_noshrink as A  # noqa: E402

EXP_GLOB = os.path.join(os.path.dirname(HERE), '00_Migration', 'raspa_share',
                        'raspa', 'structures', 'mofs', 'cif', 'ZIF*.cif')
DELTAS = [0.05, 0.10, 0.20, 0.40]       # 등록문 4절
DELTA_MUST_CATCH = 0.20                 # 등록문 4절 통과 조건 ②
RING_ELEMENTS = {'C', 'N'}              # 등록문 3-2


def ring_points(ring, vec):
    """ring_planarity 와 **같은** 언랩으로 얻은 고리 점들."""
    pos = {ring[0]: np.zeros(3)}
    for a, b in zip(ring, ring[1:]):
        pos[b] = pos[a] + vec[(a, b)]
    return np.array([pos[a] for a in ring])


def planarity_of_points(P):
    P = P - P.mean(axis=0)
    _, s, _ = np.linalg.svd(P)
    return float(s[-1] / np.sqrt(len(P)))


def six_rings(atoms):
    """6원 고리 중 고리 원자가 전부 C/N 인 것 — (ring, vec) 로 돌려준다."""
    syms = atoms.get_chemical_symbols()
    adj, vec = A.bond_graph(atoms)
    out = []
    for r in A.find_rings(adj, syms, sizes=(6,)):
        if all(syms[i] in RING_ELEMENTS for i in r):
            out.append(r)
    return out, vec


def rmsds(atoms):
    rings, vec = six_rings(atoms)
    return [A.ring_planarity(r, vec, atoms) for r in rings], rings, vec


def stage1_baseline():
    rows, skipped = [], []
    for p in sorted(glob.glob(EXP_GLOB)):
        name = os.path.basename(p)
        try:
            atoms = read(p)
            vals, _, _ = rmsds(atoms)
        except Exception as e:                       # noqa: BLE001
            skipped.append({'file': name, 'reason': f'읽기/계산 실패: {e}'})
            continue
        if not vals:
            skipped.append({'file': name, 'reason': '6원 고리 없음 (등록된 유일한 제외 사유)'})
            continue
        rows.append({'file': name, 'n_ring6': len(vals),
                     'max': max(vals), 'mean': float(np.mean(vals)),
                     'values': [round(v, 6) for v in vals]})
    allv = sorted(v for r in rows for v in r['values'])
    return rows, skipped, allv


def stage3_power(threshold):
    """합성 양성 대조 — base 6원 고리를 법선 방향으로 δ 만큼 접는다."""
    atoms = read(A.cif_path('base'))
    vals, rings, vec = rmsds(atoms)
    ref_max = max(vals)
    curve = {}
    for d in DELTAS:
        per = []
        for r in rings:
            P = ring_points(r, vec)
            c = P.mean(axis=0)
            _, _, vt = np.linalg.svd(P - c)
            n = vt[2] / np.linalg.norm(vt[2])
            Q = P.copy()
            Q[0] = Q[0] + d * n                      # 원자 하나를 평면 밖으로
            per.append(planarity_of_points(Q))
        curve[d] = {'min': min(per), 'max': max(per), 'mean': float(np.mean(per)),
                    'n_caught': sum(1 for v in per if v > threshold), 'n': len(per)}
    seq = [curve[d]['mean'] for d in DELTAS]
    checks = {
        'monotonic': all(b > a for a, b in zip(seq, seq[1:])),
        'catches_0.20': curve[DELTA_MUST_CATCH]['n_caught'] == curve[DELTA_MUST_CATCH]['n'],
        'clean_base_passes': ref_max <= threshold,
    }
    return {'reference_max': ref_max, 'curve': curve, 'checks': checks,
            'passed': all(checks.values())}


def stage4_rejudge(threshold):
    out = []
    for tag in A.DEFAULT_TAGS:
        vals, _, _ = rmsds(read(A.cif_path(tag)))
        out.append({'tag': tag, 'n_ring6': len(vals), 'max': max(vals),
                    'n_over': sum(1 for v in vals if v > threshold),
                    'verdict': '깨진 구조' if max(vals) > threshold else '정상'})
    return out


def main():
    print('=== T-3′ (등록문 T3_PRIME_20260904.md 순서) ===\n')
    print('1단계 — 기준선: 실험 ZIF CIF')
    rows, skipped, allv = stage1_baseline()
    for r in rows:
        print(f'    {r["file"]:<20} 6원 고리 {r["n_ring6"]:>3}  '
              f'평균 {r["mean"]:.4f}  최대 {r["max"]:.4f}')
    for s in skipped:
        print(f'    {s["file"]:<20} 제외 — {s["reason"]}')
    if not allv:
        sys.exit('기준선 자료가 비었습니다 — 멈춥니다.')
    thr = max(allv)
    p99 = float(np.percentile(allv, 99))
    p95 = float(np.percentile(allv, 95))
    print(f'\n2단계 — 문턱 (등록 함수: 분포의 최댓값)')
    print(f'    고리 {len(allv)}개  중앙값 {np.median(allv):.4f}  '
          f'95%p {p95:.4f}  99%p {p99:.4f}  **최댓값 {thr:.4f} Å ← 문턱**')
    print(f'    병기(판정 미사용): 0.05 Å 절대 문턱 · T-3 의 3σ 문턱 0.00471 Å')

    print(f'\n3단계 — 판별력 (문턱 {thr:.4f} Å 로)')
    power = stage3_power(thr)
    print(f'    δ=0 (원본 base) 최대 {power["reference_max"]:.4f}  '
          f'→ {"통과(안 잡힘)" if power["checks"]["clean_base_passes"] else "실패(잡힘)"}')
    for d in DELTAS:
        c = power['curve'][d]
        print(f'    δ={d:.2f} Å   평균 {c["mean"]:.4f}  '
              f'잡힌 고리 {c["n_caught"]:>3}/{c["n"]}')
    print(f'    단조 증가 {power["checks"]["monotonic"]} · '
          f'δ=0.20 전부 잡힘 {power["checks"]["catches_0.20"]}')
    print(f'    → 판별력 {"통과" if power["passed"] else "**실패 — T-3′ 폐기**"}')

    out = {'rule': 'T3_PRIME_20260904.md', 'baseline': rows, 'skipped': skipped,
           'threshold': thr, 'p99': p99, 'p95': p95, 'n_baseline_rings': len(allv),
           'power': power}
    if not power['passed']:
        out['verdict'] = 'T-3′ 폐기 — 판별력 시험 실패. T-3 판정(7개 인용 금지) 유지'
        json.dump(out, open(os.path.join(HERE, 't3_prime.json'), 'w',
                            encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'\n{out["verdict"]}')
        return 1

    print(f'\n4단계 — 9구조 재판정')
    rej = stage4_rejudge(thr)
    for r in rej:
        print(f'    {r["tag"]:<10} 6원 고리 {r["n_ring6"]:>3}  최대 {r["max"]:.4f}  '
              f'문턱 초과 {r["n_over"]:>3}  → {r["verdict"]}')
    broken = [r['tag'] for r in rej if r['verdict'] == '깨진 구조']
    out['rejudge'] = rej
    out['broken'] = broken
    out['qualifier'] = ('재선별(rescreening)이며 확증이 아니다 — (a) 값을 이미 본 뒤의 '
                        '재판정이다. T3_PRIME_20260904.md 2절.')
    json.dump(out, open(os.path.join(HERE, 't3_prime.json'), 'w',
                        encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n  깨진 구조 {len(broken)}/9: {broken or "없음"}')
    print(f'  ⚠️ {out["qualifier"]}')
    print('\n-> t3_prime.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
