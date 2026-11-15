# -*- coding: utf-8 -*-
"""COREPOP-H323 읽는 법 — `COREPOP_H323_READING_REGISTRATION_20261115.md` 의 계산을 그대로 하는 스크립트.
값을 보기 전(자료 0건)에 등록 문서와 함께 커밋. 등록 뒤에는 고치지 않음 — 고칠 일이 생기면 새 등록(CLAUDE.md §2).
보완 1(자료 0건 · 2026-11-15): 막음 없는 구조만의 민감도 판 · 판정 구간을 Fisher z(Bonett–Wright)로 · 부트스트랩은 참고.

물음 하나: 298 K 건조 Widom 선택도(§AV 우리 자, `core_pop_annotated.json` 의 `selectivity`) 순서가
323 K 습윤 3성분 선택도(결과 파일의 `S_humid`)에서도 유지되는가.

사용:  python corepop_h323_read.py <결과 json> [<결과 json> ...]
  각 결과 옆에 같은 이름의 `_audit.json` 이 있어야 함. 출력 = 화면 요약 + JSON(env READ_OUT, 기본 corepop_h323_reading_<묶음>.json).
  postman 글롭(results_*.json) 밖 이름 — 손으로 올림.
"""
import hashlib
import json
import math
import os
import random
import statistics as st
import sys
import time

D = os.path.dirname(os.path.abspath(__file__))
TGT = os.path.join(D, 'corepop_humid323_targets.json')
ANN = os.path.join(D, 'core_pop_annotated.json')
REG = 'COREPOP_H323_READING_REGISTRATION_20261115.md'
SEED = 20261115          # 부트스트랩 씨앗(등록)
NBOOT = 10000            # 부트스트랩 반복(등록)
FLAG_N2 = 0.20           # 깃발: N_N2_err / N_N2 > 0.20  (결과 머리 thresholds_registered 의 첫 조건)
FLAG_S = 0.10            # 깃발: S_humid_err / S_humid > 0.10 (같은 문자열의 둘째 조건, 1씨앗이라 평균 ± = 회차 ±)
TOPK = 10                # 상위 겹침 k
PAIR_UNITS = 1.5         # 개별 두 구조의 순위: |ΔS| ≥ 1.5 × hypot(±1, ±2) 일 때만(CLAUDE.md §2 「단위」, ± 는 RASPA 95 % 구간)


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def ranks(x):
    """평균 순위(동률은 평균)."""
    idx = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[idx[j + 1]] == x[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    ma, mb = st.fmean(a), st.fmean(b)
    sa = sum((x - ma) ** 2 for x in a)
    sb = sum((y - mb) ** 2 for y in b)
    if sa == 0 or sb == 0:
        return float('nan')
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) ** 0.5


def spearman(rows):
    return pearson(ranks([r['dry_sel'] for r in rows]), ranks([r['S'] for r in rows]))


def pct(v, q):
    v = sorted(x for x in v if x == x)
    if not v:
        return float('nan')
    k = (len(v) - 1) * q
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def boot_ci(rows, fn, seed):
    rng = random.Random(seed)
    n = len(rows)
    out = [fn([rows[rng.randrange(n)] for _ in range(n)]) for _ in range(NBOOT)]
    return pct(out, 0.025), pct(out, 0.975)


def fisher_bw(rows):
    """보완 1: 판정 구간 = Spearman ρ 의 Fisher z 95 % 구간, 분산은 Bonett–Wright (1 + ρ²/2)/(n − 3).
    무관 자료 보정 시험(n 16 · 30 · 48 · 80, 각 4,000회)에서 한쪽 거짓 양성 1.9 ~ 2.6 % — 백분위 부트스트랩은 n 48 에서 5.0 % 였음."""
    r = spearman(rows)
    n = len(rows)
    if not (abs(r) < 1) or n < 4:
        return float('nan'), float('nan')
    se = math.sqrt((1 + r * r / 2) / (n - 3))
    z = math.atanh(r)
    return math.tanh(z - 1.959964 * se), math.tanh(z + 1.959964 * se)


def median_s(rows):
    return st.median(r['S'] for r in rows)


def verdict(lo, hi):
    if lo > 0:
        return '유지 쪽 — 건조 선택도가 높을수록 습윤 S 도 높은 단조 관계(ρ 의 95 % CI 하한 > 0)'
    if hi < 0:
        return '뒤집힘 쪽 — ρ 의 95 % CI 상한 < 0'
    return '가릴 수 없음 — ρ 의 95 % CI 가 0 을 품음(관계가 없다는 뜻이 아님)'


