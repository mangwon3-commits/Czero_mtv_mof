# WSL VM 을 윈도우 쪽에서 붙잡는다. **이 스크립트는 끝나지 않는다.**
#
# [왜 끝나면 안 되는가 - 2026-08-12 오후에 배운 것]
#   처음에는 5분마다 실행돼 Start-Process 로 홀드를 띄우고 바로 끝나는 형태였다.
#   그러자 홀드가 5분마다 죽었다 (wsl_hold.log 에 "새로 띄움"이 12:45~13:25 동안
#   9번 연속). **예약 작업은 작업 프로세스가 끝날 때 자식까지 작업 개체(job object)
#   째로 종료시킨다.** Start-Process 로 떼어 놔도 소용없다.
#
#   홀드가 죽으면 VM 이 무방비가 되고, ensure_guards.sh 가 띄운 감시견도 같이
#   죽는다. 그 결과 LAMMPS 가 오늘 하루 08:25, 10:35, 11:40, 12:45 네 번 처음부터
#   다시 돌았다.
#
# [해법] 작업 프로세스 자신이 홀드를 붙잡고 안 끝난다. 예약 작업의 중복 실행
#   정책이 IgnoreNew 라, 살아 있는 동안 5분 트리거는 무시되고 죽으면 다음
#   트리거가 다시 띄운다. 그래서 재시작 로직이 따로 필요 없다.
$ErrorActionPreference = 'SilentlyContinue'
$log  = 'C:\Users\mangw\.claude_work\wsl_hold.log'

# 중복 실행 방지는 여기서 한다. 예약 작업의 MultipleInstancesPolicy=IgnoreNew 를
# 걸었는데도 14:06 과 14:07 에 두 개가 떴다. 스케줄러 쪽 정책은 믿을 것이 못 된다.
# 뮤텍스는 프로세스가 죽으면 OS 가 알아서 놓아 주므로 잠금이 남을 걱정도 없다.
$mutex = New-Object System.Threading.Mutex($false, 'Local\ClaudeWslHold')
if (-not $mutex.WaitOne(0)) { exit 0 }
$dist = 'Ubuntu'
$guard = '/home/mangwon1/.claude_work/ensure_guards.sh'
$hold  = '/home/mangwon1/.claude_work/vm_hold.sh'

# 로그는 ASCII 로 쓴다. PS 5.1 의 UTF-8 처리가 한글을 깨뜨려 읽을 수 없었다.
function Log($m) {
    "$(Get-Date -Format 'MM-dd HH:mm')  $m" | Out-File -FilePath $log -Append -Encoding ascii
}
if ((Test-Path $log) -and ((Get-Item $log).Length -gt 200KB)) {
    Get-Content $log -Tail 400 | Set-Content $log -Encoding ascii
}

Log "hold loop started (pid $PID)"

while ($true) {
    # 1) 안쪽 감시 장치를 세운다. 이 호출은 금방 끝난다.
    & wsl.exe -d $dist -e bash $guard 2>&1 | Out-Null

    # 2) VM 을 붙잡는다. vm_hold.sh 는 sleep infinity 라 여기서 막힌다.
    #    VM 이 죽거나 wsl --shutdown 이 걸리면 반환되고, 루프가 다시 건다.
    $t0 = Get-Date
    & wsl.exe -d $dist --exec $hold 2>&1 | Out-Null
    $secs = [int]((Get-Date) - $t0).TotalSeconds
    Log "hold returned after ${secs}s - VM went down, re-establishing"

    # VM 이 즉시 계속 죽는 상황에서 폭주하지 않도록 잠깐 쉰다.
    Start-Sleep -Seconds 10
}
