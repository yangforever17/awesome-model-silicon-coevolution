"""Build README.md and data/catalog.csv from the curated data files.

Inputs (all under data/):
  refs.bib        bibliography of the companion survey (titles, venues, years)
  taxonomy.yaml   parts, topics, levels, edges and badge colors
  papers.yaml     per-entry topic, level, type and note
  resolved.json   arXiv / DOI matches produced by resolve_links.py
  readme/*.md     hand-written README sections, spliced in by name

Usage:
  python scripts/build_readme.py           # write README.md and data/catalog.csv
  python scripts/build_readme.py --check   # exit 1 if either file is out of date
"""
import collections
import csv
import io
import json
import os
import re
import sys
import urllib.parse

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from bibparse import clean, parse  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

ARXIV_MIN_SIM = 0.92
DOI_MIN_SIM = 0.93
# Entries whose automatic matches are known to be wrong (same title, different work).
NO_AUTO_LINK_TYPES = {"Essay", "Book"}

EXTRA_LEVEL_COLORS = {"L1–L2": "4f46e5", "Human": "78716c", "Claimed": "a8a29e", "Undisclosed": "a8a29e"}
LEVEL_LABELS = {"Human": "Human-driven", "Claimed": "Claimed", "Undisclosed": "Undisclosed"}

VENUE_ABBR = {
    "ACM Transactions on Design Automation of Electronic Systems": "TODAES",
    "IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems": "TCAD",
    "IEEE Transactions on Computers": "TC",
    "IEEE Transactions on Evolutionary Computation": "TEVC",
    "Communications of the ACM": "CACM",
    "Journal of Machine Learning Research": "JMLR",
    "Transactions on Machine Learning Research": "TMLR",
    "Proceedings of the IEEE": "Proc. IEEE",
    "AAAI Conference on Artificial Intelligence": "AAAI",
    "International Conference on Computer-Aided Design (ICCAD) Contest": "ICCAD Contest",
    "International Symposium on Computer Architecture (ISCA), Industry Track": "ISCA Industry",
    "Findings of the Association for Computational Linguistics: NAACL": "Findings of NAACL",
    "IEEE Journal of Solid-State Circuits": "JSSC",
    "IEEE Circuits and Systems Magazine": "IEEE CAS Magazine",
}


GITHUB = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?/?$")


# --------------------------------------------------------------------------- data


def load():
    bib = {e["key"]: e for e in parse(open(os.path.join(DATA, "refs.bib"), encoding="utf-8").read())}
    tax = yaml.safe_load(open(os.path.join(DATA, "taxonomy.yaml"), encoding="utf-8"))
    ann = yaml.safe_load(open(os.path.join(DATA, "papers.yaml"), encoding="utf-8"))
    res_path = os.path.join(DATA, "resolved.json")
    res = json.load(open(res_path, encoding="utf-8")) if os.path.exists(res_path) else {}
    return bib, tax, ann, res


def venue_of(e):
    raw = clean(
        e.get("booktitle") or e.get("journal") or e.get("howpublished") or e.get("publisher") or e.get("institution") or ""
    )
    if raw in VENUE_ABBR:
        return VENUE_ABBR[raw]
    if raw.lower().startswith("arxiv") or not raw:
        return "arXiv" if raw else ""
    if raw.startswith("http"):
        return "Website"
    if raw.startswith("TODO"):
        return ""
    m = re.search(r"\(([A-Za-z][A-Za-z0-9 .&-]*)\)$", raw)
    return m.group(1) if m else raw


def first_author(e):
    raw = e.get("author", "").strip()
    if not raw or "TODO" in raw:
        return ""
    names = [n.strip() for n in re.split(r"\s+and\s+", raw)]
    if all(n.startswith("{") and n.endswith("}") for n in names if n != "others"):
        # Corporate authors such as {DeepSeek-AI} or {OpenAI} and {Broadcom}.
        return " & ".join(clean(n) for n in names if n != "others")
    first = clean(names[0])
    surname = first.split(",")[0].strip() if "," in first else first.split()[-1]
    return f"{surname} et al." if len(names) > 1 else surname


