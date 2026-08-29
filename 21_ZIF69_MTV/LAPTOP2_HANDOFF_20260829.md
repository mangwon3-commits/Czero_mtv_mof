# laptop2 인수 문서 — 앱 크래시 대비 백업 루트 (2026-08-29 02:18)

앱(데스크탑 Claude)이 죽어도 **CLI 에서 같은 세션을 그대로 이어받기** 위한 문서.
이 파일은 상태가 바뀔 때마다 갱신한다. 최신 정본은 항상 git 의 이 파일이다.

## 1. 즉시 이어받기 — ⚠ CLI 는 지금 **작동하지 않는다** (2026-08-29 검증)

**하지 말 것:** 터미널에서 그냥 `claude --resume` — 08-28 에 시도해 **403 무한
루프로 토큰 40% 를 태웠다.** 원인은 확인됐다:

    PATH 상의 claude            없음
    설치된 claude.exe           앱 폴더 안 claude-code/2.1.246, 2.1.247 뿐
    ~/.claude/.credentials.json 없음   <- CLI 가 쓸 자격증명이 아예 없다

저 exe 는 **앱이 토큰을 주입해 주는 전제**로 동작한다. 단독 실행하면 인증이
없어 API 가 403 을 주고 재시도 로직이 무한 루프에 빠진다.

**CLI 를 쓰려면 먼저 독립 설치 + 로그인이 필요하다** (사용자가 직접):

    1) 공식 설치본으로 Claude Code 를 별도 설치 (앱 내장 사본 말고)
    2) `claude login` 으로 브라우저 OAuth 인증  -> ~/.claude/.credentials.json 생성
    3) 그 다음에야  cd /d D:\Claude_MOF && claude --resume

**로그인은 반드시 사용자가 한다.** 에이전트가 대신 하지 않는다.

## 2. 현재 상태 스냅샷 (2026-08-29 02:18 기준)

- **계산: 배정 4건 전부 완주** (00:07 ALLDONE). 수치·판정은 COMMS/laptop2.md
  02:18 글이 정본: nbIm025 유지율 87.60±2.33 / nbIm075 77.83±2.76,
  판정 4-2 d=9.77≥8.68 → 고원 격하(단 깨지기 쉬움 f), 경합 분리 전제 소실.
- **게시·푸시 완료**: 이 커밋. 데스크탑 회신 대기 사항 없음(기록용).
- WSL 에 실행 중 계산 없음. 러너 로그 ~/.claude_work/, 이벤트 nb_events.tsv.

## 3. 진행 중인 백그라운드 작업 (끊겼으면 이렇게 재개)

**CALF-20 앵커 전문 대조 워크플로** (Opus 읽기 5기, 종합은 주 에이전트 몫):

- 스크립트: `C:\Users\LeeHK\.claude\projects\D--Claude-MOF\ec05659d-160d-40a7-84f8-fa858216547e\workflows\scripts\calf20-anchor-verify-wf_6f9f0c42-fca.js`
- 재개: Workflow 도구에 `{scriptPath: 위 경로, resumeFromRunId: "wf_03763dde-176"}`
- 완료 후 할 일: 주 에이전트(Fable)가 결과를 V-1(대조표)/V-2(결정 질문:
  CALF-20 분말 RH80–90 평형 <0.8 mmol/g?)/V-3(앵커 병기 단서)/V-4(출처)로
  종합 → 우편함 부록 게시 + 커밋 + HKHOME-desktop_now 통지.
  등급 상향 금지(개별 결과의 등급 존중).

## 4. 남은 일 (우선순위순)

1. 워크플로 완료 → 종합 → 부록 게시 (위 3).
2. 데스크탑 내일 통합 라운드 추적: 정정 3건 반영, r3 등록 판정, 새 배정.
3. 앱 조기 감지 재무장 (scratchpad appwatch.sh — 세션 죽으면 같이 죽으므로
   세션 재개 때마다 Monitor 로 다시 걸 것. GPU 감시 줄 추가됨).

## 5. 크래시 이력·진단 (이 기기, 2026-08-29)

| 시각 | 유형 | 증거 |
|---|---|---|
| 01:43:39 | Application Hang 1002 (행 4건째) | 이벤트 로그, WER MoAppHang |
| 01:49:29 | **GPU 프로세스 크래시** (신규 유형) | main.log 마지막 줄 `GPU process gone: crashed, exitCode 101457950`, 이후 02:11 재시작까지 무기록 |

- 이번 두 건 모두 **stealth-update 전조 없음** (누적 3건 그대로, 마지막 08-28 00:54).
- 두 건 모두 OS 재부팅 없음, WSL(17h+ 연속)·계산 데이터 무사.
- 권고: 앱 설정에서 **하드웨어 가속(GPU 가속) 끄기** 검토 — GPU 프로세스
  크래시 유형에 대한 표준 완화책. 직전 메모리 tree_rss 2.5 GB 로 다소 높았음.

## 6. 통신망

- 우편함: `21_ZIF69_MTV/COMMS/laptop2.md` (이 기기 전용 필자), 규약 COMMS.md.
- 데스크탑 직통: 세션 목록의 `HKHOME-desktop_now`. 계산 중 pull 금지(fetch+show).
- 브랜치: `laptop2-20260825`, 신원 skyjun <mangwon3@gmail.com>.
