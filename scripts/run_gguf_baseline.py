"""CPU GGUF smoke evaluation; record raw answers and exact artifact identity."""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

from evaluate import score
from prepare_data import read_rows


def render_prompt(tokenizer, content, thinking=False):
    """Render one user turn while making the model's reasoning mode explicit."""
    return tokenizer.apply_chat_template(
        [dict(role='user', content=content)], tokenize=False,
        add_generation_prompt=True, enable_thinking=thinking)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, help='GGUF Hugging Face repository')
    parser.add_argument('--revision', required=True)
    parser.add_argument('--filename', required=True)
    parser.add_argument('--quantization', required=True, help='Artifact precision, e.g. Q4_K_M')
    parser.add_argument('--tokenizer-model', required=True)
    parser.add_argument('--tokenizer-revision', required=True)
    parser.add_argument('--cases', default='evaluation/mn_smoke.jsonl')
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--max-new-tokens', type=int, default=64)
    parser.add_argument('--thinking', action=argparse.BooleanOptionalAction, default=False,
        help='Pass enable_thinking to the tokenizer chat template (default: disabled)')
    args = parser.parse_args()
    import llama_cpp
    import transformers
    from huggingface_hub import hf_hub_download
    from transformers import AutoTokenizer

    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=False)
    cases = read_rows(args.cases)
    model_path = hf_hub_download(args.model, args.filename, revision=args.revision)
    with open(model_path, 'rb') as artifact:
        artifact_sha = hashlib.file_digest(artifact, 'sha256').hexdigest()
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_model,
        revision=args.tokenizer_revision, trust_remote_code=False)
    llm = llama_cpp.Llama(model_path=model_path, n_gpu_layers=0, n_ctx=2048,
        n_threads=args.threads, n_threads_batch=args.threads, seed=42, verbose=False)
    metadata = dict(model=args.model, revision=args.revision, filename=args.filename,
        artifact_sha256=artifact_sha, tokenizer_model=args.tokenizer_model,
        tokenizer_revision=args.tokenizer_revision, backend='llama-cpp-python',
        llama_cpp=llama_cpp.__version__, transformers=transformers.__version__,
        python=platform.python_version(), device='cpu', dtype=args.quantization,
        artifact_size_bytes=Path(model_path).stat().st_size,
        chat_template_sha256=hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        threads=args.threads, seed=42, thinking=args.thinking, do_sample=False,
        max_new_tokens=args.max_new_tokens, n_ctx=2048, temperature=0.0,
        repeat_penalty=1.0, cases_sha256=hashlib.sha256(Path(args.cases).read_bytes()).hexdigest(),
        status='running', note='Quantized system experiment. Different runtime and precision from Transformers baseline; not an isolated model-size comparison.')
    def save_metadata():
        (target / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    save_metadata()
    predictions = []
    with (target / 'predictions.jsonl').open('w', encoding='utf-8') as out:
        for case in cases:
            prompt = render_prompt(tokenizer, case['prompt'], args.thinking)
            llm.reset()
            start = time.perf_counter()
            result = llm(prompt, max_tokens=args.max_new_tokens, temperature=0.0,
                top_p=1.0, top_k=0, repeat_penalty=1.0, seed=42,
                stop=['<|im_end|>', '<|endoftext|>'])
            row = dict(id=case['id'], output=result['choices'][0]['text'].strip(),
                generated_tokens=result['usage']['completion_tokens'],
                seconds=round(time.perf_counter() - start, 4),
                hit_token_limit=result['choices'][0]['finish_reason'] == 'length',
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
            predictions.append(row)
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
            out.flush()
            print(row['id'], repr(row['output']), flush=True)
    report = score(cases, predictions)
    (target / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    metadata.update(status='completed', total_generation_seconds=sum(r['seconds'] for r in predictions),
        generated_tokens=sum(r['generated_tokens'] for r in predictions),
        token_limit_hits=sum(r['hit_token_limit'] for r in predictions))
    if platform.system() == 'Linux':
        import resource
        metadata['peak_rss_kib_linux'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    save_metadata()
    print('SCORE', report['correct'], report['total'], flush=True)


if __name__ == '__main__':
    main()
