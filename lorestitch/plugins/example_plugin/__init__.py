import os, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BASE = os.path.dirname(ROOT)
NOTES_DIR = os.path.join(BASE, "notes")
META_DIR  = os.path.join(BASE, "data", "meta")

def run():
    idx_path = os.path.join(META_DIR, "index.json")
    if not os.path.exists(idx_path): return False, "index.json not found"
    idx = json.load(open(idx_path, "r", encoding="utf-8"))
    for fn in list(idx.keys()):
        fp = os.path.join(NOTES_DIR, fn)
        if not os.path.exists(fp): continue
        text = open(fp, "r", encoding="utf-8").read()
        words = re.findall(r"\w+", text, flags=re.UNICODE)
        meta = idx.get(fn) or {}
        meta["word_count"] = len(words)
        idx[fn] = meta
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return True, "plugin: word_count updated"
