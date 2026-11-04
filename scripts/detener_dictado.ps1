$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*dictado-whisper*' }
foreach ($p in $procs) {
    Write-Host "Matando Dictado Whisper PID: $($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
Stop-ScheduledTask -TaskName "HBOS-DictadoWhisper" -ErrorAction SilentlyContinue
Write-Host "Dictado Whisper detenido."

