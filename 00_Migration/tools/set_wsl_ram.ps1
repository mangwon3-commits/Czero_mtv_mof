# set_wsl_ram.ps1 -- change WSL memory allocation safely, on request.
#
# [2026-08-29] Built for the "HKHOME can raise RAM to 26GB while I am away" ask.
#
# WHY A SCRIPT AND NOT A SCHEDULED TASK:
#   The user is remote for a week. Registering new scheduled tasks, or editing
#   wsl_hold.ps1 (the recovery lifeline), is the highest-risk thing to do in
#   exactly the window where nobody can fix a mistake. On 2026-08-27 a Korean
#   comment saved as UTF-8-without-BOM was misread as CP949 and killed
#   wsl_hold.ps1 silently -- it died every 5 minutes with Last Result 1 and
#   zero log lines. So: pure ASCII here, and nothing touches the lifeline.
#
#   "HKHOME command" is satisfied by: HKHOME messages a session, the session
#   runs this script. One command, all guards inside.
#
# USAGE (from Windows PowerShell):
#   .\set_wsl_ram.ps1 -GB 26            # apply (restarts WSL)
#   .\set_wsl_ram.ps1 -GB 26 -DryRun    # show what would happen, change nothing
#   .\set_wsl_ram.ps1 -GB 24            # revert
#
# GUARDS (all must pass, else it refuses and changes nothing):
#   1. No calculation running in WSL. Restarting WSL mid-run destroys the run.
#   2. Host keeps at least MinHostGB after the change.
#   3. Requested value within [8, 28] GB.
#   4. .wslconfig is backed up before the edit.

param(
    [Parameter(Mandatory = $true)][int]$GB,
    [int]$MinHostGB = 5,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$cfg = Join-Path $env:USERPROFILE '.wslconfig'
$log = Join-Path $env:USERPROFILE '.claude_work\wsl_ram.log'

function Say($m) {
    $line = "{0}  {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Write-Output ("  " + $m)
    try {
        $d = Split-Path $log -Parent
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
        Add-Content -Path $log -Value $line -Encoding utf8
    } catch { }
}

Say "=== set_wsl_ram: requested ${GB}GB (DryRun=$DryRun) ==="

# ---- guard 3: sane range -----------------------------------------------
if ($GB -lt 8 -or $GB -gt 28) {
    Say "REFUSED: ${GB}GB is outside the allowed range 8..28."
    exit 1
}

# ---- guard 2: host headroom --------------------------------------------
$totalGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
$leftGB = [math]::Round($totalGB - $GB, 1)
Say "host total ${totalGB}GB -> WSL ${GB}GB leaves ${leftGB}GB for Windows"
if ($leftGB -lt $MinHostGB) {
    Say "REFUSED: would leave only ${leftGB}GB for Windows (minimum ${MinHostGB}GB)."
    exit 1
}

# ---- guard 1: nothing computing ----------------------------------------
# The process pattern lives inside busy_count.sh, NOT on this command line.
# If the pattern were written here, pgrep -f would match the caller itself --
# that self-match froze a watcher for 30 minutes on 2026-08-28.
$busy = -1
try {
    $raw = & wsl.exe -e bash /home/mangwon/mof_project/00_Migration/tools/busy_count.sh
    $busy = [int](($raw | Select-Object -Last 1) -replace '\D', '')
} catch {
    Say "REFUSED: could not query WSL for running jobs. Not restarting blind."
    exit 1
}
if ($busy -lt 0) {
    Say "REFUSED: busy check returned nothing usable. Not restarting blind."
    exit 1
}
Say "running calculations in WSL: $busy"
if ($busy -gt 0) {
    Say "REFUSED: $busy calculation(s) alive. Restarting WSL would destroy them."
    Say "Re-run when idle, or stop them deliberately first."
    exit 1
}

# ---- read current ------------------------------------------------------
if (-not (Test-Path $cfg)) { Say "REFUSED: $cfg not found."; exit 1 }
$text = Get-Content $cfg -Raw
$cur = 0
if ($text -match '(?m)^\s*memory\s*=\s*(\d+)GB') { $cur = [int]$Matches[1] }
Say "current memory=${cur}GB"
if ($cur -eq $GB) { Say "already ${GB}GB. Nothing to do."; exit 0 }

if ($DryRun) {
    Say "DRY RUN: would set memory=${GB}GB and run 'wsl --shutdown'. No change made."
    exit 0
}

# ---- guard 4: backup, then edit ---------------------------------------
$bak = "$cfg.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item $cfg $bak
Say "backed up -> $bak"

$new = $text -replace '(?m)^\s*memory\s*=\s*\d+GB', "memory=${GB}GB"
if ($new -eq $text) { Say "REFUSED: no memory= line matched; refusing to guess."; exit 1 }
Set-Content -Path $cfg -Value $new -Encoding utf8 -NoNewline
Say "wrote memory=${GB}GB"

# ---- restart -----------------------------------------------------------
Say "running 'wsl --shutdown' (the only way the change takes effect)"
& wsl.exe --shutdown
Start-Sleep -Seconds 5

# ---- verify ------------------------------------------------------------
$seen = & wsl.exe -e bash -c "free -g"
Say "WSL back up. free -g says: $($seen | Select-Object -Skip 1 -First 1)"
Say "=== done: memory=${GB}GB ==="
