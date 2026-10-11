#!/usr/bin/env python3
"""lint_diff.py: git/diff checks and PR classification for ai-agents-second-wiki-brain.

stdlib only, Python 3.8+. Classifies a PR by its diff (never by branch name) and enforces
the per-class rules. Run: py -I scripts/lint_diff.py --base <sha> --root .
Exit codes (same contract as lint.py): 0 no HARD, 1 any HARD (incl. merge-base not
computable, fail closed), 2 usage/internal error.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import namedtuple

Finding = namedtuple("Finding", "level code path line msg")
Change = namedtuple("Change", "status path old_mode new_mode")
HARD, WARN, INFO = "HARD", "WARN", "INFO"
_ORDER = {HARD: 0, WARN: 1, INFO: 2}
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
FLIP_LINE_RE = re.compile(r"^[+-](status|updated): ")
SYMLINK_MODE = "120000"


class GitError(Exception):
    pass


def git(root, *args, env=None):
    """Run git and return stdout bytes; raise GitError on non-zero exit."""
    cmd = ["git", "-c", "core.quotepath=false", "-C", root] + list(args)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if p.returncode != 0:
        raise GitError(p.stderr.decode("utf-8", "replace").strip())
    return p.stdout


def text_at(root, rev, path, env=None):
    """File content at a revision, LF-normalised; None if absent."""
    try:
        data = git(root, "show", "%s:%s" % (rev, path), env=env)
    except GitError:
        return None
    return data.decode("utf-8", "replace").replace("\r\n", "\n")


def read_status(text):
    """Return (status or None, 1-based line of closing '---' or 0). Takes TEXT, not a path.

    Keep identical in meaning to lint.py's canonical status line rule; quoted forms are
    read leniently here (lint.py is what rejects them).
    """
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None, 0
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        return None, 0
    status = None
    for i in range(1, end):
        m = re.match(r"^status:\s*(.*?)\s*$", lines[i])
        if m:
            v = m.group(1)
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            status = v
            break
    return status, end + 1


def parse_raw_diff(out):
    """Parse `git diff --raw -z --no-renames`: ':<om> <nm> <os> <ns> <S>\\0<path>\\0' records."""
    toks = out.decode("utf-8", "replace").split("\0")
    changes, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t.startswith(":"):
            f = t[1:].split(" ")
            if len(f) >= 5 and i + 1 < len(toks):
                changes.append(Change(f[4][:1], toks[i + 1], f[0], f[1]))
            i += 2
        else:
            i += 1
    return changes


def path_class(p):
    if p == "wiki/index.md":
        return "index"
    if p.startswith("wiki/") or p.startswith("raw/"):
        return "content"
    return "schema"


def is_page(p):
    return p.startswith("wiki/") and p.endswith(".md") and p != "wiki/index.md" and not p.startswith("wiki/log/")


def only_status_lines(root, mb, path, new_text, env):
    """True iff every changed line of `path` is a frontmatter status:/updated: line."""
    out = git(root, "diff", "-U0", "--no-color", mb, "HEAD", "--", path, env=env)
    _, fm_end = read_status(new_text)
    seen, ok = False, True
    start = 0
    for ln in out.decode("utf-8", "replace").split("\n"):
        m = HUNK_RE.match(ln)
        if m:
            start = int(m.group(1))
            if fm_end == 0 or start > fm_end:
                ok = False
            continue
        if ln.startswith(("+++", "---", "diff ", "index ", "old mode", "new mode")):
            continue
        if ln.startswith(("+", "-")):
            seen = True
            if not FLIP_LINE_RE.match(ln):
                ok = False
    return seen and ok


def body_of(text):
    """Text after the frontmatter (LF-normalised)."""
    lines = text.replace("\r\n", "\n").split("\n")
    _s, end = read_status(text)
    return "\n".join(lines[end:]) if end else text


def old_blocks(text):
    """Lines of the '## Steps' block(s): after the heading up to the next # or ## heading."""
    lines, out, i = text.replace("\r\n", "\n").split("\n"), [], 0
    while i < len(lines):
        if re.match(r"^##\s+Steps\s*$", lines[i]):
            i += 1
            while i < len(lines) and not re.match(r"^#{1,2}\s", lines[i]):
                out.append(lines[i])
                i += 1
        else:
            i += 1
    return out


