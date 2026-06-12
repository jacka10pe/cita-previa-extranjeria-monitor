# monitor_idle.ps1
# This script monitors system idle time and runs the cita-previa monitor.

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

    [StructLayout(LayoutKind.Sequential)]
    public struct LASTINPUTINFO {
        public uint cbSize;
        public uint dwTime;
    }

    public static uint GetIdleTicks() {
        LASTINPUTINFO lii = new LASTINPUTINFO();
        lii.cbSize = (uint)Marshal.SizeOf(lii);
        if (GetLastInputInfo(ref lii)) {
            return (uint)Environment.TickCount - lii.dwTime;
        }
        return 0;
    }
}
"@

$idleThresholdMs = 5 * 60 * 1000  # 5 minutes threshold
$runIntervalSec = 5 * 60         # 5 minutes between runs
$errorWaitSec = 15 * 60          # 15 minutes wait on error
$checkFrequencySec = 10          # Check idle status every 10 seconds

Write-Host "Monitoring started. Will execute main.py after 5 minutes of idle time."
Write-Host "Press Ctrl+C to stop."

while ($true) {
    $idleTicks = [Win32]::GetIdleTicks()
    
    if ($idleTicks -ge $idleThresholdMs) {
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - System idle for $([Math]::Round($idleTicks / 1000 / 60, 2)) minutes. Running main.py..."
        
        # Run main.py using poetry as suggested by the project's schedule_cita.cmd
        # We set SCRAPER_SESSION_ID to a timestamp to ensure uniqueness if needed
        $env:SCRAPER_SESSION_ID = "idle_session_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        
        poetry run python src/main.py
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - [ERROR] main.py failed with exit code $LASTEXITCODE. Pausing for 15 minutes."
            Start-Sleep -Seconds $errorWaitSec
        } else {
            Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - [SUCCESS] main.py finished. Waiting 5 minutes before next run (if still idle)."
            Start-Sleep -Seconds $runIntervalSec
        }
    } else {
        # Not idle enough yet, check again soon
        Start-Sleep -Seconds $checkFrequencySec
    }
}
