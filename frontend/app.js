/* =====================================================================
   Nexus CLIENT CONTROLLER - 5-PAGE SPA NAVIGATION & TELEMETRY
   ===================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------------
    // 1. PAGE ROUTER & NAVIGATION
    // -----------------------------------------------------------------
    const pages = document.querySelectorAll('.page-view');

    function navigateToPage(pageId) {
        console.log(`[ROUTER] Navigating to page: ${pageId}`);

        pages.forEach(page => {
            page.classList.remove('active-page');
        });

        const targetPage = document.getElementById(`page-${pageId}`);
        if (targetPage) {
            // Apply visual delay for fade transition
            targetPage.classList.add('active-page');

            // Trigger specific actions when entering certain pages
            if (pageId === 'hub') {
                connectWebSocket();
            } else if (pageId !== 'hub') {
                // If leaving the hub, ensure we release camera cleanly
                disconnectWebSocket();
            }
        }
    }

    // Page 1 -> Page 2 (with Welcome transition)
    const btnTryYourself = document.getElementById('btn-try-yourself');
    const robotHandImg = document.getElementById('robot-hand-img');

    function triggerWelcomeSequence() {
        // Change button text and style
        const btnText = btnTryYourself.querySelector('.btn-text');
        btnText.textContent = "WELCOME...";
        btnTryYourself.style.background = 'rgba(0, 229, 255, 0.2)';
        btnTryYourself.style.boxShadow = '0 0 20px var(--accent-cyan)';

        // Add a bright flash to the robot hand
        if (robotHandImg) {
            robotHandImg.style.filter = 'drop-shadow(0 0 40px rgba(0, 255, 100, 1)) drop-shadow(0 0 80px rgba(0, 255, 100, 0.8)) brightness(2) contrast(1.5)';
            robotHandImg.style.transform = 'scale(1.1)';
        }

        // Wait a short moment then navigate
        setTimeout(() => {
            // Reset styles for if they return to this page
            btnText.textContent = "TRY IT YOURSELF";
            btnTryYourself.style.background = '';
            btnTryYourself.style.boxShadow = '';
            if (robotHandImg) {
                robotHandImg.style.filter = '';
                robotHandImg.style.transform = '';
            }
            navigateToPage('armory');
        }, 1200);
    }

    btnTryYourself.addEventListener('click', triggerWelcomeSequence);
    if (robotHandImg) {
        robotHandImg.addEventListener('click', triggerWelcomeSequence);
    }

    // Page 2 -> Page 3
    document.getElementById('btn-goto-login').addEventListener('click', () => {
        navigateToPage('login');
    });

    // Page 2 interactive showcase card click description bubble logic
    const showcaseCards = document.querySelectorAll('.showcase-card');
    showcaseCards.forEach(card => {
        card.addEventListener('click', (e) => {
            const isActive = card.classList.contains('active-desc');
            // Close other descriptions for cleaner UX
            showcaseCards.forEach(c => c.classList.remove('active-desc'));
            if (!isActive) {
                card.classList.add('active-desc');
            }
            e.stopPropagation();
        });
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.showcase-card')) {
            showcaseCards.forEach(c => c.classList.remove('active-desc'));
        }
    });

    // Page 4 -> Page 5
    document.getElementById('btn-goto-credits').addEventListener('click', () => {
        navigateToPage('credits');
    });

    // Page 5 -> Page 1
    document.getElementById('btn-return-home').addEventListener('click', () => {
        navigateToPage('landing');
    });

    // -----------------------------------------------------------------
    // 2. BIOMETRIC ACCESS TERMINAL (LOGIN)
    // -----------------------------------------------------------------
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error-msg');
    const loginLaser = document.getElementById('login-laser');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.classList.add('hidden');

        const name = document.getElementById('user-name').value.trim();
        const email = document.getElementById('user-email').value.trim().toLowerCase();
        const password = document.getElementById('user-password').value;

        // --- CLIENT-SIDE VALIDATION ---
        if (name.length < 2) {
            loginError.textContent = 'OPERATOR NAME MUST BE AT LEAST 2 CHARACTERS.';
            loginError.classList.remove('hidden');
            return;
        }

        // Gmail-only validation
        const gmailRegex = /^[a-zA-Z0-9]([a-zA-Z0-9.]*[a-zA-Z0-9])?@gmail\.com$/;
        if (!gmailRegex.test(email)) {
            loginError.textContent = 'INVALID CHANNEL. ONLY @GMAIL.COM ADDRESSES ACCEPTED.';
            loginError.classList.remove('hidden');
            loginLaser.style.background = 'var(--accent-red)';
            loginLaser.style.boxShadow = '0 0 10px var(--accent-red), 0 0 20px var(--accent-red)';
            setTimeout(() => {
                loginLaser.style.background = 'var(--accent-cyan)';
                loginLaser.style.boxShadow = '0 0 10px var(--accent-cyan), 0 0 20px var(--accent-cyan)';
            }, 2000);
            return;
        }

        if (password.length < 6) {
            loginError.textContent = 'ACCESS KEY MUST BE AT LEAST 6 CHARACTERS.';
            loginError.classList.remove('hidden');
            return;
        }

        // Speed up laser scan styling during check
        loginLaser.style.animationDuration = '0.8s';
        loginLaser.style.background = 'var(--accent-green)';
        loginLaser.style.boxShadow = '0 0 10px var(--accent-green), 0 0 20px var(--accent-green)';

        try {
            console.log(`[DATABASE] Authenticating operator: ${name} (${email})`);
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const result = await response.json();

            if (response.ok) {
                console.log(`[DATABASE] ${result.mode === 'login' ? 'Returning operator authenticated.' : 'New operator registered.'}`);

                // Keep scanner glowing green for success feedback
                setTimeout(() => {
                    // Reset laser style
                    loginLaser.style.animationDuration = '4s';
                    loginLaser.style.background = 'var(--accent-cyan)';
                    loginLaser.style.boxShadow = '0 0 10px var(--accent-cyan), 0 0 20px var(--accent-cyan)';

                    // Navigate to dashboard
                    navigateToPage('hub');
                }, 1200);
            } else {
                // Show specific error from server
                const errorMessages = {
                    'INVALID_NAME': 'OPERATOR NAME MUST BE AT LEAST 2 CHARACTERS.',
                    'INVALID_EMAIL': 'INVALID CHANNEL. ONLY @GMAIL.COM ADDRESSES ACCEPTED.',
                    'WEAK_PASSWORD': 'ACCESS KEY MUST BE AT LEAST 6 CHARACTERS.',
                    'WRONG_PASSWORD': 'INCORRECT ACCESS KEY FOR THIS EMAIL.',
                    'DB_ERROR': 'SYSTEM DATABASE ERROR. RETRY AUTHENTICATION.'
                };
                const errorCode = result.code || '';
                loginError.textContent = errorMessages[errorCode] || 'AUTHENTICATION FAILED. VERIFY CREDENTIALS.';
                throw new Error(result.message || "Authentication failed");
            }
        } catch (err) {
            console.error('[DATABASE ERROR] Access Denied:', err.message);
            loginLaser.style.background = 'var(--accent-red)';
            loginLaser.style.boxShadow = '0 0 10px var(--accent-red), 0 0 20px var(--accent-red)';
            loginError.classList.remove('hidden');

            setTimeout(() => {
                loginLaser.style.animationDuration = '4s';
                loginLaser.style.background = 'var(--accent-cyan)';
                loginLaser.style.boxShadow = '0 0 10px var(--accent-cyan), 0 0 20px var(--accent-cyan)';
            }, 2000);
        }
    });

    // -----------------------------------------------------------------
    // 3. WEBSOCKET NETWORKING & TELEMETRY
    // -----------------------------------------------------------------
    const connBadge = document.getElementById('connection-status');
    const engBadge = document.getElementById('engine-status');
    const actionDisplay = document.getElementById('current-action-display');
    const coordsDisplay = document.getElementById('coordinates-display');
    const resDisplay = document.getElementById('resolution-display');
    const fpsDisplay = document.getElementById('fps-display');
    const warningOverlay = document.getElementById('no-hand-warning');

    // Hub controls
    const smoothSlider = document.getElementById('smooth-slider');
    const smoothVal = document.getElementById('smooth-val');
    const blinkSlider = document.getElementById('blink-slider');
    const blinkVal = document.getElementById('blink-val');
    const opencvToggle = document.getElementById('opencv-toggle');
    const cameraIndexInput = document.getElementById('camera-index-input');
    const toggleModalityGestures = document.getElementById('toggle-modality-gestures');
    const toggleModalityFace = document.getElementById('toggle-modality-face');
    const toggleModalityVoice = document.getElementById('toggle-modality-voice');
    const btnShutdown = document.getElementById('btn-shutdown-system');

    // SVG Canvas elements
    const svgCanvas = document.getElementById('hand-canvas');
    const linksGroup = document.getElementById('skeleton-links');
    const jointsGroup = document.getElementById('skeleton-joints');
    const virtualCursor = document.getElementById('virtual-cursor');
    const virtualCursorCore = document.getElementById('virtual-cursor-core');

    let socket = null;
    let reconnectTimeout = null;
    let engineActiveState = true; // Tracks local engine shut down status

    // Setup skeleton structures
    const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],       // Thumb
        [0, 5], [5, 6], [6, 7], [7, 8],       // Index
        [5, 9], [9, 10], [10, 11], [11, 12],   // Middle
        [9, 13], [13, 14], [14, 15], [15, 16], // Ring
        [13, 17], [17, 18], [18, 19], [19, 20], // Pinky
        [0, 17], [5, 17]                       // Palm Close
    ];

    const joints = [];
    const links = [];

    // Pre-create SVG Elements for up to 2 hands (42 landmarks, 44 links)
    for (let i = 0; i < 42; i++) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', '1.0');
        circle.setAttribute('cx', '50');
        circle.setAttribute('cy', '50');
        circle.setAttribute('class', 'hand-joint');
        if ([4, 8, 12, 16, 20, 25, 29, 33, 37, 41].includes(i)) {
            circle.classList.add('hand-joint-tip');
            circle.setAttribute('r', '1.3');
        }
        jointsGroup.appendChild(circle);
        joints.push(circle);
    }

    const allConnections = [];
    connections.forEach(([from, to]) => allConnections.push([from, to]));
    connections.forEach(([from, to]) => allConnections.push([from + 21, to + 21]));

    allConnections.forEach(([from, to]) => {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', '50');
        line.setAttribute('y1', '50');
        line.setAttribute('x2', '50');
        line.setAttribute('y2', '50');
        line.setAttribute('class', 'hand-link');
        // base hand indices
        const bFrom = from % 21;
        const bTo = to % 21;
        if ([0, 5, 9, 13, 17].includes(bFrom) && [1, 5, 9, 13, 17].includes(bTo)) {
            line.classList.add('hand-link-bone');
        }
        linksGroup.appendChild(line);
        links.push({ line, from, to });
    });

    function setSkeletonVisibility(visible) {
        const opacityVal = visible ? '1' : '0';
        jointsGroup.setAttribute('opacity', opacityVal);
        linksGroup.setAttribute('opacity', opacityVal);
        virtualCursor.setAttribute('opacity', opacityVal);
        virtualCursorCore.setAttribute('opacity', opacityVal);
    }

    function connectWebSocket() {
        if (socket && socket.readyState === WebSocket.OPEN) return;

        // Ensure engine is active locally
        engineActiveState = true;
        btnShutdown.textContent = "TERMINATE ENGINE";
        btnShutdown.className = "cyber-btn secondary-btn";

        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${wsScheme}://${window.location.host}/ws`;

        console.log(`[NETWORKING] Initializing WebSocket Client: ${wsUrl}`);
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log('[NETWORKING] Connected to Nexus engine server.');
            connBadge.textContent = 'CONNECTED';
            connBadge.className = 'status-badge connected';
            engBadge.textContent = 'ACTIVE';
            engBadge.className = 'status-badge active';

            // Sync settings immediately upon connection
            sendSettingsUpdate();
        };

        socket.onmessage = (event) => {
            const telemetryData = JSON.parse(event.data);
            updateTelemetryUI(telemetryData);
        };

        socket.onclose = () => {
            console.warn('[NETWORKING] Telemetry socket closed.');
            connBadge.textContent = 'DISCONNECTED';
            connBadge.className = 'status-badge disconnected';
            engBadge.textContent = 'INACTIVE';
            engBadge.className = 'status-badge inactive';
            warningOverlay.classList.remove('hidden');
            setSkeletonVisibility(false);

            // Reconnect if local engine shutdown wasn't triggered
            if (engineActiveState) {
                clearTimeout(reconnectTimeout);
                reconnectTimeout = setTimeout(connectWebSocket, 3000);
            }
        };

        socket.onerror = (err) => {
            console.error('[NETWORKING] WebSocket error: ', err);
            socket.close();
        };
    }

    function disconnectWebSocket() {
        engineActiveState = false;
        clearTimeout(reconnectTimeout);
        if (socket) {
            socket.close();
            socket = null;
        }
    }

    // -----------------------------------------------------------------
    // 4. TELEMETRY WRITER
    // -----------------------------------------------------------------
    function updateTelemetryUI(data) {
        // Update FPS & Action Text
        fpsDisplay.textContent = String(data.fps).padStart(2, '0');
        actionDisplay.textContent = data.current_action;

        // Coordinates and bounds
        const cursorX = String(data.cursor.x).padStart(4, '0');
        const cursorY = String(data.cursor.y).padStart(4, '0');
        coordsDisplay.textContent = `X: ${cursorX} | Y: ${cursorY}`;
        resDisplay.textContent = `${data.screen_size.width} x ${data.screen_size.height}`;

        // Title color highlights
        const rgbColor = `rgb(${data.action_color.join(',')})`;
        actionDisplay.style.color = rgbColor;
        actionDisplay.style.textShadow = `0 0 10px rgba(${data.action_color.join(',')}, 0.5)`;

        // Draw hand landmarks
        const lms = data.landmarks;
        if (lms && lms.length >= 21 && toggleModalityGestures.checked) {
            warningOverlay.classList.add('hidden');
            setSkeletonVisibility(true);

            const numHands = Math.floor(lms.length / 21);

            joints.forEach((circle, index) => {
                if (index < numHands * 21) {
                    circle.setAttribute('opacity', '1');
                    const cx = (lms[index].x * 100).toFixed(2);
                    const cy = (lms[index].y * 100).toFixed(2);
                    circle.setAttribute('cx', cx);
                    circle.setAttribute('cy', cy);
                } else {
                    circle.setAttribute('opacity', '0');
                }
            });

            links.forEach((linkObj, index) => {
                if (index < numHands * 22) {
                    linkObj.line.setAttribute('opacity', '1');
                    const x1 = (lms[linkObj.from].x * 100).toFixed(2);
                    const y1 = (lms[linkObj.from].y * 100).toFixed(2);
                    const x2 = (lms[linkObj.to].x * 100).toFixed(2);
                    const y2 = (lms[linkObj.to].y * 100).toFixed(2);
                    linkObj.line.setAttribute('x1', x1);
                    linkObj.line.setAttribute('y1', y1);
                    linkObj.line.setAttribute('x2', x2);
                    linkObj.line.setAttribute('y2', y2);
                } else {
                    linkObj.line.setAttribute('opacity', '0');
                }
            });

            // Draw Virtual Cursor
            const idxTip = lms[8];
            const vCursorX = (idxTip.x * 100).toFixed(2);
            const vCursorY = (idxTip.y * 100).toFixed(2);
            virtualCursor.setAttribute('cx', vCursorX);
            virtualCursor.setAttribute('cy', vCursorY);
            virtualCursorCore.setAttribute('cx', vCursorX);
            virtualCursorCore.setAttribute('cy', vCursorY);
        } else {
            warningOverlay.classList.remove('hidden');
            setSkeletonVisibility(false);

            if (!toggleModalityGestures.checked) {
                warningOverlay.querySelector('span').textContent = "HAND GESTURE TRACKING DISABLED";
            } else {
                warningOverlay.querySelector('span').textContent = "NO HAND DETECTED IN ACTIVE REGION";
            }
        }

        // Highlight active matrix item
        const activeAction = data.current_action;
        const gestureItems = document.querySelectorAll('.matrix-item');

        gestureItems.forEach(item => {
            let itemAction = item.getAttribute('data-gesture');

            // Reset state highlighting, leaving the base class intact
            item.classList.remove('active-state', 'active-state-green', 'active-state-red', 'active-state-orange', 'active-state-purple', 'active-state-yellow', 'active-flash');

            if (activeAction === itemAction && (toggleModalityGestures.checked || toggleModalityFace.checked)) {
                if (itemAction === 'CURSOR HOVER' || itemAction === 'FACE CURSOR') {
                    item.classList.add('active-state');
                } else if (itemAction === 'LEFT CLICK' || itemAction === 'DRAG ENGAGED' || itemAction === 'LEFT CLICK (FACE)') {
                    item.classList.add('active-state-green');
                } else if (itemAction === 'RIGHT CLICK' || itemAction === 'RIGHT CLICK (FACE)') {
                    item.classList.add('active-state-orange');
                } else if (itemAction === 'MINIMIZE WINDOWS' || itemAction === 'MAXIMIZE WINDOWS') {
                    item.classList.add('active-state-purple');
                } else if (itemAction === 'SCREENSHOT') {
                    item.classList.add('active-flash');
                } else if (itemAction === 'VOLUME UP' || itemAction === 'VOLUME DOWN') {
                    item.classList.add('active-state-yellow');
                } else if (itemAction === 'ENTER SCROLL MODE' || itemAction === 'SCROLL UP' || itemAction === 'SCROLL DOWN' || itemAction === 'EXIT SCROLL MODE') {
                    item.classList.add('active-state-red');
                }
            }
        });
    }

    // -----------------------------------------------------------------
    // 5. SETTINGS CHANGE BROADCASTER
    // -----------------------------------------------------------------
    function sendSettingsUpdate() {
        if (!socket || socket.readyState !== WebSocket.OPEN) return;

        const smoothValFloat = parseFloat(smoothSlider.value);
        const blinkValFloat = parseFloat(blinkSlider.value);
        const showOpencv = opencvToggle.checked;

        // Modalities status
        const modalities = {
            hand_gestures: toggleModalityGestures.checked,
            face_tracking: toggleModalityFace.checked,
            voice_commands: toggleModalityVoice.checked
        };

        const gesturesEnabled = {
            hover: document.getElementById('toggle-hover').checked,
            left_click: document.getElementById('toggle-left_click').checked,
            right_click: document.getElementById('toggle-right_click').checked,
            click_drag: document.getElementById('toggle-click_drag').checked,
            minimize: document.getElementById('toggle-minimize').checked,
            maximize: document.getElementById('toggle-maximize').checked,
            screenshot: document.getElementById('toggle-screenshot').checked,
            volume_up: document.getElementById('toggle-volume_up').checked,
            volume_down: document.getElementById('toggle-volume_down').checked,
            enter_scroll: document.getElementById('toggle-enter_scroll').checked,
            scroll_up: document.getElementById('toggle-scroll_up').checked,
            scroll_down: document.getElementById('toggle-scroll_down').checked,
            exit_scroll: document.getElementById('toggle-exit_scroll').checked
        };

        const payload = {
            type: 'update_settings',
            settings: {
                engine_active: engineActiveState,
                smooth_closeness: smoothValFloat,
                blink_threshold: blinkValFloat,
                show_opencv_window: showOpencv,
                camera_index: parseInt(cameraIndexInput.value) || 0,
                modalities: modalities,
                gestures_enabled: gesturesEnabled
            }
        };
        socket.send(JSON.stringify(payload));
    }

    // Settings Slider listeners
    smoothSlider.addEventListener('input', () => {
        smoothVal.textContent = parseFloat(smoothSlider.value).toFixed(1);
    });

    blinkSlider.addEventListener('input', () => {
        blinkVal.textContent = parseFloat(blinkSlider.value).toFixed(2);
    });

    smoothSlider.addEventListener('change', sendSettingsUpdate);
    blinkSlider.addEventListener('change', sendSettingsUpdate);
    opencvToggle.addEventListener('change', sendSettingsUpdate);
    cameraIndexInput.addEventListener('change', sendSettingsUpdate);
    toggleModalityGestures.addEventListener('change', () => {
        sendSettingsUpdate();
        if (toggleModalityGestures.checked && !engineActiveState) {
            // Re-engage engine if user checks gestures back on
            connectWebSocket();
        }
    });
    toggleModalityFace.addEventListener('change', sendSettingsUpdate);
    toggleModalityVoice.addEventListener('change', () => {
        if (toggleModalityVoice.checked) {
            // Voice Control ON -> Disable others
            toggleModalityGestures.checked = false;
            toggleModalityFace.checked = false;
            toggleModalityGestures.disabled = true;
            toggleModalityFace.disabled = true;
            toggleModalityGestures.parentElement.style.opacity = '0.5';
            toggleModalityFace.parentElement.style.opacity = '0.5';
        } else {
            // Voice Control OFF -> Enable others
            toggleModalityGestures.disabled = false;
            toggleModalityFace.disabled = false;
            toggleModalityGestures.parentElement.style.opacity = '1.0';
            toggleModalityFace.parentElement.style.opacity = '1.0';
        }
        sendSettingsUpdate();
    });

    // Dynamic gesture toggles
    const toggles = [
        'toggle-hover', 'toggle-click', 'toggle-right_click',
        'toggle-scroll', 'toggle-youtube', 'toggle-volume', 'toggle-boss_key', 'toggle-screenshot'
    ];

    toggles.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', sendSettingsUpdate);
        }
    });

    // -----------------------------------------------------------------
    // 6. ENGINE SHUTDOWN ENGINE
    // -----------------------------------------------------------------
    btnShutdown.addEventListener('click', () => {
        if (engineActiveState) {
            // Terminating
            console.log('[SYSTEM] Dispatching engine termination signal.');
            engineActiveState = false;

            // Send engine_active: false settings payload before disconnecting
            if (socket && socket.readyState === WebSocket.OPEN) {
                const payload = {
                    type: 'update_settings',
                    settings: {
                        engine_active: false
                    }
                };
                socket.send(JSON.stringify(payload));

                // Wait briefly for server transmission before closing local socket
                setTimeout(() => {
                    if (socket) socket.close();
                }, 200);
            }

            // Adjust shutdown button state
            btnShutdown.textContent = "ENGAGE CAMERA ENGINE";
            btnShutdown.className = "cyber-btn primary-btn";

            // Update labels
            fpsDisplay.textContent = "00";
            actionDisplay.textContent = "ENGINE TERMINATED";
            actionDisplay.style.color = "var(--accent-red)";
            actionDisplay.style.textShadow = "0 0 10px rgba(255, 51, 102, 0.5)";
            coordsDisplay.textContent = "X: 0000 | Y: 0000";

            connBadge.textContent = 'DISCONNECTED';
            connBadge.className = 'status-badge disconnected';
            engBadge.textContent = 'INACTIVE';
            engBadge.className = 'status-badge inactive';

            warningOverlay.classList.remove('hidden');
            warningOverlay.querySelector('span').textContent = "CAMERA ENGINE TERMINATED";
            setSkeletonVisibility(false);
        } else {
            // Re-engaging
            console.log('[SYSTEM] Engaging camera tracking engine...');
            connectWebSocket();
        }
    });
});
