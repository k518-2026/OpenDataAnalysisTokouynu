import json
import glob

for p in sorted(glob.glob('e:/GoogleAntigravity/automation/OpenDataAnalysisTokouynu/data/catalog/*.json')):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
        row0 = d['data'][0] if d.get('data') else {}
        print(f"{d['id']}: metrics={d.get('metrics')} | keys={list(row0.keys())}")
