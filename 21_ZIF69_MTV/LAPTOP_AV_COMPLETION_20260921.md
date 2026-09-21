# 랩탑 §AV 완주 절차 — **이 파일만 보고 실행할 수 있게** (2026-09-21 15:3x, 랩탑 Melchior)

> **왜 이 파일이 있나**: §AV 는 09-22 08:0x 무렵 끝납니다. 지금 이 기기를 보고 있는 세션이
> 그때까지 살아 있지 않을 수 있습니다. 절차가 대화에만 있으면 사라집니다(CLAUDE.md §8).
> **아래 순서대로만 하면 됩니다.** 각 칸에 "왜" 를 붙여 두었으니 건너뛸 것과 아닌 것이 구분됩니다.

## 0. 지금 무엇이 돌고 있나

    COREPOP_ASSIGN=laptop COREPOP_WORKERS=8, 09-21 14:25:05 착수, 204종 × (Widom CO₂+N₂) = 408작업
    결과 `core_pop_results_laptop.json` (작업마다 갱신) · 실행폴더 `core_pop_runs/`
    로그 `../.claude_work_corepop.out` · 견적 17.7~18.3 h -> **09-22 08:0x 무렵**
    postman 은 사본에서 돎(`~/.mof_postman/postman_laptop.sh`) — 결과를 스스로 master 로 올립니다.

    진행 보기:  grep -cE '^\s*\[' ../.claude_work_corepop.out      # 408 이면 끝
                pgrep -xc simulate                                  # 0 이면 끝

## 1. 완주 확인 (순서 중요 — **폴더를 지우기 전에** 2번을 해야 합니다)

    python3 -c "import json;d=json.load(open('core_pop_results_laptop.json'));\
      print(len([r for r in d['rows'] if r.get('status')=='ok']),'/204')"

204 가 아니면 **부족분이 왜 빠졌는지 적고** 넘어갑니다(등록 §5 P7: 실패는 **대체하지 않고 자리를 비웁니다**).

## 2. ★ 완주 표지 전수 감사 — **반드시, 폴더 삭제 전에**

    python3 check_corepop_finished.py

**왜**: 이 묶음은 `RESUME_ANY_BUG_20260921.md` §1-2 의 **신규 실행 경로 구멍이 살아 있는 옛 코드**로
돕니다(14:25 기동, 파이썬 변경은 도는 프로세스에 안 걸림 — CLAUDE.md §6). RASPA 가 중간에 죽으면
**표지 없이 `status='ok'` 로 남습니다.** 이 검사기가 `.data` 의 `Simulation finished` 를 직접 봅니다.

    불통과 0 · 판정 불가 0   -> 3번으로
    불통과 있음              -> 그 구조만 **새 코드로** 다시 돕니다(아래 명령을 그대로 다시 치면
                                완주분은 표지가 있어 회수되고 끊긴 것만 다시 돕니다):
        COREPOP_ASSIGN=laptop COREPOP_WORKERS=8 setsid nohup \
          ~/miniconda3/envs/czeromof/bin/python -u run_core_pop.py \
          > ../.claude_work_corepop.out 2>&1 < /dev/null &

## 3. 재배분 (§9-1·§9-6) — laptop2 를 돕습니다

    cd ~/mof_project && git pull          # 이제 러너가 안 도니 merge 해도 안전(§6)
    cd 21_ZIF69_MTV && python3 make_handoff.py

관문 셋이 스스로 섭니다. **막히면 그 이유가 맞는 것이니 강행하지 마십시오.**

    own_share_gate   자기 204종 완주 전이면 종료 4
    premise_gate     laptop2 대기열이 NAtoms 순이라는 전제를 laptop2 완주분으로 검증. 깨지면 종료 3
                     (그쪽이 새 코드로 재기동했으면 "꼬리" 가 꼬리가 아니라 정면으로 겹칩니다)
    결과 파일 없음    laptop2 결과 JSON 이 없으면 멈춤 — `git pull` 하고 다시

