# Qwen3.5-4B CPU experiment — 2026-10-07

This is a real, reproducible inference experiment, not a trained RAINY model or a production promotion. A pinned third-party Q4_K_M conversion of Qwen3.5-4B ran on the unchanged 24-case public Mongolian smoke set.

## Result / Үр дүн

| Executed system | Correct | Accuracy | Generation seconds | Seconds/case | Peak RSS GiB | Token-limit hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-4B-Instruct-2507 Q4_K_M (previous) | 7/24 | 29.17% | 65.4978 | 2.7291 | 4.637 | 5 |
| Qwen3.5-4B Q4_K_M (candidate) | **12/24** | **50.00%** | **52.9427** | **2.2059** | **4.241** | **2** |

The comparison gate reports `comparable=true`, an accuracy delta of **+0.2083**, and **-0.5231 seconds/case**. Both runs used the same evaluation hash, normalized exact-match metric, llama-cpp-python 0.3.36, Transformers 4.51.3, Q4_K_M, CPU, four threads, seed 42, greedy non-thinking decoding and 64 output tokens. Raw outputs and the machine-readable gate report are in `experiments/qwen35-4b-cpu-q4km-v1`.

This narrow result is promising, but `promotion_eligible=false`. Hardware/VRAM/cost fields are incomplete in the older baseline, infrastructure cost is unknown, and the public 24-case set is too small and not human-reviewed. It does not establish general Mongolian quality, safety, production readiness or state-of-the-art status. No training or fine-tuning occurred.

Category exact matches for Qwen3.5-4B were arithmetic 4/6, comprehension 3/6, instruction 2/6, transliteration 1/2, translation 0/2 and logic 2/2. Two responses reached the 64-token cap. Exact match is format-sensitive; semantic human review was not performed.

## Pinned identity

- Upstream tokenizer/model card: `Qwen/Qwen3.5-4B` at `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, Apache-2.0.
- Executed GGUF: `unsloth/Qwen3.5-4B-GGUF` at `e87f176479d0855a907a41277aca2f8ee7a09523`. This is a third-party conversion, not an official Qwen GGUF release.
- File: `Qwen3.5-4B-Q4_K_M.gguf`, 2,740,937,888 bytes.
- GGUF SHA-256: `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`.
- Chat-template SHA-256: `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715`.
- Evaluation SHA-256: `b45f694cc83a5ffd030bcbb02b5872e4ffe49133e3ee0cf6d35aa1c030955bb5`.

The runner now explicitly passes `enable_thinking` to the upstream tokenizer template instead of only claiming a mode in metadata. The executed run used `--no-thinking`. Model weights remain in the local Hugging Face cache and are not committed.

## Reproduce

Use the existing `requirements/quality-cpu-lock.txt` environment and the CPU llama-cpp-python wheel source described in the 2026-10-05 report:

```bash
python scripts/run_gguf_baseline.py \
  --model unsloth/Qwen3.5-4B-GGUF \
  --revision e87f176479d0855a907a41277aca2f8ee7a09523 \
  --filename Qwen3.5-4B-Q4_K_M.gguf --quantization Q4_K_M \
  --tokenizer-model Qwen/Qwen3.5-4B \
  --tokenizer-revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --output-dir experiments/my-qwen35-4b-q4km --no-thinking
```

Official upstream source: https://huggingface.co/Qwen/Qwen3.5-4B. Executed conversion: https://huggingface.co/unsloth/Qwen3.5-4B-GGUF/tree/e87f176479d0855a907a41277aca2f8ee7a09523. GGUF format documentation: https://huggingface.co/docs/hub/gguf. The artifact and upstream snapshots are pinned separately so the conversion is not mistaken for publisher provenance.

## Монгол дүгнэлт

Qwen3.5-4B Q4_K_M нь ижил runtime, ижил 24 smoke асуултад өмнөх 4B системийн 7/24-өөс 12/24 болж өссөн бөгөөд generation хугацаа багассан. Энэ бол бодит хэмжилт боловч жижиг, нийтэд ил smoke багцын үр дүн. Суурь загварыг сольсонгүй. Дараагийн шийдвэрийг хүний хянасан, сургалтаас тусдаа 100+ Монгол асуулт, бүрэн hardware/VRAM/cost metadata болон давтан run дээр гаргана.
