"""Print basic local runtime/GPU information without uploading it."""
import json
import platform
import shutil
import subprocess
import sys


def inspect():
    report = dict(python=platform.python_version(), python_supported=sys.version_info >= (3, 10),
                  os=platform.system(), architecture=platform.machine(), nvidia_gpus=[],
                  gpu_probe='nvidia-smi unavailable; GPU presence unknown')
    command = shutil.which('nvidia-smi')
    if command:
        try:
            result = subprocess.run([command, '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                                    capture_output=True, text=True, timeout=10, check=True)
            report['nvidia_gpus'] = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            report['gpu_probe'] = 'completed; memory values are MiB'
        except (OSError, subprocess.SubprocessError):
            report['gpu_probe'] = 'probe failed; GPU presence unknown'
    report['note'] = 'This does not test CUDA training, AMD/Apple GPUs or memory available to a model.'
    return report


if __name__ == '__main__':
    print(json.dumps(inspect(), ensure_ascii=False, indent=2))
