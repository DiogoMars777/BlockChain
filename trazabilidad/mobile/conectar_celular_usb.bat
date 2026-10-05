@echo off
chcp 65001 > nul
echo =======================================================
echo   CONEXIÓN USB DE CELULAR A BACKEND LOCAL (PORT REVERSE)
echo =======================================================
echo.

set ADB_PATH=adb
where adb >nul 2>nul
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" (
        set ADB_PATH="%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
    ) else (
        echo [ERROR] No se encontro adb.exe en el PATH ni en %LOCALAPPDATA%\Android\Sdk\platform-tools.
        pause
        exit /b 1
    )
)

echo Verificando dispositivos conectados por USB...
%ADB_PATH% devices
echo.

echo Configurando reenvío de puerto tcp:8000 -> tcp:8000...
%ADB_PATH% reverse tcp:8000 tcp:8000
if %errorlevel% equ 0 (
    echo.
    echo [EXITO] Puerto 8000 reenviado correctamente.
    echo Ahora tu celular conectado por USB puede ingresar con la URL:
    echo     http://127.0.0.1:8000/api/v1
    echo.
    echo Si prefieres usar Wi-Fi (sin cable USB), tu IP en red local es:
    echo     http://192.168.0.103:8000/api/v1
) else (
    echo.
    echo [ADVERTENCIA] No se pudo ejecutar adb reverse. Verifica que tu celular tenga Depuracion USB activada.
)

echo.
pause
