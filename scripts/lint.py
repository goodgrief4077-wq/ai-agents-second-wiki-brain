#!/usr/bin/env python3
"""lint.py: offline content checks for ai-agents-second-wiki-brain.

stdlib only, no git, no network. Python 3.8+. Run: py -I scripts/lint.py --root .
Exit codes: 0 clean (no HARD), 1 any HARD finding, 2 internal/unreadable error.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from collections import namedtuple

Finding = namedtuple("Finding", "level code path line msg")
HARD, WARN, INFO = "HARD", "WARN", "INFO"
_ORDER = {HARD: 0, WARN: 1, INFO: 2}

SLUG_RE = re.compile(r"^[a-z0-9-]+$")
# Legacy YYYY-MM-DD-<slug> stays valid; new records use YY-MM-DD-HHMM-<slug>.
RAW_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{2}-([01]\d|2[0-3])[0-5]\d)-[a-z0-9-]+$")
SKILL_PATH_RE = re.compile(r"^skills/[a-z0-9-]+/(SKILL|[a-z0-9.-]+)\.md$")
RAW_NEW_RE = re.compile(r"^(\d{2})-(\d{2})-(\d{2})-(\d{4})-")
# skills/**: sanitized, agent-neutral copies; only <placeholder> forms may stand for private details.
SKILL_PRIVATE_RES = (
    ("local path", re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/home/|/Users/")),
    ("mail address", re.compile(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")),
    ("IPv4 address or 4-part version (write v1.2.3.4 as 1.2.3)", re.compile(r"(?<![\d.])\d{1,3}(\.\d{1,3}){3}(?![\d.])")),
    ("owner title", re.compile(r"\bSir\b")),
    # Windows-path shape only: two or more plain segments, or a <placeholder> prefix. Regex escapes like \b or \d pass.
    ("backslash path", re.compile(r"[A-Za-z0-9_>]\\[A-Za-z0-9_<][A-Za-z0-9_ .<>-]*\\[A-Za-z0-9_<]|<[a-z-]+>\\")),
)
_ISO = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)"
ISO_RE = re.compile("^" + _ISO + "$")
STATUS_LINE_RE = re.compile(r"^status: (draft|live|superseded)$")
UPDATED_LINE_RE = re.compile("^updated: " + _ISO + "$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?: (.*))?$")
ITEM_RE = re.compile(r"^\s*- (.*)$")
LINK_RE = re.compile(r"!?\[\[([^\]]+)\]\]")

SECRET_RES = (
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)
# Documented example values only. This is not a suppression marker.
ALLOWED_EXAMPLES = ("AKIA" + "IOSFODNN7EXAMPLE", "wJalrXUtnFEMI/K7MDENG/" + "bPxRfiCYEXAMPLEKEY")  # split: secret scanners flag the literal

PAGE_REQUIRED = ("title", "type", "sources", "updated", "status")
OS_JUNK = ("Thumbs.db", "desktop.ini", ".DS_Store")  # local OS files, git-ignored, skipped by the tree walk
RESERVED_SLUGS = ("index", "log")  # wiki/index.md and wiki/log/ own these names
PAGE_TYPES = ("tool", "method", "synthesis")
SECTIONS = ("concepts", "entities", "synthesis", "archive")  # wiki/<section>/<slug>.md, exactly one level
TYPE_SECTION = {"tool": "entities", "method": "concepts", "synthesis": "synthesis"}  # archive/ takes any type
RAW_KINDS = ("web", "pdf", "book")
ARCHIVE_STATUS = ("saved", "failed", "excluded", "none")
READ_VIA = ("raw", "extract", "browser-render", "pdf-text")
VERIFY_BY = ("hash", "locator+archive", "none")


def fold(s):
    return unicodedata.normalize("NFKC", s).casefold()


def read_text(path):
    """Return LF-normalised text, or None if the file is not valid UTF-8."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        text = data.decode("utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


