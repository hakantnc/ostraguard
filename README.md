# OstraGuard - Autonomous Robot Platform

OstraGuard is an autonomous robot platform that combines GPS tracking, camera vision, and motor control capabilities. The system is built using Raspberry Pi and Arduino components, making it suitable for various applications including surveillance, mapping, and autonomous navigation.

## Features

- **GPS Tracking**: Real-time GPS data collection and logging
- **Camera System**: High-resolution image capture with GPS coordinates
- **Motor Control**: Precise movement control using stepper motors
- **Sensor Integration**: 
  - Ultrasonic sensors for obstacle detection
  - MPU6050 gyroscope for orientation tracking
  - Servo motors for camera positioning

## Hardware Requirements

- Raspberry Pi (with camera module)
- Arduino board
- GPS module
- MPU6050 gyroscope
- Ultrasonic sensors (3x)
- Stepper motors (2x)
- Servo motors (2x)
- A4988 stepper motor drivers

## Software Requirements

- Python 3.x
- Required Python packages:
  - pynmea2
  - opencv-python (cv2)
  - picamera2
  - pyserial
- Arduino IDE

## Project Structure

```
├── camera_auto_focus.py    # Camera focus control
├── camera_with_gps.py      # Main camera and GPS integration
├── gps.py                  # GPS module interface
├── gps_data.json          # GPS data storage
├── robot_movement_arduino.ino  # Arduino motor control
└── Raspberry/             # Raspberry Pi specific files
```

## Setup Instructions

1. **Hardware Setup**:
   - Connect GPS module to Raspberry Pi's UART port
   - Connect Arduino to Raspberry Pi via USB
   - Connect stepper motors and sensors to Arduino
   - Mount camera module on Raspberry Pi

2. **Software Setup**:
   - Install required Python packages:
     ```bash
     pip install pynmea2 opencv-python picamera2 pyserial
     ```
   - Upload Arduino code using Arduino IDE
   - Configure GPS port in `camera_with_gps.py` if needed

3. **Running the System**:
   - Start the Arduino program
   - Run the camera and GPS integration:
     ```bash
     python camera_with_gps.py
     ```

## Data Collection

- Images are saved in the `frames` directory with timestamps
- GPS data is stored in `gps_data.json`
- Sensor data is continuously streamed to the Raspberry Pi

## Motor Control Commands

The system accepts the following commands:
- `CMD:FORWARD` - Move forward
- `CMD:BACKWARD` - Move backward
- `CMD:LEFT` - Turn left
- `CMD:RIGHT` - Turn right
- `CMD:STOP` - Stop all motors

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 