@echo off
REM ===== FocusEye+ 설치 스크립트 (Windows) =====
REM 새 컴퓨터에서 처음 한 번 더블클릭하거나, 명령 프롬프트에서 setup.bat 실행.
REM 하는 일: 가상환경(.venv) 만들기 -> 필요한 패키지 설치
REM (Windows 명령창은 한글이 깨질 수 있어서 화면 메시지는 영어로 쓴다)

REM 이 파일이 있는 폴더(프로젝트 폴더)로 이동
cd /d "%~dp0"

REM Python이 설치되어 있는지 확인
where python > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install it from python.org
    echo         and check "Add python.exe to PATH" during install.
    pause
    exit /b 1
)

REM 가상환경이 없을 때만 새로 만든다
if not exist .venv (
    echo [1/2] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/2] Virtual environment already exists. Skipped.
)

REM requirements.txt에 적힌 패키지 설치
echo [2/2] Installing packages... (first time may take a few minutes)
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Package install failed. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo Done! To run:
echo   .venv\Scripts\activate
echo   python main.py
pause