class Doc:
    """One markdown file: rel path, text, parsed frontmatter (or None)."""

    def __init__(self, rel, text):
        self.rel = rel
        self.text = text
        self.lines = text.split("\n")
        self.fm = None  # dict key -> str | list[str]
        self.keyline = {}  # key -> 1-based line
        self.fm_end = 0  # 1-based line of closing ---, 0 = none
        self.errs = []  # (line, code, msg)
        self._parse()

    def _scalar(self, raw, n):
        v = raw.strip()
        if v.startswith(("[", "{")):
            self.errs.append((n, "FM_INLINE", "inline list/map not allowed; use a block list"))
            return v
        quoted = len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'"
        if quoted:
            return v[1:-1]
        if v.startswith("#") or " #" in v or ": " in v:
            self.errs.append((n, "FM_QUOTE", "unquoted value starts with '#' or contains ': ' or ' #'; quote it"))
        return v

    def _parse(self):
        if self.lines[0].rstrip() != "---":
            return
        end = next((i for i in range(1, len(self.lines)) if self.lines[i].rstrip() == "---"), None)
        if end is None:
            self.fm = {}
            self.errs.append((1, "FM_UNCLOSED", "frontmatter is not closed"))
            return
        self.fm_end = end + 1
        fm, key = {}, None
        for i in range(1, end):
            ln, n = self.lines[i], i + 1
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            m = ITEM_RE.match(ln)
            if m:
                if key is None or not isinstance(fm.get(key), list):
                    self.errs.append((n, "FM_SYNTAX", "list item without a list key"))
                else:
                    fm[key].append(self._scalar(m.group(1), n))
                continue
            m = KEY_RE.match(ln)
            if not m:
                self.errs.append((n, "FM_SYNTAX", "unparseable frontmatter line"))
                key = None
                continue
            key, val = m.group(1), (m.group(2) or "").strip()
            if key in fm:
                self.errs.append((n, "FM_DUP", "duplicate key " + key))
            self.keyline[key] = n
            fm[key] = [] if val == "" else self._scalar(val, n)
        self.fm = fm

    def raw_line(self, key):
        n = self.keyline.get(key)
        return self.lines[n - 1] if n else None


class Tree:
    def __init__(self, root):
        self.root = root
        self.pages, self.logs, self.raws = [], [], []
        self.has_index = False
        self.findings = []
        wiki, raw = os.path.join(root, "wiki"), os.path.join(root, "raw")
        for dirpath, dirs, files in os.walk(wiki):
            dirs.sort()
            rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
            for name in sorted(files):
                rel = rel_dir + "/" + name
                if not name.endswith(".md"):
                    if name != ".gitkeep" and name not in OS_JUNK:
                        self.findings.append(Finding(HARD, "UNEXPECTED_FILE", rel, 0,
                                                     "only lowercase .md files (and .gitkeep) belong under wiki/"))
                    continue
                doc = self._load(rel)
                if doc is None:
                    continue
                if rel == "wiki/index.md":
                    self.has_index = True
                elif rel.startswith("wiki/log/"):
                    if rel.count("/") != 2:
                        self.findings.append(Finding(HARD, "SECTION_DEPTH", rel, 0,
                                                     "logs are exactly wiki/log/<file>.md"))
                    self.logs.append(doc)
                else:
                    parts = rel.split("/")
                    if stem(rel) in RESERVED_SLUGS:
                        self.findings.append(Finding(HARD, "RESERVED_SLUG", rel, 0,
                                                     "slug is reserved: " + ", ".join(RESERVED_SLUGS)))
                    if len(parts) == 2:
                        self.findings.append(Finding(HARD, "SECTION_ROOT", rel, 0,
                                                     "pages live in wiki/<section>/, not at the wiki/ root"))
                    elif len(parts) > 3:
                        self.findings.append(Finding(HARD, "SECTION_DEPTH", rel, 0,
                                                     "pages are exactly one folder deep: wiki/<section>/<slug>.md"))
                    elif parts[1] not in SECTIONS:
                        self.findings.append(Finding(HARD, "SECTION_UNKNOWN", rel, 0,
                                                     "unknown section; allowed: " + ", ".join(SECTIONS)))
                    self.pages.append(doc)
        if os.path.isdir(raw):
            for name in sorted(os.listdir(raw)):
                if name.endswith(".md") and os.path.isfile(os.path.join(raw, name)):
                    doc = self._load("raw/" + name)
                    if doc is not None:
                        self.raws.append(doc)
                elif name != ".gitkeep" and name not in OS_JUNK:
                    self.findings.append(Finding(HARD, "UNEXPECTED_FILE", "raw/" + name, 0,
                                                 "only lowercase .md files (and .gitkeep) belong under raw/"))
        self.raw_slugs = {d.rel[4:-3] for d in self.raws}

    def _load(self, rel):
        text = read_text(os.path.join(self.root, rel.replace("/", os.sep)))
        if text is None:
            self.findings.append(Finding(HARD, "ENCODING", rel, 0, "not valid UTF-8"))
            return None
        return Doc(rel, text)


