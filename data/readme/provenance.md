<a id="data-provenance-and-validation"></a>

## Data Provenance and Validation <sub><a href="#readme-top">↑ top</a></sub>

The catalog is generated from the survey's bibliography ([`data/refs.bib`](data/refs.bib)) and a per-entry annotation file ([`data/papers.yaml`](data/papers.yaml)); a flat export is in [`data/catalog.csv`](data/catalog.csv).

- **{{N}}** entries, each listed exactly once under its primary topic.
- **{{LINKED}} / {{N}}** entries have at least one link: **{{ARXIV}}** arXiv records and **{{DOI}}** DOIs, plus official pages for blogs, releases and tools. Links were resolved by exact-title lookup against DataCite (for arXiv records) and Crossref, and accepted only when the registry title matches the bibliography title (similarity ≥ 0.92) and the year is consistent; all candidate matches are recorded in [`data/resolved.json`](data/resolved.json). Links that could not be matched automatically, or that matched the wrong record, are set by hand in `papers.yaml` after checking the registry entry.
- Entries still without a link ({{UNLINKED_N}}): {{UNLINKED}}.
- **{{LV_SURVEY}}** level assignments come directly from the survey's tables and text; **{{LV_CURATOR}}** were assigned by the curators with the same criteria and are marked †.

`python scripts/build_readme.py --check` verifies that the README and CSV match the data files; CI runs it on every push.
