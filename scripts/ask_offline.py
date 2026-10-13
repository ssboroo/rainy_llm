"""Run a local GGUF text model without Hub/API downloads. Experimental."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def verify_model(path, expected_sha256):
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise ValueError('expected SHA-256 must be 64 lowercase hex characters')
    path = Path(path).resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != '.gguf':
        raise ValueError('model must be a local .gguf file')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        if stream.read(4) != b'GGUF':
            raise ValueError('file has no GGUF header')
        stream.seek(0)
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != expected_sha256:
        raise ValueError('model SHA-256 mismatch; loading refused')
    return path


def generate(model_path, expected_sha256, prompt, context=2048, max_tokens=256, threads=4):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError('prompt must not be empty')
    if any(type(x) is not int or x < 1 for x in (context, max_tokens, threads)):
        raise ValueError('context, max_tokens and threads must be positive integers')
    if max_tokens >= context:
        raise ValueError('output budget must be smaller than context')
    path = verify_model(model_path, expected_sha256)
    # Only a local path is passed. Never invoke from_pretrained or a remote API.
    from llama_cpp import Llama
    model = Llama(model_path=str(path), n_ctx=context, n_threads=threads,
                  n_threads_batch=threads, n_gpu_layers=0, seed=42, verbose=False)
    try:
        template = model.metadata.get('tokenizer.chat_template')
        if not isinstance(template, str) or not template.strip():
            raise ValueError('embedded chat template required; implicit fallback refused')
        output = model.create_chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=max_tokens, temperature=0.0, stream=False)
        choice = output['choices'][0]
        return {'output': choice['message']['content'],
                'finish_reason': choice['finish_reason'], 'usage': output.get('usage'),
                'model_sha256': expected_sha256,
                'chat_template_sha256': hashlib.sha256(template.encode()).hexdigest(),
                'trained_rainy_model': False}
    finally:
        model.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--prompt')
    parser.add_argument('--context', type=int, default=2048)
    parser.add_argument('--max-tokens', type=int, default=256)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    try:
        if args.check_only:
            verify_model(args.model, args.sha256)
            result = {'artifact_integrity': True, 'runtime_compatibility': 'not tested',
                      'inference_executed': False}
        else:
            result = generate(args.model, args.sha256, args.prompt,
                              args.context, args.max_tokens, args.threads)
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        parser.exit(1, f'Offline model: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
