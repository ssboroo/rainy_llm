import hashlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from scripts.ask_offline import generate, verify_model


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
