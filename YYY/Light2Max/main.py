#!/usr/bin/env python3
"""Run camera capture, detect light points, visualize and send to Max/MSP via OSC.

Usage:
    python main.py --host 127.0.0.1 --port 8000

Controls:
    q - quit

"""
import argparse
import json
import os
import time

import cv2
import numpy as np

from detector import LightDetector
from osc_sender import OSCClient


THRESH_FILE = os.path.join(os.path.dirname(__file__), "thresholds.json")


def load_thresholds():
    if os.path.exists(THRESH_FILE):
        try:
            with open(THRESH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return (
                int(data.get("h_low", 0)),
                int(data.get("l_low", 200)),
                int(data.get("s_low", 100)),
                int(data.get("h_high", 180)),
                int(data.get("l_high", 255)),
                int(data.get("s_high", 255)),
            )
        except Exception:
            pass
    return 0, 200, 100, 180, 255, 255


def save_thresholds(vals):
    data = {
        "h_low": int(vals[0]),
        "l_low": int(vals[1]),
        "s_low": int(vals[2]),
        "h_high": int(vals[3]),
        "l_high": int(vals[4]),
        "s_high": int(vals[5]),
    }
    try:
        with open(THRESH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved thresholds to {THRESH_FILE}")
    except Exception as e:
        print("Failed to save thresholds:", e)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1", help="OSC host (Max/MSP host)")
    p.add_argument("--port", type=int, default=8000, help="OSC port (Max/MSP port)")
    p.add_argument("--camera", type=int, default=0, help="Camera index")
    p.add_argument("--video", type=str, default=None, help="Path to a video file to process instead of camera")
    # HLS thresholds (H:0-180, L,S:0-255)
    p.add_argument("--h_low", type=int, default=0)
    p.add_argument("--l_low", type=int, default=200)
    p.add_argument("--s_low", type=int, default=100)
    p.add_argument("--h_high", type=int, default=180)
    p.add_argument("--l_high", type=int, default=255)
    p.add_argument("--s_high", type=int, default=255)
    return p.parse_args()


def main():
    args = parse_args()

    # Open video source: file if provided, otherwise camera index
    if args.video:
        if not os.path.exists(args.video):
            print("Video file not found:", args.video)
            return
        cap = cv2.VideoCapture(args.video)
    else:
        cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        print("Failed to open video source")
        return
    # Load thresholds from file if present, else from CLI defaults
    h_low, l_low, s_low, h_high, l_high, s_high = load_thresholds()
    # Allow CLI to override loaded values if provided explicitly
    detector = LightDetector(args.h_low or h_low, args.l_low or l_low, args.s_low or s_low,
                             args.h_high or h_high, args.l_high or l_high, args.s_high or s_high)
    osc = OSCClient(args.host, args.port)

    win = "Light2Max"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    # Create trackbars for H, L, S (OpenCV H:0-180, L,S:0-255)
    init_vals = (detector.low[0], detector.low[1], detector.low[2], detector.high[0], detector.high[1], detector.high[2])
    cv2.createTrackbar("h_low", win, int(init_vals[0]), 180, lambda v: None)
    cv2.createTrackbar("l_low", win, int(init_vals[1]), 255, lambda v: None)
    cv2.createTrackbar("s_low", win, int(init_vals[2]), 255, lambda v: None)
    cv2.createTrackbar("h_high", win, int(init_vals[3]), 180, lambda v: None)
    cv2.createTrackbar("l_high", win, int(init_vals[4]), 255, lambda v: None)
    cv2.createTrackbar("s_high", win, int(init_vals[5]), 255, lambda v: None)

    prev_send = 0
    send_interval = 0.02  # send at up to 50 Hz

    while True:
        ret, frame = cap.read()
        if not ret:
            # if using a video file, loop: reset to start; if camera, continue trying
            if args.video:
                try:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    # small pause to avoid busy-looping
                    time.sleep(0.02)
                    continue
                except Exception:
                    print("End of video file")
                    break
            else:
                continue

        # Read trackbar values each loop and update detector thresholds
        th = (
            cv2.getTrackbarPos("h_low", win),
            cv2.getTrackbarPos("l_low", win),
            cv2.getTrackbarPos("s_low", win),
            cv2.getTrackbarPos("h_high", win),
            cv2.getTrackbarPos("l_high", win),
            cv2.getTrackbarPos("s_high", win),
        )
        # enforce min/max
        h_low_v = max(0, min(180, th[0]))
        l_low_v = max(0, min(255, th[1]))
        s_low_v = max(0, min(255, th[2]))
        h_high_v = max(0, min(180, th[3]))
        l_high_v = max(0, min(255, th[4]))
        s_high_v = max(0, min(255, th[5]))
        detector.low = np.array([h_low_v, l_low_v, s_low_v], dtype=np.uint8)
        detector.high = np.array([h_high_v, l_high_v, s_high_v], dtype=np.uint8)

        mask, centroid, area, brightness = detector.detect(frame)

        h, w = frame.shape[:2]

        # Create a stylized, slightly pixellated color frame for a retro look
        # This restores the previous color + mask side-by-side layout but with pixelation
        pixel_size = 12
        small_w = max(1, w // pixel_size)
        small_h = max(1, h // pixel_size)
        small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        stylized = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        display = stylized.copy()

        if centroid is not None:
            cx, cy = centroid
            # Draw centroid and bounding on the stylized color display
            cv2.circle(display, (cx, cy), 8, (0, 255, 0), 2)
            # normalized values
            x_norm = cx / float(w)
            y_norm = cy / float(h)
            # area normalization: relative to frame area
            area_norm = min(1.0, area / float(w * h))
            brightness_norm = brightness / 255.0

            now = time.time()
            if now - prev_send >= send_interval:
                osc.send_light(x_norm, y_norm, area_norm, brightness_norm)
                prev_send = now

            # Overlay text
            cv2.putText(display, f"x={x_norm:.2f} y={y_norm:.2f} a={area_norm:.4f} b={brightness_norm:.2f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Show current thresholds on the stylized display
        thresh_text = f"H[{h_low_v}-{h_high_v}] L[{l_low_v}-{l_high_v}] S[{s_low_v}-{s_high_v}]"
        cv2.putText(display, thresh_text, (10, display.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 0), 2)

        # Show mask in small viewport — resize so heights match for hstack (restored layout)
        if mask is not None:
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            # Smaller camera feed width for side-by-side layout
            cam_w = 480
            cam_h = max(1, int(cam_w * h / w))
            resized_frame = cv2.resize(display, (cam_w, cam_h))
            # make mask same height as resized_frame and use smaller width
            mask_h = resized_frame.shape[0]
            mask_w = 720
            resized_mask = cv2.resize(mask_rgb, (mask_w, mask_h))
            combined = np.hstack((resized_frame, resized_mask))
        else:
            combined = cv2.resize(display, (960, 540))

        cv2.imshow(win, combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            # save current trackbar thresholds
            save_thresholds((h_low_v, l_low_v, s_low_v, h_high_v, l_high_v, s_high_v))

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
