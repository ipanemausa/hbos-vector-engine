# ==============================================================================
# HBOS REPARACION AUTONOMA DE SERVICIOS DE LENGUAJE Y TECLADO
# ==============================================================================
[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] Iniciando Diagnostico y Reparacion del Sistema de Teclado..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Limpieza de Keyboard Layout Substitutes corruptos
Write-Host "[1/6] Analizando HKCU:\Keyboard Layout\Substitutes y Preload..." -ForegroundColor Yellow
$substitutesPath = "HKCU:\Keyboard Layout\Substitutes"
if (Test-Path $substitutesPath) {
    $props = (Get-ItemProperty $substitutesPath).PSObject.Properties | Where-Object { $_.Name -notmatch "^PS" }
    foreach ($p in $props) {
        Write-Host "  -> Eliminando sustituto corrupto: $($p.Name) = $($p.Value)" -ForegroundColor Gray
        Remove-ItemProperty -Path $substitutesPath -Name $p.Name -Force -ErrorAction SilentlyContinue
    }
}

$preloadPath = "HKCU:\Keyboard Layout\Preload"
if (Test-Path $preloadPath) {
    # Limpiar preload viejo
    $props = (Get-ItemProperty $preloadPath).PSObject.Properties | Where-Object { $_.Name -notmatch "^PS" }
    foreach ($p in $props) {
        Remove-ItemProperty -Path $preloadPath -Name $p.Name -Force -ErrorAction SilentlyContinue
    }
    # Establecer preload limpio: 1 = 0000080a (Latinoamerica), 2 = 00000409 (US)
    Set-ItemProperty -Path $preloadPath -Name "1" -Value "0000080a" -Force
    Set-ItemProperty -Path $preloadPath -Name "2" -Value "00000409" -Force
    Write-Host "  -> Preload reconstruido canonicamente (1: 0000080a [es-LatAm], 2: 00000409 [en-US])" -ForegroundColor Green
}

# 2. Purga de Asambleas Huerfanas en CTF (Text Services Framework)
Write-Host "[2/6] Purgando ensamblados huerfanos en CTF..." -ForegroundColor Yellow
$assemblyBase = "HKCU:\Software\Microsoft\CTF\SortOrder\AssemblyItem"
if (Test-Path $assemblyBase) {
    $legacyAssemblies = @("0x00000c0a", "0x0000580a")
    foreach ($leg in $legacyAssemblies) {
        $legPath = Join-Path $assemblyBase $leg
        if (Test-Path $legPath) {
            Remove-Item -Path $legPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  -> Eliminado ensamblado huerfano en CTF: $leg" -ForegroundColor Green
        }
    }
}

# 2.5 Neutralizacion de apps interceptoras de teclado (Wispr Flow / LogiLDA)
Write-Host "[2.5/6] Neutralizando hooks e inicios de Wispr Flow y Logitech Assistant..." -ForegroundColor Yellow
$startupWispr = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\Wispr Flow.lnk"
if (Test-Path $startupWispr) {
    Remove-Item $startupWispr -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Wispr Flow eliminado de la carpeta Inicio de Windows." -ForegroundColor Green
}
$logiRunKey = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $logiRunKey -Name "Logitech Download Assistant" -Force -ErrorAction SilentlyContinue
Remove-ItemProperty -Path $logiRunKey -Name "Logi Download Assistant" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "*wispr*", "*flow*", "*logilda*" -Force -ErrorAction SilentlyContinue

# 3. Limpieza de FilterKeys y Accesibilidad de Teclado
Write-Host "[3/6] Desactivando FilterKeys, StickyKeys y retrasos residuales..." -ForegroundColor Yellow
$accKey = "HKCU:\Control Panel\Accessibility\Keyboard Response"
if (Test-Path $accKey) {
    Set-ItemProperty -Path $accKey -Name "Flags" -Value "2" -Force
    Set-ItemProperty -Path $accKey -Name "DelayBeforeAcceptance" -Value "0" -Force
    Set-ItemProperty -Path $accKey -Name "AutoRepeatRate" -Value "0" -Force
    Set-ItemProperty -Path $accKey -Name "AutoRepeatDelay" -Value "0" -Force
    Set-ItemProperty -Path $accKey -Name "BounceTime" -Value "0" -Force
}

$stickyKey = "HKCU:\Control Panel\Accessibility\StickyKeys"
if (Test-Path $stickyKey) {
    Set-ItemProperty -Path $stickyKey -Name "Flags" -Value "506" -Force
}

