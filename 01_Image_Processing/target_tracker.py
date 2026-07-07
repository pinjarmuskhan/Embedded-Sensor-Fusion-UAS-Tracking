import cv2
import time
import sys
from picamera2 import Picamera2 

def initialize_tracker():
    print("[INFO] Initializing native Pi 5 vision stream matrix...")
    try:
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(main={"size": (640, 480)}))
        picam.start()
        print("[SUCCESS] Connected to native hardware camera module!")
    except Exception as e:
        print(f"[ERROR] Critical failure connecting to hardware: {e}")
        sys.exit(1)

    print("[INFO] Warming up camera sensor matrix...")
    time.sleep(2.0)
    prev_time = 0

    while True:
        current_time = time.time()
        frame = picam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time

        cv2.putText(frame, f"FPS: {fps:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Primary Tracking Stream - Phase 1", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam.stop()
    cv2.destroyAllWindows()
    print("[INFO] Vision node shutdown completed cleanly.")

if __name__ == "__main__":
    initialize_tracker()

