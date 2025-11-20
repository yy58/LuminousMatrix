import cv2
import numpy as np
import math


def rvec_to_euler(rvec):
    """Convert rotation vector → Euler angles (yaw, pitch, roll)."""
    R, _ = cv2.Rodrigues(rvec)

    sy = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.degrees([x, y, z])  # roll, pitch, yaw


def main():
    cap = cv2.VideoCapture(0)

    # --- camera calibration result here ----
    params = np.load("camera_params.npz")
    camera_matrix = params["camera_matrix"]
    dist_coeffs = params["dist_coeffs"]

    # ArUco dict (change if needed)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    marker_length = 0.02  # 2 cm marker side length

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                marker_length,
                camera_matrix,
                dist_coeffs,
            )

            for i, marker_id in enumerate(ids.flatten()):
                rvec = rvecs[i]
                tvec = tvecs[i]

                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.05)

                roll, pitch, yaw = rvec_to_euler(rvec)

                print(
                    f"[Marker {marker_id}] "
                    f"Pos (m): x={tvec[0][0]:.3f}, y={tvec[0][1]:.3f}, z={tvec[0][2]:.3f} | "
                    f"Euler (deg): roll={roll:.1f}, pitch={pitch:.1f}, yaw={yaw:.1f}"
                )

        cv2.imshow("Aruco Detection", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
