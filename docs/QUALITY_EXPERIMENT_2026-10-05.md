# Real CPU quality experiments — 2026-10-05

RAINY now has three newly executed model runs, not just model research notes. None is a RAINY-trained model. The 4B quantized candidate achieved the highest strict smoke score among these runs, but **7/24 is inadequate for production**. No default model was promoted.

## Measured results / Бодит үр дүн

All runs use the unchanged 24 public draft Mongolian questions, no system prompt, greedy non-thinking decoding, seed 42, four CPU threads and 64 output tokens. Expected answers are never passed to inference. The original normalized exact-match scorer was not relaxed after seeing answers.

| Executed system | Correct | Accuracy | Generation seconds, total | Seconds/case | Peak process RSS GiB | Token-limit hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-0.6B, Transformers BF16 | 0/24 | 0% | 77.5213 | 3.2301 | 1.558 | 7 |
| Qwen3-1.7B, Transformers BF16 | 0/24 | 0% | 191.3468 | 7.9728 | 3.647 | 11 |
| Qwen3-4B-Instruct-2507, llama.cpp Q4_K_M | 7/24 | 29.17% | 65.4978 | 2.7291 | 4.637 | 5 |

The 0.6B and 1.7B pair shares dtype/runtime/library versions. The 4B result changes model, quantization, tokenizer revision and backend together: it is a **system-level observation**, not an isolated model-size effect or controlled speedup. The comparison tool rejects it as a matched comparison. Single-run timings exclude downloads/loading; shared CPU and overlapping background downloads during part of the 1.7B run limit latency conclusions. RSS includes runtime and mapped weights; it is not VRAM. No GPU was used. Infrastructure cost is unknown; no paid service was started.

Environment: AMD EPYC 9V74 reported by the container, x86_64, cgroup memory limit **8 GiB**. Host-visible free memory overstates the process budget. A preceding 1.7B FP32 attempt exited 137 while loading and produced no score; memory exhaustion is the likely cause. See `experiments/quality-2026-10-05/environment.json`.

## Artifacts and identity

- `experiments/qwen3-06b-cpu-bf16-v1`: Qwen/Qwen3-0.6B at `c1899de289a04d12100db370d81485cdf75e47ca`.
- `experiments/qwen3-17b-cpu-bf16-v1`: Qwen/Qwen3-1.7B at `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- `experiments/qwen3-4b-2507-cpu-q4km-v1`: Unsloth GGUF at `a06e946bb6b655725eafa393f4a9745d460374c9`; upstream tokenizer at `cdbee75f17c01a7cc42f958dc650907174af0554`.
- GGUF SHA-256: `3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597`.
- Evaluation SHA-256: `b45f694cc83a5ffd030bcbb02b5872e4ffe49133e3ee0cf6d35aa1c030955bb5`.

Every completed run stores raw predictions, score details, token counts, timing and metadata. The previous FP32 baseline and dependency lock remain unchanged for rollback. The model weights are not committed.

## Reproduce / Ажиллуулах

Linux CPU environment used Python 3.12.14. The exact installed package snapshot is `requirements/quality-cpu-lock.txt`. BF16 support/performance depends on the CPU. Initial downloads need several GB of disk space and internet access.

```bash
python -m venv .venv-quality
source .venv-quality/bin/activate
python -m pip install -r requirements/quality-cpu-lock.txt \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

python scripts/run_baseline.py --dtype bfloat16 \
  --model Qwen/Qwen3-0.6B --revision c1899de289a04d12100db370d81485cdf75e47ca \
  --output-dir experiments/my-06b-bf16
python scripts/run_baseline.py --dtype bfloat16 \
  --model Qwen/Qwen3-1.7B --revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e \
  --output-dir experiments/my-17b-bf16
python scripts/run_gguf_baseline.py \
  --model unsloth/Qwen3-4B-Instruct-2507-GGUF \
  --revision a06e946bb6b655725eafa393f4a9745d460374c9 \
  --filename Qwen3-4B-Instruct-2507-Q4_K_M.gguf --quantization Q4_K_M \
  --tokenizer-model Qwen/Qwen3-4B-Instruct-2507 \
  --tokenizer-revision cdbee75f17c01a7cc42f958dc650907174af0554 \
  --output-dir experiments/my-4b-q4km

# Ask the pinned experimental candidate locally; no prompt logging.
python scripts/ask_candidate.py --prompt '23 дээр 19 нэм. Зөвхөн тоогоор хариул.'
```

The question CLI uses a 2048-token context and a default 256-token output budget. This is an experimental upstream model, not a released RAINY model or a claim of reliable Mongolian conversation. Benchmark runs retain the stricter 64-token budget.

## What still fails

The 0.6B model frequently repeats the question. The 1.7B model gives correct values for the first four arithmetic questions but violates requested answer format; it also makes substantive arithmetic and comprehension errors. The 4B system improves strict instruction compliance on seven cases, but mistranslates simple words, mishandles the apple story and gives the wrong ordering answer. These examples are qualitative inspection by the assistant, **not independent human review**. Do not count every exact-match failure as a semantic failure, or silently strip text until it matches a reference.

These 24 AI-authored public questions are development diagnostics, not a human-reviewed held-out benchmark. They cannot establish general Mongolian fluency, safety, statistical superiority or the best available model. No fine-tuning, adapter training or training-data collection occurred in this experiment. Quantization is not training.

## Монгол дүгнэлт ба дараагийн ажил

Бодит ахиц: ижил 24 асуултад 4B Q4_K_M систем **7 зөв хариу** өгсөн; 0.6B ба 1.7B BF16 нь **0 зөв**. Форматын алдаа оноонд нөлөөлсөн ч утгын том алдаа мөн байна. Иймээс 4B-ийг зөвхөн дараагийн туршилтын суурь нэр дэвшигч гэж үзнэ. Шинэ RAINY модель сургасан, Монгол хэлээр сайн болсон, эсвэл хамгийн шилдэг болсон гэж дүгнээгүй.

Дараагийн чанарын босго: Монгол хэлтэй хүнээр тусдаа үнэлгээний багц нягтлуулах; эрх нь баталгаатай сургалтын өгөгдлийг цэвэрлэж сургалт/validation/test-ийг эх сурвалжаар тусгаарлах; илүү хүчтэй нөөцөд багтах загваруудыг турших; зөвхөн дараа нь зөвшөөрөгдсөн GPU нөөцөөр LoRA/QLoRA сургалт хийж царцаасан үнэлгээг давтах. Энэ smoke багцын хариуг сургалтын өгөгдөл болгохгүй.

## Sources checked on 2026-10-05

- [Qwen3-1.7B official model card](https://huggingface.co/Qwen/Qwen3-1.7B): Apache-2.0, Transformers Qwen3 support and non-thinking control.
- [Qwen3-4B-Instruct-2507 official model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507): Apache-2.0, non-thinking instruction model. An older feasible candidate; not claimed to be the newest release.
- [Unsloth GGUF artifact](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF/tree/a06e946bb6b655725eafa393f4a9745d460374c9): third-party conversion, separately pinned; not Qwen's own GGUF release.
- [llama-cpp-python installation documentation](https://github.com/abetlen/llama-cpp-python): CPU binary-wheel installation. Version actually executed: 0.3.36.

RAINY project work belongs to its contributors, including ssboroo; upstream Qwen and Unsloth attribution and licenses remain applicable. This work does not transfer upstream model authorship to RAINY.
