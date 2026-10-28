# Bounded synthetic experiment supervisor

## Check the host before downloading weights

Install `psutil==7.2.2`, then run:

```sh
python scripts/run_synthetic_bounded.py --preflight --output /private/new-probe
```

This launches a small child (8MiB allocation,0.6s hold) through the same
supervisor. No model, Torch, checkpoint or training data is needed. Exit0 means
the probe completed with at least one positive RSS sample, not that a full model
fits or OS memory enforcement works. Nonzero means do not start guarded training
on this host. Reports/logs remain exclusive and fsynced. A zero-sample fast exit
now reports `unobserved_exit` rather than success.

2026-10-28 actual CLI: `monitor_error`,zero valid samples,child killed,exit1.
The child PID directory existed but its status file was unavailable. This
confirms a visibility mismatch, not permission to bypass the guard; exact host
implementation cause remains unknown. Model execution was not attempted.

`scripts/run_synthetic_bounded.py` launches only the existing synthetic CPU
runner, with 16 steps and an explicit seed. It supervises the **whole process**,
including model loading and before/after generation, not just the training loop.

```sh
python scripts/run_synthetic_bounded.py --model /private/pinned-qwen3 \
  --evaluation evaluation/mn_transfer_draft_20261026.jsonl \
  --output /private/experiments/new-seed42 --seed 42 \
  --seconds 240 --rss-mib 8192
```

Requires the tested synthetic runtime plus `psutil` (tested version
7.2.2). It records a
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

2026-10-27 real-model execution exposed a host limitation: psutil could not
observe the child PID, and the original supervisor silently counted that as
zero RSS. Historical raw supervisor reports are retained but their zero RSS is
invalid, not a resource measurement. Model-process `ru_maxrss` is reported
separately. The corrected supervisor now fails closed for missing/zero/invalid
RSS while a child is alive. A real CLI probe on this host returned
`monitor_error`, exit 1, in 0.005 seconds; do not bypass it to claim guarded
execution. A host with observable child RSS is needed for the full guard.

Монгол: Сургалтын бүх процессыг хугацаа ба RAM хэмжилтээр хянаж, алдааны шалтгаан,
лог хадгална. Хязгаар давбал зогсооно. Түр файлыг байнга хадгална гэсэн баталгаа
биш; model-ийн before/after хэмжилт, checkpoint-ийн хувийн хадгалалт тусдаа ажил.
