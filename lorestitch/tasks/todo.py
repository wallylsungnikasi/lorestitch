import os, json
from datetime import datetime
from typing import List, Dict, Optional

ROOT = os.path.dirname(os.path.dirname(__file__))
BASE = os.path.dirname(ROOT)
TASKS_DIR = os.path.join(BASE, "tasks")

def ensure_dir():
    os.makedirs(TASKS_DIR, exist_ok=True)

def add_task(title: str, due: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
    ensure_dir()
    day = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(TASKS_DIR, f"{day}.json")
    data: Dict[str, List[dict]] = {"tasks": []}
    if os.path.exists(path):
        data = json.load(open(path, "r", encoding="utf-8"))
    data["tasks"].append({"ts": datetime.now().isoformat(), "title": title, "due": due or "", "tags": tags or []})
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return path

def list_days() -> List[str]:
    ensure_dir()
    return sorted([f for f in os.listdir(TASKS_DIR) if f.endswith(".json")])

def read_day(filename: str) -> Optional[dict]:
    p = os.path.join(TASKS_DIR, filename)
    return json.load(open(p, "r", encoding="utf-8")) if os.path.exists(p) else None
