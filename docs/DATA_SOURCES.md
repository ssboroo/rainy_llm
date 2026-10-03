# Source decisions — 2026-09-29

| Source | Decision | Evidence |
| --- | --- | --- |
| Mongolian Wikipedia | 20-article pilot retrieved with attribution; unreviewed | https://mn.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=rightsinfo&format=json |
| Eduge / tugstugi/eduge | Not downloaded for training: license unresolved | https://huggingface.co/datasets/tugstugi/eduge |
| Tatoeba / OPUS | Research candidate only; no corpus imported in this run | https://huggingface.co/datasets/Helsinki-NLP/tatoeba_mt |

Wikipedia rightsinfo returned Creative Commons Attribution-Share Alike 4.0 and https://creativecommons.org/licenses/by-sa/4.0/deed.mn. Terms and attribution guidance: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use . The pilot contains only text, not images. Article-specific notices and quality still need review before expansion or training release.

Do not infer dataset rights from a GitHub code license or a model license. Do not treat public availability as permission. The project owner retains rights in original project materials; upstream text keeps its own license.

Next data work: editorial review, remove template/disambiguation remnants, document factual/linguistic issues, reserve article-level evaluation sources, create a versioned clean corpus. Increasing raw volume is not a substitute for data quality.

## Machine-readable shortlist — 2026-10-03

`data/source_registry.json` is the source-of-truth shortlist and `python scripts/validate_source_registry.py` checks its policy invariants. It distinguishes a licensed pilot, an evaluation-only candidate, and held sources. A public download page is not enough to set `training_allowed`.

- **Mongolian Wikipedia pilot:** approved only at its current 20-article, revision-pinned research scope; still unreviewed.
- **FLORES+ `khk_Cyrl`:** CC-BY-SA-4.0 evaluation candidate. Its official card says it should not be used as training data, access conditions must be accepted, and version 4.6 is current. Pin an immutable Hub commit before acquisition and keep it held out.
- **Eduge and CulturaX Mongolian:** held. Neither is approved for training by this registry while content-license/provenance questions remain unresolved.

The validator is a reproducibility guard, not legal advice. A source may be technically valid in the registry and still require human license, privacy, quality and contamination review.
