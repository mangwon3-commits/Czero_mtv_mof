"""T-B2w 결과 JSON 의 ff_check 재판독 (09-06). 첫 판 run_tb2w.py 의 정규식이 'p_0/k_B:' 의 콜론을 못 읽어
OwOw_eps=None → ok=False 로 39행을 '실패' 표시했다. 출력 파일에서 다시 읽어 ok 를 바로잡는다. K_H 값은 건드리지 않는다.
사용: python fix_tb2w_ffcheck.py v3w_water_kh/water_kh_ALLw_<tag>.json
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tb2w as W
p = sys.argv[1]; d = json.load(open(p))
n_fixed = 0
for r in d['rows']:
    old = r.get('ff_check', {}).get('ok')
    r['ff_check'] = W.ff_check(r['name'])
    kh_ok = r.get('KH_water') is not None
    r['ok'] = bool(kh_ok and r['ff_check']['ok'])
    if r['ff_check']['ok']:
        r.pop('WARN_ff_check', None)
    if old != r['ff_check']['ok']:
        n_fixed += 1
d['note'] = d.get('note', '') + ' | ff_check 는 fix_tb2w_ffcheck.py(콜론 정규식)로 재판독함'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
ok = sum(1 for r in d['rows'] if r['ok']); print(f'재판독 {n_fixed}행 변경, ok {ok}/{len(d["rows"])} -> {p}')
