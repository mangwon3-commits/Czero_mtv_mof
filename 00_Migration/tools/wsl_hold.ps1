# WSL VM 을 윈도우 쪽에서 붙잡는다. **이 스크립트는 끝나지 않는다.**
#
# [왜 끝나면 안 되는가 - 2026-08-12 오후]
#   처음에는 5분마다 실행돼 Start-Process 로 홀드를 띄우고 바로 끝나는 형태였다.
#   그러자 홀드가 5분마다 죽었다. 예약 작업은 작업 개체(job object)로 자식을 묶어
#   두므로 Start-Process 로 떼어 놔도 소용없다. 작업 프로세스 자신이 붙잡아야 한다.
#
# [왜 자가 복구가 필요한가 - 2026-08-12 16:41]
#   OOM 이 dbus-daemon 을 죽이자 WSL 배포판이 통째로 먹통이 됐다. 그 뒤로
#   `wsl.exe --exec` 이 **0초 만에 반환**하는 상태가 계속됐다. 다시 거는 것만으로는
#   절대 안 풀린다 — 10초마다 재시도하며 20분을 허비했다.
#   이 상태를 푸는 유일한 방법은 `wsl --shutdown` 이다.
#
#   더 나쁜 것은 이때 세션의 셸 도구까지 같이 죽는다는 점이다. 작업 디렉터리가
#   \\wsl.localhost\Ubuntu\ 라서, VM 이 없으면 PowerShell 도 bash 도 못 뜬다.
#   즉 **사람이든 에이전트든 셸로는 손을 쓸 수 없다.** 복구는 이 예약 작업 안에
#   들어 있어야 한다.
# [2026-08-28 랩탑이 잡은 함정 - 이 스크립트를 다른 기기에 그대로 두면
#  **남의 계산을 죽입니다**]
#
#   경로 셋이 데스크탑(mangw / mangwon1)에 하드코딩돼 있었습니다. 다른 기기에서는
#   $hold 가 없으므로 `wsl.exe --exec` 이 **0초 만에 반환**하고, 그것이 아래
#   자가 복구의 발동 조건과 정확히 같습니다. 즉 **30~40초 만에 wsl --shutdown**
#   이 돕니다.
#
#   66행의 "이 상태에서는 도는 계산이 어차피 없으므로 잃을 것이 없다" 가
#   **거짓이 되는 경로**입니다. 원래 그 문장은 "dbus 가 죽어 아무것도 못 돈다"
#   를 뜻했는데, **경로가 없어도 같은 증상**이 나옵니다. 증상이 같다고 원인이
#   같은 것이 아닙니다.
#
#   08-19 relax_fixcell.py 가 /home/mangwon1/.../xtb 를 박아 랩탑에서 죽은 것과
#   같은 형태인데, 그때는 자기만 죽었고 **이것은 남의 계산까지 죽입니다.**
#
#   고친 것 둘:
#     (1) 경로를 현재 사용자에서 유도. 환경변수로 덮을 수 있게 둠
#     (2) 기동 시 경로를 확인하고 **없으면 루프에 들어가지 않고 종료**.
#         아무것도 안 하는 홀드가 wsl --shutdown 을 도는 홀드보다 낫습니다
#     (3) shutdown 직전에 **도는 계산을 세고, 있으면 안 죽입니다**
$ErrorActionPreference = 'SilentlyContinue'
$dist = 'Ubuntu'
if ($env:CLAUDE_WSL_DIST) { $dist = $env:CLAUDE_WSL_DIST }
$log = Join-Path $env:USERPROFILE '.claude_work\wsl_hold.log'
if ($env:CLAUDE_HOLD_LOG) { $log = $env:CLAUDE_HOLD_LOG }

# 배포판 안 홈은 물어봅니다 - 기기마다 사용자명이 다릅니다.
$lxhome = $env:CLAUDE_WSL_HOME
if (-not $lxhome) { $lxhome = (& wsl.exe -d $dist -e sh -c 'echo -n $HOME' 2>$null) }
# 못 물어봤으면 **추측하지 않습니다.** /root 로 떨어뜨리면 경로가 틀린 채로
# 루프에 들어가고, 그것이 바로 08-28 에 막으려는 그 경로입니다.
if (-not $lxhome) {
    Log "!! WSL home lookup failed - exiting. (set CLAUDE_WSL_HOME to override)"
    exit 1
}
$guard = "$lxhome/.claude_work/ensure_guards.sh"
$hold  = "$lxhome/.claude_work/vm_hold.sh"

$FAST_RETURN_SEC = 30   # 이보다 빨리 반환하면 붙잡기 실패로 본다
$FAILS_BEFORE_SHUTDOWN = 3

