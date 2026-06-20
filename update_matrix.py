import re

html_file = 'frontend/index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_list = """                        <div class="matrix-list">
                            <!-- Right Hand Gestures -->
                            <div class="matrix-item" id="gesture-hover" data-gesture="CURSOR HOVER">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Move Cursor</h4>
                                    <p>Hold your right index finger up. The cursor will follow your finger's movement.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-hover" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-left-click" data-gesture="LEFT CLICK">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Left Click</h4>
                                    <p>Pinch your right index finger and thumb together.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-left_click" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-right-click" data-gesture="RIGHT CLICK">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Right Click</h4>
                                    <p>Hold only your right pinky finger up (all other fingers closed).</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-right_click" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-drag" data-gesture="DRAG ENGAGED">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Click and Drag</h4>
                                    <p>Pinch your right pinky and thumb together. This holds the mouse button down, allowing you to drag items by moving your hand. Releasing the pinch releases the drag.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-click_drag" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <!-- Left Hand Gestures -->
                            <div class="matrix-item" id="gesture-minimize" data-gesture="MINIMIZE WINDOWS">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Minimize Windows</h4>
                                    <p>Make a closed fist with your left hand for more than 0.6 seconds to show the desktop.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-minimize" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-maximize" data-gesture="MAXIMIZE WINDOWS">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Maximize Windows</h4>
                                    <p>Show an open palm with your left hand for more than 0.6 seconds to restore the windows.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-maximize" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-screenshot" data-gesture="SCREENSHOT">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Take a Screenshot</h4>
                                    <p>Make a "phone" gesture with your left hand (only thumb and pinky up). It saves screenshots to a screenshots directory.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-screenshot" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-vol-up" data-gesture="VOLUME UP">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Volume Up</h4>
                                    <p>Make a closed fist with your left thumb pointing straight up.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-volume_up" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-vol-down" data-gesture="VOLUME DOWN">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Volume Down</h4>
                                    <p>Make a closed fist with your left thumb pointing straight down.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-volume_down" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <!-- Two-Handed Gestures (Scroll Mode) -->
                            <div class="matrix-item" id="gesture-enter-scroll" data-gesture="ENTER SCROLL MODE">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Enter Scroll Mode</h4>
                                    <p>Hold both hands up with open palms for more than 1 second.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-enter_scroll" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-scroll-up" data-gesture="SCROLL UP">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Scroll Up</h4>
                                    <p>While in scroll mode, hold your right index finger up.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-scroll_up" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-scroll-down" data-gesture="SCROLL DOWN">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Scroll Down</h4>
                                    <p>While in scroll mode, hold both your right index and middle fingers up.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-scroll_down" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>

                            <div class="matrix-item" id="gesture-exit-scroll" data-gesture="EXIT SCROLL MODE">
                                <div class="item-status-light"></div>
                                <div class="item-details">
                                    <h4>Exit Scroll Mode</h4>
                                    <p>Make a closed fist with both hands for more than 1 second.</p>
                                </div>
                                <label class="mini-toggle">
                                    <input type="checkbox" id="toggle-exit_scroll" checked>
                                    <span class="mini-slider"></span>
                                </label>
                            </div>
                        </div>"""

pattern = re.compile(r'<div class="matrix-list">.*?</div>\s*</div>\s*<!-- Navigation footer', re.DOTALL)
new_content = pattern.sub(new_list + '\n                    </div>\n\n                <!-- Navigation footer', content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
