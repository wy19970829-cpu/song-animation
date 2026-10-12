# Song Animation · 歌曲文字动画 Skill

把歌曲做成会跳动的文字：逐字弹起、均衡换行、动态背景，并导出带声音的视频。可作为 Codex / 兼容 Agent Skills 的 Skill 使用，也可以单独运行网页。

代码与原创演示素材采用 **MIT 开源协议**。演示为原创合成旋律，没有歌唱人声；替换为自己的歌曲音频即可播放原唱。没有付费 API、云服务或账号依赖。

## 不懂代码，就这样跟 AI 说

先看 [大白话安装与使用说明](USAGE.md)。[下载最新安装包](https://github.com/wy19970829-cpu/song-animation/releases/latest)。

安装时：

> 帮我把这个 song-animation 文件夹安装好，让我以后能做会唱歌、字会跳的网页。

第一次使用时，提供音频和歌词，再说：

> 用歌曲动画 Skill，把我给你的音频和歌词做成会唱歌、字会跳、背景会动的网页，做好后打开给我看。

以后找回自己的项目时：

> 打开我之前做的那个歌词动画，就是会唱歌、字会跳的那个。

有多个项目时说清歌名，例如“打开我的《玫瑰》歌词动画”。《玫瑰》只是说法示例，安装包不包含这首歌。第一次做完后，请 AI 告诉你项目保存在哪里，并把位置保存下来；新对话找不到时，把项目文件夹位置发给它。

接着改，可以直接说：

- “把背景换成海浪，歌曲和歌词不变。”
- “让歌词跳得活泼一点，别让第二行只剩一两个字。”
- “换成我给你的新音频和新歌词。”
- “把这个动画导出成视频，保存好并告诉我在哪。”

如果 AI 没认出这个工具，在话前面加上“使用 $song-animation”。

## 立即运行

需要 Python 3；可选 ffmpeg / ffprobe 用于读取 MP3/M4A 时长或裁剪音频。

源码仓库不需要附带音频二进制；运行演示时若没有 `assets/demo.wav`，构建脚本会在生成目录中自动合成同一段原创演示旋律。安装 ZIP 已包含演示 WAV。

```sh
python3 scripts/build.py examples/demo.json --output demo
python3 -m http.server 8767 --bind 127.0.0.1 --directory demo
```

打开 `http://127.0.0.1:8767`。点播放观看，点“歌曲与背景”更换音频、LRC、预设或图片。右上角“导出视频”会从头录制；等整段播放完成，点“保存视频”。支持的浏览器优先生成 MP4，也可能输出 WebM。当前浏览器画幅决定视频比例，录制期间保持页面打开。

## 安装为 Skill

在 GitHub 仓库点击 **Code → Download ZIP** 下载源码，也可以下载 Releases 中的安装包。解压后的目录如果叫 `song-animation-main`，先重命名为 `song-animation`。

把整个 `song-animation` 文件夹放入 `~/.codex/skills/`，新建或重新打开会话后使用：

> 使用 $song-animation，把这首歌做成歌词动画，背景换成蓝色海浪。

> 使用 $song-animation，保留歌曲和歌词，只把背景改成星空。

> 使用 $song-animation，把这几句歌词换成我提供的新版本，字跳得更活泼。

“一句话修改”由 AI 编辑配置并重建网页，不需要手动改 HTML。只给歌名时仍需补充音频文件；仅有文字没有演唱时间时，会明确标记同步精度为估算。

修改显示歌词不会改变录音里的歌唱内容；要让唱词一起变化，请提供匹配的新音频。

## 自定义与扩展

- 每首歌有独立 `project.json`：歌曲、歌词、背景、动画强度。
- 预设：文字玫瑰、动态海浪、流动星空；支持自定义图片。
- 时间轴：LRC 句时点，或 JSON 逐字时间；纯文本可先预览。
- 导出：同时记录画面和音轨，不含网页按钮。
- 开发者入口：`assets/player.html` 中的 `drawBackdrop()` / `paintExport()`。

字段及命令见 [references/config.md](references/config.md)。运行回归检查：`python3 -m unittest discover -s tests`。

## 分发

可修改、打包、分享代码及本包的原创演示素材，保留 [LICENSE](LICENSE)。自己的歌曲、歌词和图片放在独立项目中；这些素材的授权不由代码的 MIT 协议授予。

可以直接 Fork 仓库，在自己的副本中修改背景、动效或脚本；也可以提交 Pull Request。具体步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。分享源码或安装 ZIP 即可，无需附带个人歌曲项目或浏览器下载文件。
