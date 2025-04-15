# Smart Traffic Signal System

A comprehensive AI-powered traffic management solution that leverages **computer vision**, **machine learning**, and **real-time data processing** to dynamically control traffic flow, detect emergency vehicles, and ensure road safety through a unified web interface.

---

## Overview

The **Smart Traffic Signal** system is designed to automate and optimize traffic signal control by analyzing real-time traffic density and giving priority to emergency vehicles such as ambulances. It consists of multiple integrated components that work together to provide an intelligent and responsive traffic control infrastructure.

## Architecture Diagram
![image](https://github.com/user-attachments/assets/6c9a998d-f34f-4882-b459-c422e9967649)


---

## Components

### 1. **Traffic Signal Control System**
- Core control logic for signal operations
- Real-time analysis of traffic density
- Adaptive signal timing based on congestion levels

### 2. **Vehicle Detection Module**
- Vehicle detection, counting, and classification using computer vision
- Traffic density estimation using live feed analysis
- Generates input for traffic signal controller

### 3. **Emergency Vehicle Detection (Ambulance)**
- Detection and tracking of emergency vehicles (ambulances)
- Automatically overrides standard signal patterns to prioritize emergency response
- Sends real-time alerts to the control system and web dashboard

### 4. **Web Dashboard - Road Safety Interface**
- Real-time visualization of traffic data
- Signal states and alerts for emergency vehicles
- Interactive analytics dashboard for performance monitoring

### 5. **Traffic Management System**
- Centralized system to manage, analyze, and report traffic data
- Facilitates smooth flow coordination across intersections
- Stores historical data for analysis and optimization

---

## Key Features

- ✅ **Real-Time Traffic Monitoring**
- 🚑 **Emergency Vehicle Priority System**
- ⏱️ **Dynamic Signal Timing Adjustment**
- 🌐 **Web-Based Monitoring Interface**
- 📊 **Traffic Data Analytics and Reporting**

---

## Technologies Used

| Category             | Technologies                                             |
|----------------------|----------------------------------------------------------|
| **Programming**      | Python, JavaScript                                       |
| **Computer Vision**  | OpenCV                                                   |
| **Machine Learning** | Scikit-learn, TensorFlow/Keras (if used for models)      |
| **Web Development**  | HTML, CSS, JavaScript                                    |
| **Backend ** | Flask              |
| **Data Processing**  | Pandas, NumPy                                            |

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kartik4540/Smart_Traffic_Signal
---

 Usage

-Vehicle Detection: Run the vehicle detection module with a connected camera or video feed.

-Traffic Signal Control: The controller script dynamically adjusts signal timings based on input from the vehicle detection module.

-Ambulance Detection: Emergency vehicles are prioritized when detected by the system.

---


DEMO:

-https://drive.google.com/file/d/1tguVPZsqqwmw4Qe-F5MrNu-5Jp3nM8pT/view?usp=sharing