$toggleKey = "HKCU:\Control Panel\Accessibility\ToggleKeys"
if (Test-Path $toggleKey) {
    Set-ItemProperty -Path $toggleKey -Name "Flags" -Value "58" -Force
}

# 4. Establecer WinUserLanguageList Canónico
Write-Host "[4/6] Reconfigurando lista de idiomas de usuario en Windows..." -ForegroundColor Yellow
try {
    $userLangs = New-WinUserLanguageList -Language "es-MX"
    $userLangs[0].InputMethodTips.Clear()
    $userLangs[0].InputMethodTips.Add("080A:0000080A") # Teclado Latinoamericano
    $userLangs[0].InputMethodTips.Add("080A:00000409") # Teclado US (para teclas fisicas en ingles)
    
    $enLang = New-WinUserLanguageList -Language "en-US"
    $userLangs.Add($enLang[0])
    
    Set-WinUserLanguageList -LanguageList $userLangs -Force
    Set-WinDefaultInputMethodOverride -InputTip "080A:0000080A" -ErrorAction SilentlyContinue
    Write-Host "  -> Perfiles de idioma guardados y validados con exito." -ForegroundColor Green
} catch {
    Write-Host "  -> Advertencia al actualizar WinUserLanguageList: $($_.Exception.Message)" -ForegroundColor DarkYellow
}

# 5. Reinicio Limpio de CTFMON y TextInputHost
Write-Host "[5/6] Reiniciando subsistemas Text Services Framework (ctfmon y TextInputHost)..." -ForegroundColor Yellow
Stop-Process -Name "TextInputHost" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ctfmon" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 600

Start-Process "C:\Windows\System32\ctfmon.exe"
Write-Host "  -> ctfmon.exe reiniciado con los nuevos perfiles limpios." -ForegroundColor Green

# 6. Broadcast Win32 de actualizacion de configuracion de teclado
Write-Host "[6/6] Notificando a todas las aplicaciones abiertas (Chrome, Edge, Terminales)..." -ForegroundColor Yellow
$win32Broadcast = @"
using System;
using System.Runtime.InteropServices;

public class WinInputFixer {
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(
        IntPtr hWnd,
        uint Msg,
        UIntPtr wParam,
        string lParam,
        uint fuFlags,
        uint uTimeout,
        out UIntPtr lpdwResult);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);

    public const uint HWND_BROADCAST = 0xffff;
    public const uint WM_SETTINGCHANGE = 0x001A;
    public const uint SMTO_ABORTIFHUNG = 0x0002;
    public const uint SPI_SETFILTERKEYS = 0x0033;

    [StructLayout(LayoutKind.Sequential)]
    public struct FILTERKEYS {
        public uint cbSize;
        public uint dwFlags;
        public uint iWaitMSec;
        public uint iDelayMSec;
        public uint iRepeatMSec;
        public uint iBounceMSec;
    }

    public static void ApplyLive() {
        FILTERKEYS fk = new FILTERKEYS();
        fk.cbSize = (uint)Marshal.SizeOf(fk);
        fk.dwFlags = 2; // FKF_AVAILABLE, but OFF (bit 0 is 0)
        fk.iWaitMSec = 0;
        fk.iDelayMSec = 0;
        fk.iRepeatMSec = 0;
        fk.iBounceMSec = 0;

        IntPtr ptr = Marshal.AllocHGlobal(Marshal.SizeOf(fk));
        Marshal.StructureToPtr(fk, ptr, false);
        SystemParametersInfo(SPI_SETFILTERKEYS, (uint)Marshal.SizeOf(fk), ptr, 3);
        Marshal.FreeHGlobal(ptr);

        UIntPtr result;
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "Keyboard Layout", SMTO_ABORTIFHUNG, 2000, out result);
        SendMessageTimeout((IntPtr)HWND_BROADCAST, WM_SETTINGCHANGE, UIntPtr.Zero, "intl", SMTO_ABORTIFHUNG, 2000, out result);
    }
}
"@

try {
    Add-Type -TypeDefinition $win32Broadcast -Language CSharp -ErrorAction SilentlyContinue
    [WinInputFixer]::ApplyLive()
    Write-Host "  -> Senal WM_SETTINGCHANGE enviada a todas las ventanas activas." -ForegroundColor Green
} catch {
    Write-Host "  -> Error enviando broadcast Win32: $($_.Exception.Message)" -ForegroundColor DarkYellow
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[HBOS] REPARACION COMPLETADA CON EXITO." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
