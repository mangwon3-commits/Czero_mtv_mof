#!/usr/bin/env python
"""RH90 유지율 재계산 — **수정 힘장 계열 v3w** (`WATER_FIX_20260906.md` §2·§4 등록분).

`run_water.py` 를 감싸 **경로를 전부 새로** 잡습니다. 러너의 이어받기는 출력 파일의
존재만 보고 **어느 힘장으로 만들어졌는지 안 봅니다**(CLAUDE.md §3). 그래서
`HERE` 와 `RUNS` 를 **둘 다** 새 경로로 두어 결함판을 물려받을 길 자체를 없앱니다.

    HERE      v3w_water/           (water_results.json + water_results_<기기>.json)
    RUNS      water_runs_v3w/
    CHARGED   charged_v3/
    RH_LIST   [0.90]               RH0 행은 물 분자 0이라 결함과 무관 — 옛 값을 분모로 씁니다
    TARGETS   랩탑 몫 11종 (§4)

**힘장 관문이 둘 있습니다. 하나라도 걸리면 산출물을 쓰지 마십시오.**

    착수 전   실물 힘장 md5 == FF_MD5            아니면 **즉시 중단**
    완주 후   출력 머리말 `Hw - Hw [ZERO_POTENTIAL]` · `Ow - Ow 89.633/3.097`
              아니면 그 행을 `ff_check.ok = false` 로 찍고 **K 값을 쓰지 말라고 적습니다**

사용:
    python run_water_v3w.py                 등록된 11종 전부
    python run_water_v3w.py --only saIm050  검증용 1건 (§4 가 시키는 첫 건)
"""
import hashlib, json, os, re, socket, sys

import run_water as rw

HERE = os.path.dirname(os.path.abspath(__file__))
def _ff_path():
    """힘장 실물 경로. **기기마다 다릅니다.**

    ⚠️ 초판은 `~/RASPA/simulations/...` 로 박혀 있었습니다. 이 러너를 다른 기기가
    import 하면(데스크탑 `run_tb2w.py`) **그 기기의 RASPA 가 다른 곳에 있을 때
    md5 관문이 파일을 못 찾아 `return 4` 로 착수를 막습니다.** 자동 착수 체인에서는
    아무도 안 보고 있는 사이에 그렇게 됩니다.
    RASPA 자신이 쓰는 `$RASPA_DIR` 를 먼저 봅니다.
    """
    cands = []
    if os.environ.get('RASPA_DIR'):
        cands.append(os.path.join(os.environ['RASPA_DIR'], 'share', 'raspa',
                                  'forcefield', 'UFF_MOF',
                                  'force_field_mixing_rules.def'))
    cands.append(os.path.expanduser(
        '~/RASPA/simulations/share/raspa/forcefield/UFF_MOF/'
        'force_field_mixing_rules.def'))
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


FF_PATH = _ff_path()
FF_MD5 = '8e8ec933f9013c7e932da04dc256efd3'      # WATER_FIX_20260906.md §1 ①
FF_TAG = 'UFF_MOF+HwLw_none_20260906'

# --- 경로 재지정 (module 전역이라 함수 안에서 이 값을 읽습니다) --------------
rw.HERE = os.path.join(HERE, 'v3w_water')
rw.RUNS = os.path.join(HERE, 'water_runs_v3w')
rw.CHARGED = os.path.join(HERE, 'charged_v3')
rw.WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
rw.RH_LIST = [0.90]
rw.MAX_WORKERS = 8
rw.TARGETS = [
    ('saIm025',     'SO3H 25%'),
    ('saIm050',     'SO3H 50%'),
    ('saIm0583',    'SO3H 58.3%'),
    ('saIm0583e1',  'SO3H 58.3% 실현 1'),
    ('saIm0583e2',  'SO3H 58.3% 실현 2'),
    ('saIm0583e3',  'SO3H 58.3% 실현 3'),
    ('saIm0583e4',  'SO3H 58.3% 실현 4'),
    ('saIm0583e5',  'SO3H 58.3% 실현 5'),
    ('saIm0625',    'SO3H 62.5%'),
    ('saIm0667',    'SO3H 66.7%'),
    ('saIm075',     'SO3H 75% — 관문 미해결(STAGE2 판정문). 관찰용'),
]


def ff_gate():
    """착수 전 관문 — 실물 힘장이 등록된 판인지."""
    if not os.path.exists(FF_PATH):
        print(f'!! 힘장 파일 없음: {FF_PATH}'); return None
    m = hashlib.md5(open(FF_PATH, 'rb').read()).hexdigest()
    print(f'  힘장 {FF_PATH}\n       md5 {m}  ({"**일치**" if m == FF_MD5 else "**불일치 — 중단**"})')
    return m if m == FF_MD5 else None


