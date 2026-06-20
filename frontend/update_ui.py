import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# The replacement HTML string
new_html = """                <div class="armory-segments">
                    <div class="armory-top-row">
                        <!-- Left Segment -->
                        <div class="armory-segment">
                            <h3 class="segment-title">Left Hand Gestures (System Controls)</h3>
                            <div class="segment-grid">
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with your left hand for more than 0.6 seconds to show the desktop.</div>
                                    <div class="showcase-header"><h3>Minimize Windows (Boss Key)</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-fist"><div class="fist-shape"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-boss"><div class="mock-windows"><div class="win window-1"></div><div class="win window-2"></div></div><div class="mock-desktop"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Show an open palm with your left hand for more than 0.6 seconds to restore the windows.</div>
                                    <div class="showcase-header"><h3>Maximize Windows</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-pinky"><div class="hand-shape-pinky" style="animation: none; transform: none;"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-boss" style="animation-direction: reverse;"><div class="mock-windows"><div class="win window-1"></div><div class="win window-2"></div></div><div class="mock-desktop"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a "phone" gesture with your left hand (only thumb and pinky up). It saves screenshots to a screenshots directory.</div>
                                    <div class="showcase-header"><h3>Take a Screenshot</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-spiderman"><div class="spiderman-hand"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-flash"><div class="mock-flash"></div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" stroke-width="1.5" style="width: 24px; height: 24px; position: absolute; z-index: 1;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" /></svg></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with your left thumb pointing straight up.</div>
                                    <div class="showcase-header"><h3>Volume Up</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-pinky"><div class="hand-shape-pinky" style="transform: rotate(0); animation: none; border-radius: 8px 8px 14px 14px;"><div style="position:absolute;top:-10px;left:5px;width:6px;height:12px;background:var(--accent-yellow);border-radius:2px;"></div></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-vol"><div class="vol-slider-mock"><div class="vol-fill" style="width: 80%; animation: none;"></div></div><span class="vol-label" style="animation: none; color: var(--accent-yellow);">VOL: UP</span></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with your left thumb pointing straight down.</div>
                                    <div class="showcase-header"><h3>Volume Down</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-pinky"><div class="hand-shape-pinky" style="transform: rotate(180deg); animation: none; border-radius: 8px 8px 14px 14px;"><div style="position:absolute;top:-10px;left:5px;width:6px;height:12px;background:var(--accent-yellow);border-radius:2px;"></div></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-vol"><div class="vol-slider-mock"><div class="vol-fill" style="width: 20%; animation: none;"></div></div><span class="vol-label" style="animation: none; color: var(--accent-yellow);">VOL: DOWN</span></div></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Right Segment -->
                        <div class="armory-segment">
                            <h3 class="segment-title">Right Hand Gestures (Primary Mouse Controls)</h3>
                            <div class="segment-grid">
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Hold your right index finger up. The cursor will follow your finger's movement.</div>
                                    <div class="showcase-header"><h3>Move Cursor</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-hover"><div class="hover-finger"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-cursor"><div class="mock-cursor"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Pinch your right index finger and thumb together.</div>
                                    <div class="showcase-header"><h3>Left Click</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch"><div class="hand-shape"></div><div class="pinch-dot"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-click"><div class="mock-cursor"></div><div class="mock-file"></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Hold only your right pinky finger up (all other fingers closed).</div>
                                    <div class="showcase-header"><h3>Right Click</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch-middle"><div class="hand-shape-middle"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-menu"><div class="mock-menu"><div class="menu-line"></div><div class="menu-line"></div></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Pinch your right pinky and thumb together. This holds the mouse button down, allowing you to drag items by moving your hand. Releasing the pinch releases the drag.</div>
                                    <div class="showcase-header"><h3>Click and Drag</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-pinch"><div class="hand-shape" style="border-radius: 50% 10% 50% 50%;"></div><div class="pinch-dot"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-click"><div class="mock-cursor"></div><div class="mock-file" style="animation: none; border-color: var(--accent-cyan); background: rgba(0, 229, 255, 0.08); transform: scale(1);"></div></div></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bottom Row -->
                    <div class="armory-bottom-row">
                        <div class="armory-segment">
                            <h3 class="segment-title">Two-Handed Gestures (Scroll Mode)</h3>
                            <div class="segment-grid four-cols">
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Hold both hands up with open palms for more than 1 second.</div>
                                    <div class="showcase-header"><h3>Enter Scroll Mode</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HANDS</span><div class="visual-placeholder loop-pinch-ring"><div class="hand-shape-ring" style="animation:none; transform:none; display:flex; gap:10px;"><div class="hand-shape-pinky" style="width:20px;height:20px;border-radius:2px;"></div><div class="hand-shape-pinky" style="width:20px;height:20px;border-radius:2px;"></div></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder"><span style="color:var(--accent-cyan); font-weight:bold; font-size:12px;">SCROLL MODE ON</span></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">While in scroll mode, hold your right index finger up.</div>
                                    <div class="showcase-header"><h3>Scroll Up</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-hover"><div class="hover-finger"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-scroll"><div class="mock-webpage"><div class="web-line line-1" style="animation-direction:reverse;"></div><div class="web-line line-2" style="animation-direction:reverse;"></div><div class="web-line line-3" style="animation-direction:reverse;"></div></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">While in scroll mode, hold both your right index and middle fingers up.</div>
                                    <div class="showcase-header"><h3>Scroll Down</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-peace"><div class="peace-fingers"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-scroll"><div class="mock-webpage"><div class="web-line line-1"></div><div class="web-line line-2"></div><div class="web-line line-3"></div></div></div></div>
                                    </div>
                                </div>
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Make a closed fist with both hands for more than 1 second.</div>
                                    <div class="showcase-header"><h3>Exit Scroll Mode</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HANDS</span><div class="visual-placeholder loop-fist"><div class="fist-shape" style="animation:none; width:15px; height:15px; margin-right:5px;"></div><div class="fist-shape" style="animation:none; width:15px; height:15px;"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder"><span style="color:var(--text-muted); font-weight:bold; font-size:12px;">SCROLL MODE OFF</span></div></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""

# Find the block from <div class="showcase-grid"> to just before <div class="navigation-footer">
# Use re.DOTALL to match across newlines
pattern = re.compile(r'<div class="showcase-grid">.*?(?=<div class="navigation-footer">)', re.DOTALL)
new_content = pattern.sub(new_html + '\n\n                ', content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
