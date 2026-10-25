"""Reload a hash-sealed synthetic checkpoint and compare every saved prediction."""
import argparse
import json
import os
from pathlib import Path
import socket

from train_lora_cpu import (digest, snapshot, checkpoint_inventory, checkpoint_step,
                            identity_digest, CHECKPOINT_MANIFEST)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--run', required=True)
    p.add_argument('--evaluation', required=True)
    p.add_argument('--step', type=int, required=True)
    args = p.parse_args()
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
    for case in cases:
        ids = tok.apply_chat_template([dict(role='user', content=case['prompt'])], tokenize=True,
            add_generation_prompt=True, enable_thinking=False, return_tensors='pt')
        with torch.inference_mode():
            result = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                max_new_tokens=32, do_sample=False, use_cache=True, pad_token_id=tok.eos_token_id)
        actual = tok.decode(result[0,ids.shape[1]:], skip_special_tokens=True).strip()
        if actual != expected[case['id']]:
            raise ValueError(f"reload prediction mismatch: {case['id']}")
    print(json.dumps(dict(reloaded_checkpoint=args.step, matching_predictions=len(cases),
        checkpoint_hashes_verified=True, training_resume_tested=False)))


if __name__ == '__main__':
    main()
