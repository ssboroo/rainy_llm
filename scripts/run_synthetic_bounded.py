"""Supervise the synthetic experiment with whole-process wall/RSS budgets.

Linux/psutil runtime tool; retained logs are NOT proof that a run completed.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from train_lora_cpu import outside_git


def supervise(command, log, seconds, rss_bytes, measure):
    start = time.monotonic()
    peak = 0
    reason = None
    error = None
    samples = 0
    try:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    except OSError as exc:
        return dict(returncode=None, stop_reason='launch_error',
                    error_type=type(exc).__name__, elapsed_seconds=time.monotonic()-start,
                    peak_sampled_rss_bytes=0, rss_sampling_seconds=0.1, completed=False)
    try:
        while child.poll() is None:
            rss = measure(child.pid)
            if not isinstance(rss, int) or isinstance(rss, bool) or rss <= 0:
                # A disappearing process can race the sample. An alive child
                # with no observable RSS must never be treated as using 0 bytes.
                if child.poll() is not None:
                    break
                raise RuntimeError('child RSS unavailable; memory guard cannot operate')
            peak = max(peak, rss)
            samples += 1
            if rss > rss_bytes:
                reason = 'rss_limit'
            elif time.monotonic() - start > seconds:
                reason = 'wall_timeout'
            if reason:
                child.kill()
                break
            time.sleep(0.1)
        code = child.wait()
    except Exception as exc:
        reason = 'monitor_error'
        error = type(exc).__name__
        child.kill()
        code = child.wait()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        log.flush()
        os.fsync(log.fileno())
    if code == 0 and reason is None and samples == 0:
        reason = 'unobserved_exit'
    return dict(returncode=code, stop_reason=reason, error_type=error,
                elapsed_seconds=time.monotonic()-start, peak_sampled_rss_bytes=peak,
                rss_samples=samples, rss_sampling_seconds=0.1,
                completed=code == 0 and reason is None)


def preflight(log, measure):
    """Exercise the same monitor on a small real process, never load model weights."""
    result = supervise([sys.executable, '-c',
        'import time; payload=bytearray(8*1024*1024); time.sleep(0.6)'],
        log, 3, 256*1024**2, measure)
    result.update(probe='8MiB allocation and 0.6s hold',
                  model_loaded=False, training_executed=False)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight', action='store_true', help='Probe child RSS without model/runtime download')
    for name in ['model', 'evaluation']:
        p.add_argument('--'+name)
    p.add_argument('--output', required=True)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--seconds', type=int, default=240)
    p.add_argument('--rss-mib', type=int, default=8192)
    args = p.parse_args()
    if not args.preflight and (not args.model or not args.evaluation):
        p.error('--model and --evaluation required for training')
    if not 1 <= args.seconds <= 600 or not 256 <= args.rss_mib <= 8192:
        p.error('budget must be 1..600 seconds and 256..8192 MiB RSS')
    if not 0 <= args.seed < 2**32:
        p.error('seed must be unsigned32')
    out = outside_git(args.output)
    if out.exists():
        p.error('output must be new')
    out.parent.mkdir(parents=True, exist_ok=True)
    import psutil
    def measure(pid):
        try:
            return psutil.Process(pid).memory_info().rss
        except psutil.NoSuchProcess:
            return None
    # No descendants are expected: the fixed CPU runner does not launch workers.
    # RSS sampling is a best-effort guard, not an OS/cgroup hard memory limit.
    with Path(str(out)+'.supervisor.json').open('x') as report:
        with Path(str(out)+'.log').open('x') as log:
            result = preflight(log, measure) if args.preflight else supervise([sys.executable, str(Path(__file__).with_name('synthetic_lora_experiment.py')),
                '--model', args.model, '--evaluation', args.evaluation, '--output', str(out),
                '--steps', '16', '--seed', str(args.seed)], log, args.seconds,
                args.rss_mib*1024**2, measure)
        json.dump(result, report, indent=2)
        report.write('\n'); report.flush(); os.fsync(report.fileno())
    print(json.dumps(result))
    raise SystemExit(0 if result['completed'] else 1)


if __name__ == '__main__':
    main()
