"""Bounded synthetic CPU experiment, NOT reviewed-corpus RAINY training.

No external training data accepted. Draft evaluation is never optimized on.
Uses a local Qwen3 snapshot; outputs (including weights) must be outside Git.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import time

from evaluate import score, normalized
from train_lora_cpu import outside_git, snapshot, seal_checkpoint
from synthetic_resume import validate_resume, save_rng, restore_state


def synthetic_rows():
    """AI-authored technical fixtures; not counted as collected Mongolian sources."""
    rows = []
    for a, b in [(11, 2), (13, 3), (15, 4), (18, 5), (21, 6), (23, 8),
                 (26, 9), (31, 11), (34, 12), (38, 13), (41, 15), (43, 16),
                 (46, 17), (51, 18), (54, 21), (57, 22)]:
        rows.append(dict(prompt=f'{a} дээр {b} нэм. Зөвхөн тоогоор хариул.', answer=str(a+b)))
    for word in ['Салхи', 'Бороо', 'Уул', 'Гол', 'Тал', 'Мод', 'Нуур', 'Чулуу',
                 'Өвөл', 'Хавар', 'Зун', 'Намар', 'Цас', 'Үүл', 'Навч', 'Цэцэг']:
        rows.append(dict(prompt=f'Дараах үгийг өөрчлөлтгүй давтаж бич: {word}', answer=word))
    return rows


def validate_separation(rows, cases):
    prompts = [normalized(r['prompt']) for r in rows]
    if len(set(prompts)) != len(prompts):
        raise ValueError('duplicate training prompt')
    if set(prompts) & {normalized(c['prompt']) for c in cases}:
        raise ValueError('training/evaluation prompt overlap')


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--evaluation', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--steps', type=int, default=16)
    p.add_argument('--seconds', type=int, default=600)
    p.add_argument('--session-steps', type=int, default=32)
    p.add_argument('--resume', help='sealed checkpoint from the same runner/config; new output required')
    p.add_argument('--skip-evaluation', action='store_true', help='resume mechanics only; no quality score')
    args = p.parse_args()
    if not 1 <= args.steps <= 32 or not 1 <= args.seconds <= 600:
        p.error('technical smoke limited to 32 steps / 600 training seconds')
    if not 1 <= args.session_steps <= 32:
        p.error('session-steps must be in 1..32')
    out = outside_git(args.output)
    model_path = Path(args.model).resolve(strict=True)
    if out == model_path or model_path in out.parents or out in model_path.parents:
        p.error('model and output must be disjoint')
    cases_bytes = Path(args.evaluation).read_bytes()
    cases = [json.loads(line) for line in cases_bytes.decode().splitlines() if line.strip()]
    rows = synthetic_rows()
    validate_separation(rows, cases)
    model_files = {k:v for k,v in snapshot(model_path).items() if not k.startswith('.cache/')}
    for key in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY']:
        os.environ[key] = '1'
    # Block Python network connections as well as library online lookup.
    import socket
    def denied(*a, **kw):
        raise RuntimeError('network disabled during experiment')
    socket.socket.connect = denied
    socket.create_connection = denied
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
    from peft import LoraConfig, get_peft_model
    torch.set_num_threads(4)
    set_seed(42)
    identity = dict(kind='synthetic-technical-smoke-not-rainy-release',
        human_reviewed=False, training_sources_added=0,
        model_files=model_files, evaluation_sha256=hashlib.sha256(cases_bytes).hexdigest(),
        training_sha256=hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        versions={n: importlib.metadata.version(n) for n in ['torch','transformers','peft','accelerate']},
        seed=42, threads=4, dtype='float32', device='cpu', max_new_tokens=32,
        do_sample=False, enable_thinking=False, learning_rate=0.0003,
        lora=dict(r=4, lora_alpha=8, lora_dropout=0.0, target_modules=['q_proj','v_proj']),
        total_steps=args.steps, training_seconds_cap=args.seconds,
        skip_evaluation=args.skip_evaluation,
        python=platform.python_version(), network='Python socket connect blocked; HF offline')
    resume = validate_resume(args.resume, identity, len(rows)) if args.resume else None
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'identity.json', identity)
    write_json(out/'synthetic_train.json', rows)
    tok = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
        trust_remote_code=False, torch_dtype=torch.float32, low_cpu_mem_usage=True,
        use_safetensors=True)

    def evaluate(label):
        model.eval()
        predictions = []
        with (out/f'{label}.jsonl').open('x', encoding='utf-8') as stream:
            for case in cases:
                ids = tok.apply_chat_template([dict(role='user', content=case['prompt'])],
                    tokenize=True, add_generation_prompt=True, enable_thinking=False,
                    return_tensors='pt')
                start = time.monotonic()
                with torch.inference_mode():
                    result = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                        max_new_tokens=32, do_sample=False, pad_token_id=tok.eos_token_id,
                        use_cache=True)
                generated = result[0, ids.shape[1]:]
                row = dict(id=case['id'], output=tok.decode(generated, skip_special_tokens=True).strip(),
                           seconds=time.monotonic()-start, tokens=len(generated),
                           hit_token_limit=len(generated)==32)
                predictions.append(row)
                stream.write(json.dumps(row, ensure_ascii=False)+'\n'); stream.flush()
                print(label, case['id'], repr(row['output']), flush=True)
        report = score(cases, predictions)
        report['seconds'] = sum(r['seconds'] for r in predictions)
        report['tokens'] = sum(r['tokens'] for r in predictions)
        write_json(out/f'{label}-scores.json', report)
        return report

    before = None
    if not args.skip_evaluation:
        before = evaluate('before')
    if resume:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(resume[0]), is_trainable=True, local_files_only=True)
    else:
        model = get_peft_model(model, LoraConfig(task_type='CAUSAL_LM', **identity['lora']))
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=0.0003)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    order = torch.randperm(len(rows)).tolist()
    losses = []
    start_step = 0
    if resume:
        order = resume[1]['order']
        losses = resume[1]['losses'][:]
        start_step = resume[1]['global_step']
        restore_state(resume[0], optimizer, scheduler)
    start = time.monotonic()
    model.train()
    for step in range(start_step, min(args.steps, start_step + args.session_steps)):
        row = rows[order[step]]
        messages = [dict(role='user', content=row['prompt'])]
        prefix = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, enable_thinking=False)
        full = tok.apply_chat_template(messages+[dict(role='assistant',content=row['answer'])],
                                      tokenize=True, add_generation_prompt=False, enable_thinking=False)
        if full[:len(prefix)] != prefix or len(full) > 128 or len(full) <= len(prefix):
            raise ValueError('invalid assistant-only tokenization')
        ids = torch.tensor([full])
        labels = ids.clone(); labels[:, :len(prefix)] = -100
        optimizer.zero_grad(set_to_none=True)
        loss = model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels, use_cache=False).loss
        if not torch.isfinite(loss):
            raise RuntimeError('nonfinite loss')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step(); scheduler.step()
        losses.append(float(loss.detach()))
        print('TRAIN',step+1,losses[-1],flush=True)
        # Each step retains complete optimizer/scheduler/RNG state, outside Git.
        checkpoint = out/f'checkpoint-{step+1}'
        model.save_pretrained(checkpoint, safe_serialization=True)
        torch.save(optimizer.state_dict(), checkpoint/'optimizer.pt')
        torch.save(scheduler.state_dict(), checkpoint/'scheduler.pt')
        save_rng(checkpoint/'rng_state.pth')
        write_json(checkpoint/'trainer_state.json', dict(global_step=step+1, order=order, losses=losses))
        seal_checkpoint(checkpoint, identity)
        if time.monotonic()-start >= args.seconds:
            break
    training_seconds = time.monotonic()-start
    after = None if args.skip_evaluation else evaluate('after')
    write_json(out/'summary.json', dict(before=before, after=after, steps=len(losses), losses=losses,
        training_seconds=training_seconds, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        session_steps=len(losses)-start_step,
        accuracy_delta=None if args.skip_evaluation else after['accuracy']-before['accuracy'], general_mongolian_improvement_proven=False,
        note='Draft 24-case diagnostic; synthetic training; no human review. No model promotion.'))
    print('DONE',len(losses),'steps',training_seconds,'seconds',flush=True)


if __name__ == '__main__':
    main()
