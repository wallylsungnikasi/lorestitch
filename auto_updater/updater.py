from datetime import datetime, UTC
import os, sys, random, re, subprocess
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auto_updater.notify import notify

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNIPPETS_DIR = os.path.join(ROOT, "data", "snippets_code")
TARGET_DIRS = [os.path.join(ROOT, p) for p in [
    "lorestitch","lorestitch/core","lorestitch/graph","lorestitch/exporters",
    "lorestitch/plugins","lorestitch/utils","lorestitch/tasks","lorestitch/bookmarks"]]

PROB_ADD = 0.6
PROB_DELETE = 0.2
PROB_MINOR = 0.35

SNIPPET_HEADER = re.compile(r"# --- snippet: (.+?) ---")
SNIPPET_END = re.compile(r"# --- endsnippet ---", re.MULTILINE)
DEF_OR_CLASS = re.compile(r"^(def |class )", re.MULTILINE)

def load_all_snippets():
    snippets = {}
    if not os.path.isdir(SNIPPETS_DIR): return snippets
    for fname in os.listdir(SNIPPETS_DIR):
        p = os.path.join(SNIPPETS_DIR, fname)
        if not os.path.isfile(p): continue
        text = open(p, "r", encoding="utf-8").read()
        for s in SNIPPET_HEADER.finditer(text):
            name = s.group(1).strip()
            m_end = SNIPPET_END.search(text, pos=s.end())
            if not m_end: continue
            code = text[s.start():m_end.end()].strip() + "\n\n"
            snippets[name] = code
    return snippets

def list_target_files():
    t = []
    for d in TARGET_DIRS:
        for r, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for f in files:
                if f.endswith(".py"): t.append(os.path.join(r, f))
    return t

def find_snippet_blocks(text):
    blocks = {}
    for m in SNIPPET_HEADER.finditer(text):
        name = m.group(1).strip()
        m_end = SNIPPET_END.search(text, pos=m.end())
        if not m_end: continue
        blocks[name] = (m.start(), m_end.end())
    return blocks

def random_insertion_index(text):
    pos = [m.start() for m in DEF_OR_CLASS.finditer(text)]
    pos.append(len(text))
    return random.choice(pos)

def insert_snippet(text, code):
    idx = random_insertion_index(text)
    prefix = "" if (idx == 0 or text[max(0, idx-1)] == "\n") else "\n"
    return text[:idx] + prefix + "\n" + code + text[idx:], idx

def replace_snippet(text, name, code, blocks):
    s, e = blocks[name]; return text[:s] + code + text[e:]

def delete_snippet(text, name, blocks):
    s, e = blocks[name]; return text[:s] + text[e:]

def minor_tweak(path):
    stamp = f"# tweak {datetime.now(UTC).isoformat()}\n"
    with open(path, "a", encoding="utf-8") as f: f.write(stamp)
    return f"Minor tweak in {os.path.relpath(path, ROOT)}"

def choose_action_and_apply(snippets, targets):
    if not targets: return "No target .py files found."
    target = random.choice(targets); txt = open(target, "r", encoding="utf-8").read()
    blocks = find_snippet_blocks(txt); inserted = list(blocks.keys())
    if random.random() < PROB_MINOR: return minor_tweak(target)
    if inserted and random.random() < PROB_DELETE:
        name = random.choice(inserted); new = delete_snippet(txt, name, blocks)
        open(target, "w", encoding="utf-8").write(new)
        return f"Deleted snippet '{name}' from {os.path.relpath(target, ROOT)}"
    if snippets and random.random() < PROB_ADD:
        name, code = random.choice(list(snippets.items()))
        if name in blocks: new = replace_snippet(txt, name, code, blocks)
        else: new, _ = insert_snippet(txt, code)
        open(target, "w", encoding="utf-8").write(new)
        return f"{'Replaced' if name in blocks else 'Added'} snippet '{name}' in {os.path.relpath(target, ROOT)}"
    open(target, "a", encoding="utf-8").write(f"\n# autosave {datetime.now(UTC).isoformat()}\n")
    return f"Touched {os.path.relpath(path=target, start=ROOT)} (no snippet change)"

def check_syntax():
    try:
        py = []
        for r, d, files in os.walk(ROOT):
            if "__pycache__" in r: continue
            for f in files:
                if f.endswith(".py"): py.append(os.path.join(r, f))
        if not py: return True
        subprocess.run(["python3", "-m", "py_compile"] + py, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def git_commit_and_push(msg: str):
    try:
        subprocess.run(["git", "add", "."], check=True)
        r = subprocess.run(["git", "commit", "-m", msg])
        if r.returncode != 0: return False, "No changes to commit"
        p = subprocess.run(["git", "pull", "--rebase"])
        if p.returncode != 0:
            subprocess.run(["git", "rebase", "--abort"], check=False)
            ff = subprocess.run(["git", "pull", "--ff-only"])
            if ff.returncode != 0: return False, "Pull failed"
        subprocess.run(["git", "push"], check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, str(e)

def main():
    s = load_all_snippets(); t = list_target_files()
    msg = choose_action_and_apply(s, t)
    if not check_syntax():
        notify(f"Syntax error after change: {msg}. Commit aborted."); return
    ok, err = git_commit_and_push(msg)
    notify(f"{'Committed' if ok else 'Commit failed'}: {msg}" + ("" if ok else f". Error: {err}"))

if __name__ == "__main__":
    main()
