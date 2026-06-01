import os
import json

found_400 = False
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
    
    # Check directory file counts
    if len(files) == 400:
        print(f"Directory {root} has exactly 400 files.")
        found_400 = True
    elif len(files) > 390 and len(files) < 410:
        print(f"Directory {root} has {len(files)} files.")
        
    for f in files:
        if f.endswith('.json'):
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    length = len(data) if isinstance(data, (list, dict)) else 0
                    if length == 400:
                        print(f"JSON File {os.path.join(root, f)} has 400 elements.")
                        found_400 = True
            except Exception as e:
                pass

if not found_400:
    print("No structures with exactly 400 elements found.")
