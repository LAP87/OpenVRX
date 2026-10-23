# OpenVRX bench rig, Windows side: keep WSL awake, attach the boards with usbipd, hand over to tools/bench/bench.py.
#
#   tools\bench.ps1                     same as "up": guard + attach the Tang + "devices" in WSL
#   tools\bench.ps1 up                  WSL guard, Tang attached with auto-attach, then bench.py devices
#   tools\bench.ps1 attach [-Xiao]      attach the Tang (and, only with -Xiao, the XIAO ESP32-C5)
#   tools\bench.ps1 guard               start the WSL guard if it is not running
#   tools\bench.ps1 state               what usbipd sees (bound, attached), from `usbipd state`
#   tools\bench.ps1 <anything else>     passed to bench.py in WSL, e.g.:
#   tools\bench.ps1 flash m6_puck_proto --build-dir /root/openvrx-wt/n58/gateware/build
#   tools\bench.ps1 log m6 --seconds 20 --out /mnt/c/.../bench-logs/m6.jsonl
#
# Boards are found by VID:PID, not by bus id (it changes when a cable moves): 0403:6010 Tang Nano 20K (BL616 in FTDI
# mode), 303a:1001 XIAO ESP32-C5 (USB-serial-JTAG). Attaching runs `usbipd attach --wsl --hardware-id <vid:pid>
# --auto-attach` as a hidden process that outlives this script and attaches the board again after a replug.
# A board must be bound (shared) once by an administrator (`usbipd bind --busid <id>`); this script never elevates.
# The XIAO is attached only with -Xiao: Windows' serial class has left it in the ROM download mode before
# (hub docs/BANK_2026-10-23.md), and its console belongs to tools/bench/c5.py in WSL.
#
# WSL stops its VM a while after the last process ends and the attached boards go with it. The guard is a hidden
# `wsl.exe -d Ubuntu -- sleep 36000` (10 h); "up" starts one when none is running.
# Commands go to WSL with `wsl.exe -e` (no shell in between), so `$` in arguments survives.
param(
    [Parameter(Position = 0)][string]$Command = 'up',
    [switch]$Xiao,
    [string]$Distro = 'Ubuntu',
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest
)
$ErrorActionPreference = 'Stop'
$Python = '/root/openvrx-review/OpenVRX-Core/.venv/bin/python'
$Boards = [ordered]@{ tang = '0403:6010'; xiao = '303a:1001' }

function Get-WslPath([string]$win) {
    # C:\x\y -> /mnt/c/x/y, computed here: wslpath's answer comes back through the console code page, which breaks
    # the non-ASCII characters of the hub's path ("Drönare") in Windows PowerShell 5.1
    $full = [IO.Path]::GetFullPath($win)
    if ($full -notmatch '^([A-Za-z]):\\(.*)$') { throw "not a drive path: $full" }
    return '/mnt/' + $Matches[1].ToLower() + '/' + ($Matches[2] -replace '\\', '/')
}

function Start-Guard {
    $g = Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" |
        Where-Object { $_.CommandLine -match "-d\s+$Distro\s+--\s+sleep\s+\d+" }
    if ($g) { Write-Host "WSL guard running (pid $(@($g)[0].ProcessId))"; return }
    Start-Process -WindowStyle Hidden -FilePath wsl.exe -ArgumentList @('-d', $Distro, '--', 'sleep', '36000')
    Start-Sleep -Seconds 2
    Write-Host "WSL guard started (sleep 36000 in $Distro)"
}

function Get-UsbState {
    # usbipd 5: JSON with BusId, InstanceId (USB\VID_xxxx&PID_xxxx\serial), PersistedGuid (bound) and
    # ClientIPAddress (attached)
    $s = (& usbipd state) -join "`n" | ConvertFrom-Json
    foreach ($d in $s.Devices) {
        if ($d.InstanceId -match 'VID_([0-9A-F]{4})&PID_([0-9A-F]{4})') {
            $vp = ("{0}:{1}" -f $Matches[1], $Matches[2]).ToLower()
            $kind = ($Boards.GetEnumerator() | Where-Object { $_.Value -eq $vp } | Select-Object -First 1).Key
            [pscustomobject]@{ Kind = $kind; VidPid = $vp; BusId = $d.BusId; Bound = [bool]$d.PersistedGuid
                               Attached = [bool]$d.ClientIPAddress; Description = $d.Description }
        }
    }
}

function Show-State {
    Get-UsbState | Where-Object { $_.Kind } | Format-Table Kind, VidPid, BusId, Bound, Attached, Description -AutoSize
}

function Start-AutoAttach([string]$kind) {
    $vp = $Boards[$kind]
    $dev = Get-UsbState | Where-Object { $_.VidPid -eq $vp } | Select-Object -First 1
    if (-not $dev -or -not $dev.BusId) { Write-Host "$kind ($vp) is not plugged in"; return }
    if (-not $dev.Bound) {
        Write-Host "$kind ($vp, bus $($dev.BusId)) is not bound: an administrator runs once  usbipd bind --busid $($dev.BusId)"
        return
    }
    $running = Get-CimInstance Win32_Process -Filter "Name='usbipd.exe'" |
        Where-Object { $_.CommandLine -match 'attach' -and $_.CommandLine -match [regex]::Escape($vp) }
    if ($running) {
        Write-Host "$kind auto-attach already running (pid $(@($running)[0].ProcessId)); attached: $($dev.Attached)"
        return
    }
    Start-Process -WindowStyle Hidden -FilePath usbipd.exe `
        -ArgumentList @('attach', '--wsl', $Distro, '--hardware-id', $vp, '--auto-attach')
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        $dev = Get-UsbState | Where-Object { $_.VidPid -eq $vp } | Select-Object -First 1
        if ($dev.Attached) { break }
    }
    Write-Host "$kind auto-attach started; attached: $($dev.Attached) (bus $($dev.BusId))"
}

function Invoke-Bench([string[]]$argv) {
    $hub = Get-WslPath (Split-Path -Parent $PSScriptRoot)
    & wsl.exe -d $Distro --cd $hub -e $Python tools/bench/bench.py @argv | Out-Host
    return $LASTEXITCODE
}

$prevEnc = [Console]::OutputEncoding
[Console]::OutputEncoding = [Text.Encoding]::UTF8    # bench.py writes UTF-8
try {
switch ($Command) {
    'guard'  { Start-Guard }
    'state'  { Show-State }
    'attach' {
        Start-Guard
        Start-AutoAttach 'tang'
        if ($Xiao) { Start-AutoAttach 'xiao' }
    }
    'up' {
        Start-Guard
        Start-AutoAttach 'tang'
        if ($Xiao) { Start-AutoAttach 'xiao' }
        exit (Invoke-Bench @('devices'))
    }
    default { exit (Invoke-Bench (@($Command) + @($Rest | Where-Object { $_ -ne $null }))) }
}
} finally { [Console]::OutputEncoding = $prevEnc }
