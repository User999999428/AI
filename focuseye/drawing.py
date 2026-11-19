"""화면에 그리기 담당 모듈.

랜드마크(얼굴 점)와 상태 글자를 웹캠 화면 위에 그린다.
"""

import cv2
from mediapipe.tasks.python import vision

_draw = vision.drawing_utils
_styles = vision.drawing_styles
_conn = vision.FaceLandmarksConnections


def draw_face_landmarks(frame, face_landmarks):
    """얼굴 한 개의 랜드마크를 화면에 그린다.

    - 얼굴 그물망(tesselation): 얼굴 전체를 덮는 얇은 선
    - 윤곽(contours): 눈, 눈썹, 입, 얼굴 테두리
    - 홍채(iris): 눈동자
    """
    # 1) 얼굴 그물망
    _draw.draw_landmarks(
        image=frame,
        landmark_list=face_landmarks,
        connections=_conn.FACE_LANDMARKS_TESSELATION,
        landmark_drawing_spec=None,  # 점은 그리지 않고 선만 그린다
        connection_drawing_spec=_styles.get_default_face_mesh_tesselation_style(),
    )
    # 2) 눈·눈썹·입·얼굴 윤곽
    _draw.draw_landmarks(
        image=frame,
        landmark_list=face_landmarks,
        connections=_conn.FACE_LANDMARKS_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=_styles.get_default_face_mesh_contours_style(),
    )
    # 3) 양쪽 눈동자
    _draw.draw_landmarks(
        image=frame,
        landmark_list=face_landmarks,
        connections=_conn.FACE_LANDMARKS_LEFT_IRIS + _conn.FACE_LANDMARKS_RIGHT_IRIS,
        landmark_drawing_spec=None,
        connection_drawing_spec=_styles.get_default_face_mesh_iris_connections_style(),
    )


def draw_eye_points(frame, points_list):
    """EAR 계산에 쓰는 눈 점(눈마다 6개)을 노란 점으로 표시한다.

    어떤 점으로 계산하는지 눈으로 확인할 수 있게 하려는 것.
    """
    for points in points_list:
        for x, y in points:
            cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 255), -1)  # 노란색


def draw_eye_state(frame, state, ear_threshold):
    """EAR 숫자, 눈 상태, EAR 막대그래프를 왼쪽에 표시한다."""
    # 1) EAR 숫자: 평균값과 각 눈의 값, 기준값
    cv2.putText(
        frame,
        f"EAR: {state.ear:.2f}  (L {state.ear_left:.2f} / R {state.ear_right:.2f})",
        (10, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
    )

    # 2) 눈 상태: 뜸(초록) / 감음(주황) + 감은 시간
    if state.is_closed:
        text, color = f"Eyes: CLOSED {state.closed_seconds:.1f}s", (0, 165, 255)
    else:
        text, color = "Eyes: OPEN", (0, 200, 0)
    cv2.putText(frame, text, (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # 3) EAR 막대: 0 ~ 0.4 범위를 길이 200픽셀로 나타내고, 기준값 위치에 빨간 선을 긋는다
    #    막대가 빨간 선 왼쪽으로 줄어들면 '감음'으로 판단된다.
    x0, y0, bar_w, bar_h, max_ear = 10, 152, 200, 12, 0.4
    filled = int(min(state.ear / max_ear, 1.0) * bar_w)
    cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y0 + bar_h), (80, 80, 80), -1)  # 회색 바탕
    cv2.rectangle(frame, (x0, y0), (x0 + filled, y0 + bar_h), color, -1)  # 현재 EAR
    tx = x0 + int(min(ear_threshold / max_ear, 1.0) * bar_w)
    cv2.line(frame, (tx, y0 - 3), (tx, y0 + bar_h + 3), (0, 0, 255), 2)  # 기준값
    cv2.putText(frame, f"th={ear_threshold:.2f}", (x0 + bar_w + 8, y0 + 11),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # 4) 보정 중이면 안내 문구 (노란색)
    if state.calibration_left > 0:
        cv2.putText(frame, f"Calibrating... keep eyes open {state.calibration_left:.1f}s",
                    (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)


def draw_drowsy_warning(frame):
    """졸음 경고: 화면 테두리를 빨갛게 하고 가운데에 큰 글씨를 띄운다.

    (OpenCV 기본 글꼴은 한글을 못 써서 'DROWSY'(졸음)라고 영어로 표시한다)
    """
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 12)  # 빨간 테두리

    text = "DROWSY! Wake up!"
    font, scale, thick = cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3
    (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
    x, y = (w - tw) // 2, h // 2
    # 글씨가 잘 보이도록 뒤에 빨간 상자를 깔고 흰 글씨를 쓴다
    cv2.rectangle(frame, (x - 20, y - th - 20), (x + tw + 20, y + 20), (0, 0, 200), -1)
    cv2.putText(frame, text, (x, y), font, scale, (255, 255, 255), thick)


def draw_status(frame, face_found: bool, fps: float):
    """왼쪽 위에 얼굴 인식 여부와 FPS(초당 처리 프레임 수)를 쓴다.

    OpenCV 기본 글꼴은 한글을 못 그리므로 화면 글자는 영어로 쓴다.
    """
    if face_found:
        text, color = "Face: OK", (0, 200, 0)  # 초록색 (BGR 순서)
    else:
        text, color = "Face: NOT FOUND", (0, 0, 255)  # 빨간색
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "q: quit   c: calibrate eyes", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
