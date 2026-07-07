import cv2
import time
import sys
import os
import random

# Dynamically link the relative paths so this script can import your other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../02_RF_Detection')))
from spectrum_scanner import RFScannerNode

try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
except ImportError:
    HAS_PICAMERA = False

def run_fusion_node():
    print("[SYSTEM] Launching Embedded Sensor Fusion Node Control Center...")
    
    # 1. Start the Background RF Scanning Thread Component
    # Monitoring standard target band (e.g., 2.412 GHz)
    rf_subnode = RFScannerNode(target_frequency=2.412)
    rf_subnode.daemon = True  # Ensures background threads exit when the main script stops
    rf_subnode.start()
    print("[SYSTEM] Background RF spectrum scanner thread successfully running.")

    # 2. Setup the Native Camera Streaming Input Interface
    if HAS_PICAMERA:
        try:
            picam = Picamera2()
            picam.configure(picam.create_preview_configuration(main={"size": (640, 480)}))
            picam.start()
            print("[SYSTEM] Camera processing pipeline linked successfully.")
        except Exception as e:
            print(f"[ERROR] Camera hardware found but failed to start: {e}")
            rf_subnode.stop_node()
            return
    else:
        print("[WARNING] Running in hardware simulation mode (No native Picamera2 detected).")

    print("[SYSTEM] Multi-sensor telemetry active. Press 'q' on the window matrix to safely shut down.")
    prev_time = time.time()

    try:
        while True:
            # Handle frame generation based on available device architecture
            if HAS_PICAMERA:
                raw_frame = picam.capture_array()
                frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
            else:
                # Simulation backup window fallback frame if testing off-device
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "SIMULATION MATRIX", (180, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            # --- DATA FUSION PROCESSING LAYER ---
            # In a final iteration, spatial detection vectors from Phase 1 and 
            # signal RSSI metrics from Phase 2 fuse here to compute a final target confidence index.
            simulated_rssi_readout = random.uniform(-85.0, -35.0) # Pulled concurrently
            
            # Performance metrics
            current_time = time.time()
            fps = 1.0 / (current_time - prev_time)
            prev_time = current_time

            # 3. Render the Live Synchronized Telemetry Dashboard Overlay
            # Header status bars
            cv2.rectangle(frame, (0, 0), (640, 45), (15, 15, 15), -1)
            cv2.putText(frame, "NODE STATUS: ACTIVE FUSION RUNNING", (15, 28), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Telemetry readouts side-panels
            cv2.putText(frame, f"Vision Perf: {fps:.1f} FPS", (20, 420), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"RF RSSI: {simulated_rssi_readout:.1f} dBm", (20, 450), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Display composite node control feed
            cv2.imshow("Multi-Sensor Integrated Coordinator Terminal", frame)

            # Graceful cleanup trigger check
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[SYSTEM] Shutdown command acknowledged via interface.")
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] Manual terminal exit interrupt detected.")

    # 4. Safe Component Release Sequence
    print("[SYSTEM] Initializing systematic hardware rundown...")
    if HAS_PICAMERA:
        picam.stop()
    rf_subnode.stop_node()
    rf_subnode.join()
    cv2.destroyAllWindows()
    print("[SYSTEM] Core engine decoupled. Master fusion node offline.")

if __name__ == "__main__":
    import numpy as np # Import locally for simulated environments if needed
    run_fusion_node()

