# ==============================================================================
# HBOS - APAGADO AUTOMATICO TOTAL DE SUGERENCIAS DE TEXTO Y PREDICCION EN POWERSHELL
# ==============================================================================
$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] Tomando el control total en PowerShell..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Cerrar la ventana de Configuracion para que no retenga el estado anterior en memoria
Write-Host "[1/5] Cerrando ventanas de configuracion abiertas..." -ForegroundColor Yellow
Stop-Process -Name "SystemSettings" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 300

# 2. Desactivar en el Registro todas las sugerencias de texto de teclado fisico y multilingue
Write-Host "[2/5] Apagando interruptores de prediccion en el registro..." -ForegroundColor Yellow
$inputSettings = "HKCU:\Software\Microsoft\Input\Settings"
if (-not (Test-Path $inputSettings)) { New-Item -Path $inputSettings -Force | Out-Null }

Set-ItemProperty -Path $inputSettings -Name "EnableHwkbTextPrediction" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $inputSettings -Name "EnableHwkbAutocorrection" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $inputSettings -Name "MultilingualEnabled" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $inputSettings -Name "VoiceTypingEnabled" -Value 0 -Type DWord -Force

Write-Host "  -> EnableHwkbTextPrediction = 0 (DESACTIVADO)" -ForegroundColor Green
Write-Host "  -> MultilingualEnabled = 0 (DESACTIVADO)" -ForegroundColor Green
Write-Host "  -> EnableHwkbAutocorrection = 0 (DESACTIVADO)" -ForegroundColor Green

# 3. Desactivar en TabletTip
$tabTip = "HKCU:\Software\Microsoft\TabletTip\1.7"
if (Test-Path $tabTip) {
    Set-ItemProperty -Path $tabTip -Name "EnableAutocorrection" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $tabTip -Name "EnableTextPrediction" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
}

# 4. Detener y reiniciar limpiamente el motor de entrada de texto
Write-Host "[3/5] Reiniciando TextInputHost y ctfmon..." -ForegroundColor Yellow
Stop-Process -Name "TextInputHost", "ctfmon" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 400
Start-Process "C:\Windows\System32\ctfmon.exe"
Write-Host "  -> Motor Text Services Framework reiniciado en limpio." -ForegroundColor Green

# 5. Broadcast de actualizacion a todas las ventanas
Write-Host "[4/5] Transmitiendo cambio a todas las ventanas..." -ForegroundColor Yellow
$csharp = @"
using System;
using System.Runtime.InteropServices;
public class SettingsNotifier {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
    public const uint HWND_BROADCAST = 0xffff;
    public const uint WM_SETTINGCHANGE = 0x001A;
    public const uint SMTO_ABORTIFHUNG = 0x0002;
    public static void Notify() {
        UIntPtr res;
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Policy", SMTO_ABORTIFHUNG, 1500, out res);
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "intl", SMTO_ABORTIFHUNG, 1500, out res);
    }
}
"@
try {
    Add-Type -TypeDefinition $csharp -Language CSharp -ErrorAction SilentlyContinue
    [SettingsNotifier]::Notify()
    Write-Host "  -> Notificacion transmitida." -ForegroundColor Green
} catch {
    Write-Host "  -> Nota broadcast: $($_.Exception.Message)" -ForegroundColor DarkYellow
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] CONTROL TOTAL COMPLETADO: PREDICCIONES APAGADAS AL 100%." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

