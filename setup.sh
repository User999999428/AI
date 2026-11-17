#!/usr/bin/env bash
# ===== FocusEye+ 설치 스크립트 (Mac) =====
# 새 컴퓨터에서 처음 한 번 실행:  bash setup.sh
# 하는 일: 가상환경(.venv) 만들기 -> 필요한 패키지 설치
set -e

# 이 스크립트가 있는 폴더(프로젝트 폴더)로 이동
cd "$(dirname "$0")"

if ! command -v python3 > /dev/null; then
    echo "[오류] python3를 찾을 수 없습니다. python.org 에서 설치하세요."
    exit 1
fi

if [ ! -d .venv ]; then
    echo "[1/2] 가상환경 만드는 중..."
    python3 -m venv .venv
else
    echo "[1/2] 가상환경이 이미 있습니다. 건너뜀"
fi

echo "[2/2] 패키지 설치 중... (처음에는 몇 분 걸릴 수 있음)"
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo
echo "설치 완료! 실행 방법:"
echo "  source .venv/bin/activate"
echo "  python main.py"
