# Smart Attendance System with Liveness Detection

An AI-powered attendance system that uses **Face Recognition** combined with **Liveness Detection (Blink + Blur)** to prevent spoofing using photos or mobile screens.

---

## Features

* Face Recognition using `face_recognition`
  
* Blink Detection (Eye Aspect Ratio - EAR)
    
* Real-time webcam processing
  
* Multi-user support (each person tracked independently)
  
* Attendance logging in Excel (Name, Date, Time)
  
* Fast processing using image scaling

---

## Liveness Detection Logic

To ensure the detected face is **real and not a spoof**, the system applies:

* **Blink Detection** → User must blink to be verified
* **Blur Detection** → Detects low-quality or fake inputs
* **Time-based** verification

---

## Technologies Used

* Python
* OpenCV
* face_recognition (dlib)
* NumPy
* Pandas
* SciPy

---

## Project Structure

```
Attendance-System/
│
├── AttendanceSystem.py
├── requirements.txt
├── ImagesAttendance/
│   ├── person1.jpg
│   ├── person2.jpg
│
├── Attendance.xlsx   (generated automatically)
```

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/engasmaaibrahim/Attendance-System.git
cd Attendance-System
```

2. Create environment (optional but recommended):

```bash
conda create -n attendance_env python=3.10
conda activate attendance_env
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
python AttendanceSystem.py
```

* Webcam will start automatically
* Blink once to verify identity
* Attendance will be recorded

---


## Anti-Spoofing Capability

This system is designed to reduce spoofing attempts:

| Scenario          | Result         |
| ----------------- | -------------- |
| Real person       | ✅ Accepted     |
| Photo on phone    | ❌ Rejected     |
| No blink          | ❌ Not verified |
| Low quality image | ⚠️ Rejected    |


---


## Author

**Asmaa Ibrahim**
AI & Machine Learning Engineer

