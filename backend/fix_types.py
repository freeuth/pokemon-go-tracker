#!/usr/bin/env python3
import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Fix type hints
    content = re.sub(r': str \| None', ': Optional[str]', content)
    content = re.sub(r': int \| None', ': Optional[int]', content)
    content = re.sub(r': float \| None', ': Optional[float]', content)
    content = re.sub(r': dict \| None', ': Optional[dict]', content)
    content = re.sub(r': datetime \| None', ': Optional[datetime]', content)
    content = re.sub(r' -> Dict \| None:', ' -> Optional[Dict]:', content)

    # Add Optional import if needed
    if 'Optional[' in content and 'from typing import' in content:
        if not re.search(r'from typing import.*Optional', content):
            content = re.sub(
                r'from typing import ',
                'from typing import Optional, ',
                content,
                count=1
            )

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed: {filepath}")

# Walk through app directory
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            fix_file(filepath)

print("All files fixed!")
