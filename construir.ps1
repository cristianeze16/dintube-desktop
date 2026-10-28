# Arma DinTube de escritorio: dist\DinTube\DinTube.exe y, si está Inno Setup, instalador\DinTube-Setup.exe
# Uso: doble click en construir.bat (o .\construir.ps1 [-Origen C:\dev\dintube])
# -Version: "3.0.4" (lo calcula la Action de GitHub a partir de VERSION en dintube; en builds locales 0.0.0)
param([string]$Origen = (Join-Path $PSScriptRoot "..\dintube"), [string]$Version = "0.0.0")
$ErrorActionPreference = "Stop"
$Origen = (Resolve-Path $Origen).Path  # antes de cambiar de carpeta: puede ser relativa
Set-Location $PSScriptRoot

# 1. Entorno propio (no usa el venv de dintube)
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creando .venv..."
    py -3 -m venv .venv
}
$py = ".venv\Scripts\python.exe"
& $py -m pip install -q --upgrade pip
& $py -m pip install -q --upgrade -r (Join-Path $Origen "requirements.txt") -r requirements-escritorio.txt
if ($LASTEXITCODE) { throw "Falló pip install" }

$env:DINTUBE_VERSION = $Version

# 2. Copiar y parchear servidor.py, descargar.py y web/
& $py preparar.py $Origen
if ($LASTEXITCODE) { throw "Falló preparar.py" }

# 3. ffmpeg, ffprobe y deno (se bajan una sola vez; borrá build\bin para actualizarlos)
$bin = "build\bin"
New-Item -ItemType Directory -Force $bin | Out-Null
$tmp = Join-Path $env:TEMP "dintube-build"
New-Item -ItemType Directory -Force $tmp | Out-Null
if (-not (Test-Path "$bin\ffmpeg.exe")) {
    Write-Host "Bajando ffmpeg..."
    $zip = "$tmp\ffmpeg.zip"
    Invoke-WebRequest "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile $zip
    Expand-Archive $zip "$tmp\ffmpeg" -Force
    Get-ChildItem "$tmp\ffmpeg" -Recurse -Include ffmpeg.exe, ffprobe.exe | Copy-Item -Destination $bin
}
if (-not (Test-Path "$bin\deno.exe")) {
    Write-Host "Bajando deno..."
    $zip = "$tmp\deno.zip"
    Invoke-WebRequest "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip" -OutFile $zip
    Expand-Archive $zip $bin -Force
}

# 4. Empaquetar con PyInstaller (carpeta, no un solo exe: arranca mucho más rápido)
& $py -m PyInstaller app_escritorio.py --noconfirm --clean --noconsole --onedir `
    --name DinTube --icon build\dintube.ico `
    --paths build\src --hidden-import servidor --hidden-import descargar `
    --add-data "build\src;src" --add-data "build\web;web" --add-data "build\bin;bin" --add-data "build\version.txt;." `
    --collect-all yt_dlp --collect-all yt_dlp_ejs --collect-data segno
if ($LASTEXITCODE) { throw "Falló PyInstaller" }
Write-Host "`nApp lista: dist\DinTube\DinTube.exe"

# 5. Instalador (opcional): https://jrsoftware.org/isdl.php
$iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
          "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($iscc) {
    & $iscc "/DVersion=$Version" instalador.iss
    if ($LASTEXITCODE) { throw "Falló Inno Setup" }
    Write-Host "Instalador listo: instalador\DinTube-Setup.exe"
} else {
    Write-Host "No encontré Inno Setup 6: instalalo para generar DinTube-Setup.exe (la app en dist\ ya funciona igual)."
}
