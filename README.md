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
- [x] **2단계**: 눈 감김 감지 (원리 설명: [docs/stage2_eye_closure.md](docs/stage2_eye_closure.md))
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

### 2~3. 자동 설치 (추천)

설치 스크립트가 아래 2, 3번(가상환경 만들기 + 패키지 설치)을 한 번에 해 줍니다.

- **Windows**: 폴더에서 `setup.bat` 더블클릭
- **Mac**: 터미널에서 `bash setup.sh`

끝나면 가상환경을 켜고(아래 2번의 "켜기" 명령) 4번으로 넘어가세요.
직접 해 보고 싶다면 아래 2, 3번을 따라 하면 됩니다.

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

**Windows: `run.bat` 더블클릭 (가장 쉬움)**

- 가상환경을 켜고 `main.py`를 실행하는 것까지 한 번에 해 줍니다. 명령어를 입력할 필요가 없습니다.
- `setup.bat`을 먼저 한 번 실행해 두어야 합니다. 안 했다면 그렇게 하라는 안내가 나옵니다.
- 오류가 나면 창이 바로 닫히지 않고 멈추니, 메시지를 읽고 아무 키나 눌러 닫으세요.
- 웹캠 번호를 바꾸려면 명령 프롬프트에서 `run.bat --camera 1` 처럼 실행합니다.

**직접 실행 (Windows, Mac 모두)**: 가상환경을 켠 상태에서

```bash
python main.py
```

- 처음 실행하면 AI 모델 파일(약 4MB)을 `models/` 폴더에 자동으로 내려받습니다.
- 웹캠 창이 뜨고 얼굴에 그물망과 눈 윤곽이 그려지면 성공입니다.
- **종료: 영상 창을 한 번 클릭한 뒤 `q` 키** (창의 X 버튼도 됩니다)
- 웹캠이 여러 개라면 번호를 바꿔 보세요: `python main.py --camera 1`

### 화면 보는 법

| 표시 | 뜻 |
|---|---|
| `Face: OK` / `NOT FOUND` | 얼굴을 찾았는지 |
| `EAR: 0.30 (L .. / R ..)` | 눈이 얼마나 떠 있는지 (두 눈 평균, 화면 왼쪽/오른쪽 눈). 감으면 0에 가까워짐 |
| `Eyes: OPEN` / `CLOSED 0.8s` | 눈 상태와 계속 감고 있는 시간 |
| 막대 + 빨간 선 | 막대 = 현재 EAR, 빨간 선 = 기준값. 막대가 선보다 짧아지면 "감음" |
| 눈 위의 노란 점 | EAR 계산에 쓰는 점 (눈마다 6개) |
| `DROWSY! Wake up!` + 빨간 테두리 | 눈을 기준 시간(1.5초) 이상 감고 있음 = 졸음 |

### 키

| 키 | 기능 |
|---|---|
| `q` | 종료 |
| `c` | **눈 보정**: 3초 동안 눈을 편하게 뜨고 화면을 보면 내 눈에 맞게 기준값을 자동으로 정함 |

### 기준값 바꾸기 (사람마다 다름)

눈을 떴는데 `CLOSED`가 자주 뜨거나, 감았는데 `OPEN`으로 나오면 기준값을 바꿉니다.

1. **가장 쉬움: 실행 중 `c` 키**로 보정합니다. 이번 실행에만 적용되고, 결과가 콘솔(검은 창)에 나옵니다.
2. **이번 실행만 바꾸기**: 옵션을 붙여 실행합니다.

   ```bash
   python main.py --ear-threshold 0.2 --drowsy-seconds 2
   ```

   `run.bat`에서도 같은 옵션을 쓸 수 있습니다. 예: `run.bat --ear-threshold 0.2`
3. **항상 바꾸기**: [`focuseye/config.py`](focuseye/config.py)의 숫자를 고칩니다.

| 설정 | 기본값 | 뜻 |
|---|---|---|
| `EAR_THRESHOLD` | 0.18 | EAR이 이보다 작으면 "눈 감음" |
| `DROWSY_SECONDS` | 1.5 | 이 시간(초) 이상 계속 감으면 "졸음" |
| `CALIBRATION_RATIO` | 0.6 | 보정 때 "눈 뜬 EAR × 이 비율"을 기준값으로 씀 |

### 웹캠 없이 사진으로 검증하기

