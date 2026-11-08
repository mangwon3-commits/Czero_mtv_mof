# -*- coding: utf-8 -*-
"""등록 D — CoRE 판 Zn(bib)(bdtdc)(2017[Zn][dia]3[FSR]1 · CoRE 기하 · CoRE 전하)의 298 K 습윤 TSA 회수량 9작업 · laptop2.
등록 `ASSIGN_ZNBDT_6SEED_CORE_20261108.md` §D · `ASSIGN_CORE22_HUMID_PLAN_20261108.md` §0(이 결과를 G 의 그 행으로 씀).

⑩ 실행기 `run_e24i_no2_humid_wc.py`(md5 c2d4673a · 물만 막음 삽입 · 막음 감사)를 **무수정 import** 하고 모듈 전역만 바꿉니다.
  ① 대상: `core_pop_cifs.zip` 안의 `2017_Zn__dia_3_FSR_1.cif` 바이트(md5 430a80b0 · C 실행기와 같은 파일)를 저장소 밖
     `~/.mof_chain/core22_1108/cifs/` 에 풀고(이미 있으면 md5 대조만), 실행기의 prep() 이 `charged_v3/core_zn_dia_fsr1_h1~h3_DDEC6.cif` 로
     바이트 같은 사본을 만듭니다(`_DDEC6` 는 이름 규칙일 뿐 · 전하는 CoRE CIF 의 것 · 사본은 커밋 안 함).
  ② 막음: C 준비 결과 `results_core22_blocks_laptop.json` 의 이 구조 행 — 1.65(CO₂) 구 0 · 1.82(N₂) 구 0 · **1.30(물) 구 4** → ⑩ 과 같은
     물만 막음(ads · tsa · vsa 모두). 막음 파일 `core22_zeo_runs/2017_Zn__dia_3_FSR_1/block1.30/2017_Zn__dia_3_FSR_1.block` 은 master 판을
     저장소 밖 `~/.mof_chain/core22_d/` 에 꺼내 쓰고, md5 를 막음 결과 JSON 의 block_md5 와 대조합니다.
  ③ 조건 · 감사 · 착수 간격: ⑩ 그대로(298 K · CO₂ 15 kPa · 물 2,852.1 Pa → tsa 373 K → vsa 5 kPa · 5,000 + 15,000 · 물 차단 수 = 구 4 × 셀 수).
  ④ 이름: 결과 `v3w_humid_wc/humid_working_capacity_w2_core_zn_dia_fsr1_laptop2.json`(등록 §D) · 요약 `results_core_zn_dia_fsr1_humid_summary_laptop2.json`
     · 잠금 `~/.mof_chain/.core_zn_dia_fsr1_hwc_start.lock`. 요약 머리의 test · assign 두 칸만 D 판으로 바로잡고 `launcher_fix` 에 바꾸기 전 값을 남깁니다.
사용: python run_core22_d_humid_wc.py   (CORE22_D_DRY=1 이면 ⑩ 의 E24I_DRY 와 같이 저장소 밖 10 사이클 드라이)
"""
import hashlib
import json
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
TAG = 'core_zn_dia_fsr1'
KEY, FILE, CIF_MD5 = '2017[Zn][dia]3[FSR]1', '2017_Zn__dia_3_FSR_1.cif', '430a80b09897741b80702e70cc784cbb'
MACHINE = 'laptop2'
if os.environ.get('CORE22_D_DRY'):
    os.environ['E24I_DRY'] = '1'
os.environ['HWC_V3W_TARGETS'] = ','.join(f'{TAG}_h{k}' for k in (1, 2, 3))
os.environ.setdefault('HWC_V3W_WORKERS', '6')
os.environ['HWC_V3W_RESULT'] = f'humid_working_capacity_w2_{TAG}_{MACHINE}.json'


def md5b(b):
    return hashlib.md5(b).hexdigest()


# ① CoRE CIF(저장소 밖)
CIFS = os.path.expanduser('~/.mof_chain/core22_1108/cifs'); os.makedirs(CIFS, exist_ok=True)
SRC = os.path.join(CIFS, FILE)
with zipfile.ZipFile(os.path.join(HERE, 'core_pop_cifs.zip')) as zf:
    zb = zf.read(FILE)
if md5b(zb) != CIF_MD5:
    sys.exit(f'  !! zip 안 {FILE} md5 {md5b(zb)} ≠ {CIF_MD5} — 착수 안 함')
if not os.path.exists(SRC):
    open(SRC, 'wb').write(zb)
if md5b(open(SRC, 'rb').read()) != CIF_MD5:
    sys.exit(f'  !! 풀린 {SRC} 가 zip 바이트와 다름 — 착수 안 함')

# ② 막음 표(master 판 막음 결과 · 막음 파일)
def show(path):
    return subprocess.run(['git', 'show', f'origin/master:21_ZIF69_MTV/{path}'], cwd=HERE, capture_output=True, check=True).stdout


BJ = json.loads(show('results_core22_blocks_laptop.json'))
if not BJ.get('all_blocks_ok'):
    sys.exit('  !! 막음 결과가 전부 ok 가 아님 — 착수 안 함')
