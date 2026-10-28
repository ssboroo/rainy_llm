"""Exact tensor/state comparison; not a language-quality benchmark."""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference')
    p.add_argument('resumed')
    p.add_argument('--output', required=True)
    a = p.parse_args()
    import torch
    from safetensors.torch import load_file
    def equal(x, y):
        if type(x) is not type(y):
            return False
        if isinstance(x, torch.Tensor):
            return x.dtype == y.dtype and x.shape == y.shape and torch.equal(x, y)
        if isinstance(x, dict):
            return x.keys() == y.keys() and all(equal(x[k], y[k]) for k in x)
        if isinstance(x, (list, tuple)):
            return len(x) == len(y) and all(equal(i,j) for i,j in zip(x,y))
        return x == y
    left, right = Path(a.reference), Path(a.resumed)
    result = {'adapter_tensors_exact':equal(load_file(str(left/'adapter_model.safetensors')),
                                           load_file(str(right/'adapter_model.safetensors')))}
    for file in ['optimizer.pt','scheduler.pt','rng_state.pth']:
        result[file] = equal(torch.load(left/file, weights_only=True, map_location='cpu'),
                             torch.load(right/file, weights_only=True, map_location='cpu'))
    result['trainer_state_exact'] = json.loads((left/'trainer_state.json').read_text()) == json.loads((right/'trainer_state.json').read_text())
    result['all_exact'] = all(result.values())
    with Path(a.output).open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))
    if not result['all_exact']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
