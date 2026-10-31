import io
import json
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.ask_offline import chat_session, main, verify_model


class OfflineChatSessionTests(unittest.TestCase):
    def setUp(self):
        self.model = MagicMock()
        self.model.metadata = {'tokenizer.chat_template': 'fixture-template'}
        self.model.tokenize.side_effect = lambda text, add_bos=False, special=True: [1] * len(text.decode('utf-8'))
        self.factory = MagicMock(return_value=self.model)
        self.patchers = [
            patch('scripts.ask_offline.verify_model', return_value=Path('/local/model.gguf')),
            patch.dict('sys.modules', {'llama_cpp': types.SimpleNamespace(Llama=self.factory)}),
        ]
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop)

    def test_reuses_one_model_and_carries_assistant_history(self):
        self.model.create_chat_completion.side_effect = [
            {'choices': [{'message': {'content': 'Эхний хариу'}}]},
            {'choices': [{'message': {'content': 'Хоёр дахь хариу'}}]},
        ]
        output = io.StringIO()
        with patch('builtins.input', side_effect=['Сайн уу', 'Намайг санаж байна уу?', '/exit']), redirect_stdout(output):
            result = chat_session('/local/model.gguf', 'a' * 64, max_history_turns=4)
        self.assertEqual(result['turns'], 2)
        self.assertFalse(result['history_persisted'])
        self.assertFalse(result['trained_rainy_model'])
        self.factory.assert_called_once()
        self.model.close.assert_called_once()
        self.assertEqual(self.model.create_chat_completion.call_count, 2)
        second_messages = self.model.create_chat_completion.call_args_list[1].kwargs['messages']
        self.assertEqual(second_messages, [
            {'role': 'user', 'content': 'Сайн уу'},
            {'role': 'assistant', 'content': 'Эхний хариу'},
            {'role': 'user', 'content': 'Намайг санаж байна уу?'},
        ])
        self.assertIn('Эхний хариу', output.getvalue())

    def test_history_limit_keeps_only_current_turn_when_one(self):
        self.model.create_chat_completion.side_effect = [
            {'choices': [{'message': {'content': 'A'}}]},
            {'choices': [{'message': {'content': 'B'}}]},
        ]
        with patch('builtins.input', side_effect=['Нэг', 'Хоёр', '/exit']), redirect_stdout(io.StringIO()):
            chat_session('/local/model.gguf', 'a' * 64, max_history_turns=1)
        self.assertEqual(self.model.create_chat_completion.call_args_list[1].kwargs['messages'], [
            {'role': 'user', 'content': 'Хоёр'}
        ])

    def test_clear_command_removes_prior_context(self):
        self.model.create_chat_completion.side_effect = [
            {'choices': [{'message': {'content': 'A'}}]},
            {'choices': [{'message': {'content': 'B'}}]},
        ]
        with patch('builtins.input', side_effect=['Нэг', '/clear', 'Хоёр', '/exit']), redirect_stdout(io.StringIO()):
            chat_session('/local/model.gguf', 'a' * 64)
        self.assertEqual(self.model.create_chat_completion.call_args_list[1].kwargs['messages'], [
            {'role': 'user', 'content': 'Хоёр'}
        ])

    def test_stream_mode_prints_deltas_and_saves_complete_assistant_turn(self):
        self.model.create_chat_completion.side_effect = [
            iter([
                {'choices': [{'delta': {'content': 'Урсгал '}, 'finish_reason': None}]},
                {'choices': [{'delta': {'content': 'хариу'}, 'finish_reason': 'stop'}]},
            ]),
            iter([{'choices': [{'delta': {'content': 'Дараагийн хариу'}, 'finish_reason': 'stop'}]}]),
        ]
        output = io.StringIO()
        with patch('builtins.input', side_effect=['Эхний асуулт', 'Дараагийн асуулт', '/exit']), redirect_stdout(output):
            result = chat_session('/local/model.gguf', 'a' * 64, stream=True)
        self.assertEqual(result['turns'], 2)
        self.assertIn('RAINY: Урсгал хариу', output.getvalue())
        self.assertTrue(self.model.create_chat_completion.call_args_list[0].kwargs['stream'])
        second_messages = self.model.create_chat_completion.call_args_list[1].kwargs['messages']
        self.assertEqual(second_messages[1], {'role': 'assistant', 'content': 'Урсгал хариу'})
        self.assertTrue(self.model.create_chat_completion.call_args_list[1].kwargs['stream'])

    def test_bad_hash_refuses_before_opening_chat_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.gguf'
            path.write_bytes(b'GGUFtest-fixture-not-real-weights')
            with patch('scripts.ask_offline.verify_model', wraps=verify_model):
                with self.assertRaisesRegex(ValueError, 'mismatch'):
                    chat_session(path, '0' * 64)
        self.factory.assert_not_called()

    def test_invalid_history_limit_refuses_before_loading_model(self):
        with self.assertRaisesRegex(ValueError, 'between 1 and 64'):
            chat_session('/local/model.gguf', 'a' * 64, max_history_turns=0)
        self.factory.assert_not_called()

    def test_backend_failure_closes_model_and_does_not_return_a_session(self):
        self.model.create_chat_completion.side_effect = RuntimeError('backend failure')
        with patch('builtins.input', side_effect=['асуулт']), redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'backend failure'):
                chat_session('/local/model.gguf', 'a' * 64)
        self.model.close.assert_called_once()

    def test_missing_template_refuses_chat_and_closes_model(self):
        self.model.metadata = {}
        with self.assertRaisesRegex(ValueError, 'template'):
            chat_session('/local/model.gguf', 'a' * 64)
        self.model.create_chat_completion.assert_not_called()
        self.model.close.assert_called_once()

    def test_history_token_budget_keeps_newest_complete_pair(self):
        self.model.create_chat_completion.side_effect = [
            {'choices': [{'message': {'content': 'A'}}]},
            {'choices': [{'message': {'content': 'B'}}]},
            {'choices': [{'message': {'content': 'C'}}]},
        ]
        with patch('builtins.input', side_effect=['old', 'recent', 'now', '/exit']), redirect_stdout(io.StringIO()):
            chat_session('/local/model.gguf', 'a' * 64, max_history_turns=4, max_history_tokens=30)
        self.assertEqual(self.model.create_chat_completion.call_args_list[2].kwargs['messages'], [
            {'role': 'user', 'content': 'recent'},
            {'role': 'assistant', 'content': 'B'},
            {'role': 'user', 'content': 'now'},
        ])

    def test_overlong_current_prompt_is_refused_without_backend_call(self):
        self.model.create_chat_completion.return_value = {'choices': [{'message': {'content': 'Хариу'}}]}
        output = io.StringIO()
        with patch('builtins.input', side_effect=['x' * 300, 'ok', '/exit']), redirect_stdout(output):
            result = chat_session('/local/model.gguf', 'a' * 64, context=512,
                                  max_tokens=256, max_history_tokens=100)
        self.assertEqual(result['turns'], 1)
        self.assertEqual(self.model.create_chat_completion.call_count, 1)
        self.assertIn('Асуулт хэт урт байна', output.getvalue())

    def test_missing_runtime_tokenizer_fails_closed_and_closes_model(self):
        self.model.tokenize = None
        with self.assertRaisesRegex(ValueError, 'tokenizer is required'):
            chat_session('/local/model.gguf', 'a' * 64)
        self.model.create_chat_completion.assert_not_called()
        self.model.close.assert_called_once()

    def test_invalid_history_token_budget_refuses_before_loading_model(self):
        with self.assertRaisesRegex(ValueError, 'between 0 and 1000000'):
            chat_session('/local/model.gguf', 'a' * 64, max_history_tokens=-1)
        self.factory.assert_not_called()

    def test_chat_cli_prints_session_identity(self):
        expected = {'turns': 1, 'model_sha256': 'a' * 64,
                    'chat_template_sha256': 'b' * 64, 'trained_rainy_model': False,
                    'history_persisted': False, 'max_history_turns': 8,
                    'max_history_tokens': 1024, 'last_input_tokens_estimate': 0,
                    'context_safety_reserve_tokens': 128}
        output = io.StringIO()
        argv = ['ask_offline.py', '--model', '/local/model.gguf', '--sha256', 'a' * 64, '--chat', '--stream']
        with patch('sys.argv', argv), patch('scripts.ask_offline.chat_session', return_value=expected), redirect_stdout(output):
            main()
        self.assertEqual(json.loads(output.getvalue()), expected)

    def test_chat_and_check_only_are_mutually_exclusive(self):
        argv = ['ask_offline.py', '--model', '/local/model.gguf', '--sha256', 'a' * 64, '--chat', '--check-only']
        with patch('sys.argv', argv), self.assertRaises(SystemExit) as raised:
            main()
        self.assertEqual(raised.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
