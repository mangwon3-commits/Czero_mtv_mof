# postman.sh — 세션 없이 도는 우편배달부 (2026-09-19 등록 · 15:0x 데스크탑 기동으로 세 기기 전부 가동)

CLAUDE.md §8 대로 **쓰기 전에 파일로** 남깁니다. 대화에만 있으면 다른 기기 세션은
이 말을 모릅니다.

## 왜

09-12~09-16 의 나흘 공백이 계산이 아니라 **전달**에서 났습니다(ASSIGN_20260907 §640:
"완주와 전달 사이가 약한 고리"). 09-18~19 에도 §AJ 6시간 · §AK ⑥ 7시간 · ⑤ 관문 실패
하룻밤을 아무도 몰랐습니다. 세션이 닫히면 전달이 멈춥니다. 그래서 세션과 무관하게
도는 배달부를 둡니다.

## 설계 (사용자 09-19 지시문 그대로)

5분마다 ① fetch 해 새 커밋을 받은편지함에, ② 저장소 bash 스크립트/러너가 안 돌 때만
master ff-pull(랩탑류는 merge), ③ 결과 파일 자동 커밋·푸시, ④ master 기기는 다른
브랜치의 결과 파일을 반입, ⑤ simulate 수 변화와 러너 로그의 `rc=`/`Traceback`/`OOM`
을 받은편지함에, ⑥ 새 줄이 생기면 `.postman_flag` touch.

**`pkill -f` 없음. 판정·착수·문서 편집 없음.** (CLAUDE.md §4 의 `pkill -f` 함정,
§2 의 판정 규율을 건드리지 않게 만든 설계입니다.)

## 기동

    cd ~/mof_project && git pull && setsid nohup bash postman.sh <기기이름> > /dev/null 2>&1 < /dev/null &

`<기기이름>` 은 `desktop` · `laptop` · `laptop2`. 받은편지함은 기기마다 따로
(`.postman_inbox_<기기>`), 로그는 `.postman_<기기>.log`.

세우기: `ps -eo pid,args | grep -v grep | grep postman.sh` 로 **PID 를 먼저 보고**
PID 로 죽이십시오(§4).

## 세션은 이렇게 깨어난다

    Monitor 도구:  tail -n0 -F .postman_inbox_<기기> | grep --line-buffered .      (세션 수명 동안 지속)
    보조: CronCreate 로 매시 23분 "받은편지함·bgstate 훑고 할 일 하기" 프롬프트(세션 한정, 7일 자동 만료)
    받은편지함 한 줄 = 사건 하나. 세션은 그 줄을 읽고 CLAUDE.md §9 대로 다음 배정을 띄우거나 판정을 쓴다.

## 배달부가 하는 것 / 안 하는 것

    한다   fetch·새 커밋 알림 · master ff-pull(데스크탑)/merge(랩탑류) · 결과 파일 자동 커밋·푸시 ·
           (master 기기) 다른 브랜치 결과 파일 반입 · simulate 수 변화·러너 로그의 rc=/Traceback/OOM 알림
    안 한다  계산 착수 · 판정 · 문서 편집 · 돌고 있는 bash 스크립트/러너가 있을 때의 pull(§6) · pkill -f(§4)
    결과 파일 = v3w_*/ JSON·JSONL, results_*.json, risk_results*.json, relax_v3/*_relaxed.cif,
           charged_v3/*_DDEC6.cif, relax_v3_judged.json, risk_v3sub_index.json, COMMS/*.md, watchdog.log,
           tnf_results_*.json, tnf_widom_*.json
    실패는 받은편지함에 `!!` 로 적고 멈추지 않는다.

## 09-19 15:4x 판 — (5) ③ 자동 커밋이 안 맞는 글롭 하나에 통째로 죽음(rc=128, 로그 없음) → 패턴별 add. **이 판으로 세 기기 재기동.**

## 09-19 15:0x 판 — 두 기기가 첫 주기에 잡은 결함 셋을 고쳤습니다

    (1) 랩탑   crontab watchdog.sh 가 매시 watchdog.log 에 한 줄 붙임 → tracked_dirty 영구 교착
               → RESULT_PATTERNS 에 watchdog.log 추가. 같은 주기에 커밋돼 스스로 풀립니다.
    (2) laptop2 repo_bash_running 이 bash 만 봄 → 파이썬 러너 직접 기동 기기에서 5분마다 pull, charged_v3 CIF 가
               러너 밑에서 바뀔 경로 → runner_running() 추가(simulate 또는 run_*.py 살아 있으면 pull 건너뜀).
    (3) 둘 다   첫 틱에 09-03 tb5_chain.log 의 옛 !! 줄 범람 → 기동 시 sz_* 를 현재 크기로 미리 채움.

    (6) **④ 반입이 master 를 되돌릴 수 있었음(15:5x).** `git diff last cur` 두 점은 브랜치가 병합해 들여온 master 커밋의 파일까지 집어
               브랜치의 더 오래된 판을 master 에 덮어썼습니다(e9f52b5 가 watchdog.log 한 줄을 지움). 지금은 `git log cur ^last ^HEAD` 로
               **master 에 없는 커밋이 만진 파일만** 반입합니다. 결과 JSON 은 기기별 파일이라 실제 피해는 watchdog.log 뿐이었습니다.

**띄우기 전에 `git status --porcelain -uno` 를 한 번 보십시오**(laptop2 교훈 — 앞단 산출물
`charged_v3.json`·`relax_v3_results.json` 이 RESULT_PATTERNS 밖이라 dirty 로 남아 pull 을 막았습니다).

**이미 도는 기기(랩탑·laptop2, 14:34 판)**: 돌던 bash 는 옛 판을 읽습니다(§6, 바이트 오프셋).
`git pull`(또는 merge 로 이 파일이 오면) 뒤 **PID 로 세우고 다시 띄우십시오.** 급하지 않습니다 —
옛 판도 보내기는 정상이고, (1)(2) 는 그 기기에서 이미 손으로 막아 두었습니다.

## SendMessage 는 보조

상대 세션이 살아 있을 때만 닿고, 닿아도 읽혔는지 안 알려 줍니다(09-18 §AK 오배송 사례).
급한 지시는 SendMessage + 우편함 둘 다.

## 먼저 알고 띄우십시오 (검토 의견 둘 — 랩탑 판 그대로)

1. **반쯤 쓰인 JSON 을 집을 수 있습니다.** ③ 의 `git add` 는 러너가 결과 JSON 을
   쓰는 도중에도 걸립니다. 러너가 임시파일에 쓰고 rename 하지 않는다면 잘린 JSON 이
   커밋될 수 있습니다. 받은편지함의 `[푸시]` 줄을 보고 **JSON 이 파싱되는지** 한 번은
   확인하십시오.
2. **자동 커밋은 되돌리기 쉬운 쪽으로만 합니다.** 이 스크립트는 결과 파일 경로만
   건드리고 문서·러너는 건드리지 않습니다. 그 경계를 넓히지 마십시오 — 넓히는 순간
   "누가 고쳤는지 모르는 문서" 가 생깁니다.

`.postman_*` 산출물은 `.gitignore` 에 넣었습니다(받은편지함·로그·상태·플래그).

## 지금 상태

    데스크탑   09-19 15:5x 재기동((6) 판) — master, ④ 반입 담당
    랩탑       09-19 14:34 기동(14:34 판, PID 612430) — 재기동 권고
    laptop2    09-19 14:34 기동(14:34 판, PID 426) — 재기동 권고
