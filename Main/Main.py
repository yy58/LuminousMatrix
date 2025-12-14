# project/main.py
from multiprocessing import Process
import time
import signal
import sys

from Light2Max.C_Sound import run as run_light2max
from AreciboMessage.A_ArUcoDetector import run as run_aruco
from AreciboMessage.B_AreciboMessage import run as run_render


def main():
    p_c = Process(target=run_light2max, name="Light2Max-C")
    p_a = Process(target=run_aruco, name="Aruco-A")
    p_b = Process(target=run_render, name="Render-B")

    p_c.start()
    p_a.start()
    p_b.start()

    try:
        while True:
            time.sleep(1)
            if not (p_c.is_alive() and p_a.is_alive() and p_b.is_alive()):
                print("One process exited, shutting down.")
                break

    except KeyboardInterrupt:
        print("\nCtrl+C received, terminating processes...")

    finally:
        for p in (p_c, p_a, p_b):
            if p.is_alive():
                p.terminate()
                p.join()

        sys.exit(0)


if __name__ == "__main__":
    main()
