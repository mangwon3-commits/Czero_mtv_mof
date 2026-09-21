# 이어받기가 **중간값을 완주값으로** 받고 있었습니다 (2026-09-21 **14:36**, laptop2 발견 · 데스크탑 수정)

> **근본 결함 6번째 후보입니다.** 유형이 앞의 다섯과 같습니다 — **실패가 결과처럼 보이는 것**(CLAUDE.md §0).
> CLAUDE.md §0 의 목록에 넣을지는 **사용자 판단**입니다. 이 문서가 그 판단에 필요한 자료입니다.

## 1. 무엇이 틀렸나

`run_aryl_gcmc.run_one` 의 이어받기:

    done = glob.glob(os.path.join(d, 'Output','System_0','*.data'))
    if done:
        r = parse(done[0])
        if any(x is not None for x in r):        # <-- 여섯 값 중 **하나라도**
            return name, gas, mode, r, 'cached'

`parse` 는 `(kh, ekh, u, eu, load, eload)` 를 돌려주고 **파일에서 마지막으로 맞은 줄**을 씁니다.
그래서 **사이클이 덜 찬 중간 평균**이 그대로 `cached` 로 나갑니다.

    · 그 행에는 **아무 표지가 없습니다** — `status` 는 `ok` 입니다.
    · 오차는 중간 블록의 것이라 **오히려 더 좁아 보입니다.**
    · 같은 무늬가 09-19 `run_humid_wc.py` 에 있었는데, 그때는 파서가 최종 요약 줄을 요구한다는
      **우연이 보호**였습니다. 여기에는 그 우연이 없습니다.

### 1-2. 신규 실행 경로에도 같은 구멍이 있었습니다 (데스크탑이 덧붙여 찾음)

    subprocess.run([SIMULATE, ...], check=False)     # RASPA 가 죽어도 예외가 안 납니다
    ...
    res = parse(outs[0])
    return name, gas, mode, res, 'ok'                # <-- 관문 없이 'ok'

**RASPA 가 중간에 죽으면 이어받기를 거치지 않고도 중간값이 `ok` 로 나갑니다.** laptop2 가 지적한 것은
이어받기 쪽이지만, 같은 관문이 신규 경로에도 없었습니다.

## 2. 왜 이번 묶음은 안 걸렸나 — **운입니다**

laptop2 가 14:22:27 에 띄웠다가 14:24:32 에 재기동했습니다. 첫 판이 약 **90초** 돌았고 그 사이
RASPA 가 헨리 블록을 **한 번도 안 찍어서** `parse` 가 여섯 값 전부 `None` 을 돌려줬습니다
(`any(...)` 가 False → 이어받지 않음). **1~2분만 더 돌았으면 걸렸습니다.**

laptop2 검사 결과: `cached` 표지 로그 **전수 0건** · 폴더당 `.data` 정확히 1개 ·
모든 `.data` 생성 시각이 재기동 **이후** · `/proc/<pid>/cwd` 로 현재 `simulate` 가 그 폴더를 잡고 있음.
**지금 §AV 묶음에 오염은 없습니다.**

랩탑은 재기동 **전에** 끊긴 폴더 8개를 지웠고(맞는 처리), laptop2 는 재기동 **후**라 폴더가
살아 있는 작업의 것이므로 **지우면 안 됩니다.** 두 기기의 처리가 반대인데 **둘 다 맞습니다.**

## 3. 고친 것

    def finished(path):     # `run_tnf.py:178` 과 **같은 조건**
        return 'Simulation finished' in open(path, errors='ignore').read()

    def primary(mode, r):   # 그 모드가 반드시 내놓아야 하는 값
        return None if r is None else (r[0] if mode == 'widom' else r[4])

    이어받기   if done and finished(done[0]):  r = parse(...);  if primary(mode, r) is not None: -> cached
    신규 실행   if not finished(outs[0]): -> '미완주' ;  if primary(mode, res) is None: -> '값없음'

**값이 아니라 표지가 자입니다.** 끊긴 파일에도 헨리 값은 남아 있으므로(아래 검증) 값의 존재는
완주의 증거가 못 됩니다.

### 3-2. 그리고 그 실패를 받는 쪽도 고쳤습니다 (`run_core_pop.py`)

`run_one` 은 실패 시 `r` 자체를 `None` 으로 돌려줍니다(`미완주`·`timeout`·`no-output`·`값없음`·`다른세션실행중`).
제가 쓴 행 조립이 `elif kc is not None:` 이라 **그 경우를 놓쳐서 값 없는 행이 `status='ok'` 로 남았습니다.**
`else` 로 고치고, 실패 사유(`run_status`)를 행에 같이 남깁니다. **제가 만든 같은 유형의 결함입니다.**

## 4. 검증

    완주 파일   finished=True   · parse 헨리 1.656e-05 · primary(widom) 있음  -> cached (정상)
    끊긴 파일   finished=False  · parse 헨리 1.656e-05(값은 **있음**)
                옛 판정 any(...) = **True**  -> 이것이 cached 로 나갔습니다
                새 판정            -> 이어받지 않음

    행 조립(가짜 실행)  timeout 두 건 -> `둘 다 실패(timeout/timeout)`  · KH 없음 · 선택도 없음
                        미완주 한 건 -> `N2 실패(미완주)`
                        옛 판이었다면 셋 다 `status='ok'` 로 남았습니다.

## 5. 적용 범위와 위험

`run_aryl_gcmc` 를 `import` 하는 것: `run_core_pop` · `run_bridge_core` · `run_candidate_gcmc` ·
`run_gcmc_v2/v3` · `run_working_capacity` · `run_humid_wc` · `run_widom_tnf` · `run_repeat_e5` ·
`run_anchor_zif93` · `srep_run`.

**돌고 있는 프로세스에는 반영되지 않습니다**(CLAUDE.md §6). 재기동할 때 새 코드가 걸립니다 — 그리고
이 변경은 **재기동을 더 안전하게만** 만듭니다:

    · 진짜로 완주한 실행은 표지가 있으므로 **그대로 회수**됩니다. 잃는 것이 없습니다.
    · 중간에 끊긴 실행만 다시 돕니다. **그것이 옳은 동작입니다.**
    · 기존 결과 JSON 은 건드리지 않습니다.

**과거 결과 중 이 결함에 물린 것이 있는지는 이 문서가 답하지 않습니다.** `cached` 로 회수된 행을
소급 검사하려면 실행 폴더가 남아 있어야 하는데 대부분 §7 로 지웠습니다. 남아 있는 것만이라도
검사할 가치가 있는지는 별도 판단입니다.
