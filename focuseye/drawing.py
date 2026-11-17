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
    cv2.putText(frame, "q: quit", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
