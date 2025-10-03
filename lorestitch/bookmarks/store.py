import os, json
from datetime import datetime
from typing import List, Dict, Optional

ROOT = os.path.dirname(os.path.dirname(__file__))
BASE = os.path.dirname(ROOT)
BM_DIR = os.path.join(BASE, "bookmarks")

def ensure_dir():
    os.makedirs(BM_DIR, exist_ok=True)

def add_bookmark(url: str, title: Optional[str] = None, tags: Optional[List[str]] = None, note: str = "") -> str:
    ensure_dir()
    day = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(BM_DIR, f"{day}.json")
    data: Dict[str, List[dict]] = {"bookmarks": []}
    if os.path.exists(path):
        data = json.load(open(path, "r", encoding="utf-8"))
    data["bookmarks"].append({"ts": datetime.now().isoformat(), "url": url, "title": title or "", "tags": tags or [], "note": note})
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return path

def list_days() -> List[str]:
    ensure_dir()
    return sorted([f for f in os.listdir(BM_DIR) if f.endswith(".json")])

def read_day(filename: str) -> Optional[dict]:
    p = os.path.join(BM_DIR, filename)
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else None
