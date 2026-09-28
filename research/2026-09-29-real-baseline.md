# Real Mongolian data and first actual model baseline

## Collected data

20 real Mongolian Wikipedia introductions, 18,934 Unicode characters. Files: data/mnwiki_pilot/corpus.jsonl, manifest.json, README.md. Each text has source, revision metadata, attribution, CC BY-SA 4.0 license link and SHA-256. Checked all 20 hashes and unique IDs. The site rightsinfo API confirms CC BY-SA 4.0. Text quality remains unreviewed; template remnants and questionable wording were observed. This is a pilot, not a curated training corpus.

Eduge was not used because its dataset card labels the license unknown. No synthetic text was substituted for collected documents.

## Actual inference

Model: Qwen/Qwen3-0.6B, revision c1899de289a04d12100db370d81485cdf75e47ca. CPU float32, 4 threads, seed 42, thinking disabled, greedy decoding, 64 output tokens. The small older model was selected for feasibility, not freshness. This was inference only; Wikipedia data was not used to train or prompt it.

24/24 prompts completed. Normalized exact match: **0/24 (0%)**. Seven responses hit the output token cap. Total generation time: **120.8175 seconds**; generated tokens: **1,072**. Average per prompt: approximately 5.03 seconds. These timings exclude download/load. Outputs, scores and metadata are committed under experiments/qwen3-06b-cpu-v1/.

Qualitative inspection: many answers repeated or reformatted the question instead of solving it. Some included relevant words but failed the requested short-answer format. Zero exact-match does not mean zero semantic knowledge. The 24 public draft questions are small and not independently human-validated. The model-card recommended sampling parameters were not used; this is a deterministic greedy smoke run, not a vendor benchmark reproduction.

## Validation

24 existing unit tests passed. Corpus hashes/IDs verified. Baseline completed with 24 unique predictions and recorded model/case revisions. No training, larger model comparison or GPU benchmark performed.

## Next decision

Do not promote this tiny configuration to RAINY's production base. Review the evaluation rubric and run a stronger feasible model under documented, comparable decoding settings. Clean and review the real corpus before generating supervision; reserve evaluation documents first. Retain this poor baseline instead of hiding or relabeling its results.

## Монгол

Бодит 20 өгүүллийг цуглуулж, эх сурвалж, лицензтэй хадгалсан. Qwen3-0.6B загварыг CPU дээр үнэхээр ажиллуулж, 24 асуултын хариу гаргасан. Яг тохирсон хариултын оноо 0/24; 7 хариулт токены хязгаарт хүрсэн. Энэ тохиргоог эцсийн суурь болгохгүй. Илүү чадвартай загварын харьцуулалт, өгөгдлийн хүний хяналт дараагийн алхам. Сургалт хийгдээгүй.
