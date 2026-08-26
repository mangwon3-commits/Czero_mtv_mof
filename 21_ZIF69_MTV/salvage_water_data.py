"""중단된 수분 런의 완주분을 RASPA 출력에서 직접 건져 JSON 으로 만든다.

[왜 필요한가 — run_water.py 는 전량 완주 후 한 번만 쓴다]
    `run_water.py` 의 저장은 `main()` 끝에 딱 한 번입니다. 그래서 러너를
    중간에 죽이면 **완주한 작업의 결과도 JSON 에 하나도 안 남습니다.**
    `.data` 파일에는 다 있는데 사람이 손으로 뽑아야 합니다.

    08-26 저압 18작업이 그 상태입니다 — 8작업이 완주했는데
    `v3_water_lowrh/` 는 빈 폴더입니다. 여기서 러너를 죽이면 30시간 중
    14시간치가 **파일로는 사라집니다.**

    분기 (가)(대조군 non-null 시 v4 저압 중단)를 실행하려면 죽이기 전에
    이것을 돌려야 합니다. 그러지 않으면 단일 치환기 8점 — 판정과 무관해서
    **살아남아야 할 값들** — 까지 같이 잃습니다.

[무엇을 하는가]
    작업 폴더의 `System_0/*.data` 를 읽어 `Simulation finished` 가 있는 것만
    골라, run_water.py 가 쓰는 것과 **같은 키**로 JSON 을 만듭니다.
    미완주 작업은 건드리지 않습니다.

[자를 두 벌 두지 않는다 — COMMS 규약 ⑥ (가)]
    유지율과 그 유의도는 **직접 계산하지 않습니다.** run_water.py 가 이미
    `den = sqrt(ec**2 + e0**2)` 로 하는 계산을 손으로 다시 짜면 같은 양에
    두 개의 자가 생깁니다(08-26 laptop2 사례). 여기서는 **로딩과 오차만**
    적고, 유지율은 나중에 run_water 나 merge 도구가 계산하게 둡니다.

사용:
    python salvage_water_data.py <작업폴더> <출력.json> [--tag laptop]
예:
    python salvage_water_data.py water_runs_lowrh \\
        v3_water_lowrh/water_results_laptop.json --tag laptop
"""
import glob
import json
import os
import re
import sys

# 작업 폴더 이름 규약: rh<두자리>_<조성>  (run_water.py 가 만드는 형식)
DIRPAT = re.compile(r'^rh(\d+)_(.+)$')

# RASPA 출력에서 성분별 절대 로딩을 뽑습니다. 성분 블록 안의 첫 번째
# 'Average loading absolute [mol/kg framework]' 가 그 성분의 값입니다.
COMP = re.compile(
    r'Component\s+(\d+)\s+\[(\w+)\].*?'
    r'Average loading absolute \[mol/kg framework\]\s+'
    r'([\d.eE+-]+)\s*\+/-\s*([\d.eE+-]+)', re.S)


def read_job(d):
    """완주한 작업 하나를 읽어 (조성, RH, 로딩dict) 를 낸다. 미완주면 None."""
    hits = glob.glob(os.path.join(d, '**', 'System_0', '*.data'), recursive=True)
    if not hits:
        return None
    txt = open(hits[0], encoding='utf-8', errors='ignore').read()
    if 'Simulation finished' not in txt:
        return None
    out = {}
    for _idx, name, val, err in COMP.findall(txt):
        out[name] = (float(val), float(err))
    return out or None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    runs, dst = sys.argv[1], sys.argv[2]
    tag = None
    if '--tag' in sys.argv:
        tag = sys.argv[sys.argv.index('--tag') + 1]

    rows, skipped = [], []
    for d in sorted(glob.glob(os.path.join(runs, '*'))):
        if not os.path.isdir(d):
            continue
        m = DIRPAT.match(os.path.basename(d))
        if not m:
            continue
        rh = int(m.group(1)) / 100.0
        name = m.group(2)
        got = read_job(d)
        if got is None:
            skipped.append(os.path.basename(d))
            continue
        co2 = got.get('CO2')
        h2o = got.get('water') or got.get('H2O') or got.get('Water')
        if co2 is None:
            skipped.append(os.path.basename(d) + ' (CO2 없음)')
            continue
        r = {'name': name, 'RH': rh,
             'CO2_molkg': co2[0], 'CO2_err': co2[1]}
        if rh > 0 and h2o is not None:
            r['H2O_molkg'] = h2o[0]
            r['H2O_err'] = h2o[1]
            r['H2O_over_CO2'] = (h2o[0] / co2[0]) if co2[0] else None
        rows.append(r)

    rows.sort(key=lambda r: (r['name'], r['RH']))
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f'건진 작업 {len(rows)}개 -> {dst}')
    for r in rows:
        w = f"  물 {r['H2O_molkg']:.4f}" if 'H2O_molkg' in r else ''
        print(f"  {r['name']:10} RH{int(r['RH']*100):>3}%  "
              f"CO2 {r['CO2_molkg']:.4f} ± {r['CO2_err']:.4f}{w}")
    if skipped:
        print(f'\n미완주로 건너뜀 {len(skipped)}개: {" ".join(skipped)}')
    if tag and not os.path.basename(dst).endswith(f'_{tag}.json'):
        print(f'\n!! 파일명에 기기 태그가 없습니다. merge_water_batches.py 의 '
              f'machine_of 가 거부합니다 — water_results_{tag}.json 형식이어야 합니다.')
    print('\n주의: 유지율은 여기서 계산하지 않았습니다. run_water / merge 도구가 '
          '자기 식으로 냅니다 (COMMS 규약 ⑥ 가).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