def arxiv_from_bib(e):
    for f in ("url", "howpublished", "note", "journal", "eprint"):
        m = re.search(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:\s*|arXiv preprint )((?:\d{4}\.\d{4,5})|(?:[a-z-]+/\d{7}))", e.get(f, ""))
        if m:
            return m.group(1)
    return None


def links_for(key, e, a, r):
    """Return ordered list of (label, url) and the arXiv id, preferring curated sources."""
    links = []
    if a.get("url"):
        links.append(("Link", a["url"]))
    arxiv = a.get("arxiv") or arxiv_from_bib(e)
    rx = (r or {}).get("arxiv")
    auto_ok = a.get("type", "Paper") not in NO_AUTO_LINK_TYPES and not a.get("no_auto_link")
    if not arxiv and auto_ok and rx and rx["sim"] >= ARXIV_MIN_SIM:
        arxiv = rx["id"]
    if arxiv and not a.get("no_arxiv"):
        links.append(("arXiv", f"https://arxiv.org/abs/{arxiv}"))
    doi = a.get("doi")
    rc = (r or {}).get("crossref")
    if not doi and auto_ok and rc and rc["sim"] >= DOI_MIN_SIM and not str(rc["doi"]).lower().startswith("10.48550/arxiv"):
        try:
            year_ok = rc.get("year") is None or abs(int(rc["year"]) - int(e.get("year", 0))) <= 2
        except ValueError:
            year_ok = True
        if year_ok:
            doi = rc["doi"]
    if doi and not a.get("no_doi"):
        links.append(("DOI", f"https://doi.org/{doi}"))
    m = re.search(r"https?://[^\s{}]+", e.get("howpublished", ""))
    bib_url = e.get("url") or (m.group(0) if m else "")
    if bib_url and not a.get("url") and "arxiv.org" not in bib_url and not a.get("ignore_bib_url"):
        links.append(("Link", bib_url))
    seen, out = set(), []
    for lab, u in links:
        if u not in seen:
            seen.add(u)
            out.append((lab, u))
    return out, arxiv, doi


def build_entries(bib, tax, ann, res):
    part_of, topic_meta = {}, {}
    for p in tax["parts"]:
        for t in p["topics"]:
            part_of[t["id"]] = p
            topic_meta[t["id"]] = t
    entries = []
    for key, e in bib.items():
        a = ann[key]
        p = part_of[a["topic"]]
        links, arxiv, doi = links_for(key, e, a, res.get(key))
        entries.append(
            {
                "key": key,
                "title": a.get("title_en") or clean(e.get("title", "")),
                "title_orig": clean(e.get("title", "")) if a.get("title_en") else "",
                "authors": first_author(e),
                "year": e.get("year", ""),
                "venue": venue_of(e),
                "part": p["id"],
                "topic": a["topic"],
                "edge": a.get("edge") or topic_meta[a["topic"]].get("edge") or p.get("edge"),
                "type": a.get("type", "Paper"),
                "level": a.get("level"),
                "lsrc": a.get("lsrc"),
                "featured": bool(a.get("featured")),
                "short": a.get("short"),
                "note": a.get("note", ""),
                "links": links,
                "code": a.get("code") or next((m.group(1) for _, u in links for m in [GITHUB.match(u)] if m), None),
                "arxiv": arxiv,
                "doi": doi,
                "section": e.get("section", ""),
                "verified": e.get("verified", ""),
            }
        )
    return entries


# --------------------------------------------------------------------------- rendering


def badge(label, color):
    text = label.replace("-", "--").replace("_", "__").replace(" ", "_")
    return f"![{label}](https://img.shields.io/badge/-{urllib.parse.quote(text, safe='_-.')}-{color}?style=flat-square)"


def level_color(tax, level):
    return tax["levels"][level]["color"] if level in tax["levels"] else EXTRA_LEVEL_COLORS[level]


def level_badge(tax, x):
    if not x["level"]:
        return ""
    dagger = " †" if x["lsrc"] == "curator" else ""
    return badge(LEVEL_LABELS.get(x["level"], x["level"]), level_color(tax, x["level"])) + dagger


def anchor(text):
    """GitHub heading anchor."""
    a = text.strip().lower()
    a = re.sub(r"[^\w\- ]", "", a)
    return a.replace(" ", "-")


