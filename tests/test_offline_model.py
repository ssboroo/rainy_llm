import hashlib
import io
import json
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch
from scripts.ask_offline import generate, generate_stream, main, verify_model


class OfflineModelTests(unittest.TestCase):
    def test_integrity_before_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.gguf'
            path.write_bytes(b'GGUFtest-fixture-not-real-weights')
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(verify_model(path, sha), path)
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                generate(path, '0' * 64, 'Сайн уу')
            path.write_bytes(b'not a model')
            with self.assertRaisesRegex(ValueError, 'header'):
                verify_model(path, sha)

    def test_local_model_call_and_cleanup(self):
        model = MagicMock()
        model.metadata = {'tokenizer.chat_template': 'fixture-template'}
        model.create_chat_completion.return_value = {
            'choices': [{'message': {'content': 'mock хариу'}, 'finish_reason': 'stop'}]}
        factory = MagicMock(return_value=model)
        with patch('scripts.ask_offline.verify_model', return_value=Path('/local/model.gguf')), patch.dict('sys.modules', {'llama_cpp': types.SimpleNamespace(Llama=factory)}):
            result = generate('/local/model.gguf', 'a' * 64, 'Сайн уу')
        self.assertEqual(factory.call_args.kwargs['model_path'], '/local/model.gguf')
        self.assertEqual(factory.call_args.kwargs['n_gpu_layers'], 0)
        self.assertEqual(result['output'], 'mock хариу')
        model.close.assert_called_once()

    def test_missing_template_refuses_generation(self):
        model = MagicMock()
        model.metadata = {}
        with patch('scripts.ask_offline.verify_model', return_value=Path('/local/model.gguf')), patch.dict('sys.modules', {'llama_cpp': types.SimpleNamespace(Llama=lambda **kw: model)}):
            with self.assertRaisesRegex(ValueError, 'template'):
                generate('/local/model.gguf', 'a' * 64, 'Сайн уу')
        model.create_chat_completion.assert_not_called()
        model.close.assert_called_once()


    def test_stream_emits_text_deltas_and_terminal_metadata(self):
        model = MagicMock()
        model.metadata = {'tokenizer.chat_template': 'fixture-template'}
        model.create_chat_completion.return_value = iter([
            {'choices': [{'delta': {'content': 'Монгол '}, 'finish_reason': None}]},
            {'choices': [{'delta': {'content': 'хариу'}, 'finish_reason': None}]},
            {'choices': [{'delta': {}, 'finish_reason': 'stop'}],
             'usage': {'completion_tokens': 2}},
        ])
        with patch('scripts.ask_offline.verify_model', return_value=Path('/local/model.gguf')), patch.dict('sys.modules', {'llama_cpp': types.SimpleNamespace(Llama=lambda **kw: model)}):
            events = list(generate_stream('/local/model.gguf', 'a' * 64, 'Сайн уу'))
        self.assertEqual(events[0], {'type': 'delta', 'text': 'Монгол '})
        self.assertEqual(events[1], {'type': 'delta', 'text': 'хариу'})
        self.assertEqual(events[-1]['type'], 'done')
        self.assertEqual(events[-1]['finish_reason'], 'stop')
        self.assertEqual(events[-1]['usage'], {'completion_tokens': 2})
        self.assertFalse(events[-1]['trained_rainy_model'])
        model.create_chat_completion.assert_called_once()
        self.assertTrue(model.create_chat_completion.call_args.kwargs['stream'])
        model.close.assert_called_once()

    def test_stream_refuses_missing_template_and_closes(self):
        model = MagicMock()
        model.metadata = {}
        with patch('scripts.ask_offline.verify_model', return_value=Path('/local/model.gguf')), patch.dict('sys.modules', {'llama_cpp': types.SimpleNamespace(Llama=lambda **kw: model)}):
            with self.assertRaisesRegex(ValueError, 'template'):
                list(generate_stream('/local/model.gguf', 'a' * 64, 'Сайн уу'))
        model.create_chat_completion.assert_not_called()
        model.close.assert_called_once()

    def test_stream_cli_writes_ndjson_events(self):
        events = [{'type': 'delta', 'text': 'Сайн '}, {'type': 'delta', 'text': 'уу'},
                  {'type': 'done', 'finish_reason': 'stop', 'usage': None,
                   'model_sha256': 'a' * 64, 'chat_template_sha256': 'b' * 64,
                   'trained_rainy_model': False}]
        output = io.StringIO()
        argv = ['ask_offline.py', '--model', '/local/model.gguf', '--sha256', 'a' * 64,
                '--prompt', 'Сайн уу', '--stream']
        with patch('sys.argv', argv), patch('scripts.ask_offline.generate_stream', return_value=iter(events)), redirect_stdout(output):
            main()
        lines = output.getvalue().splitlines()
        self.assertEqual([json.loads(line) for line in lines], events)
        self.assertEqual(len(lines), 3)

    def test_stream_and_check_only_are_mutually_exclusive(self):
        argv = ['ask_offline.py', '--model', '/local/model.gguf', '--sha256', 'a' * 64,
                '--check-only', '--stream']
        with patch('sys.argv', argv), self.assertRaises(SystemExit) as raised:
            main()
        self.assertEqual(raised.exception.code, 2)
