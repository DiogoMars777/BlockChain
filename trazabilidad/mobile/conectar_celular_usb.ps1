# Script PowerShell para reenviar el puerto 8000 a un celular Android conectado por USB
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   CONEXION USB DE CELULAR A BACKEND LOCAL (ADB REVERSE)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

$adb = "adb"
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
    $sdkAdb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
    if (Test-Path $sdkAdb) {
        $adb = $sdkAdb
    } else {
        Write-Error "No se encontro adb.exe en el PATH ni en el SDK de Android."
        exit 1
    }
}

Write-Host "Dispositivos conectados:" -ForegroundColor Yellow
& $adb devices

Write-Host "`nReenviando puerto tcp:8000 -> tcp:8000..." -ForegroundColor Yellow
& $adb reverse tcp:8000 tcp:8000

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[EXITO] Reenvio de puerto 8000 completado." -ForegroundColor Green
    Write-Host "URL para el celular por USB: http://127.0.0.1:8000/api/v1" -ForegroundColor Green
    Write-Host "URL alternativa por Wi-Fi:   http://192.168.0.103:8000/api/v1" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] Fallo adb reverse. Asegurate de tener Depuracion USB habilitada en tu telefono." -ForegroundColor Red
}
