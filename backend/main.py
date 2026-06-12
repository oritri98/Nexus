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

# Initialize MediaPipe Hands in the main thread scope
# This prevents thread-safety and dynamic lazy-loading issues inside child threads
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)

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


def tracking_loop():
    global telemetry, config, screen_w, screen_h
    
    cap = None
        
    # Using global 'hands' initialized in main thread
    global hands
    # State variables
    prev_x, prev_y = 0, 0
    prev_time = time.time()
    is_dragging = False
    desktop_active = False
    vol_clutch_active = False
    vol_start_y = 0
    last_screenshot_time = 0
    scroll_mode_active = False

    # Non-blocking debounce timestamps (replaces blocking pyautogui.sleep)
    last_boss_key_time = 0
    last_right_click_time = 0
    last_double_click_time = 0
    last_scroll_toggle_time = 0
    last_youtube_time = 0

    # Hysteresis thresholds to prevent drag buzzing
    PINCH_ENGAGE = 28     # distance to START drag
    PINCH_RELEASE = 40    # distance to STOP drag (wider gap = stable)

    print("[SYSTEM] Core Tracking Thread Started.")

    while True:
        # Check if engine has been disabled
        if not config.get("engine_active", True):
            if cap is not None and cap.isOpened():
                cap.release()
                cv2.destroyAllWindows()
                print("[SYSTEM] Camera Released (Engine Standby).")
            time.sleep(0.2)
            continue
            
        # Initialize camera if not active
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[ERROR] Camera could not be opened. Retrying...")
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
        results = hands.process(rgb_frame)
        
        current_action = "SYSTEM IDLE"
        action_color = [0, 255, 255] # Cyan
        normalized_lms = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                
                # Convert landmarks to simple list of dicts for WebSocket transmission
                normalized_lms = [{"x": p.x, "y": p.y, "z": p.z} for p in lm]
                
                # Fingertips landmarks
                thumb, index, middle, ring, pinky = lm[4], lm[8], lm[12], lm[16], lm[20]
                
                # --- CURSOR MATH ---
                target_x = int(index.x * screen_w)
                target_y = int(index.y * screen_h)
                
                # Dynamic smooth factor
                smooth = float(config["smooth_closeness"])
                curr_x = prev_x + (target_x - prev_x) / smooth
                curr_y = prev_y + (target_y - prev_y) / smooth
                
                # --- CAMERA PIXELS FOR GESTURE RANGE MATH ---
                thm_x, thm_y = int(thumb.x * w), int(thumb.y * h)
                idx_x, idx_y = int(index.x * w), int(index.y * h)
                mid_x, mid_y = int(middle.x * w), int(middle.y * h)
                rng_x, rng_y = int(ring.x * w), int(ring.y * h)
                pky_x, pky_y = int(pinky.x * w), int(pinky.y * h)
                
                # --- DISTANCE CALCULATIONS ---
                dist_left = math.hypot(thm_x - idx_x, thm_y - idx_y)
                dist_right = math.hypot(thm_x - mid_x, thm_y - mid_y)
                dist_double = math.hypot(thm_x - rng_x, thm_y - rng_y)
                dist_vol = math.hypot(thm_x - pky_x, thm_y - pky_y)
                
                # Scale-invariant anatomical check to prevent false pinches when fingers are folded
                w_x, w_y = int(lm[0].x * w), int(lm[0].y * h)
                
                mid_mcp_x, mid_mcp_y = int(lm[9].x * w), int(lm[9].y * h)
                rng_mcp_x, rng_mcp_y = int(lm[13].x * w), int(lm[13].y * h)
                pky_mcp_x, pky_mcp_y = int(lm[17].x * w), int(lm[17].y * h)
                
                # A finger is considered "active" (eligible for pinch) if its tip is further from the wrist 
                # than its knuckle. If folded tightly into a fist, the tip is tucked in closer to the wrist.
                is_mid_active = math.hypot(mid_x - w_x, mid_y - w_y) > (math.hypot(mid_mcp_x - w_x, mid_mcp_y - w_y) * 0.75)
                is_rng_active = math.hypot(rng_x - w_x, rng_y - w_y) > (math.hypot(rng_mcp_x - w_x, rng_mcp_y - w_y) * 0.75)
                is_pky_active = math.hypot(pky_x - w_x, pky_y - w_y) > (math.hypot(pky_mcp_x - w_x, pky_mcp_y - w_y) * 0.75)
                
                # -------------------------------------------------------------
                # GESTURE DETECTIONS (Finger States)
                # -------------------------------------------------------------
                # Using y-coordinates to determine if fingers are extended (Up) or folded (Down)
                # Note: Lower Y value = higher on screen.
                is_index_up = index.y < lm[6].y
                is_middle_up = middle.y < lm[10].y
                is_ring_up = ring.y < lm[14].y
                is_pinky_up = pinky.y < lm[18].y
                
                # Thumb orientation
                is_thumb_pointing_up = thumb.y < lm[3].y - 0.05
                is_thumb_pointing_down = thumb.y > lm[3].y + 0.05
                is_thumb_sideways = abs(thumb.y - lm[3].y) < abs(thumb.x - lm[3].x)
                
                all_fingers_folded = not is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up
                all_fingers_up = is_index_up and is_middle_up and is_ring_up and is_pinky_up
                
                # --- GESTURE ACTION TREE ---
                if config["modalities"]["hand_gestures"]:
                    
                    # 1. BOSS KEY (Minimize Window) - Thumbs Down (All fingers folded, thumb down)
                    if not is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up and is_thumb_pointing_down and config["gestures_enabled"].get("boss_key", True):
                        current_action = "BOSS KEY (DESKTOP MINIMIZE)"
                        action_color = [255, 0, 0] # Red
                        if not desktop_active and (time.time() - last_boss_key_time > 1.0):
                            pyautogui.hotkey('win', 'd')
                            desktop_active = True
                            last_boss_key_time = time.time()
                    else:
                        if desktop_active and config["gestures_enabled"].get("boss_key", True) and (time.time() - last_boss_key_time > 1.0):
                            pyautogui.hotkey('win', 'd')
                            desktop_active = False
                            last_boss_key_time = time.time()
                            
                        # 2. VOLUME DOWN - Closed Fist (All fingers folded, thumb not down)
                        if not is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up and not is_thumb_pointing_down and config["gestures_enabled"].get("volume", True):
                            current_action = "VOLUME DOWN"
                            action_color = [255, 255, 0] # Yellow
                            pyautogui.press('volumedown')
                            
                        # 3. VOLUME UP - Open Palm (All fingers up)
                        elif is_index_up and is_middle_up and is_ring_up and is_pinky_up and config["gestures_enabled"].get("volume", True):
                            current_action = "VOLUME UP"
                            action_color = [255, 255, 0] # Yellow
                            pyautogui.press('volumeup')
                            
                        # 4. SCREENSHOT - Call Me Sign (Pinky + Thumb up, others folded)
                        elif not is_index_up and not is_middle_up and not is_ring_up and is_pinky_up and is_thumb_pointing_up and config["gestures_enabled"].get("screenshot", True) and (time.time() - last_screenshot_time > 3.0):
                            current_action = "SCREENSHOT CAPTURED!"
                            action_color = [255, 255, 255] # White
                            screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
                            pyautogui.screenshot(screenshot_path)
                            last_screenshot_time = time.time()
                            print(f"[SYSTEM] Screenshot saved to: {screenshot_path}")
                            
                        # 5. RIGHT CLICK - Gun Shape (Index + Thumb up, others folded)
                        elif is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up and is_thumb_pointing_up and config["gestures_enabled"].get("right_click", True) and (time.time() - last_right_click_time > 0.4):
                            current_action = "RIGHT CLICK ISSUED"
                            action_color = [255, 165, 0] # Orange
                            pyautogui.click(button='right')
                            last_right_click_time = time.time()
                            
                        # 6. SCROLL TOGGLE - Three Fingers Up (Index + Middle + Ring up, Pinky folded)
                        elif is_index_up and is_middle_up and is_ring_up and not is_pinky_up and config["gestures_enabled"].get("scroll", True) and (time.time() - last_scroll_toggle_time > 1.0):
                            scroll_mode_active = not scroll_mode_active
                            last_scroll_toggle_time = time.time()
                            current_action = "SCROLL MODE TOGGLED"
                            action_color = [255, 0, 255] # Purple
                            
                        # 7. OPEN YOUTUBE - Peace Sign (Index + Middle up, Ring + Pinky folded)
                        elif is_index_up and is_middle_up and not is_ring_up and not is_pinky_up and config["gestures_enabled"].get("youtube", True) and (time.time() - last_youtube_time > 3.0):
                            current_action = "OPENING YOUTUBE"
                            action_color = [255, 0, 0] # Red YouTube
                            webbrowser.open('https://youtube.com')
                            last_youtube_time = time.time()
                            
                        # 8. SCROLL SYSTEM ACTIONS (If active)
                        elif scroll_mode_active:
                            current_action = "SCROLL MODE ACTIVE"
                            action_color = [255, 0, 255] # Purple
                            # Hand moving up (y decreases) = Scroll Up
                            # Hand moving down (y increases) = Scroll Down
                            # We can just use the index finger's Y coordinate to drive scrolling dynamically.
                            if is_index_up:
                                pyautogui.scroll(30)
                            elif not is_index_up:
                                pyautogui.scroll(-30)
                                
                        # 9. LEFT CLICK & DRAG & POINTER CONTROL
                        else:
                            # Pinch = Left Click / Drag
                            if dist_left < PINCH_ENGAGE and config["gestures_enabled"].get("click", True):
                                current_action = "DRAG / LEFT CLICK"
                                action_color = [0, 255, 0] # Green
                                if not is_dragging:
                                    pyautogui.mouseDown()
                                    is_dragging = True
                                # If dragging, and index is up (e.g. index/thumb pinch while moving)
                                pyautogui.moveTo(int(curr_x), int(curr_y))
                                prev_x, prev_y = curr_x, curr_y
                            
                            # Release drag
                            elif is_dragging and dist_left > PINCH_RELEASE:
                                pyautogui.mouseUp()
                                is_dragging = False
                                
                            # Move Pointer (Index finger ONLY up, Thumb NOT up)
                            elif is_index_up and not is_middle_up and not is_ring_up and not is_pinky_up and not is_thumb_pointing_up:
                                current_action = "CURSOR HOVER"
                                action_color = [0, 255, 255] # Cyan
                                if config["gestures_enabled"].get("hover", True):
                                    pyautogui.moveTo(int(curr_x), int(curr_y))
                                prev_x, prev_y = curr_x, curr_y
                                
                            # Open hand / Any other state
                            else:
                                current_action = "POINTER STOP (HAND OPEN)"
                                action_color = [100, 255, 255] # Light Cyan
                                pass
                else:
                    # Hands are tracked visually, but actual mouse triggers are bypassed
                    vol_clutch_active = False
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    
                    if config["modalities"]["voice_commands"]:
                        current_action = "VOICE ENGINE STANDBY"
                        action_color = [157, 78, 221] # Violet glow
                    else:
                        current_action = "SYSTEM STANDBY"
                        action_color = [100, 100, 100] # Grey glow
                                
        # Calculate local FPS
        curr_time = time.time()
        fps = int(1 / (curr_time - prev_time)) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        # Update shared telemetry dictionary
        with telemetry_lock:
            telemetry["fps"] = fps
            telemetry["current_action"] = current_action
            telemetry["action_color"] = action_color
            telemetry["cursor"] = {"x": int(prev_x), "y": int(prev_y)}
            telemetry["desktop_active"] = desktop_active
            telemetry["landmarks"] = normalized_lms
            
        # Draw on local window if enabled
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
            # If window was open but turned off, close it safely
            try:
                if cv2.getWindowProperty("Nexus Gesture Engine - Tracking Monitor", cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyAllWindows()
            except:
                pass
                
        # Small sleep to yield thread without causing latency
        time.sleep(0.001)

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