def load(paths):
    T = {r['key']: r for r in json.load(open(TGT, encoding='utf-8'))['rows']}
    A = {r['key']: r for r in json.load(open(ANN, encoding='utf-8'))['rows']}
    rows, excluded, files, seen, batches = [], [], [], set(), set()
    for p in paths:
        ap = p[:-5] + '_audit.json'
        if not p.endswith('.json') or p.endswith('_audit.json'):
            raise SystemExit(f'!! 결과 파일이 아님: {p}')
        if not os.path.exists(ap):
            raise SystemExit(f'!! 감사 파일 없음: {ap}')
        d = json.load(open(p, encoding='utf-8'))
        au = {r['name']: r for r in json.load(open(ap, encoding='utf-8'))['rows']}
        if d.get('reps') != 1:
            raise SystemExit(f'!! reps {d.get("reps")} — 이 등록은 1씨앗 결과만 받음: {p}')
        files.append({'file': os.path.basename(p), 'md5': md5(p), 'audit_md5': md5(ap),
                      'machine': d.get('machine'), 'batches': d.get('batches'), 'n_rows': len(d['rows'])})
        batches.update(d.get('batches') or [])
        for r in d['rows']:
            k = r.get('core_key')
            if k in seen:
                raise SystemExit(f'!! 같은 구조가 두 번: {k}')
            seen.add(k)
            a = au.get(r.get('name'))
            S, Se, N, Ne = r.get('S_humid'), r.get('S_humid_err'), r.get('N_N2'), r.get('N_N2_err')
            num = lambda x: isinstance(x, (int, float)) and x == x
            why = None
            if k not in T:
                why = 'targets 밖'
            elif not (r.get('ok') is True and r.get('finished') is True):
                why = '결과 ok/finished 아님'
            elif not (a and a.get('ok') is True and a.get('finished') is True):
                why = '감사 ok/finished 아님'
            elif not (num(S) and S > 0 and num(Se) and num(N) and N > 0 and num(Ne)):
                why = 'S_humid · N_N2 값 없음'
            elif not num(A.get(k, {}).get('selectivity')):
                why = '건조 selectivity 없음'
            if why:
                excluded.append({'key': k, 'name': r.get('name'), 'why': why})
                continue
            flag = (Ne / N > FLAG_N2) or (Se / S > FLAG_S)
            bl, bc = r.get('input_blockpockets_lines'), r.get('blocked_components')          # 보완 1: 막음 표지
            if not isinstance(bl, int) or not isinstance(bc, list) or (bl > 0) != bool(bc):
                raise SystemExit(f'!! 막음 표지가 없거나 서로 어긋남({k}: input_blockpockets_lines {bl!r} · blocked_components {bc!r}) — 계산 안 함')
            rows.append({'key': k, 'batch': T[k]['batch'], 'dry_rank': T[k]['rank'], 'dry_sel': A[k]['selectivity'],
                         'S': S, 'S_err': Se, 'N2_rel': Ne / N, 'S_rel': Se / S, 'flag': flag, 'blocked': bool(bc),
                         'file': os.path.basename(p)})
    missing = sorted((T[k]['rank'], k) for k in T if T[k]['batch'] in batches and k not in seen)
    return rows, excluded, files, sorted(batches), [{'dry_rank': r, 'key': k} for r, k in missing]


