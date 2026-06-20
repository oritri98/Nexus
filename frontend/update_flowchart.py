import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_bottom_row = """                    <!-- Bottom Row -->
                    <div class="armory-bottom-row">
                        <div class="armory-segment">
                            <h3 class="segment-title">Two-Handed Gestures (Scroll Mode)</h3>
                            
                            <div class="flowchart-container">
                                <!-- Step 1: Enter Scroll Mode -->
                                <div class="flow-step">
                                    <div class="showcase-card glass-panel flow-card">
                                        <div class="card-desc-bubble">Hold both hands up with open palms for more than 1 second.</div>
                                        <div class="showcase-header"><h3>Enter Scroll Mode</h3></div>
                                        <div class="split-visuals">
                                            <div class="visual-pane hand-pane"><span class="pane-label">HANDS</span><div class="visual-placeholder loop-pinch-ring"><div class="hand-shape-ring" style="animation:none; transform:none; display:flex; gap:10px;"><div class="hand-shape-pinky" style="width:20px;height:20px;border-radius:2px;"></div><div class="hand-shape-pinky" style="width:20px;height:20px;border-radius:2px;"></div></div></div></div>
                                            <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder"><span style="color:var(--accent-cyan); font-weight:bold; font-size:12px;">SCROLL MODE ON</span></div></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="flow-arrow">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                                </div>

                                <!-- Step 2: Middle Actions (Up / Down) -->
                                <div class="flow-column">
                                    <div class="showcase-card glass-panel flow-card">
                                        <div class="card-desc-bubble">While in scroll mode, hold your right index finger up.</div>
                                        <div class="showcase-header"><h3>Scroll Up</h3></div>
                                        <div class="split-visuals">
                                            <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-hover"><div class="hover-finger"></div></div></div>
                                            <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-scroll"><div class="mock-webpage"><div class="web-line line-1" style="animation-direction:reverse;"></div><div class="web-line line-2" style="animation-direction:reverse;"></div><div class="web-line line-3" style="animation-direction:reverse;"></div></div></div></div>
                                        </div>
                                    </div>

                                    <div class="showcase-card glass-panel flow-card">
                                        <div class="card-desc-bubble">While in scroll mode, hold both your right index and middle fingers up.</div>
                                        <div class="showcase-header"><h3>Scroll Down</h3></div>
                                        <div class="split-visuals">
                                            <div class="visual-pane hand-pane"><span class="pane-label">HAND</span><div class="visual-placeholder loop-peace"><div class="peace-fingers"></div></div></div>
                                            <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder loop-scroll"><div class="mock-webpage"><div class="web-line line-1"></div><div class="web-line line-2"></div><div class="web-line line-3"></div></div></div></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="flow-arrow">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                                </div>

                                <!-- Step 3: Exit Scroll Mode -->
                                <div class="flow-step">
                                    <div class="showcase-card glass-panel flow-card">
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

# Using regex to replace the Bottom Row portion
pattern = re.compile(r'<!-- Bottom Row -->.*?</div>\s*</div>\s*</div>', re.DOTALL)
new_content = pattern.sub(new_bottom_row, content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
