"""수분 배치 진행 상황 — 로그가 아니라 출력 파일을 보고 셉니다.

[왜 필요한가]
    `run_water.py:301` 이 `ex.map(_star, jobs)` 로 돕니다. chunksize 기본값이
    1 이라 워커는 비는 대로 다음 작업을 집습니다(파도로 끊기지 않습니다).
    **그런데 `ex.map` 은 결과를 제출 순서대로 내놓습니다.**

    작업 순서는 조성별·RH 오름차순이므로(`run_water.py:295`), 16작업이면

        idx 0~2   saIm0583 RH0/25/50
        idx 3     saIm0583 RH90     <- 가장 비싼 축(20시간대)
        idx 4~15  나머지 12작업

    입니다. 루프가 idx 3 에서 막히므로 **로그는 세 줄을 찍고 20시간 가까이
    얼어붙습니다.** 그 사이 idx 4~15 가 완주해도 한 줄도 안 나옵니다.

    CLAUDE.md 4 절이 "실행 폴더 개수로 세지 마라", "출력 파일이 그대로여도
    멈춘 게 아니다" 라고 적은 그 함정의 세 번째 판입니다. 여기서 "멈췄다"고
    판단해 죽였다 살리면, 진행 중이던 RH90 의 20시간이 통째로 날아갑니다
    (체크포인트는 배치만 복원하고 진행도는 복원하지 않습니다).

[무엇을 보나]
    러너 **자신의** 판정 함수를 그대로 씁니다 — 새 기준을 만들지 않습니다.
    `rw.finished()` 와 `rw.net_charge_ok()` 는 이어받기가 "이 작업은 끝났다"
    고 인정할 때 쓰는 바로 그 검사입니다. 즉 여기서 완료로 세는 것과
    러너가 `cached` 로 건너뛰는 것이 항상 일치합니다.

사용:
    러너와 **같은 env** 로 도세요. run_water 를 import 하므로 numpy 가 필요하고,
    시스템 python 에는 대개 없습니다.

    ~/miniconda3/envs/czeromof/bin/python water_progress.py
    ~/miniconda3/envs/czeromof/bin/python water_progress.py --runs water_runs
"""
import argparse
import glob
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_water as rw  # noqa: E402

DIRPAT = re.compile(r'^rh(\d+)_(.+)$')


def scan(runs):
    out = []
    for d in sorted(glob.glob(os.path.join(runs, 'rh*_*'))):
        m = DIRPAT.match(os.path.basename(d))
        if not m:
            continue
        rh, name = int(m.group(1)), m.group(2)
        data = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        ck = os.path.join(d, 'CrashRestart', 'binary_restart.dat')
        done = bool(data) and rw.finished(data[0]) and rw.net_charge_ok(data[0])
        # 체크포인트가 최근이면 살아 있는 것. mtime 은 500 사이클마다 갱신된다.
        ck_age = (time.time() - os.path.getmtime(ck)) if os.path.exists(ck) else None
        out.append({'name': name, 'rh': rh, 'done': done, 'ck_age': ck_age,
                    'resumed': os.path.exists(os.path.join(d, '.resume_attempted'))})
    return out


def human(sec):
    if sec is None:
        return '없음'
    if sec < 90:
        return f'{int(sec)}초 전'
    if sec < 5400:
        return f'{sec/60:.0f}분 전'
    return f'{sec/3600:.1f}시간 전'


def main():
    ap = argparse.ArgumentParser(description='수분 배치 진행 — 출력 파일 기준')
    ap.add_argument('--runs', default='water_runs_v3grid', help='실행 폴더')
    a = ap.parse_args()

    if not os.path.isdir(a.runs):
        print(f'!! 실행 폴더가 없습니다: {a.runs}')
        return 1

    rows = scan(a.runs)
    if not rows:
        print(f'{a.runs} 에 rh*_* 폴더가 없습니다 (아직 시작 전이거나 이미 정리됨)')
        return 0

    done = [r for r in rows if r['done']]
    print(f'{a.runs} — 완료 {len(done)} / 착수 {len(rows)}')
    print(f'{"조성":<12} {"RH":>5} {"상태":<8} {"체크포인트 갱신":>16}  비고')
    print('-' * 60)
    for r in sorted(rows, key=lambda x: (x['name'], x['rh'])):
        st = '완료' if r['done'] else '진행 중'
        note = '이어받기 시도됨' if r['resumed'] and not r['done'] else ''
        # 체크포인트가 오래 멈춰 있으면 죽었을 수 있다. 다만 RH90 은 500
        # 사이클에 30분 넘게 걸리므로 그것만으로 단정하지 않는다.
        if not r['done'] and r['ck_age'] and r['ck_age'] > 7200:
            note = (note + ' / 2시간 넘게 조용함 — pgrep -x simulate 로 확인').strip(' /')
        print(f'{r["name"]:<12} {r["rh"]:>4}% {st:<8} {human(r["ck_age"]):>16}  {note}')

    print()
    print('완료 판정은 러너의 finished() + net_charge_ok() 를 그대로 씁니다 —')
    print('여기서 완료인 것과 러너가 cached 로 건너뛰는 것이 항상 일치합니다.')
    print('로그(water_v3grid*.log)는 ex.map 이 제출 순서로 내놓기 때문에')
    print('비싼 작업 하나에서 막힙니다. 진행은 로그가 아니라 이 표로 보세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
