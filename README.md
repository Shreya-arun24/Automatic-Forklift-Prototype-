# Automatic Forklift Prototype using Vibrational Analysis

## Project Overview

This project presents an intelligent forklift prototype that integrates embedded sensors, real-time monitoring, and vibration analysis to enhance warehouse automation and safety. The system continuously monitors its lifting dynamics and mechanical health through advanced sensor integration and signal processing.

## 🎯 Key Features

- **Real-time Vibrational Analysis**: Continuous monitoring of mechanical stress and structural integrity
- **Omnidirectional Movement**: Mecanum wheel-based locomotion for enhanced maneuverability
- **Precision Lifting**: Lead screw mechanism with NEMA stepper motor for accurate load handling
- **Smart Sensing**: Load cell integration for weight measurement and vibration detection
- **Remote Control**: Flutter-based mobile application for wireless operation
- **Predictive Maintenance**: Early fault detection through signal processing
- **3D Simulation**: PyGame and OpenGL-based warehouse environment simulation

## 🏗️ System Architecture

### Hardware Components

- **Raspberry Pi 4**: Central processing unit and system controller
- **NEMA 17 Stepper Motor**: Precision lifting mechanism
- **Lead Screw Assembly**: Linear motion conversion system
- **Mecanum Wheels (4x)**: Omnidirectional locomotion system
- **Load Cell**: Weight measurement and vibration sensing
- **Motor Drivers**: Stepper and DC motor control interfaces

### Software Stack

- **Control System**: Python-based Raspberry Pi programming
- **Mobile App**: Flutter/Dart cross-platform application
- **Signal Processing**: FFT, Wavelet Transform, STFT analysis
- **Simulation**: PyGame with OpenGL for 3D visualization
- **Data Analysis**: SciPy for advanced signal processing

## 📱 Mobile Application

The Flutter-based mobile application provides:

- Directional control (forward, backward, left, right, rotate)
- Lifting mechanism control (up/down)
- Real-time sensor feedback display
- Wireless communication via Bluetooth/Wi-Fi
- User-friendly interface with responsive design

## 🔧 Installation & Setup

### Hardware Requirements

```
- Raspberry Pi 4 (4GB RAM recommended)
- NEMA 17 Stepper Motor
- Lead Screw Assembly
- 4x Mecanum Wheels with DC Motors
- Load Cell (HX711 compatible)
- Motor Driver Boards (A4988/DRV8825)
- Power Supply (12V/5V)
- Chassis and Mechanical Components
```

### Software Dependencies

```bash
# Raspberry Pi Setup
sudo apt update
sudo apt install python3-pip
pip3 install numpy scipy matplotlib pygame PyOpenGL

# For signal processing
pip3 install scikit-learn pandas

# GPIO control
pip3 install RPi.GPIO gpiozero
```

### Mobile App Setup

```bash
# Install Flutter
flutter doctor
flutter pub get

# Build and install
flutter build apk
```

## 🚀 Usage

### 1. Hardware Assembly
- Mount the stepper motor and lead screw assembly
- Install mecanum wheels and connect motor drivers
- Position load cell on the fork mechanism
- Connect all components to Raspberry Pi GPIO pins

### 2. Software Configuration
```python
# Basic control example
from forklift_control import ForkliftController

controller = ForkliftController()
controller.initialize_sensors()
controller.start_monitoring()
```

### 3. Mobile App Connection
- Enable Bluetooth/Wi-Fi on Raspberry Pi
- Launch the mobile application
- Connect to the forklift system
- Begin remote operation

## 📊 Vibrational Analysis Features

### Signal Processing Methods
- **Fast Fourier Transform (FFT)**: Frequency domain analysis
- **Wavelet Transform**: Time-frequency analysis
- **Short-Time Fourier Transform (STFT)**: Dynamic frequency analysis

### Monitoring Capabilities
- Load condition assessment
- Mechanical stress detection
- Early fault identification
- Predictive maintenance alerts
- Real-time performance metrics

## 🎮 Simulation Environment

The 3D simulation provides:
- Realistic warehouse environment (20x20 units)
- Dynamic forklift movement and lifting
- Real-time vibration data generation
- Load handling scenarios
- Performance visualization

### Running the Simulation
```python
python3 forklift_simulation.py
```

## 📈 Data Analysis

### Vibration Patterns
- Empty load state: Baseline vibration levels
- Medium load state: Moderate stress indicators
- Heavy load state: High amplitude vibrations
- Anomaly detection: Threshold-based alerts

### Frequency Analysis
- Dominant frequencies: 5-6 Hz typical range
- Resonance detection: Peak identification
- Mechanical health assessment
- Wear pattern analysis

## 🔬 Research Applications

This prototype serves as a foundation for:
- Industrial automation research
- Predictive maintenance studies
- Vibration analysis methodologies
- Smart warehouse system development
- IoT integration in material handling

## 📚 Technical Documentation

### Key Algorithms
1. **Vibration Analysis Pipeline**
   - Data acquisition from load cell
   - Signal preprocessing and filtering
   - FFT-based frequency analysis
   - Anomaly detection algorithms

2. **Control System**
   - Stepper motor position control
   - Mecanum wheel coordination
   - Real-time sensor integration
   - Safety monitoring protocols

## 🏆 Project Team

- **Varshitha Thilak Kumar** - CB.SC.U4AIE23258
- **Siri Sanjana S** - CB.SC.U4AIE23249  
- **Shreya Arun** - CB.SC.U4AIE23253
- **Anagha Menon** - CB.SC.U4AIE23212

## 📖 References

1. Bouri, M., et al. "Vibration Analysis for Condition Monitoring of Forklift Trucks," IEEE Transactions on Industrial Electronics, 2020.
2. Kim, Y., Park, J. "Real-Time Load Detection in Automated Material Handling Systems," IJPEM, 2022.
3. Karthik, S., Devi, R. "Vibrational Signal Analysis Using FFT and Wavelet," IJMERR, 2021.
