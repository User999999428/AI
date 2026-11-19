"""눈 감김 감지 모듈 (2단계).

[원리: EAR (Eye Aspect Ratio, 눈 종횡비)]
눈 하나에서 점 6개를 고른다.

        p2    p3              p1, p4 : 눈의 양 끝 (가로)
    p1            p4          p2, p6 : 위·아래 눈꺼풀 한 쌍 (세로 1)
        p6    p5              p3, p5 : 위·아래 눈꺼풀 한 쌍 (세로 2)

         |p2 - p6| + |p3 - p5|        (세로 길이 2개의 합)
  EAR = ─────────────────────────
             2 × |p1 - p4|            (가로 길이의 2배)

- 눈을 뜨면 세로 길이가 길어서 EAR이 크다 (약 0.25~0.35).
- 눈을 감으면 세로 길이가 0에 가까워져서 EAR도 0에 가까워진다.
- '비율'이라서 카메라에 가까이 있든 멀리 있든 값이 거의 같다.

[졸음 판단]
EAR이 기준값보다 작은 상태가 정해진 시간(예: 1.5초) 이상 이어지면 졸음.
짧은 눈 깜빡임(0.1~0.4초)은 졸음으로 보지 않는다.

[보정]
눈 뜬 EAR은 사람마다 달라서, c 키를 누르면 3초 동안 내 눈 뜬 EAR을 재고
그 값 × 0.6 을 기준값으로 정한다.

자세한 설명(보고서용): docs/stage2_eye_closure.md
"""

import math
from dataclasses import dataclass

