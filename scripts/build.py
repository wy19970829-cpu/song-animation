#!/usr/bin/env python3
"""Build an offline song animation page using only Python's standard library."""
import argparse
import html
import json
import math
import re
import shutil
import subprocess
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def create_demo(path):
    """Generate the original, voice-free demo when cloning source without binaries."""
    rate, seconds = 22050, 24
    notes = [261.63, 329.63, 392, 329.63, 293.66, 349.23, 440, 349.23]
    samples = bytearray()
    for index in range(rate * seconds):
        t = index / rate
        beat = t % 1.5
        frequency = notes[int(t / 1.5) % len(notes)]
        gain = min(1, beat / .04) * math.exp(-beat * 2.3) * min(1, (seconds-t) / .4)
        value = (math.sin(2*math.pi*frequency*t) + .28*math.sin(2*math.pi*frequency*2*t)) * .19 * gain
        samples.extend(struct.pack('<h', int(max(-1, min(1, value))*32767)))
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples)


def read_lrc(path):
    rows = []
    offset = 0.0
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        match = re.search(r'\[offset:([+-]?\d+)\]', line)
        if match:
            offset = float(match[1]) / 1000
        text = re.sub(r'\[[^]]+\]', '', line).strip()
        for stamp in re.finditer(r'\[(\d+):(\d{2})(?:[.:](\d{1,3}))?\]', line):
            if text:
                rows.append(dict(time=int(stamp[1]) * 60 + int(stamp[2]) + float('0.' + (stamp[3] or '0')), text=text))
    for row in rows:
        row['time'] = max(0, row['time'] - offset)
    if not rows:
        raise ValueError('LRC 没有带时间的歌词；纯文本请放在 lyrics 数组中。')
    return sorted(rows, key=lambda row: row['time'])


def audio_duration(path):
    if path.suffix.lower() == '.wav':
        with wave.open(str(path)) as wav:
            return wav.getnframes() / wav.getframerate()
    probe = shutil.which('ffprobe')
    if not probe:
        raise ValueError('非 WAV 音频需要 ffprobe，或在配置中提供 duration 秒数。')
    result = subprocess.run([probe, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)], check=True, capture_output=True, text=True)
    return float(result.stdout)


def normalize_rows(raw, duration):
    if not isinstance(raw, list) or not raw:
        raise ValueError('lyrics 需要至少一句歌词。')
    estimated = any(isinstance(row, str) or 'time' not in row for row in raw)
    rows = [dict(time=duration*i/len(raw), text=row) if isinstance(row, str) else dict(row) for i, row in enumerate(raw)]
    if any('time' not in row for row in rows):
        raise ValueError('不要混用带时间和不带时间的歌词。')
    previous = -1.0
    for index, row in enumerate(rows):
        row['time'] = float(row['time'])
        if row['time'] <= previous or not 0 <= row['time'] < duration:
            raise ValueError('歌词 time 必须递增，并位于音频时长内。')
        previous = row['time']
        if not isinstance(row.get('text'), str) or not row['text'].strip():
            raise ValueError('歌词 text 不能为空。')
        next_time = float(rows[index+1]['time']) if index+1 < len(rows) else duration
        row['end'] = float(row.get('end', next_time))
        row['vocalEnd'] = float(row.get('vocalEnd', row['end']))
        if not row['time'] < row['vocalEnd'] <= next_time + 0.5 or not row['time'] < row['end'] <= next_time:
            raise ValueError('end / vocalEnd 应在本句开始和下一句之间。')
        if row.get('words'):
            count = len(row['text'].replace('\n', ''))
            if len(row['words']) != count:
                raise ValueError('words 数量需要与歌词字数一致（不含换行）。')
            start = row['time']
            for word in row['words']:
                if not start <= float(word['start']) < float(word['end']) <= row['vocalEnd'] + .01:
                    raise ValueError('逐字时间需递增，且位于本句 vocalEnd 内。')
                start = float(word['end'])
    return rows, estimated


def build(config_path, output):
    config_path, output = Path(config_path).resolve(), Path(output).resolve()
    config = json.loads(config_path.read_text(encoding='utf-8'))
    source = (config_path.parent / config.get('audio', '')).resolve()
    if not source.is_file() and source == ROOT / 'assets/demo.wav':
        output.mkdir(parents=True, exist_ok=True)
        source = output / 'music.wav'
        create_demo(source)
    if not source.is_file():
        raise ValueError('找不到 audio 指定的本地音频。')
    duration = float(config['duration']) if config.get('duration') else audio_duration(source)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('duration 必须是正数。')
    output.mkdir(parents=True, exist_ok=True)
    clip = config.get('clip')
    name = 'music' + ('.m4a' if clip else source.suffix.lower())
    target = output / name
    if clip:
        start, end = float(clip.get('start', 0)), float(clip['end'])
        if not 0 <= start < end <= duration + .1:
            raise ValueError('clip 起止时间超出音频范围。')
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            raise ValueError('裁剪音频需要 ffmpeg。')
        subprocess.run([ffmpeg, '-v', 'error', '-y', '-ss', str(start), '-i', str(source), '-t', str(end-start), '-c:a', 'aac', '-b:a', '160k', str(target)], check=True)
        duration = end-start
    elif source != target:
        shutil.copyfile(source, target)
    raw = read_lrc(config_path.parent / config['lyrics_file']) if config.get('lyrics_file') else config.get('lyrics')
    rows, estimated = normalize_rows(raw, duration)
    estimated = estimated or config.get('timing') == 'estimated'
    background = dict(config.get('background', {}))
    if background.get('preset', 'rose') not in ('rose', 'ocean', 'stars'):
        raise ValueError('background.preset 支持 rose / ocean / stars。')
    if background.get('image'):
        image = (config_path.parent / background['image']).resolve()
        if image.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            raise ValueError('背景图片支持 PNG / JPEG / WebP。')
        shutil.copyfile(image, output / ('background' + image.suffix.lower()))
        background['image'] = 'background' + image.suffix.lower()
    timing = 'estimated' if estimated else 'character' if all(row.get('words') for row in rows) else 'sentence'
    payload = dict(title=config.get('title', '文字音乐'), artist=config.get('artist', ''), audio=name, duration=duration, lyrics=rows, background=background, motion=config.get('motion', {}), estimated=estimated, timing=timing, offset=float(config.get('offset', 0)))
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = (ROOT / 'assets/player.html').read_text(encoding='utf-8')
    page = template.replace('__CONFIG_JSON__', encoded).replace('__AUDIO_FILE__', html.escape(name, quote=True))
    (output / 'index.html').write_text(page, encoding='utf-8')
    portable = {key: value for key, value in payload.items() if key != 'estimated'}
    (output / 'project.json').write_text(json.dumps(portable, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(page=str(output / 'index.html'), duration=round(duration, 3), lyrics=len(rows), timing=timing), ensure_ascii=False))
    return output / 'index.html'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='构建音乐文字动画网页')
    parser.add_argument('config', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.config, args.output)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')
