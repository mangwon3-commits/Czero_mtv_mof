# -*- coding: utf-8 -*-
"""COREPOP-H323 — 재시도 단계에서 멈춘 막음 파일에서 '세 탐침 ok' 부분집합을 만들고(b03a 와 같은 방법), 빠진 구조를 넘길 키 파일을 만듦.
b03a(desktop 11-14 23:05 글)는 손으로 만들었고, 이 도구는 그 규칙을 그대로 코드로 옮긴 것(사용자 지시 2026-11-15 "랩탑으로 넘겨").
  subset  python corepop_subset_blocks.py subset <멈춘 막음 파일> [--out <경로>] [--why <문장>]
          → <이름>a.json: 행 · 값 · 파일 · md5 무변경. 세 탐침 모두 block_ok True · n_spheres 있음 · .block md5 재대조가 맞는 행만.
            derived_from · excluded_not_ok(+사유) · finished(만든 시각) · finished_note · summary · all_blocks_ok · n_rows 를 붙임. 원판은 안 건드림.
            원판에 'finished' 가 있으면(완주 파일) 만들지 않음 — 그때는 부분집합이 필요 없음.
  keys    python corepop_subset_blocks.py keys <키 파일 출력> <부분집합 파일> [<부분집합 파일> ...] [--why <문장>]
          → {'keys': [...], 'sources': [...]} — 각 부분집합의 excluded_not_ok 를 대상 목록 순서로 합침(중복이면 멈춤).
기계적 사실뿐 — 값 읽기 · 판정 없음.
"""
import hashlib
import json
import os
import sys
import time

D = os.path.dirname(os.path.abspath(__file__))
TGT = os.path.join(D, 'corepop_humid323_targets.json')
PROBES = ('1.65', '1.82', '1.30')


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        v = sys.argv[i + 1]
        del sys.argv[i:i + 2]
        return v
    return default


def why_not_ok(r):
    for x in PROBES:
        c = r.get(f'r{x}')
        if c is None:
            return f'r{x} 미시도'
        if c.get('block_ok') is not True or c.get('n_spheres') is None:
            return f"r{x} 실패(rc {c.get('rc')} · 가드 {c.get('stopped_by_guard')} · 최대 {c.get('peak_rss_MB')} MB)"
        bf = c.get('block_file')
        if not bf or not os.path.exists(os.path.join(D, bf)) or md5(os.path.join(D, bf)) != c.get('block_md5'):
            return f'r{x} .block 파일 없음 또는 md5 불일치'
    return None


def subset(src, out, why):
    d = json.load(open(src, encoding='utf-8'))
    if 'finished' in d:
        raise SystemExit(f'!! {os.path.basename(src)} 는 완주 파일 — 부분집합이 필요 없음')
    keep, excl, reasons = [], [], {}
    for r in d['rows']:
        w = why_not_ok(r)
        if w:
            excl.append(r['key'])
            reasons[r['key']] = w
        else:
            keep.append(r)
    if not keep:
        raise SystemExit('!! 세 탐침 ok 행 0 — 만들지 않음')
    o = {k: v for k, v in d.items() if k not in ('rows', 'summary', 'all_blocks_ok', 'n_needing_blockpockets', 'aborted')}
    o['derived_from'] = {'file': os.path.basename(src), 'md5': md5(src),
                         'note': '재시도 단계에서 멈춘 막음 실행의 행을 그대로 옮김 — 값 · 파일 · md5 무변경 (corepop_subset_blocks.py)'}
    o['why'] = why
    o['rows'] = keep
    o['n_rows'] = len(keep)
    o['excluded_not_ok'] = excl
    o['excluded_reasons'] = reasons
    o['all_blocks_ok'] = True
    o['summary'] = {r['key']: {f'spheres_{x}': r[f'r{x}']['n_spheres'] for x in PROBES} for r in keep}
    o['finished'] = time.strftime('%F %T')
    o['finished_note'] = f'이 부분집합 파일을 만든 시각 — 담긴 {len(keep)}행은 각자 Zeo++ 호출이 rc 0 · 가드 없음 · .block 1개로 끝난 것(.block md5 재대조 {len(keep)}×3)'
    tmp = out + '.tmp'
    json.dump(o, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, out)
    print(f'부분집합 {os.path.basename(out)}: ok {len(keep)} · 빠짐 {len(excl)} · 원판 {os.path.basename(src)} md5 {md5(src)[:8]}')
    for k in excl:
        print(f'  빠짐 {k}: {reasons[k]}')
    return 0


def keys(out, files, why):
    order = [r['key'] for r in json.load(open(TGT, encoding='utf-8'))['rows']]
    ks, src = [], []
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        if 'derived_from' not in d or 'excluded_not_ok' not in d:
            raise SystemExit(f'!! {os.path.basename(f)} 는 부분집합 파일이 아님')
        ks += d['excluded_not_ok']
        src.append({'file': os.path.basename(f), 'md5': md5(f), 'excluded_not_ok': d['excluded_not_ok'],
                    'excluded_reasons': d.get('excluded_reasons')})
    if len(set(ks)) != len(ks):
        raise SystemExit('!! 같은 구조가 두 부분집합에서 빠짐 — 확인')
    ks = sorted(ks, key=order.index)
    o = {'test': 'COREPOP-H323 — 다른 기기에서 막음이 안 된 구조(넘길 목록)', 'why': why, 'made': time.strftime('%F %T'),
         'keys': ks, 'n': len(ks), 'sources': src}
    json.dump(o, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'키 파일 {os.path.basename(out)}: {len(ks)}구조 · 출처 {[s["file"] for s in src]}')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('subset', 'keys'):
        raise SystemExit(__doc__)
    why = arg('--why', '')
    out = arg('--out')
    if sys.argv[1] == 'subset':
        s = sys.argv[2]
        sys.exit(subset(s, out or s[:-5] + 'a.json', why))
    sys.exit(keys(sys.argv[2], sys.argv[3:], why))
