import cv2
import numpy as np


class LightDetector:
    """Detect bright colored light spots using HLS thresholding.

    Methods
    - detect(frame) -> mask, (cx, cy), area, mean_light
    """

    def __init__(self, h_low=0, l_low=200, s_low=100, h_high=180, l_high=255, s_high=255):
        # H, L, S thresholds in HLS space (OpenCV uses H:0-180, L,S:0-255)
        self.low = np.array([h_low, l_low, s_low], dtype=np.uint8)
        self.high = np.array([h_high, l_high, s_high], dtype=np.uint8)

    def detect(self, frame):
        """Return mask, centroid (x,y), area, mean_light

        centroid is None if nothing found.
        area is the pixel area of the detected mask.
        mean_light is mean of the L channel inside the mask (0-255).
        """
        if frame is None:
            return None, None, 0, 0

        # Convert to HLS (OpenCV uses HLS naming; H,L,S)
        hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)

        # Threshold
        mask = cv2.inRange(hls, self.low, self.high)

        # Optional: morphological clean-up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Find contours to compute area and centroid
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return mask, None, 0, 0

        # Choose largest contour (assumed main light)
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        M = cv2.moments(largest)
        if M.get("m00", 0) == 0:
            return mask, None, area, 0

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Mean lightness inside mask (L channel)
        l_channel = hls[:, :, 1]
        mean_light = 0
        mask_bool = mask.astype(bool)
        if mask_bool.any():
            mean_light = int(l_channel[mask_bool].mean())

        return mask, (cx, cy), area, mean_light
