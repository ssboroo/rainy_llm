# Source decisions — 2026-09-29

| Source | Decision | Evidence |
| --- | --- | --- |
| Mongolian Wikipedia | 20-article pilot retrieved with attribution; unreviewed | https://mn.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=rightsinfo&format=json |
| Eduge / tugstugi/eduge | Not downloaded for training: license unresolved | https://huggingface.co/datasets/tugstugi/eduge |
| Tatoeba / OPUS | Research candidate only; no corpus imported in this run | https://huggingface.co/datasets/Helsinki-NLP/tatoeba_mt |

Wikipedia rightsinfo returned Creative Commons Attribution-Share Alike 4.0 and https://creativecommons.org/licenses/by-sa/4.0/deed.mn. Terms and attribution guidance: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use . The pilot contains only text, not images. Article-specific notices and quality still need review before expansion or training release.

Do not infer dataset rights from a GitHub code license or a model license. Do not treat public availability as permission. The project owner retains rights in original project materials; upstream text keeps its own license.

Next data work: editorial review, remove template/disambiguation remnants, document factual/linguistic issues, reserve article-level evaluation sources, create a versioned clean corpus. Increasing raw volume is not a substitute for data quality.
