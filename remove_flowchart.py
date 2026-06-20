import re

html_file = 'frontend/index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the flowchart back with the standard grid, keeping the correct gesture classes
new_bottom = """                    <!-- Bottom Row -->
                    <div class="armory-bottom-row">
                        <div class="armory-segment">
                            <h3 class="segment-title">Two-Handed Gestures (Scroll Mode)</h3>
                            <div class="segment-grid four-cols">
                                <div class="showcase-card glass-panel">
                                    <div class="card-desc-bubble">Hold both hands up with open palms for more than 1 second.</div>
                                    <div class="showcase-header"><h3>Enter Scroll Mode</h3></div>
                                    <div class="split-visuals">
                                        <div class="visual-pane hand-pane"><span class="pane-label">HANDS</span><div class="visual-placeholder" style="display:flex;gap:10px;"><div class="palm-shape" style="transform:scale(0.8);"><div class="palm-shape-inner"></div><div class="palm-shape-thumb" style="transform:scaleX(-1);"></div></div><div class="palm-shape" style="transform:scale(0.8);"><div class="palm-shape-inner"></div><div class="palm-shape-thumb"></div></div></div></div>
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
                                        <div class="visual-pane hand-pane"><span class="pane-label">HANDS</span><div class="visual-placeholder loop-fist" style="display:flex;gap:5px;animation:none;"><div class="fist-shape" style="animation:none; width:15px; height:15px;"></div><div class="fist-shape" style="animation:none; width:15px; height:15px;"></div></div></div>
                                        <div class="visual-pane screen-pane"><span class="pane-label">SCREEN</span><div class="visual-placeholder"><span style="color:var(--text-muted); font-weight:bold; font-size:12px;">SCROLL MODE OFF</span></div></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>"""

pattern = re.compile(r'<!-- Bottom Row -->\s*<div class="armory-bottom-row flowchart-container">.*?</div>\s*</div>\s*</div>\s*</div>', re.DOTALL)
new_content = pattern.sub(new_bottom, content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
