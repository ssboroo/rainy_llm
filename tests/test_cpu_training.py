import json
from pathlib import Path
import tempfile
import unittest
from scripts.train_lora_cpu import prepare, tokenize, snapshot, outside_git, check_resume, digest


class Tokenizer:
    chat_template = 'fixture'
    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        return [1, 2] if add_generation_prompt else [1, 2, 3, 4]


class TrainingTests(unittest.TestCase):
    def test_assistant_mask_and_no_truncation(self):
        rows = [{'messages': [{'role': 'user'}, {'role': 'assistant'}]}]
        item = tokenize(rows, Tokenizer(), 4)[0]
        self.assertEqual(item['labels'], [-100, -100, 3, 4])
        with self.assertRaisesRegex(ValueError, 'truncation'):
            tokenize(rows, Tokenizer(), 3)
        tok = Tokenizer()
        tok.chat_template = ''
        with self.assertRaisesRegex(ValueError, 'template'):
            tokenize(rows, tok, 4)

    def test_non_prefix_template_rejected(self):
        class Bad(Tokenizer):
            def apply_chat_template(self, messages, tokenize, add_generation_prompt):
                return [9] if add_generation_prompt else [1, 2]
        with self.assertRaisesRegex(ValueError, 'prefix'):
            tokenize([{'messages': [{}, {}]}], Bad(), 4)

    def test_model_hash_and_git_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'config.json').write_text('{}')
            (root / 'model.safetensors').write_bytes(b'fixture-not-real-weights')
            old = snapshot(root)
            (root / 'model.safetensors').write_bytes(b'changed')
            self.assertNotEqual(old, snapshot(root))
            (root / '.git').mkdir()
            with self.assertRaisesRegex(ValueError, 'Git'):
                outside_git(root / 'out')

    def test_resume_identity_and_complete_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'run_identity.json').write_text('{"seed":42}')
            cp = root / 'checkpoint-1'
            cp.mkdir()
            with self.assertRaisesRegex(ValueError, 'identity'):
                check_resume(root, cp, {'seed': 43})
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                check_resume(root, cp, {'seed': 42})
            for name in ['adapter_config.json', 'adapter_model.safetensors', 'optimizer.pt',
                         'scheduler.pt', 'rng_state.pth', 'trainer_state.json']:
                (cp / name).write_text('fixture')
            self.assertEqual(check_resume(root, cp, {'seed': 42}), str(cp))
            (cp / 'checkpoint-is-incomplete.txt').touch()
            with self.assertRaisesRegex(ValueError, 'complete'):
                check_resume(root, cp, {'seed': 42})

    def test_review_and_eval_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data, evaluation, review = [root / n for n in ['data', 'eval', 'review']]
            row = dict(id='1', instruction='Сайн уу', output='Сайн', source='fixture', license='CC0-1.0', split='train')
            data.write_text(json.dumps(row)+'\n')
            case = dict(id='e', category='writing', prompt='Өөр асуулт', answers=['a'],
                        review_status='draft-needs-human-review', source='fixture-eval')
            evaluation.write_text(json.dumps(case)+'\n')
            review.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'attestation'):
                prepare(data, evaluation, review)
            approval = dict(data_sha256=digest(data), reviewer_role='human-reviewer', reviewer='test-fixture-only',
                            quality_reviewed=True, privacy_reviewed=True, training_rights_verified=True,
                            approved_source_licenses=[dict(source='fixture', license='CC0-1.0')])
            review.write_text(json.dumps(approval))
            self.assertEqual(len(prepare(data, evaluation, review)), 1)
            case['prompt'] = row['instruction']
            evaluation.write_text(json.dumps(case)+'\n')
            with self.assertRaisesRegex(ValueError, 'overlap'):
                prepare(data, evaluation, review)
            case['prompt'] = 'Өөр асуулт'
            evaluation.write_text(json.dumps(case)+'\n')
            row['output'] = 'Өөр'
            data.write_text(json.dumps(row)+'\n')
            with self.assertRaisesRegex(ValueError, 'attestation'):
                prepare(data, evaluation, review)


if __name__ == '__main__':
    unittest.main()
