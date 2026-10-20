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

`data/source_registry.json` is the source-of-truth shortlist and `python scripts/validate_source_registry.py` checks its policy invariants. Schema v2 distinguishes a verified license, missing license, and conflicting license evidence; unresolved sources must be held and training-blocked. A public download page is not enough to set `training_allowed`.

- **Mongolian Wikipedia pilot:** approved only at its current 20-article, revision-pinned research scope; still unreviewed.
- **FLORES+ `khk_Cyrl`:** CC-BY-SA-4.0 evaluation candidate. Its official card says it should not be used as training data, access conditions must be accepted, and version 4.6 is current. Public metadata was pinned on 2026-10-08 to Hub commit `e707e62e762a9e2faca3933aa315f4665cc3cd8f`; gated content was not downloaded. Keep it held out and do not acquire it until the project owner accepts the terms.
- **Eduge and CulturaX Mongolian:** held. Neither is approved for training by this registry while content-license/provenance questions remain unresolved.
- **MADLAD-400 `mn`:** pinned to Hub commit `9d886a76bd8fa69b294f2dd3843dacb8388ee5a5`, but held. The official card metadata says ODC-By while its body says CC-BY-4.0. It identifies the audited `mn` slice as Mongolian Cyrillic and reports 879,878 clean documents; the language audit sampled only 20 documents and the card warns that clean web data still contains noise. No dataset files were downloaded. Resolve the publisher-side license conflict, then review upstream provenance, privacy, quality, deduplication and evaluation overlap before any acquisition or training.

The validator is a reproducibility guard, not legal advice. A source may be technically valid in the registry and still require human license, privacy, quality and contamination review.
