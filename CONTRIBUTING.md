# 修改与贡献

任何人都可以下载、Fork、修改本项目；代码和原创演示素材使用 MIT 协议。

## 改自己的歌曲

建立独立歌曲目录，在其中保存音频和 `project.json`，然后调用 `scripts/build.py`。自然语言修改由使用本 Skill 的 AI 完成；也可以手动编辑配置。字段说明见 [references/config.md](references/config.md)。

## 改背景或动效

1. Fork GitHub 仓库，在自己的副本中开一个分支。
2. 编辑 `assets/player.html`。背景入口是 `drawBackdrop()`；文字动效入口是 `updateKaraoke()`；视频合成入口是 `paintExport()`。
3. 用 `examples/demo.json` 构建演示，实际播放并检查导出效果。
4. 运行 `python3 -m unittest discover -s tests`，然后在 GitHub 提交 Pull Request。

也欢迎直接提交 Issue，说明遇到的问题、浏览器和复现步骤。

修改时保留均衡换行、暂停时的动画状态，以及歌词估算精度提示。添加新背景时同步更新配置校验和背景选择菜单。

公开贡献使用本包的原创演示素材；个人音频、歌词、图片和 `references/local-projects.json` 留在自己的歌曲目录中。
