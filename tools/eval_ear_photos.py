"""사진으로 눈 감김 판단(EAR) 정확도 검증하기.

웹캠이 없는 컴퓨터에서도, 눈 뜬 사진과 눈 감은 사진을 넣어서
"EAR 기준값을 얼마로 하면 얼마나 잘 맞히는지"를 숫자로 확인한다.

[사용법] 프로젝트 폴더(AI)에서 가상환경을 켠 뒤:
    python tools/eval_ear_photos.py --list     ← 1) 폴더 구조만 먼저 확인
    python tools/eval_ear_photos.py            ← 2) 전체 검증 실행

    다른 폴더를 검사하려면:  --data data/다른폴더

[눈 뜬/감은 사진 구분 방법]
사진이 들어 있는 폴더 이름(또는 파일 이름)을 보고 정한다.
    이름에 "close"가 들어 있으면 → 눈 감은 사진  (예: ClosedFace)
    이름에 "open"이 들어 있으면  → 눈 뜬 사진    (예: OpenFace)
    둘 다 없으면                → 구분 불가 (검증에서 빼고 개수만 알려 줌)

[저장하는 것 - 숫자만]
    results/ear_threshold_accuracy.csv        기준값별 정확도 표 (보고서용, GitHub에 올려도 됨)
    data/results/ear_per_image.csv            사진마다 EAR 값 (데이터셋 파일 이름이 들어 있어서
                                              data/ 안에 둔다 → GitHub에 안 올라감)
사진(이미지)은 절대 저장하지 않는다. 메모리에서 분석만 하고 버린다.
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np

# 이 파일은 tools/ 폴더 안에 있어서, 한 단계 위(프로젝트 폴더)를 알려 줘야 focuseye를 불러올 수 있다
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from focuseye.eye_state import SCREEN_LEFT_EYE, SCREEN_RIGHT_EYE, eye_aspect_ratio, eye_points  # noqa: E402
from focuseye.face_tracker import FaceTracker  # noqa: E402

DEFAULT_DATA = PROJECT_DIR / "data" / "dataset_B_FacialImages_highResolution"
SUMMARY_CSV = PROJECT_DIR / "results" / "ear_threshold_accuracy.csv"
PER_IMAGE_CSV = PROJECT_DIR / "data" / "results" / "ear_per_image.csv"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".pgm", ".tif", ".tiff"}

# 검사할 기준값: 0.10, 0.11, ..., 0.30
THRESHOLDS = [round(0.10 + 0.01 * i, 2) for i in range(21)]


# ── 1. 사진 찾기와 라벨(눈 뜸/감음) 정하기 ───────────────────────

def label_from_path(path, root):
    """경로의 폴더 이름·파일 이름으로 'closed' / 'open' / None(모름)을 정한다."""
    parts = [p.lower() for p in path.relative_to(root).parts]
    has_closed = any("close" in p for p in parts)
    has_open = any("open" in p for p in parts)
    if has_closed and not has_open:
        return "closed"
    if has_open and not has_closed:
        return "open"
    return None  # 둘 다 없거나, 둘 다 있어서 헷갈림


def find_images(root):
    """root 아래의 모든 사진 파일을 찾아 정렬해서 돌려준다."""
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def print_structure(root, images):
    """폴더별 사진 수와, 그 폴더를 어떻게 구분했는지 보여 준다."""
    print(f"\n[폴더 구조] {root}")
    counts = {}  # {폴더: [사진 수, 라벨]}
    for img in images:
        folder = img.parent.relative_to(root)
        if folder not in counts:
            counts[folder] = [0, label_from_path(img, root)]
        counts[folder][0] += 1
    names = {"closed": "눈 감음", "open": "눈 뜸", None: "구분 불가"}
    for folder, (n, label) in sorted(counts.items()):
        # 맨 위 폴더는 "." 으로 나와서 알아보기 쉽게 바꾼다
        # (맨 위 폴더에 사진이 바로 있으면 파일 이름으로 구분한다)
        name = "(맨 위 폴더, 파일 이름으로 구분)" if str(folder) == "." else str(folder)
        print(f"  {name:<40} 사진 {n:>5}장  → {names[label]}")
    total = {k: sum(1 for i in images if label_from_path(i, root) == k) for k in names}
    print(f"  합계: 눈 감음 {total['closed']}장, 눈 뜸 {total['open']}장, 구분 불가 {total[None]}장")
    return total


# ── 2. 사진 한 장 분석 ──────────────────────────────────────

def read_image(path):
    """사진을 읽는다. (cv2.imread는 한글 경로를 못 읽을 때가 있어서 이 방법을 쓴다)"""
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)  # 흑백 사진도 컬러(3채널)로 바꿔서 읽음


def add_margin(img, ratio):
    """사진 둘레에 여백을 붙인다 (메모리에서만, 저장 안 함).

    얼굴만 꽉 차게 잘린 사진은 MediaPipe가 얼굴을 잘 못 찾는다.
    둘레에 가장자리 색을 늘여 붙이면 '얼굴이 화면 안에 있는 사진'처럼 되어 더 잘 찾는다.
    EAR은 비율이라서 여백을 붙여도 값이 변하지 않는다.
    """
    if ratio <= 0:
        return img
    h, w = img.shape[:2]
    dy, dx = int(h * ratio), int(w * ratio)
    return cv2.copyMakeBorder(img, dy, dy, dx, dx, cv2.BORDER_REPLICATE)


def analyze(tracker, path, margin):
    """사진 한 장의 EAR을 계산한다. 얼굴을 못 찾으면 None."""
    img = read_image(path)
    if img is None:
        return None
    img = add_margin(img, margin)
    h, w = img.shape[:2]
    result = tracker.process(img)
    if not result.face_landmarks:
        return None
    face = result.face_landmarks[0]
    ear_l = eye_aspect_ratio(eye_points(face, SCREEN_LEFT_EYE, w, h))
    ear_r = eye_aspect_ratio(eye_points(face, SCREEN_RIGHT_EYE, w, h))
    return ear_l, ear_r, (ear_l + ear_r) / 2


# ── 3. 기준값별 정확도 계산 ───────────────────────────────────

def accuracy_table(rows):
    """얼굴을 찾은 사진들로 기준값마다 정확도를 계산한다.

    판단 규칙은 프로그램과 같다: EAR < 기준값 이면 '눈 감음'.
    한 종류 사진만 있으면, 없는 쪽 비율과 전체 정확도는 계산할 수 없어서 None으로 둔다.
    """
    closed = [r["ear"] for r in rows if r["label"] == "closed"]
    opened = [r["ear"] for r in rows if r["label"] == "open"]
    both = bool(closed) and bool(opened)
    table = []
    for th in THRESHOLDS:
        closed_ok = sum(1 for e in closed if e < th)  # 감은 사진을 '감음'으로 맞힘
        open_ok = sum(1 for e in opened if e >= th)  # 뜬 사진을 '뜸'으로 맞힘
        table.append({
            "threshold": th,
            "accuracy": (closed_ok + open_ok) / (len(closed) + len(opened)) if both else None,
            "closed_correct_rate": closed_ok / len(closed) if closed else None,
            "open_correct_rate": open_ok / len(opened) if opened else None,
        })
    return table


def print_ear_stats(rows):
    """눈 뜬/감은 사진의 EAR이 보통 얼마인지 보여 준다."""
    print("\n[EAR 분포] (얼굴을 찾은 사진만)")
    print(f"  {'구분':<8}{'사진 수':>8}{'평균':>8}{'중앙값':>8}{'최소':>8}{'최대':>8}")
    for label, name in (("open", "눈 뜸"), ("closed", "눈 감음")):
        ears = [r["ear"] for r in rows if r["label"] == label]
        if ears:
            print(f"  {name:<8}{len(ears):>8}{statistics.mean(ears):>8.3f}"
                  f"{statistics.median(ears):>8.3f}{min(ears):>8.3f}{max(ears):>8.3f}")


def _pct(value):
    """비율을 '95.0%'처럼 바꾼다. 계산할 수 없는 값(None)은 '-'."""
    return "-" if value is None else f"{value:.1%}"


def print_table(table):
    """표를 출력하고, 정확도가 가장 높은 줄을 돌려준다 (정할 수 없으면 None)."""
    print("\n[기준값별 정확도]  판단 규칙: EAR < 기준값 → 눈 감음")
    print(f"  {'기준값':>6}  {'전체 정확도':>10}  {'감은 눈 맞힘':>10}  {'뜬 눈 맞힘':>10}")
    # 눈 뜬/감은 사진이 둘 다 있어야 '가장 좋은 기준값'을 정할 수 있다
    best = None
    if table[0]["accuracy"] is not None:
        best = max(table, key=lambda t: t["accuracy"])
    for t in table:
        mark = "  ← 최고" if t is best else ""
        print(f"  {t['threshold']:>6.2f}  {_pct(t['accuracy']):>10}  "
              f"{_pct(t['closed_correct_rate']):>10}  {_pct(t['open_correct_rate']):>10}{mark}")
    return best


# ── 4. CSV 저장 (숫자만) ────────────────────────────────────

def save_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: 엑셀에서 열어도 글자가 깨지지 않게 하는 방식
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="사진으로 EAR 눈 감김 판단 정확도 검증")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="사진 폴더")
    parser.add_argument("--list", action="store_true", help="폴더 구조만 보여 주고 끝내기")
    parser.add_argument("--margin", type=float, default=0.3,
                        help="사진 둘레에 붙일 여백 비율 (기본 0.3 = 30%%). 0이면 여백 없음")
    args = parser.parse_args()

    root = args.data.resolve()
    if not root.is_dir():
        print(f"[오류] 폴더가 없습니다: {root}")
        return 1

    images = find_images(root)
    if not images:
        print(f"[오류] 사진 파일을 찾지 못했습니다: {root}")
        return 1
    total = print_structure(root, images)
    if args.list:
        return 0
    if total["closed"] == 0 and total["open"] == 0:
        print("\n[오류] 눈 뜬 사진과 감은 사진을 구분하지 못했습니다.")
        print("       폴더 이름에 open / close 가 들어 있어야 합니다. 위 [폴더 구조] 출력을 확인하세요.")
        return 1
    if total["closed"] == 0 or total["open"] == 0:
        # 한 종류만 있어도 그 사진들의 EAR 분포와 '맞힌 비율'은 알 수 있다
        missing = "눈 뜬" if total["open"] == 0 else "눈 감은"
        print(f"\n[주의] {missing} 사진이 없습니다. 있는 사진만 분석합니다.")
        print("       전체 정확도와 '가장 좋은 기준값'은 두 종류가 다 있어야 계산할 수 있습니다.")

    # 라벨을 아는 사진만 분석
    targets = [(p, label_from_path(p, root)) for p in images]
    targets = [(p, lab) for p, lab in targets if lab is not None]
    print(f"\n[분석 시작] 사진 {len(targets)}장, 여백 {args.margin:.0%}  (사진은 저장하지 않음)")

    rows = []
    not_found = {"closed": 0, "open": 0}
    with FaceTracker(image_mode=True) as tracker:
        for i, (path, label) in enumerate(targets, 1):
            ear = analyze(tracker, path, args.margin)
            row = {"file": str(path.relative_to(root)), "label": label, "face_found": ear is not None,
                   "ear_left": "", "ear_right": "", "ear": ""}
            if ear is None:
                not_found[label] += 1
            else:
                row["ear_left"], row["ear_right"], row["ear"] = (round(v, 4) for v in ear)
            rows.append(row)
            if i % 200 == 0 or i == len(targets):
                print(f"  {i}/{len(targets)}장 완료")

    found = [r for r in rows if r["face_found"]]
    print("\n[얼굴 찾기 결과]")
    for label, name in (("closed", "눈 감음"), ("open", "눈 뜸")):
        n = sum(1 for _, lab in targets if lab == label)
        print(f"  {name}: {n}장 중 {n - not_found[label]}장 찾음, 못 찾음 {not_found[label]}장")
    if not found:
        print("[오류] 얼굴을 찾은 사진이 없습니다. --margin 값을 바꿔 보세요 (예: 0.5)")
        return 1

    print_ear_stats(found)
    table = accuracy_table(found)
    best = print_table(table)
    if best is not None:
        print(f"\n→ 이 사진들에서는 기준값 {best['threshold']:.2f}일 때 정확도가 가장 높습니다 ({best['accuracy']:.1%}).")
        print("  (사진 속 사람들 기준이라 내 눈과 다를 수 있습니다. 실제 사용 땐 c 키 보정도 함께 쓰세요)")
    else:
        print("\n→ 한 종류 사진만 있어서 '가장 좋은 기준값'은 정할 수 없습니다.")
        print("  (감은 눈만 있으면 기준값을 높일수록 무조건 더 잘 맞히기 때문. 뜬 눈을 잘못 잡는 정도를 모름)")

    # 숫자만 CSV로 저장 (계산할 수 없는 칸은 빈칸)
    save_csv(SUMMARY_CSV, [{k: ("" if v is None else round(v, 4)) for k, v in t.items()}
                           for t in table],
             ["threshold", "accuracy", "closed_correct_rate", "open_correct_rate"])
    save_csv(PER_IMAGE_CSV, rows, ["file", "label", "face_found", "ear_left", "ear_right", "ear"])
    print("\n[저장] 숫자만 저장했습니다 (사진은 저장하지 않음)")
    print(f"  {SUMMARY_CSV.relative_to(PROJECT_DIR)}   ← 기준값별 정확도 (보고서용)")
    print(f"  {PER_IMAGE_CSV.relative_to(PROJECT_DIR)}   ← 사진별 EAR (data/ 안이라 GitHub에 안 올라감)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