def stem(rel):
    return os.path.basename(rel)[:-3]


def body_lines(doc):
    """Yield (1-based line no, text) for body lines, skipping code fences and inline code."""
    fence = False
    for i in range(doc.fm_end, len(doc.lines)):
        ln = doc.lines[i]
        if ln.lstrip().startswith(("```", "~~~")):
            fence = not fence
            continue
        if fence:
            continue
        yield i + 1, re.sub(r"`[^`]*`", "", ln)


def scalar(doc, key):
    v = doc.fm.get(key)
    return v if isinstance(v, str) and v != "" else None


def check_frontmatter_syntax(doc, add):
    for n, code, msg in doc.errs:
        add(HARD, code, doc.rel, n, msg)


def check_page(doc, tree, add):
    rel = doc.rel
    if not SLUG_RE.match(stem(rel)):
        add(HARD, "FILENAME_CHARSET", rel, 0, "filename must match [a-z0-9-]+.md")
    if doc.fm is None:
        add(HARD, "FM_MISSING", rel, 1, "no frontmatter")
        return
    check_frontmatter_syntax(doc, add)
    fm = doc.fm
    for k in PAGE_REQUIRED:
        if not fm.get(k):
            add(HARD, "FM_FIELD_MISSING", rel, 0, "missing required field " + k)
    ptype = scalar(doc, "type")
    if ptype is not None and ptype not in PAGE_TYPES:
        add(HARD, "FM_TYPE", rel, doc.keyline.get("type", 0), "type must be tool, method or synthesis")
    parts = rel.split("/")
    if len(parts) == 3 and parts[1] in TYPE_SECTION.values() and ptype in TYPE_SECTION \
            and TYPE_SECTION[ptype] != parts[1]:
        add(HARD, "SECTION_TYPE", rel, 0, "type %s belongs in %s/ (archive/ takes any type)" % (ptype, TYPE_SECTION[ptype]))
    if (ptype == "tool") != bool(scalar(doc, "tool_version")):
        add(HARD, "FM_TOOL_VERSION", rel, 0, "tool_version required iff type is tool")
    status = scalar(doc, "status")
    if status is not None:
        line = doc.raw_line("status")
        if status not in ("draft", "live", "superseded"):
            add(HARD, "FM_STATUS_ENUM", rel, doc.keyline["status"], "status must be draft, live or superseded")
        elif not STATUS_LINE_RE.match(line):
            add(HARD, "FM_STATUS_FORM", rel, doc.keyline["status"], "status line must be canonical: 'status: <value>'")
    upd = scalar(doc, "updated")
    if upd is not None:
        if not ISO_RE.match(upd):
            add(HARD, "FM_UPDATED", rel, doc.keyline["updated"], "updated must be ISO with offset")
        elif not UPDATED_LINE_RE.match(doc.raw_line("updated")):
            add(HARD, "FM_UPDATED", rel, doc.keyline["updated"], "updated line must be canonical, unquoted")
    srcs = fm.get("sources")
    if srcs:
        if not isinstance(srcs, list):
            add(HARD, "SRC_FORM", rel, doc.keyline.get("sources", 0), "sources must be a block list")
        else:
            for s in srcs:
                slug, sep, loc = s.partition(" @ ")
                if not sep and s.endswith(" @"):  # trailing space was stripped: empty locator
                    slug, sep, loc = s[:-2], " @ ", ""
                if not sep or not slug.strip():
                    add(HARD, "SRC_FORM", rel, doc.keyline["sources"], "source entry must be '<raw-slug> @ <locator>'")
                elif slug.strip() not in tree.raw_slugs:
                    add(HARD, "SRC_UNRESOLVED", rel, doc.keyline["sources"], "source slug has no raw record: " + slug.strip())
                elif not loc.strip():
                    add(HARD, "SRC_LOCATOR", rel, doc.keyline["sources"], "empty locator for " + slug.strip())
    al = fm.get("aliases")
    if al is not None and not isinstance(al, list):
        add(HARD, "FM_ALIASES", rel, doc.keyline.get("aliases", 0), "aliases must be a block list")


def link_targets(tree):
    t = set()
    for d in tree.pages:
        t.add(fold(stem(d.rel)))
        if d.fm and isinstance(d.fm.get("aliases"), list):
            t.update(fold(a) for a in d.fm["aliases"] if a)
    return t


