import cv2
import mediapipe as mp
import pyautogui
import math
import time
import threading
import asyncio
import os
import json
import webbrowser
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Initialize MediaPipe Hands Tasks API in the main thread scope
# This prevents thread-safety and dynamic lazy-loading issues inside child threads
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

base_options = mp_python.BaseOptions(model_asset_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "hand_landmarker.task")))
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=2,
                                       min_hand_detection_confidence=0.75,
                                       min_tracking_confidence=0.75)
detector = vision.HandLandmarker.create_from_options(options)

# Initialize FastAPI
app = FastAPI(title="Nexus Gesture Engine")

# Enable CORS for frontend web accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database file location
DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "users.json"))

# Pydantic model for User Logins
class LoginRequest(BaseModel):
    name: str
    email: str
    password: str

# Static Telemetry State (shared between tracking thread and WebSocket thread)
telemetry = {
    "fps": 0,
    "current_action": "SYSTEM IDLE",
    "action_color": [0, 255, 255], # RGB format
    "cursor": {"x": 0, "y": 0},
    "volume": 50,
    "desktop_active": False,
    "landmarks": [],
    "screen_size": {"width": 1920, "height": 1080}
}

# Configuration settings (dynamic from frontend)
config = {
    "engine_active": True,
    "smooth_closeness": 2.0,
    "show_opencv_window": False,
    "modalities": {
        "hand_gestures": True,
        "voice_commands": False
    },
    "gestures_enabled": {
        "hover": True,
        "boss_key": True,
        "screenshot": True,
        "volume": True,
        "scroll": True,
        "click": True,
        "right_click": True,
        "double_click": True
    }
}

# Screen coordinates setup
screen_w, screen_h = pyautogui.size()
telemetry["screen_size"] = {"width": screen_w, "height": screen_h}
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  

# Track WebSocket connections
connected_clients = set()

# Thread lock for telemetry object access
telemetry_lock = threading.Lock()

# Directory for screenshots
SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "screenshots"))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def draw_hand_skeleton(frame, landmarks, w, h, color):
    connections = [
        (0,1), (1,2), (2,3), (3,4),
        (0,5), (5,6), (6,7), (7,8),
        (5,9), (9,10), (10,11), (11,12),
        (9,13), (13,14), (14,15), (15,16),
        (13,17), (0,17), (17,18), (18,19), (19,20)
    ]
    for start_idx, end_idx in connections:
        pt1 = (int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h))
        pt2 = (int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h))
        cv2.line(frame, pt1, pt2, color, 2)
    for lm in landmarks:
        pt = (int(lm.x * w), int(lm.y * h))
        cv2.circle(frame, pt, 4, color, -1)


