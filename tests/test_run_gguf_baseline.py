import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

from run_gguf_baseline import render_prompt


class FakeTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        self.messages = messages
        self.kwargs = kwargs
        return 'rendered prompt'


class RenderPromptTests(unittest.TestCase):
    def test_passes_explicit_non_thinking_mode(self):
        tokenizer = FakeTokenizer()

        rendered = render_prompt(tokenizer, 'Сайн уу?', thinking=False)

        self.assertEqual(rendered, 'rendered prompt')
        self.assertEqual(tokenizer.messages, [{'role': 'user', 'content': 'Сайн уу?'}])
        self.assertEqual(tokenizer.kwargs, {
            'tokenize': False,
            'add_generation_prompt': True,
            'enable_thinking': False,
        })

    def test_can_enable_thinking_mode(self):
        tokenizer = FakeTokenizer()

        render_prompt(tokenizer, 'Бодож хариул.', thinking=True)

        self.assertTrue(tokenizer.kwargs['enable_thinking'])


if __name__ == '__main__':
    unittest.main()
