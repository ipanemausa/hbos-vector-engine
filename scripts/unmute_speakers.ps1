# ==============================================================================
# HBOS - CONTROL TOTAL DE AUDIO: DESMUTE Y VOLUMEN A 80%
# ==============================================================================
$ErrorActionPreference = "Continue"

$csharp = @"
using System;
using System.Runtime.InteropServices;

namespace AudioController {
    [ComImport]
    [Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    internal class MMDeviceEnumeratorComObject { }

    internal enum EDataFlow {
        eRender,
        eCapture,
        eAll,
        EDataFlow_enum_count
    }

    internal enum ERole {
        eConsole,
        eMultimedia,
        eCommunications,
        ERole_enum_count
    }

    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMMDeviceEnumerator {
        int NotImpl1();
        [PreserveSig]
        int GetDefaultAudioEndpoint(EDataFlow dataFlow, ERole role, out IMMDevice ppDevice);
    }

    [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMMDevice {
        [PreserveSig]
        int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
    }

    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IAudioEndpointVolume {
        int NotImpl1();
        int NotImpl2();
        int GetChannelCount(out int pnChannelCount);
        [PreserveSig]
        int SetMasterVolumeLevel(float fLevelDB, ref Guid pguidEventContext);
        [PreserveSig]
        int SetMasterVolumeLevelScalar(float fLevel, ref Guid pguidEventContext);
        [PreserveSig]
        int GetMasterVolumeLevel(out float pfLevelDB);
        [PreserveSig]
        int GetMasterVolumeLevelScalar(out float pfLevel);
        [PreserveSig]
        int SetChannelVolumeLevel(uint nChannel, float fLevelDB, ref Guid pguidEventContext);
        [PreserveSig]
        int SetChannelVolumeLevelScalar(uint nChannel, float fLevel, ref Guid pguidEventContext);
        [PreserveSig]
        int GetChannelVolumeLevel(uint nChannel, out float pfLevelDB);
        [PreserveSig]
        int GetChannelVolumeLevelScalar(uint nChannel, out float pfLevel);
        [PreserveSig]
        int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, ref Guid pguidEventContext);
        [PreserveSig]
        int GetMute([MarshalAs(UnmanagedType.Bool)] out bool pbMute);
    }

    public class CoreAudioHelper {
        public static void SetVolumeAndUnmute(float volumeLevel) {
            var enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
            IMMDevice dev = null;
            enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender, ERole.eMultimedia, out dev);
            if (dev != null) {
                var IID_IAudioEndpointVolume = typeof(IAudioEndpointVolume).GUID;
                object epvObj;
                dev.Activate(ref IID_IAudioEndpointVolume, 0, IntPtr.Zero, out epvObj);
                var epv = (IAudioEndpointVolume)epvObj;
                
                Guid g = Guid.Empty;
                epv.SetMute(false, ref g);
                epv.SetMasterVolumeLevelScalar(volumeLevel, ref g);
            }
        }

        public static string GetStatus() {
            var enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
            IMMDevice dev = null;
            enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender, ERole.eMultimedia, out dev);
            if (dev != null) {
                var IID_IAudioEndpointVolume = typeof(IAudioEndpointVolume).GUID;
                object epvObj;
                dev.Activate(ref IID_IAudioEndpointVolume, 0, IntPtr.Zero, out epvObj);
                var epv = (IAudioEndpointVolume)epvObj;
                
                bool isMuted;
                float vol;
                epv.GetMute(out isMuted);
                epv.GetMasterVolumeLevelScalar(out vol);
                return string.Format("Mute: {0} | Volumen: {1:P0}", isMuted, vol);
            }
            return "No se pudo obtener el dispositivo";
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $csharp -Language CSharp -ErrorAction SilentlyContinue
    
    Write-Host "[1/2] Desmuteando parlantes y fijando volumen al 80%..." -ForegroundColor Cyan
    [AudioController.CoreAudioHelper]::SetVolumeAndUnmute([float]0.80)
    
    $status = [AudioController.CoreAudioHelper]::GetStatus()
    Write-Host "[OK] Estado actual de los parlantes: $status" -ForegroundColor Green

    # Reproducir tono de confirmacion
    Write-Host "[2/2] Reproduciendo sonido de prueba..." -ForegroundColor Yellow
    [System.Media.SystemSounds]::Asterisk.Play()
} catch {
    Write-Host "Error controlando audio: $($_.Exception.Message)" -ForegroundColor Red
}