def check_links(doc, targets, add):
    for n, ln in body_lines(doc):
        for m in LINK_RE.finditer(ln):
            tgt = m.group(1).split("|")[0].split("#")[0].rstrip('\\').strip()
            if not tgt:
                continue
            t = tgt[:-3] if tgt.lower().endswith(".md") else tgt
            if t.lower().startswith("wiki/"):
                t = t[5:]
            if "/" in t or fold(t) not in targets:
                add(HARD, "LINK_DANGLING", doc.rel, n, "link target not in wiki/: [[" + tgt + "]]")


def check_raw(doc, add):
    rel = doc.rel
    if not RAW_NAME_RE.match(stem(rel)):
        add(HARD, "RAW_NAME", rel, 0, "raw filename must be YY-MM-DD-HHMM-<slug>.md (legacy YYYY-MM-DD-<slug>.md stays valid)")
    if doc.fm is None:
        add(HARD, "FM_MISSING", rel, 1, "no frontmatter")
        return
    check_frontmatter_syntax(doc, add)
    kind = scalar(doc, "source_kind")
    if kind not in RAW_KINDS:
        add(HARD, "RAW_ENUM", rel, doc.keyline.get("source_kind", 0), "source_kind must be web, pdf or book")
    if not any(scalar(doc, k) for k in ("url", "doi", "isbn")):
        add(HARD, "RAW_FIELD", rel, 0, "one of url, doi, isbn is required")
    for k in ("retrieved", "licence_note", "archive_status"):
        if not scalar(doc, k):
            add(HARD, "RAW_FIELD", rel, 0, "missing required field " + k)
    ret = scalar(doc, "retrieved")
    if ret and not ISO_RE.match(ret):
        add(HARD, "RAW_FIELD", rel, doc.keyline["retrieved"], "retrieved must be ISO with offset")
    arch = scalar(doc, "archive_status")
    if arch and arch not in ARCHIVE_STATUS:
        add(HARD, "RAW_ENUM", rel, doc.keyline["archive_status"], "archive_status must be saved, failed, excluded or none")
    rv = scalar(doc, "read_via")
    if kind == "web":
        if rv is None:
            add(HARD, "RAW_FIELD", rel, 0, "read_via is required for web")
        elif rv not in READ_VIA:
            add(HARD, "RAW_ENUM", rel, doc.keyline["read_via"], "read_via must be raw, extract, browser-render or pdf-text")
    vb = scalar(doc, "verify_by")
    if vb is not None and vb not in VERIFY_BY:
        add(HARD, "RAW_ENUM", rel, doc.keyline["verify_by"], "verify_by must be hash, locator+archive or none")
    if arch == "saved" and not (scalar(doc, "archive_url") and scalar(doc, "archive_timestamp")):
        add(HARD, "RAW_ARCHIVE", rel, 0, "archive_status saved needs archive_url and archive_timestamp")
    sha = scalar(doc, "body_sha256")
    if sha is not None and not SHA256_RE.match(sha):
        add(HARD, "RAW_FIELD", rel, doc.keyline["body_sha256"], "body_sha256 must be 64 lowercase hex")
    if kind == "web" and not (sha or scalar(doc, "archive_url")) and vb != "none":
        add(HARD, "RAW_ANCHOR", rel, 0, "web record has no re-find anchor; set verify_by: none")


def check_duplicates(tree, add):
    for label, docs in (("wiki", tree.pages), ("raw", tree.raws)):
        seen = {}
        for d in docs:
            seen.setdefault(fold(stem(d.rel)), []).append(d.rel)
        for paths in seen.values():
            if len(paths) > 1:
                add(HARD, "DUP_BASENAME", paths[1], 0, "duplicate basename in " + label + "/: " + ", ".join(paths))


