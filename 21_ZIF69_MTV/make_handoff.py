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
B = 0.651                      # T-BR-1 **구조 12점** 실측 지수 (cost_scan_core_pop.py) · 95 % CI [0.500, 0.801]
PAIRS = 10                     # §9-6 겹치는 짝 — 기기 항 검정용(laptop2 완주분에서 크기 분위로)
K2 = 13.10 / 396 ** B          # laptop2 분/작업 (자기 실측 눈금, 12워커)
K1 = 18.03 / 1520 ** B         # laptop  분/작업 (자기 실측 눈금, 8워커)
W2, W1 = 12, 8


def queue(pick, order='NAtoms'):
    """도는 laptop2 프로세스의 대기열 순서를 그대로 재현한다(안정정렬).

    `order` 는 `premise_gate` 가 완주분으로 **확인한** 자입니다 — 기본은 전제(NAtoms)이고,
    증거가 N_super 를 가리키면 그쪽으로 바뀝니다(laptop2 가 새 코드로 재기동한 경우).
    """
    s = [p for p in pick if p.get('assign') == 'laptop2']
    key = (lambda p: -int(p.get('NAtoms') or 0)) if order == 'NAtoms' else \
          (lambda p: -int(p.get('N_super') or 0))
    return sorted(s, key=key)



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
        print(f'  전제 검증  {k:24} 완료분과 겹침 {v}/{n} = {v/n*100:.0f} %')

    best = max(hit, key=hit.get)

    # ① **둘 다 안 맞으면 막는다** (데스크탑 09-21 15:1x 보탬).
    #    랩탑의 원판은 두 후보를 **서로** 견주기만 해서, 둘 다 형편없어도 NAtoms 쪽이 조금만
    #    높으면 통과했습니다. laptop2 가 우리가 모르는 순서로 돌고 있으면(다른 pick 파일,
    #    다른 워커, 손으로 좁힌 목록) 꼬리 논리 자체가 성립하지 않습니다. 절대 문턱을 둡니다.
    if hit[best] < 0.75 * n:
        print(f'  !! **어느 정렬로도 설명이 안 됩니다**(최고 {hit[best]}/{n} < 75 %). '
              f'laptop2 가 우리가 모르는 순서로 돌고 있습니다.', flush=True)
        print('     꼬리 논리가 성립하지 않습니다. laptop2 에 실제 대기열을 물으십시오.'
              ' (강행하려면 `--force-premise` — 권하지 않습니다.)', flush=True)
        return '--force-premise' in sys.argv

    # ② **N_super 쪽이 이기면 막지 말고 그 자를 쓴다** (데스크탑 보탬).
    #    막으면 7 h 단축을 통째로 잃습니다. laptop2 가 새 코드로 재기동했다는 뜻일 뿐이고,
    #    그 경우의 올바른 꼬리는 **N_super 내림차순의 꼬리**입니다 — 우리가 그 순서도 압니다.
    if best != 'NAtoms 내림차순(전제)':
        print(f'  ** 전제와 다릅니다 — laptop2 대기열이 **{best}** 입니다'
              f'(새 코드로 재기동한 것으로 보입니다).', flush=True)
        print('     막지 않고 **그 자의 꼬리**로 뽑습니다. 꼬리 논리는 그대로 섭니다.', flush=True)
        premise_gate.order = 'N_super'
    return True


def own_share_gate(pick):
    """★ **랩탑이 자기 204종을 먼저 끝냈는가.** (데스크탑 09-21 15:1x 추가)

    §9-1 의 발동 조건이 바로 이것인데 스크립트가 **안 보고 있었습니다.** 지금(15:07) 돌려 보니
    laptop2 완주 4종 기준으로 **172종**을 넘기라고 나옵니다 — 랩탑이 자기 몫을 도는 중에
    그걸 받으면 자기 204종이 늦어지고 재배분의 목적이 뒤집힙니다.
    """
    mine = [p for p in pick if p.get('assign') == 'laptop']
    f = os.path.join(HERE, 'core_pop_results_laptop.json')
    if not os.path.exists(f):
        print(f'!! core_pop_results_laptop.json 이 없습니다 — 랩탑 몫 0/{len(mine)}.', flush=True)
        print('   §9-1 발동 조건은 **랩탑이 자기 204종을 완주한 뒤** 입니다.', flush=True)
        return '--force-own' in sys.argv
    d = json.load(open(f, encoding='utf-8'))
    ok = sum(1 for r in d.get('rows', []) if r.get('status') == 'ok')
    if ok < len(mine):
        print(f'!! 랩탑 자기 몫 **{ok}/{len(mine)}** — 아직 완주 전입니다.', flush=True)
        print('   §9-1 발동 조건은 자기 몫 완주입니다. 끝난 뒤 다시 도십시오.'
              ' (강행하려면 `--force-own`.)', flush=True)
        return '--force-own' in sys.argv
    print(f'  랩탑 자기 몫 {ok}/{len(mine)} 완주 — 발동 조건 충족.')
    return True


def main():
    pick = json.load(open(os.path.join(HERE, 'core_pop_pick.json'), encoding='utf-8'))
    if not own_share_gate(pick):
        return 4
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
    # 관문이 증거로 **다른 자**를 확인했으면 대기열을 그 자로 다시 세웁니다.
    if getattr(premise_gate, 'order', 'NAtoms') != 'NAtoms':
        q = queue(pick, premise_gate.order)
        print(f'  대기열을 {premise_gate.order} 자로 다시 세웠습니다.')

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

    # ★ §9-6 겹치는 짝 — **기기 항을 보려면 같은 구조를 두 기기에서 재야 합니다**(랩탑 09-21 15:3x).
    #   배수가 튼튼했던 이유가 구조 성질의 약분인데, 서로 다른 구조로 두 기기를 견주면 구조 사이 퍼짐
    #   21 % 가 그대로 들어와 경합 차이 8 % 를 덮습니다. 지금 설계로는 겹치는 짝이 **0** 입니다.
    #   **laptop2 가 이미 끝낸 것** 중에서 고르므로 충돌 위험이 없습니다(그쪽은 다시 안 돕니다).
    donep = [p for p in queue(pick) if p['file'] in done]
    donep.sort(key=lambda p: p['N_super'])
    pairs = []
    if len(donep) >= PAIRS:
        idx = [round((i + 0.5) * len(donep) / PAIRS) for i in range(PAIRS)]   # 크기 분위로 고르게
        seen = set()
        for i in idx:
            q_ = donep[min(i, len(donep) - 1)]
            if q_['file'] not in seen:
                seen.add(q_['file']); pairs.append(dict(q_, pair=True))
    else:
        print(f'  .. 겹치는 짝 보류 — laptop2 완주 {len(donep)}종 < {PAIRS}종')
    if pairs:
        extra = sum(t1(q_) for q_ in pairs) / W1
        print(f'  겹치는 짝 **{len(pairs)}종** 추가 (N_super {pairs[0]["N_super"]}~{pairs[-1]["N_super"]}) '
              f'· 랩탑에 +{extra:.2f} h · 기기 항 검정용')
    tail = tail + pairs

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
