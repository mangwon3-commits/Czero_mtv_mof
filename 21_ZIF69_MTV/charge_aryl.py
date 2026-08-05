"""아릴 치환 계열(−NO₂ / −CH₃ / −Br)에 DDEC6 전하를 부여한다. GCMC 는 별도.

[왜 전하 부여만 떼어냈나]
    charge_and_run.py 는 PACMAN(전하) → Widom → GCMC 를 한 프로세스에서 이어 돈다.
    그런데 이 둘은 쓰는 자원이 완전히 다르다.

        PACMAN  : torch CUDA — GPU 를 쓰고 CPU 는 거의 안 쓴다
        RASPA   : 순수 CPU, 물리 코어 하나를 통째로 점유

    지금 수분 경쟁 20작업이 물리 코어 8개를 전부 잡고 있다. GCMC 를 지금 걸면
    코어를 두고 싸우느라 양쪽이 다 느려지지만, **PACMAN 은 놀고 있는 GPU 를 쓰므로
    지금 돌려도 수분 계산을 방해하지 않는다.** 그래서 직렬 의존을 미리 끊어 둔다.
    수분이 끝나는 순간 GCMC 가 바로 시작될 수 있다.

[대상 — 감사를 통과한 것만]
    aryl_scan_index.json 에서 pass=true 인 것만 고른다. 전하 계산은 구조가
    깨져 있어도 숫자를 뱉기 때문에, 여기서 거르지 않으면 원자 겹침(clash)이 있는
    구조에 전하가 붙어 GCMC 까지 흘러간다. −CH₃ 50% 이상은 clash 6/12/27 개로
    탈락했고, −C≡N 은 전 조성 실패다(빌더가 C-아릴 축으로 회전시키는데 −C≡N 이
    그 축과 일직선이라 치환기가 벤조 고리를 파고든다).

[EQeq 를 쓰지 않는 이유]
    structures/ 의 CIF 에는 빌더가 써 넣은 EQeq 전하가 남아 있다. EQeq 는 공명에
    의한 전하 분리를 못 다루는데, −NO₂ 는 그 대표적인 경우다(N⁺−O⁻ 두 개가
    등가 공명). 여기서 EQeq 를 쓰면 이 계열의 결론 자체가 무의미해진다.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, 'structures')
CHARGED = os.path.join(HERE, 'charged')
INDEX = os.path.join(HERE, 'aryl_scan_index.json')


def fix_tags(path):
    """PACMAN 출력은 최신 CIF 딕셔너리 태그를 쓰는데 RASPA 2.0.41 은 구 태그만 읽는다."""
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def net_charge(path):
    """전하 합. PACMAN 은 neutral=True 로 불렀어도 반올림 잔차가 남을 수 있다."""
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
    idx = json.load(open(INDEX, encoding='utf-8'))
    targets = [r for r in idx if r.get('pass')]
    skipped = [r for r in idx if not r.get('pass')]

    print(f'감사 통과 {len(targets)}종 / 탈락 {len(skipped)}종', flush=True)
    for r in skipped:
        print(f'  [제외] {r["tag"]:<9} {r["group"]:<5} clash={r.get("clash")}', flush=True)
    print(flush=True)

    os.makedirs(CHARGED, exist_ok=True)
    from PACMANCharge import pmcharge

    done, fail = [], []
    for r in targets:
        tag = r['tag']
        final = os.path.join(CHARGED, tag + '_DDEC6.cif')
        if os.path.exists(final):
            q, n = net_charge(final)
            print(f'  [이미있음] {tag:<9} 원자 {n:<4} 순전하 {q:+.6f}', flush=True)
            done.append(tag)
            continue
        src = os.path.join(STRUCT, f'ZIF69_{tag}.cif')
        if not os.path.exists(src):
            print(f'  [구조없음] {src}', flush=True)
            fail.append(tag)
            continue
        # PACMAN 은 입력 CIF 를 건드리므로 반드시 사본에서 돌린다.
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
        print(f'  [ok] {tag:<9} {r["group"]:<5} 원자 {n:<4} 순전하 {q:+.6f}', flush=True)
        done.append(tag)

    print(f'\n전하 완료 {len(done)}종, 실패 {len(fail)}종', flush=True)
    if fail:
        print('실패:', fail)
    with open(os.path.join(HERE, 'aryl_charged.json'), 'w', encoding='utf-8') as f:
        json.dump({'charged': done, 'failed': fail,
                   'excluded': [r['tag'] for r in skipped]}, f,
                  indent=2, ensure_ascii=False)
    print('[OK] aryl_charged.json')
    print('\n다음: 수분 경쟁이 끝나면 run_aryl_gcmc.py (Widom CO2/N2 + 0.15 bar GCMC)')
    return 0 if done else 1


if __name__ == '__main__':
    sys.exit(main())
