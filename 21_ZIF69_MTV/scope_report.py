"""글롭이 어느 버전의 파일을 쓸어 왔는지 먼저 말해 주는 도구.

[왜 있나]
    CLAUDE.md §2 는 *"v1/v2/v3 는 서로 다른 구조에서 나왔습니다. 버전을 넘나들며
    인용하지 마세요"* 라고 적었고, 저장소는 같은 실수를 **반복**했습니다.

        08-2x  `risk_results*.json` 을 넓게 잡아 v1/v2 파일이 섞임
               -> saIm100 이 관문을 통과한 것처럼 보임 (15.74% vs v3 의 22.50%)
        09-05  `*/water_results*.json` 을 넓게 잡아 v2 계열이 섞임
               -> RH0 분모가 "오염됐다" 는 정반대 결론이 나올 뻔함
                  (v3 만 보면 최대 0.45 단위, v2 를 섞으면 18.91 단위)

    **두 번 다 값이 이상해서가 아니라 출처를 물어서 갈렸습니다.** 그래서 도구는
    값을 안 봅니다 — **어느 파일이 잡혔는지와 그 버전만** 말합니다.

[쓰는 법]
    python scope_report.py '<글롭>' ['<글롭>' ...]

    마지막 줄에 **주장에 그대로 붙일 범위 문장**이 나옵니다. 저장소 규율은
    *"전수·전량 주장에는 조회 범위를 함께 적는다"* 이므로, 그 줄을 판정문이나
    우편함 글에 복사해 넣으십시오.

    버전이 둘 이상 섞이면 **종료코드 1** 입니다. 관문으로 써도 되고, 섞는 것이
    의도라면 그 사실을 범위 문장에 적고 넘어가면 됩니다.

[한계 — 경로만 봅니다]
    파일 **내용**의 버전은 안 봅니다. 경로에 표시가 없는 구판(`water_results.json`,
    `results_v2.json` 같은 저장소 뿌리의 것)은 `표시없음` 으로 묶습니다.
    **`표시없음` 이 하나라도 있으면 사람이 직접 확인해야 합니다** — 09-05 에
    분모를 오염시킬 뻔한 것이 바로 그 무리였습니다.
"""
import glob as _glob
import os
import re
import sys
from collections import OrderedDict

PATS = OrderedDict([
    # v3w 는 **v3 앞에** 둡니다 — 뒤에 두면 `v3` 규칙이 먼저 물어 v3w 산출물이
    # 결함 힘장 계열로 잡힙니다(WATER_FIX_20260906.md §2). 순서가 판정입니다.
    ('v3w', re.compile(r'(^|[/_])v3w|_v3w([_./]|$)')),
    ('v4', re.compile(r'(^|[/_])v4|_v4([_./]|$)')),
    ('v3', re.compile(r'(^|[/_])v3|_v3([_./]|$)')),
    ('v2', re.compile(r'(^|[/_])v2|_v2([_./]|$)')),
    ('v1', re.compile(r'(^|[/_])v1|_v1([_./]|$)')),
])

def version_of(path):
    p = path.replace('\\', '/')
    for name, rx in PATS.items():
        if rx.search(p):
            return name
    return '표시없음'

def main(argv):
    if not argv:
        print(__doc__.strip()); return 2
    groups = OrderedDict()
    total = 0
    for pat in argv:
        for f in sorted(_glob.glob(pat, recursive=True)):
            if not os.path.isfile(f):
                continue
            groups.setdefault(version_of(f), []).append(f)
            total += 1
    if not total:
        print(f'  매칭 0개 — 글롭이 아무것도 안 잡았습니다: {argv}')
        return 1
    order = [k for k in list(PATS) + ['표시없음'] if k in groups]
    print(f'  글롭 {argv}')
    print(f'  매칭 **{total}개**, 버전 **{len(order)}종**\n')
    for k in order:
        fs = groups[k]
        mark = '  ⚠️' if k == '표시없음' else ''
        print(f'  [{k}] {len(fs)}개{mark}')
        for f in fs[:8]:
            print(f'      {f}')
        if len(fs) > 8:
            print(f'      … 외 {len(fs)-8}개')
    counts = ', '.join(f'{k} {len(groups[k])}' for k in order)
    print(f'\n  범위 문장 (그대로 붙여 쓰십시오):')
    print(f'    > 조회 범위: `{" ".join(argv)}` — 매칭 {total}개 ({counts}).')
    if '표시없음' in groups:
        print('\n  ⚠️ **`표시없음` 이 있습니다.** 경로에 버전 표시가 없는 파일은')
        print('     도구가 판정하지 못합니다. 내용을 직접 확인하십시오.')
    if len(order) > 1:
        print(f'\n  🔴 **버전이 {len(order)}종 섞였습니다.** §2 는 버전을 넘나드는')
        print('     인용을 금합니다. 섞는 것이 의도라면 범위 문장에 그렇게 적으십시오.')
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