출력된 명령을 그대로 칩니다. **세 환경변수를 절대 빼지 마십시오:**

    COREPOP_ASSIGN=laptop2 COREPOP_MACHINE=laptop COREPOP_WORKERS=8 \
      COREPOP_PICK=core_pop_handoff.json \
      COREPOP_OUT=core_pop_results_laptop2_by_laptop.json \
      setsid nohup ~/miniconda3/envs/czeromof/bin/python -u run_core_pop.py \
      > ../.claude_work_corepop_hand.out 2>&1 < /dev/null &

    COREPOP_OUT    빼면 laptop2 프로세스와 **같은 파일을 동시에 덮어써 서로의 행을 잃습니다**
    COREPOP_MACHINE 빼면 잰 기기가 laptop2 로 기록됩니다 — **전달자가 측정자로 기록**
    COREPOP_PICK   빼면 laptop2 몫 308종을 통째로 다시 돕니다

## 4. 보고 (우편함 `COMMS/laptop.md`, 그다음 push)

적을 것: 완주 시각·소요 · 204/204 여부와 실패 목록 · **2번 감사 결과** · 3번 착수(꼬리 k종 + 짝 몇 종)

## 5. ★ 지수 적합 — 완주 때가 **유일한** 기회입니다

    구조별 소요를 실행폴더에서 건집니다(`simulation.input` mtime -> `.data` mtime).
    **폴더를 지우기 전에 하십시오.**

**왜 완주 때뿐인가**: 09-21 15:2x 실측으로 **구조 사이 퍼짐이 21 %** 입니다(같은 구조 안 CO₂/N₂ 는 ≤2.9 %,
같은 MOF 의 ASR/FSR 짝은 0.1 %). 즉 적은 구조로 낸 지수는 전부 이 퍼짐에 덮입니다 — 6구조 적합이
b 0.728 ± 0.323 으로 아무것도 못 가린 이유가 그것입니다. **204구조가 모여야 가려집니다.**

    · 정본 지수는 T-BR-1 의 **0.651**(12구조 × 5.8배)입니다. 이것이 저장소의 **유일한 독립 측정**입니다.
    · **경합 배수를 거쳐 적합하지 마십시오** — 배수는 데스크탑 지수를 이미 깔고 있어 순환입니다.
      **자기 절대 시간으로 직접** 적합해야 세 번째 독립 기기가 됩니다.

## 6. 짝 10종의 쓰임 (§9-6) — **검정이지 보정이 아닙니다**

`pair: True` 인 10종은 laptop2 도 이미 돈 구조입니다. 합칠 때 모집단엔 하나만 들어가고 둘은 따로
`pairs` 로 나옵니다. **K_H 비 중앙값이 1.0 이면 기기 항 없음.** 기기 항이 나오면 **그때 따로 등록**합니다 —
지금 보정식을 정하면 결과를 보고 기준을 고치는 것이 됩니다(CLAUDE.md §2).
덤: 같은 구조 짝이라 **시간 비**도 구조가 약분된 형태로 나옵니다 — 랩탑↔laptop2 기기 속도비의
첫 측정이고, 랩탑↔데스크탑은 그것과 데스크탑↔laptop2 의 **이음**으로 지지됩니다(T-RT-1d §3 방식).

## 7. 하지 말 것

    · 결과를 `results_v3.json`·`v3*` 에 섞지 마십시오 — **외부 계열 구조**입니다.
    · 백분위·순위·판정을 내지 마십시오. **수치 전달만** — 판정은 등록 §5·§6 대로 종합자가 냅니다.
    · 고정값(사이클·힘장·CO₂/N₂ 정의·전하·Ewald·컷오프)을 바꾸지 마십시오.
    · **러너가 도는 동안 수동 `git merge`/`git pull` 금지**(CLAUDE.md §6) — 09-21 15:1x 에 제가
      이것을 어겨 도는 결과 JSON 에 충돌 표시가 박혔습니다. 꼭 한 경로만 필요하면
      `git checkout origin/master -- <경로>` 를 쓰십시오.
    · 실행폴더는 **2번과 5번을 마친 뒤에** 지우십시오.

## 8. 읽을 것

    COREPOP_REGISTRATION_20260921.md   등록(자료 0건) — 예측 P1~P7 과 사용 제한 (ㄱ)~(ㅁ)
    BRIDGE_CORE_RESULT_20260921.md     왜 이 일이 생겼는지(T-BR-1 철회)
    RESUME_ANY_BUG_20260921.md         2번 감사가 필요한 이유
    COMMS/laptop.md 09-21 절            오늘의 경위 전부
