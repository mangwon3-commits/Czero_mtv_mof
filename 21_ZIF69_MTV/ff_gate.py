"""힘장 관문 **한 자리** — 상수와 두 관문 함수 (2026-09-07 신설).

정의와 경계는 `FF_GATES_20260907.md` 에 있습니다. 요약:

    파일 관문    착수 **전**      공용 힘장 md5              **파일이 맞는가**
    머리말 관문  착수 **직후**~   출력 .data 머리말의 쌍 표  **RASPA 가 그걸 읽었나**

**왜 모듈로 뺐는가 — 상수가 갈라지면 한 곳만 고치는 사고가 납니다.**
`FF_MD5` 가 `run_water_v3w.py` 와 `run_tb2_water_kh.py` 두 곳에 각각 적혀 있었고,
사슬·밀도 러너에 관문을 더하면 셋·넷이 됩니다. 힘장을 또 고칠 때(09-06 에 실제로
고쳤습니다) 한 곳을 빠뜨리면 **그 러너만 조용히 옛 기준으로 통과시킵니다.**
랩탑 제안(09-07)이고, "같은 이름 두 세대" 와 같은 형태입니다.

**이 모듈은 프로젝트 안의 무엇도 import 하지 않습니다.** 그래야 어디서 불러도
안전합니다 — `run_water_v3w` 와 `run_density_water_v3` 는 **둘 다** `run_water` 의
모듈 전역(`rw.HERE`·`rw.RUNS`)을 자기 계열로 덮어써서, 예전에는 그 둘 중 하나를
import 하는 것만으로 **다른 계열의 산출물이 엉뚱한 폴더로 샜습니다**(09-07 실측,
랩탑이 `053a806` 으로 `run_water_v3w` 쪽 배선을 `wire()` 로 빼내 고쳤습니다).
그 사고를 되풀이하지 않으려면 **관문 모듈은 계속 stdlib 만** 써야 합니다.
"""
import hashlib
import os
import re

FF_MD5 = '8e8ec933f9013c7e932da04dc256efd3'      # WATER_FIX_20260906.md §1 ①
FF_TAG = 'UFF_MOF+HwLw_none_20260906'
OWOW_EPS = 89.633                                 # TIP5P-Ew Ow-Ow (WATER_FIX §1)
ZERO_PAIRS = ('HwHw', 'OwHw', 'OwLw', 'LwLw')     # 이 넷은 ZERO_POTENTIAL 이어야 합니다


def ff_path():
    """공용 힘장 파일 자리. `RASPA_DIR` 이 있으면 그것을 먼저 봅니다."""
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


def md5_gate(path=None, verbose=True):
    """**파일 관문** — 공용 힘장 파일이 그 파일인가. 착수 **전**에 답합니다.

    돌려주는 것: (ok, md5 또는 None). 머리말 관문을 대신하지 못합니다 —
    09-05 에 **파일은 맞는데 RASPA 가 지역 힘장을 읽어** 결함판으로 완주한
    사례가 있습니다(`FF_GATES_20260907.md` §1).
    """
    p = path or ff_path()
    if not os.path.exists(p):
        if verbose:
            print(f'  [파일 관문] **못 찾음** {p}')
        return False, None
    m = hashlib.md5(open(p, 'rb').read()).hexdigest()
    ok = (m == FF_MD5)
    if verbose:
        print(f'  [파일 관문] {p}\n              md5 {m}  '
              f'({"**일치**" if ok else f"**불일치 — 기대 {FF_MD5}**"})')
    return ok, m


def read_ff_header(path):
    """**머리말 관문** — RASPA 가 **인쇄한** 쌍을 읽습니다. `path` 는 파일이거나 폴더.

    ⚠️ 러너 설정이 아니라 RASPA 의 출력을 봅니다. 09-05 에 지역 힘장이 안 먹은 채
    완주한 사례가 있었고, 설정만 보면 그것을 못 잡습니다.

    ⚠️ 쌍 이름은 **오른쪽 정렬로 채워집니다** — 실제 줄은
        `     Hw -      Hw [ZERO_POTENTIAL]`
    이라 `'Hw - Hw' in ln` 은 **절대 안 맞습니다**(09-06 실측). 정규식으로 봅니다.

    ⚠️ **`22.14170` 을 grep 하지 마십시오.** 고친 판의 출력에도 그 수가 12,246번
    나옵니다 — 골격 수소 `H_` 의 정당한 UFF 값입니다. 결함은 그 수의 존재가 아니라
    **`Hw` 쌍이 그 값을 갖는 것**이었습니다.

    ⚠️ **폴더를 주면 그 아래 첫 `.data` 로 답합니다.** 여러 조성이 섞인 뿌리를 주면
    **한 실행이 다른 실행을 대신 통과시킵니다**(09-07 `5c30af6`). **조성별로** 부르십시오.
    """
    RX = {a + b: re.compile(r'^\s*' + a + r'\s+-\s+' + b + r'\s')
          for a, b in (('Hw', 'Hw'), ('Ow', 'Hw'), ('Ow', 'Lw'),
                       ('Lw', 'Lw'), ('Ow', 'Ow'))}
    out = {}

    def scan(fp):
        with open(fp, encoding='utf-8', errors='ignore') as f:
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
                    return True
        return False

    if os.path.isdir(path):
        done = False
        for root, _, files in os.walk(path):
            for fn in sorted(files):
                if fn.endswith('.data') and scan(os.path.join(root, fn)):
                    done = True
                    break
            if done:
                break
    elif os.path.exists(path):
        scan(path)

    out['ok'] = (all(out.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
                 and out.get('OwOw_eps') is not None
                 and abs(out['OwOw_eps'] - OWOW_EPS) < 1e-3)
    return out
