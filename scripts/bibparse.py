"""Minimal BibTeX reader (no external dependencies).

Handles nested braces and quoted values well enough for the survey's refs.bib.
"""
import re
import unicodedata

_ACCENTS = {'"': "̈", "'": "́", "`": "̀", "^": "̂", "~": "̃", "=": "̄", ".": "̇"}
_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.S)


def _read_value(text, i):
    """Read a field value starting at index i; return (value, next_index)."""
    while text[i].isspace():
        i += 1
    if text[i] == "{":
        depth, j = 0, i
        while True:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return text[i + 1 : j], j + 1
            j += 1
    if text[i] == '"':
        j = i + 1
        while text[j] != '"' or text[j - 1] == "\\":
            j += 1
        return text[i + 1 : j], j + 1
    m = re.match(r"[^,}\s]+", text[i:])
    return m.group(0), i + m.end()


def parse(text):
    entries = []
    for m in _ENTRY_RE.finditer(text):
        etype, key = m.group(1).lower(), m.group(2)
        if etype in ("comment", "string", "preamble"):
            continue
        i = m.end()
        fields = {}
        while True:
            fm = re.compile(r"\s*([A-Za-z_-]+)\s*=\s*").match(text, i)
            if not fm:
                break
            value, i = _read_value(text, fm.end())
            fields[fm.group(1).lower()] = " ".join(value.split())
            sep = re.compile(r"\s*,?").match(text, i)
            i = sep.end()
        entries.append({"type": etype, "key": key, **fields})
    return entries


def clean(s):
    """Strip TeX markup for display."""
    if not s:
        return s
    s = re.sub(
        r'\{?\\(["\'`^~=.])\{?([A-Za-z])\}?\}?',
        lambda m: unicodedata.normalize("NFC", m.group(2) + _ACCENTS[m.group(1)]),
        s,
    )
    s = s.replace("\\&", "&").replace("--", "–").replace("~", " ")
    s = re.sub(r"\\textit\{([^}]*)\}|\\emph\{([^}]*)\}", lambda m: m.group(1) or m.group(2), s)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    s = s.replace("{", "").replace("}", "").replace("$", "")
    return " ".join(s.split())