def check_index_equal(root, env, add):
    """Index PR must equal BASE's `lint.py --index --stdout` run over the head tree.

    Uses the sibling lint.py of THIS script (main's copy when Sir runs main's), never
    root/scripts. Any inability to compare fails closed.
    """
    lint = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint.py")
    try:
        p = subprocess.run([sys.executable, "-I", lint, "--index", "--stdout", "--root", root],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    except OSError as e:
        add(HARD, "INDEX_UNCHECKED", "wiki/index.md", 0, "cannot run lint.py (fail closed): %s" % type(e).__name__)
        return
    head = text_at(root, "HEAD", "wiki/index.md", env)
    if p.returncode != 0 or head is None:
        add(HARD, "INDEX_UNCHECKED", "wiki/index.md", 0, "index not comparable (fail closed)")
        return
    want = p.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
    if want != head:
        add(HARD, "INDEX_MISMATCH", "wiki/index.md", 0, "index differs from lint.py --index output")


def analyze(root, base, env=None):
    """Return (class, findings) for the diff merge-base(base, HEAD)..HEAD."""
    out = []

    def add(level, code, path, line, msg):
        out.append(Finding(level, code, path, line, msg))

    try:
        mb = git(root, "merge-base", base, "HEAD", env=env).decode().strip()
        if not mb:
            raise GitError("empty merge-base")
        changes = parse_raw_diff(git(root, "diff", "--raw", "-z", "--no-renames", mb, "HEAD", env=env))
    except GitError as e:
        add(HARD, "MERGE_BASE", "-", 0, "merge-base/diff not computable (fail closed): " + str(e)[:120])
        return "unknown", out
    if not changes:
        return "none", out

    for c in changes:
        if c.new_mode == SYMLINK_MODE:
            add(HARD, "SYMLINK", c.path, 0, "symlink (git mode 120000) not allowed")
        # any non-add change under raw/ (any file type, incl. T); only deleting the raw/.gitkeep placeholder is exempt
        if c.path.startswith("raw/") and c.status != "A" and not (c.path == "raw/.gitkeep" and c.status == "D"):
            add(HARD, "RAW_MODIFIED", c.path, 0, "raw records are add-only (status %s)" % c.status)

    classes = {path_class(c.path) for c in changes}
    if len(classes) > 1:
        add(HARD, "MIXED", "-", 0, "mixed diff touches: " + ", ".join(sorted(classes)))
        cls = "mixed"
    elif classes == {"index"}:
        cls = "index"
    elif classes == {"schema"}:
        cls = "schema"
    else:
        cls = "ingest"
        pages = [c for c in changes if is_page(c.path)]
        only = all(c.status == "M" and is_page(c.path) for c in changes)
        if only:
            flip = True
            for c in changes:
                nt = text_at(root, "HEAD", c.path, env) or ""
                if not only_status_lines(root, mb, c.path, nt, env):
                    flip = False
                    break
            if flip:
                cls = "flip"
        del pages

    deleted_pages = {os.path.basename(c.path): c.path for c in changes if c.status == "D" and is_page(c.path)}
    for c in changes:
        if not is_page(c.path) or c.new_mode == SYMLINK_MODE:
            continue  # symlinks already failed above; their "content" is a link target
        new = text_at(root, "HEAD", c.path, env)
        new_status = read_status(new)[0] if new is not None else None
        moved_from = deleted_pages.get(os.path.basename(c.path)) if c.status == "A" else None
        if moved_from is not None:
            # a folder move is delete+add of the same slug: judge it like a modification of the old page
            old = text_at(root, mb, moved_from, env)
            old_status = read_status(old)[0] if old is not None else None
            add(INFO, "MOVED", c.path, 0, "page moved from %s" % moved_from)
            if old_status != new_status:
                add(HARD, "STATUS_CHANGE", c.path, 0,
                    "pages becoming %s: status change outside a flip PR (move first, flip separately)" % new_status)
            elif new_status == "live" and body_of(old or "") != body_of(new or ""):
                add(INFO, "LIVE_BODY_CHANGED", c.path, 0,
                    "live page body changed: re-spot-check before it counts as live")
        elif c.status == "A" and new_status != "draft":
            add(HARD, "ADDED_NOT_DRAFT", c.path, 0, "new page must be status: draft (is %s)" % new_status)
        elif c.status == "M":
            old = text_at(root, mb, c.path, env)
            old_status = read_status(old)[0] if old is not None else None
            if old_status != new_status:
                if cls == "flip":
                    add(INFO, "BECOMING", c.path, 0, "pages becoming %s: %s" % (new_status, c.path))
                else:
                    add(HARD, "STATUS_CHANGE", c.path, 0,
                        "pages becoming %s: status change outside a flip PR" % new_status)

    if cls == "flip":
        add(INFO, "STATUS_ONLY", "-", 0, "status-only: yes")
    for c in changes:  # INFO for Sir's merge read
        if is_page(c.path) and c.status == "M" and c.new_mode != SYMLINK_MODE and cls != "flip":
            old, new = text_at(root, mb, c.path, env) or "", text_at(root, "HEAD", c.path, env) or ""
            if old_blocks(old) != old_blocks(new):
                add(INFO, "STEPS_CHANGED", c.path, 0, "Steps block changed (read it before merging)")
            if read_status(new)[0] == "live" and body_of(old) != body_of(new):
                add(INFO, "LIVE_BODY_CHANGED", c.path, 0,
                    "live page body changed: re-spot-check before it counts as live")
    if cls == "index":
        check_index_equal(root, env, add)
    if cls == "schema":
        add(INFO, "SCHEMA", "-", 0, "needs Sir's explicit OK (schema change)")
    return cls, out


def report(cls, findings):
    print("class: " + cls)
    fs = sorted(findings, key=lambda f: (_ORDER[f.level], f.path, f.line, f.code))
    for f in fs:
        loc = f.path + (":" + str(f.line) if f.line else "")
        print("%s %s %s %s" % (f.level, f.code, loc, f.msg))
    hard = sum(1 for f in fs if f.level == HARD)
    print("lint_diff: %d HARD" % hard)
    return 1 if hard else 0


# ---- selftest -------------------------------------------------------------

def _read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8").replace("\r\n", "\n")


def _expect(path):
    exp = {"exit": 0, "class": None, "hard": set(), "symlink": [], "base_sha": None}
    for ln in _read(path).split("\n"):
        k, _, v = ln.partition(":")
        k, v = k.strip(), v.strip()
        if k == "exit":
            exp["exit"] = int(v)
        elif k == "class":
            exp["class"] = v
        elif k == "hard":
            exp["hard"] = set(v.split())
        elif k == "symlink":
            exp["symlink"] = v.split()
        elif k == "base_sha":
            exp["base_sha"] = v
    return exp


def _isolated_env():
    env = dict(os.environ)
    env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})
    return env


