# -*- coding: utf-8 -*-
"""§AW-2: (1) 아무도 두 압력을 다 끝내지 않은 종을 pick 파일로 쓰고
          (2) **살아 있음 지표**를 함께 찍는다.

⚠ 살아 있음을 "두 압력 다 끝난 종의 수" 로 재면 안 된다 (laptop2 11:2x).
  `run_core_wc.py:104` 의 **바깥 루프가 압력**이라, 0.15 bar 단계(작업합의 약 70 %,
  12워커로 ~11.6 h) 내내 그 수는 **0 에서 안 움직인다.** 기기가 꽉 차 도는데
  "아무도 안 돈다" 로 읽힌다. `run_status` 는 `row['run_status'][f'{P:g}bar'] = stt` 로
  **작업마다, 실패해도** 채워지므로 두 단계 모두에서 단조 증가한다.

마지막 줄: "<남은 종 수> <run_status 칸> <값 칸>"

두 생존 지표를 **같이** 냅니다 — 랩탑 11:3x 의 정리대로 둘은 **"전량 실패 중인 기기"** 에서 갈립니다.
  `run_status` 칸 : 실패해도 오름 → 실패 중인 기기를 **살아 있음**으로 봄 → 중복을 덜 냄
  `값` 칸         : 값이 나와야 오름 → 실패 중인 기기를 **죽음**으로 봄 → 빈자리를 메움
제 사슬은 `run_status` 를 **주 문턱(3 h)**, `값` 을 **보조 문턱(6 h)** 으로 씁니다.
보조가 없으면 **남이 전량 실패에 빠졌을 때 제 지표만 계속 올라 아무도 안 메웁니다**
(10:39 에 제가 172종을 3분 만에 전부 `[no-output]` 낸 그 상태). 랩탑 지표가 덮어 주지만
그쪽이 같이 죽으면 남는 자리라, 제 쪽에서도 닫습니다.
"""
import json, glob, os, subprocess
G = '/home/mangwon1/mof_project'
R = os.path.join(G, '21_ZIF69_MTV')
MINE = 'ext2_desktop'                      # 내 출력은 대조에서 뺀다

def sh(*a):
    return subprocess.run(a, cwd=G, capture_output=True, text=True).stdout

done, cells, vals, nfile = set(), 0, 0, 0

def take(txt):
    global cells, vals, nfile
    try:
        rows = json.loads(txt).get('rows', [])
    except Exception:
        return
    nfile += 1
    for r in rows:
        cells += len(r.get('run_status') or {})
        vals += (r.get('n_0.15bar') is not None) + (r.get('n_0.01bar') is not None)
        if r.get('n_0.15bar') is not None and r.get('n_0.01bar') is not None:
            done.add(r['file'])

for f in glob.glob(os.path.join(R, 'core_wc_results*.json')):
    if MINE in f:
        continue
    take(open(f, encoding='utf-8', errors='ignore').read())
refs = [l.strip() for l in sh('git', 'for-each-ref', '--format=%(refname:short)',
                              'refs/remotes/origin').splitlines() if l.strip() and 'HEAD' not in l]
for rb in refs:
    for p in sh('git', 'ls-tree', '-r', '--name-only', rb, '21_ZIF69_MTV/').splitlines():
        b = p.split('/')[-1]
        if b.startswith('core_wc_results') and b.endswith('.json') and MINE not in b:
            take(sh('git', 'show', '%s:%s' % (rb, p)))

target = json.load(open(os.path.join(R, 'core_wc_pick2.json'), encoding='utf-8'))
keep = [q for q in target if q['file'] not in done]
for q in keep:
    q['assign'] = 'desktop'
    q['source'] = '§AW-2 메움(데스크탑)'
json.dump(keep, open(os.path.join(R, 'core_wc_pick3_desktop_run.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('결과파일 %d · 두압력완주 %d종 / 목표 %d종 · run_status 칸 %d · 값 칸 %d' %
      (nfile, len(done), len(target), cells, vals))
print('%d %d %d' % (len(keep), cells, vals))