눈 뜬/감은 얼굴 사진 데이터셋(CEW)으로, 기준값 0.10~0.30에서 각각 정확도가 얼마인지 확인할 수 있습니다.
데이터 넣는 위치, 실행 방법, 라이선스는 [docs/dataset_cew.md](docs/dataset_cew.md)를 보세요.

```bash
python tools/eval_ear_photos.py
```

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

---

## 다른 컴퓨터에서 이어서 작업하기

코드는 GitHub에 올려 두고, 각 컴퓨터는 **받아서(pull) → 작업 → 올리기(push)**를 반복합니다.

### 무엇이 옮겨지고, 무엇이 안 옮겨지나

| 항목 | GitHub로 옮겨짐? | 새 컴퓨터에서는 |
|---|---|---|
| 코드, README, PROGRESS.md | O | `git pull`로 받음 |
| 가상환경 `.venv/` | X (컴퓨터마다 다름) | `setup.bat` / `setup.sh` 한 번 실행 |
| 모델 `models/` | X (용량 때문) | 첫 실행 때 자동 다운로드 |
| 외부 데이터셋 `data/` | X (재배포 금지) | 필요한 컴퓨터에서 직접 내려받아 넣기 |
| 얼굴 영상·사진 | X (애초에 저장 안 함) | - |

### 새 컴퓨터에서 처음 한 번

1. Python과 Git 설치 (Git: [git-scm.com](https://git-scm.com/downloads))
2. 위 "1. 코드 내려받기"대로 `git clone`
3. `setup.bat`(Windows) 또는 `bash setup.sh`(Mac) 실행
4. 커밋할 때 쓸 내 이름·이메일 등록 (컴퓨터마다 한 번)

```bash
git config --global user.name "내 이름"
```

```bash
git config --global user.email "GitHub에 등록한 이메일"
```

5. 처음 `git push` 할 때 GitHub 로그인 창이 뜨면 로그인합니다.

### 매번 작업할 때

**시작 전: 최신 코드 받기** (다른 컴퓨터에서 한 작업을 가져옴)

```bash
git pull
```

그리고 `PROGRESS.md`를 열어 어디까지 했는지 확인합니다.
`requirements.txt`가 바뀌었다면 설치 스크립트를 한 번 더 실행하세요.

**끝난 후: 올리기** (`PROGRESS.md`의 작업 일지도 한 줄 적어 두기)

```bash
git add .
```

```bash
git commit -m "무엇을 했는지 한 줄 설명"
```

```bash
git push
```

> **push를 잊지 마세요.** 올리지 않으면 다른 컴퓨터에서 이어서 할 수 없습니다.
> 같은 내용을 두 컴퓨터에서 동시에 고치면 충돌이 날 수 있으니, 항상 pull 먼저!

## 파일 구조

```
AI/
├── main.py                 # 실행 파일 (웹캠 루프)
├── focuseye/
│   ├── config.py           # 설정값 (눈 감김 기준값 등) ← 여기 숫자만 바꾸면 됨
│   ├── face_tracker.py     # MediaPipe로 얼굴 랜드마크 찾기
│   ├── eye_state.py        # 2단계: EAR 계산, 눈 감김·졸음 판단, 보정
│   └── drawing.py          # 화면에 랜드마크·상태 글자 그리기
├── tools/
│   └── eval_ear_photos.py  # 웹캠 없이 사진(CEW 등)으로 EAR 기준값별 정확도 검증
├── results/                # 검증 결과 숫자 요약 (CSV, 사진 없음)
├── docs/
│   ├── stage2_eye_closure.md  # 눈 감김 감지 원리 (보고서용)
│   └── dataset_cew.md      # CEW 데이터셋 출처·라이선스·사용법
├── models/                 # AI 모델 (자동 다운로드, git에 안 올림)
├── data/                   # 외부 데이터셋 (예: CEW). 재배포 금지 → git에 절대 안 올림
│                           #   필요한 컴퓨터마다 직접 내려받아 이 폴더에 넣기
├── requirements.txt        # 필요 패키지 목록
├── setup.bat / setup.sh    # 새 컴퓨터 자동 설치 (Windows / Mac)
├── run.bat                 # Windows: 더블클릭으로 실행
├── PROGRESS.md             # 진행 기록: 어디까지 했나, 다음 할 일
├── README.md
└── CLAUDE.md               # AI 도우미(Claude)용 작업 규칙
```