def main(paths):
    rows, excluded, files, batches, missing = load(paths)
    if len(rows) < 10:
        raise SystemExit(f'!! 포함 행 {len(rows)} < 10 — 이 등록은 계산하지 않음')
    out = {'registration': REG, 'script_md5': md5(os.path.abspath(__file__)), 'made': time.strftime('%F %T'),
           'files': files, 'batches': batches, 'n_included': len(rows), 'excluded': excluded,
           'missing_from_results': missing, 'n_missing': len(missing),
           'ci_rule': 'ρ 판정 구간 = Fisher z 95 % · Bonett–Wright 분산(보완 1). ci95_bootstrap_ref 는 참고(판정에 안 씀)',
           'boot': {'seed': SEED, 'n': NBOOT, 'ci': 'percentile 95 % — ρ 는 참고 · 묶음 중앙값 구간에 씀'}}
    prim = spearman(rows)
    lo, hi = fisher_bw(rows)                                      # 보완 1: 판정 = Fisher z(Bonett–Wright) · 부트스트랩은 참고
    out['primary'] = {'rows': 'all included (flag 포함)', 'n': len(rows), 'spearman_rho': prim, 'ci95': [lo, hi],
                      'ci95_bootstrap_ref': list(boot_ci(rows, spearman, SEED)), 'verdict': verdict(lo, hi)}
    nf = [r for r in rows if not r['flag']]
    if len(nf) >= 10:
        p2 = spearman(nf)
        l2, h2 = fisher_bw(nf)
        out['sensitivity_no_flag'] = {'n': len(nf), 'flagged': [r['key'] for r in rows if r['flag']],
                                      'spearman_rho': p2, 'ci95': [l2, h2], 'ci95_bootstrap_ref': list(boot_ci(nf, spearman, SEED + 1)),
                                      'verdict': verdict(l2, h2)}
        out['flag_sensitive'] = verdict(lo, hi).split(' — ')[0] != verdict(l2, h2).split(' — ')[0]
    nb = [r for r in rows if not r['blocked']]                    # 보완 1: 323 K 에서 어느 성분도 막지 않은 구조만(298 K 건조도 막음 없음)
    out['sensitivity_no_block'] = {'n': len(nb), 'blocked': [r['key'] for r in rows if r['blocked']]}
    if len(nb) >= 10:
        p3 = spearman(nb)
        l3, h3 = fisher_bw(nb)
        out['sensitivity_no_block'].update({'spearman_rho': p3, 'ci95': [l3, h3], 'ci95_bootstrap_ref': list(boot_ci(nb, spearman, SEED + 2)),
                                            'verdict': verdict(l3, h3)})
        out['block_sensitive'] = verdict(lo, hi).split(' — ')[0] != verdict(l3, h3).split(' — ')[0]
    else:
        out['sensitivity_no_block']['verdict'] = '계산 안 함 — 막음 없는 행 10 미만'
    T = {r['key']: r for r in json.load(open(TGT, encoding='utf-8'))['rows']}
    per = []
    for i, b in enumerate(batches):
        br = [r for r in rows if r['batch'] == b]
        e = {'batch': b, 'n': len(br), 'n_missing': sum(1 for m in missing if T[m['key']]['batch'] == b)}
        if br:
            e['median_S'] = median_s(br)
            e['median_ci95'] = list(boot_ci(br, median_s, SEED + 10 + i)) if len(br) >= 5 else None
            e['n_flag'] = sum(r['flag'] for r in br)
        per.append(e)
    out['per_batch'] = per
    sep = []
    for a in per:
        for b in per:
            if a['batch'] < b['batch'] and a.get('median_ci95') and b.get('median_ci95'):
                (al, ah), (bl, bh) = a['median_ci95'], b['median_ci95']
                sep.append({'pair': [a['batch'], b['batch']], 'ci_separated': ah < bl or bh < al})
    out['per_batch_ci_separated'] = sep
    k = min(TOPK, len(rows))
    top_dry = {r['key'] for r in sorted(rows, key=lambda r: (-r['dry_sel'], r['key']))[:k]}
    by_s = sorted(rows, key=lambda r: (-r['S'], r['key']))
    top_s = {r['key'] for r in by_s[:k]}
    out['topk_overlap'] = {'k': k, 'overlap': len(top_dry & top_s), 'random_expectation': k * k / len(rows)}
    tab = []
    for i, r in enumerate(by_s[:k]):
        e = {'S_order': i + 1, 'key': r['key'], 'batch': r['batch'], 'dry_rank': r['dry_rank'], 'S': r['S'], 'S_err': r['S_err'], 'flag': r['flag']}
        if i + 1 < len(by_s):
            n2 = by_s[i + 1]
            e['vs_next_resolved'] = abs(r['S'] - n2['S']) >= PAIR_UNITS * (r['S_err'] ** 2 + n2['S_err'] ** 2) ** 0.5
        tab.append(e)
    out['top_by_S'] = tab
    dst = os.environ.get('READ_OUT') or os.path.join(D, f"corepop_h323_reading_{'_'.join(batches)}.json")
    json.dump(out, open(dst, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"포함 {len(rows)} · 제외 {len(excluded)} · 결과에 없음(막음 실패 등) {len(missing)} · 묶음 {batches}")
    print(f"주 ρ = {prim:.3f}  95 % CI [{lo:.3f}, {hi:.3f}]  → {out['primary']['verdict']}")
    if 'sensitivity_no_flag' in out:
        s = out['sensitivity_no_flag']
        print(f"깃발 뺀 ρ = {s['spearman_rho']:.3f}  [{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}] (n {s['n']}, 깃발 {len(s['flagged'])}) · 깃발에 민감 {out['flag_sensitive']}")
    s = out['sensitivity_no_block']
    if 'spearman_rho' in s:
        print(f"막음 없는 구조만 ρ = {s['spearman_rho']:.3f}  [{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}] (n {s['n']}, 막음 {len(s['blocked'])}) · 막음에 민감 {out['block_sensitive']}")
    else:
        print(f"막음 없는 구조만: {s['verdict']} (n {s['n']})")
    for e in per:
        ci = e.get('median_ci95')
        print(f"  {e['batch']}: n {e['n']} · 빠짐 {e['n_missing']} · 중앙 S {e.get('median_S', float('nan')):.2f}"
              f"{f' [{ci[0]:.2f}, {ci[1]:.2f}]' if ci else ''} · 깃발 {e.get('n_flag', 0)}")
    print(f"  묶음 CI 분리: {[(x['pair'], x['ci_separated']) for x in sep]}")
    print(f"  상위 {k} 겹침 {out['topk_overlap']['overlap']} (무작위 기대 {out['topk_overlap']['random_expectation']:.2f})")
    print(f"저장 {dst}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1:]))
