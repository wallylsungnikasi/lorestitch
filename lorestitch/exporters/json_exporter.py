import os, json
from ..graph.build import build_graph, load_index

ROOT = os.path.dirname(os.path.dirname(__file__))
BASE = os.path.dirname(ROOT)
REPORTS_DIR = os.path.join(BASE, "reports")

def export_all_to_json() -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    out = {"index": load_index(), "graph": build_graph()}
    p = os.path.join(REPORTS_DIR, "export.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return p