# 계산으로 볼 프로세스. 하나라도 있으면 wsl --shutdown 을 하지 않습니다.
# CLAUDE.md §4: `pgrep -f` 는 **자기 명령줄에 매칭**됩니다. 실측으로 확인 -
# 계산 7건일 때 `pgrep -f` 는 11 을 냈고 `ps -eo comm=` 는 7 을 냈습니다.
# 자기 매칭이 있으면 이 관문이 **항상 참**이 되어 자가 복구가 영영 안 돕니다.
$BUSY_RE = '^(simulate|lmp_serial|lmp|network|xtb)$'

function Log($m) {
    "$(Get-Date -Format 'MM-dd HH:mm')  $m" | Out-File -FilePath $log -Append -Encoding ascii
}
if ((Test-Path $log) -and ((Get-Item $log).Length -gt 200KB)) {
    Get-Content $log -Tail 400 | Set-Content $log -Encoding ascii
}

# 이전 판(뮤텍스 이름이 다르다)이 아직 돌고 있으면 정리한다. 그쪽에는 자가 복구가
# 없어 영원히 0초 반환만 반복한다.
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.CommandLine -like '*wsl_hold.ps1*' -and $_.ProcessId -ne $PID } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# 중복 실행 방지. 예약 작업의 MultipleInstancesPolicy=IgnoreNew 를 걸었는데도
# 두 개가 뜬 적이 있어(08-12 14:06, 14:07) 여기서 직접 막는다.
$mutex = New-Object System.Threading.Mutex($false, 'Local\ClaudeWslHold2')
if (-not $mutex.WaitOne(0)) { exit 0 }

# [2026-08-28] 기동 관문 - 경로가 없으면 **루프에 안 들어갑니다.**
# 없는 경로로 루프를 돌면 30~40초 만에 wsl --shutdown 이 발동합니다.
& wsl.exe -d $dist -e test -f $guard 2>&1 | Out-Null
$okGuard = $LASTEXITCODE
& wsl.exe -d $dist -e test -f $hold 2>&1 | Out-Null
$okHold = $LASTEXITCODE
if (($okGuard -ne 0) -or ($okHold -ne 0)) {
    Log "!! path missing - guard rc=$okGuard hold rc=$okHold"
    Log "!! not entering loop. create the two files first."
    exit 1
}

Log "hold loop started (pid $PID, dist=$dist, home=$lxhome)"
$fails = 0

while ($true) {
    # 1) 안쪽 감시 장치를 세운다. 금방 끝난다.
    & wsl.exe -d $dist -e bash $guard 2>&1 | Out-Null

    # 2) VM 을 붙잡는다. vm_hold.sh 는 sleep infinity 라 여기서 막힌다.
    $t0 = Get-Date
    & wsl.exe -d $dist --exec $hold 2>&1 | Out-Null
    $secs = [int]((Get-Date) - $t0).TotalSeconds

    if ($secs -lt $FAST_RETURN_SEC) {
        $fails++
        Log "hold returned after ${secs}s (연속 실패 $fails)"
    } else {
        $fails = 0
        Log "hold returned after ${secs}s - VM went down, re-establishing"
    }

    # 3) 자가 복구. 붙잡기가 연달아 즉시 실패하면 배포판이 먹통인 것이므로
    #    `wsl --shutdown` 으로 판을 접었다 다시 편다. 이 상태에서는 도는 계산이
    #    어차피 없으므로 잃을 것이 없다.
    if ($fails -ge $FAILS_BEFORE_SHUTDOWN) {
        # [2026-08-28] 죽이기 전에 **도는 계산을 셉니다.**
        # 원래 주석이 "이 상태에서는 도는 계산이 어차피 없다" 를 가정했는데,
        # 그 가정이 틀리는 경로가 있습니다(위 헤더). 세어서 있으면 안 죽입니다.
        $busy = (& wsl.exe -d $dist -e sh -c "ps -eo comm= | grep -cE '$BUSY_RE'" 2>$null)
        if ($busy -and ([int]$busy) -gt 0) {
            Log "!! shutdown 조건이나 계산 $busy 건이 돌고 있음 - **죽이지 않습니다.** 사람이 볼 것"
            $fails = 0
            Start-Sleep -Seconds 60
            continue
        }
        Log "배포판이 먹통으로 판단됨 - wsl --shutdown 실행"
        & wsl.exe --shutdown 2>&1 | Out-Null
        Start-Sleep -Seconds 25
        & wsl.exe -d $dist -e true 2>&1 | Out-Null
        Start-Sleep -Seconds 10
        Log "wsl --shutdown 후 재기동 시도함"
        $fails = 0
    }

    Start-Sleep -Seconds 10
}
