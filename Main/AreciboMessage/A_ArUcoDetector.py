import cv2
import numpy as np
import math

import zmq
import pickle


MARKER_LENGTH = 0.02

ZMQ_FRAME_PORT = 5555   # from file C
ZMQ_ARUCO_PORT = 5556  # to file B

# Calculate yaw angle
def get_yaw_from_rvec(rvec):
    R, _ = cv2.Rodrigues(rvec)
    yaw = math.atan2(R[1, 0], R[0, 0])
    return np.degrees(yaw)

def run():
        # -------- Receive frames from C --------
    ctx = zmq.Context()

    frame_sub = ctx.socket(zmq.SUB)
    frame_sub.connect(f"tcp://localhost:{ZMQ_FRAME_PORT}")
    frame_sub.setsockopt_string(zmq.SUBSCRIBE, "")

    # -------- Publish ArUco data to B --------
    aruco_pub = ctx.socket(zmq.PUB)
    aruco_pub.bind(f"tcp://*:{ZMQ_ARUCO_PORT}")


    params = np.load("camera_params.npz")
    camera_matrix = params["camera_matrix"]
    dist_coeffs = params["dist_coeffs"]

    dict_aruco = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dict_aruco, parameters)

    last_ids = None
    last_corners = None


    while True:
        # Receive frame from C
        frame = pickle.loads(frame_sub.recv())

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray)

        # Found ArUco
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
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_ITERATIVE
                )

                all_rvecs.append(rvec.reshape(3, 1))
                all_tvecs.append(tvec.reshape(3, 1))

            rvecs = all_rvecs
            tvecs = all_tvecs

            aruco_list = []
            for i, marker_id in enumerate(ids.flatten()):
                corner = corners[i][0]
                u = float(np.mean(corner[:, 0]))
                v = float(np.mean(corner[:, 1]))
                r = rvecs[i]
                yaw = get_yaw_from_rvec(r)

                aruco_list.append({
                    "id": int(marker_id),
                    "x": round(u, 1),
                    "y": round(v, 1),
                    "yaw": round(float(yaw), 1)
                })

                print(
                    f"[ID {marker_id}] "
                    f"Pos: x={u:.1f}, y={v:.1f}  |  "
                    f"Yaw={yaw:.1f}"
                )

            # Send to B
            aruco_pub.send_pyobj(aruco_list)
            print("----")


            # Update cache
            last_ids = ids
            last_corners = corners

        else:
            #   Print disappearance info
            if last_ids is not None:
                for marker_id in last_ids.flatten():
                    print(f"[ID {marker_id}] disappeared")
                    aruco_pub.send_pyobj([])

            # Clear cache (stop drawing)
            last_ids = None
            last_corners = None

        # Drawing Part
        if last_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, last_corners, last_ids)

        cv2.imshow("Aruco Detection", frame)
        if cv2.waitKey(1) == 27:
            break

    frame_sub.close()
    aruco_pub.close()
    ctx.term()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
