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

LEVEL_ORDER = ["L0", "L1", "L1–L2", "L2", "L3", "L4", "Human", "Claimed", "Undisclosed"]
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
    return f"![](https://img.shields.io/badge/-{urllib.parse.quote(text, safe='_-.')}-{color})"


def level_color(tax, level):
    return tax["levels"][level]["color"] if level in tax["levels"] else EXTRA_LEVEL_COLORS[level]


def anchor(text):
    """GitHub heading anchor."""
    a = text.strip().lower()
    a = re.sub(r"[^\w\- ]", "", a)
    return a.replace(" ", "-")


def entry_md(tax, x):
    link_md = " ".join(f"[[{lab}]({u})]" for lab, u in x["links"])
    if not link_md:
        link_md = "" if x["type"] == "Book" else "_link pending_"
    meta = " · ".join(s for s in (x["authors"], " ".join(s for s in (x["venue"], x["year"]) if s)) if s)
    badges = []
    if x["level"]:
        lab = LEVEL_LABELS.get(x["level"], f"Level-{x['level']}")
        badges.append(badge(lab, level_color(tax, x["level"])))
    if x["edge"]:
        ed = tax["edges"][x["edge"]]
        badges.append(badge(ed["label"], ed["color"]))
    badges.append(badge(x["type"], tax["types"][x["type"]]))
    dagger = " †" if x["lsrc"] == "curator" else ""
    orig = f" ({x['title_orig']})" if x["title_orig"] else ""
    lines = [
        f"1. **{x['title']}**{orig}  ",
        "   " + " · ".join(s for s in (link_md, meta) if s) + "  ",
        f"   {' '.join(badges)}  ",
    ]
    if x["note"]:
        lines.append(f"   {x['note']}{dagger}")
    else:
        lines[-1] = lines[-1].rstrip()
    return "\n".join(lines)


def first_link(x):
    return x["links"][0][1] if x["links"] else None


def short_name(title):
    m = re.match(r"^([^:]{2,40}):", title)
    return m.group(1) if m else title


def featured_table(tax, xs):
    rows = ["| Work | Level | Why it matters |", "| --- | :---: | --- |"]
    for x in xs:
        name = x["short"] or short_name(x["title"])
        u = first_link(x)
        cell = f"[{name}]({u})" if u else name
        lvl = ""
        if x["level"]:
            lvl = LEVEL_LABELS.get(x["level"], x["level"]) + (" †" if x["lsrc"] == "curator" else "")
        rows.append(f"| {cell} ({x['year']}) | {lvl} | {x['note']} |")
    return "\n".join(rows)


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
        f"## {number}. {p['title']} <sub><a href=\"#readme-top\">↑ top</a></sub>",
        "",
        f"{p['blurb'].strip()} *Survey: {p['survey']}.* **{len(xs)} entries.**",
        "",
    ]
    feat = sorted((x for x in xs if x["featured"]), key=sort_key)
    if feat and p["id"] != "cases":
        out += ["### Featured", "", featured_table(tax, feat), ""]
    topics = p["topics"]
    if len(topics) > 1:
        out.append(
            "Topics: "
            + " · ".join(
                f"[{t['title']}](#{anchor(t['title'] + ' ' + str(sum(1 for x in xs if x['topic'] == t['id'])))})"
                for t in topics
            )
        )
        out.append("")
    for t in topics:
        ts = sorted((x for x in xs if x["topic"] == t["id"]), key=sort_key)
        if not ts:
            continue
        if len(topics) > 1:
            out += [f"### {t['title']} ({len(ts)})", ""]
        noun = "entry" if len(ts) == 1 else "entries"
        out += ["<details>", f"<summary>Show {len(ts)} {noun}</summary>", ""]
        out += [entry_md(tax, x) for x in ts]
        out += ["", "</details>", ""]
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


