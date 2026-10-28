"""Reload a hash-sealed synthetic checkpoint and compare every saved prediction."""
import argparse
import json
import os
from pathlib import Path
import socket
import time
import resource
from importlib.metadata import version

from train_lora_cpu import (digest, snapshot, checkpoint_inventory, checkpoint_step,
                            identity_digest, CHECKPOINT_MANIFEST)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--evaluation', required=True)
    p.add_argument('--step', type=int, required=True)
    p.add_argument('--report', help='New JSON report path; never overwrite existing evidence')
    args = p.parse_args()
    started = time.perf_counter()
    if args.report and Path(args.report).exists():
        raise FileExistsError(args.report)
    run = Path(args.run).resolve(strict=True)
    identity = json.loads((run/'identity.json').read_text())
    # Hub download bookkeeping is machine-specific, not model/tokenizer content.
    expected_model = {k:v for k,v in identity['model_files'].items() if not k.startswith('.cache/')}
    actual_model = {k:v for k,v in snapshot(args.model).items() if not k.startswith('.cache/')}
    if expected_model != actual_model:
        raise ValueError('model snapshot changed')
    if identity['evaluation_sha256'] != digest(args.evaluation):
        raise ValueError('evaluation changed')
    checkpoint = run/f'checkpoint-{args.step}'
    if checkpoint.is_symlink() or checkpoint.resolve().parent != run:
        raise ValueError('checkpoint must belong to run')
    expected_seal = dict(schema=1, global_step=checkpoint_step(checkpoint, identity),
        run_identity_sha256=identity_digest(identity), files=checkpoint_inventory(checkpoint))
    if json.loads((checkpoint/CHECKPOINT_MANIFEST).read_text()) != expected_seal:
        raise ValueError('checkpoint integrity mismatch')
    for name in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY']:
        os.environ[name] = '1'
    def denied(*a, **kw):
        raise RuntimeError('network disabled')
    socket.socket.connect = denied
    socket.create_connection = denied
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(identity['threads'])
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True, trust_remote_code=False)
    base = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True,
        trust_remote_code=False, use_safetensors=True, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model = PeftModel.from_pretrained(base, checkpoint, local_files_only=True).eval()
    expected = {r['id']: r['output'] for r in map(json.loads, (run/'after.jsonl').read_text().splitlines())}
    cases = list(map(json.loads, Path(args.evaluation).read_text().splitlines()))
    if set(expected) != {c['id'] for c in cases}:
        raise ValueError('prediction IDs mismatch')
    predictions = []
    for case in cases:
        case_started = time.perf_counter()
        ids = tok.apply_chat_template([dict(role='user', content=case['prompt'])], tokenize=True,
            add_generation_prompt=True, enable_thinking=False, return_tensors='pt')
        with torch.inference_mode():
            result = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                max_new_tokens=32, do_sample=False, use_cache=True, pad_token_id=tok.eos_token_id)
        actual = tok.decode(result[0,ids.shape[1]:], skip_special_tokens=True).strip()
        predictions.append(dict(id=case['id'], output=actual,
            elapsed_seconds=time.perf_counter()-case_started))
        if actual != expected[case['id']]:
            raise ValueError(f"reload prediction mismatch: {case['id']}")
    report = dict(reloaded_checkpoint=args.step, matching_predictions=len(cases),
        checkpoint_hashes_verified=True, training_resume_tested=False,
        evaluation_sha256=digest(args.evaluation),
        run_identity_sha256=identity_digest(identity),
        elapsed_seconds=time.perf_counter()-started,
        peak_rss_native=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_rss_unit='KiB on Linux; bytes on macOS',
        network_isolation='Python socket guards and HF offline flags; not OS isolation',
        runtime={name:version(name) for name in ['torch','transformers','peft','accelerate']},
        predictions=predictions)
    if args.report:
        with open(args.report, 'x', encoding='utf-8') as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
