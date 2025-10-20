# 🎯 HC-05 Gesture Controller

A modern **Python GUI application** that allows you to **control and visualize gestures** using an **HC-05 Bluetooth module**. The app is designed for **Human-Computer Interaction (HCI)** experiments and supports **real-time gesture detection and transmission**.

---

## 🌟 Features

- **Live Gesture Display**  
  Visualize gestures in real-time with expressive emojis:  
  - 👈 LEFT  
  - 👋 CENTER  
  - 👉 RIGHT  
  - ✋ NONE  

- **Bluetooth Connectivity**  
  - Connect/disconnect to an HC-05 module.  
  - COM port selection and refresh.  
  - Status indicator with **green/red dot** for connection status.

- **Gesture Control**  
  - Send gestures manually using modern, colorful buttons.  
  - Gesture counts updated automatically for analytics.

- **Real-time Feedback**  
  - Displays the last received gesture from HC-05.  
  - Gesture visualizer updates in real-time, keeping the emoji **centered**.

- **Modern GUI**  
  - Colorful, intuitive interface.  
  - Hover effects on buttons.  
  - Clear layout for HCI experiments.

---

## 🛠️ Requirements

- Python 3.x  
- `tkinter` (usually included with Python)  
- `pyserial`  

Install dependencies:

```bash
pip install pyserial
