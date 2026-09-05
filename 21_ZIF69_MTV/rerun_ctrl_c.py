"""(다) 재실행 — 분자(`Hw none`) + 분모(현행)를 **같은 배치**로.

[왜 다시] 첫 실행에서 지역 힘장이 **안 먹었습니다**. `<rundir>/UFF_MOF/` 에 사본을
     두면 RASPA 가 안 봅니다 — `$RASPA_DIR/share/raspa/forcefield/` 를 봅니다.
     **등록된 확인 조건(`Hw-Hw` eps)이 그걸 잡았고**, 잡았기 때문에 잘못된 `D` 를
     안 냈습니다. 연무시험(10사이클)으로 새 경로가 먹는 것을 **띄우기 전에** 확인:
         Hw-Hw [ZERO_POTENTIAL] · Ow-Hw [ZERO_POTENTIAL] · Ow-Ow 불변 · 순전하 0

[판정] 기준은 `TB2_CONTROLS_20260905.md` (다) 그대로. **바뀐 것은 실행 방법뿐입니다.**
"""
import json, os, socket, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tb2_ext as E, run_tb2_water_kh as T


def job(local_ff):
    return E.run_water_ff('base', local_ff)


if __name__ == '__main__':
    with Pool(2) as p:
        num, den = p.map(job, [True, False])
    tag = socket.gethostname().lower()
    f = os.path.join(T.OUT, f'widom_control_hwnone_{tag}.json')
    out = {'tag': tag, 'cycles_init': T.INIT, 'cycles_production': T.CYCLES,
           'WARN': '진단 전용. 지역 힘장 사본(Hw none/Lw none). 규약 힘장이 아니다.',
           'note': '1차 실행은 지역 힘장이 안 먹어 무효(확인 조건이 잡음). '
                   'RASPA_DIR 트리로 재실행.',
           'rows': [num], 'denominator_rows': [den]}
    json.dump(out, open(f, 'w'), ensure_ascii=False, indent=2)
    for lbl, r in (('분자 Hw-none', num), ('분모 현행', den)):
        print(f"  [{'ok' if r['ok'] else '실패'}] {lbl:14s} K_H {r['KH_water']}  "
              f"HwHw {r['HwHw_eps']}  적용 {r['ff_applied']}", flush=True)
    if num['ok'] and den['ok']:
        D = den['KH_water'] / num['KH_water']
        rel = ((den['KH_water_err']/den['KH_water'])**2
               + (num['KH_water_err']/num['KH_water'])**2) ** 0.5
        print(f"  **D = {D:.3f}**  상대± {rel*100:.1f}%", flush=True)
    print(f'-> {f}', flush=True)
