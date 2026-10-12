import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('song_build', ROOT / 'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SongBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = json.loads((ROOT / 'examples/demo.json').read_text())
        self.config['audio'] = str(ROOT / 'assets/demo.wav')

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        path = self.root / 'song.json'
        path.write_text(json.dumps(self.config, ensure_ascii=False), encoding='utf-8')
        return path

    def test_changed_background_preserves_song_and_rebuilds_portably(self):
        path = self.write()
        subprocess.run([sys.executable, str(ROOT / 'scripts/edit.py'), str(path), '--background', 'ocean', '--strength', '1.4'], check=True, capture_output=True)
        changed = json.loads(path.read_text())
        self.assertEqual(changed['lyrics'], self.config['lyrics'])
        self.assertEqual(changed['audio'], self.config['audio'])
        page = builder.build(path, self.root / 'out')
        self.assertIn('"preset":"ocean"', page.read_text())
        self.assertEqual(builder.audio_duration(page.parent / 'music.wav'), 24)
        rebuilt = builder.build(page.parent / 'project.json', self.root / 'rebuilt')
        self.assertTrue((rebuilt.parent / 'music.wav').exists())

    def test_plain_text_keeps_estimation_after_rebuild_and_escapes_html(self):
        self.config['title'] = '</script><script>alert(1)</script>'
        self.config['lyrics'] = ['新的第一句', '新的第二句']
        page = builder.build(self.write(), self.root / 'out')
        self.assertNotIn(self.config['title'], page.read_text())
        self.assertIn('"timing":"estimated"', page.read_text())
        rebuilt = builder.build(page.parent / 'project.json', self.root / 'again')
        self.assertIn('"timing":"estimated"', rebuilt.read_text())

    def test_lrc_offset_multi_timestamp_and_validation(self):
        lrc = self.root / 'song.lrc'
        lrc.write_text('[offset:100]\n[00:01.50][00:04.500]你好\n[00:08.00]世界', encoding='utf-8')
        self.assertEqual([row['time'] for row in builder.read_lrc(lrc)], [1.4, 4.4, 7.9])
        self.config.pop('lyrics')
        self.config['lyrics_file'] = 'song.lrc'
        page = builder.build(self.write(), self.root / 'lrc')
        self.assertIn('"timing":"sentence"', page.read_text())
        with self.assertRaises(ValueError):
            builder.normalize_rows([dict(time=25, text='超出音频')], 24)
        with self.assertRaises(ValueError):
            builder.normalize_rows([dict(time=1, text='两字', words=[dict(start=1, end=2)])], 24)

    def test_import_new_audio_clears_old_duration_and_clip(self):
        self.config['duration'] = 100
        self.config['clip'] = dict(start=20, end=40)
        path = self.write()
        subprocess.run([sys.executable, str(ROOT / 'scripts/edit.py'), str(path), '--audio', str(ROOT / 'assets/demo.wav')], check=True, capture_output=True)
        changed = json.loads(path.read_text())
        self.assertNotIn('duration', changed)
        self.assertNotIn('clip', changed)


if __name__ == '__main__':
    unittest.main()
