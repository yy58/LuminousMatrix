import cv2
import numpy as np
import math

MARKER_LENGTH = 0.02

class ArucoDetector:
    """
    ArUco 检测器
    - 一张 frame 就检测一次
    - solvePnP 不改
    - 打印内容不改
    - drawDetectedMarkers 不改
    """

    def __init__(self):
        params = np.load("camera_params.npz")
        self.camera_matrix = params["camera_matrix"]
        self.dist_coeffs = params["dist_coeffs"]

        self.dict_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.dict_aruco, self.parameters)

        # 缓存上一帧检测数据（用于绘制）
        self.last_ids = None
        self.last_corners = None

    @staticmethod
    def get_yaw_from_rvec(rvec):
        R, _ = cv2.Rodrigues(rvec)
        yaw = math.atan2(R[1, 0], R[0, 0])
        return np.degrees(yaw)

    def detect(self, frame):
        """
        对传入的单帧进行 ArUco 检测
        返回: (ids, corners, rvecs, tvecs) 或 None
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        if ids is not None:
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
                    self.camera_matrix,
                    self.dist_coeffs,
                    flags=cv2.SOLVEPNP_ITERATIVE
                )
                all_rvecs.append(rvec.reshape(3, 1))
                all_tvecs.append(tvec.reshape(3, 1))

            rvecs = all_rvecs
            tvecs = all_tvecs

            # 打印（保持原逻辑）
            for i, marker_id in enumerate(ids.flatten()):
                corner = corners[i][0]
                u = float(np.mean(corner[:, 0]))
                v = float(np.mean(corner[:, 1]))
                r = rvecs[i]
                yaw = ArucoDetector.get_yaw_from_rvec(r)

                print(
                    f"[ID {marker_id}] "
                    f"Pos: x={u:.3f}, y={v:.3f}  |  "
                    f"Yaw={yaw:.1f}"
                )

            # 更新缓存，用于绘制
            self.last_ids = ids
            self.last_corners = corners

            return ids, corners, rvecs, tvecs
        else:
            # ArUco 消失打印信息
            if self.last_ids is not None:
                for marker_id in self.last_ids.flatten():
                    print(f"[ID {marker_id}] disappeared")
            self.last_ids = None
            self.last_corners = None
            return None

    def draw(self, frame):
        """保持原绘制逻辑"""
        if self.last_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, self.last_corners, self.last_ids)
