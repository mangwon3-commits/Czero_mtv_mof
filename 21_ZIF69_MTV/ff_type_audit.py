"""힘장 유사원자 형 감사 — **앞자리 일치로 조용히 물려받는 형**을 찾습니다.

[왜] 2026-09-05 에 `UFF_MOF/force_field_mixing_rules.def` 에 `Hw`(물 수소) 항이
     없어서, RASPA 의 **앞자리 일치**로 `H_`(UFF 수소, ε 22.1417 K, σ 2.57113 Å)를
     물려받았습니다. **TIP5P 수소는 LJ 가 없어야 합니다.** 그 결과 `Ow-Hw` 반발이
     생겨 수소결합이 억제됐고(이합체 우물 -22.9 -> -10.0 kJ/mol, 최소 2.70 -> 3.60 Å),
     이 저장소의 **모든 물 계산**이 그 물로 돌았습니다.

     `Lw` 가 멀쩡한 것은 **운**입니다 — `L` 로 시작하는 형이 없어 매칭이 안 됐을 뿐.
     `Hw` 는 하필 `H_` 와 앞자리가 겹쳤습니다.

[머리말 계수로는 안 잡힙니다] `# number of defined interactions` 는 55 = 55 로
     맞습니다(배포본도 36 = 36). **개수가 아니라 이름을 봐야 합니다.**

[검사]
     정확 일치 있음        OK
     앞자리 일치만 있음    **WARN** — 다른 형의 값을 조용히 물려받습니다
     아무 일치 없음        INFO — RASPA 가 무상호작용으로 둡니다(의도면 정상)

     앞자리 비교는 형 이름의 **끝 `_` 를 떼고** 합니다 — `H_` -> `H` 라야
     `Hw` 가 걸립니다. 처음에 `startswith("H_")` 로 짰다가 **알려진 결함을
     0건으로 통과**시켰습니다(09-05). 여러 형이 걸리면 **뒤에 정의된 것**이
     이깁니다(파일 7행이 그렇게 적어 둡니다).

[자체 검증] `--selftest` 로 **RASPA 가 실제로 쓴 값**과 대조합니다. 완주한
     출력의 머리말에서 `Hw - Hw` 를 읽어 이 감사기의 예측과 맞는지 봅니다.
     **감사기를 알려진 결함으로 먼저 시험하지 않으면 그 감사기를 믿을 수 없습니다.**

사용:  python3 ff_type_audit.py [힘장이름 ...]      (기본 UFF_MOF)
"""
import os, re, sys, glob

SHARE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '..', '00_Migration', 'raspa_share', 'raspa')
FFDIR = os.path.join(SHARE, 'forcefield')
MOLDIR = os.path.join(SHARE, 'molecules')
LOCAL_DEFS = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '19_WaterCompetition', 'water.def')]


def mixing_types(ff):
    """혼합규칙에 정의된 형 이름. 머리말·꼬리말 제외."""
    p = os.path.join(FFDIR, ff, 'force_field_mixing_rules.def')
    out = []
    for i, ln in enumerate(open(p, encoding='utf-8', errors='ignore'), 1):
        s = ln.strip()
        if not s or s.startswith('#') or i <= 7:
            continue
        f = s.split()
        if len(f) >= 2 and re.fullmatch(r'[A-Za-z][A-Za-z0-9_\-+]*', f[0]) \
                and f[1].lower() in ('lennard-jones', 'lennard_jones', 'none'):
            out.append((f[0], i, f[1].lower()))
    return out


def def_atoms(path):
    """분자 정의 파일의 유사원자 이름 (원자 위치 절에서)."""
    names, seen = [], False
    for ln in open(path, encoding='utf-8', errors='ignore'):
        if 'atomic positions' in ln.lower():
            seen = True
            continue
        if seen:
            f = ln.split()
            if len(f) >= 5 and f[0].isdigit():
                names.append(f[1])
            elif f and f[0].startswith('#'):
                break
    return names


def audit(ff, used):
    types = mixing_types(ff)
    exact = {t[0] for t in types}
    print(f'\n=== {ff} — 정의된 형 {len(types)}개 ===')
    warn = 0
    for name, src in sorted(set(used)):
        if name in exact:
            print(f'  OK    {name:<8} 정확 일치                        ({src})')
            continue
        pre = [t for t in types if name.startswith(t[0].rstrip('_'))]
        if pre:
            # RASPA 는 뒤에 정의된 것이 덮으므로 마지막 일치가 이깁니다
            t = max(pre, key=lambda x: x[1])
            print(f'  WARN  {name:<8} **{t[0]}** 를 앞자리로 물려받음 '
                  f'({os.path.basename(ff)}:{t[1]}, {t[2]})   ({src})')
            warn += 1
        else:
            print(f'  INFO  {name:<8} 일치 없음 -> 무상호작용            ({src})')
    return warn


def selftest(ff, out_data):
    """RASPA 가 실제로 쓴 Hw-Hw 값과 이 감사기의 예측을 대조."""
    got = None
    for ln in open(out_data, encoding='utf-8', errors='ignore'):
        m = re.search(r'Hw\s*-\s*Hw\s*\[LENNARD_JONES\]\s*p_0/k_B:\s*'
                      r'([0-9.]+).*?p_1:\s*([0-9.]+)', ln)
        if m:
            got = (float(m.group(1)), float(m.group(2)))
            break
    types = mixing_types(ff)
    pre = [t for t in types if 'Hw'.startswith(t[0].rstrip('_'))]
    exact = [t for t in types if t[0] == 'Hw']
    src = exact[-1] if exact else (max(pre, key=lambda x: x[1]) if pre else None)
    pred = None
    if src:
        for i, ln in enumerate(open(os.path.join(FFDIR, ff,
                               'force_field_mixing_rules.def'),
                               encoding='utf-8', errors='ignore'), 1):
            if i == src[1]:
                f = ln.split()
                pred = (float(f[2]), float(f[3])) if len(f) >= 4 else 'none'
    print(f'[자체검증] 감사기 예측: {src[0] if src else "없음"} -> {pred}')
    print(f'[자체검증] RASPA 실제 : Hw-Hw -> {got}')
    ok = (pred == 'none' and got is None) or (
        got and pred != 'none' and abs(pred[0] - got[0]) < 1e-3
        and abs(pred[1] - got[1]) < 1e-4)
    print('[자체검증] ' + ('**일치 — 감사기를 믿을 수 있습니다**' if ok
                           else '**불일치 — 감사기가 틀렸습니다. 고치기 전에 쓰지 마십시오**'))
    return 0 if ok else 1


def main():
    if sys.argv[1:2] == ['--selftest']:
        return selftest(sys.argv[2], sys.argv[3])
    ffs = sys.argv[1:] or ['UFF_MOF']
    used = []
    for p in LOCAL_DEFS + [os.path.join(MOLDIR, 'TraPPE', n)
                           for n in ('CO2.def', 'N2.def', 'water.def')]:
        if os.path.isfile(p):
            for a in def_atoms(p):
                used.append((a, os.path.relpath(p, SHARE) if SHARE in p
                             else os.path.basename(p)))
    if not used:
        print('분자 정의를 못 찾았습니다.'); return 1
    total = sum(audit(ff, used) for ff in ffs)
    print(f'\n경고 {total}건. **WARN 은 다른 형의 값을 조용히 쓰고 있다는 뜻입니다.**')
    return 0


if __name__ == '__main__':
    sys.exit(main())