_GIT_OPTS = ["-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull,
             "-c", "core.autocrlf=false", "-c", "core.safecrlf=false"]


def _g(root, env, *args, data=None):
    p = subprocess.run(["git"] + _GIT_OPTS + ["-C", root] + list(args), input=data,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if p.returncode != 0:
        raise GitError(p.stderr.decode("utf-8", "replace"))
    return p.stdout


def _wipe(root):
    for name in os.listdir(root):
        if name == ".git":
            continue
        p = os.path.join(root, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.unlink(p)


def _copy_tree(src, dst):
    for dp, _, files in os.walk(src):
        for name in files:
            s = os.path.join(dp, name)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(s, d)


def run_selftest():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "diff")
    if not os.path.isdir(base_dir):
        print("selftest: no fixtures at " + base_dir)
        return 2
    env = _isolated_env()
    total = failed = 0
    for case in sorted(os.listdir(base_dir)):
        cdir = os.path.join(base_dir, case)
        if not os.path.isdir(os.path.join(cdir, "base")):
            continue
        total += 1
        exp = _expect(os.path.join(cdir, "expect.txt"))
        tmp = tempfile.mkdtemp(prefix="diffix-")
        try:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo)
            _g(repo, env, "init", "-q", "-b", "main")
            _copy_tree(os.path.join(cdir, "base"), repo)
            _g(repo, env, "add", "-A")
            _g(repo, env, "commit", "-q", "-m", "base")
            base_sha = _g(repo, env, "rev-parse", "HEAD").decode().strip()
            _wipe(repo)
            _copy_tree(os.path.join(cdir, "head"), repo)
            links = []
            for rel in exp["symlink"]:  # Windows symlinks need privilege: write the index entry directly
                p = os.path.join(repo, rel)
                links.append((rel, _read(p)))
                os.unlink(p)
            _g(repo, env, "add", "-A")
            for rel, target in links:
                blob = _g(repo, env, "hash-object", "-w", "--stdin", data=target.encode()).decode().strip()
                _g(repo, env, "update-index", "--add", "--cacheinfo", "120000,%s,%s" % (blob, rel))
            _g(repo, env, "commit", "-q", "--allow-empty", "-m", "head")
            use_base = "0123456789012345678901234567890123456789" if exp["base_sha"] == "bogus" else base_sha
            cls, fs = analyze(repo, use_base, env)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        hard = {f.code for f in fs if f.level == HARD}
        code = 1 if hard else 0
        ok = code == exp["exit"] and hard == exp["hard"] and cls == exp["class"]
        failed += 0 if ok else 1
        print("%s %s (class %s, exit %d, HARD %s)" % ("PASS" if ok else "FAIL", case, cls, code,
                                                      " ".join(sorted(hard)) or "-"))
        if not ok:
            print("     expected class %s, exit %d, HARD %s" % (exp["class"], exp["exit"],
                                                              " ".join(sorted(exp["hard"])) or "-"))
    # reader parity table: keep identical to the table in lint.py's fixtures (status forms)
    table = (("---\nstatus: draft\n---\n", "draft"), ("---\nstatus: 'live'\n---\n", "live"),
             ("---\r\nstatus: live \r\n---\r\n", "live"), ("no frontmatter\n", None))
    for text, want in table:
        total += 1
        got = read_status(text)[0]
        ok = got == want
        failed += 0 if ok else 1
        print("%s read_status %r -> %r" % ("PASS" if ok else "FAIL", text[:24], got))
    print("selftest: %d/%d passed" % (total - failed, total))
    return 1 if failed or total == 0 else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="git/diff lint and PR classification")
    ap.add_argument("--root", default=".")
    ap.add_argument("--base")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if args.selftest:
            return run_selftest()
        if not args.base:
            print("lint_diff: --base <sha> is required", file=sys.stderr)
            return 2
        cls, fs = analyze(args.root, args.base)
        return report(cls, fs)
    except Exception as e:  # internal error: fail closed with exit 2
        print("lint_diff: internal error: %r" % (e,), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
