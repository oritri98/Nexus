import re

content = open('original_index.html', encoding='utf-16').read()
blocks = re.findall(r'<div class="showcase-header">\s*<h3>(.*?)</h3>.*?<div class="split-visuals">(.*?)</div>\s*</div>\s*</div>', content, re.DOTALL)
for b in blocks:
    print(b[0])
    print(b[1])
    print("---")
