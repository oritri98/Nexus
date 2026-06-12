# Nexus - Sci-Fi Glassmorphic Gesture Control Hub

Nexus is a next-generation gesture-based spatial interface that uses OpenCV to capture webcam input, MediaPipe to track a 21-point hand skeleton in real-time, and FastAPI/WebSockets to stream telemetry and coordinates to a beautiful, glassmorphic control center web UI.

---

## Folder Structure

```
gesture-control-app/
├── backend/
│   ├── main.py            # FastAPI WebSocket Server + MediaPipe/OpenCV Thread
│   └── requirements.txt   # Python Dependencies
├── frontend/
│   ├── index.html         # Glassmorphic Dashboard Layout
│   ├── style.css          # Cyberpunk/Neon Dark-mode Stylesheet
│   └── app.js             # WebSocket Controller & SVG Skeleton Hand Renderer
└── README.md              # This User Guide
```

---

## Architecture Design

Instead of rendering telemetry over a raw OpenCV window or streaming heavy camera video frames to the browser, Nexus separates the **Core Tracking Thread** and the **Dashboard User Interface**:
1. **Core Thread (Python)**: Continuously reads the camera, executes the MediaPipe tracking model, calculates cursor coordinates via Linear Interpolation (smoothing), checks distances between fingers to trigger OS commands via PyAutoGUI, and updates a shared state.
2. **FastAPI Web Server**: Serves the frontend web pages and opens a WebSockets endpoint (`/ws`).
3. **Telemetry Streaming**: Streams normalized joint coordinates (21 coordinates, 30 times per second) and action states down to the frontend.
4. **SVG Hand Skeleton Visualizer**: The frontend JS maps these coordinates onto an SVG wireframe hand canvas, offering real-time tracking feedback.
5. **Control Deck**: Sliders and checkboxes on the web dashboard immediately send updates back to the Python backend to adjust cursor smoothing and toggle individual gestures.

---

## Installation & Setup

### 1. Install Dependencies
Make sure you have python installed. Run the following command in your terminal to install the required packages:
```bash
pip install -r backend/requirements.txt
```

### 2. Run the App
Navigate to the project directory and run the main backend script:
```bash
python backend/main.py
```

### 3. Open the Dashboard
Once the server starts up, open your web browser and navigate to:
```
http://localhost:8000
```

---

## Active Gestures

- **Hover**: Move your index finger to glide the cursor across the screen.
- **Left Click & Drag**: Pinch Index + Thumb. Hold contact to drag windows.
- **Right Click**: Pinch Middle + Thumb.
- **Double Click**: Pinch Ring + Thumb.
- **Infinite Scroll**: Raise Index + Middle fingers (Peace sign) and move vertically.
- **DJ Volume Mixer**: Pinch Pinky + Thumb, then move your hand vertically.
- **The Boss Key**: Form a Closed Fist to instantly minimize all windows. Open hand to restore them.
- **Spider-Man Screenshot**: Extend Index, Pinky, and Thumb (curl Middle and Ring) to capture a screenshot (saved to `screenshots/` directory).

---

## Customization

- **Cursor Smoothing**: Use the slider in the web control deck. Higher values damp cursor jitter (but add slight latency).
- **Toggle Gestures**: Enable or disable specific gesture actions directly from the dashboard card toggles.
- **Local Video Feed**: Turn on "Local Camera Feed Window" in the settings panel to show the raw webcam monitor.