ROW = {r['key']: r for r in BJ['rows']}[KEY]
if ROW['cif_md5'] != CIF_MD5:
    sys.exit(f'  !! 막음 결과의 CIF md5 {ROW["cif_md5"]} ≠ {CIF_MD5}')
for r, n in (('r1.65', 0), ('r1.82', 0), ('r1.30', 4)):
    if ROW[r]['n_spheres'] != n or not ROW[r]['block_ok']:
        sys.exit(f'  !! {KEY} {r} 구 {ROW[r]["n_spheres"]} ≠ {n}(이 실행기는 물만 막음) — 착수 안 함')
BDIR = os.path.expanduser('~/.mof_chain/core22_d'); os.makedirs(BDIR, exist_ok=True)
WB = os.path.join(BDIR, os.path.basename(ROW['r1.30']['block_file']))
open(WB, 'wb').write(show(ROW['r1.30']['block_file']))
if md5b(open(WB, 'rb').read()) != ROW['r1.30']['block_md5']:
    sys.exit('  !! 물 막음 파일 md5 가 막음 결과와 다름 — 착수 안 함')

import run_e24i_no2_humid_wc as N   # noqa: E402
if md5b(open(os.path.abspath(N.__file__), 'rb').read()) != 'c2d4673a41523ddee59295f2a8938200':
    sys.exit('  !! ⑩ 실행기 md5 불일치 — 착수 안 함')
N.BASE_TAG = TAG
N.SRC_CIF, N.SRC_MD5_PREFIX = SRC, CIF_MD5
N.WBLOCK, N.WBLOCK_MD5, N.WKEY = WB, ROW['r1.30']['block_md5'], f'{TAG}_water'
N.LOCK = os.path.join(N.CHAIN, f'.{TAG}_hwc_start.lock')
if not N.DRY:
    N.SUMMARY = os.path.join(HERE, f'results_{TAG}_humid_summary_{MACHINE}.json')
hw = N.hw


def fix_summary():
    if not os.path.exists(N.SUMMARY):
        return
    d = json.load(open(N.SUMMARY, encoding='utf-8'))
    before = {k: d.get(k) for k in ('test', 'assign')}
    d['test'] = f'CoRE 판 Zn(bib)(bdtdc) {KEY}(CoRE 기하 · CoRE 전하) 298 K 습윤 TSA 작업 용량 — 물 막음 1.30 구 4'
    d['assign'] = 'ASSIGN_ZNBDT_6SEED_CORE_20261108.md §D · ASSIGN_CORE22_HUMID_PLAN_20261108.md §0(G 의 이 행)'
    d['core'] = {'key': KEY, 'file': FILE, 'cif_md5': CIF_MD5, 'blocks_source': 'results_core22_blocks_laptop.json (origin/master)',
                 'block_r1.30': ROW['r1.30']['block_file'], 'n_spheres': {'r1.65': 0, 'r1.82': 0, 'r1.30': 4}}
    d['launcher'] = {'file': os.path.basename(__file__), 'md5': md5b(open(os.path.abspath(__file__), 'rb').read())}
    d['launcher_fix'] = {'why': '⑩ 실행기 summarize() 가 −NO₂ 문구를 고정으로 씀 — 값 · 행 · 감사는 그대로', 'before': before}
    json.dump(d, open(N.SUMMARY, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    ok, fm = N.ff_gate.md5_gate()
    print(f"  파일 관문 md5 {fm} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    print(f'등록 D — {KEY} 298 K 습윤 WC(물 막음 1.30 구 4) · 작업 {len(N.JOBS)} · 드라이 {N.DRY} · 사이클 {hw.CYCLES}+{hw.INIT}', flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:12s} {getattr(hw, k)}', flush=True)
    print(f'  SRC          {SRC} ({CIF_MD5[:8]}) · 물 막음 {WB} ({N.WBLOCK_MD5[:8]} · 구 {N.nsph()}) · 요약 {N.SUMMARY}', flush=True)
    if os.path.exists(hw.RESULT) or any(os.path.exists(os.path.join(hw.RUNS, f'{lab}_{t}')) for t in hw.TARGETS for lab, *_ in hw.CONDITIONS):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        sys.exit(1)
    info = N.prep()
    rc = hw.main()
    rows, aud = N.audit()
    out = N.summarize(rows, aud, info)
    fix_summary()
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:<22} ok {r['ok']} · 입력 막음 줄 {r.get('blockpockets_in_input')} · 물 차단 {r.get('block', {}).get('water', {}).get('n_blocked')}"
              f"/{r.get('n_expected_water')} · 셀 {r.get('unit_cells')} · 완주 {r.get('finished')} · rc {r.get('returncode')} · not-found {r.get('stderr_not_found')} · 씨앗 {r.get('seed')}", flush=True)
    print(f"요약 저장 {N.SUMMARY} · {json.dumps({k: v for k, v in out.get('summary', {}).items() if k != 'loadings'}, ensure_ascii=False)[:900]}", flush=True)
    sys.exit(rc or 0)
