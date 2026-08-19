# C: 압박 해소 — 사용자 복귀(2026-08-21) 후 직접 실행

**보류 이유:** 데스크탑에 윈도우 쪽 원격 경로가 없습니다. Tailscale 미설치,
OpenSSH 서버 없음, 원격 데스크톱 중지. 지금 데스크탑에 닿는 유일한 길인
Claude 원격제어 세션은 **WSL 안에서 돌기 때문에 `wsl --shutdown` 과 함께
죽습니다.** 이사가 중간에 깨지면 되살릴 손이 없어 데스크탑이 통째로 멈춥니다.
2026-08-19 에 사용자가 "복귀 후 직접 정리" 로 결정했습니다.

## 측정값 (2026-08-19 08:xx)

| | 용량 | 여유 |
|---|---|---|
| **C:** | 231 GB | **1.5 GB** (99.4% 사용) |
| **D:** | 932 GB | 598 GB |
| E: | 932 GB | 400 GB |

    vhdx   C:\Users\mangw\AppData\Local\wsl\{258c41b3-4a0c-4696-9f3a-dd8d9f25480b}\ext4.vhdx
           35.4 GiB. 07:35~08:xx 사이 **자라지 않음**
    WSL 안 사용량 32 GB / 1007 GB

**C: 를 먹고 있는 것은 우리가 아닙니다.** vhdx 는 고정인데 C: 여유만 1.9 ->
1.5 GB 로 줄었습니다. 윈도우 업데이트 캐시·복원 지점·페이지파일 쪽입니다.

## 실행 순서 (윈도우 PowerShell, 관리자)

```powershell
schtasks /Change /TN ClaudeWslHold /DISABLE      # 1. 반드시 먼저
wsl --shutdown                                    # 2. 계산이 0일 때만
wsl --export Ubuntu D:\WSL\ubuntu_backup_20260821.tar   # 3. 복구 보험(선택)
wsl --manage Ubuntu --move D:\WSL\Ubuntu          # 4. 본 작업, 10~30분
wsl -d Ubuntu -e true                             # 5. 부팅 확인
schtasks /Change /TN ClaudeWslHold /ENABLE        # 6. 감시견 복구
```

### 1번을 빠뜨리면 실패합니다

`ClaudeWslHold` 예약 작업이 **5분마다 WSL 을 깨웁니다**(`~/.claude_work/
ensure_guards.sh` 를 부르려고). 그런데 `wsl --manage --move` 는 배포판이
멈춰 있어야 합니다. 이사 도중 그 작업이 부팅을 걸면 깨집니다.

**서로 모르는 두 자동장치가 부딪히는 자리입니다.** 08-19 랩탑 L1 실패
(관문은 옳았는데 관문이 세는 대상이 오염됨)와 같은 계열입니다.

### 실패하면

```powershell
wsl --import Ubuntu D:\WSL\Ubuntu D:\WSL\ubuntu_backup_20260821.tar
```

3번 export 를 건너뛰었는데 4번이 깨지면 **복구 수단이 없습니다.** 35 GB 여유가
D: 에 충분하므로 건너뛸 이유가 없습니다.

## 대안 — 급할 때만

C: 가 정말 마르면 이사 대신 **sparse 전환**을 쓰세요. 회수는 4~6 GB 뿐이지만
수십 초에 끝나 취약 구간이 훨씬 짧습니다.

```powershell
wsl --shutdown
wsl --manage Ubuntu --set-sparse true
wsl -d Ubuntu -e true
```

## 하지 말 것

**계산을 `/mnt/d` 에서 돌리지 마세요.** RASPA 는 작은 쓰기를 수없이 하는데
DrvFs 는 네이티브 ext4 보다 훨씬 느리고 권한·대소문자 문제가 붙습니다.
**옮길 것은 작업이 아니라 디스크입니다.**

## 이미 해 둔 것 (셧다운 불필요했던 것들)

- `density_v2/` (324 MB, VTK 70개) -> `/mnt/d/mof_backup/20260819/` 백업.
  CLAUDE.md 7절이 "사본이 없다" 고 적어 둔 그 파일입니다. 이제 있습니다
- `cleanup_for_compact.sh` 대기 모드 — RASPA·xtb 가 0이 되면 수확 끝난 실행
  폴더 3.3 GB 를 지웁니다. C: 를 늘리지는 못하지만 **vhdx 슬랙을 9 GB 대로
  넓혀 남은 창 동안 vhdx 가 더 커질 일이 없게** 합니다
- C: 여유 감시 (1200/1000/800/600/400 MB 선)

## 경보가 울리면 세션이 할 일 (윈도우 권한 없이 가능한 것)

1. 새 계산을 띄우지 않는다
2. WSL 안에서 더 비운다 — conda/pip 캐시 약 6.8 GB (`~/.cache`), 재생성 가능
3. 사용자에게 보고. **`wsl --shutdown` 계열은 원격에서 실행하지 않는다**
