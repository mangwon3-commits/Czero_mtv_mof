# -*- coding: utf-8 -*-
"""§AS (가) Q_st(n) **§-보완** 러너 — 저피복 점(0.01 · 0.02 bar) 36+6작업.

등록 `QSTN_SUPP_REGISTRATION_20260924.md`(자료 0건 09-24 14:2x). 식·고정값은 §AS 와 같고
**압력 두 점만 더합니다.** 한 조성의 여섯 점은 **한 기기**에서 나와야 합니다(§1-1) —
`Q_st` 가 세 온도의 기울기이므로 온도를 기기에 걸쳐 나누면 기기 항이 기울기에 들어갑니다.

    python run_qn_supp.py --only base,saIm025,saIm050            # Junseok
    python run_qn_supp.py --only mslm050,sa50nb50,saIm0583,base  # laptop2 (base 는 §1-2 교차)

이어받기: 결과 JSON 이 있고 **그 안의 `CO2_molkg` 가 null 이 아닐 때만** `cached`.
**파일 존재만으로 건너뛰지 않습니다** — 09-21 `RESUME_ANY_BUG` 와 같은 무늬를 막습니다.
(`run_tnf.py` 자체가 `finished()` 로 'Simulation finished' 를 요구하므로, 표지가 없으면
그 행의 `CO2_molkg` 가 null 로 남습니다.)
"""
import argparse, fcntl, glob, json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 선행 검사 — `run_tnf.py` 를 **이 파이썬으로** 띄우므로 여기서 numpy 가 되면 자식도 됩니다.
# (09-24 데스크탑 예행에서 conda 밖 python3 로 띄워 42작업이 전부 rc=1 로 탈 뻔했습니다.
#  빨리·크게 죽는 것이 조용히 다 실패하는 것보다 낫습니다.)
try:
    import numpy  # noqa: F401
except ImportError:
    sys.exit('numpy 가 없습니다 — `run_tnf.py` 가 이 파이썬(%s)으로 뜹니다.\n'
             'conda 환경(czeromof 류)의 python 으로 다시 띄우십시오.' % sys.executable)

HERE = os.path.dirname(os.path.abspath(__file__))
FF_MD5 = '8e8ec933f9013c7e932da04dc256efd3'          # 등록 §1 — 기존 72건과 같은 값
TEMPS = [283.0, 298.0, 313.0]
PRESS = [0.01, 0.02]                                  # ← §-보완이 더하는 두 점
#   §-보완2(2026-09-24, `QSTN_SUPP2_REGISTRATION_20260924.md`)는 `--press 0.005` 로 덮습니다.
#   ⚠ 압력이 태그에 들어가지만 **서식이 `%.2f` 면 0.005 가 0.01 로 반올림**됩니다 —
#   `_ptag()` 가 그것을 막습니다. 등록문의 '저절로 갈립니다' 는 **그 함수가 있어야** 참입니다.
ALL = ['base', 'mslm050', 'sa50nb50', 'saIm025', 'saIm050', 'saIm0583']
# ② 2026-09-24 Caspar 발견 — `base` 를 두 기기가 내면 **결과 파일 이름이 같습니다**
#    (`tnf_results_qn_base_*.json`). `RESULT_PATTERNS` 안이고 `NOAUTO_IMPORT` 밖이라
#    07:38~08:25 능력 문서와 **같은 핑퐁**이 납니다(checkout 반입은 조상을 안 만듦).
#    등록 §1-2 의 "정본 = Junseok 판" 을 **파일 이름으로 지킬 수 없습니다.**
#    → 교차 검산 쪽만 `--tag-suffix _l2` 로 갈라 냅니다. 정본은 등록 이름 그대로.
SUFFIX = ['']


