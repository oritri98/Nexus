import re

css_file = 'style.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_css_additions = """
/* Flowchart Layout for Two-Handed Gestures */
.flowchart-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    padding: 20px 0;
}

.flow-step {
    flex: 1;
    display: flex;
    justify-content: center;
}

.flow-column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.flow-card {
    width: 100%;
}

.flow-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
}

.flow-arrow svg {
    width: 100%;
    height: 100%;
}
"""

with open(css_file, 'a', encoding='utf-8') as f:
    f.write(new_css_additions)
