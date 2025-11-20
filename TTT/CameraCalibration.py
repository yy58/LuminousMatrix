import cv2
import numpy as np
import os

# Chessboard inner corners (9x6)
CHESSBOARD = (9, 6)
SQUARE_SIZE = 0.025  # 2.5 cm square (change if needed)

SAVE_DIR = "calibration_images"
os.makedirs(SAVE_DIR, exist_ok=True)


def main():
    cap = cv2.VideoCapture(0)

    # prepare object points: (0,0,0), (1,0,0), ..., (8,5,0)
    objp = np.zeros((CHESSBOARD[0] * CHESSBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESSBOARD[0], 0:CHESSBOARD[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    objpoints = []  # 3D points
    imgpoints = []  # 2D points

    img_count = 0

    print("Calibration tool running...")
    print("[s] Save chessboard image   |   [q] Calibrate   |   [ESC] Exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, CHESSBOARD, None)

        if found:
            cv2.drawChessboardCorners(frame, CHESSBOARD, corners, found)

        cv2.imshow("Calibration", frame)
        key = cv2.waitKey(1)

        if key == ord("s") and found:
            img_name = f"{SAVE_DIR}/img_{img_count:02d}.png"
            cv2.imwrite(img_name, frame)
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
            )
            imgpoints.append(corners2)
            img_count += 1
            print(f"Saved: {img_name}")

        elif key == ord("q"):
            print("Starting calibration...")
            break

        elif key == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    if img_count < 10:
        print("Not enough images (need >= 10).")
        return

    # --- Calibration ---
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    print("\n=== Calibration Result ===")
    print("RMS error:", ret)
    print("Camera matrix:\n", camera_matrix)
    print("Distortion coefficients:\n", dist_coeffs.ravel())

    # save
    np.savez("camera_params.npz",
             camera_matrix=camera_matrix,
             dist_coeffs=dist_coeffs)

    print("\nSaved to 'camera_params.npz'")


if __name__ == "__main__":
    main()
