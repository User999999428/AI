# CLAUDE.md

FocusEye+ 작업 시 지켜야 할 규칙. 프로젝트 소개는 README.md 참고.

## 프로젝트 한 줄 요약

웹캠 영상에서 얼굴·눈을 인식해 눈 감김, 얼굴 방향, 시선 방향, 자리 이탈을 분석하고
집중도를 0~100점과 그래프로 보여 주며, 집중도가 낮으면 알리는 Python 프로그램.

## 반드시 지킬 원칙

1. **얼굴 영상·사진을 절대 파일로 저장하지 않는다.**
   - `cv2.imwrite`, `cv2.VideoWriter`, 스크린샷 저장 등 금지.
   - 저장 가능한 것은 숫자 데이터(점수, 시각, 각도, 상태 등)뿐.
   - 영상을 인터넷으로 보내지 않는다. 분석은 모두 로컬에서.
2. **주석은 한국어로, 고등학생이 이해할 수 있게 쉽게** 쓴다.
   - 사용자는 코드를 이해하면서 진행하고 싶어 한다. 왜 그렇게 하는지도 짧게 설명.
   - 화면(`cv2.putText`)에 쓰는 글자는 영어 (OpenCV 기본 글꼴이 한글 미지원).
3. **단계별로 진행한다.** 요청받은 단계까지만 구현하고, 다음 단계 코드는 미리 만들지 않는다.
   - 단계가 끝나면 사용자가 확인할 항목을 알려 준다.
4. 코드는 단순하게. 고급 문법·과한 추상화보다 읽기 쉬운 코드를 우선한다.

## 여러 컴퓨터에서 작업

사용자는 여러 컴퓨터(Windows/Mac, 클라우드 세션)를 오가며 작업한다.
- **작업 시작 시 `PROGRESS.md`를 먼저 읽고** 현재 단계와 사용자 확인 결과를 파악한다.
- **작업이 끝나면 `PROGRESS.md`를 갱신**한다 (현재 상태, 확인 목록, 작업 일지 한 줄).
- README 단계 체크박스, CLAUDE.md 단계 목록도 함께 맞춘다.
- 패키지를 추가하면 `requirements.txt`에 넣는다 (`setup.bat`/`setup.sh`가 이 파일로 설치).
- 컴퓨터마다 다른 것(`.venv/`, `models/`)은 커밋하지 않는다.

## 개발 단계 (진행 상황은 README 체크박스와 맞춘다)

1. 웹캠 화면 + 얼굴 랜드마크 표시 ← 완료
2. 눈 감김 감지
3. 얼굴 방향, 시선 방향 추정
4. 자리 이탈 감지
5. 집중도 점수 계산
6. 그래프, 알림, 세션 기록

## 기술 메모

- **MediaPipe 1.2.3 고정.** 1.x에는 `mp.solutions`(예전 face_mesh)가 없다.
  `mediapipe.tasks.python.vision.FaceLandmarker` (Tasks API)만 사용한다.
  - 실행 모드는 `RunningMode.VIDEO`, `detect_for_video(image, timestamp_ms)` 호출.
    timestamp는 반드시 계속 증가해야 한다 (`FaceTracker.process`가 처리).
  - 그리기는 `vision.drawing_utils`, `vision.drawing_styles`, `vision.FaceLandmarksConnections`.
  - 모델 파일 `models/face_landmarker.task`는 첫 실행 시 자동 다운로드 (git 제외).
- 랜드마크는 478개. 0~467 얼굴, 468~477 홍채(눈동자). 좌표 x, y는 0~1 비율.
- `output_facial_transformation_matrixes=True`가 켜져 있음 → 3단계 고개 각도 계산에 사용.
- OpenCV는 `opencv-contrib-python`만 쓴다 (mediapipe 의존성). `opencv-python`을 추가하면 충돌.
- 프레임은 `cv2.flip(frame, 1)`로 좌우 반전된 상태로 분석한다 (거울 화면).
  좌/우 판단 로직을 짤 때 이 점을 고려할 것.

## 파일 구조

- `main.py`: 웹캠 루프 (읽기 → 분석 → 그리기 → 표시, q로 종료)
- `focuseye/face_tracker.py`: `FaceTracker` 클래스, 모델 다운로드
- `focuseye/drawing.py`: 랜드마크·상태 텍스트 그리기
- `setup.bat` / `setup.sh`: 새 컴퓨터용 설치 스크립트 (.venv 생성 + requirements 설치)
- `run.bat`: Windows 더블클릭 실행 (.venv 켜기 → `python main.py`, 오류 시 창 멈춤)
  - `main.py`는 오류면 종료 코드 1을 돌려줘야 한다 (run.bat이 이것으로 오류를 판단).
  - `.bat` 파일의 화면 메시지(echo)는 영어, 주석(REM)은 한국어. 맨 위에 `chcp 65001`.
- `PROGRESS.md`: 진행 상태·확인 목록·작업 일지
- 새 분석 기능은 `focuseye/` 안에 기능별 모듈로 추가한다 (예: `eye_state.py`).

## 테스트

- 개발 환경(클라우드)에는 웹캠이 없다. 웹캠 동작 확인은 사용자 PC에서 한다.
- 로직 검증은 얼굴 사진을 `FaceTracker.process()`에 넣어 확인할 수 있다.
  테스트용 이미지는 저장소에 커밋하지 않는다.
- 리눅스 컨테이너에서는 `libegl1`, `libgles2`가 없으면 MediaPipe가 로드되지 않는다.
