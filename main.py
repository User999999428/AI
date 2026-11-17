"""FocusEye+ 실행 파일 (1단계: 웹캠 + 얼굴 랜드마크 표시).

실행:  python main.py
종료:  영상 창을 클릭한 뒤 q 키

[개인정보 원칙]
웹캠 영상은 메모리에서 분석·표시만 하고, 파일로 절대 저장하지 않는다.
"""

import argparse
import time

import cv2

from focuseye.drawing import draw_face_landmarks, draw_status
from focuseye.face_tracker import FaceTracker

WINDOW_NAME = "FocusEye+"


def main():
    # 명령줄 옵션: 웹캠이 여러 개면 --camera 1 처럼 번호를 바꿔 볼 수 있다
    parser = argparse.ArgumentParser(description="FocusEye+ 1단계")
    parser.add_argument("--camera", type=int, default=0, help="웹캠 번호 (기본 0)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[오류] {args.camera}번 웹캠을 열 수 없습니다. 연결 상태나 카메라 권한을 확인하세요.")
        return

    fps = 0.0
    prev_time = time.monotonic()

    with FaceTracker() as tracker:
        while True:
            ok, frame = cap.read()  # 웹캠에서 사진 한 장(프레임)을 읽는다
            if not ok:
                print("[오류] 웹캠 영상을 읽지 못했습니다.")
                break

            # 좌우 반전: 거울처럼 보이게 해서 움직임이 자연스럽다
            frame = cv2.flip(frame, 1)

            # 얼굴 랜드마크 찾기
            result = tracker.process(frame)
            face_found = len(result.face_landmarks) > 0
            for face in result.face_landmarks:
                draw_face_landmarks(frame, face)

            # FPS 계산 (부드럽게 보이도록 이전 값과 섞는다)
            now = time.monotonic()
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now

            draw_status(frame, face_found, fps)
            cv2.imshow(WINDOW_NAME, frame)  # 화면에 보여주기만 하고 저장하지 않음

            # q 키를 누르거나 창의 X 버튼을 누르면 종료
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
