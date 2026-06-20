import re

css_file = 'frontend/style.css'
with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_css = """
/* CUSTOM HAND SHAPES FOR NEW GESTURES */

/* Open Palm */
.palm-shape {
    width: 30px; height: 35px;
    background: transparent;
    border: 2px solid var(--text-muted);
    border-radius: 6px;
    position: relative;
    animation: palmShapeLoop 2.5s infinite ease-in-out;
}
.palm-shape::before, .palm-shape::after {
    content: '';
    position: absolute;
    width: 6px; height: 18px;
    border: 2px solid var(--text-muted);
    border-radius: 4px;
    top: -15px;
}
.palm-shape::before { left: 4px; }
.palm-shape::after { right: 4px; }
.palm-shape-inner {
    position: absolute;
    width: 6px; height: 20px;
    border: 2px solid var(--text-muted);
    border-radius: 4px;
    top: -20px; left: 14px;
}
.palm-shape-thumb {
    position: absolute;
    width: 14px; height: 6px;
    border: 2px solid var(--text-muted);
    border-radius: 4px;
    top: 10px; left: -12px;
}
@keyframes palmShapeLoop {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05) translateY(-2px); }
}

/* Thumbs Up & Down */
.thumb-up-shape {
    width: 25px; height: 25px;
    background: transparent;
    border: 3px solid var(--text-muted);
    border-radius: 6px 6px 10px 10px;
    position: relative;
    animation: thumbUpLoop 2s infinite ease-in-out;
}
.thumb-up-shape::after {
    content: '';
    position: absolute;
    width: 10px; height: 18px;
    border: 3px solid var(--text-muted);
    border-radius: 5px;
    top: -18px; left: 0px;
}
@keyframes thumbUpLoop {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

.thumb-down-shape {
    width: 25px; height: 25px;
    background: transparent;
    border: 3px solid var(--text-muted);
    border-radius: 10px 10px 6px 6px;
    position: relative;
    animation: thumbDownLoop 2s infinite ease-in-out;
}
.thumb-down-shape::after {
    content: '';
    position: absolute;
    width: 10px; height: 18px;
    border: 3px solid var(--text-muted);
    border-radius: 5px;
    bottom: -18px; left: 0px;
}
@keyframes thumbDownLoop {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}

/* Vol Down slider hack */
.loop-vol-down .vol-fill {
    animation: volDownLoop 2s infinite ease-in-out;
}
@keyframes volDownLoop {
    0%, 100% { height: 100%; opacity: 1; }
    50% { height: 10%; opacity: 0.5; }
}

/* Pinky Drag */
.loop-drag-pinky .hand-shape-pinky {
    animation: pinkyDragMove 3s infinite ease-in-out;
}
.loop-drag-pinky .pinch-dot {
    position: absolute;
    width: 6px; height: 6px;
    background: var(--accent-cyan);
    border-radius: 50%;
    right: 2px;
    top: -10px;
    animation: pinkyDragDot 3s infinite ease-in-out;
}
@keyframes pinkyDragMove {
    0%, 100% { transform: translateX(0) scale(1); }
    50% { transform: translateX(10px) scale(0.95); }
}
@keyframes pinkyDragDot {
    0%, 100% { opacity: 0; transform: scale(0.5); }
    20%, 80% { opacity: 1; transform: scale(1); }
}
"""

if "CUSTOM HAND SHAPES FOR NEW GESTURES" not in content:
    with open(css_file, 'a', encoding='utf-8') as f:
        f.write("\n" + new_css)
    print("CSS updated.")
else:
    print("CSS already updated.")
