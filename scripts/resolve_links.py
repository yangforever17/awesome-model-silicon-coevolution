"""Resolve arXiv IDs and DOIs for refs.bib entries by exact-title lookup.

arXiv records are found through DataCite (which registers arXiv DOIs and has no
per-request throttling), falling back to the arXiv API for misses; DOIs come
from Crossref.

Writes a cache (data/resolved.json) so reruns only query unresolved entries.
Every match records its title similarity; build_readme.py accepts only
high-similarity matches, and anything below the threshold is left for manual
curation in data/papers.yaml (url / arxiv / doi fields).

Usage: python scripts/resolve_links.py path/to/refs.bib [--arxiv-api]
"""
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

import requests

sys.path.insert(0, os.path.dirname(__file__))
from bibparse import clean, parse  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "resolved.json")
UA = {"User-Agent": "awesome-model-silicon-coevolution/1.0"}
ATOM = "{http://www.w3.org/2005/Atom}"


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def ascii_words(title):
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9 ]+", " ", folded).split()


def datacite_search(title):
    phrase = " ".join(ascii_words(title))
    r = requests.get(
        "https://api.datacite.org/dois",
        params={"query": f'titles.title:"{phrase}"', "client-id": "arxiv.content", "page[size]": 5},
        headers=UA,
        timeout=30,
    )
    if r.status_code != 200:
        return None
    best = None
    for x in r.json().get("data", []):
        t = x["attributes"]["titles"][0]["title"]
        aid = x["id"].lower().split("arxiv.", 1)[-1]
        s = sim(title, t)
        if not best or s > best["sim"]:
            best = {"id": aid, "title": " ".join(t.split()), "sim": round(s, 3), "published": str(x["attributes"].get("publicationYear"))}
    return best


def arxiv_search(title):
    words = ascii_words(title)
    query = "ti:" + urllib.parse.quote('"' + " ".join(words) + '"')
    for attempt in range(4):
        r = requests.get(
            f"https://export.arxiv.org/api/query?search_query={query}&max_results=5",
            headers=UA,
            timeout=30,
        )
        if r.status_code == 200:
            break
        time.sleep(5 * (attempt + 1))
    else:
        return None
    best = None
    for e in ET.fromstring(r.text).findall(f"{ATOM}entry"):
        t = " ".join(e.find(f"{ATOM}title").text.split())
        aid = e.find(f"{ATOM}id").text.rsplit("/abs/", 1)[-1]
        aid = re.sub(r"v\d+$", "", aid)
        s = sim(title, t)
        if not best or s > best["sim"]:
            best = {"id": aid, "title": t, "sim": round(s, 3), "published": e.find(f"{ATOM}published").text[:10]}
    return best


def crossref_search(title):
    r = requests.get(
        "https://api.crossref.org/works",
        params={"query.title": title, "rows": 5, "select": "title,DOI,issued,container-title,type"},
        headers=UA,
        timeout=30,
    )
    if r.status_code != 200:
        return None
    best = None
    for it in r.json()["message"]["items"]:
        t = (it.get("title") or [""])[0]
        s = sim(title, t)
        if not best or s > best["sim"]:
            year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
            best = {
                "doi": it["DOI"],
                "title": t,
                "sim": round(s, 3),
                "year": year,
                "venue": (it.get("container-title") or [""])[0],
                "type": it.get("type"),
            }
    return best


def resolve(e, rec):
    title = clean(e.get("title", ""))
    if "arxiv" not in rec:
        rec["arxiv"] = datacite_search(title)
    if "crossref" not in rec:
        rec["crossref"] = crossref_search(title)
    return rec


def main(bib_path, use_arxiv_api=False):
    entries = parse(open(bib_path, encoding="utf-8").read())
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {e["key"]: pool.submit(resolve, e, cache.setdefault(e["key"], {})) for e in entries}
        for key, f in futures.items():
            rec = f.result()
            a, c = rec["arxiv"], rec["crossref"]
            print(f"{key}: arxiv={a and a['id']}({a and a['sim']}) doi={c and c['doi']}({c and c['sim']})", flush=True)
    if use_arxiv_api:
        # Second chance for titles DataCite did not match closely.
        for e in entries:
            rec = cache[e["key"]]
            if not rec["arxiv"] or rec["arxiv"]["sim"] < 0.92:
                hit = arxiv_search(clean(e.get("title", "")))
                if hit and (not rec["arxiv"] or hit["sim"] > rec["arxiv"]["sim"]):
                    rec["arxiv"] = hit
                    print(f"{e['key']}: arxiv-api={hit['id']}({hit['sim']})", flush=True)
                time.sleep(3)  # arXiv API etiquette
    json.dump(cache, open(CACHE, "w"), indent=1, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1], use_arxiv_api="--arxiv-api" in sys.argv)
