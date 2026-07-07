import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
import time
import threading
import random
import os

# --- GLOBAL TELEMETRY VARIABLES ---
current_rf_power = -65.0
rf_status_text = "SCANNING..."
system_running = True

# --- TIMING & METRIC VARIABLES ---
drone_seen_start_time = None  
soft_kill_triggered = False   

# --- SYSFS DIRECT LINUX HARDWARE CONTROL LAYER ---
# BCM 18 corresponds precisely to Physical Pin 12
SYSFS_PIN = "18"  

def setup_hardware():
    """Initializes the physical pin using standard Linux filesystem paths."""
    print("[Hardware] Initializing pin interface via Linux Sysfs...")
    # Export the pin path if it isn't opened yet
    if not os.path.exists(f"/sys/class/gpio/gpio{SYSFS_PIN}"):
        try:
            with open("/sys/class/gpio/export", "w") as f:
                f.write(SYSFS_PIN)
            time.sleep(0.1)
        except Exception as e:
            print(f"[Hardware Warning] Software-only mode (Sysfs access denied): {e}")
            return False
            
    # Set pin configuration direction to Output
    try:
        with open(f"/sys/class/gpio/gpio{SYSFS_PIN}/direction", "w") as f:
            f.write("out")
        # Set a safe initial state (0V / Off)
        with open(f"/sys/class/gpio/gpio{SYSFS_PIN}/value", "w") as f:
            f.write("0")
        print(f"[Hardware Success] Connected directly to BCM Pin {SYSFS_PIN} (Physical Pin 12).")
        return True
    except Exception as e:
        print(f"[Hardware Warning] Configuration error on digital line: {e}")
        return False

def hardware_set_state(active=False):
    """Pushes voltage out of Physical Pin 12 by writing directly to the core file."""
    global hardware_available
    if hardware_available:
        try:
            val_str = "1" if active else "0"
            with open(f"/sys/class/gpio/gpio{SYSFS_PIN}/value", "w") as f:
                f.write(val_str)
        except Exception:
            pass

def cleanup_hardware():
    """Safely unexports the system path pin resource on program exit."""
    global hardware_available
    hardware_set_state(active=False)
    if os.path.exists(f"/sys/class/gpio/gpio{SYSFS_PIN}"):
        try:
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write(SYSFS_PIN)
            print("[Hardware] Pin released cleanly.")
        except Exception:
            pass

# Automatically check and boot the physical interface layer
hardware_available = setup_hardware()


def bladerf_rf_worker():
    """Background Thread: Updates the simulated frequency metrics independently 
    to ensure the main video track processing feed stays smooth."""
    global current_rf_power, rf_status_text, system_running
    while system_running:
        simulated_noise = random.uniform(-68.0, -45.0)
        
        if random.random() > 0.85:
            current_rf_power = random.uniform(-30.0, -12.0)
            rf_status_text = "RF ALERT: DRONE FREQUENCY SIGNATURE DETECTED"
        else:
            current_rf_power = simulated_noise
            rf_status_text = "SCANNING FREQUENCIES..."
            
        time.sleep(0.25)


def main():
    global current_rf_power, rf_status_text, system_running
    global drone_seen_start_time, soft_kill_triggered
    
    print("==========================================================")
    print("STARTING ACTIVE EMBEDDED SENSOR FUSION DRONE SENTINEL")
    print("==========================================================")
    
    # Load Neural Network weights configuration
    model = YOLO('yolov8n_drone.pt') 

    # Initialize Camera Module 3 Sensor Core
    picam2 = Picamera2()
    config = picam2.preview_configuration
    config.main.size = (640, 480)
    config.main.format = "BGR888"
    picam2.configure(config)
    picam2.start()

    try:
        picam2.set_controls({"AfMode": 2})  # Enable Continuous Autofocus
        picam2.autofocus_cycle()
        print("[Camera] Lens autofocus matrix calibrated successfully.")
    except Exception:
        pass

    # Launch parallel software tracking telemetry worker loop
    rf_thread = threading.Thread(target=bladerf_rf_worker, daemon=True)
    rf_thread.start()

    print("[System Engine Active] Entering live tracking feed loop...")
    time.sleep(1) 

    try:
        while True:
            frame = picam2.capture_array()
            if frame is None:
                continue

            # Run detection inference at native 640 configuration
            results = model(frame, verbose=False, imgsz=640, conf=0.25) 
            annotated_frame = frame.copy()

            # --- RENDER TELEMETRY DASHBOARD OVERLAY ---
            text_color = (0, 0, 255) if "ALERT" in rf_status_text else (0, 255, 255)
            cv2.putText(annotated_frame, f"RF Status: {rf_status_text}", (20, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)
            cv2.putText(annotated_frame, f"2.407 GHz Power: {current_rf_power:.1f} dBm", (20, 65), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            cv2.line(annotated_frame, (20, 75), (280, 75), (150, 150, 150), 1)

            drone_present_this_frame = False

            # --- EVALUATE INFERENCE DETECTIONS ---
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    conf_score = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Target classified as Drone (Class 4)
                    if class_id == 4:
                        drone_present_this_frame = True
                        
                        if drone_seen_start_time is None:
                            drone_seen_start_time = time.time()

                        elapsed_lock_time = time.time() - drone_seen_start_time

                        # --- VERIFIED THRESHOLD TRANSITION (2 SECONDS) ---
                        if elapsed_lock_time >= 2.0:
                            soft_kill_triggered = True
                            
                            # 1. HARDWARE: Turn on the physical LED indicator
                            hardware_set_state(active=True)

                            # 2. SOFTWARE DASHBOARD UI: High-visibility warning overlay bar
                            cv2.rectangle(annotated_frame, (0, 0), (640, 45), (0, 0, 180), -1)
                            cv2.putText(annotated_frame, "WARNING: COUNTERMEASURE ACTIVE - LOCK CONFIRMED", (40, 28), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                            
                            # Warning Cyan bounding box overlay indicator
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
                            cv2.putText(annotated_frame, f"DRONE MITIGATED ({conf_score:.2f})", (x1, y1 - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
                        else:
                            # Countdown locking lock state indicators
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(annotated_frame, f"LOCKING TARGET ({elapsed_lock_time:.1f}s)", (x1, y1 - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                        
                    # Target classified as Bird (Class 14)
                    elif class_id == 14:
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(annotated_frame, f"BIRD ({conf_score:.2f})", (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

            # --- AUTOMATED RESET FAILSAFE RESET TIMELINE ---
            if not drone_present_this_frame:
                drone_seen_start_time = None  
                if soft_kill_triggered:
                    soft_kill_triggered = False
                    hardware_set_state(active=False)  # Instantly cut voltage to 0V
                    print("[Failsafe Reset] Target tracking broken. Disarming physical pin.")

            # Output view processing canvas frames
            cv2.imshow("Multi-Sensor Drone Tracking Feed", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' key triggered manually. Safely terminating processes...")
                break

    except KeyboardInterrupt:
        print("\nManual break execution signal received.")

    finally:
        system_running = False
        cleanup_hardware()
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        print("System shutdown completed cleanly.")

if __name__ == '__main__':
    main()

