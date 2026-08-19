"""v3 1단계 — 이완된 구조에 PACMAN(DDEC6) 전하를 다시 얹는다.

[왜 전하를 다시 계산하나]
    이완으로 원자가 움직였습니다. C-H 가 0.949 -> 1.077 로 0.13 A 길어졌고
    아릴-치환기 결합도 바뀌었습니다. **전하는 기하의 함수**이므로 v2 전하를
    이완된 구조에 재사용하면 서로 맞지 않는 짝이 됩니다.

    AUDIT_20260814.md 가 C-H 정규화만으로 K_H 가 4.7~6.8% 움직인다고 쟀는데,
    그 경로의 절반이 전하였습니다.

[관문 — relax_v3_judged.json 의 pass 만]
    charge_v2.py 가 rebuild_index.json 의 pass 를 봤듯이, 여기서는 이완 판정을
    봅니다. **전하 계산은 구조가 깨져 있어도 숫자를 뱉습니다.** 여기서 거르지
    않으면 깨진 구조에 전하가 붙어 GCMC 까지 흘러갑니다 -- 2026-08-14 사태가
    정확히 그렇게 흘러갔습니다.

    판정 파일은 judge_relax_v3.py 가 만든 것을 씁니다. 배치가 스스로 남기는
    relax_v3_results.json 은 방향족 C-C 를 잘못 세던 판본이라 쓰지 않습니다.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from charge_v2 import fix_tags, net_charge, NET_Q_TOL   # noqa: E402

RELAXED = os.path.join(HERE, 'relax_v3')
CHARGED = os.path.join(HERE, 'charged_v3')
JUDGED = os.path.join(HERE, 'relax_v3_judged.json')
RESULT = os.path.join(HERE, 'charged_v3.json')

# [대조군을 잊지 말 것]
#   structures_v2/ 에는 무치환 모체가 없습니다. 모체는 빌더 결함의 대상이
#   아니었으므로 재구축하지 않았고(STRUCTURE_DEFECT.md 7절), v2 에서는 v1 의
#   charged/base_DDEC6.cif 를 그대로 가져다 썼습니다.
#
#   그런데 v3 에서는 **모체도 이완됩니다.** 오히려 모체가 이완 방법을 판정한
#   바로 그 구조입니다(relax_fixcell). 이것을 빼면 v3 에 기준선이 없어서
#   "치환이 얼마나 바꿨나" 를 말할 수 없습니다. 명시적으로 넣습니다.
PARENT = os.path.join(HERE, 'relax_fixcell', 'base_relaxed_gfnff_fixcell.cif')


def main():
    if not os.path.exists(JUDGED):
        print(f'  판정 파일이 없습니다: {JUDGED}')
        print('  judge_relax_v3.py 를 먼저 도세요.')
        return 1
    j = json.load(open(JUDGED, encoding='utf-8'))
    ok = [r for r in j['rows'] if r.get('pass')]
    bad = [r['name'] for r in j['rows'] if not r.get('pass')]
    print(f'이완 판정 통과 {len(ok)}종 / 미달 {len(bad)}종', flush=True)
    for n in bad:
        print(f'  [제외] {n}', flush=True)
    if not ok:
        return 1

    os.makedirs(CHARGED, exist_ok=True)

    # 모체를 목록 맨 앞에 둡니다. 연기 시험이 이것 하나로 돌기 때문입니다.
    jobs = []
    if os.path.exists(PARENT):
        jobs.append(('base', PARENT))
        print('  대조군: 이완된 무치환 모체를 포함합니다', flush=True)
    else:
        print(f'  !! 이완된 모체가 없습니다: {PARENT}', flush=True)
        print('     대조군 없이 진행하면 v2 와 비교할 기준선이 사라집니다.', flush=True)
    for r in ok:
        # relax_v3 의 이름은 ZIF69_<tag> 입니다. v2 와 태그 규약을 맞춥니다.
        jobs.append((r['name'].replace('ZIF69_', ''),
                     os.path.join(RELAXED, f'{r["name"]}_relaxed.cif')))

    done, fail, warn = [], [], []
    for tag, src in jobs:
        final = os.path.join(CHARGED, tag + '_DDEC6.cif')
        if os.path.exists(final):
            q, n = net_charge(final)
            flag = f'  <-- 순전하 {NET_Q_TOL} 초과' if abs(q) > NET_Q_TOL else ''
            if flag:
                warn.append(tag)
            print(f'  [이미있음] {tag:<9} 원자 {n:<4} 순전하 {q:+.6f}{flag}', flush=True)
            done.append(tag)
            continue
        if not os.path.exists(src):
            print(f'  [구조없음] {src}', flush=True)
            fail.append(tag)
            continue
        # PACMAN 이 없는 기기에서도 전부 [이미있음]이면 여기 도달하지 않는다.
        from PACMANCharge import pmcharge
        # PACMAN 의 predict() 는 입력 CIF 를 덮어씁니다. 반드시 사본에서.
        work = os.path.join(CHARGED, tag + '.cif')
        shutil.copy(src, work)
        try:
            pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                             atom_type=True, neutral=True, keep_connect=False)
        except Exception as e:                                  # noqa: BLE001
            print(f'  [전하실패] {tag}: {type(e).__name__}: {e}', flush=True)
            fail.append(tag)
            os.path.exists(work) and os.remove(work)
            continue
        pac = work.replace('.cif', '_pacman.cif')
        if not os.path.exists(pac):
            print(f'  [출력없음] {tag}', flush=True)
            fail.append(tag)
            continue
        shutil.move(pac, final)
        t = open(final, encoding='utf-8').read()
        t = re.sub(r'^data_\S+', f'data_{tag}_DDEC6', t, count=1, flags=re.M)
        open(final, 'w', encoding='utf-8').write(t)
        fix_tags(final)
        os.path.exists(work) and os.remove(work)
        q, n = net_charge(final)
        flag = f'  <-- 순전하 {NET_Q_TOL} 초과' if abs(q) > NET_Q_TOL else ''
        if flag:
            warn.append(tag)
        print(f'  [ok] {tag:<9} 원자 {n:<4} 순전하 {q:+.6f}{flag}', flush=True)
        done.append(tag)

    print(f'\n전하 완료 {len(done)}종, 실패 {len(fail)}종', flush=True)
    if warn:
        print(f'순전하 경고 {len(warn)}종: {warn}')
    json.dump({'charged': done, 'failed': fail, 'net_charge_warn': warn,
               'excluded': bad, 'source': 'relax_v3 (GFN-FF, 셀 고정)',
               'note': 'v3 — 이완된 기하 위에서 전하를 다시 계산'},
              open(RESULT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'[OK] {os.path.basename(RESULT)}')
    return 0 if done else 1


if __name__ == '__main__':
    sys.exit(main())
