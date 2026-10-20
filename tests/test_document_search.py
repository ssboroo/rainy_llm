import tempfile
import unittest
from pathlib import Path
from scripts.search_documents import search_documents


class DocumentSearchTests(unittest.TestCase):
    def test_mongolian_source_lines_and_no_match(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'policy.md'
            path.write_text('\n' * 12 + 'Хүргэлт ажлын хоёр хоногт хийгдэнэ.\n', encoding='utf-8')
            hit = search_documents(folder, 'ХҮРГЭЛТ')['results'][0]
            self.assertEqual((hit['path'], hit['line_start'], hit['line_end']), ('policy.md', 13, 13))
            self.assertEqual(hit['excerpt'], path.read_text(encoding='utf-8').splitlines()[12])
            self.assertEqual(search_documents(folder, 'сансрын')['results'], [])

    def test_changes_and_deletion_are_visible(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'one.txt'
            path.write_text('Хүргэлт', encoding='utf-8')
            old = search_documents(folder, 'Хүргэлт')['snapshot']
            path.write_text('Төлбөр', encoding='utf-8')
            new = search_documents(folder, 'Хүргэлт')
            self.assertEqual(new['results'], [])
            self.assertNotEqual(old, new['snapshot'])
            path.unlink()
            self.assertEqual(search_documents(folder, 'Төлбөр')['files_indexed'], 0)

    def test_hidden_symlink_and_nontext_files_excluded(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / 'secret.txt'
            secret.write_text('нууц', encoding='utf-8')
            (Path(folder) / 'link.txt').symlink_to(secret)
            (Path(folder) / 'linked').symlink_to(outside, target_is_directory=True)
            (Path(folder) / '.secret.txt').write_text('нууц', encoding='utf-8')
            (Path(folder) / 'data.csv').write_text('нууц', encoding='utf-8')
            self.assertEqual(search_documents(folder, 'нууц')['files_indexed'], 0)

    def test_query_syntax_is_literal_and_limits_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'one.txt').write_text('Хүргэлт', encoding='utf-8')
            self.assertEqual(len(search_documents(folder, '"Хүргэлт" OR NOT *')['results']), 1)
            for query in ['', '***', 'a' * 1001]:
                with self.assertRaises(ValueError):
                    search_documents(folder, query)
            (Path(folder) / 'big.txt').write_bytes(b'a' * (1024 * 1024 + 1))
            with self.assertRaisesRegex(ValueError, 'size limit'):
                search_documents(folder, 'Хүргэлт')
