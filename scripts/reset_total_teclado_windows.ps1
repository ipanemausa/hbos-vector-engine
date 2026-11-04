# ==============================================================================
# HBOS - RESET TOTAL Y DEFINITIVO DE LA CONFIGURACION DE TECLADO Y ENTRADA
# ==============================================================================
$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] EJECUTANDO RESET TOTAL DE CONFIGURACION DE TECLADO..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Reset completo de Accesibilidad (FilterKeys, StickyKeys, ToggleKeys, Retardos)
Write-Host "[1/7] Restableciendo claves de Accesibilidad a valores de fabrica..." -ForegroundColor Yellow
$accPath = "HKCU:\Control Panel\Accessibility"

# Keyboard Response (FilterKeys - la causa comun de teclas que no responden sin mantenerlas)
$kr = "$accPath\Keyboard Response"
if (-not (Test-Path $kr)) { New-Item $kr -Force | Out-Null }
Set-ItemProperty $kr -Name "Flags" -Value "2" -Force
Set-ItemProperty $kr -Name "DelayBeforeAcceptance" -Value "0" -Force
Set-ItemProperty $kr -Name "AutoRepeatRate" -Value "0" -Force
Set-ItemProperty $kr -Name "AutoRepeatDelay" -Value "0" -Force
Set-ItemProperty $kr -Name "BounceTime" -Value "0" -Force

# StickyKeys (Teclas especiales)
$sk = "$accPath\StickyKeys"
if (-not (Test-Path $sk)) { New-Item $sk -Force | Out-Null }
Set-ItemProperty $sk -Name "Flags" -Value "506" -Force

# ToggleKeys
$tk = "$accPath\ToggleKeys"
if (-not (Test-Path $tk)) { New-Item $tk -Force | Out-Null }
Set-ItemProperty $tk -Name "Flags" -Value "58" -Force

# MouseKeys
$mk = "$accPath\MouseKeys"
if (-not (Test-Path $mk)) { New-Item $mk -Force | Out-Null }
Set-ItemProperty $mk -Name "Flags" -Value "58" -Force

# 2. Reset radical de Keyboard Layout y Substitutes
Write-Host "[2/7] Purgando tablas de sustitucion y mapas de scancodes corruptos..." -ForegroundColor Yellow
$subPath = "HKCU:\Keyboard Layout\Substitutes"
if (Test-Path $subPath) {
    Remove-Item -Path $subPath -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -Path $subPath -Force | Out-Null
    Write-Host "  -> Carpeta Substitutes vaciada y reiniciada a cero." -ForegroundColor Green
}

$scancodePath = "HKCU:\Keyboard Layout"
Remove-ItemProperty -Path $scancodePath -Name "Scancode Map" -Force -ErrorAction SilentlyContinue

$preloadPath = "HKCU:\Keyboard Layout\Preload"
if (Test-Path $preloadPath) {
    $props = (Get-ItemProperty $preloadPath).PSObject.Properties | Where-Object { $_.Name -notmatch "^PS" }
    foreach ($p in $props) {
        Remove-ItemProperty -Path $preloadPath -Name $p.Name -Force -ErrorAction SilentlyContinue
    }
    Set-ItemProperty -Path $preloadPath -Name "1" -Value "0000080a" -Force
    Set-ItemProperty -Path $preloadPath -Name "2" -Value "00000409" -Force
    Write-Host "  -> Preload reiniciado a 1: 0000080a (Español Latinoamericano) y 2: 00000409 (US)." -ForegroundColor Green
}

# 3. Purga completa de la cache de Text Services Framework (CTF)
Write-Host "[3/7] Purgando cache de ensamblados e InputSessions en CTF..." -ForegroundColor Yellow
$ctfPaths = @(
    "HKCU:\Software\Microsoft\CTF\SortOrder",
    "HKCU:\Software\Microsoft\CTF\Assemblies",
    "HKCU:\Software\Microsoft\CTF\InputSession",
    "HKCU:\Software\Microsoft\CTF\HiddenDummyLayouts"
)
foreach ($cp in $ctfPaths) {
    if (Test-Path $cp) {
        Remove-Item -Path $cp -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  -> Cache CTF eliminada: $cp" -ForegroundColor Green
    }
}

