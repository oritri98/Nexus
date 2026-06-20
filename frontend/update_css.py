import re

css_file = 'style.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_css = """
/* Grid layout - Updated for segments */
.armory-segments {
    display: flex;
    flex-direction: column;
    gap: 30px;
    margin-top: 15px;
}

.armory-top-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
}

.armory-segment {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(0, 229, 255, 0.1);
    border-radius: var(--border-radius-lg);
    padding: 20px;
}

.segment-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-cyan);
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 1px solid rgba(0, 229, 255, 0.2);
    padding-bottom: 10px;
    display: inline-block;
}

.segment-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.segment-grid.four-cols {
    grid-template-columns: repeat(4, 1fr);
}
"""

# Replace the .showcase-grid block with the new layout
pattern = re.compile(r'/\* Grid layout \*/\s*\.showcase-grid\s*\{[^}]*\}', re.DOTALL)
new_content = pattern.sub(new_css, content)

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
