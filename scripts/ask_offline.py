#!/usr/bin/env python3
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


def _validate_generation(prompt, context, max_tokens, threads):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError('prompt must not be empty')
    if any(type(x) is not int or x < 1 for x in (context, max_tokens, threads)):
        raise ValueError('context, max_tokens and threads must be positive integers')
    if max_tokens >= context:
        raise ValueError('output budget must be smaller than context')


def _open_model(path, context, threads):
    # Only a local path is passed. Never invoke from_pretrained or a remote API.
    from llama_cpp import Llama
    return Llama(model_path=str(path), n_ctx=context, n_threads=threads,
                 n_threads_batch=threads, n_gpu_layers=0, seed=42, verbose=False)


def _require_template(model):
    template = model.metadata.get('tokenizer.chat_template')
    if not isinstance(template, str) or not template.strip():
        raise ValueError('embedded chat template required; implicit fallback refused')
    return template


def generate(model_path, expected_sha256, prompt, context=2048, max_tokens=256, threads=4):
    _validate_generation(prompt, context, max_tokens, threads)
    path = verify_model(model_path, expected_sha256)
    model = _open_model(path, context, threads)
    try:
        template = _require_template(model)
        prompt_tokens_estimate, input_token_budget, context_safety_reserve = (
            _check_prompt_budget(model, prompt, context, max_tokens))
        output = model.create_chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=max_tokens, temperature=0.0, stream=False)
        choice = output['choices'][0]
        return {'output': choice['message']['content'],
                'finish_reason': choice['finish_reason'], 'usage': output.get('usage'),
                'model_sha256': expected_sha256,
                'chat_template_sha256': hashlib.sha256(template.encode()).hexdigest(),
                'prompt_tokens_estimate': prompt_tokens_estimate,
                'input_token_budget': input_token_budget,
                'context_safety_reserve_tokens': context_safety_reserve,
                'trained_rainy_model': False}
    finally:
        model.close()


def generate_stream(model_path, expected_sha256, prompt, context=2048, max_tokens=256, threads=4):
    """Yield NDJSON-ready text deltas, then one terminal metadata event."""
    _validate_generation(prompt, context, max_tokens, threads)
    path = verify_model(model_path, expected_sha256)
    model = _open_model(path, context, threads)
    try:
        template = _require_template(model)
        prompt_tokens_estimate, input_token_budget, context_safety_reserve = (
            _check_prompt_budget(model, prompt, context, max_tokens))
        finish_reason = None
        usage = None
        chunks = model.create_chat_completion(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=max_tokens, temperature=0.0, stream=True)
        for chunk in chunks:
            if not isinstance(chunk, dict):
                raise ValueError('backend returned a malformed stream chunk')
            if chunk.get('usage') is not None:
                usage = chunk['usage']
            choices = chunk.get('choices') or []
            if not choices:
                continue
            choice = choices[0]
            if not isinstance(choice, dict):
                raise ValueError('backend returned a malformed stream choice')
            delta = choice.get('delta') or {}
            content = delta.get('content')
            if content is not None:
                if not isinstance(content, str):
                    raise ValueError('backend returned non-text delta content')
                if content:
                    yield {'type': 'delta', 'text': content}
            if choice.get('finish_reason') is not None:
                finish_reason = choice['finish_reason']
        yield {'type': 'done', 'finish_reason': finish_reason, 'usage': usage,
               'model_sha256': expected_sha256,
               'chat_template_sha256': hashlib.sha256(template.encode()).hexdigest(),
               'prompt_tokens_estimate': prompt_tokens_estimate,
               'input_token_budget': input_token_budget,
               'context_safety_reserve_tokens': context_safety_reserve,
               'trained_rainy_model': False}
    finally:
        model.close()


CHAT_MESSAGE_OVERHEAD_TOKENS = 8