# MediaPipe 얼굴 랜드마크 번호 (순서: p1, p2, p3, p4, p5, p6)
# 화면에서 '왼쪽에 보이는 눈' / '오른쪽에 보이는 눈' 기준으로 이름을 붙였다.
# (화면을 좌우 반전해서 보여 주므로 사람 기준 왼쪽·오른쪽과 헷갈리지 않게 화면 기준으로 통일)
SCREEN_LEFT_EYE = [33, 160, 158, 133, 153, 144]
SCREEN_RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def _distance(a, b):
    """두 점 사이의 거리 (피타고라스 정리)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def eye_aspect_ratio(points):
    """점 6개 [(x, y), ...] (p1~p6 순서)로 EAR을 계산한다."""
    p1, p2, p3, p4, p5, p6 = points
    vertical = _distance(p2, p6) + _distance(p3, p5)  # 세로 길이 2개
    horizontal = _distance(p1, p4)  # 가로 길이
    if horizontal == 0:
        return 0.0
    return vertical / (2.0 * horizontal)


def eye_points(face_landmarks, indices, width, height):
    """랜드마크에서 눈 점 6개를 '픽셀 좌표'로 꺼낸다.

    랜드마크의 x, y는 0~1 비율 값이다. 화면은 보통 가로가 더 길어서
    비율 그대로 거리를 재면 가로·세로 길이가 왜곡된다.
    그래서 화면 크기(width, height)를 곱해 실제 픽셀 위치로 바꾼다.
    """
    return [(face_landmarks[i].x * width, face_landmarks[i].y * height) for i in indices]


@dataclass
class EyeState:
    """한 프레임의 눈 상태 분석 결과 (숫자 데이터만 담는다)."""

    ear_left: float  # 화면 왼쪽 눈의 EAR
    ear_right: float  # 화면 오른쪽 눈의 EAR
    ear: float  # 두 눈 평균 (흔들림 줄인 값). 판단에는 이 값을 쓴다
    is_closed: bool  # 지금 눈을 감았는가
    closed_seconds: float  # 지금까지 계속 감고 있던 시간 (초)
    is_drowsy: bool  # 졸음인가 (감은 시간이 기준 이상)
    calibration_left: float  # 보정 중이면 남은 시간(초), 보정 중이 아니면 0


class EyeStateDetector:
    """프레임마다 EAR을 계산하고, 눈 감은 시간을 재서 졸음을 판단한다."""

    def __init__(self, ear_threshold, drowsy_seconds, smoothing=0.5,
                 calibration_seconds=3.0, calibration_ratio=0.6):
        self.ear_threshold = ear_threshold
        self.drowsy_seconds = drowsy_seconds
        self.smoothing = smoothing
        self.calibration_seconds = calibration_seconds
        self.calibration_ratio = calibration_ratio
        self._smoothed_ear = None  # 흔들림을 줄인 EAR 값
        self._closed_since = None  # 눈을 감기 시작한 시각 (뜨고 있으면 None)
        self._calib_end = None  # 보정이 끝나는 시각 (보정 중이 아니면 None)
        self._calib_samples = []  # 보정 중에 모은 EAR 값들
        self.calibration_done = None  # 보정이 막 끝난 프레임에만 새 기준값이 들어간다
        self.last_open_ear = None  # 마지막 보정에서 잰 '눈 뜬 EAR'

    # ── 보정: 내 눈에 맞는 기준값 자동으로 정하기 ──────────────

    def start_calibration(self, now):
        """보정 시작. 지금부터 calibration_seconds 동안 눈 뜬 EAR을 모은다."""
        self._calib_end = now + self.calibration_seconds
        self._calib_samples = []

    def _finish_calibration(self):
        """모은 EAR로 새 기준값을 정한다. 새 기준값을 돌려준다 (실패하면 None)."""
        self._calib_end = None
        if not self._calib_samples:
            return None  # 보정 중에 얼굴이 한 번도 안 보였음
        # '가운데 값(중앙값)'을 쓴다. 보정 중에 눈을 깜빡여 EAR이 잠깐 작아져도
        # 평균과 달리 중앙값은 거의 영향을 받지 않는다.
        samples = sorted(self._calib_samples)
        open_ear = samples[len(samples) // 2]
        self.ear_threshold = round(open_ear * self.calibration_ratio, 3)
        self.last_open_ear = open_ear  # 화면·콘솔 안내용
        return self.ear_threshold

    # ── 매 프레임 분석 ────────────────────────────────────────

    def update(self, face_landmarks, width, height, now):
        """얼굴 랜드마크 한 세트를 넣으면 EyeState를 돌려준다.

        now: 현재 시각(초). time.monotonic() 값을 넣는다.
        """
        ear_left = eye_aspect_ratio(eye_points(face_landmarks, SCREEN_LEFT_EYE, width, height))
        ear_right = eye_aspect_ratio(eye_points(face_landmarks, SCREEN_RIGHT_EYE, width, height))
        ear = (ear_left + ear_right) / 2  # 두 눈 평균: 한쪽만 잘못 잡혀도 덜 흔들린다

        # 보정 중이면 EAR 값을 모으고, 시간이 다 되면 기준값을 새로 정한다
        self.calibration_done = None  # 이번 프레임에 보정이 끝났으면 새 기준값이 들어간다
        calibration_left = 0.0
        if self._calib_end is not None:
            self._calib_samples.append(ear)
            if now >= self._calib_end:
                self.calibration_done = self._finish_calibration()
            else:
                calibration_left = self._calib_end - now

        # 흔들림 줄이기: 이전 값과 새 값을 섞는다
        if self._smoothed_ear is None:
            self._smoothed_ear = ear
        else:
            self._smoothed_ear = self.smoothing * ear + (1 - self.smoothing) * self._smoothed_ear

        # 눈 감김 판단
        is_closed = self._smoothed_ear < self.ear_threshold

        # 감은 시간 재기: 감기 시작한 시각을 기억해 두고, 지금 시각과의 차이를 구한다
        if is_closed:
            if self._closed_since is None:
                self._closed_since = now
            closed_seconds = now - self._closed_since
        else:
            self._closed_since = None  # 눈을 뜨면 초기화
            closed_seconds = 0.0

        return EyeState(
            ear_left=ear_left,
            ear_right=ear_right,
            ear=self._smoothed_ear,
            is_closed=is_closed,
            closed_seconds=closed_seconds,
            # 보정 중에는 졸음 경고를 띄우지 않는다 (기준값을 정하는 중이라서)
            is_drowsy=closed_seconds >= self.drowsy_seconds and calibration_left == 0,
            calibration_left=calibration_left,
        )

    def reset(self):
        """얼굴이 안 보일 때 호출한다. 감은 시간 기록을 지운다.

        (얼굴이 사라진 것은 졸음이 아니라 '자리 이탈'이다 → 4단계에서 따로 처리)
        """
        self._smoothed_ear = None
        self._closed_since = None
