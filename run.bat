@echo off
chcp 65001 > nul
REM ===== FocusEye+ 실행 스크립트 (Windows) =====
REM 더블클릭하면 가상환경을 켜고 main.py를 실행한다.
REM 웹캠 번호를 바꾸려면 명령창에서 실행: run.bat --camera 1
REM (Windows 명령창은 한글이 깨질 수 있어서 화면 메시지는 영어로 쓴다)

REM 이 파일이 있는 폴더(프로젝트 폴더)로 이동
cd /d "%~dp0"

REM 가상환경이 없으면 setup.bat부터 실행해야 한다
if not exist .venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found.
    echo         Run setup.bat first, then try again.
    pause
    exit /b 1
)

REM 가상환경 켜기 (call을 붙여야 끝난 뒤 이 파일로 돌아온다)
call .venv\Scripts\activate.bat

echo Starting FocusEye+ ... (click the video window and press q to quit)
REM %* : run.bat 뒤에 붙인 옵션을 main.py에 그대로 전달
python main.py %*

REM 오류로 끝났으면 창이 바로 닫히지 않게 멈춘다 (오류 메시지를 읽을 수 있게)
if errorlevel 1 (
    echo.
    echo [ERROR] FocusEye+ stopped with an error. Check the message above.
    pause
    exit /b 1
)
