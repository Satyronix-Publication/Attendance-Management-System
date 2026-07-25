import os
import glob

replacements = {
    '#1a1a2e': '#0f0a1e',
    '#16213e': '#1e1040',
    '#0f3460': '#2d1b60',
    '#e94560': '#8b5cf6'
}

files = glob.glob('*.py')
for f in files:
    if f == 'database.py' or f == 'theme_updater.py':
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated colors in {f}")

print("Done replacing themes.")
