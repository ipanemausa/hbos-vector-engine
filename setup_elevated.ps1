# Setup elevated components for Tailscale, OpenSSH Server, and Bitwarden
$logFile = "$env:USERPROFILE\hbos-docs\setup_elevated.log"
Start-Transcript -Path $logFile -Append

Write-Host "=== [1/3] Installing Tailscale ==="
if (-not (Get-Command tailscale -ErrorAction SilentlyContinue) -and -not (Test-Path "C:\Program Files\Tailscale\tailscale.exe")) {
    winget install --id Tailscale.Tailscale -e --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "Tailscale already installed."
}

Write-Host "=== [2/3] Installing OpenSSH Server ==="
$sshdCap = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($sshdCap.State -ne 'Installed') {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
} else {
    Write-Host "OpenSSH Server capability already installed."
}

Start-Service sshd -ErrorAction SilentlyContinue
Set-Service sshd -StartupType Automatic -ErrorAction SilentlyContinue

# Harden sshd_config
$sshdConfig = "$env:ProgramData\ssh\sshd_config"
if (Test-Path $sshdConfig) {
    $cfg = Get-Content $sshdConfig -Raw
    if ($cfg -notmatch 'PubkeyAuthentication\s+yes') {
        $cfg = $cfg -replace '#?PubkeyAuthentication.*', 'PubkeyAuthentication yes'
    }
    if ($cfg -notmatch 'PasswordAuthentication\s+no') {
        $cfg = $cfg -replace '#?PasswordAuthentication.*', 'PasswordAuthentication no'
    }
    Set-Content -Path $sshdConfig -Value $cfg -Force
    Restart-Service sshd -ErrorAction SilentlyContinue
}

# Firewall rule for Tailscale CGNAT
Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object DisplayName -like '*OpenSSH*' | Set-NetFirewallRule -RemoteAddress 100.64.0.0/10 -ErrorAction SilentlyContinue

Write-Host "=== [3/3] Installing Bitwarden ==="
$bwInstalled = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match "Bitwarden" }) -or (Get-Command bitwarden -ErrorAction SilentlyContinue)
if (-not $bwInstalled) {
    winget install --id Bitwarden.Bitwarden -e --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "Bitwarden already installed."
}

Stop-Transcript
