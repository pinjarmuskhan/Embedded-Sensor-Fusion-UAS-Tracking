# Design and Development of an Embedded Sensor Fusion Node for Real-Time UAS Tracking and Mitigation

An autonomous, multi-threaded edge-computing platform built on a Raspberry Pi 5. This system fuses real-time electro-optical target detection with parallel RF spectrum monitoring to maintain high-confidence locks on Unmanned Aircraft Systems (UAS) before triggering automated hardware mitigation interfaces.

## 🛠️ Project Architecture & Roadmap

1. **01_Image_Processing**
   - Implements real-time video stream capture arrays utilizing optimized computer vision object tracking networks.
   
2. **02_RF_Detection**
   - Establishes an independent background frequency monitoring system utilizing Python `threading` workers to scan telemetry signal spikes without interrupting the main camera pipeline.

3. **03_Combined_Fusion**
   - Merges spatial vision bounding arrays and RF telemetry data streams into a single unified tracking matrix and live telemetry dashboard interface.

4. **04_Embedded_Mitigation**
   - Integrates the software decision engine with physical system layers. Bypasses standard system execution locks by calling direct Linux Sysfs core system paths to trigger physical pin voltages when target validation metrics are maintained continuously for over 2 seconds.

## 💻 Hardware Environment
- **Processing Core:** Raspberry Pi 5 (8GB RAM)
- **Vision Sensor:** Raspberry Pi Camera Module 3 (Continuous Autofocus Matrix Active)
- **Mitigation Simulation:** Broadcom BCM Pin 18 (Physical Pin 12) driving a low-power indicator circuit on a solderless breadboard.

