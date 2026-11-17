# FocusEye+

**웹캠 기반 학습 집중도 분석 시스템**

웹캠으로 공부하는 사람의 얼굴과 눈을 인식해서 집중 상태를 실시간으로 분석합니다.
집중도를 0~100점 점수와 그래프로 보여 주고, 집중도가 떨어지면 알려 줍니다.

> 2026년 인공지능 기초 프로젝트 (20601)

## 왜 만들었나

- 온라인 학습이 늘면서 스마트폰, 딴생각 등으로 집중력이 쉽게 떨어진다.
- 내가 얼마나 집중하고 있는지 스스로 객관적으로 알기 어렵다.
- 집중도를 숫자로 보여 주면 학습 습관을 고치고 자기주도 학습에 도움이 된다.

## 주요 기능

| 기능 | 설명 |
|---|---|
| 눈 감김 감지 | 눈을 오래 감고 있으면 졸음으로 판단 |
| 얼굴 방향 추정 | 고개를 옆·아래로 돌렸는지 확인 |
| 시선 방향 추정 | 눈동자가 화면 밖을 보는지 확인 |
| 자리 이탈 감지 | 얼굴이 화면에서 사라졌는지 확인 |
| 집중도 점수 | 위 정보를 합쳐 0~100점으로 계산 |
| 그래프·알림·기록 | 시간별 그래프, 집중도 하락 알림, 세션 기록 저장 |

## 사용 기술

- **Python**: 프로그래밍 언어
- **OpenCV**: 웹캠 영상 읽기, 화면에 그리기
- **MediaPipe (Face Landmarker)**: 얼굴의 점 478개(눈, 코, 입, 눈동자 등) 위치 인식

## 개인정보 보호 원칙

- **얼굴 영상은 절대 저장하지 않습니다.** 메모리에서 실시간 분석만 하고 바로 버립니다.
- 저장하는 것은 **집중도 점수 같은 숫자 데이터뿐**입니다.
- 모든 분석은 내 컴퓨터 안에서만 이루어지고, 인터넷으로 영상을 보내지 않습니다.
  (인터넷은 처음 실행할 때 AI 모델 파일을 한 번 내려받을 때만 씁니다.)

## 개발 단계

- [x] **1단계**: 웹캠 화면 띄우기 + 얼굴 랜드마크 표시
- [ ] 2단계: 눈 감김 감지
- [ ] 3단계: 얼굴 방향, 시선 방향 추정
- [ ] 4단계: 자리 이탈 감지
- [ ] 5단계: 집중도 점수 계산
- [ ] 6단계: 그래프, 알림, 세션 기록

---

## 내 컴퓨터에서 설치하고 실행하기

### 준비물

- 웹캠이 있는 컴퓨터: **Windows 10/11 (64비트)** 또는 **Apple Silicon Mac (M1 이상)**
  - 인텔 CPU 맥은 MediaPipe가 지원하지 않습니다.
- **Python 3.10 ~ 3.13** ([python.org](https://www.python.org/downloads/)에서 설치)
  - Windows 설치 화면에서 **"Add python.exe to PATH"를 꼭 체크**하세요.
- Git (저장소 내려받기용) 또는 GitHub에서 ZIP으로 내려받기

### 1. 코드 내려받기

```bash
git clone https://github.com/User999999428/AI.git
```

```bash
cd AI
```

### 2. 가상환경 만들고 켜기

가상환경은 이 프로젝트 전용 패키지 상자입니다. 다른 프로젝트와 섞이지 않게 해 줍니다.

**Windows (PowerShell 또는 명령 프롬프트)**

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

> PowerShell에서 "스크립트를 실행할 수 없습니다" 오류가 나면 먼저
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 를 실행하고 다시 시도하세요.

**Mac (터미널)**

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

켜지면 줄 앞에 `(.venv)`가 붙습니다. 터미널을 새로 열 때마다 이 "켜기" 명령을 다시 실행해야 합니다.

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 실행

```bash
python main.py
```

- 처음 실행하면 AI 모델 파일(약 4MB)을 `models/` 폴더에 자동으로 내려받습니다.
- 웹캠 창이 뜨고 얼굴에 그물망과 눈 윤곽이 그려지면 성공입니다.
- **종료: 영상 창을 한 번 클릭한 뒤 `q` 키** (창의 X 버튼도 됩니다)
- 웹캠이 여러 개라면 번호를 바꿔 보세요: `python main.py --camera 1`

### 자주 나는 문제

| 증상 | 해결 |
|---|---|
| `웹캠을 열 수 없습니다` | 다른 프로그램(Zoom, 카메라 앱 등)이 웹캠을 쓰고 있지 않은지 확인. `--camera 1` 시도 |
| Mac에서 화면이 검거나 바로 꺼짐 | 시스템 설정 → 개인정보 보호 및 보안 → 카메라 → 터미널(또는 VS Code) 허용 후 재실행 |
| Windows에서 카메라 접근 거부 | 설정 → 개인 정보 → 카메라 → "데스크톱 앱이 카메라에 액세스하도록 허용" 켜기 |
| `No module named ...` | 가상환경이 켜져 있는지(`(.venv)` 표시) 확인 후 `pip install -r requirements.txt` 다시 실행 |
| 모델 다운로드 실패 | 인터넷 연결 확인. 학교망이라면 아래 주소의 파일을 직접 받아 `models/face_landmarker.task`로 저장 |
| `cv2` 관련 이상한 오류 | `pip uninstall opencv-python` 후 `pip install -r requirements.txt` (OpenCV 두 개가 겹친 경우) |

모델 파일 주소:
`https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`

## 파일 구조

```
AI/
├── main.py                 # 실행 파일 (웹캠 루프)
├── focuseye/
│   ├── face_tracker.py     # MediaPipe로 얼굴 랜드마크 찾기
│   └── drawing.py          # 화면에 랜드마크·상태 글자 그리기
├── models/                 # AI 모델 (자동 다운로드, git에 안 올림)
├── requirements.txt        # 필요 패키지 목록
├── README.md
└── CLAUDE.md               # AI 도우미(Claude)용 작업 규칙
```
