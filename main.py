"""FocusEye+ 실행 파일.

지금까지 만든 기능
- 1단계: 웹캠 화면 + 얼굴 랜드마크 표시
- 2단계: 눈 감김 감지 (EAR 계산, 오래 감으면 졸음 경고)

실행:  python main.py
       python main.py --ear-threshold 0.18 --drowsy-seconds 2   (기준값을 바꿔서 실행)
키:    q = 종료,  c = 눈 기준값 보정 (3초 동안 눈을 편하게 뜨고 화면 보기)

[개인정보 원칙]
웹캠 영상은 메모리에서 분석·표시만 하고, 파일로 절대 저장하지 않는다.
"""

import argparse
import sys
import time

import cv2

from focuseye import config
from focuseye.drawing import (
    draw_drowsy_warning,
    draw_eye_points,
    draw_eye_state,
    draw_face_landmarks,
    draw_status,
)
from focuseye.eye_state import SCREEN_LEFT_EYE, SCREEN_RIGHT_EYE, EyeStateDetector, eye_points
from focuseye.face_tracker import FaceTracker

WINDOW_NAME = "FocusEye+"


def main():
    """프로그램 본체. 정상 종료면 0, 오류면 1을 돌려준다.

    (run.bat은 이 값이 1이면 창을 바로 닫지 않고 오류 메시지를 보여 준다)
    """
    # 명령줄 옵션
    #   기준값의 기본값은 focuseye/config.py 에 있다. 옵션을 주면 이번 실행에서만 바뀐다.
    parser = argparse.ArgumentParser(description="FocusEye+")
    parser.add_argument("--camera", type=int, default=0, help="웹캠 번호 (기본 0)")
    parser.add_argument("--ear-threshold", type=float, default=config.EAR_THRESHOLD,
                        help=f"눈 감김 기준 EAR (기본 {config.EAR_THRESHOLD})")
    parser.add_argument("--drowsy-seconds", type=float, default=config.DROWSY_SECONDS,
                        help=f"졸음 판단 시간(초) (기본 {config.DROWSY_SECONDS})")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[오류] {args.camera}번 웹캠을 열 수 없습니다. 연결 상태나 카메라 권한을 확인하세요.")
        return 1

    print(f"[설정] 눈 감김 기준 EAR = {args.ear_threshold}, 졸음 판단 시간 = {args.drowsy_seconds}초")

    print("[안내] c 키: 3초 동안 눈을 편하게 뜨고 화면을 보면 내 눈에 맞게 기준값을 자동으로 정합니다.")

    eye_detector = EyeStateDetector(
        ear_threshold=args.ear_threshold,
        drowsy_seconds=args.drowsy_seconds,
        smoothing=config.EAR_SMOOTHING,
        calibration_seconds=config.CALIBRATION_SECONDS,
        calibration_ratio=config.CALIBRATION_RATIO,
    )

    exit_code = 0
    fps = 0.0
    prev_time = time.monotonic()

    with FaceTracker() as tracker:
        while True:
            ok, frame = cap.read()  # 웹캠에서 사진 한 장(프레임)을 읽는다
            if not ok:
                print("[오류] 웹캠 영상을 읽지 못했습니다.")
                exit_code = 1
                break

            # 좌우 반전: 거울처럼 보이게 해서 움직임이 자연스럽다
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            now = time.monotonic()

            # 1단계: 얼굴 랜드마크 찾기
            result = tracker.process(frame)
            face_found = len(result.face_landmarks) > 0

            eye_state = None
            if face_found:
                face = result.face_landmarks[0]  # 한 명만 분석
                draw_face_landmarks(frame, face)

                # 2단계: 눈 감김 분석
                eye_state = eye_detector.update(face, width, height, now)
                if eye_detector.calibration_done is not None:
                    print(f"[보정 완료] 눈 뜬 EAR = {eye_detector.last_open_ear:.3f}"
                          f" → 기준값 = {eye_detector.calibration_done}"
                          "  (잘 맞으면 focuseye/config.py의 EAR_THRESHOLD에 적어 두세요)")
                draw_eye_points(frame, [
                    eye_points(face, SCREEN_LEFT_EYE, width, height),
                    eye_points(face, SCREEN_RIGHT_EYE, width, height),
                ])
            else:
                # 얼굴이 안 보이면 눈 감은 시간 기록을 지운다 (자리 이탈은 4단계에서 처리)
                eye_detector.reset()

            # FPS 계산 (부드럽게 보이도록 이전 값과 섞는다)
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now

            # 화면에 정보 표시
            draw_status(frame, face_found, fps)
            if eye_state is not None:
                draw_eye_state(frame, eye_state, eye_detector.ear_threshold)
                if eye_state.is_drowsy:
                    draw_drowsy_warning(frame)

            cv2.imshow(WINDOW_NAME, frame)  # 화면에 보여주기만 하고 저장하지 않음

            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):  # c: 눈 기준값 보정 시작
                eye_detector.start_calibration(now)
            if key == ord("q"):  # q 키나 창의 X 버튼을 누르면 종료
                break
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    cap.release()
    cv2.destroyAllWindows()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())  # 종료 코드(0 또는 1)를 운영체제에 알려 준다