def skill_docs(root):
    """Every .md file under skills/ as a Doc (non-.md files are flagged by check_skills)."""
    out = []
    base = os.path.join(root, "skills")
    for dirpath, dirs, files in os.walk(base):
        dirs.sort()
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            text = read_text(os.path.join(dirpath, name))
            if text is not None:
                out.append(Doc(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/"), text))
    return out


def check_skills(root, add):
    """skills/ is outside the wiki/raw rules but public: markdown only, no private detail."""
    base = os.path.join(root, "skills")
    for dirpath, dirs, files in os.walk(base):
        dirs.sort()
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if rel != "skills/README.md" and not SKILL_PATH_RE.match(rel):
                add(HARD, "SKILLS_FILE", rel, 0, "only skills/README.md, skills/<name>/SKILL.md and one level of lowercase skills/<name>/<file>.md belong under skills/")
    for d in skill_docs(root):
        for i, ln in enumerate(d.lines):
            for kind, rx in SKILL_PRIVATE_RES:
                if rx.search(ln):
                    add(HARD, "SKILLS_PRIVATE", d.rel, i + 1,
                        kind + " in skills/ (use a <placeholder>; value not printed)")


def scan_files(tree):
    """Docs scanned for secrets and deny keywords: wiki/, raw/, skills/ and AGENTS.md."""
    docs = tree.pages + tree.logs + tree.raws + skill_docs(tree.root)
    for rel in ("wiki/index.md", "AGENTS.md"):
        text = read_text(os.path.join(tree.root, rel))
        if text is not None:
            docs.append(Doc(rel, text))
    return docs


def check_secrets(doc, add):
    for i, ln in enumerate(doc.lines):
        for ok in ALLOWED_EXAMPLES:
            ln = ln.replace(ok, "")
        if any(r.search(ln) for r in SECRET_RES):
            add(HARD, "SECRET", doc.rel, i + 1, "secret-like token (value not printed)")


def load_deny(path):
    """Return list of folded keywords, or None if unreadable (fail closed)."""
    text = read_text(path)
    if text is None:
        return None
    return [fold(w.strip()) for w in text.split("\n") if w.strip() and not w.startswith("#")]


def check_deny(docs, words, add):
    for d in docs:
        if d.rel == "AGENTS.md":
            continue
        for i, ln in enumerate(d.lines):
            f = fold(ln)
            if any(w in f for w in words):
                add(HARD, "DENY_HIT", d.rel, i + 1, "deny-list keyword (not printed)")


# ---- 5c: WARN / INFO checks and the generated index ----------------------

INSTR_RES = tuple(re.compile(p, re.I) for p in (
    r"ignore\s+(all\s+|any\s+)?(previous|prior|above)",
    r"you\s+(must|should|will)\s",
    r"system\s+prompt",
    r"AGENTS\.md",
    r"do\s+not\s+tell",
    r"(curl|wget)[^\n]*\|\s*(sh|bash)",
))
IMPERATIVE_RE = re.compile(
    r"^\s*(?:[-*]\s+|\d+[.)]\s+)?(run|execute|send|post|delete|open|fetch|download|install|set|write)\b", re.I)
URL_RE = re.compile(r"https?://\S+", re.I)
STEPS_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")
STEPS_SRC_RE = re.compile(r"\(src: [a-z0-9-]+ @ [^)]+\)\s*$")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)(?:#[^)]*)?\)")
MAX_PAGE_LINES = 150
MAX_STEPS_LINES = 40


def steps_blocks(lines):
    """Return [(first, last)] 0-based inclusive line ranges AFTER each '## Steps' heading,
    ending before the next '#' or '##' heading or EOF (H6)."""
    out, i = [], 0
    while i < len(lines):
        if re.match(r"^##\s+Steps\s*$", lines[i]):
            j = i + 1
            while j < len(lines) and not re.match(r"^#{1,2}\s", lines[j]):
                j += 1
            out.append((i + 1, j - 1))
            i = j
        else:
            i += 1
    return out


def _line_count(doc):
    n = len(doc.lines)
    return n - 1 if n and doc.lines[-1] == "" else n


def _parse_iso(s):
    from datetime import datetime
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else None


def check_instructions(doc, is_method, add):
    """Warn-only heuristic over ALL lines; prints file:line only, never the matched text."""
    in_steps = set()
    if is_method:
        for a, b in steps_blocks(doc.lines):
            in_steps.update(range(a, b + 1))
    for i, ln in enumerate(doc.lines):
        steps = i in in_steps
        hit = any(r.search(ln) for r in INSTR_RES)
        hit = hit or (steps and URL_RE.search(ln) is not None)
        hit = hit or (not steps and IMPERATIVE_RE.match(ln) is not None)
        if hit:
            add(WARN, "INSTRUCTION", doc.rel, i + 1, "instruction-like line (heuristic; text not printed)")


def check_steps(doc, is_method, add):
    blocks = steps_blocks(doc.lines)
    if not blocks:
        return
    if not is_method:
        add(WARN, "STEPS_STRUCTURE", doc.rel, blocks[0][0], "## Steps is allowed on type: method pages only")
    if len(blocks) > 1:
        add(WARN, "STEPS_STRUCTURE", doc.rel, blocks[1][0], "more than one ## Steps block")
    a, b = blocks[0]
    if b - a + 1 > MAX_STEPS_LINES:
        add(WARN, "STEPS_STRUCTURE", doc.rel, a + 1, "Steps block longer than %d lines" % MAX_STEPS_LINES)
    for i in range(a, b + 1):
        ln = doc.lines[i]
        if STEPS_ITEM_RE.match(ln) and not STEPS_SRC_RE.search(ln):
            add(WARN, "STEPS_NO_SRC", doc.rel, i + 1, "Steps item without (src: <raw-slug> @ ...)")


def check_warnings(tree, add, deny_given):
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc) + timedelta(minutes=5)
    slugs = {stem(d.rel) for d in tree.pages}
    seen = {}
    for d in tree.pages:
        fm = d.fm or {}
        is_method = fm.get("type") == "method"
        check_instructions(d, is_method, add)
        check_steps(d, is_method, add)
        srcs = fm.get("sources") if isinstance(fm.get("sources"), list) else []
        tv = fm.get("tool_version")
        has_releases = any(x.partition(" @ ")[2].strip().lower() == "releases" for x in srcs)
        if fm.get("type") == "tool" and isinstance(tv, str) and tv != "hosted-service" and not has_releases:
            add(WARN, "RELEASES_SOURCE", d.rel, d.keyline.get("tool_version", 0),
                "tool_version needs a source with locator 'releases' (or tool_version: hosted-service)")
        if _line_count(d) > MAX_PAGE_LINES:
            add(WARN, "PAGE_LONG", d.rel, 0, "page longer than %d lines (limit comes from pilot data)" % MAX_PAGE_LINES)
        upd = _parse_iso(fm.get("updated", "")) if isinstance(fm.get("updated"), str) else None
        if upd is not None and upd > now:
            add(WARN, "DATE_FUTURE", d.rel, d.keyline.get("updated", 0), "updated is in the future")
        for n, ln in body_lines(d):
            for m in MDLINK_RE.finditer(ln):
                if "://" not in m.group(1) and os.path.basename(m.group(1))[:-3] in slugs:
                    add(WARN, "MDLINK_TO_WIKI", d.rel, n, "use [[slug]] wikilinks, not [text](x.md)")
        names = [fm.get("title")] + (fm.get("aliases") if isinstance(fm.get("aliases"), list) else [])
        for nm in names:
            if isinstance(nm, str) and nm:
                seen.setdefault(fold(nm), set()).add(d.rel)
    for rels in seen.values():
        if len(rels) > 1:
            add(WARN, "DUP_TITLE_ALIAS", sorted(rels)[1], 0, "title/alias shared by: " + ", ".join(sorted(rels)))
    for d in tree.logs:
        check_instructions(d, False, add)
    for d in tree.raws:
        fm = d.fm or {}
        check_instructions(d, False, add)
        for n, ln in body_lines(d):
            if LINK_RE.search(ln):
                add(WARN, "RAW_WIKILINK", d.rel, n, "wikilink in a raw record body")
        ret = fm.get("retrieved") if isinstance(fm.get("retrieved"), str) else None
        if ret:
            base = os.path.basename(d.rel)
            m = RAW_NEW_RE.match(base)
            if m:
                name_date, name_hm = "20%s-%s-%s" % m.group(1, 2, 3), m.group(4)
            else:
                name_date, name_hm = base[:10], None
            if name_date != ret[:10] or (name_hm is not None and ret[11:13] + ret[14:16] != name_hm):
                add(WARN, "RAW_DATE_MISMATCH", d.rel, 0, "filename date or time differs from retrieved")
            r = _parse_iso(ret)
            if r is not None and r > now:
                add(WARN, "DATE_FUTURE", d.rel, d.keyline.get("retrieved", 0), "retrieved is in the future")
        if fm.get("body_sha256") and fm.get("read_via") != "raw" and fm.get("source_kind") == "web":
            add(WARN, "HASH_WITHOUT_RAW", d.rel, 0, "body_sha256 present but read_via is not raw (web record)")
    idx = read_text(os.path.join(tree.root, "wiki", "index.md"))
    if idx is not None:
        check_instructions(Doc("wiki/index.md", idx), False, add)
    if idx != build_index(tree) and (tree.pages or idx is not None):
        add(INFO, "INDEX_STALE", "wiki/index.md", 0, "index differs from generated output (never fails)")
    if not deny_given:
        add(WARN, "DENY_SKIPPED", "-", 0, "no local deny file given: personal names and handles are not checked (pass --deny-file)")


_ESC_DROP = set("[]()<>!|`" + chr(92))


def _esc(s):
    """Index text from untrusted frontmatter: drop markdown/HTML syntax, control and bidi characters."""
    import unicodedata
    out = []
    for ch in s:
        if ch in _ESC_DROP or unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp"):
            out.append(" " if ch in "\r\n\t" else "")
        else:
            out.append(ch)
    return " ".join("".join(out).split()).lstrip("#>").strip()[:120]


def build_index(tree):
    """Deterministic index: grouped by type/status, sorted by slug, LF, no timestamp."""
    order = ("tool", "method", "synthesis", "draft", "superseded", "unclassified", "archive")
    groups = {g: [] for g in order}
    for d in tree.pages:
        fm, slug = d.fm or {}, stem(d.rel)
        status = fm.get("status") if isinstance(fm.get("status"), str) else None
        ptype = fm.get("type") if isinstance(fm.get("type"), str) else None
        title = (_esc(fm["title"]) if isinstance(fm.get("title"), str) else "") or slug
        al = [_esc(a) for a in fm.get("aliases", []) if isinstance(fm.get("aliases"), list) and a]
        line = "- [[%s]]: %s" % (slug, title) + (" (aliases: %s)" % " | ".join(al) if al else "")
        if d.rel.startswith("wiki/archive/"):
            g = "archive"
        elif status == "draft":
            g = "draft"
        elif status == "superseded":
            g = "superseded"
        elif status == "live" and ptype in PAGE_TYPES:
            g = ptype
        else:
            g = "unclassified"
        groups[g].append((slug, line))
    out = ["# Index", "", "Generated by `scripts/lint.py --index`. Hand edits are overwritten and rejected in review.", ""]
    for g in order:
        if groups[g]:
            out += ["## " + g, ""] + [ln for _, ln in sorted(groups[g])] + [""]
    return "\n".join(out).rstrip("\n") + "\n"


def run_checks(root, deny_file=None):
    tree = Tree(root)
    out = list(tree.findings)

    def add(level, code, path, line, msg):
        out.append(Finding(level, code, path, line, msg))

    targets = link_targets(tree)
    for d in tree.pages:
        check_page(d, tree, add)
        check_links(d, targets, add)
    for d in tree.logs:
        check_links(d, targets, add)
    idx_text = read_text(os.path.join(tree.root, "wiki", "index.md"))
    if idx_text is not None:
        check_links(Doc("wiki/index.md", idx_text), targets, add)
    for d in tree.raws:
        check_raw(d, add)
    check_duplicates(tree, add)
    check_skills(tree.root, add)
    docs = scan_files(tree)
    for d in docs:
        check_secrets(d, add)
    if deny_file is not None:
        words = load_deny(deny_file)
        if words is None:
            add(HARD, "DENY_FILE", str(deny_file), 0, "deny file unreadable (fail closed)")
        else:
            check_deny(docs, words, add)
    check_warnings(tree, add, deny_file is not None)
    return sorted(out, key=lambda f: (_ORDER[f.level], f.path, f.line, f.code))


def report(findings):
    for f in findings:
        loc = f.path + (":" + str(f.line) if f.line else "")
        print("%s %s %s %s" % (f.level, f.code, loc, f.msg))
    hard = sum(1 for f in findings if f.level == HARD)
    print("lint: %d HARD, %d WARN, %d INFO" % (hard, sum(f.level == WARN for f in findings),
                                              sum(f.level == INFO for f in findings)))
    return 1 if hard else 0


# ---- selftest -------------------------------------------------------------

_TOKENS = {  # fake secrets are built at runtime, never stored as literals
    "@@AKIA@@": "AKIA" + "QWERTYUIOPASDFGH",
    "@@GHP@@": "ghp_" + "a" * 30,
    "@@SK@@": "sk-" + "b" * 30,
    "@@PEM@@": "-----BEGIN RSA PRIVATE" + " KEY-----",
    "@@AKIA_EXAMPLE@@": "AKIA" + "IOSFODNN7EXAMPLE",
}


def _materialise(src, dst):
    shutil.copytree(src, dst)
    for dp, _, files in os.walk(dst):
        for name in files:
            p = os.path.join(dp, name)
            text = read_text(p)
            if text and "@@" in text:
                for k, v in _TOKENS.items():
                    text = text.replace(k, v)
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text)


