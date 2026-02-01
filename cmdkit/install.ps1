$ErrorActionPreference = "Stop"

$Repo = "arnav-khandelwal/cmdkit"
$Asset = "cmdkit-windows.exe"
$InstallDir = "$env:LOCALAPPDATA\cmdkit"

$Url = "https://github.com/$Repo/releases/latest/download/$Asset"

Write-Host "⬇️ Downloading cmdkit for Windows..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

$BinaryPath = "$InstallDir\cmdkit.exe"
Invoke-WebRequest $Url -OutFile $BinaryPath

Write-Host "📦 Installing cmdkit to $InstallDir"

# Add to PATH if not already there
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$UserPath;$InstallDir",
        "User"
    )
    Write-Host "🔧 Added cmdkit to PATH (restart terminal required)"
}

Write-Host "✅ cmdkit installed successfully!"
Write-Host "👉 Run: cmdkit --help"