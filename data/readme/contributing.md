<a id="contributing"></a>

## Contributing <sub><a href="#readme-top">↑ top</a></sub>

The README is generated, so please do not edit it by hand. To add or revise an entry:

1. Add the BibTeX record to [`data/refs.bib`](data/refs.bib).
2. Add an annotation to [`data/papers.yaml`](data/papers.yaml) with its topic, type, level (if it applies) and a one-line note. Place it on the tower by stating **which layer it acts on → which signal it reads → which layer it updates → whether the update reaches the executor**.
3. Run `python scripts/resolve_links.py data/refs.bib` to look up arXiv and DOI links, then `python scripts/build_readme.py`.

```yaml
newkey2026example:
  topic: ms-kernel        # see data/taxonomy.yaml
  type: Paper             # Paper | Survey | Benchmark | Dataset | Tool | Industry | Essay | Book
  level: L1               # L0–L4, Human, Claimed, Undisclosed (omit if not applicable)
  lsrc: curator           # survey | curator
  note: "One sentence on what the work changes and what feedback it reads."
```

If a work changes several layers, place it under the highest level it actually demonstrates. See [CONTRIBUTING.md](CONTRIBUTING.md) for details. Corrections to curator-assigned (†) levels are especially welcome.

---
