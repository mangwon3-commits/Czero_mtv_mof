"""재생 에너지 수지 v3 — 확정된 v3 작업 용량 위의 산술.

regen_energy.py 의 검증된 비용 함수(sensible / vacuum_work / drying)를
그대로 가져다 쓰고, 입력만 v3 로 바꾼다. 가정(Cp 0.9 대푯값, 회수율 50%,
열회수 0%)도 그대로다 -- 가정을 바꾸면 v2 수지와 비교할 수 없다.

v2 와 달라지는 것은 두 입력뿐이다:
    Q_st   v3 GCMC (results_v3.json 의 값)
    WC     v3_wc(건조) + v3_humid_wc(습윤)

산출: regen_energy_v3.json
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from regen_energy import sensible, vacuum_work, drying, RECOVERY, \
    CP_FRAMEWORK, CP_RANGE, HEAT_RECOVERY, RECOVERY_RANGE  # noqa: E402

# [2026-08-27] 하드코딩을 걷어냈습니다. 일일 감사(08-26)가 잡은 것:
#
#   "승자 조성 saIm0583 은 건조·습윤 WC 가 둘 다 완비되어 있는데
#    regen_energy_v3.py 의 NAMES/파일 목록에서 완전히 빠져 있어
#    regen_energy_v3.json 에 그 행 자체가 존재하지 않습니다."
#
# 원인은 이 스크립트가 접미사 없는 파일 **하나씩만** 열고 NAMES 를 손으로
# 적어 둔 것이었습니다. `_g0583` `_ext` `_grid` `_mslm075` 접미사 파일과
# v4_humid_wc/ 는 아예 안 열렸습니다. **글롭으로 바꾸고 NAMES 를 자료에서
# 유도합니다** — 새 조성이 생기면 자동으로 들어옵니다.


def load_qst():
    """Q_st 를 결과 파일에서 읽는다. 손으로 적어 두면 새 조성이 누락된다."""
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'results_v3*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
        for r in rows:
            if 'Qst_CO2' in r:
                out[r['name']] = r['Qst_CO2']
    return out


def load_wc():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'v3_wc', '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for r in (d['rows'] if isinstance(d, dict) and 'rows' in d else d):
            w = r['working_capacity']
            out.setdefault(r['name'], {})['dry_tsa'] = w['tsa']['value']
            out[r['name']]['dry_vsa'] = w['vsa05']['value']
    for sub in ('v3_humid_wc', 'v4_humid_wc'):
        for f in sorted(glob.glob(os.path.join(HERE, sub, '*.json'))):
            d = json.load(open(f, encoding='utf-8'))
            for r in (d['rows'] if isinstance(d, dict) and 'rows' in d else d):
                w = r['working_capacity']
                out.setdefault(r['name'], {})['wet_tsa'] = w['tsa']['value']
                out[r['name']]['wet_vsa'] = w['vsa']['value']
    return out


QST = load_qst()
# 건조·습윤·Q_st 가 **셋 다** 있는 조성만. 하나라도 없으면 계산이 안 됩니다.
NAMES = sorted(n for n, v in load_wc().items()
               if {'dry_tsa', 'dry_vsa', 'wet_tsa', 'wet_vsa'} <= set(v)
               and n in QST)


def main():
    wc = load_wc()
    vw = vacuum_work()
    dc = drying()
    print('=== 재생 에너지 v3 (kJ / mol CO2) — 가정은 v2 와 동일 ===')
    print('  ⚠️ WC 는 **생산 실현 하나**의 값입니다. 08-27 에 생산 실현이')
    print('     앙상블 평균보다 높다는 것이 확인됐습니다(saIm0583 +1.76 SD,')
    print('     saIm050 +1.16 SD). 조성 간 재생에너지 **순위를 이 표로 매기지')
    print('     마세요** — 배치 산포가 들어 있지 않습니다.')
    print()
    print(f'  Cp {CP_FRAMEWORK} J/(g K) [실측 아님, 감도 {CP_RANGE}] · '
          f'열회수 {HEAT_RECOVERY*100:.0f}% · CO2 회수율 {RECOVERY*100:.0f}% · '
          f'건조 잠열 {dc:.2f} · 진공 일 하한 {vw:.2f}')
    print()
    print(f'  {"조성·방식":<16}{"WC":>8}{"Q_st":>8}{"현열":>8}{"건조":>8}{"합계":>9}')
    print('  ' + '-' * 57)
    rows = []
    for n in NAMES:
        e = {'name': n, 'Q_st': QST[n], 'wc': wc[n]}
        for variant, label in (('wet', '젖은 채'), ('dry', '말려서')):
            v = wc[n].get(f'{variant}_tsa')
            if v is None:
                continue
            sh = sensible(v)
            d_ = dc if variant == 'dry' else 0.0
            tot = QST[n] + sh + d_
            e[f'{variant}_tsa_kJ_per_mol'] = round(tot, 2)
            print(f'  {n + " · " + label:<16}{v:>8.4f}{QST[n]:>8.2f}'
                  f'{sh:>8.2f}{d_:>8.2f}{tot:>9.2f}')
        rows.append(e)
    print()
    print('=== 감도: 골격 비열 (TSA 합계, 젖은 채) ===')
    for cp in (CP_RANGE[0], CP_FRAMEWORK, CP_RANGE[1]):
        line = f'  Cp {cp:<5.1f}'
        for n in NAMES:
            line += f'{QST[n] + sensible(wc[n]["wet_tsa"], cp=cp):>10.1f}'
        print(line + '   (' + ' '.join(NAMES) + ')')
    out = {'generation': 'v3',
           'assumptions': '=== regen_energy.py 와 동일 (Cp 0.9, 회수율 0.5, 열회수 0) ===',
           'vacuum_work_kJ_mol_lower_bound': round(vw, 3),
           'drying_kJ_mol': round(dc, 3), 'rows': rows}
    with open(os.path.join(HERE, 'regen_energy_v3.json'), 'w',
              encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print('\n[OK] regen_energy_v3.json')
    print('주: 감도분석 없이 합계를 인용하지 마세요. Cp 는 실측이 아닙니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
