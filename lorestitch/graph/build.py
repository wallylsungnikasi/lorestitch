import os, json, re
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(__file__))
BASE = os.path.dirname(ROOT)
META_DIR = os.path.join(BASE, "data", "meta")

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\-_]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s

def load_index() -> Dict[str, dict]:
    p = os.path.join(META_DIR, "index.json")
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else {}

def build_graph() -> Dict[str, List[str]]:
    idx = load_index()
    title2file = {slugify(fn.rsplit(".",1)[0]): fn for fn in idx.keys()}
    g: Dict[str, List[str]] = {fn: [] for fn in idx.keys()}
    for fn, meta in idx.items():
        for link in meta.get("links", []):
            target = title2file.get(slugify(link))
            if target and target != fn and target in g:
                g[fn].append(target)
    return g