def cell(s):
    return s.replace("|", "\\|")


def short_name(title):
    m = re.match(r"^([^:]{2,40}):", title)
    return m.group(1) if m else title


def tidy_note(x):
    """Drop a leading 'Name:' that repeats the work's own name, since the title sits in the same row."""
    note = x["note"]
    for name in filter(None, (x["short"], short_name(x["title"]))):
        m = re.match(re.escape(name) + r"\s*:\s+", note)
        if m:
            rest = note[m.end():]
            return rest[:1].upper() + rest[1:]
    return note


def venue_cell(x, url=None):
    venue = x["venue"] if x["venue"] not in ("", "Website") else ("" if x["type"] == "Paper" else x["type"])
    text = "&nbsp;".join(cell(s) for s in (venue, x["year"]) if s)
    return f"[{text}]({url})" if url and text else text


def entry_row(tax, x, with_level):
    title = cell(x["title"]) + (f" ({cell(x['title_orig'])})" if x["title_orig"] else "")
    # The title links to the primary source and the venue to the second (usually the DOI).
    links = [u for _, u in x["links"]]
    if links:
        title = f"[{title}]({links[0]})" + "".join(f" [[{lab}]({u})]" for lab, u in x["links"][2:])
    if x["code"]:
        stars = f"https://img.shields.io/github/stars/{x['code']}?style=social&label=Code"
        title += f" [![Code]({stars})](https://github.com/{x['code']})"
    star = "⭐ " if x["featured"] else ""
    cols = [star + title, venue_cell(x, links[1] if len(links) > 1 else None)]
    if with_level:
        cols.append(level_badge(tax, x))
    cols.append(cell(tidy_note(x)))
    return "| " + " | ".join(cols) + " |"


def entry_table(tax, xs):
    with_level = any(x["level"] for x in xs)
    head = ["Work", "Venue"] + (["Level"] if with_level else []) + ["Note"]
    align = [":---", ":---"] + ([":---:"] if with_level else []) + [":---"]
    rows = ["| " + " | ".join(head) + " |", "| " + " | ".join(align) + " |"]
    return "\n".join(rows + [entry_row(tax, x, with_level) for x in xs])


def sort_key(x):
    try:
        y = int(x["year"])
    except ValueError:
        y = 9999
    return (y, x["title"].lower())


def render_part(tax, p, number, entries):
    xs = [x for x in entries if x["part"] == p["id"]]
    out = [
        f'<a id="part-{p["id"]}"></a>',
        "",
        f"## {number}. {p['title']}",
        "",
        f"{p['blurb'].strip()} <sub>Survey {p['survey']} · {len(xs)} entries</sub>",
        "",
    ]
    topics = [t for t in p["topics"] if any(x["topic"] == t["id"] for x in xs)]
    if len(topics) > 1:
        out += [
            "> " + " · ".join(
                f"[{t['title']}](#{anchor(t['title'])}) {sum(1 for x in xs if x['topic'] == t['id'])}" for t in topics
            ),
            "",
        ]
    for t in topics:
        ts = sorted((x for x in xs if x["topic"] == t["id"]), key=sort_key)
        if len(topics) > 1:
            out += [f"### {t['title']}", ""]
        if t.get("fold"):
            years = sorted(x["year"] for x in ts if x["year"].isdigit())
            span = f" · {years[0]}–{years[-1]}" if years else ""
            out += ["<details>", f"<summary>Show {len(ts)} entries{span}</summary>", "", entry_table(tax, ts), "", "</details>", ""]
        else:
            out += [entry_table(tax, ts), ""]
    out += ['<p align="right"><sub><a href="#contents">↑ Contents</a></sub></p>', ""]
    return "\n".join(out)


def snippet(name):
    return open(os.path.join(DATA, "readme", f"{name}.md"), encoding="utf-8").read().strip() + "\n"


def stats(entries):
    n = len(entries)
    linked = sum(1 for x in entries if x["links"])
    return {
        "n": n,
        "arxiv": sum(1 for x in entries if x["arxiv"]),
        "doi": sum(1 for x in entries if x["doi"]),
        "linked": linked,
        "unlinked": [x for x in entries if not x["links"]],
        "lv_survey": sum(1 for x in entries if x["level"] and x["lsrc"] == "survey"),
        "lv_curator": sum(1 for x in entries if x["level"] and x["lsrc"] == "curator"),
        "verified": sum(1 for x in entries if x["verified"] == "yes"),
    }


