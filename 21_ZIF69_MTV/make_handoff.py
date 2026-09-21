# -*- coding: utf-8 -*-
"""§9-1 재배분 — 랩탑이 받아 갈 **laptop2 대기열의 꼬리**를 뽑는다.

[왜 꼬리인가 — laptop2 가 제 초안을 깼습니다]
    초안은 "N_super 오름차순으로 절반" 이었습니다. 전제는 "laptop2 는 LPT 라 큰 것부터 내려오니
    작은 것부터 올라가면 안 마주친다" 였는데, **도는 프로세스는 NAtoms 로 정렬돼 있습니다**
    (N_super 정렬 수정 ddf73bf 는 그 뒤에 나왔고 파이썬은 도는 프로세스에 안 걸립니다).
    두 자의 순위 상관은 **스피어만 rho = +0.206** — 거의 무관합니다. 재현 결과 랩탑 완주 시점에
    laptop2 에 남는 139종 중 **80종(58 %)** 이 전체 하위 절반이라, 초안대로면 정면으로 겹칩니다.

    **고친 자: laptop2 의 실제 대기열 순서의 꼬리부터.** 그 자리가 laptop2 가 가장 늦게 닿는 곳이라
    겹침이 0 입니다. laptop2 의 대기열은 결정적으로 재현됩니다 —
    `core_pop_pick.json` 순서(CoRE K_H 오름차순)를 **NAtoms 내림차순으로 안정정렬**한 것입니다.

[쓰는 법 — 랩탑이 자기 204종을 끝낸 직후]
    git pull                                   # laptop2 최신 결과 JSON 을 받는다
    python make_handoff.py                     # -> core_pop_handoff.json (+ 화면에 명령 한 줄)
    COREPOP_ASSIGN=laptop2 COREPOP_MACHINE=laptop COREPOP_WORKERS=8 \
      COREPOP_PICK=core_pop_handoff.json \
      COREPOP_OUT=core_pop_results_laptop2_by_laptop.json \
      setsid nohup python -u run_core_pop.py > ../.claude_work_corepop_hand.out 2>&1 < /dev/null &

    ★ `COREPOP_OUT` 을 **반드시 따로** 주십시오. `core_pop_results_laptop2.json` 을 그대로 쓰면
      laptop2 프로세스와 같은 파일을 동시에 덮어써 서로의 행을 잃습니다(작업마다 갱신하는 구조).
    ★ `COREPOP_MACHINE=laptop` 을 빼면 **전달자가 측정자로 기록**됩니다.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = 0.651                      # T-BR-1 24점 실측 지수 (cost_scan_core_pop.py)
K2 = 13.10 / 396 ** B          # laptop2 분/작업 (자기 실측 눈금, 12워커)
K1 = 18.03 / 1520 ** B         # laptop  분/작업 (자기 실측 눈금, 8워커)
W2, W1 = 12, 8


def queue(pick):
    """도는 laptop2 프로세스의 대기열 순서를 그대로 재현한다(안정정렬)."""
    s = [p for p in pick if p.get('assign') == 'laptop2']
    return sorted(s, key=lambda p: -int(p.get('NAtoms') or 0))



def premise_gate(q, done, pick):
    """★ 꼬리 논리의 **전제**를 laptop2 의 완주분으로 검증한다(랩탑 09-21 15:0x 추가).

    이 스크립트 전체가 "laptop2 대기열 = pick 순서를 NAtoms 내림차순 안정정렬" 위에 서 있다.
    그 전제는 laptop2 가 **옛 코드로 돌고 있을 때만** 참이다 — 만약 그쪽이 N_super 정렬
    (ddf73bf) 이후에 재기동했다면 대기열이 달라지고, 그러면 "꼬리" 가 꼬리가 아니라서
    **정면으로 겹칩니다.** 겹침은 오염이 아니라 낭비지만, 7 h 단축을 노리고 7 h 를 버립니다.

    전제는 마침 **이 스크립트가 돌 수 있게 되는 순간**(laptop2 결과 JSON 도착)에 검증
    가능해진다 — 완주분이 어느 정렬의 앞머리와 맞는지 보면 된다. 그래서 관문으로 만든다.
    """
    n = len(done)
    if n < 8:
        print(f'  .. 전제 검증 보류 — laptop2 완주 {n}종으로는 정렬을 못 가립니다(8종 이상 필요).')
        return True
    l2 = [p for p in pick if p.get('assign') == 'laptop2']
    heads = {
        'NAtoms 내림차순(전제)': [p['file'] for p in sorted(l2, key=lambda x: -int(x.get('NAtoms') or 0))][:n],
        'N_super 내림차순(새 자)': [p['file'] for p in sorted(l2, key=lambda x: -int(x.get('N_super') or 0))][:n],
    }
    hit = {k: len(set(v) & done) for k, v in heads.items()}
    for k, v in hit.items():
        print(f'  전제 검증  {k:24} 완료분과 겹침 {v}/{n}')
    if hit['NAtoms 내림차순(전제)'] >= hit['N_super 내림차순(새 자)']:
        return True
    print('  !! **전제가 깨졌습니다** — laptop2 대기열이 NAtoms 순이 아닙니다'
          '(새 코드로 재기동했을 가능성). 꼬리가 꼬리가 아니므로 이 목록은 겹칩니다.',
          flush=True)
    print('     laptop2 에 실제 정렬을 묻고 `queue()` 를 맞춘 뒤 다시 도십시오.'
          ' (그래도 강행하려면 `--force-premise`.)', flush=True)
    return '--force-premise' in sys.argv


def main():
    pick = json.load(open(os.path.join(HERE, 'core_pop_pick.json'), encoding='utf-8'))
    q = queue(pick)

    done = set()
    f2 = os.path.join(HERE, 'core_pop_results_laptop2.json')
    if os.path.exists(f2):
        d = json.load(open(f2, encoding='utf-8'))
        done = {r['file'] for r in d.get('rows', []) if r.get('status') == 'ok'}
        print(f'laptop2 완료 {len(done)}종 (core_pop_results_laptop2.json)')
    else:
        print('!! core_pop_results_laptop2.json 이 없습니다.', flush=True)
        print('   `git pull` 로 laptop2 의 최신 결과를 받고 다시 도십시오.', flush=True)
        print('   이 파일 없이 만든 목록은 laptop2 가 **이미 끝낸 것까지 포함**해 낭비가 됩니다.', flush=True)
        print('   (정말 빈 상태에서 만들려면 `--force`.)', flush=True)
        if '--force' not in sys.argv:
            return 2

    if not premise_gate(q, done, pick):
        return 3

    rest = [p for p in q if p['file'] not in done]
    t2 = lambda p: 2 * K2 * p['N_super'] ** B / 60
    t1 = lambda p: 2 * K1 * p['N_super'] ** B / 60

    best = None
    for k in range(len(rest) + 1):
        tail = rest[len(rest) - k:]
        a = sum(t1(p) for p in tail) / W1          # 랩탑이 도는 시간
        b = sum(t2(p) for p in rest[:len(rest) - k]) / W2   # laptop2 가 남기는 시간
        m = max(a, b)
        if best is None or m < best[0]:
            best = (m, k, a, b)
    m, k, a, b = best
    tail = rest[len(rest) - k:]

    print(f'남은 {len(rest)}종 · 랩탑이 받을 **꼬리 {k}종**')
    print(f'  랩탑 {a:.2f} h · laptop2 {b:.2f} h · 두 기기 동시 종료까지 **{m:.2f} h**')
    print(f'  재배분 없으면 laptop2 단독 {sum(t2(p) for p in rest)/W2:.2f} h '
          f'-> **{sum(t2(p) for p in rest)/W2 - m:.1f} h 단축**')
    print(f'  겹침 0 — 이 {k}종은 laptop2 대기열의 맨 뒤라 가장 늦게 닿습니다.')

    out = os.path.join(HERE, 'core_pop_handoff.json')
    json.dump(tail, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n저장 {out}  ({len(tail)}종)')
    print('\n기동:')
    print('  COREPOP_ASSIGN=laptop2 COREPOP_MACHINE=laptop COREPOP_WORKERS=8 \\')
    print('    COREPOP_PICK=core_pop_handoff.json \\')
    print('    COREPOP_OUT=core_pop_results_laptop2_by_laptop.json \\')
    print('    setsid nohup ~/miniconda3/envs/czeromof/bin/python -u run_core_pop.py \\')
    print('    > ../.claude_work_corepop_hand.out 2>&1 < /dev/null &')
    return 0


if __name__ == '__main__':
    sys.exit(main())
