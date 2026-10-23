# Contributing

Thanks for helping keep this map accurate. `README.md` and `data/catalog.csv` are generated; edit the files under `data/` and rebuild.

## Files

| File | What it holds |
| --- | --- |
| `data/refs.bib` | Bibliographic records (the companion survey's bibliography). |
| `data/papers.yaml` | Per-entry annotations: topic, type, level, level source, note, key-work flag (⭐), and link overrides. |
| `data/taxonomy.yaml` | Parts and topics, level definitions, layer edges and badge colors. |
| `data/resolved.json` | Cached arXiv / Crossref matches from `scripts/resolve_links.py`, with title similarity scores. |
| `data/readme/*.md` | Hand-written README sections. |

## Adding an entry

1. Add the BibTeX record to `data/refs.bib` (include `url`, `doi` or an arXiv ID when you have one).
2. Add an annotation to `data/papers.yaml` (see the field reference at the top of that file).
3. Resolve links and rebuild:

   ```bash
   pip install pyyaml requests
   python scripts/resolve_links.py data/refs.bib
   python scripts/build_readme.py
   ```

4. Open a pull request. CI fails if the README is out of date.

## Placing a work

Answer three questions in the note or the pull request:

- **Layer.** Which edge of the tower does it act on: Model → Silicon, Model → Stack, Silicon → Model, or a cross-layer loop?
- **Level.** How much of the R&D loop does the AI run? Use the L0–L4 decision rules in the README. Use `Human` for cross-layer co-design decided by people, and `Claimed` or `Undisclosed` for industrial statements that cannot be checked. Leave the level empty for foundations, theory and classic hardware papers.
- **Signal.** Which feedback tier does its loop depend on (S1 compile, S2 function, S3 PPA, S4 profile, S5 end-to-end, S6 post-silicon)?

If a work changes several layers, place it under the highest level it actually demonstrates. Set `lsrc: survey` only when the level is stated in the survey; otherwise use `lsrc: curator`, which shows a † in the README.

## Links

Automatic links are accepted only when the registry title matches the bibliography title (similarity ≥ 0.92) and the year is consistent; every candidate is kept in `data/resolved.json`. Link research to its proceedings page, DOI or arXiv record, and industry items to the organization's own publication, not a repost. If automatic resolution picks the wrong record, set `url`, `arxiv` or `doi` explicitly in `papers.yaml`, or set `no_auto_link: true`.