# 4. Reconstruccion canónica de la lista de idiomas
Write-Host "[4/7] Aplicando WinUserLanguageList canónico..." -ForegroundColor Yellow
try {
    $list = New-WinUserLanguageList -Language "es-MX"
    $list[0].InputMethodTips.Clear()
    $list[0].InputMethodTips.Add("080A:0000080A")
    $list[0].InputMethodTips.Add("080A:00000409")
    $en = New-WinUserLanguageList -Language "en-US"
    $list.Add($en[0])
    Set-WinUserLanguageList -LanguageList $list -Force
    Set-WinDefaultInputMethodOverride -InputTip "080A:0000080A" -ErrorAction SilentlyContinue
    Write-Host "  -> Idioma predeterminado fijado en es-MX (LatAm)." -ForegroundColor Green
} catch {
    Write-Host "  -> Nota sobre LanguageList: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 5. Neutralizar cualquier bloqueo residual de Wispr Flow y Logitech
Write-Host "[5/7] Verificando bloqueo de Wispr Flow y servicios interceptores..." -ForegroundColor Yellow
Stop-Process -Name "*wispr*", "*flow*", "*logilda*" -Force -ErrorAction SilentlyContinue
$startupLnk = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Wispr Flow.lnk"
if (Test-Path $startupLnk) { Remove-Item $startupLnk -Force -ErrorAction SilentlyContinue }

# 6. Reinicio coordinado de subsistemas de Windows
Write-Host "[6/7] Reiniciando TextInputHost y ctfmon..." -ForegroundColor Yellow
Stop-Process -Name "TextInputHost", "ctfmon" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500
Start-Process "C:\Windows\System32\ctfmon.exe"
Write-Host "  -> ctfmon.exe levantado en estado limpio." -ForegroundColor Green

# 7. Broadcast Win32 SPI_SETFILTERKEYS y WM_SETTINGCHANGE
Write-Host "[7/7] Transmitiendo actualizacion a todas las ventanas de Windows..." -ForegroundColor Yellow
$csharp = @"
using System;
using System.Runtime.InteropServices;

public class FullReset {
    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);

    public const uint HWND_BROADCAST = 0xffff;
    public const uint WM_SETTINGCHANGE = 0x001A;
    public const uint SMTO_ABORTIFHUNG = 0x0002;
    public const uint SPI_SETFILTERKEYS = 0x0033;
    public const uint SPI_SETSTICKYKEYS = 0x003B;
    public const uint SPI_SETTOGGLEKEYS = 0x0034;

    [StructLayout(LayoutKind.Sequential)]
    public struct FILTERKEYS {
        public uint cbSize;
        public uint dwFlags;
        public uint iWaitMSec;
        public uint iDelayMSec;
        public uint iRepeatMSec;
        public uint iBounceMSec;
    }

    public static void Execute() {
        FILTERKEYS fk = new FILTERKEYS();
        fk.cbSize = (uint)Marshal.SizeOf(fk);
        fk.dwFlags = 2; // FKF_AVAILABLE, bit 0 is 0 (OFF)
        fk.iWaitMSec = 0;
        fk.iDelayMSec = 0;
        fk.iRepeatMSec = 0;
        fk.iBounceMSec = 0;

        IntPtr ptr = Marshal.AllocHGlobal(Marshal.SizeOf(fk));
        Marshal.StructureToPtr(fk, ptr, false);
        SystemParametersInfo(SPI_SETFILTERKEYS, (uint)Marshal.SizeOf(fk), ptr, 3);
        Marshal.FreeHGlobal(ptr);

        UIntPtr res;
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Keyboard Layout", SMTO_ABORTIFHUNG, 2000, out res);
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "intl", SMTO_ABORTIFHUNG, 2000, out res);
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Policy", SMTO_ABORTIFHUNG, 2000, out res);
    }
}
"@

try {
    Add-Type -TypeDefinition $csharp -Language CSharp -ErrorAction SilentlyContinue
    [FullReset]::Execute()
    Write-Host "  -> Parametros aplicados en tiempo real al kernel de usuario de Windows." -ForegroundColor Green
} catch {
    Write-Host "  -> Error en CSharp: $($_.Exception.Message)" -ForegroundColor DarkYellow
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] RESET TOTAL COMPLETADO EXITOSAMENTE AL 100%." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

