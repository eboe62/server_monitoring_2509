import os
import re
import json

ADR_DIR = 'docs/decisiones/'
adrs = sorted([f for f in os.listdir(ADR_DIR) if f.startswith('ADR-') and f.endswith('.md')])

audit_data = []

for adr_file in adrs:
    path = os.path.join(ADR_DIR, adr_file)
    with open(path, 'r', encoding='utf-8') as f:
        # Read first 40 lines to capture headers and context start
        lines = [f.readline().strip() for _ in range(40)]
    
    headers = {}
    content_preview = ""
    in_headers = True
    
    for line in lines:
        if line.startswith('---'):
            in_headers = False
            continue
        
        if in_headers:
            match = re.match(r'^([^:#]+):\s*(.*)', line)
            if match:
                headers[match.group(1).strip()] = match.group(2).strip()
        else:
            content_preview += line + "\n"

    audit_data.append({
        "file": adr_file,
        "headers": headers,
        "first_line": lines[0] if lines else ""
    })

print(json.dumps(audit_data, indent=2))
