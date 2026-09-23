import json
import glob
from pathlib import Path

out_lines = []
for p in sorted(glob.glob('e:/GoogleAntigravity/automation/OpenDataAnalysisTokouynu/data/catalog/*.json')):
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    out_lines.append(f"=== {Path(p).name} ===")
    out_lines.append(f"time_col: {d.get('time_col')}")
    out_lines.append(f"group_col: {d.get('group_col')}")
    out_lines.append(f"metrics: {d.get('metrics')}")
    if d.get("data"):
        out_lines.append(f"data[0] keys: {list(d['data'][0].keys())}")
        grp = d.get('group_col')
        if grp and grp in d['data'][0]:
            out_lines.append(f"group sample value: {d['data'][0][grp]}")

with open('e:/GoogleAntigravity/automation/OpenDataAnalysisTokouynu/tools/keys_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
