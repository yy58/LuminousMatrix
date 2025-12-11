import cv2
import numpy as np
import math

MARKER_LENGTH = 0.02
DETECT_INTERVAL = 60

def get_yaw_from_rvec(rvec):
    R, _ = cv2.Rodrigues(rvec)
    yaw = math.atan2(R[1, 0], R[0, 0])
    return np.degrees(yaw)

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    params = np.load("camera_params.npz")
    camera_matrix = params["camera_matrix"]
    dist_coeffs = params["dist_coeffs"]

    dict_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dict_aruco, parameters)

    last_ids = None
    last_corners = None

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # frame = cv2.flip(frame, 1)

        frame_id += 1
        need_detect = False

        # 每 N 帧检测一次
        if frame_id % DETECT_INTERVAL == 0:
            need_detect = True

        # 没有历史数据必须检测
        if last_ids is None:
            need_detect = True

        # ----------------------
        #     检 测 逻 辑
        # ----------------------
        if need_detect:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            # 找到了 ArUco
            if ids is not None:
                # # 修正角点顺序（因为使用了水平镜像）
                # for i in range(len(corners)):
                #     c = corners[i][0]
                #     corners[i][0] = np.array([c[1], c[0], c[3], c[2]])

                half = MARKER_LENGTH / 2
                obj_points = np.array([
                    [-half,  half, 0],
                    [ half,  half, 0],
                    [ half, -half, 0],
                    [-half, -half, 0]
                ], dtype=np.float32)

                all_rvecs = []
                all_tvecs = []

                for c in corners:
                    img_points = c[0].astype(np.float32)

                    ok, rvec, tvec = cv2.solvePnP(
                        obj_points,
                        img_points,
                        camera_matrix,
                        dist_coeffs,
                        flags=cv2.SOLVEPNP_ITERATIVE
                    )

                    all_rvecs.append(rvec.reshape(3, 1))
                    all_tvecs.append(tvec.reshape(3, 1))

                rvecs = all_rvecs
                tvecs = all_tvecs

                # 打印（只在检测时打印）
                for i, marker_id in enumerate(ids.flatten()):
                    corner = corners[i][0]
                    u = float(np.mean(corner[:, 0]))
                    v = float(np.mean(corner[:, 1]))
                    r = rvecs[i]
                    yaw = get_yaw_from_rvec(r)

                    print(
                        f"[ID {marker_id}] "
                        f"Pos: x={u:.3f}, y={v:.3f}  |  "
                        f"Yaw={yaw:.1f}"
                    )

                # 更新缓存
                last_ids = ids
                last_corners = corners

            else:
                # ---------------------------
                #   ArUco 消失：打印消失信息
                # ---------------------------
                if last_ids is not None:
                    for marker_id in last_ids.flatten():
                        print(f"[ID {marker_id}] disappeared")

                # 清空缓存（画面不再绘制）
                last_ids = None
                last_corners = None

        # ----------------------
        #      绘 图 部 分
        # ----------------------
        if last_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, last_corners, last_ids)

        cv2.imshow("Aruco (Lazy Detection + Print Control)", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
