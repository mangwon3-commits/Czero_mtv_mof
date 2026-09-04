"""참조 감사 — 취합 전에 돌린다 (ASSIGN_20260903 §4 ⑤ · ASSIGN_20260904 §2 D2).

09-03 에 master 가 5~16회씩 인용하던 판정 문서 8건이 `laptop-20260822` 에만
있었습니다(§4 ①② 위반). 사람이 눈으로 잡은 그 사례를 기계로 잡습니다.

규칙은 09-03 에 랩탑·laptop2 가 실제로 돌려 얻은 것 그대로이고, 여기서
새로 만들지 않습니다:

  ① 양방향으로 본다
     (a) master 문서가 인용하는데 **master 에 없는** .md
     (b) 가지 문서가 인용하는데 **그 가지에만 있는** .md   <- 8건이 이 모양

  ② "master 에 없음" 만으로 끊긴 참조로 판정하지 않는다.
     **master 에 없음 AND `COMMS.md` 등록표로 가지·상태를 알 수 없음** 일 때만.
     (`cloud4c.md` 는 14곳 인용·master 부재지만 등록표가 가지와 종료 상태를
      적어 두어 도달 가능 = 오탐)

  ③ 파일명 정규식에 **선행 숫자**를 넣는다.
     `48H_COMPUTE_PLAN.md` 가 잘려 오탐 난 전력.

  ③' [09-04 추가] 잘린 이름이 **문서 본문에 예시로 적혀** 있으면 정규식만으로는
     못 거릅니다(③ 을 설명하는 문장 자체가 잘린 이름을 담고 있습니다). 그래서
     플래그된 이름이 master 실파일 basename 의 **접미사**이면 '오탐(잘린 인용)'
     으로 자동 분류합니다. 사람 목록이 필요 없습니다.

  ④ [09-04 추가] 아직 만들지 않은 **예정 산출물**은 `ref_audit_ignore.json` 에
     사유와 함께 등록합니다. 억제한 것도 요약에 찍습니다 — 조용히 숨기면
     이 감사가 하려던 일과 반대가 됩니다.

산출: ref_audit.json + 사람이 읽을 요약.

    python ref_audit.py                     # master + 원격 가지 전부
    python ref_audit.py --refs origin/laptop-20260822 origin/junseok
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# ③ 선행 숫자를 허용한다. 경로 붙은 인용(`21_ZIF69_MTV/TIERS.md`)도 받는다.
MD_RE = re.compile(
    r'(?<![A-Za-z0-9_./-])'
    r'((?:[0-9A-Za-z_][0-9A-Za-z_.-]*/)*[0-9A-Za-z_][0-9A-Za-z_.-]*\.md)')

# 인용으로 세지 않는 것 — 글롭·자리표시자
SKIP = re.compile(r'[*?<>{}]')


def git(*args, cwd=REPO):
    return subprocess.run(('git',) + args, cwd=cwd, capture_output=True,
                          text=True, check=True).stdout


def md_files(ref):
    """ref 에 실재하는 .md 경로 집합."""
    out = set()
    for line in git('ls-tree', '-r', '--name-only', ref).splitlines():
        if line.endswith('.md'):
            out.add(line)
    return out


def read(ref, path):
    try:
        return git('show', f'{ref}:{path}')
    except subprocess.CalledProcessError:
        return ''


def citations(ref, paths):
    """{인용된 basename: [(인용한 파일, 횟수)]}"""
    cited = defaultdict(list)
    for p in sorted(paths):
        text = read(ref, p)
        if not text:
            continue
        counts = defaultdict(int)
        for m in MD_RE.finditer(text):
            name = m.group(1)
            if SKIP.search(name):
                continue
            base = os.path.basename(name)
            if base == os.path.basename(p):      # 자기 자신
                continue
            counts[base] += 1
        for base, n in counts.items():
            cited[base].append({'by': p, 'n': n})
    return cited


def registry(ref):
    """COMMS.md 등록표에서 이름 -> 그 이름이 적힌 줄들.

    ② 의 '가지·상태를 알 수 없음' 판정에 쓴다. 이름이 등록표에 있으면
    사람이 그 줄에서 가지와 상태를 읽을 수 있으므로 도달 가능으로 본다.
    """
    hit = defaultdict(list)
    text = read(ref, '21_ZIF69_MTV/COMMS.md')
    for i, line in enumerate(text.splitlines(), 1):
        for m in MD_RE.finditer(line):
            name = m.group(1)
            if SKIP.search(name):
                continue
            hit[os.path.basename(name)].append(i)
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', nargs='*', default=None,
                    help='검사할 가지 (기본: 원격 가지 전부)')
    ap.add_argument('--master', default='master')
    ap.add_argument('--json', default=os.path.join(HERE, 'ref_audit.json'))
    a = ap.parse_args()

    if a.refs is None:
        a.refs = [r.strip() for r in git('for-each-ref', '--format=%(refname:short)',
                                         'refs/remotes/origin').splitlines()
                  if r.strip() and not r.strip().endswith('/HEAD')
                  and r.strip() != 'origin/' + a.master]

    ignore = {}
    ig_path = os.path.join(HERE, 'ref_audit_ignore.json')
    if os.path.exists(ig_path):
        ignore = {e['name']: e for e in json.load(open(ig_path, encoding='utf-8'))}

    m_files = md_files(a.master)
    m_base = {os.path.basename(p) for p in m_files}
    m_cited = citations(a.master, m_files)
    reg = registry(a.master)

    # (a) master 가 인용하는데 master 에 없는 것
    a_rows = []
    for base, by in sorted(m_cited.items()):
        if base in m_base:
            continue
        lines = reg.get(base)
        found_in = [r for r in a.refs
                    if any(os.path.basename(x) == base for x in md_files(r))]
        # ③' 잘린 인용 — 실파일 basename 의 접미사인가
        truncated = sorted(b for b in m_base
                           if b != base and b.endswith(base))
        if lines:
            verdict = '도달 가능(COMMS.md 등록표)'
        elif truncated:
            verdict = '오탐(잘린 인용)'
        elif base in ignore:
            verdict = '보류(사유 등록)'
        else:
            verdict = '끊긴 참조'
        a_rows.append({
            'name': base,
            'cited_by': by,
            'total_citations': sum(x['n'] for x in by),
            'registry_lines': lines or [],
            'truncation_of': truncated,
            'found_in_refs': found_in,
            'ignore_reason': ignore.get(base, {}).get('reason'),
            'verdict': verdict,
        })

    # (b) 가지 문서가 인용하는데 그 가지에만 있는 것
    b_rows = []
    for ref in a.refs:
        r_files = md_files(ref)
        only = {p for p in r_files if os.path.basename(p) not in m_base}
        if not only:
            continue
        r_cited = citations(ref, r_files)
        for p in sorted(only):
            base = os.path.basename(p)
            by = r_cited.get(base, [])
            b_rows.append({
                'branch': ref, 'path': p,
                'cited_by': by,
                'total_citations': sum(x['n'] for x in by),
                'verdict': ('취합 대상 — 인용되고 있고 master 에 없음' if by
                            else '가지 전용 문서(인용 없음)'),
            })

    out = {'rule': 'ASSIGN_20260903 §4 ⑤ (규칙 ①②③)',
           'master': a.master, 'refs': a.refs,
           'master_md_count': len(m_files),
           'a_master_cites_missing': a_rows,
           'b_branch_only_cited': b_rows}
    with open(a.json, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    broken = [r for r in a_rows if r['verdict'] == '끊긴 참조']
    reach = [r for r in a_rows if r['verdict'] == '도달 가능(COMMS.md 등록표)']
    trunc = [r for r in a_rows if r['verdict'] == '오탐(잘린 인용)']
    held = [r for r in a_rows if r['verdict'] == '보류(사유 등록)']
    merge = [r for r in b_rows if r['cited_by']]

    print(f'=== 참조 감사 — master({len(m_files)}개 .md) 대 {len(a.refs)} 가지 ===\n')
    print(f'(a) master 가 인용하는데 master 에 없는 .md — 끊긴 참조 **{len(broken)}건**')
    print(f'    (제외: 등록표 도달 가능 {len(reach)} · 잘린 인용 {len(trunc)} · '
          f'사유 등록 {len(held)})')
    for r in broken:
        print(f'    ✗ {r["name"]:<40} {r["total_citations"]:>3}회  '
              f'← {", ".join(x["by"] for x in r["cited_by"][:3])}')
    for r in reach:
        tail = (f'등록표 {r["registry_lines"][:3]} → 도달 가능'
                if r['found_in_refs'] else
                f'등록표 {r["registry_lines"][:3]} → 도달 가능이나 '
                f'**어느 가지에도 실파일 없음**')
        print(f'    · {r["name"]:<40} {r["total_citations"]:>3}회  {tail}')
    for r in trunc:
        print(f'    · {r["name"]:<40} {r["total_citations"]:>3}회  '
              f'← 실파일 {r["truncation_of"][0]} 의 잘린 인용 → 오탐')
    for r in held:
        print(f'    · {r["name"]:<40} {r["total_citations"]:>3}회  '
              f'보류: {r["ignore_reason"]}')
    print(f'\n(b) 가지에만 있으면서 그 가지 안에서 인용되는 .md — **{len(merge)}건** '
          f'(취합 전에 잡을 것)')
    for r in merge:
        print(f'    ! {r["branch"]:<28} {r["path"]:<48} {r["total_citations"]:>3}회')
    if not merge:
        print('    (없음)')
    print(f'\n-> {a.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
