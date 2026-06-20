import re

content = open('frontend/style.css', encoding='utf-8').read()
classes = re.findall(r'\.([a-zA-Z0-9_-]+)', content)
relevant = sorted(list(set(c for c in classes if 'loop' in c or 'hand' in c or 'fist' in c or 'peace' in c or 'hover' in c or 'thumb' in c)))
print("\n".join(relevant))
