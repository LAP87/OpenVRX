# Headless terminal for the C5VRX receiver (XIAO ESP32-C5 on a Windows COM port).
#
# The chip's USB-serial-JTAG port maps the CDC control lines like the classic ESP auto-reset circuit:
# DTR=0 with RTS=1 holds the chip in reset, DTR=1 with RTS=0 pulls the boot strap, both equal does nothing.
# System.IO.Ports changes the two lines one at a time at open and close, which rebooted the chip and left it
# in the ROM download mode (silent until a power cycle). This script therefore uses the Win32 API directly:
# CreateFile, one SetCommState with the whole DCB (115200 8N1, DTR and RTS both on, or both off, in the same
# call), blocking reads with a timeout (an immediate-return read never sees anything on this driver), and the
# lines dropped together before every close.
#
# Modes:  -Daemon   hold the port; append everything to $Dir\full.log and the lines without the FIELD_TRACE /
#                   FIELD_DIAG flood to $Dir\short.log; send the bytes of $Dir\cmd.txt (then delete it);
#                   reopen when the device re-enumerates
#         -Reboot   normal reboot of the chip through the lines (reset with the boot strap released)
#         (default) one shot: optional -Key, read -Secs seconds, print the lines (filtered, or -Grep)
param(
    [string]$Port = 'COM5',
    [switch]$Daemon,
    [switch]$Reboot,
    [string]$Dir = "$env:TEMP\c5vrx",
    [string]$Key = '',
    [double]$Secs = 8,
    [string]$Grep = '',
    [switch]$All,
    [int]$Dtr = 1,
    [int]$Rts = 1
)
$src = @'
using System;
using System.Runtime.InteropServices;
public class Win32Com {
    [StructLayout(LayoutKind.Sequential)] public struct DCB {
        public uint DCBlength; public uint BaudRate; public uint Flags; public ushort wReserved; public ushort XonLim;
        public ushort XoffLim; public byte ByteSize; public byte Parity; public byte StopBits; public sbyte XonChar;
        public sbyte XoffChar; public sbyte ErrorChar; public sbyte EofChar; public sbyte EvtChar; public ushort wReserved1; }
    [StructLayout(LayoutKind.Sequential)] public struct COMMTIMEOUTS {
        public uint ReadIntervalTimeout; public uint ReadTotalTimeoutMultiplier; public uint ReadTotalTimeoutConstant;
        public uint WriteTotalTimeoutMultiplier; public uint WriteTotalTimeoutConstant; }
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr sa, uint disp, uint flags, IntPtr tmpl);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool GetCommState(IntPtr h, ref DCB dcb);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool SetCommState(IntPtr h, ref DCB dcb);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool SetCommTimeouts(IntPtr h, ref COMMTIMEOUTS t);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool PurgeComm(IntPtr h, uint flags);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool ReadFile(IntPtr h, byte[] buf, uint n, out uint read, IntPtr ov);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool WriteFile(IntPtr h, byte[] buf, uint n, out uint written, IntPtr ov);
    [DllImport("kernel32.dll", SetLastError = true)] public static extern bool CloseHandle(IntPtr h);
    static uint LineFlags(bool dtr, bool rts) {
        // fBinary, fTXContinueOnXoff, fDtrControl (bits 4-5) and fRtsControl (bits 12-13) = ENABLE or DISABLE
        return 1u | (1u << 7) | (dtr ? (1u << 4) : 0u) | (rts ? (1u << 12) : 0u);
    }
    public static bool SetLines(IntPtr h, bool dtr, bool rts) {
        DCB d = new DCB(); d.DCBlength = (uint)Marshal.SizeOf(typeof(DCB));
        if (!GetCommState(h, ref d)) return false;
        d.Flags = LineFlags(dtr, rts);
        return SetCommState(h, ref d);
    }
    public static IntPtr Open(string port, bool dtr, bool rts, out string err) {
        err = "";
        IntPtr h = CreateFile("\\\\.\\" + port, 0xC0000000u, 0, IntPtr.Zero, 3, 0, IntPtr.Zero);
        if (h == new IntPtr(-1)) { err = "CreateFile " + Marshal.GetLastWin32Error(); return IntPtr.Zero; }
        DCB d = new DCB(); d.DCBlength = (uint)Marshal.SizeOf(typeof(DCB));
        if (!GetCommState(h, ref d)) { err = "GetCommState " + Marshal.GetLastWin32Error(); CloseHandle(h); return IntPtr.Zero; }
        d.BaudRate = 115200; d.ByteSize = 8; d.Parity = 0; d.StopBits = 0;
        d.Flags = LineFlags(dtr, rts);
        if (!SetCommState(h, ref d)) { err = "SetCommState " + Marshal.GetLastWin32Error(); CloseHandle(h); return IntPtr.Zero; }
        // a read waits up to 200 ms for data and returns 50 ms after the last byte; a write gives up after 1 s
        COMMTIMEOUTS t = new COMMTIMEOUTS(); t.ReadIntervalTimeout = 50; t.ReadTotalTimeoutConstant = 200; t.WriteTotalTimeoutConstant = 1000;
        if (!SetCommTimeouts(h, ref t)) { err = "SetCommTimeouts " + Marshal.GetLastWin32Error(); CloseHandle(h); return IntPtr.Zero; }
        PurgeComm(h, 0x000Cu);
        return h;
    }
    public static void Close(IntPtr h, bool release) {
        if (h == IntPtr.Zero) return;
        if (release) SetLines(h, false, false);   // both lines off in one call: no reset, no boot strap
        CloseHandle(h);
    }
    public static byte[] Read(IntPtr h, out bool ok) {
        byte[] buf = new byte[65536]; uint n;
        ok = ReadFile(h, buf, (uint)buf.Length, out n, IntPtr.Zero);
        byte[] outb = new byte[n]; Array.Copy(buf, outb, n); return outb;
    }
    public static bool Write(IntPtr h, byte[] data) { uint w; return WriteFile(h, data, (uint)data.Length, out w, IntPtr.Zero) && w == data.Length; }
}
'@
if (-not ('Win32Com' -as [type])) { Add-Type -TypeDefinition $src }
$enc = [System.Text.Encoding]::GetEncoding(28591)

