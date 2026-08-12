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
$ErrorActionPreference = 'SilentlyContinue'
$log   = 'C:\Users\mangw\.claude_work\wsl_hold.log'
$dist  = 'Ubuntu'
$guard = '/home/mangwon1/.claude_work/ensure_guards.sh'
$hold  = '/home/mangwon1/.claude_work/vm_hold.sh'
$FAST_RETURN_SEC = 30   # 이보다 빨리 반환하면 붙잡기 실패로 본다
$FAILS_BEFORE_SHUTDOWN = 3

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

Log "hold loop started (pid $PID)"
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