def tracking_loop():
    global telemetry, config, screen_w, screen_h
    
    cap = None
    global detector
    
    prev_x, prev_y = 0, 0
    prev_time = time.time()
    is_dragging = False
    desktop_active = False
    
    last_screenshot_time = 0
    last_right_click_time = 0
    last_boss_key_time = 0
    last_left_click_time = 0
    
    maximize_gesture_start = None
    minimize_gesture_start = None
    scroll_mode_active = False
    two_hands_open_start = None
    two_hands_closed_start = None
    last_both_open_time = 0
    last_both_closed_time = 0
    global_cooldown_until = 0

    PINCH_ENGAGE = 28
    PINCH_RELEASE = 40

    print("[SYSTEM] Core Tracking Thread Started.")

    while True:
        try:
            if not config.get("engine_active", True):
                if cap is not None and cap.isOpened():
                    cap.release()
                    cv2.destroyAllWindows()
                    print("[SYSTEM] Camera Released (Engine Standby).")
                time.sleep(0.2)
                continue
                
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    time.sleep(1.0)
                    continue
                print("[SYSTEM] Camera Initialized (Engine Active).")
                
            success, frame = cap.read()
            if not success:
                time.sleep(0.01)
                continue
                
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape 
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = detector.detect(mp_image)
            
            current_action = "SYSTEM IDLE"
            action_color = [0, 255, 255] # Cyan
            normalized_lms = []
            
            right_hand_state = None
            left_hand_state = None
            hands_data = []

            if results.hand_landmarks and results.handedness:
                for idx, hand_landmarks in enumerate(results.hand_landmarks):
                    category = results.handedness[idx][0].category_name
                    is_right_hand = (category == "Left") # Mirrored camera
                    
                    lm = hand_landmarks
                    normalized_lms.extend([{"x": p.x, "y": p.y, "z": p.z} for p in lm])
                    draw_hand_skeleton(frame, lm, w, h, (0, 255, 0) if is_right_hand else (255, 0, 255))
                    
                    thumb, index, middle, ring, pinky = lm[4], lm[8], lm[12], lm[16], lm[20]
                    
                    is_index_up = index.y < lm[6].y
                    is_middle_up = middle.y < lm[10].y
                    is_ring_up = ring.y < lm[14].y
                    is_pinky_up = pinky.y < lm[18].y
                    
                    is_open_palm = is_index_up and is_middle_up and is_ring_up and is_pinky_up
                    is_fist = not is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up
                    
                    # Thumbs up: thumb tip is significantly ABOVE the index MCP and straight
                    is_thumb_up = (thumb.y < lm[5].y - 0.06) and (thumb.y < lm[3].y - 0.02)
                    # Thumbs down: thumb tip is significantly BELOW the wrist and straight
                    is_thumb_down = (thumb.y > lm[0].y + 0.06) and (thumb.y > lm[3].y + 0.02)
                    
                    thm_x, thm_y = int(thumb.x * w), int(thumb.y * h)
                    idx_x, idx_y = int(index.x * w), int(index.y * h)
                    pky_x, pky_y = int(pinky.x * w), int(pinky.y * h)
                    
                    dist_idx_thumb = math.hypot(thm_x - idx_x, thm_y - idx_y)
                    dist_pky_thumb = math.hypot(thm_x - pky_x, thm_y - pky_y)
                    
                    state = {
                        "is_open_palm": is_open_palm,
                        "is_fist": is_fist,
                        "is_index_up": is_index_up,
                        "is_middle_up": is_middle_up,
                        "is_ring_up": is_ring_up,
                        "is_pinky_up": is_pinky_up,
                        "is_thumb_up": is_thumb_up,
                        "is_thumb_down": is_thumb_down,
                        "dist_idx_thumb": dist_idx_thumb,
                        "dist_pky_thumb": dist_pky_thumb,
                        "index_x": index.x,
                        "index_y": index.y
                    }
                    hands_data.append(state)
                    
                    if is_right_hand:
                        right_hand_state = state
                    else:
                        left_hand_state = state

                # Scroll toggle logic (Both hands)
                both_open = len(hands_data) >= 2 and all(h["is_open_palm"] for h in hands_data[:2])
                both_closed = len(hands_data) >= 2 and all(h["is_fist"] for h in hands_data[:2])
                
                curr_t = time.time()
                
                if both_open:
                    last_both_open_time = curr_t
                    if two_hands_open_start is None:
                        two_hands_open_start = curr_t
                    elif curr_t - two_hands_open_start > 1.0:
                        if not scroll_mode_active:
                            scroll_mode_active = True
                            global_cooldown_until = curr_t + 1.0
                else:
                    if curr_t - last_both_open_time > 0.3:
                        two_hands_open_start = None
                        
                if both_closed:
                    last_both_closed_time = curr_t
                    if two_hands_closed_start is None:
                        two_hands_closed_start = curr_t
                    elif curr_t - two_hands_closed_start > 1.0:
                        if scroll_mode_active:
                            scroll_mode_active = False
                            global_cooldown_until = curr_t + 1.0
                else:
                    if curr_t - last_both_closed_time > 0.3:
                        two_hands_closed_start = None

                if scroll_mode_active:
                    current_action = "SCROLL MODE ACTIVE"
                    action_color = [255, 0, 255]
                    # During scroll mode, only scrolling works. Let's say right hand controls it.
                    if right_hand_state and config["gestures_enabled"].get("scroll", True):
                        if right_hand_state["is_index_up"] and not right_hand_state["is_middle_up"]:
                            pyautogui.scroll(30)
                        elif right_hand_state["is_index_up"] and right_hand_state["is_middle_up"]:
                            pyautogui.scroll(-30)
                elif both_open or both_closed or curr_t < global_cooldown_until:
                    # BLOCK ALL NORMAL GESTURES
                    current_action = "GESTURE STANDBY"
                    action_color = [100, 100, 100]
                else:
                    # Normal Gestures
                    if config["modalities"]["hand_gestures"]:
                        if right_hand_state:
                            state = right_hand_state
                            
                            target_x = int(state["index_x"] * screen_w)
                            target_y = int(state["index_y"] * screen_h)
                            smooth = float(config["smooth_closeness"])
                            curr_x = prev_x + (target_x - prev_x) / smooth
                            curr_y = prev_y + (target_y - prev_y) / smooth
                            
                            # Right Click: Only pinky showing
                            if state["is_pinky_up"] and not state["is_index_up"] and not state["is_middle_up"] and not state["is_ring_up"] and not state["is_thumb_up"]:
                                if config["gestures_enabled"].get("right_click", True) and (time.time() - last_right_click_time > 1.0):
                                    current_action = "RIGHT CLICK"
                                    action_color = [255, 165, 0]
                                    pyautogui.click(button='right')
                                    last_right_click_time = time.time()
                                    
                            # Left Click: Pinch index and thumb
                            elif state["dist_idx_thumb"] < PINCH_ENGAGE and config["gestures_enabled"].get("click", True):
                                if time.time() - last_left_click_time > 0.5:
                                    current_action = "LEFT CLICK"
                                    action_color = [0, 255, 0]
                                    pyautogui.click()
                                    last_left_click_time = time.time()
                                    
                            # Drag: Pinch thumb and pinky
                            elif state["dist_pky_thumb"] < PINCH_ENGAGE and config["gestures_enabled"].get("click", True):
                                current_action = "DRAG ENGAGED"
                                action_color = [0, 100, 255]
                                if not is_dragging:
                                    pyautogui.mouseDown()
                                    is_dragging = True
                                pyautogui.moveTo(int(curr_x), int(curr_y))
                                prev_x, prev_y = curr_x, curr_y
                            
                            # Move cursor: index finger showing
                            elif state["is_index_up"]:
                                if is_dragging and state["dist_pky_thumb"] > PINCH_RELEASE:
                                    pyautogui.mouseUp()
                                    is_dragging = False
                                
                                current_action = "CURSOR HOVER"
                                action_color = [0, 255, 255]
                                if config["gestures_enabled"].get("hover", True):
                                    pyautogui.moveTo(int(curr_x), int(curr_y))
                                prev_x, prev_y = curr_x, curr_y
                                
                            else:
                                if is_dragging:
                                    pyautogui.mouseUp()
                                    is_dragging = False
                                if current_action == "SYSTEM IDLE":
                                    current_action = "POINTER STOP (HAND OPEN)"
                                    action_color = [100, 255, 255]

                        if left_hand_state:
                            state = left_hand_state
                            curr_t = time.time()
                            
                            is_maximize_pose = state['is_open_palm']
                            is_minimize_pose = state['is_fist'] and not state['is_thumb_up'] and not state['is_thumb_down']
                            
                            # 1. Maximize windows: Palm open
                            if is_maximize_pose:
                                if maximize_gesture_start is None:
                                    maximize_gesture_start = curr_t
                                elif curr_t - maximize_gesture_start > 0.6:
                                    if config['gestures_enabled'].get('boss_key', True):
                                        if desktop_active and (curr_t - last_boss_key_time > 1.5):
                                            current_action = 'MAXIMIZE WINDOWS'
                                            action_color = [0, 255, 0]
                                            pyautogui.hotkey('win', 'd')
                                            desktop_active = False
                                            last_boss_key_time = curr_t
                            else:
                                maximize_gesture_start = None
                                    
                            # 2. Minimize windows: Palm close motion
                            if is_minimize_pose:
                                if minimize_gesture_start is None:
                                    minimize_gesture_start = curr_t
                                elif curr_t - minimize_gesture_start > 0.6:
                                    if config['gestures_enabled'].get('boss_key', True):
                                        if not desktop_active and (curr_t - last_boss_key_time > 1.5):
                                            current_action = 'MINIMIZE WINDOWS'
                                            action_color = [255, 0, 0]
                                            pyautogui.hotkey('win', 'd')
                                            desktop_active = True
                                            last_boss_key_time = curr_t
                            else:
                                minimize_gesture_start = None

                            # 3. Screenshot: Phone call sign
                            if state['is_thumb_up'] and state['is_pinky_up'] and not state['is_index_up'] and not state['is_middle_up'] and not state['is_ring_up']:
                                if config['gestures_enabled'].get('screenshot', True) and (curr_t - last_screenshot_time > 3.0):
                                    current_action = 'SCREENSHOT'
                                    action_color = [255, 255, 255]
                                    screenshot_path = os.path.join(SCREENSHOT_DIR, f'screenshot_{int(curr_t)}.png')
                                    pyautogui.screenshot(screenshot_path)
                                    last_screenshot_time = curr_t
                                    
                            # 4. Volume Controls
                            if state['is_fist']:
                                if state['is_thumb_up'] and config['gestures_enabled'].get('volume', True):
                                    current_action = 'VOLUME UP'
                                    action_color = [255, 255, 0]
                                    pyautogui.press('volumeup')
                                elif state['is_thumb_down'] and config['gestures_enabled'].get('volume', True):
                                    current_action = 'VOLUME DOWN'
                                    action_color = [255, 255, 0]
                                    pyautogui.press('volumedown')

            # Calculate local FPS
            curr_time = time.time()
            fps = int(1 / (curr_time - prev_time)) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            with telemetry_lock:
                telemetry["fps"] = fps
                telemetry["current_action"] = current_action
                telemetry["action_color"] = action_color
                telemetry["cursor"] = {"x": int(prev_x), "y": int(prev_y)}
                telemetry["desktop_active"] = desktop_active
                telemetry["landmarks"] = normalized_lms
                
            if config["show_opencv_window"]:
                cv2.rectangle(frame, (40, 80), (w - 40, h - 40), (50, 50, 50), 1)
                cv2.putText(frame, "ACTIVE TRACKING ZONE", (45, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
                cv2.putText(frame, f"STATE: {current_action}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, tuple(action_color[::-1]), 2)
                cv2.putText(frame, f"FPS: {fps}", (w - 110, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)
                
                cv2.imshow("Nexus Gesture Engine - Tracking Monitor", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    config["show_opencv_window"] = False
                    cv2.destroyAllWindows()
            else:
                try:
                    if cv2.getWindowProperty("Nexus Gesture Engine - Tracking Monitor", cv2.WND_PROP_VISIBLE) >= 1:
                        cv2.destroyAllWindows()
                except:
                    pass
                    
            time.sleep(0.001)
        except Exception as e:
            print(f"[ERROR] Tracking loop error: {e}")
            time.sleep(1)


# Start tracking loop in a background daemon thread
t = threading.Thread(target=tracking_loop, daemon=True)
t.start()


# FastAPI WebSockets Connection
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"[SYSTEM] WebSocket Client Connected. Total: {len(connected_clients)}")
    
    # Task to handle incoming messages (e.g. changing settings)
    async def receive_messages():
        global config
        try:
            while True:
                data = await websocket.receive_json()
                if data.get("type") == "update_settings":
                    new_settings = data.get("settings", {})
                    # Update config safely
                    if "engine_active" in new_settings:
                        config["engine_active"] = bool(new_settings["engine_active"])
                    if "smooth_closeness" in new_settings:
                        config["smooth_closeness"] = float(new_settings["smooth_closeness"])
                    if "show_opencv_window" in new_settings:
                        config["show_opencv_window"] = bool(new_settings["show_opencv_window"])
                    if "gestures_enabled" in new_settings:
                        for gesture_key, val in new_settings["gestures_enabled"].items():
                            if gesture_key in config["gestures_enabled"]:
                                config["gestures_enabled"][gesture_key] = bool(val)
                    if "modalities" in new_settings:
                        for mod_key, val in new_settings["modalities"].items():
                            if mod_key in config["modalities"]:
                                config["modalities"][mod_key] = bool(val)
                    print(f"[SYSTEM] Config Updated: {config}")
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[ERROR] WebSocket receive error: {e}")

    # Start the receiver task
    receive_task = asyncio.create_task(receive_messages())
    
    try:
        # Stream telemetry data down to the frontend client
        while True:
            with telemetry_lock:
                # Create a copy of the telemetry data to send
                data_to_send = dict(telemetry)
            
            # Send data at ~30 FPS
            try:
                await websocket.send_json(data_to_send)
            except (WebSocketDisconnect, RuntimeError):
                break
            await asyncio.sleep(0.033)
            
    except WebSocketDisconnect:
        print("[SYSTEM] WebSocket Client Disconnected.")
    finally:
        connected_clients.remove(websocket)
        receive_task.cancel()

@app.post("/api/login")
def handle_login(data: LoginRequest):
    import re
    from fastapi.responses import JSONResponse
    
    email = data.email.strip().lower()
    name = data.name.strip()
    password = data.password.strip()
    
    # --- VALIDATION 1: Name must not be empty ---
    if not name or len(name) < 2:
        return JSONResponse(status_code=400, content={"status": "error", "code": "INVALID_NAME", "message": "Operator name must be at least 2 characters."})
    
    # --- VALIDATION 2: Must be a valid Gmail address ---
    gmail_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9.]*[a-zA-Z0-9])?@gmail\.com$'
    if not re.match(gmail_pattern, email):
        return JSONResponse(status_code=400, content={"status": "error", "code": "INVALID_EMAIL", "message": "Only valid Gmail addresses (@gmail.com) are accepted."})
    
    # --- VALIDATION 3: Password must be at least 6 characters ---
    if len(password) < 6:
        return JSONResponse(status_code=400, content={"status": "error", "code": "WEAK_PASSWORD", "message": "Access key must be at least 6 characters."})
    
    # Load existing users
    users = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                users = json.load(f)
        except Exception as e:
            print(f"[DATABASE ERROR] Could not read database file: {e}")
    
    # --- CHECK: Does this email already exist? ---
    existing_user = None
    for user in users:
        if user.get("email", "").lower() == email:
            existing_user = user
            break
    
    if existing_user:
        # Email already registered — this is a LOGIN attempt
        if existing_user["password"] == password:
            print(f"\n[DATABASE] Returning Operator Authenticated!")
            print(f"  Name:  {existing_user['name']}")
            print(f"  Email: {email}\n")
            return {"status": "success", "message": "Welcome back, Operator.", "mode": "login"}
        else:
            return JSONResponse(status_code=401, content={"status": "error", "code": "WRONG_PASSWORD", "message": "Incorrect access key for this email."})
    
    # --- NEW REGISTRATION ---
    record = {
        "name": name,
        "email": email,
        "password": password,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    users.append(record)
    
    try:
        with open(DB_FILE, "w") as f:
            json.dump(users, f, indent=4)
        print(f"\n[DATABASE] New Operator Registered!")
        print(f"  Name:     {name}")
        print(f"  Email:    {email}")
        print(f"  Saved to: {DB_FILE}\n")
    except Exception as e:
        print(f"[DATABASE ERROR] Could not write database file: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "code": "DB_ERROR", "message": "System error. Try again."})
        
    return {"status": "success", "message": "Access Granted. Operator registered.", "mode": "register"}

# Mount frontend directory to serve the Glassmorphic Dashboard
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Run server on port 8000
    print("[SYSTEM] Launching Web Interface on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
