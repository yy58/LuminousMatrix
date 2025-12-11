import threading
import queue
import time
import cv2

from C_SoundProcessor import CameraProcessor
from A_ArUcoDetector import ArucoDetector
from B_AreciboMessage import RaySimulator

# ---------------- Config ----------------
CAM_WIDTH = 1280
CAM_HEIGHT = 720
DETECT_INTERVAL = 60  # 每60帧检测一次

# ---------------- Queues / Shared Data ----------------
frame_queue = queue.Queue(maxsize=5)       # 主线程 -> C / A
prism_data_lock = threading.Lock()
prism_data = []                             # A -> B

# ---------------- Thread: C模块 ----------------
def thread_C(cam_proc):
    while True:
        try:
            frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        quit_flag = cam_proc.process_frame(frame)
        if quit_flag:
            break

# ---------------- Thread: A模块 ----------------
def thread_A(aruco_detector):
    frame_counter = 0
    while True:
        try:
            frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        frame_counter += 1
        if frame_counter % DETECT_INTERVAL != 0:
            continue  # 每60帧检测一次

        result = aruco_detector.detect(frame)
        with prism_data_lock:
            prism_data.clear()
            if result is not None:
                ids, corners, rvecs, tvecs = result
                for i, marker_id in enumerate(ids.flatten()):
                    corner = corners[i][0]
                    cx = float(corner[:, 0].mean())
                    cy = float(corner[:, 1].mean())
                    yaw = ArucoDetector.get_yaw_from_rvec(rvecs[i])
                    prism_data.append((marker_id, cx, cy, yaw))
            # 若没有检测到 marker，prism_data 会被清空，B模块自动不绘制

# ---------------- Thread: B模块 ----------------
def thread_B(simulator):
    simulator.set_window_size(CAM_WIDTH, CAM_HEIGHT)
    running = True
    while running:
        with prism_data_lock:
            simulator.update_prism_data(prism_data)
        simulator.draw()
        time.sleep(0.016)  # 约 60 FPS

# ---------------- Main ----------------
def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    if not cap.isOpened():
        print("Failed to open camera")
        return

    # 初始化模块
    cam_proc = CameraProcessor()
    aruco_detector = ArucoDetector()
    simulator = RaySimulator()

    # 创建线程
    tC = threading.Thread(target=thread_C, args=(cam_proc,), daemon=True)
    tA = threading.Thread(target=thread_A, args=(aruco_detector,), daemon=True)
    tB = threading.Thread(target=thread_B, args=(simulator,), daemon=True)

    tC.start()
    tA.start()
    tB.start()

    frame_id = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_id += 1

            # 放入队列供C / A使用
            if not frame_queue.full():
                frame_queue.put(frame)

            # 绘制A的检测结果
            aruco_detector.draw(frame)
            cv2.imshow("Aruco View", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
