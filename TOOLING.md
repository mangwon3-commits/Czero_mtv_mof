# 윈도우에서 WSL 안의 계산을 부리는 법 — 실측으로 정리

2026-08-15. 세션 내내 셸 호출이 조용히 깨져서 시간을 잃었습니다.
추측으로 우회하지 말고 **무엇이 왜 깨지는지** 재서 정리했습니다.

## 0. 한 줄 요약

| 도구 | 깨지는 것 | 처방 |
|---|---|---|
| **PowerShell** | `$(...)`, 중첩 따옴표, `\|\|` | **간단한 것만.** `wsl.exe -d Ubuntu -e bash <절대경로.sh>` |
| **Bash (Git Bash)** | **맨 인자로 넘긴 유닉스 절대경로** | 호출 앞에 **`MSYS_NO_PATHCONV=1`** |

## 1. PowerShell 이 깨지는 이유

PowerShell 은 인자를 `wsl.exe` 에 넘기기 **전에 스스로 해석**합니다.

```powershell
wsl.exe -d Ubuntu -e bash -c "echo $(pgrep -c simulate)"
```

`$(...)` 는 **PowerShell 의 부분식**입니다. bash 가 보기 전에 PowerShell 이
`pgrep` 을 실행하려 하고, 윈도우에 그런 명령이 없으니

```
pgrep : The term 'pgrep' is not recognized as the name of a cmdlet...
```

홑따옴표로 바꿔도 소용없었습니다. 실측:

```powershell
wsl.exe -d Ubuntu -e bash -c 'echo "A1: $(pgrep -c simulate)"'
  -> 출력이 "A1" 뿐. 나머지가 통째로 사라짐
```

같은 이유로 이것들이 전부 깨집니다.

- `||`, `&&` — PowerShell 5.1 에 파이프라인 연쇄 연산자가 **없습니다**
- `awk '{print $7}'` — `$7` 이 PowerShell 변수로 먹힘
- heredoc(`<<'EOF'`) — PowerShell 문법이 아님
- `2>/dev/null` — `2>$null` 로 써야 하는데 그러면 bash 가 못 알아봄

**PowerShell 로 bash 한 줄을 넘기려 하지 마세요.** `.sh` 파일에 쓰고 경로만
넘기면 이 문제가 전부 사라집니다 — 넘기는 인자에 `$` 도 따옴표도 없기 때문입니다.

## 2. Bash 도구가 깨지는 이유 — 이건 정반대입니다

Git Bash 는 MSYS2 위에서 돕니다. MSYS2 는 편의를 위해 **유닉스풍 절대경로처럼
보이는 인자를 윈도우 경로로 자동 변환**합니다. WSL 안의 경로에는 그 변환이
항상 틀립니다.

```
wsl.exe -d Ubuntu -e bash /home/mangwon1/mof_project/boost.sh
  -> bash: C:/Program Files/Git/home/mangwon1/mof_project/boost.sh: No such file
```

**범위를 실측으로 분리했습니다.**

| 형태 | 변환되나 |
|---|---|
| `bash /home/x.sh` (**맨 인자**) | ❌ **변환됨 — 깨짐** |
| `bash -c 'wc -l < /home/x.log'` (따옴표 안) | ✅ 멀쩡 |
| `$(...)`, `awk '{print $7}'`, `\|\|`, `&&` | ✅ 멀쩡 |
| 파이프, grep 정규식, 한글 | ✅ 멀쩡 |

**깨지는 것은 맨 인자 경로 하나뿐입니다.** 그런데 그게 스크립트를 실행하는
가장 흔한 형태라 자주 걸렸습니다.

## 3. 확정된 세 패턴 (전부 실측 통과)

```bash
# 1. 스크립트 실행 — 접두 변수
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash /home/mangwon1/mof_project/boost.sh

# 2. 스크립트 실행 — 변수 없이, 따옴표 안으로 넣기
wsl.exe -d Ubuntu -e bash -c 'bash /home/mangwon1/mof_project/boost.sh'

# 3. 복잡한 한 줄 — 접두 변수 + 무엇이든
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -c \
  'echo "완료 $(grep -c ok log)건 / 메모리 $(free -g | awk "NR==2{print \$7}")GB"'
```

## 4. 왜 프로파일로 못 고치나

`~/.bashrc` 와 `~/.bash_profile` 에 `export MSYS_NO_PATHCONV=1` 을 넣어 봤지만
**Claude Code 의 Bash 도구에는 걸리지 않습니다.** 그 도구는 bash 를
**비대화형·비로그인**으로 부르므로 둘 다 읽지 않습니다. 실측 확인:

```
MSYS_NO_PATHCONV=[]  MSYS2_ARG_CONV_EXCL=[]
```

`BASH_ENV` 를 쓰면 비대화형 셸도 파일을 읽지만, 그러려면 **윈도우 사용자 환경
변수를 영구 등록**해야 합니다. 프로젝트 밖 환경을 건드리는 일이라 하지
않았습니다. 필요하면 사람이 판단할 일입니다.

```powershell
# 원한다면 (사용자 판단):
setx MSYS_NO_PATHCONV 1
```

그래도 `~/.bashrc` 는 남겨 뒀습니다 — **사람이 직접 여는 Git Bash 창**에서는
그 설정이 걸립니다.

## 4-1. 커밋 메시지는 **파일**로 넘기세요

`bash -c '...'` 안에 heredoc 으로 긴 메시지를 넣으면, **메시지에 아포스트로피가
하나만 있어도 거기서 홑따옴표 문자열이 끊깁니다.**

```
... van't Hoff ...
        ^ 여기서 -c '...' 가 닫혀 버림
  -> bash: syntax error near unexpected token `('
  -> here-document at line 4 delimited by end-of-file
```

`van't Hoff`, `Rappe's`, 한글 안의 `'` 전부 같은 문제를 냅니다.
**메시지를 파일에 쓰고 `-F` 로 넘기면 인용 문제가 원천적으로 사라집니다.**

```bash
# 메시지는 Write 도구로 파일에 쓴 다음
MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -c \
  'cd /home/mangwon1/mof_project && git commit -F /home/mangwon1/.claude_work/msg.txt'
```

## 5. 곁들여 — 이 프로젝트에서 반복된 셸 함정

`00_Migration/MIGRATION.md` 3절에 전부 있지만, 자주 걸린 것만.

- **돌고 있는 bash 스크립트를 편집하지 마세요.** bash 는 스크립트를 바이트
  오프셋으로 읽어 나가므로, 실행 중에 길이가 바뀌면 엉뚱한 줄을 실행합니다.
  고쳤으면 죽이고 다시 띄우세요.
- **`$(date)` 가 `$?` 를 덮어씁니다.** 종료코드를 먼저 받으세요.
  이걸 놓쳐 OOM 두 건이 "종료코드 0 / 전체 완료" 로 보고됐습니다.
- **`setsid nohup ... < /dev/null &`** 로 띄우세요. 안 그러면 세션이 끝날 때
  같이 죽습니다. (덕분에 클로드가 업데이트로 재시작돼도 계산이 살아남았습니다.)
- **진행 상황을 실행 디렉터리 개수로 세지 마세요.** `run_water.py` 와
  `run_working_capacity.py` 는 결과를 뽑은 뒤 폴더를 지웁니다. 끝난 것일수록
  안 보여서 "시작 0 / 완주 0" 이 나옵니다. **로그를 세세요.**
