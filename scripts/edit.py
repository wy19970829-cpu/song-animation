#!/usr/bin/env python3
"""Small deterministic config editor; natural language interpretation belongs to the agent."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description='修改歌曲、歌词或背景配置')
parser.add_argument('config', type=Path)
parser.add_argument('--title')
parser.add_argument('--artist')
parser.add_argument('--audio', type=Path)
parser.add_argument('--lyrics', type=Path, help='JSON 时间轴、LRC 或逐行 TXT')
parser.add_argument('--background', choices=['rose', 'ocean', 'stars'])
parser.add_argument('--image', type=Path)
parser.add_argument('--strength', type=float)
args = parser.parse_args()
config = json.loads(args.config.read_text(encoding='utf-8'))
for key in ('title', 'artist'):
    if getattr(args, key) is not None:
        config[key] = getattr(args, key)
if args.audio:
    config['audio'] = str(args.audio.resolve())
    config.pop('duration', None)
    config.pop('clip', None)
if args.lyrics:
    config.pop('timing', None)
    config.pop('lyrics_file', None)
    if args.lyrics.suffix.lower() == '.lrc':
        config['lyrics_file'] = str(args.lyrics.resolve())
        config.pop('lyrics', None)
    else:
        text = args.lyrics.read_text(encoding='utf-8-sig')
        config['lyrics'] = json.loads(text) if args.lyrics.suffix.lower() == '.json' else [line.strip() for line in text.splitlines() if line.strip()]
if args.background or args.image:
    config.setdefault('background', {})
    if args.background:
        config['background']['preset'] = args.background
        config['background'].pop('image', None)
    if args.image:
        config['background']['image'] = str(args.image.resolve())
if args.strength is not None:
    if not 0 <= args.strength <= 2:
        parser.error('strength 取值 0–2')
    config.setdefault('motion', {})['strength'] = args.strength
args.config.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(str(args.config.resolve()))