def read_ff_header(rundir):
    """완주 후 관문 — 출력 머리말에서 실제로 쓰인 쌍을 읽습니다.

    ⚠️ 러너 설정이 아니라 **RASPA 가 인쇄한 것**을 봅니다. 09-05 에 지역 힘장이
    안 먹은 채로 완주한 사례가 있었고(`widom_control_hwnone_hkhome.json` 의 note),
    설정만 보면 그것을 못 잡습니다.
    """
    # ⚠️ RASPA 는 쌍 이름을 **오른쪽 정렬로 채웁니다** — 실제 줄은
    #     `     Hw -      Hw [ZERO_POTENTIAL]`
    # 이라 `'Hw - Hw' in ln` 은 **절대 안 맞습니다**(09-06 실측). 정규식으로 봅니다.
    #
    # ⚠️ 그리고 `22.14170` 을 grep 하는 방식은 **쓰면 안 됩니다.** 고친 판의
    #    출력에도 그 수가 **12,246번** 나옵니다 — 골격 수소 `H_` 의 정당한 UFF
    #    값이기 때문입니다. 결함은 그 수의 존재가 아니라 **`Hw` 쌍이 그 값을
    #    갖는 것**이었습니다. 반드시 **쌍 이름으로** 보십시오.
    RX = {'HwHw': re.compile(r'^\s*Hw\s+-\s+Hw\s'),
          'OwHw': re.compile(r'^\s*Ow\s+-\s+Hw\s'),
          'OwLw': re.compile(r'^\s*Ow\s+-\s+Lw\s'),
          'LwLw': re.compile(r'^\s*Lw\s+-\s+Lw\s'),
          'OwOw': re.compile(r'^\s*Ow\s+-\s+Ow\s')}
    out = {}
    for root, _, files in os.walk(rundir):
        for fn in sorted(files):
            if not fn.endswith('.data'):
                continue
            with open(os.path.join(root, fn), encoding='utf-8', errors='ignore') as f:
                for ln in f:
                    for k, rx in RX.items():
                        if k not in out and rx.match(ln):
                            if k == 'OwOw':
                                g = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ln)
                                out['OwOw'] = ln.strip()[:100]
                                out['OwOw_eps'] = float(g[1]) if len(g) > 1 else None
                            else:
                                out[k] = ('ZERO_POTENTIAL' if 'ZERO_POTENTIAL' in ln
                                          else ln.strip()[:100])
                    if len(set(RX) & set(out)) == len(RX):
                        return out
            if len(set(RX) & set(out)) == len(RX):
                return out
    return out


def main():
    if '--stamp-only' in sys.argv:
        # 도는 프로세스는 import 시점의 함수를 쥐고 있어 이 파일을 고쳐도 안 바뀝니다
        # (CLAUDE.md §6). 그 실행이 남긴 잘못된 ff_check 를 **다시 찍기** 위한 길입니다.
        return stamp()
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1:]
        rw.TARGETS = [t for t in rw.TARGETS if t[0] in only]
        missing = [n for n in only if n not in [t[0] for t in rw.TARGETS]]
        if missing:
            print(f'!! 등록 목록에 없는 이름: {missing}  (§4 목록만 돕니다)'); return 2

    print('RH90 유지율 재계산 — **v3w 계열** (수정 힘장)', flush=True)
    print(f'  HERE {rw.HERE}\n  RUNS {rw.RUNS}\n  CHARGED {rw.CHARGED}', flush=True)
    print(f'  RH {rw.RH_LIST} · 워커 {rw.MAX_WORKERS} · 대상 {len(rw.TARGETS)}종'
          f'{"  [--only]" if only else ""}: ' + ', '.join(n for n, _ in rw.TARGETS), flush=True)
    if ff_gate() is None:
        return 1
    for d in (rw.HERE, rw.RUNS):
        os.makedirs(d, exist_ok=True)

    rc = rw.main()
    return 0 if (stamp() == 0 and rc == 0) else 1


def stamp():
    """산출물에 힘장 출처를 **행마다** 남깁니다.

    등록문은 "JSON 최상단" 이라 했으나 `water_results.json` 은 **맨 리스트**이고
    이 형식을 그대로 순회하는 판독기가 열 곳 넘습니다(check_retention.py ·
    repro_verdict.py · merge_water_batches.py · scope_report.py …).
    **그래서 행마다 찍고 사이드카를 따로 둡니다** — 형식을 안 깨고, 행이 다른
    파일로 복사돼도 힘장 표기가 **따라갑니다.** 어젯밤 밀도 격자에서 곁의 설정
    파일이 자료와 떨어진 그 문제를, 곁에 두지 않는 쪽으로 막습니다.
    """
    chk = read_ff_header(rw.RUNS)
    ok = (all(chk.get(k) == 'ZERO_POTENTIAL' for k in ('HwHw', 'OwHw', 'OwLw', 'LwLw'))
          and chk.get('OwOw_eps') is not None and abs(chk['OwOw_eps'] - 89.633) < 1e-3)
    chk['ok'] = ok
    print(f'\n  [힘장 확인 — 출력 머리말] {json.dumps(chk, ensure_ascii=False)}')
    print(f'  -> {"**통과.** Hw-Hw 가 ZERO_POTENTIAL, Ow-Ow 89.633" if ok else "**실패 — 이 산출물의 K 값을 쓰지 마십시오**"}')

    p = os.path.join(rw.HERE, 'water_results.json')
    if os.path.exists(p):
        rows = json.load(open(p, encoding='utf-8'))
        for r in rows:
            r['forcefield'] = FF_TAG
            r['ff_check'] = chk
        json.dump(rows, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        json.dump({'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'ff_path': FF_PATH,
                   'ff_check': chk, 'series': 'v3w', 'host': socket.gethostname().lower(),
                   'RH_LIST': rw.RH_LIST, 'targets': [n for n, _ in rw.TARGETS],
                   'note': '수정 힘장(Hw none/Lw none) 계열. v3 결함판과 섞지 말 것.'},
                  open(os.path.join(rw.HERE, 'water_results_meta.json'), 'w',
                       encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'  {len(rows)}행에 forcefield·ff_check 를 찍고 사이드카를 남겼습니다.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
