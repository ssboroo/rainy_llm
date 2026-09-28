# Quality tools / Чанарын хэрэгслүүд

Python 3.10+, standard library only. Run from the repository root.

## Inspect the local computer / Төхөөрөмжөө шалгах

```bash
python scripts/doctor.py
```

Prints Python, OS, architecture and NVIDIA name/total VRAM if nvidia-smi works. It uploads nothing, installs nothing and does not test CUDA training. Missing nvidia-smi means GPU status is unknown; AMD/Apple GPUs are not probed. Run this on the actual training machine, not just a cloud coding environment.

Өөрийн компьютер дээр ажиллуулаад үр дүнг ашиглан тохирох загвар, сургалтын тохиргоо сонгоно. GPU илрээгүй нь GPU байхгүй гэсэн баталгаа биш.

## Audit data / Өгөгдөл шалгах

```bash
python scripts/audit_data.py data/examples.jsonl --output audit-report.json
```

The report includes row positions, possible email/phone/secret patterns, low Cyrillic ratios and similar prompt pairs. It never copies source text into findings. Similarity is character-based SequenceMatcher, not semantic similarity. It reports pairs without deleting records. Maximum 1,000 records per call because comparison is quadratic; long prompts may also be slow. For larger corpora a shingling/MinHash or indexed approach remains future work.

All findings require review. Eight-digit numbers can be arithmetic rather than phone numbers. Low Cyrillic ratio can be valid translation or code data. Zero findings does not guarantee privacy, quality or correct licensing. Do not use this report as an automatic release gate without a human policy.

Шалгалт нь ойролцоолсон дүрэмтэй. Тайланд эх текст, утас, имэйлийг бүтнээр харуулахгүй. Ижил төстэй асуултыг мөрийн дугаараар заана; өөрөө устгахгүй. Тайланг хүн хянах шаардлагатай.

## Export chat records / Chat формат гаргах

```bash
python scripts/export_chat.py data/examples.jsonl --split train --output-dir outputs/chat-v1
```

The exporter validates the input, selects only the requested split, preserves id/source/license, and writes messages.jsonl plus a hash manifest. An optional --system string adds a system message; by default no extra instruction is introduced. Input context is appended to the user instruction with a blank line. Existing output directories are refused.

This is generic messages data, not tokenized tensors. Before training, apply the selected model's documented chat template and decide truncation, sequence length, assistant-only loss masking and packing. A model-specific trainer must deliberately consume messages and retain metadata separately if needed.

Энэ команд өгөгдлийг user/assistant messages хэлбэрт хөрвүүлнэ. Загвар сургахгүй, tokenizer ажиллуулахгүй. Сонгосон загварт таарсан chat template, loss mask, sequence length дараагийн алхам хэвээр.

## Validation

24 local unit tests passed on Python 3.12. The audit and export CLIs were exercised on the format example. No model inference, training, CUDA or cross-platform integration test has been performed.
