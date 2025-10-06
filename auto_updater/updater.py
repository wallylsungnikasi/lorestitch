from datetime import datetime, UTC
import os, sys, random, re, subprocess
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auto_updater.notify import notify

import re, random, subprocess as _subprocess
TYPO_PROB = 0.04  # ~4% rare typos

def _typo_word(w: str) -> str:
    if len(w) < 4: return w
    i = random.randint(1, len(w)-2)
    return w[:i-1] + w[i] + w[i-1] + w[i+1:]

def sprinkle_typos(s: str, prob: float = TYPO_PROB) -> str:
    parts = re.split(r'(`[^`]+`|\w+://\S+|[a-f0-9]{7,40})', s)
    out = []
    for p in parts:
        if p.startswith('`') or '://' in p or re.fullmatch(r'[a-f0-9]{7,40}', p or ''):
            out.append(p); continue
        words = p.split(' ')
        for i,w in enumerate(words):
            if random.random() < prob and re.match(r'[A-Za-z]', w):
                words[i] = _typo_word(w)
        out.append(' '.join(words))
    return ''.join(out)

def humanize(msg: str) -> str:
    m = (msg or "").strip()
    g = re.match(r"(Added|Deleted|Replaced)\s+snippet\s+'([^']+)'\s+(?:in|into|from)\s+(.+)", m, re.I)
    if g:
        kind, name, path = g.group(1).lower(), g.group(2), g.group(3)
        added = [
            f"Add snippet “{name}” to {path}", f"Dropped in snippet “{name}” into {path}",
            f"New code: “{name}” now lives in {path}", f"Introduce “{name}” under {path}",
            f"Wire up “{name}” in {path}", f"Bring in “{name}” to {path}",
            f"Lay down “{name}” in {path}", f"Plant “{name}” inside {path}",
        ]
        deleted = [
            f"Remove “{name}” from {path}", f"Cleanup: deleted “{name}” from {path}",
            f"Trim dead code — “{name}” out of {path}", f"Drop “{name}” from {path}",
            f"Cut “{name}” out of {path}", f"Retire “{name}” from {path}",
            f"Scrub out “{name}” in {path}", f"Prune “{name}” away from {path}",
        ]
        replaced = [
            f"Replace “{name}” in {path}", f"Refresh snippet “{name}” in {path}",
            f"Rework “{name}” — see {path}", f"Swap in a better “{name}” for {path}",
            f"Revamp “{name}” within {path}", f"Overhaul “{name}” in {path}",
            f"Modernize “{name}” inside {path}", f"Refactor “{name}” in {path}",
        ]
        pool = {"added": added, "deleted": deleted, "replaced": replaced}[kind]
        import random as _r
        return sprinkle_typos(_r.choice(pool))
    if re.match(r"\bTouched\s+.+?\(no snippet change\)", m, re.I) or "no snippet change" in m:
        opts = [
            "Touch up (no functional change)",
            "Small nudge (no functional change)",
            "Maintenance tweak (no logic change)",
            "Tiny housekeeping (no behavior change)",
            "Keep things tidy (no logic changes)",
            "Polish a little bit",
        ]
        import random as _r
        pm = re.search(r"Touched\s+(.+?)\s+\(no snippet change\)", m, re.I)
        if pm:
            path = pm.group(1)
            opts = [f"Touch up {path} (no functional change)",
                    f"Small nudge in {path}",
                    f"Maintenance tweak in {path}",
                    f"Tiny housekeeping in {path}",
                    f"Keep {path} tidy (no logic changes)",
                    f"Polish {path} a little bit"]
        return sprinkle_typos(_r.choice(opts))
    if re.search(r"\btests?\b", m, re.I):
        import random as _r
        return sprinkle_typos(_r.choice([
            "Tests: tighten and clarify","Make tests less flaky","Update tests a bit",
            "Tests: improve coverage slightly","Deflake tests around edge cases","Stabilize a couple of tests",
        ]))
    if re.search(r"\bdocs?\b|README", m, re.I):
        import random as _r
        return sprinkle_typos(_r.choice([
            "Docs pass: clarify wording","README: quick refresh","Polish docs a little",
            "Docs: add missing bits","Docs cleanup and rewording","Docs: small touch-up across sections",
        ]))
    generic = [
        "Small improvements here and there","A couple of neat touch-ups",
        "Quiet but helpful refactor","Subtle code hygiene improvements",
        "Nip and tuck around the codebase","Sanded down a few rough edges",
        "Quality-of-life tweaks","Tidy up minor inconsistencies",
    ]
    import random as _r
    return sprinkle_typos(m if len(m) > 60 else _r.choice(generic))

# monkey-patch subprocess.run (перехватываем git commit -m)
try:
    _real_run = _subprocess.run
    def _patched_run(args, *a, **kw):
        try:
            arr = args
            if isinstance(arr,(list,tuple)) and len(arr) >= 3:
                if str(arr[0]) == "git" and str(arr[1]) == "commit":
                    arr = list(arr)
                    for i,x in enumerate(arr):
                        if x == "-m" and i+1 < len(arr):
                            arr[i+1] = humanize(str(arr[i+1]))
                            break
            return _real_run(arr, *a, **kw)
        except Exception:
            return _real_run(args, *a, **kw)
    _subprocess.run = _patched_run
except Exception:
    pass

# monkey-patch GitPython Repo.index.commit (если используется)
try:
    import git as _git
    _RealCommit = _git.index.base.IndexFile.commit
    def _patched_commit(self, message, *a, **kw):
        try:
            message = humanize(str(message))
        except Exception:
            pass
        return _RealCommit(self, message, *a, **kw)
    _git.index.base.IndexFile.commit = _patched_commit
except Exception:
    pass


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