def _expect(path):
    exp = {"exit": 0, "hard": set(), "warn": None}  # warn: exact WARN set, asserted only if given
    for ln in (read_text(path) or "").split("\n"):
        k, _, v = ln.partition(":")
        if k.strip() == "exit":
            exp["exit"] = int(v)
        elif k.strip() == "hard":
            exp["hard"] = set(v.split())
        elif k.strip() == "warn":
            exp["warn"] = set(v.split())
    return exp


def run_selftest():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "lint")
    if not os.path.isdir(base):
        print("selftest: no fixtures at " + base)
        return 2
    failed = total = 0
    for case in sorted(os.listdir(base)):
        cdir = os.path.join(base, case)
        if not os.path.isdir(os.path.join(cdir, "tree")):
            continue
        total += 1
        exp = _expect(os.path.join(cdir, "expect.txt"))
        tmp = tempfile.mkdtemp(prefix="lintfix-")
        try:
            work = os.path.join(tmp, "tree")
            _materialise(os.path.join(cdir, "tree"), work)
            deny = os.path.join(cdir, "deny.txt")
            if os.path.exists(os.path.join(cdir, "deny-missing")):
                deny = os.path.join(tmp, "no-such-file.txt")
            elif not os.path.exists(deny):
                deny = None
            fs = run_checks(work, deny)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        hard = {f.code for f in fs if f.level == HARD}
        code = 1 if hard else 0
        warn = {f.code for f in fs if f.level == WARN}
        ok = code == exp["exit"] and hard == exp["hard"] and (exp["warn"] is None or warn == exp["warn"])
        failed += 0 if ok else 1
        print("%s %s (exit %d, HARD %s)" % ("PASS" if ok else "FAIL", case, code, " ".join(sorted(hard)) or "-"))
        if not ok:
            print("     expected exit %d, HARD %s, WARN %s (got WARN %s)" % (
                exp["exit"], " ".join(sorted(exp["hard"])) or "-",
                " ".join(sorted(exp["warn"])) if exp["warn"] is not None else "(any)",
                " ".join(sorted(warn)) or "-"))
    esc_cases = (
        ("![x](https://evil.example/p.png)", "xhttps://evil.example/p.png"),
        ("<img src=x onerror=1>", "img src=x onerror=1"),
        ("a | b", "a b"),
        ("evil" + chr(0x202E) + "title", "eviltitle"),
        ("# Heading [[link]]", "Heading link"),
    )
    for raw_in, want in esc_cases:
        total += 1
        got = _esc(raw_in)
        ok = got == want
        failed += 0 if ok else 1
        print("%s _esc %r -> %r" % ("PASS" if ok else "FAIL", raw_in, got))
    total += 1
    tdir = tempfile.mkdtemp(prefix="lintidx-")
    try:
        os.makedirs(os.path.join(tdir, "wiki"))
        nl = chr(10)
        page = nl.join(["---", 'title: "[]()"', "type: tool", "status: draft", "---", "body", ""])
        with open(os.path.join(tdir, "wiki", "empty-title.md"), "w", encoding="utf-8", newline=nl) as fh:
            fh.write(page)
        ok = "- [[empty-title]]: empty-title" in build_index(Tree(tdir)).split(nl)
    finally:
        shutil.rmtree(tdir, ignore_errors=True)
    failed += 0 if ok else 1
    print("%s index title of only dropped characters falls back to slug" % ("PASS" if ok else "FAIL"))
    print("selftest: %d/%d passed" % (total - failed, total))
    return 1 if failed or total == 0 else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="offline content lint for the wiki")
    ap.add_argument("--root", default=".")
    ap.add_argument("--deny-file")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--index", action="store_true", help="generate wiki/index.md")
    ap.add_argument("--stdout", action="store_true", help="with --index: print instead of writing")
    args = ap.parse_args(argv)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if args.selftest:
            return run_selftest()
        if not os.path.isdir(args.root):
            print("lint: root not found: " + args.root, file=sys.stderr)
            return 2
        if args.index:
            data = build_index(Tree(args.root)).encode("utf-8")
            if args.stdout:
                sys.stdout.buffer.write(data)  # bytes: LF stays LF on Windows
                sys.stdout.buffer.flush()
            else:
                with open(os.path.join(args.root, "wiki", "index.md"), "wb") as f:
                    f.write(data)
            return 0
        return report(run_checks(args.root, args.deny_file))
    except Exception as e:  # internal error: fail closed with exit 2
        print("lint: internal error: %r" % (e,), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