function Open-Port([bool]$dtr, [bool]$rts) {
    $err = ''
    $h = [Win32Com]::Open($Port, $dtr, $rts, [ref]$err)
    if ($h -eq [IntPtr]::Zero) { throw "open failed: $err" }
    return $h
}

if ($Reboot) {
    # EN low (DTR 0, RTS 1), then both off: the chip boots normally and re-enumerates on USB
    $h = Open-Port $false $false
    Start-Sleep -Milliseconds 100
    [void][Win32Com]::SetLines($h, $false, $true)
    Start-Sleep -Milliseconds 150
    [void][Win32Com]::SetLines($h, $false, $false)
    Start-Sleep -Milliseconds 100
    [Win32Com]::Close($h, $false)
    Write-Output 'reboot pulse sent; the port re-enumerates in a few seconds'
    exit 0
}

if ($Daemon) {
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    $full = Join-Path $Dir 'full.log'; $short = Join-Path $Dir 'short.log'; $cmd = Join-Path $Dir 'cmd.txt'; $state = Join-Path $Dir 'state.txt'
    $buf = ''
    while ($true) {
        $h = [IntPtr]::Zero
        $alive = $false
        try {
            $h = Open-Port ([bool]$Dtr) ([bool]$Rts)
            $alive = $true
            Set-Content -Path $state -Value ("open {0}" -f (Get-Date -Format 'HH:mm:ss'))
            Add-Content -Path $short -Value ("### port opened {0} (win32)" -f (Get-Date -Format 'HH:mm:ss'))
            $silent = 0
            while ($true) {
                if (Test-Path $cmd) {
                    $keys = (Get-Content -Path $cmd -Raw)
                    Remove-Item -Path $cmd -Force
                    if ($keys) {
                        $keys = $keys.Trim()
                        foreach ($ch in $keys.ToCharArray()) { [void][Win32Com]::Write($h, $enc.GetBytes([string]$ch)); Start-Sleep -Milliseconds 150 }
                        $stamp = "### sent {0} at {1}" -f $keys, (Get-Date -Format 'HH:mm:ss')
                        Add-Content -Path $short -Value $stamp; Add-Content -Path $full -Value $stamp
                    }
                }
                $ok = $true
                $data = [Win32Com]::Read($h, [ref]$ok)
                if (-not $ok) { $alive = $false; throw "read failed" }
                if ($data.Length -eq 0) { $silent++; if ($silent % 300 -eq 0) { Set-Content -Path $state -Value ("open, silent {0} s" -f [int]($silent / 5)) }; continue }
                $silent = 0
                $text = $enc.GetString($data)
                Add-Content -Path $full -Value $text -NoNewline
                $buf += $text
                while ($buf.Contains("`n")) {
                    $i = $buf.IndexOf("`n"); $line = $buf.Substring(0, $i).TrimEnd("`r"); $buf = $buf.Substring($i + 1)
                    if ($line.StartsWith('FIELD_TRACE') -or $line.StartsWith('FIELD_DIAG')) { continue }
                    Add-Content -Path $short -Value ((Get-Date -Format 'HH:mm:ss') + ' ' + $line)
                }
            }
        }
        catch {
            Set-Content -Path $state -Value ("error {0}: {1}" -f (Get-Date -Format 'HH:mm:ss'), $_.Exception.Message)
            [Win32Com]::Close($h, $alive)
            Start-Sleep -Seconds 1
        }
    }
}
else {
    $h = Open-Port ([bool]$Dtr) ([bool]$Rts)
    try {
        if ($Key -ne '') { Start-Sleep -Milliseconds 300; [void][Win32Com]::Write($h, $enc.GetBytes($Key)) }
        $t0 = Get-Date; $buf = ''; $total = 0; $shown = 0
        while (((Get-Date) - $t0).TotalSeconds -lt $Secs) {
            $ok = $true
            $data = [Win32Com]::Read($h, [ref]$ok)
            if (-not $ok) { Write-Output 'read failed'; break }
            if ($data.Length -eq 0) { continue }
            $buf += $enc.GetString($data)
            while ($buf.Contains("`n")) {
                $i = $buf.IndexOf("`n"); $line = $buf.Substring(0, $i).TrimEnd("`r"); $buf = $buf.Substring($i + 1)
                $total++
                if (-not $All -and ($line.StartsWith('FIELD_TRACE') -or $line.StartsWith('FIELD_DIAG'))) { continue }
                if ($Grep -ne '' -and -not ($line -match $Grep)) { continue }
                Write-Output ("{0,6:F2} {1}" -f ((Get-Date) - $t0).TotalSeconds, $line.Substring(0, [Math]::Min(200, $line.Length)))
                $shown++
            }
        }
        Write-Output ("[{0} lines in all, {1} shown]" -f $total, $shown)
    }
    finally { [Win32Com]::Close($h, $true) }
}
