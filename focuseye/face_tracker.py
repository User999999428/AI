"""얼굴 랜드마크 찾기 담당 모듈 (1단계).

MediaPipe의 FaceLandmarker를 이용해 얼굴의 점 478개(랜드마크)를 찾는다.
- 0~467번: 얼굴 윤곽, 눈, 코, 입 등
- 468~477번: 눈동자(홍채) 위치  → 3단계 시선 추정에서 사용

[개인정보 원칙]
이 모듈은 영상을 받아 '점 좌표(숫자)'만 돌려준다.
영상은 어디에도 저장하지 않는다.
"""

import time
import urllib.request
from pathlib import Path

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

# 얼굴 랜드마크 AI 모델 파일 (Google 공식 배포본)
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)
# 모델은 프로젝트 폴더 안 models/ 에 저장한다 (git에는 올리지 않음)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task"


def ensure_model(path: Path = MODEL_PATH) -> Path:
    """모델 파일이 없으면 처음 한 번만 내려받는다."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[안내] 얼굴 인식 모델을 내려받는 중... ({path.name}, 약 4MB)")
        urllib.request.urlretrieve(MODEL_URL, path)
        print("[안내] 다운로드 완료")
    return path


class FaceTracker:
    """웹캠 프레임을 넣으면 얼굴 랜드마크를 돌려주는 클래스."""

    def __init__(self, num_faces: int = 1):
        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(ensure_model())),
            # VIDEO 모드: 연속된 프레임을 처리. 앞 프레임 정보를 이용해 더 빠르고 안정적이다.
            running_mode=vision.RunningMode.VIDEO,
            num_faces=num_faces,  # 공부하는 사람 1명만 분석
            # 5단계 이후 표정 분석 등에 쓸 수 있는 옵션 (지금은 끔)
            output_face_blendshapes=False,
            # 3단계 얼굴 방향(고개 각도) 계산에 쓸 '얼굴 회전 행렬'을 미리 켜 둔다
            output_facial_transformation_matrixes=True,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._start = time.monotonic()
        self._last_ts = -1

    def process(self, frame_bgr):
        """BGR 이미지(OpenCV 형식) 한 장을 분석해 결과를 돌려준다.

        반환값 result.face_landmarks : 얼굴별 점 목록.
            얼굴이 없으면 빈 리스트 [] 이다.
            각 점은 x, y가 0~1 사이 비율 값이다. (화면 왼쪽 위가 0, 오른쪽 아래가 1)
        """
        # OpenCV는 BGR 순서, MediaPipe는 RGB 순서를 쓰므로 색 순서를 바꾼다
        rgb = frame_bgr[:, :, ::-1].copy()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO 모드는 '시간(ms)'이 계속 커져야 한다
        ts = int((time.monotonic() - self._start) * 1000)
        if ts <= self._last_ts:
            ts = self._last_ts + 1
        self._last_ts = ts

        return self._landmarker.detect_for_video(mp_image, ts)

    def close(self):
        self._landmarker.close()

    # with 문으로 쓰면 끝날 때 자동으로 close() 된다
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
