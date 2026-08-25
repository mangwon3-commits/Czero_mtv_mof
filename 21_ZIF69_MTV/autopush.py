#!/usr/bin/env python3
"""러너 완주를 감시해 결과 JSON 만 자기 가지로 커밋·푸시한다.

[왜 필요한가]
    2026-08-24 23:07 에 앙상블 10작업이 끝났는데 저장소에는 08-25 10:52 까지
    아무것도 도착하지 않았다. 계산이 죽은 것도 세션이 끊긴 것도 아니고,
    **세션이 스스로 깨어나지 않기 때문**이다. 사람이 부르지 않으면 완주를
    알릴 주체가 없다. 11시간 동안 다른 두 기기는 이 기기가 살아 있는지조차
    확인할 수 없었다.

    COMMS.md 의 우편함은 이 구멍을 못 막는다. 우편함도 사람이 써야 한다.

[무엇을 하지 않는가 — 이쪽이 더 중요하다]
    사람 없이 공유 저장소에 쓰는 물건이라, 할 수 있는 일을 최대한 줄였다.

    - `master` 에 쓰지 않는다. 자기 가지 이름을 인자로 받고 다르면 멈춘다
    - `git add -A` 를 쓰지 않는다. 파일을 이름으로만 받고, 그중에서도
      허용 목록·크기·경로 검사를 통과한 것만 넣는다
    - `git pull` / `git merge` / `git rebase` 를 하지 않는다. 계산 중
      병합 금지가 COMMS.md 규약이고, 자동으로는 더더욱 안 된다
    - `--force` 로 밀지 않는다. 거절당하면 커밋만 남기고 사람을 부른다
    - 판정을 쓰지 않는다. 우편함에 넣는 글은 "몇 행이 도착했다" 까지고
      문턱 적용·해석은 사람 몫으로 남긴다. 자동 생성 표시를 붙인다

[완주를 어떻게 아는가]
    러너는 `rc == 0` 일 때만 기기 태그 사본을 만든다
    (`run_water_v3ens0583.py` 끝부분). 그래서 태그 파일의 존재가 아니라
    **감시 시작 이후로 갱신됐는지**를 본다. 이전 배치가 남긴 같은 이름
    파일을 완주로 오독하지 않기 위해서다.

    드라이버 PID 종료 + 태그 파일 갱신 + 로그 성공 표지 + JSON 검사를
    전부 통과해야 올린다. 하나라도 실패하면 **커밋조차 하지 않고**
    상태 파일에 이유를 적는다.

사용:
    python autopush.py --selftest
    python autopush.py --pid 12345 \
        --result 21_ZIF69_MTV/v3_water_ens/water_results_junseok.json \
        --log    21_ZIF69_MTV/water_ens_rh25.log \
        --expect 12 --label 'ens RH25 2작업' --branch junseok-20260822
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime

REPO = os.path.expanduser('~/mof_project')
STATE = os.path.expanduser('~/.autopush')
LOCK = os.path.join(STATE, 'lock')
STATUS = os.path.join(STATE, 'status.json')
JOURNAL = os.path.join(STATE, 'autopush.log')

MAX_FILE_BYTES = 5 * 1024 * 1024        # 결과 JSON 은 수 KB, 로그는 수십 KB
PUSH_TRIES = 5

# 올려도 되는 곳. 실행 디렉터리(122 MB)를 실수로 넣는 것을 막는 것이 주목적이다.
ALLOW_PREFIX = (
    '21_ZIF69_MTV/v3_water_ens/',
    '21_ZIF69_MTV/v3_water_grid/',
    '21_ZIF69_MTV/v4_water_mix/',
    '21_ZIF69_MTV/COMMS/',
)
ALLOW_SUFFIX = ('.json', '.log', '.md')
DENY_SUBSTR = ('water_runs', 'runs_v3', 'Output/', 'Restart/', 'CrashRestart/',
               'Movies/', 'VTK/', '.data', '.cif')

# 결과 행이 갖춰야 할 열. 하나라도 없으면 절반만 찬 행이다.
REQUIRED_KEYS = ('name', 'label', 'RH', 'CO2_molkg', 'CO2_err',
                 'H2O_molkg', 'H2O_err', 'CO2_retention_pct',
                 'retention_sigma', 'H2O_over_CO2')


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def note(msg):
    line = f'[{now()}] {msg}'
    print(line, flush=True)
    os.makedirs(STATE, exist_ok=True)
    with open(JOURNAL, 'a', encoding='utf-8') as fh:
        fh.write(line + '\n')


def write_status(state, label, problems=None, extra=None):
    os.makedirs(STATE, exist_ok=True)
    doc = {'state': state, 'label': label, 'at': now(),
           'problems': problems or []}
    if extra:
        doc.update(extra)
    with open(STATUS, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    return doc


# ---------------------------------------------------------------- git

def git(*args, check=True):
    p = subprocess.run(('git',) + args, cwd=REPO, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)} -> {p.returncode}\n{p.stderr.strip()}')
    return p


def current_branch():
    return git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()


# ------------------------------------------------------------ 검사기

def check_paths(paths):
    """올려도 되는 파일인지. 실패 이유를 목록으로 돌려준다."""
    bad = []
    for rel in paths:
        if rel.startswith('/') or '..' in rel.split('/'):
            bad.append(f'{rel}: 절대경로이거나 상위로 올라간다')
            continue
        if any(d in rel for d in DENY_SUBSTR):
            bad.append(f'{rel}: 실행 산출물 경로다 (금지 문자열)')
            continue
        if not rel.startswith(ALLOW_PREFIX) and not rel.endswith('.log'):
            bad.append(f'{rel}: 허용된 폴더가 아니다')
            continue
        if not rel.endswith(ALLOW_SUFFIX):
            bad.append(f'{rel}: 허용된 확장자가 아니다')
            continue
        full = os.path.join(REPO, rel)
        if not os.path.exists(full):
            bad.append(f'{rel}: 파일이 없다')
            continue
        size = os.path.getsize(full)
        if size > MAX_FILE_BYTES:
            bad.append(f'{rel}: {size} 바이트로 상한 {MAX_FILE_BYTES} 초과')
    return bad


def check_log(path):
    """러너 로그가 성공으로 끝났는지."""
    bad = []
    if not os.path.exists(path):
        return [f'로그가 없다: {path}']
    txt = open(path, encoding='utf-8', errors='replace').read()
    if 'Traceback' in txt:
        bad.append('로그에 Traceback 이 있다')
    if '[OK]' not in txt:
        bad.append('로그에 [OK] 표지가 없다')
    if '기기명 사본 저장' not in txt:
        bad.append('로그에 기기명 사본 저장 줄이 없다 (러너가 rc=0 으로 끝나지 않았다)')
    for mark in ('!!', '중단합니다'):
        if mark in txt:
            bad.append(f'로그에 자체 검사 실패 표지가 있다: {mark!r}')
    return bad


def check_json(path, expect):
    """결과 JSON 이 온전한지. 절반만 찬 행을 완성된 행으로 올리지 않기 위한 것."""
    if not os.path.exists(path):
        return [f'결과 파일이 없다: {path}'], None
    try:
        rows = json.load(open(path, encoding='utf-8'))
    except Exception as exc:
        return [f'JSON 을 읽을 수 없다: {exc}'], None
    return check_rows(rows, expect)


def check_rows(rows, expect):
    """행 목록 자체를 검사한다 (파일로 쓰기 전에도 볼 수 있게 분리)."""
    bad = []
    if not isinstance(rows, list):
        return [f'리스트가 아니다: {type(rows).__name__}'], None
    if not rows:
        return ['행이 없다'], None
    if expect is not None and len(rows) != expect:
        bad.append(f'행 수가 {len(rows)}, 기대값 {expect}')
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            bad.append(f'{i}행이 사전이 아니다')
            continue
        for k in REQUIRED_KEYS:
            if k not in r:
                bad.append(f'{i}행({r.get("name", "?")}/{r.get("RH", "?")})에 {k} 가 없다')
        for k, v in r.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                bad.append(f'{i}행 {k} 가 {v} 다')
        c = r.get('CO2_molkg')
        if isinstance(c, (int, float)) and not (c > 0):
            bad.append(f'{i}행 CO2_molkg 가 {c} 다 (0 이하)')
    return bad, rows


# ------------------------------------------------------------- 본체

def union_rows(base, new):
    """(name, RH) 로 합친다. 겹치면 **덮지 않고 멈춘다.**

    덮어쓰기를 허용하면 merge_water_batches.py 독스트링이 경고하는 그 상황이
    된다 — 먼저 있던 행이 조용히 사라지고 파일은 멀쩡해 보인다. 겹침은
    사람이 볼 일이지 이 스크립트가 고를 일이 아니다.
    """
    def key(r):
        return (r['name'], float(r['RH']))

    bk = {key(r) for r in base}
    nk = {key(r) for r in new}
    clash = sorted(bk & nk)
    if clash:
        return None, [f'합집합에 겹치는 (조성, RH) 가 있다: {clash}. '
                      '덮어쓰지 않고 멈춘다.']
    merged = sorted(base + new, key=key)
    return merged, []


def read_git_rows(spec):
    """'<ref>:<path>' 에서 결과 행을 읽는다. 커밋된 것이라 변조 위험이 없다."""
    if ':' not in spec:
        return None, [f'--union-from 형식이 <ref>:<path> 가 아니다: {spec}']
    p = git('show', spec, check=False)
    if p.returncode != 0:
        return None, [f'git show {spec} 실패: {p.stderr.strip()[:200]}']
    try:
        rows = json.loads(p.stdout)
    except Exception as exc:
        return None, [f'{spec} 를 JSON 으로 읽을 수 없다: {exc}']
    if not isinstance(rows, list) or not rows:
        return None, [f'{spec} 가 비어 있거나 리스트가 아니다']
    return rows, []


def wait_for_exit(pid, poll=30, cap_hours=48):
    """PID 가 사라질 때까지 기다린다. 상한을 둬 영원히 남지 않게 한다."""
    deadline = time.time() + cap_hours * 3600
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False        # 남의 프로세스다. 기다리지 않는다
        time.sleep(poll)
    return False


def mailbox_entry(label, result_rel, log_rel, nrows, verified):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        f'## {ts} — [자동] {label} 완주. 결과 파일만 올립니다',
        '',
        '**받는 곳**: 데스크탑, 랩탑',
        '**요약**: 감시 스크립트가 완주를 감지해 결과 JSON 을 올렸습니다.',
        '**이 글은 자동 생성입니다 — 판정도 해석도 들어 있지 않습니다.**',
        '사람이 확인한 분석은 별도 글로 올라옵니다.',
        '**답 필요**: 아니오',
        '',
        f'- 완주 감지  `{ts}`',
        f'- 결과 파일  `{result_rel}` — {nrows}행',
        f'- 러너 로그  `{log_rel}`',
        '',
        '통과한 검사:',
        '',
    ]
    lines += [f'- {v}' for v in verified]
    lines += [
        '',
        '이 글에 숫자에 대한 판정은 없습니다. 등록된 문턱을 대는 것은',
        '사람이 합니다. 자동으로 올리는 것은 **결과가 저장소에 도착했다는',
        '사실**까지입니다 — 08-24 에 완주한 계산이 11시간 동안 아무에게도',
        '전달되지 않은 일이 있어 그 구멍만 막는 것입니다.',
        '',
        '---',
        '',
    ]
    return '\n'.join(lines)


def run(args):
    os.makedirs(STATE, exist_ok=True)

    # 두 감시가 겹치지 않게 한다.
    import fcntl
    lockfh = open(LOCK, 'w')
    try:
        fcntl.flock(lockfh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        note('다른 감시가 이미 돌고 있다. 이 감시는 종료한다.')
        return 3
    lockfh.write(str(os.getpid()))
    lockfh.flush()

    label = args.label
    note(f'감시 시작 — {label} (PID {args.pid})')
    write_status('watching', label, extra={'pid': args.pid})

    result_full = os.path.join(REPO, args.result)
    before = os.path.getmtime(result_full) if os.path.exists(result_full) else 0.0
    started = time.time()

    if not wait_for_exit(args.pid, poll=args.poll):
        p = ['드라이버 PID 가 상한 시간 안에 끝나지 않았거나 남의 프로세스다']
        note(p[0]); write_status('failed', label, p); return 1
    note('드라이버 종료 확인')

    # 파일 시스템이 따라오도록 잠깐 준다.
    time.sleep(5)

    problems = []
    verified = []

    if not os.path.exists(result_full):
        problems.append(f'결과 파일이 생기지 않았다: {args.result}')
    else:
        after = os.path.getmtime(result_full)
        if after <= before or after < started:
            problems.append('결과 파일이 이번 실행으로 갱신되지 않았다 '
                            '(이전 배치가 남긴 파일일 수 있다)')
        else:
            verified.append('결과 파일이 이번 실행에서 새로 쓰였다')

    lp = check_log(os.path.join(REPO, args.log))
    problems += lp
    if not lp:
        verified.append('러너 로그에 성공 표지 `[OK]` 와 기기명 사본 줄이 있고 Traceback 이 없다')

    # 합집합 — 좁힌 러너가 자기 TARGETS 밖의 행을 버리고 쓰는 경우를 되돌린다.
    # run_water.py:314/318 이 rows 를 res 가 아니라 TARGETS x RH_LIST 로 만들기
    # 때문에, 같은 결과 파일을 공유하는 두 번째 러너가 앞선 행을 지운다.
    rows = None
    if args.union_from:
        jp0, produced = check_json(result_full, None)   # (문제, 행) 순서다
        problems += jp0
        if not jp0:
            base, bp = read_git_rows(args.union_from)
            problems += bp
            if not bp:
                merged, up = union_rows(base, produced)
                problems += up
                if not up:
                    rows = merged
                    note(f'합집합: 커밋본 {len(base)}행 + 이번 실행 {len(produced)}행 '
                         f'= {len(merged)}행 (겹침 0)')
                    verified.append(
                        f'`{args.union_from}` 의 {len(base)}행과 이번 실행 '
                        f'{len(produced)}행을 (조성, RH) 로 합쳤습니다 — 겹침 0, 덮어쓴 행 0')
        if rows is not None:
            rp, _ = check_rows(rows, args.expect)
            problems += rp
            if not rp:
                verified.append(
                    f'합친 {len(rows)}행이 필수 열 {len(REQUIRED_KEYS)}종 전부 존재, '
                    'NaN·무한대 없음, CO2 로딩 전부 양수')
    else:
        jp, rows = check_json(result_full, args.expect)
        problems += jp
        if not jp:
            verified.append(f'결과 JSON {len(rows)}행, 필수 열 {len(REQUIRED_KEYS)}종 전부 존재, '
                            'NaN·무한대 없음, CO2 로딩 전부 양수')

    files = [args.result, args.log]
    if args.mailbox:
        files.append(args.mailbox)
    pp = check_paths(files)
    problems += pp
    if not pp:
        verified.append('올리는 파일이 허용 폴더·확장자·크기 안에 있고 실행 산출물이 아니다')

    br = current_branch()
    if br != args.branch:
        problems.append(f'가지가 {br} 다. {args.branch} 가 아니면 올리지 않는다')
    else:
        verified.append(f'자기 가지 `{br}` 에서만 작업한다')

    if problems:
        note('검증 실패 — 커밋하지 않는다:')
        for p in problems:
            note(f'   - {p}')
        write_status('failed', label, problems)
        return 1

    note('검증 전 항목 통과')

    entry = mailbox_entry(label, args.result, args.log, len(rows), verified)

    if args.dry_run:
        # 작업 트리를 건드리지 않는다. 넣을 글을 보여 주기만 한다.
        note('--dry-run — 커밋·푸시하지 않고, 우편함도 고치지 않는다')
        note('넣었을 글:\n' + entry)
        write_status('dry-run-ok', label,
                     extra={'files': files, 'rows': len(rows)})
        return 0

    # 여기부터 작업 트리를 고친다. 실패하면 전부 되돌린다 — 우편함만
    # 고쳐진 채 커밋 없이 남으면 다음 사람이 그것을 사람이 쓴 글로 읽는다.
    backups = []                       # [(절대경로, 원래내용 또는 None)]

    def edit(full, text):
        old = open(full, encoding='utf-8').read() if os.path.exists(full) else None
        backups.append((full, old))
        with open(full, 'w', encoding='utf-8') as fh:
            fh.write(text)

    def rollback(why):
        for full, old in reversed(backups):
            if old is None:
                os.remove(full)
            else:
                with open(full, 'w', encoding='utf-8') as fh:
                    fh.write(old)
        if backups:
            note(f'작업 트리 편집 {len(backups)}건을 되돌렸다')
        git('reset', '-q', check=False)
        note(why)

    if args.union_from:
        blob = json.dumps(rows, indent=2, ensure_ascii=False)
        edit(result_full, blob)
        note(f'합친 {len(rows)}행을 {args.result} 에 썼다')
        # 러너는 태그본과 무태그본을 같게 유지한다. 무태그본이 이어받기의
        # 입력(run_water.py:285)이므로 여기서도 같게 맞춰야 다음 실행이
        # 이미 끝난 작업을 다시 돌지 않는다.
        sibling = os.path.join(os.path.dirname(result_full), 'water_results.json')
        if os.path.exists(sibling) and sibling != result_full:
            edit(sibling, blob)
            note('무태그본(이어받기 입력)도 같게 맞췄다')

    if args.mailbox:
        mb_full = os.path.join(REPO, args.mailbox)
        body = open(mb_full, encoding='utf-8').read().split('\n')
        idx = next((i for i, ln in enumerate(body) if ln.startswith('## ')), len(body))
        edit(mb_full, '\n'.join(body[:idx] + entry.split('\n') + body[idx:]))
        note(f'우편함에 자동 생성 글을 넣었다: {args.mailbox}')

    git('add', '--', *files)
    staged = git('diff', '--cached', '--name-only').stdout.split()
    unexpected = [s for s in staged if s not in files]
    if unexpected:
        rollback(f'예상 밖 파일이 스테이지에 있다: {unexpected}')
        write_status('failed', label, [f'예상 밖 파일: {unexpected}'])
        return 1
    if not staged:
        rollback('바뀐 것이 없다. 커밋하지 않는다.')
        write_status('nothing-to-do', label)
        return 0

    msg = (f'[자동] {label} 완주 — 결과 파일 도착 (분석 전)\n'
           f'\n'
           f'감시 스크립트(autopush.py)가 드라이버 종료를 감지하고 올렸습니다.\n'
           f'결과 {len(rows)}행. 검증: 로그 성공 표지, 필수 열 전부, NaN 없음,\n'
           f'CO2 로딩 전부 양수, 파일이 이번 실행에서 새로 쓰임.\n'
           f'\n'
           f'판정·해석은 들어 있지 않습니다. 등록된 문턱을 대는 것은 사람이\n'
           f'합니다. 이 커밋이 보장하는 것은 결과가 저장소에 도착했다는\n'
           f'사실까지입니다.\n'
           f'\n'
           f'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n')
    try:
        git('commit', '-q', '-m', msg)
    except RuntimeError as exc:
        rollback(f'커밋이 실패했다: {exc}')
        write_status('failed', label, [f'커밋 실패: {exc}'])
        return 1
    head = git('rev-parse', '--short', 'HEAD').stdout.strip()
    note(f'커밋 {head}')

    for attempt in range(1, PUSH_TRIES + 1):
        p = git('push', 'origin', args.branch, check=False)
        if p.returncode == 0:
            note(f'푸시 성공 (시도 {attempt})')
            write_status('pushed', label,
                         extra={'commit': head, 'rows': len(rows), 'files': files})
            return 0
        note(f'푸시 실패 (시도 {attempt}/{PUSH_TRIES}): {p.stderr.strip()[:200]}')
        time.sleep(min(60 * attempt, 300))

    note('푸시를 포기한다. 커밋은 로컬에 남아 있으니 사람이 밀어야 한다.')
    note('강제 푸시는 하지 않는다 — 남의 커밋을 지울 수 있다.')
    write_status('commit-only', label,
                 ['푸시가 반복 실패했다. 로컬 커밋은 남아 있다.'],
                 extra={'commit': head})
    return 2


# ---------------------------------------------------------- 자체 시험

def selftest():
    import tempfile
    ok = True

    def expect(name, cond):
        nonlocal ok
        print(f'  {"통과" if cond else "실패"}  {name}')
        if not cond:
            ok = False

    good = [{'name': 'x', 'label': 'x', 'RH': 0.0, 'CO2_molkg': 1.2,
             'CO2_err': 0.03, 'H2O_molkg': 0.0, 'H2O_err': 0.0,
             'CO2_retention_pct': 100.0, 'retention_sigma': 0.0,
             'H2O_over_CO2': 0.0}]

    d = tempfile.mkdtemp()

    def wjson(obj):
        p = os.path.join(d, f'r{time.time_ns()}.json')
        json.dump(obj, open(p, 'w', encoding='utf-8'))
        return p

    print('JSON 검사기')
    expect('정상 1행을 통과시킨다', check_json(wjson(good), 1)[0] == [])
    expect('행 수가 다르면 잡는다', check_json(wjson(good), 2)[0] != [])
    expect('리스트가 아니면 잡는다', check_json(wjson({'a': 1}), 1)[0] != [])
    expect('빈 리스트를 잡는다', check_json(wjson([]), 0)[0] != [])
    bad = json.loads(json.dumps(good)); del bad[0]['CO2_err']
    expect('열이 빠지면 잡는다', check_json(wjson(bad), 1)[0] != [])
    p = os.path.join(d, 'nan.json')
    open(p, 'w').write('[{"name":"x","label":"x","RH":0.0,"CO2_molkg":1.0,'
                       '"CO2_err":0.0,"H2O_molkg":0.0,"H2O_err":0.0,'
                       '"CO2_retention_pct":NaN,"retention_sigma":0.0,'
                       '"H2O_over_CO2":0.0}]')
    expect('NaN 을 잡는다', check_json(p, 1)[0] != [])
    zero = json.loads(json.dumps(good)); zero[0]['CO2_molkg'] = 0.0
    expect('CO2 로딩 0 을 잡는다', check_json(wjson(zero), 1)[0] != [])
    expect('없는 파일을 잡는다', check_json(os.path.join(d, 'nope.json'), 1)[0] != [])

    print('합집합 (좁힌 러너가 버린 행을 되살리는 부분)')
    b = [dict(good[0], name='e1', RH=0.0), dict(good[0], name='e1', RH=0.9)]
    n = [dict(good[0], name='e1', RH=0.25)]
    m, prob = union_rows(b, n)
    expect('겹치지 않으면 합친다', prob == [] and len(m) == 3)
    expect('합친 결과가 (조성, RH) 로 정렬된다',
           m is not None and [r['RH'] for r in m] == [0.0, 0.25, 0.9])
    _, prob2 = union_rows(b, b)
    expect('겹치면 덮지 않고 멈춘다', prob2 != [])
    _, prob3 = union_rows(b, [dict(good[0], name='e1', RH=0.0)])
    expect('한 행만 겹쳐도 멈춘다', prob3 != [])
    m4, prob4 = union_rows(b, [dict(good[0], name='e2', RH=0.0)])
    expect('다른 조성의 같은 RH 는 겹침이 아니다', prob4 == [] and len(m4) == 3)

    print('로그 검사기')
    lg = os.path.join(d, 'ok.log')
    open(lg, 'w', encoding='utf-8').write('...\n[OK] water_results.json\n  기기명 사본 저장: /x\n')
    expect('성공 로그를 통과시킨다', check_log(lg) == [])
    lg2 = os.path.join(d, 'tb.log')
    open(lg2, 'w', encoding='utf-8').write('[OK]\n기기명 사본 저장: /x\nTraceback (most recent call last):\n')
    expect('Traceback 을 잡는다', check_log(lg2) != [])
    lg3 = os.path.join(d, 'part.log')
    open(lg3, 'w', encoding='utf-8').write('[OK] water_results.json\n')
    expect('기기명 사본 줄이 없으면 잡는다', check_log(lg3) != [])
    lg4 = os.path.join(d, 'halt.log')
    open(lg4, 'w', encoding='utf-8').write('  !! 5자리 물이 아닙니다. 중단합니다.\n')
    expect('러너 자체 검사 실패를 잡는다', check_log(lg4) != [])

    print('경로 검사기 (122 MB 실행 디렉터리를 막는 것이 목적)')
    expect('실행 디렉터리를 거부한다',
           check_paths(['21_ZIF69_MTV/water_runs_v3ens/rh25_x/Output/System_0/a.data']) != [])
    expect('.data 를 거부한다', check_paths(['21_ZIF69_MTV/v3_water_ens/a.data']) != [])
    expect('.cif 를 거부한다', check_paths(['21_ZIF69_MTV/v3_water_ens/a.cif']) != [])
    expect('상위 경로를 거부한다', check_paths(['../../etc/passwd']) != [])
    expect('절대경로를 거부한다', check_paths(['/etc/passwd']) != [])
    expect('허용 밖 폴더를 거부한다', check_paths(['21_ZIF69_MTV/charged_v3/x.json']) != [])
    real = '21_ZIF69_MTV/v3_water_ens/water_results_junseok.json'
    if os.path.exists(os.path.join(REPO, real)):
        expect('실제 결과 파일을 통과시킨다', check_paths([real]) == [])
    else:
        print('  건너뜀  실제 결과 파일이 없어 확인 못 함')

    print()
    print('전부 통과' if ok else '실패한 항목이 있다')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--pid', type=int)
    ap.add_argument('--result')
    ap.add_argument('--log')
    ap.add_argument('--mailbox', default=None,
                    help='자동 생성 글을 넣을 우편함 (생략하면 안 넣는다)')
    ap.add_argument('--union-from', default=None, metavar='REF:PATH',
                    help='커밋된 결과와 (조성, RH) 로 합친다. 좁힌 러너가 '
                         '자기 TARGETS 밖의 행을 버리고 쓰는 것을 되돌린다. '
                         '겹치면 덮지 않고 멈춘다.')
    ap.add_argument('--expect', type=int, default=None)
    ap.add_argument('--label', default='계산')
    ap.add_argument('--branch', required=False, default='junseok-20260822')
    ap.add_argument('--poll', type=int, default=30)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    for need in ('pid', 'result', 'log'):
        if not getattr(a, need):
            ap.error(f'--{need} 가 필요합니다')
    if a.branch == 'master':
        print('master 에는 자동으로 쓰지 않습니다.', file=sys.stderr)
        return 1
    try:
        return run(a)
    except Exception as exc:                       # noqa: BLE001
        import traceback
        note('감시가 예외로 죽었다:\n' + traceback.format_exc())
        write_status('crashed', a.label, [repr(exc)])
        return 1


if __name__ == '__main__':
    sys.exit(main())
