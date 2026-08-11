# WSL VM 을 윈도우 쪽에서 붙잡고, 안쪽 감시 장치가 살아 있는지 5분마다 확인한다.
#
# [왜 필요한가 - 2026-08-10 의 실패]
#   08-10 16:39 에 vmIdleTimeout=-1 을 적용하고 LAMMPS 를 재실행했는데,
#   17:25:06 에 VM 이 또 꺼졌다 (Hyper-V-VmSwitch 포트 삭제 기록으로 확인).
#   그때 VM 안에서는 wsl_keepalive.sh 가 돌고 있었다. 안쪽의 sleep 루프도,
#   .wslconfig 설정도 막지 못했다.
#
#   더 중요한 것은 복구가 원리상 불가능했다는 점이다. VM 이 꺼지면 안에 있던
#   감시견도 같이 죽는다. 되살릴 주체는 VM 바깥에 있어야 한다. crontab @reboot 은
#   keepalive 만 띄우고 감시견은 안 띄웠기 때문에, 17:25 에 VM 이 다시 떴을 때도
#   LAMMPS 는 39시간 동안 죽은 채 방치됐다.
#
# [해법] 두 가지를 한다.
#   1. wsl.exe 클라이언트 프로세스를 하나 붙잡아 둔다. 안쪽 프로세스와 달리
#      이건 WSL 이 '붙어 있는 세션'으로 세므로 유휴 판정을 실제로 막는다.
#   2. 안쪽 ensure_guards.sh 를 불러 keepalive 와 감시견을 되살린다.
$ErrorActionPreference = 'SilentlyContinue'
$log = 'C:\Users\mangw\.claude_work\wsl_hold.log'

function Log($m) {
    "$(Get-Date -Format 'MM-dd HH:mm')  $m" | Out-File -FilePath $log -Append -Encoding utf8
}

# 로그가 무한히 자라지 않게 한다.
if ((Test-Path $log) -and ((Get-Item $log).Length -gt 200KB)) {
    Get-Content $log -Tail 400 | Set-Content $log -Encoding utf8
}

# 1) VM 을 붙잡는 클라이언트
#    ArgumentList 는 공백으로 이어 붙이므로 bash -c '...' 형태는 인용이 깨진다.
#    (첫 시도가 그래서 즉시 죽었다.) 스크립트 파일로 넘겨 인용 문제를 없앤다.
$hold = Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" |
        Where-Object { $_.CommandLine -like '*vm_hold.sh*' }
if (-not $hold) {
    # 출력 리다이렉트가 반드시 있어야 한다. 예약 작업에는 콘솔이 없는데,
    # 콘솔 없이 띄운 wsl.exe 는 조용히 즉시 죽는다 (08-12 08:20, 08:22 두 번 겪음).
    # 파이프를 붙여 주면 산다.
    Start-Process -WindowStyle Hidden -FilePath 'wsl.exe' -ArgumentList @(
        '-d','Ubuntu','--exec','/home/mangwon1/.claude_work/vm_hold.sh'
    ) -RedirectStandardOutput 'C:\Users\mangw\.claude_work\vm_hold.out' `
      -RedirectStandardError  'C:\Users\mangw\.claude_work\vm_hold.err'
    Log 'VM 홀드 프로세스 없음 - 새로 띄움'
}

# 2) 안쪽 감시 장치
$out = & wsl.exe -d Ubuntu -e bash /home/mangwon1/.claude_work/ensure_guards.sh 2>&1
if ($LASTEXITCODE -ne 0) { Log "ensure_guards.sh 실패 (exit $LASTEXITCODE): $out" }