# ── 착수 간격 잠금 (2026-09-24 14:3x — **Caspar(Junseok) 발견**) ────────────────
# `run_tnf.py:312` 이 자기 주석에 적어 둔 그대로입니다:
#     "씨앗 = 착수 시각(초). 같은 초에 두 개가 뜨면 **같은 난수열**입니다."
#     time.sleep((i % max(1, cfg['workers'])) * cfg['stagger'])
# 그 보호는 **한 호출 안 여러 작업**을 전제합니다. 이 러너는 작업마다 `run_tnf.py` 를
# 따로(작업 1개, i=0) 부르므로 `sleep 0` — **워커 N 개가 같은 초에 뜹니다.**
# §AS 72건은 사슬이 하나씩 띄워 씨앗 72개가 전부 다르고 **최소 간격 12 s** 였습니다(검산 일치).
# 그래서 같은 12 s 를 여기서 직접 겁니다. 작업이 한 시간대이므로 12워커 기동 지연 144 s 는 무시할 만합니다.
#
# ⚠ 2차 수정 (14:4x — **laptop2 발견**): 첫 판은 `threading.Lock` 이라 **한 프로세스 안에서만**
#   걸렸습니다. 한 기기에서 러너를 둘 띄우면(laptop2 가 실제로 A·B 로 나눠 띄웠습니다)
#   **서로의 착수가 같은 초에 겹칩니다.** 잠금을 **파일 잠금(flock)** 으로 올려 기기 전체에 겁니다.
#   잠금 파일은 **저장소 밖**입니다(§9 의 사슬·postman 과 같은 수).
MIN_GAP = float(os.environ.get('QN_SUPP_MIN_GAP', '12'))
LOCKF = os.environ.get('QN_SUPP_LOCK',
                       os.path.join(os.path.expanduser('~'), '.mof_qn_supp_launch.lock'))
_GATE = threading.Lock()


def wait_turn():
    with _GATE:                                   # ① 프로세스 안 (파일 경합을 줄입니다)
        with open(LOCKF, 'a+') as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)        # ② 프로세스 사이 — 기기 전체
            try:
                fh.seek(0)
                try:
                    last = float((fh.read() or '').strip() or 0)
                except ValueError:
                    last = 0.0
                w = last + MIN_GAP - time.time()
                if w > 0:
                    time.sleep(w)                 # 잠금을 **든 채로** 잡니다 — 그래야 직렬화됩니다
                fh.seek(0); fh.truncate()
                fh.write('%.3f' % time.time()); fh.flush()
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)


def audit_seeds(verbose=True):
    """**기기 전체** 씨앗 감사 — 실행 폴더를 직접 읽습니다.

    러너의 끝 감사는 **자기 프로세스가 맡은 작업**만 셉니다(laptop2 지적). 러너를 둘 띄웠거나
    남이 띄운 것이 섞였으면 못 봅니다. 이것은 `tnf_runs_qn_*` **전부**를 훑습니다.
    """
    seeds = {}
    pat = os.path.join(HERE, 'tnf_runs_qn_*', '*', 'Output', 'System_0', '*.data')
    for f in glob.glob(pat):
        try:
            with open(f, encoding='utf-8', errors='ignore') as fh:
                for ln in fh:
                    m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
                    if m:
                        seeds.setdefault(int(m.group(1)), []).append(
                            f.split(os.sep)[-5])
                        break
                    if ln.startswith('Number of cycles'):
                        break
        except OSError:
            continue
    dup = {k: sorted(set(v)) for k, v in seeds.items() if len(set(v)) > 1}
    if verbose:
        print('기기 전수 씨앗 감사 — 실행 폴더 %d · 서로 다른 씨앗 %d · **겹침 %d건**'
              % (sum(len(v) for v in seeds.values()), len(seeds), len(dup)), flush=True)
        for k, v in sorted(dup.items()):
            print('  !! 씨앗 %d 를 %d 작업이 공유: %s' % (k, len(v), ' '.join(v)), flush=True)
        if dup:
            print('  → 겹친 작업은 **같은 난수열**입니다. 실행 폴더를 저장소 밖으로 격리하고 다시 도십시오.',
                  flush=True)
    return dup


