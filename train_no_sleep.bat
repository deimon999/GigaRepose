@echo off
REM Keep PC awake during model training
echo ====================================================================
echo TRAINING SESSION - KEEPING PC AWAKE
echo ====================================================================
echo.
echo This script will prevent your PC from sleeping during training.
echo Press Ctrl+C to stop and allow sleep again.
echo.
echo Starting in 5 seconds...
timeout /t 5

REM Start the training
echo.
echo Starting model training...
start /B python train_6hours.py 2>&1 | powershell -Command "$input | Tee-Object -FilePath training_log.txt"

REM Keep system awake using PowerShell
powershell -Command "$code = '[DllImport(\"kernel32.dll\", CharSet = CharSet.Auto,SetLastError = true)] public static extern void SetThreadExecutionState(uint esFlags);'; $type = Add-Type -MemberDefinition $code -Name System -Namespace Win32 -PassThru; $ES_CONTINUOUS = [uint32]'0x80000000'; $ES_SYSTEM_REQUIRED = [uint32]'0x00000001'; $type::SetThreadExecutionState($ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED); Write-Host 'System sleep disabled - training in progress...'; Write-Host 'Monitoring training log every 5 minutes...'; Write-Host ''; while ($true) { Start-Sleep -Seconds 300; if (Test-Path 'training_log.txt') { Write-Host ''; Write-Host '=== Training Progress Update ===' -ForegroundColor Cyan; Get-Content training_log.txt -Tail 15; Write-Host ''; } }"

echo.
echo Training complete or interrupted!
pause
