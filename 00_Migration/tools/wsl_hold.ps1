# WSL hold - keeps a WSL distro alive from the Windows side.
#
# ============================================================================
# ASCII ONLY. Do not put non-ASCII characters in this file.
#   2026-08-28 (Junseok): a version with Korean comments was saved as UTF-8
#   without a BOM. Windows PowerShell 5.1 read it as the ANSI codepage and a
#   string terminator broke. The scheduled task then died instantly every
#   5 minutes with exit code 1 and never wrote a single log line - it looked
#   installed and healthy from the outside. Keep rationale in the repo docs.
# ============================================================================
#
# WHY THIS EXISTS
#   With no wsl.exe client attached from Windows, systemd-logind powers the
#   distro off and every setsid/nohup background calculation dies with it.
#   .wslconfig vmIdleTimeout=-1 only covers the VM, not the distro.
#
# WHY IT MUST NOT EXIT
#   Task Scheduler binds children to a job object, so Start-Process cannot
#   detach a hold. The task process itself has to hold the handle.
#
# ============================================================================
# 2026-08-28 FLEET HAZARD FIXED - read this before editing
#
#   The previous version hardcoded one machine's paths:
#       $log   = 'C:\Users\mangw\.claude_work\wsl_hold.log'
#       $hold  = '/home/mangwon1/.claude_work/vm_hold.sh'
#
#   On any other machine that path does not exist, so `wsl.exe --exec` returns
#   immediately. The loop counts 3 fast returns in ~30 seconds and then runs
#   `wsl --shutdown`, on the assumption written at the old line 66 that
#   "no calculation can be running in this state". That assumption is FALSE on
#   a machine where the only problem is a wrong path. The laptop caught this
#   with 40.7 core-hours in flight, including a 6.5 hour RASPA job.
#
#   Same shape as 08-19, when relax_fixcell.py hardcoded /home/mangwon1/.../xtb
#   and died on the laptop. That one only killed itself. This one kills other
#   people's calculations.
#
#   Two changes make it safe:
#     1. PREFLIGHT. If the hold script is not present and executable inside the
#        distro, log loudly and exit 1. Never enter the loop. A wrong path can
#        no longer reach the shutdown branch at all.
#     2. BUSY GUARD. Never run `wsl --shutdown` while a calculation is alive,
#        even when the distro really does look wedged.
# ============================================================================
#
# CONFIGURATION - environment variables, all optional
#   CLAUDE_WSL_DIST   distro name                (default: Ubuntu)
#   CLAUDE_WSL_HOLD   path to vm_hold.sh in WSL  (default: auto-detected)
#   CLAUDE_WSL_GUARD  optional guard script in WSL, run once per loop
#
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File wsl_hold.ps1

$ErrorActionPreference = 'SilentlyContinue'

$work = Join-Path $env:USERPROFILE '.claude_work'
$log  = Join-Path $work 'wsl_hold.log'
$dist = if ($env:CLAUDE_WSL_DIST) { $env:CLAUDE_WSL_DIST } else { 'Ubuntu' }

$FAST_RETURN_SEC       = 30
$FAILS_BEFORE_SHUTDOWN = 3
$BUSY_PATTERN          = 'simulate|lmp_serial|/network|risk_screen|run_water|run_humid'

if (-not (Test-Path $work)) { New-Item -ItemType Directory -Path $work -Force | Out-Null }

function Log($m) {
    "$(Get-Date -Format 'MM-dd HH:mm:ss')  $m" | Out-File -FilePath $log -Append -Encoding ascii
}
if ((Test-Path $log) -and ((Get-Item $log).Length -gt 200KB)) {
    Get-Content $log -Tail 400 | Set-Content $log -Encoding ascii
}

function WslTest($path) {
    # Returns $true only if the path is executable inside the distro.
    $r = (& wsl.exe -d $dist -e sh -c "test -x '$path' && echo YES" 2>$null | Out-String).Trim()
    return ($r -eq 'YES')
}

# --- resolve the hold script -------------------------------------------------
$hold = $env:CLAUDE_WSL_HOLD
if (-not $hold) {
    $wslHome = (& wsl.exe -d $dist -e sh -c 'echo $HOME' 2>$null | Out-String).Trim()
    foreach ($cand in @(
        "$wslHome/mof_project/00_Migration/tools/vm_hold.sh",
        "$wslHome/.claude_work/vm_hold.sh"
    )) {
        if ($wslHome -and (WslTest $cand)) { $hold = $cand; break }
    }
}

# --- PREFLIGHT: refuse to run rather than risk a shutdown --------------------
if (-not $hold) {
    Log "PREFLIGHT FAILED: no vm_hold.sh found in distro '$dist'. Set CLAUDE_WSL_HOLD. Exiting without touching WSL."
    exit 1
}
if (-not (WslTest $hold)) {
    Log "PREFLIGHT FAILED: '$hold' is not executable in distro '$dist'. Exiting without touching WSL."
    exit 1
}

$guard = $env:CLAUDE_WSL_GUARD
if ($guard -and -not (WslTest $guard)) {
    Log "guard '$guard' not executable - ignoring it"
    $guard = $null
}

# Only one instance. The task repeats every few minutes; later starts back off.
$mutex = New-Object System.Threading.Mutex($false, "Local\ClaudeWslHold_$dist")
if (-not $mutex.WaitOne(0)) { exit 0 }

Log "hold loop started (pid $PID, dist $dist, hold $hold)"
$fails = 0

while ($true) {
    if ($guard) { & wsl.exe -d $dist -e sh "$guard" 2>&1 | Out-Null }

    $t0 = Get-Date
    & wsl.exe -d $dist --exec $hold 2>&1 | Out-Null
    $secs = [int]((Get-Date) - $t0).TotalSeconds

    if ($secs -lt $FAST_RETURN_SEC) {
        $fails++
        Log "hold returned after ${secs}s (consecutive fast returns: $fails)"
    } else {
        $fails = 0
        Log "hold returned after ${secs}s - distro went down, re-attaching"
    }

    if ($fails -ge $FAILS_BEFORE_SHUTDOWN) {
        $busy = (& wsl.exe -d $dist -e pgrep -c -f $BUSY_PATTERN 2>$null | Out-String).Trim()
        if ($busy -match '^\d+$' -and [int]$busy -gt 0) {
            Log "looks wedged, but $busy calculation processes are alive - NOT shutting down"
            $fails = 0
        } else {
            Log "distro appears wedged and no calculation is alive - running wsl --shutdown"
            & wsl.exe --shutdown 2>&1 | Out-Null
            Start-Sleep -Seconds 25
            & wsl.exe -d $dist -e true 2>&1 | Out-Null
            Start-Sleep -Seconds 10
            Log "restarted after wsl --shutdown"
            $fails = 0
        }
    }

    Start-Sleep -Seconds 5
}
