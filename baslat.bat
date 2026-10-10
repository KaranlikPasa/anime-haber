@echo off
chcp 65001 >nul
title Anime Haber - Nyaa.si Takipçisi

echo ======================================================
echo          ANİME HABER - Nyaa.si Takipçisi
echo ======================================================
echo.

cd /d "%~dp0"

:: Python kontrolü
set "PYTHON_CMD=python"
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "py" (
        set "PYTHON_CMD=py"
    ) else (
        echo [HATA] Python bulunamadi! Lutfen Python'un kurulu oldugundan emin olun.
        pause
        exit /b 1
    )
)

echo [1/2] Moduller dogrulaniyor...
"%PYTHON_CMD%" -m pip install -r requirements.txt --quiet --no-warn-script-location

echo [2/2] Anime Haber baslatiliyor...
echo.

"%PYTHON_CMD%" main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [HATA] Uygulama bir hata ile kapandi!
    echo Ayrintilar icin 'anime_haber.log' dosyasina bakabilirsiniz.
    pause
)