def _message_token_cost(model, content):
    tokenizer = getattr(model, 'tokenize', None)
    if not callable(tokenizer):
        raise ValueError('runtime tokenizer is required for token-bounded chat history')
    try:
        tokens = tokenizer(content.encode('utf-8'), add_bos=False, special=True)
    except Exception as exc:
        raise ValueError(f'could not tokenize chat message: {exc}') from exc
    if not isinstance(tokens, (list, tuple)):
        raise ValueError('runtime tokenizer returned an invalid token sequence')
    return len(tokens) + CHAT_MESSAGE_OVERHEAD_TOKENS


def _check_prompt_budget(model, prompt, context, max_tokens):
    """Fail closed before generation when a single prompt exceeds safe context."""
    reserve = max(64, min(256, context // 16))
    input_budget = context - max_tokens - reserve
    if input_budget < 1:
        raise ValueError('context leaves no safe input budget after output and template reserve')
    prompt_tokens = _message_token_cost(model, prompt)
    if prompt_tokens > input_budget:
        raise ValueError(
            f'prompt is too long ({prompt_tokens} estimated tokens; safe input budget {input_budget})')
    return prompt_tokens, input_budget, reserve


def _fit_chat_messages(model, history, prompt, context, max_tokens,
                       max_history_turns, max_history_tokens):
    # Reserve space for chat-template/control tokens and small tokenizer/template
    # differences. The backend still remains authoritative about its real context.
    reserve = max(64, min(256, context // 16))
    input_budget = context - max_tokens - reserve
    prompt_cost = _message_token_cost(model, prompt)
    if prompt_cost > input_budget:
        return None, prompt_cost, input_budget, reserve

    prior_limit = 2 * max(0, max_history_turns - 1)
    prior = history[-prior_limit:] if prior_limit else []
    if len(prior) % 2:
        prior = prior[1:]

    remaining = min(max_history_tokens, input_budget - prompt_cost)
    selected = []
    selected_cost = 0
    # Keep a contiguous suffix of complete user/assistant pairs. If the newest
    # pair cannot fit, older pairs are not cherry-picked out of order.
    for index in range(len(prior) - 2, -1, -2):
        pair = prior[index:index + 2]
        pair_cost = sum(_message_token_cost(model, item['content']) for item in pair)
        if pair_cost > remaining:
            break
        selected = pair + selected
        selected_cost += pair_cost
        remaining -= pair_cost

    request_messages = selected + [{'role': 'user', 'content': prompt}]
    return request_messages, prompt_cost + selected_cost, input_budget, reserve


def chat_session(model_path, expected_sha256, context=2048, max_tokens=256, threads=4,
                 stream=False, max_history_turns=8, max_history_tokens=1024):
    """Run a local chat with bounded turn count and tokenizer-estimated history tokens."""
    _validate_generation('interactive chat', context, max_tokens, threads)
    if type(max_history_turns) is not int or not 1 <= max_history_turns <= 64:
        raise ValueError('max_history_turns must be between 1 and 64')
    if type(max_history_tokens) is not int or not 0 <= max_history_tokens <= 1000000:
        raise ValueError('max_history_tokens must be between 0 and 1000000')
    path = verify_model(model_path, expected_sha256)
    model = _open_model(path, context, threads)
    try:
        if not callable(getattr(model, 'tokenize', None)):
            raise ValueError('runtime tokenizer is required for token-bounded chat history')
        template = _require_template(model)
        messages = []
        turns = 0
        last_input_tokens_estimate = 0
        last_context_reserve = max(64, min(256, context // 16))
        print('RAINY offline chat — /help, /clear, /exit')
        while True:
            try:
                prompt = input('Та: ')
            except EOFError:
                break
            prompt = prompt.strip()
            if not prompt:
                continue
            command = prompt.casefold()
            if command in ('/exit', '/quit'):
                break
            if command == '/help':
                print('/clear — ярианы түүх арилгах; /exit — гарах')
                continue
            if command == '/clear':
                messages.clear()
                print('Ярианы түүх ариллаа.')
                continue

            try:
                request_messages, input_estimate, input_budget, reserve = _fit_chat_messages(
                    model, messages, prompt, context, max_tokens,
                    max_history_turns, max_history_tokens)
            except (RuntimeError, ValueError) as exc:
                print(f'RAINY: Токен тоолол амжилтгүй; энэ асуултыг илгээсэнгүй: {exc}')
                continue
            if request_messages is None:
                print(f'RAINY: Асуулт хэт урт байна (ойролцоогоор {input_estimate} токен; '
                      f'оролтын төсөв {input_budget}). Товчилж дахин илгээнэ үү.')
                continue

            try:
                print('RAINY: ', end='', flush=True)
                if stream:
                    chunks = model.create_chat_completion(
                        messages=request_messages, max_tokens=max_tokens,
                        temperature=0.0, stream=True)
                    pieces = []
                    for chunk in chunks:
                        if not isinstance(chunk, dict):
                            raise ValueError('backend returned a malformed stream chunk')
                        choices = chunk.get('choices') or []
                        if not choices:
                            continue
                        choice = choices[0]
                        if not isinstance(choice, dict):
                            raise ValueError('backend returned a malformed stream choice')
                        delta = choice.get('delta') or {}
                        content = delta.get('content')
                        if content is not None:
                            if not isinstance(content, str):
                                raise ValueError('backend returned non-text assistant content')
                            if content:
                                print(content, end='', flush=True)
                                pieces.append(content)
                    answer = ''.join(pieces)
                    print()
                else:
                    output = model.create_chat_completion(
                        messages=request_messages, max_tokens=max_tokens,
                        temperature=0.0, stream=False)
                    answer = output['choices'][0]['message']['content']
                    if not isinstance(answer, str):
                        raise ValueError('backend returned non-text assistant content')
                    print(answer)
            except Exception:
                raise
            messages = request_messages + [{'role': 'assistant', 'content': answer}]
            turns += 1
            last_input_tokens_estimate = input_estimate
            last_context_reserve = reserve
        return {'turns': turns, 'model_sha256': expected_sha256,
                'chat_template_sha256': hashlib.sha256(template.encode()).hexdigest(),
                'trained_rainy_model': False, 'history_persisted': False,
                'max_history_turns': max_history_turns,
                'max_history_tokens': max_history_tokens,
                'last_input_tokens_estimate': last_input_tokens_estimate,
                'context_safety_reserve_tokens': last_context_reserve}
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
    parser.add_argument('--chat', action='store_true',
                        help='start a bounded interactive chat; history stays in memory only')
    parser.add_argument('--max-history-turns', type=int, default=8,
                        help='maximum user/assistant turns retained in RAM (1..64)')
    parser.add_argument('--max-history-tokens', type=int, default=1024,
                        help='tokenizer-estimated budget for prior turns; current prompt has a separate context budget')
    parser.add_argument('--stream', action='store_true',
                        help='emit NDJSON deltas for one prompt; stream plain text in --chat mode')
    args = parser.parse_args()
    if args.check_only and (args.stream or args.chat):
        parser.error('--stream/--chat cannot be combined with --check-only')
    if args.chat and args.prompt:
        parser.error('--prompt cannot be combined with --chat')
    if not args.chat and not args.check_only and not args.prompt:
        parser.error('--prompt is required unless --chat or --check-only is used')
    if not args.chat and args.max_history_turns != 8:
        parser.error('--max-history-turns is only valid with --chat')
    if not args.chat and args.max_history_tokens != 1024:
        parser.error('--max-history-tokens is only valid with --chat')
    try:
        if args.check_only:
            verify_model(args.model, args.sha256)
            result = {'artifact_integrity': True, 'runtime_compatibility': 'not tested',
                      'inference_executed': False}
        elif args.chat:
            result = chat_session(args.model, args.sha256, args.context, args.max_tokens,
                                  args.threads, args.stream, args.max_history_turns,
                                  args.max_history_tokens)
        elif args.stream:
            for event in generate_stream(args.model, args.sha256, args.prompt,
                                          args.context, args.max_tokens, args.threads):
                print(json.dumps(event, ensure_ascii=False, separators=(',', ':')), flush=True)
            return
        else:
            result = generate(args.model, args.sha256, args.prompt,
                              args.context, args.max_tokens, args.threads)
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        parser.exit(1, f'Offline model: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
