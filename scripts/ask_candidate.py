"""Ask the pinned experimental CPU model one question; no prompt logging."""
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--max-new-tokens', type=int, default=256)
    args = parser.parse_args()
    from huggingface_hub import hf_hub_download
    from transformers import AutoTokenizer
    from llama_cpp import Llama
    tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-4B-Instruct-2507',
        revision='cdbee75f17c01a7cc42f958dc650907174af0554', trust_remote_code=False)
    model_path = hf_hub_download('unsloth/Qwen3-4B-Instruct-2507-GGUF',
        'Qwen3-4B-Instruct-2507-Q4_K_M.gguf', revision='a06e946bb6b655725eafa393f4a9745d460374c9')
    model = Llama(model_path=model_path, n_gpu_layers=0, n_ctx=2048,
        n_threads=4, n_threads_batch=4, seed=42, verbose=False)
    prompt = tokenizer.apply_chat_template([dict(role='user', content=args.prompt)],
        tokenize=False, add_generation_prompt=True)
    if len(model.tokenize(prompt.encode())) + args.max_new_tokens > 2048:
        parser.error('Prompt and output budget exceed the 2048-token context limit.')
    result = model(prompt, max_tokens=args.max_new_tokens, temperature=0.0,
        top_p=1.0, top_k=0, repeat_penalty=1.0, seed=42,
        stop=['<|im_end|>', '<|endoftext|>'])
    print(result['choices'][0]['text'].strip())
    if result['choices'][0]['finish_reason'] == 'length':
        import sys
        print('Output reached the token limit and may be incomplete.', file=sys.stderr)


if __name__ == '__main__':
    main()