def _ptag(p):
    """압력을 태그 문자열로. **기존 태그를 한 글자도 안 바꾸면서** 0.005 를 가릅니다.

    ⚠ 2026-09-24 19:4x — `%.2f` 하나로는 **0.005 가 `0.01bar` 로 반올림**됩니다.
      §-보완2(0.005 bar)를 그대로 띄웠으면 §-보완의 **0.01 bar 결과 6개를 덮어썼습니다.**
      등록문에 *"압력은 태그에 들어가므로 저절로 갈립니다"* 라고 **제가 써 놓고**,
      바로 그 줄을 시험해서 잡았습니다 — **쓴 것을 시험한 덕**입니다.
      고친 방법: `%.2f` 가 값을 **되돌려 주면** 그대로 쓰고(0.01·0.02·0.05·0.15·0.50·1.00 전부 유지),
      안 되돌려 주면 `%g` 로 갑니다(0.005 → `0.005bar`).
    """
    t = '%.2f' % p
    return t if float(t) == float(p) else ('%g' % p)


def tag_of(c, T, p):
    return 'qn_%s%s_%dK_%sbar' % (c, SUFFIX[0], int(T), _ptag(p))


def out_of(c, T, p):
    return os.path.join(HERE, 'tnf_results_%s.json' % tag_of(c, T, p))


def done(path):
    """완주 판정 — **값이 아니라 표지가 자입니다**(CLAUDE.md §0)."""
    try:
        rows = json.load(open(path, encoding='utf-8'))
    except Exception:
        return False
    if not isinstance(rows, list) or not rows:
        return False
    return all(r.get('CO2_molkg') is not None for r in rows)


