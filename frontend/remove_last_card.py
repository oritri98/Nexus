import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the HTML starting from the second flow-arrow to the end of flow-step
# Let's find the exact block to remove.
block_to_remove = """
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
                                </div>"""

content = content.replace(block_to_remove, "")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
