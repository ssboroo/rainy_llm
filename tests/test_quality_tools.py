import json
import unittest
from unittest.mock import patch
from scripts.audit_data import audit
from scripts.export_chat import convert
from scripts.doctor import inspect


def row(i='1', **updates):
    return dict(dict(id=i, instruction='Монгол хэлээр мэндчил', input='', output='Сайн байна уу', source='example', license='test-only', split='train'), **updates)


class QualityTests(unittest.TestCase):
    def test_private_text_not_in_report(self):
        report = audit([row(output='user@example.com password=example 99112233')])
        serialized = json.dumps(report)
        self.assertNotIn('user@example.com', serialized)
        self.assertNotIn('99112233', serialized)
        self.assertEqual(len([f for f in report['findings'] if f['kind'].startswith('possible_')]), 3)

    def test_cross_split_prompt(self):
        report = audit([row(), row('2', split='test')])
        self.assertTrue(any(f.get('cross_split') for f in report['findings']))

    def test_invalid_threshold_or_size(self):
        for kwargs in [dict(threshold=0), dict(threshold=2), dict(max_rows=0)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                audit([row()], **kwargs)

    def test_bad_field(self):
        with self.assertRaises(ValueError):
            audit([row(input=1)])

    def test_only_selected_split_exported(self):
        result = convert([row(), row('2', split='test')], 'train')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['messages'][-1]['role'], 'assistant')
        self.assertEqual(result[0]['source'], 'example')

    def test_input_and_system_preserved(self):
        result = convert([row(input='Нэмэлт нөхцөл')], 'train', 'Монгол хэлээр хариул')
        self.assertEqual(len(result[0]['messages']), 3)
        self.assertIn('Нэмэлт нөхцөл', result[0]['messages'][1]['content'])

    def test_empty_export_rejected(self):
        with self.assertRaises(ValueError):
            convert([row()], 'test')

    @patch('scripts.doctor.shutil.which', return_value=None)
    def test_missing_gpu_command(self, mocked):
        self.assertIn('unknown', inspect()['gpu_probe'])