def run_one(job):
    c, T, p = job
    out = out_of(c, T, p)
    if done(out):
        return c, T, p, 'cached', 0.0
    cif = os.path.join(HERE, 'charged_v3', '%s_DDEC6.cif' % c)
    if not os.path.exists(cif):
        return c, T, p, 'CIF 없음', 0.0
    wait_turn()                                        # ← 착수 간격 잠금
    t0 = time.time()
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, 'run_tnf.py'),
         '--cif', cif, '--tag', tag_of(c, T, p),
         '--temp', str(T), '--pco2', str(p), '--rh', '0', '--workers', '1'],
        cwd=HERE, capture_output=True, text=True)
    dt = (time.time() - t0) / 60.0
    if not done(out):                                  # rc 를 믿지 않습니다 — 출력을 봅니다
        tail = (r.stderr or r.stdout or '')[-300:].replace('\n', ' ')
        return c, T, p, '미완주 rc=%d %s' % (r.returncode, tail), dt
    return c, T, p, 'ok', dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=','.join(ALL), help='조성 쉼표 구분')
    ap.add_argument('--workers', type=int,
                    default=int(os.environ.get('QN_SUPP_WORKERS', '6')))
    ap.add_argument('--tag-suffix', default='',
                    help='결과 이름을 가릅니다(교차 검산 쪽만, 예: _l2). 정본은 빈 값.')
    ap.add_argument('--press', default=None,
                    help='압력 목록(쉼표, bar). 기본 0.01,0.02. §-보완2 는 0.005')
    ap.add_argument('--audit-seeds', action='store_true',
                    help='계산 없이 **기기 전수** 씨앗 감사만 하고 끝냅니다(러너 여럿이어도 봅니다).')
    a = ap.parse_args()
    if a.press:
        try:
            ps = [float(x) for x in a.press.split(',') if x.strip()]
        except ValueError:
            sys.exit('--press 를 못 읽었습니다: %r' % a.press)
        if not ps:
            sys.exit('--press 가 비었습니다')
        PRESS[:] = ps                                  # 태그가 압력을 담으므로 파일이 갈립니다
    if a.audit_seeds:
        sys.exit(1 if audit_seeds() else 0)
    SUFFIX[0] = a.tag_suffix
    comps = [c.strip() for c in a.only.split(',') if c.strip()]
    bad = [c for c in comps if c not in ALL]
    if bad:
        sys.exit('등록 밖 조성: %s (등록 §1 은 %s)' % (bad, ALL))

    # ⚠ `RASPA_DIR` 은 **`share/raspa` 의 부모**입니다(예: `$HOME/RASPA/simulations`).
    #   09-24 데스크탑이 한 단계 깊게 줘서 172구조가 3분 만에 전부 `[no-output]` 이 났고,
    #   laptop2 는 변수 자체가 비어 여기서 막혔습니다. **막되 고치는 법을 알려 줍니다.**
    rd = os.environ.get('RASPA_DIR', '')
    ffp = os.path.join(rd, 'share', 'raspa',
                       'forcefield', 'UFF_MOF', 'force_field_mixing_rules.def')
    import hashlib
    if not os.path.exists(ffp):
        hint = ''
        for c in (os.path.join(os.path.expanduser('~'), 'RASPA', 'simulations'),
                  os.path.join(os.path.expanduser('~'), 'RASPA')):
            if os.path.exists(os.path.join(c, 'share', 'raspa', 'forcefield',
                                           'UFF_MOF', 'force_field_mixing_rules.def')):
                hint = '\n이 기기에서 맞는 값은 이것으로 보입니다:  export RASPA_DIR=%s' % c
                break
        sys.exit('힘장 파일 없음: %s\n'
                 'RASPA_DIR=%r — **`share/raspa` 의 부모**를 주십시오(한 단계 깊게 주면 안 됩니다).%s'
                 % (ffp, rd, hint))
    m = hashlib.md5(open(ffp, 'rb').read()).hexdigest()
    if m != FF_MD5:
        sys.exit('힘장 관문 실패: %s != %s (등록 §1)' % (m, FF_MD5))
    print('힘장 관문 통과  %s  (RASPA_DIR=%s)' % (m, rd), flush=True)

    jobs = [(c, T, p) for c in comps for T in TEMPS for p in PRESS]
    print('§-보완  조성 %d · 온도 %d · 압력 %s → %d작업 · 워커 %d'
          % (len(comps), len(TEMPS), PRESS, len(jobs), a.workers), flush=True)
    n_ok = n_cache = n_bad = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}     # submit+as_completed (§5)
        for i, f in enumerate(as_completed(futs), 1):
            c, T, p, st, dt = f.result()
            if st == 'ok':
                n_ok += 1
            elif st == 'cached':
                n_cache += 1
            else:
                n_bad += 1
            print('[%2d/%d] %-10s %3dK %6sbar  %-10s %5.1f min'
                  % (i, len(jobs), c, int(T), _ptag(p), st, dt), flush=True)
    # ── 씨앗 감사 — **막은 것과 안 겹친 것은 다릅니다.** 끝나고 실제로 셉니다.
    seeds = {}
    for c, T, p in jobs:
        try:
            for r in json.load(open(out_of(c, T, p), encoding='utf-8')):
                if r.get('seed') is not None:
                    seeds.setdefault(r['seed'], []).append(tag_of(c, T, p))
        except Exception:
            pass
    dup = {k: v for k, v in seeds.items() if len(v) > 1}
    print('\n완주 %d · cached %d · 실패 %d' % (n_ok, n_cache, n_bad), flush=True)
    print('이 프로세스 씨앗 %d개 · 서로 다른 것 %d개 · 겹침 %d건'
          % (sum(len(v) for v in seeds.values()), len(seeds), len(dup)), flush=True)
    for k, v in dup.items():
        print('  !! 씨앗 %d 를 %d 작업이 공유: %s' % (k, len(v), ' '.join(v)), flush=True)
    dup2 = audit_seeds()          # ← 기기 전수 (러너 둘이어도 봅니다 — laptop2 지적)
    sys.exit(1 if (n_bad or dup or dup2) else 0)


if __name__ == '__main__':
    main()
