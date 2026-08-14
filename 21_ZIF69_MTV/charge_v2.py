"""structures_v2/ 에 PACMAN(DDEC6) 전하를 부여한다 — 재계산 1단계.

[왜 다시 하나 — STRUCTURE_DEFECT.md]
    2026-08-14 에 기존 치환 구조가 전부 깨져 있었던 것이 드러났다. 빌더가 치환기를
    결정구조가 비워 준 방향이 아니라 이상적 프래그먼트가 가리키는 방향에 놓았고,
    ZIF-69 모체 고리가 일그러져 있어(벤조 C–C 1.273 Å, C–Cl 1.982 Å) 치환기가
    이웃 고리 수소를 0.5~0.95 Å 까지 관통했다. 빌더를 고쳐 structures_v2/ 에
    다시 만들었고, 이제 그 위에 전하부터 다시 얹는다.

[대상 — 두 검사를 모두 통과한 것만]
    rebuild_index.json 의 pass=true 만 고른다. **전하 계산은 구조가 깨져 있어도
    숫자를 뱉는다.** 여기서 거르지 않으면 겹친 구조에 전하가 붙어 GCMC 까지
    흘러간다 — 이번 사태가 정확히 그렇게 흘러갔다.
    −CH₃(mbIm)는 아직 탈락 상태라 자동으로 빠진다.

[EQeq 를 쓰지 않는 이유]
    structures_v2/ 의 CIF 에는 빌더가 써 넣은 EQeq 전하가 남아 있다. EQeq 는 공명에
    의한 전하 분리를 못 다루는데 −NO₂ 가 그 대표 사례(N⁺−O⁻ 두 개가 등가 공명)라,
    EQeq 로 계산하면 이 계열 비교의 결론 자체가 무의미해진다.

[자원]
    PACMAN 은 torch CUDA 를 쓴다. 지금 물리 코어는 무치환 모체 습윤 MD 두 작업이
    쓰고 있는데, 이쪽은 GPU 라 서로 방해하지 않는다.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, 'structures_v2')
CHARGED = os.path.join(HERE, 'charged_v2')
INDEX = os.path.join(HERE, 'rebuild_index.json')
RESULT = os.path.join(HERE, 'charged_v2.json')

# 순전하 허용치. PACMAN 은 neutral=True 로 불러도 반올림 잔차가 남는다.
# 이 프로젝트의 기존 기준(5e-5)을 그대로 쓴다.
NET_Q_TOL = 5e-5


def fix_tags(path):
    """PACMAN 출력은 최신 CIF 딕셔너리 태그를 쓰는데 RASPA 2.0.41 은 구 태그만 읽는다."""
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def net_charge(path):
    tot, n = 0.0, 0
    for line in open(path, encoding='utf-8', errors='ignore'):
        p = line.split()
        if len(p) >= 8 and re.match(r'^[A-Z][a-z]?\d*$', p[0]):
            try:
                tot += float(p[-1])
                n += 1
            except ValueError:
                pass
    return tot, n


def main():
    rows = json.load(open(INDEX, encoding='utf-8'))
    targets = [r for r in rows if r.get('pass')]
    skipped = [r for r in rows if not r.get('pass')]

    print(f'검사 통과 {len(targets)}종 / 제외 {len(skipped)}종', flush=True)
    for r in skipped:
        why = r.get('reason') or (f'융합 {r.get("fused_linkers")} / '
                                  f'금지접촉 {r.get("forbidden_contacts")}')
        print(f'  [제외] {r["tag"]:<9} {r.get("group",""):<8} {why}', flush=True)
    print(flush=True)

    os.makedirs(CHARGED, exist_ok=True)
    from PACMANCharge import pmcharge

    done, fail, warn = [], [], []
    for r in targets:
        tag = r['tag']
        final = os.path.join(CHARGED, tag + '_DDEC6.cif')
        if os.path.exists(final):
            q, n = net_charge(final)
            # 재사용 경로에서도 순전하 검사를 **똑같이** 한다. 이 분기만 검사를
            # 건너뛰면, 이어 돌린 실행에서는 경고가 통째로 사라진다.
            flag = ''
            if abs(q) > NET_Q_TOL:
                flag = f'  <-- 순전하 {NET_Q_TOL} 초과'
                warn.append(tag)
            print(f'  [이미있음] {tag:<9} 원자 {n:<4} 순전하 {q:+.6f}{flag}', flush=True)
            done.append(tag)
            continue
        src = os.path.join(STRUCT, f'ZIF69_{tag}.cif')
        if not os.path.exists(src):
            print(f'  [구조없음] {src}', flush=True)
            fail.append(tag)
            continue
        # PACMAN 의 predict() 는 **입력 CIF 를 정규화해 덮어쓴다.** 반드시 사본에서.
        work = os.path.join(CHARGED, tag + '.cif')
        shutil.copy(src, work)
        try:
            pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                             atom_type=True, neutral=True, keep_connect=False)
        except Exception as e:
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
        flag = ''
        if abs(q) > NET_Q_TOL:
            flag = f'  <-- 순전하 {NET_Q_TOL} 초과'
            warn.append(tag)
        print(f'  [ok] {tag:<9} {r.get("group",""):<8} 원자 {n:<4} '
              f'순전하 {q:+.6f}{flag}', flush=True)
        done.append(tag)

    print(f'\n전하 완료 {len(done)}종, 실패 {len(fail)}종', flush=True)
    if warn:
        print(f'순전하 경고 {len(warn)}종: {warn}')
        print('  RASPA 의 Ewald 합이 알짜전하에 민감하므로 GCMC 전에 확인할 것.')
    if fail:
        print('실패:', fail)
    json.dump({'charged': done, 'failed': fail, 'net_charge_warn': warn,
               'excluded': [r['tag'] for r in skipped],
               'source': 'structures_v2', 'note': 'STRUCTURE_DEFECT.md 이후 재계산'},
              open(RESULT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'[OK] {os.path.basename(RESULT)}')
    print('\n다음: run_widom_v2.py (Widom CO2/N2 헨리 상수) -> GCMC 0.15 bar')
    return 0 if done else 1


if __name__ == '__main__':
    sys.exit(main())
