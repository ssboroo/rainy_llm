import unittest
from scripts.prepare_data import prepare
from scripts.evaluate import score


def row(i, source='s', prompt=None):
    return dict(id=str(i), instruction=prompt or f'Асуулт {i}', input='', output='Хариу', source=source, license='test-only')


class PipelineTests(unittest.TestCase):
    def test_same_source_stays_together(self):
        rows, report = prepare([row(1), row(2)])
        self.assertEqual(len({r['split'] for r in rows}), 1)
        self.assertEqual(report['groups'], 1)

    def test_prompt_connects_sources(self):
        rows, report = prepare([row(1, 'a', 'Ижил'), dict(row(2, 'b', 'Ижил'), output='Өөр'), row(3, 'b')])
        self.assertEqual(report['groups'], 1)
        self.assertEqual(len({r['split'] for r in rows}), 1)

    def test_order_independent(self):
        rows = [row(i, str(i)) for i in range(30)]
        self.assertEqual(prepare(rows), prepare(list(reversed(rows))))

    def test_deduplicate(self):
        rows, report = prepare([row(1, prompt='Ижил'), row(2, prompt='Ижил')])
        self.assertEqual(len(rows), 1)
        self.assertEqual(report['removed_exact_duplicates'], 1)

    def test_heldout_rejected(self):
        with self.assertRaises(ValueError):
            prepare([row(1, prompt='Нууц тест')], heldout=['Нууц тест'])

    def test_invalid_data(self):
        for rows in [[], [row(1), row(1)], [dict(row(1), license='')], [dict(row(1), input=3)]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                prepare(rows)

    def test_score_missing_in_denominator(self):
        cases = [dict(id=str(i), prompt='Асуулт', category='test', answers=['Сайн']) for i in range(2)]
        report = score(cases, [dict(id='0', output=' САЙН ')])
        self.assertEqual(report['accuracy'], .5)
        self.assertEqual(report['missing'], 1)

    def test_score_rejects_unknown_and_duplicate(self):
        cases = [dict(id='0', prompt='Асуулт', category='test', answers=['Сайн'])]
        for predictions in [[dict(id='x', output='')], [dict(id='0', output='Сайн')]*2]:
            with self.subTest(predictions=predictions), self.assertRaises(ValueError):
                score(cases, predictions)

    def test_empty_eval_fails(self):
        with self.assertRaises(ValueError):
            score([], [])

    def test_bad_case_fails(self):
        with self.assertRaises(ValueError):
            score([dict(id='1', prompt='a', category='b', answers='wrong')], [])
