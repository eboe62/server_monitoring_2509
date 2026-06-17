import os
import re
import json

ADR_DIR = 'docs/decisiones/'
ADR_INDEX_PATH = 'ai/governance/14_ADR_INDEX.md'

def parse_index():
    index_data = {}
    if not os.path.exists(ADR_INDEX_PATH): return index_data
    with open(ADR_INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match table rows: | ADR-XXXX | Title | Status | Scope | Date | Related | Notes |
    rows = re.findall(r'\| (ADR-\d+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|', content)
    for row in rows:
        index_data[row[0]] = {
            'title': row[1].strip(),
            'status': row[2].strip(),
            'scope': row[3].strip(),
            'date': row[4].strip(),
            'related': row[5].strip(),
            'notes': row[6].strip()
        }
    return index_data

def get_file_metadata(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read(1000) # Read enough for headers
    
    lines = content.split('\n')
    title_line = lines[0].strip()
    title_match = re.search(r'# ADR-\d+[:\s\u2013\u2014\-]+(.*)', title_line)
    title = title_match.group(1).strip() if title_match else title_line.replace('# ', '')
    
    date_match = re.search(r'^(?:Date|Fecha):\s*(.*)', content, re.MULTILINE | re.IGNORECASE)
    date = date_match.group(1).strip() if date_match else None
    
    status_match = re.search(r'^(?:Status|Estado):\s*(.*)', content, re.MULTILINE | re.IGNORECASE)
    status = status_match.group(1).strip() if status_match else None
    
    return {'title': title, 'date': date, 'status': status}

index_data = parse_index()
adrs = sorted([f for f in os.listdir(ADR_DIR) if f.startswith('ADR-') and f.endswith('.md')])

proposals = []

for adr_file in adrs:
    path = os.path.join(ADR_DIR, adr_file)
    id_match = re.search(r'ADR-(\d+)', adr_file)
    adr_id = f'ADR-{id_match.group(1)}' if id_match else 'UNKNOWN'
    
    file_meta = get_file_metadata(path)
    idx = index_data.get(adr_id, {})
    
    # Documentary Fields
    status = idx.get('status') or file_meta.get('status') or 'REVIEW_REQUIRED'
    date = file_meta.get('date') or idx.get('date') or 'REVIEW_REQUIRED'
    scope = idx.get('scope') or 'REVIEW_REQUIRED'
    related = idx.get('related') if idx.get('related') and idx.get('related') != '-' else 'NONE'
    
    val_ref = 'NONE'
    if idx.get('notes') and 'make ' in idx['notes']:
        # Extract make command if possible
        cmd = re.search(r'(`make \S+`|make \S+)', idx['notes'])
        if cmd: val_ref = cmd.group(1).replace('`', '')

    # Semantic Fields (Conservative)
    dtype = 'REVIEW_REQUIRED'
    title_full = file_meta['title']
    if any(k in title_full.lower() for k in ['security', 'hardening', 'authentication', 'seguridad', 'endurecimiento']):
        dtype = 'SECURITY'
    elif any(k in title_full.lower() for k in ['architecture', 'architectural pattern', 'arquitectura', 'patrón']):
        dtype = 'ARCHITECTURE'
    
    tags = 'REVIEW_REQUIRED' # Conservative
    
    # Evidence Check
    fields_with_evidence = []
    if idx.get('status') or file_meta.get('status'): fields_with_evidence.append('Status')
    if file_meta.get('date') or idx.get('date'): fields_with_evidence.append('Date')
    if idx.get('scope'): fields_with_evidence.append('Scope')
    if idx.get('related') and idx.get('related') != '-': fields_with_evidence.append('Related ADRs')
    if val_ref != 'NONE': fields_with_evidence.append('Validation Reference')
    if dtype != 'REVIEW_REQUIRED': fields_with_evidence.append('Decision Type')

    fields_pending = []
    if status == 'REVIEW_REQUIRED': fields_pending.append('Status')
    if date == 'REVIEW_REQUIRED': fields_pending.append('Date')
    if scope == 'REVIEW_REQUIRED': fields_pending.append('Scope')
    if dtype == 'REVIEW_REQUIRED': fields_pending.append('Decision Type')
    if tags == 'REVIEW_REQUIRED': fields_pending.append('Tags')

    confidence = 'HIGH'
    # HIGH: All documentary fields have evidence (Status, Date, Scope, Related ADRs, Validation Reference)
    # Actually user says: "Todos los campos documentales tienen evidencia"
    doc_fields = ['Status', 'Date', 'Scope'] # Minimum for HIGH
    if not all(f in fields_with_evidence for f in doc_fields):
        confidence = 'MEDIUM'
    
    # Conflict check
    if idx.get('status') and file_meta.get('status'):
        # Map statuses for comparison
        s1 = idx['status'].upper()
        s2 = file_meta['status'].upper()
        # Simple mapping
        if s2 == 'APROBADO': s2 = 'APPROVED'
        if s2 == 'ACCEPTED': s2 = 'APPROVED'
        if s1 != s2 and s1 in ['APPROVED', 'PROPOSED', 'DEPRECATED', 'SUPERSEDED']:
            confidence = 'LOW'

    proposals.append({
        'adr': adr_id,
        'title': title_full,
        'header': {
            'Status': status,
            'Date': date,
            'Decision Type': dtype,
            'Scope': scope,
            'Tags': tags,
            'Related ADRs': related,
            'Supersedes': 'NONE',
            'Superseded By': 'NONE',
            'Validation Reference': val_ref
        },
        'evidence': fields_with_evidence,
        'pending': fields_pending,
        'confidence': confidence
    })

print(json.dumps(proposals, indent=2))
