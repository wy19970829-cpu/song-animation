# 配置与扩展

`project.json` 是每首歌曲可独立编辑、重建的源文件。`scripts/build.py` 不需要第三方 Python 包；音频为 WAV 时自动读取时长，其他格式用 ffprobe，或显式给出 `duration`。裁剪需要 ffmpeg。生成文件可以双击播放，视频导出使用 HTTP 预览。

```json
{
  "title": "歌名",
  "artist": "演唱者",
  "audio": "my-song.mp3",
  "duration": 120,
  "lyrics": [
    {"time": 2, "text": "第一句歌词", "vocalEnd": 5},
    {"time": 6, "text": "第二句歌词", "vocalEnd": 9}
  ],
  "background": {"preset": "ocean", "image": "海边.jpg", "imageOpacity": 0.48},
  "motion": {"strength": 1.3},
  "offset": 0
}
```

- `audio`：相对配置文件的路径或绝对路径。构建会复制音频，生成项目可独立搬运。
- `duration`：音频时长，通常省略并自动读取。
- `lyrics`：带时间的句数组，或不带时间的纯文本数组。纯文本时间按时长均分并在页面标识为估算。
- `lyrics_file`：代替 `lyrics`，指向标准 LRC 文件。多时点、毫秒及 `[offset:...]` 均支持。
- `time`：本句显示时间；`end`：字幕结束时间，默认下一句起点；`vocalEnd`：本句唱完时间。设置 `end` 早于下一句可显示间奏。
- `words`：逐字 `{ "start": 2, "end": 2.3 }` 数组，与 `text` 的字符数量相同（不含换行）。时间单位均为秒，递增、不重叠。没有 `words` 时逐字动效由句时点插值。
- `chorus`：句对象中设为 `true` 使用副歌字体。
- `clip`：例如 `{ "start": 28, "end": 206 }`，构建时截取音频；歌词时间必须以截取后片段的 0 秒为起点。省略则保留全部音频。
- `background.preset`：`rose` 文字玫瑰、`ocean` 动态海浪、`stars` 流动星空。
- `background.image`：可选 PNG/JPEG/WebP，叠加在动画背景下；`imageOpacity` 默认 0.48。
- `background.color / accent`：可选 CSS 颜色，控制底色与界面强调色。
- `motion.strength`：0–2，默认 1，控制文字跳跃幅度。系统“减少动态效果”设置优先。
- `offset`：歌词提前秒数，负数表示延后。

## 一句话修改的含义

自然语言由使用 Skill 的 AI 解释并编辑配置；网页不调用付费模型、没有隐藏的聊天接口。例：“把背景换成蓝色海浪，歌词跳得更明显，其他不变。”AI 将背景设为 `ocean`、强度设为 `1.4`，重建并实际预览。

```sh
python3 scripts/edit.py /path/to/project.json --background ocean --strength 1.4
python3 scripts/edit.py /path/to/project.json --audio /path/to/new.mp3 --lyrics /path/to/new.lrc --title "新歌" --artist "演唱者"
python3 scripts/build.py /path/to/project.json --output /path/to/page
```

## 自己扩展背景

复制 `assets/player.html` 到独立开发副本。背景入口是 `drawBackdrop(t,cx,cy,scale)`；背景为 Canvas 2D，可以画粒子、海浪或添加 `drawImage`。`amplitude` 是当前音乐强度，`t` 在暂停时停止；`draw()` 同步更新歌词，`paintExport()` 将背景与文字合成为视频画面。保留 `__CONFIG_JSON__` 和 `__AUDIO_FILE__` 两个构建占位符。

三个预设均会进入导出画面。自定义图片通过浏览器本地导入时只是当前会话，长期保留应写入配置。没有内置麦克风、系统录屏、云上传或账号要求。