def render(bib, tax, ann, res):
    entries = build_entries(bib, tax, ann, res)
    st = stats(entries)
    parts = tax["parts"]
    numbered = list(enumerate(parts, 1))

    glance = ["| # | Part | Survey | Entries | Levels present |", "| ---: | --- | --- | ---: | --- |"]
    for i, p in numbered:
        xs = [x for x in entries if x["part"] == p["id"]]
        lv = collections.Counter(x["level"] for x in xs if x["level"])
        lv_s = ", ".join(f"{LEVEL_LABELS.get(k, k)} ×{lv[k]}" for k in LEVEL_ORDER if k in lv) or "—"
        glance.append(f"| {i} | [{p['title']}](#part-{p['id']}) | {p['survey']} | {len(xs)} | {lv_s} |")

    lvl_counts = collections.Counter(x["level"] for x in entries if x["level"])
    level_rows = ["| Level | Name | Decision rule | Entries |", "| --- | --- | --- | ---: |"]
    for k, v in tax["levels"].items():
        level_rows.append(f"| {badge(k, v['color'])} | {v['name']} | {v['rule']} | {lvl_counts.get(k, 0) or '—'} |")

    toc = [
        "- [Start Here](#start-here)",
        "- [Latest Updates](#latest-updates)",
        "- [Companion Survey](#companion-survey)",
        "- [Why Now: Intelligence Is Climbing Toward RSI](#why-now)",
        "- [The Framework: Layers, Levels, Signals](#the-framework)",
        "- [Where the Loop Breaks](#where-the-loop-breaks)",
        "- [How to Read the Tags](#how-to-read-the-tags)",
        "- [Catalog at a Glance](#catalog-at-a-glance)",
    ]
    toc += [f"- [{i}. {p['title']}](#part-{p['id']})" for i, p in numbered]
    toc += ["- [Contributing](#contributing)", "- [Citation](#citation)", "- [Data Provenance and Validation](#data-provenance-and-validation)"]

    body = []
    body.append(
        snippet("header")
        .replace("{{N}}", str(st["n"]))
    )
    body.append(snippet("intro"))
    body.append(snippet("start-here"))
    body.append(snippet("updates"))
    body.append("## Table of Contents\n\n" + "\n".join(toc) + "\n")
    body.append(snippet("survey"))
    body.append(snippet("whynow"))
    body.append(snippet("framework").replace("{{LEVEL_TABLE}}", "\n".join(level_rows)))
    body.append(snippet("loop-breaks"))
    body.append(snippet("tags"))
    body.append(
        '<a id="catalog-at-a-glance"></a>\n\n## Catalog at a Glance <sub><a href="#readme-top">↑ top</a></sub>\n\n'
        f"**{st['n']} entries** in {len(parts)} parts. Each entry appears once, under its primary topic.\n\n"
        + "\n".join(glance)
        + "\n"
    )
    for i, p in numbered:
        part_md = render_part(tax, p, i, entries)
        if p["id"] == "cases":
            part_md = part_md.replace("<details>", snippet("cases-table") + "\n<details>", 1)
        body.append(part_md)
    body.append(snippet("contributing"))
    body.append(snippet("citation"))
    prov = snippet("provenance")
    unlinked = ", ".join(f"`{x['key']}`" for x in st["unlinked"]) or "none"
    for k, v in {
        "N": st["n"],
        "ARXIV": st["arxiv"],
        "DOI": st["doi"],
        "LINKED": st["linked"],
        "UNLINKED_N": len(st["unlinked"]),
        "UNLINKED": unlinked,
        "LV_SURVEY": st["lv_survey"],
        "LV_CURATOR": st["lv_curator"],
        "VERIFIED": st["verified"],
    }.items():
        prov = prov.replace("{{" + k + "}}", str(v))
    body.append(prov)
    readme = "\n".join(body).rstrip() + "\n"
    readme = re.sub(r"\n{3,}", "\n\n", readme)

    buf = io.StringIO()
    cols = ["key", "title", "authors", "year", "venue", "part", "topic", "edge", "type", "level", "level_source", "arxiv", "doi", "links", "note"]
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
