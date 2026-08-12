# ClaudeWslHold 예약 작업을 XML 로 다시 등록한다.
#
# schtasks 의 명령줄 형태로는 아래 두 가지를 못 준다. 그런데 이 둘이 핵심이다.
#   ExecutionTimeLimit  PT0S   - 무제한. 기본값(3일)이면 사흘 뒤 홀드가 끊긴다.
#   MultipleInstancesPolicy IgnoreNew - 살아 있으면 5분 트리거를 무시한다.
#     이것 덕분에 "죽었을 때만 다시 띄우기"가 재시작 로직 없이 성립한다.
# LogonTrigger 도 넣는다. 08-12 13:31 윈도우 재부팅 뒤 예약 작업의 다음 차례가
# 14:05 였고, 그동안 WSL 을 깨우는 것이 아무것도 없어 30분이 비었다.
$user = "$env:USERDOMAIN\$env:USERNAME"
$ps   = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Holds the WSL Ubuntu VM open so long-running calculations and the
    \\wsl.localhost share survive. The task process itself must stay running:
    Task Scheduler kills child processes when the task ends.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>$user</UserId>
      <Delay>PT30S</Delay>
    </LogonTrigger>
    <TimeTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>2026-08-12T00:00:00</StartBoundary>
      <Repetition>
        <Interval>PT5M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$user</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$ps</Command>
      <Arguments>-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\mangw\.claude_work\wsl_hold.ps1"</Arguments>
    </Exec>
  </Actions>
</Task>
"@
$path = 'C:\Users\mangw\.claude_work\ClaudeWslHold.xml'
[System.IO.File]::WriteAllText($path, $xml, [System.Text.Encoding]::Unicode)

schtasks /end    /tn ClaudeWslHold 2>&1 | Out-Null
schtasks /delete /tn ClaudeWslHold /f 2>&1 | Out-Null
schtasks /create /tn ClaudeWslHold /xml $path /f
