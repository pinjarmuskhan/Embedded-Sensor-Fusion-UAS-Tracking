import time
import threading
import random

class RFScannerNode(threading.Thread):
    def __init__(self, target_frequency=2.412):
        super().__init__()
        self.target_frequency = target_frequency  # frequency in GHz (e.g., standard Wi-Fi/drone band)
        self.is_running = True
        print(f"[RF INFO] Background scanning sub-node initialized at {self.target_frequency} GHz.")

    def run(self):
        """Background thread execution loop"""
        while self.is_running:
            # Simulating raw spectrum RSSI power signal parsing
            simulated_rssi = random.uniform(-90, -30) # Signal strength in dBm
            
            if simulated_rssi > -50:
                print(f"\n[ALERT] High signal peak detected: {simulated_rssi:.2f} dBm on channel!")
            
            # Scan cadence throttling to reduce CPU strain on the Pi
            time.sleep(0.5)

    def stop_node(self):
        self.is_running = False
        print("[RF INFO] Background spectrum sub-node halted.")

if __name__ == "__main__":
    # Local validation test run
    rf_node = RFScannerNode()
    rf_node.start()
    
    try:
        time.sleep(5)  # Let it scan for 5 seconds in the background
    except KeyboardInterrupt:
        pass
        
    rf_node.stop_node()
    rf_node.join()

