# Bounded synthetic experiment supervisor

`scripts/run_synthetic_bounded.py` launches only the existing synthetic CPU
runner, with 16 steps and an explicit seed. It supervises the **whole process**,
including model loading and before/after generation, not just the training loop.

```sh
python scripts/run_synthetic_bounded.py --model /private/pinned-qwen3 \
  --evaluation evaluation/mn_transfer_draft_20261026.jsonl \
  --output /private/experiments/new-seed42 --seed 42 \
  --seconds 240 --rss-mib 8192
```

Requires the tested synthetic runtime plus `psutil` (previously installed version
7.2.2); this supervisor has not yet completed a real model run. It records a
sibling `.log` and `.supervisor.json`, refuses existing output/report/log files,
and returns nonzero for child failure, timeout, RSS excess or monitor failure.
Logs/reports are flushed and fsynced after process termination. Do not place
outputs inside Git. Save completed checkpoints privately before session end.

RSS is sampled every 0.1 seconds and applies to the child only: this is a
best-effort guard, not a hard cgroup limit, and the fixed runner must not launch
workers. Limit exceeded means immediate kill; a checkpoint being written may
be incomplete and must pass the existing seal checks before resume. An external
host/session termination can still prevent the final report or erase temporary
files. No automatic upload, persistence guarantee or unattended long training.

Actual tests launch short Python child processes and check success, exit3,
timeout, injected RSS excess, monitor exception and missing executable. Memory
limit tests inject the measurement; they do not allocate 8GiB or prove OOM safety.
These are process-control tests, not model inference or language-quality tests.

Монгол: Сургалтын бүх процессыг хугацаа ба RAM хэмжилтээр хянаж, алдааны шалтгаан,
лог хадгална. Хязгаар давбал зогсооно. Түр файлыг байнга хадгална гэсэн баталгаа
биш; model-ийн before/after хэмжилт, checkpoint-ийн хувийн хадгалалт тусдаа ажил.
