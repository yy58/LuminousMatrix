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
    except Exception as e:
        print("Failed to save thresholds:", e)


class CameraProcessor:
    """
    重构后的摄像头处理类，逻辑 100% 不变
    main.py 负责：
        - 读取 frame
        - 每帧调用 process_frame(frame)
    """

    def __init__(self, host="127.0.0.1", port=8000):
        # Load thresholds
        h_low, l_low, s_low, h_high, l_high, s_high = load_thresholds()

        self.detector = LightDetector(h_low, l_low, s_low, h_high, l_high, s_high)
        self.osc = OSCClient(host, port)

        # Window
        self.win = "Light2Max"
        cv2.namedWindow(self.win, cv2.WINDOW_NORMAL)

        # UI Trackbars
        init_vals = (*self.detector.low, *self.detector.high)
        cv2.createTrackbar("h_low", self.win, int(init_vals[0]), 180, lambda v: None)
        cv2.createTrackbar("l_low", self.win, int(init_vals[1]), 255, lambda v: None)
        cv2.createTrackbar("s_low", self.win, int(init_vals[2]), 255, lambda v: None)
        cv2.createTrackbar("h_high", self.win, int(init_vals[3]), 180, lambda v: None)
        cv2.createTrackbar("l_high", self.win, int(init_vals[4]), 255, lambda v: None)
        cv2.createTrackbar("s_high", self.win, int(init_vals[5]), 255, lambda v: None)

        self.prev_send = 0
        self.send_interval = 0.02   # 50Hz

    def _update_thresholds(self):
        th = (
            cv2.getTrackbarPos("h_low", self.win),
            cv2.getTrackbarPos("l_low", self.win),
            cv2.getTrackbarPos("s_low", self.win),
            cv2.getTrackbarPos("h_high", self.win),
            cv2.getTrackbarPos("l_high", self.win),
            cv2.getTrackbarPos("s_high", self.win),
        )

        h_low = max(0, min(180, th[0]))
        l_low = max(0, min(255, th[1]))
        s_low = max(0, min(255, th[2]))
        h_high = max(0, min(180, th[3]))
        l_high = max(0, min(255, th[4]))
        s_high = max(0, min(255, th[5]))

        self.detector.low = np.array([h_low, l_low, s_low], dtype=np.uint8)
        self.detector.high = np.array([h_high, l_high, s_high], dtype=np.uint8)

    def process_frame(self, frame):
        """
        main.py 每帧调用
        返回：
            - 是否退出：True/False
        """

        self._update_thresholds()

        mask, centroid, area, brightness = self.detector.detect(frame)

        h, w = frame.shape[:2]

        # Stylized pixelation (原逻辑不变)
        pixel_size = 12
        small = cv2.resize(frame, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
        display = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        # Draw centroid
        if centroid is not None:
            cx, cy = centroid
            cv2.circle(display, (cx, cy), 8, (0, 255, 0), 2)

            x_norm = cx / float(w)
            y_norm = cy / float(h)
            area_norm = min(1.0, area / float(w * h))
            brightness_norm = brightness / 255.0

            now = time.time()
            if now - self.prev_send >= self.send_interval:
                self.osc.send_light(x_norm, y_norm, area_norm, brightness_norm)
                self.prev_send = now

            cv2.putText(display, f"x={x_norm:.2f} y={y_norm:.2f} a={area_norm:.4f} b={brightness_norm:.2f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # Show thresholds
        low = self.detector.low
        high = self.detector.high
        cv2.putText(display,
                    f"H[{low[0]}-{high[0]}] L[{low[1]}-{high[1]}] S[{low[2]}-{high[2]}]",
                    (10, display.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220,220,0), 2)

        # mask viewport
        if mask is not None:
            mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cam_w = 480
            cam_h = int(cam_w * h / w)
            resized_frame = cv2.resize(display, (cam_w, cam_h))
            mask_h = resized_frame.shape[0]
            mask_w = 720
            resized_mask = cv2.resize(mask_rgb, (mask_w, mask_h))
            combined = np.hstack((resized_frame, resized_mask))
        else:
            combined = cv2.resize(display, (960, 540))

        cv2.imshow(self.win, combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return True
        elif key == ord("s"):
            save_thresholds((*low, *high))

        return False