def fill(text, values):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


def render(bib, tax, ann, res):
    entries = build_entries(bib, tax, ann, res)
    st = stats(entries)
    parts = tax["parts"]
    numbered = list(enumerate(parts, 1))

    lvl_counts = collections.Counter(x["level"] for x in entries if x["level"])
    level_rows = ["| Level | Name | Decision rule | Entries |", "| :---: | --- | --- | ---: |"]
    for k, v in tax["levels"].items():
        level_rows.append(f"| {badge(k, v['color'])} | {v['name']} | {v['rule']} | {lvl_counts.get(k, 0) or '—'} |")

    contents = ["| | Part | Entries | Survey |", "| ---: | --- | ---: | --- |"]
    for i, p in numbered:
        n = sum(1 for x in entries if x["part"] == p["id"])
        contents.append(f"| {i} | [{p['title']}](#part-{p['id']}) | {n} | {p['survey']} |")

    legend = " ".join(badge(k, v["color"]) for k, v in tax["levels"].items() if k in lvl_counts)
    legend += " " + " ".join(badge(LEVEL_LABELS[k], EXTRA_LEVEL_COLORS[k]) for k in ("Human", "Claimed", "Undisclosed"))

    values = {
        "N": st["n"],
        "ARXIV": st["arxiv"],
        "DOI": st["doi"],
        "LINKED": st["linked"],
        "UNLINKED_N": len(st["unlinked"]),
        "UNLINKED": ", ".join(f"`{x['key']}`" for x in st["unlinked"]) or "none",
        "LV_SURVEY": st["lv_survey"],
        "LV_CURATOR": st["lv_curator"],
        "VERIFIED": st["verified"],
        "LEVEL_TABLE": "\n".join(level_rows),
        "CONTENTS": "\n".join(contents),
        "LEGEND": legend,
    }
    body = [fill(snippet(name), values) for name in ("header", "intro", "news", "catalog", "whynow", "framework", "legend")]
    for i, p in numbered:
        part_md = render_part(tax, p, i, entries)
        if p["id"] == "cases":
            # The case table already summarizes each case; keep the source list folded.
            head, _, rest = part_md.partition("| Work |")
            part_md = head + snippet("cases-table") + "\n<details>\n<summary>Sources</summary>\n\n| Work |" + rest.rstrip() + "\n\n</details>\n"
        body.append(part_md)
    body += [fill(snippet(name), values) for name in ("survey", "contributing")]
    readme = "\n".join(body).rstrip() + "\n"
    readme = re.sub(r"\n{3,}", "\n\n", readme)

    buf = io.StringIO()
    cols = ["key", "title", "authors", "year", "venue", "part", "topic", "edge", "type", "level", "level_source", "arxiv", "doi", "code", "links", "note"]
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for x in sorted(entries, key=lambda x: (x["part"], x["topic"], sort_key(x))):
        w.writerow(
            {
                **{c: x.get(c, "") for c in cols},
                "level": x["level"] or "",
                "level_source": x["lsrc"] or "",
                "arxiv": x["arxiv"] or "",
                "doi": x["doi"] or "",
                "code": f"https://github.com/{x['code']}" if x["code"] else "",
                "links": " ".join(u for _, u in x["links"]),
            }
        )
    return readme, buf.getvalue()


def main():
    readme, catalog = render(*load())
    targets = {os.path.join(ROOT, "README.md"): readme, os.path.join(DATA, "catalog.csv"): catalog}
    if "--check" in sys.argv:
        stale = [p for p, c in targets.items() if not os.path.exists(p) or open(p, encoding="utf-8").read() != c]
        if stale:
            print("Out of date (run python scripts/build_readme.py):", *stale, sep="\n  ")
            sys.exit(1)
        print("README.md and catalog.csv are up to date.")
        return
    for p, c in targets.items():
        open(p, "w", encoding="utf-8").write(c)
    print("Wrote", *targets, sep="\n  ")


if __name__ == "__main__":
    main()
