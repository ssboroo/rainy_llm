"""Experimental local-only, bounded CPU LoRA training. See docs/CPU_TRAINING.md."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

try:
    from .validate_data import validate
    from .validate_evaluation import read_jsonl, validate_cases
    from .export_chat import convert
except ImportError:
    from validate_data import validate
    from validate_evaluation import read_jsonl, validate_cases
    from export_chat import convert


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot(path):
    root = Path(path).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('model must be an existing local directory')
    files = {}
    for file in sorted(root.rglob('*')):
        if file.is_symlink():
            raise ValueError('materialize model snapshot; symlinks are not accepted')
        if file.is_file():
            files[file.relative_to(root).as_posix()] = digest(file)
    if 'config.json' not in files or not any(k.endswith('.safetensors') for k in files):
        raise ValueError('local model requires config.json and safetensors weights')
    return files


def outside_git(path):
    target = Path(path).resolve()
    if any((p / '.git').exists() for p in (target, *target.parents)):
        raise ValueError('training output/checkpoints must be outside every Git checkout')
    return target


def prepare(data, evaluation, review):
    _, errors = validate(data)
    if errors:
        raise ValueError('; '.join(errors))
    rows = read_jsonl(data)
    if any(row['split'] != 'train' for row in rows):
        raise ValueError('training input must contain only train records')
    errors, _ = validate_cases(read_jsonl(evaluation), rows)
    if errors:
        raise ValueError('; '.join(errors))
    approval = json.loads(Path(review).read_text(encoding='utf-8'))
    if (approval.get('data_sha256') != digest(data)
            or approval.get('reviewer_role') != 'human-reviewer'
            or not isinstance(approval.get('reviewer'), str)
            or not approval['reviewer'].strip()
            or approval.get('quality_reviewed') is not True
            or approval.get('privacy_reviewed') is not True
            or approval.get('training_rights_verified') is not True):
        raise ValueError('hash-bound human data review and training-rights attestation required')
    approved = approval.get('approved_source_licenses', [])
    if any({'source': r['source'], 'license': r['license']} not in approved for r in rows):
        raise ValueError('each source/license pair needs review approval')
    return convert(rows, 'train')


def tokenize(rows, tokenizer, max_length):
    if not tokenizer.chat_template:
        raise ValueError('explicit local chat template required')
    items = []
    for row in rows:
        messages = row['messages']
        prefix = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
        full = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
        if full[:len(prefix)] != prefix or len(full) <= len(prefix):
            raise ValueError('template does not support safe assistant-only prefix masking')
        if len(full) > max_length:
            raise ValueError('record exceeds max-length; refusing silent answer truncation')
        items.append({'input_ids': full, 'attention_mask': [1] * len(full),
                      'labels': [-100] * len(prefix) + full[len(prefix):]})
    return items


def check_resume(output, checkpoint, identity):
    if json.loads((output / 'run_identity.json').read_text()) != identity:
        raise ValueError('resume identity changed: model/data/review/eval/config/runtime must match')
    checkpoint = Path(checkpoint).resolve(strict=True)
    if checkpoint.parent != output or not checkpoint.name.startswith('checkpoint-'):
        raise ValueError('resume checkpoint must belong to this run directory')
    required = ['adapter_config.json', 'adapter_model.safetensors', 'optimizer.pt',
                'scheduler.pt', 'rng_state.pth', 'trainer_state.json']
    if any(not (checkpoint / name).is_file() for name in required):
        raise ValueError('incomplete checkpoint: adapter/optimizer/scheduler/RNG/state required')
    if (checkpoint / 'checkpoint-is-incomplete.txt').exists():
        raise ValueError('checkpoint save did not complete')
    return str(checkpoint)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('model', 'data', 'evaluation', 'review', 'output'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--total-steps', type=int, default=20)
    p.add_argument('--session-steps', type=int, default=2)
    p.add_argument('--seconds', type=int, default=120)
    p.add_argument('--max-length', type=int, default=256)
    p.add_argument('--threads', type=int, default=2)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--resume')
    p.add_argument('--persistent-storage-confirmed', action='store_true')
    return p


def main():
    p = parser()
    args = p.parse_args()
    try:
        for key, cap in [('total_steps', 1000), ('session_steps', 100), ('seconds', 3600),
                         ('max_length', 512), ('threads', 8)]:
            if not 1 <= getattr(args, key) <= cap:
                raise ValueError(f'{key} must be in 1..{cap}')
        if not args.persistent_storage_confirmed:
            raise ValueError('confirm durable private/non-repository checkpoint storage first')
        output = outside_git(args.output)
        rows = prepare(args.data, args.evaluation, args.review)
        model_dir = Path(args.model).resolve(strict=True)
        if output == model_dir or model_dir in output.parents or output in model_dir.parents:
            raise ValueError('model and output directories must be disjoint')
        model_files = snapshot(model_dir)
        # Never contact the Hub or enable remote model code/telemetry.
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        import torch
        from transformers import (AutoTokenizer, AutoModelForCausalLM, Trainer,
                                  TrainingArguments, TrainerCallback, set_seed)
        from peft import LoraConfig, get_peft_model
        versions = {name: importlib.metadata.version(name)
                    for name in ('torch', 'transformers', 'peft', 'accelerate')}
        identity = dict(schema=1, runner_sha256=digest(__file__), model_files=model_files, data_sha256=digest(args.data),
                        evaluation_sha256=digest(args.evaluation), review_sha256=digest(args.review),
                        versions=versions, seed=args.seed, total_steps=args.total_steps,
                        max_length=args.max_length, threads=args.threads,
                        lora=dict(r=8, lora_alpha=16, lora_dropout=0.0, target_modules='all-linear'),
                        learning_rate=0.0001, loss='assistant-only', device='cpu-float32')
        resume = check_resume(output, args.resume, identity) if args.resume else None
        if not resume and output.exists():
            raise ValueError('new run output already exists; use a new directory or explicit resume')
        torch.set_num_threads(args.threads)
        set_seed(args.seed)
        tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True, trust_remote_code=False)
        dataset = tokenize(rows, tokenizer, args.max_length)
        model = AutoModelForCausalLM.from_pretrained(str(model_dir), local_files_only=True,
                    trust_remote_code=False, use_safetensors=True, torch_dtype=torch.float32)
        model.config.use_cache = False
        model = get_peft_model(model, LoraConfig(task_type='CAUSAL_LM', **identity['lora']))
        # Batch size one, no padding, labels already mask every prompt token.
        def collate(batch):
            return {key: torch.tensor([batch[0][key]], dtype=torch.long) for key in batch[0]}

        class Budget(TrainerCallback):
            def on_train_begin(self, args, state, control, **kwargs):
                self.start_step, self.start_time = state.global_step, time.monotonic()

            def on_step_end(self, args, state, control, **kwargs):
                if (state.global_step - self.start_step >= cli.session_steps
                        or time.monotonic() - self.start_time >= cli.seconds):
                    control.should_save = True
                    control.should_training_stop = True
                return control

        cli = args
        training_args = TrainingArguments(output_dir=str(output), use_cpu=True,
            max_steps=args.total_steps, per_device_train_batch_size=1,
            learning_rate=identity['learning_rate'], lr_scheduler_type='constant',
            save_strategy='steps', save_steps=1, save_total_limit=2, save_only_model=False,
            logging_steps=1, logging_nan_inf_filter=False, report_to='none', push_to_hub=False,
            seed=args.seed, data_seed=args.seed, dataloader_num_workers=0,
            dataloader_pin_memory=False, optim='adamw_torch', disable_tqdm=True)
        if not resume:
            output.mkdir(parents=True, exist_ok=False)
            (output / 'run_identity.json').write_text(json.dumps(identity, indent=2) + '\n')
        trainer = Trainer(model=model, args=training_args, train_dataset=dataset,
                          data_collator=collate, callbacks=[Budget()])
        start = time.monotonic()
        result = trainer.train(resume_from_checkpoint=resume)
        print(json.dumps(dict(global_step=trainer.state.global_step, metrics=result.metrics,
            elapsed_seconds=time.monotonic()-start, device='cpu', model_quality_measured=False)))
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
