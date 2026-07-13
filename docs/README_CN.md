# markdown2cheatsheet

将 Markdown 笔记转换为高密度、可打印的 cheatsheet，并提供可直接使用的本地图形界面。

[English README](../README.md)  
[使用手册](USAGE_CN.md)  
[开发说明](DEVELOPMENT_CN.md)

## 效果预览

![效果预览](../outputview.jpg)

## 功能特点

- 支持 `2 / 3 / 4 / 5 / 6` 栏输出
- 可直接选择颜色模板、字体、字号和行间距
- 通过 Pandoc 生成自包含 HTML
- 提供本地图形界面，可导入 Markdown、预览结果并下载 HTML
- 命令行和图形界面共用同一套转换核心

## 依赖

| 工具 | 用途 | 安装方式 |
| --- | --- | --- |
| [Pandoc](https://pandoc.org) | Markdown 转独立 HTML | macOS: `brew install pandoc` · Ubuntu/Debian: `sudo apt install pandoc` · Fedora: `sudo dnf install pandoc` · Arch/Manjaro: `sudo pacman -Sy pandoc-cli` · Windows: `winget install JohnMacFarlane.Pandoc` |
| Python 3 | 运行转换器和本地图形界面 | macOS/Linux 通常自带；Windows 可从 [python.org](https://python.org) 安装 |

## 环境配置

先检查 Pandoc 是否可用：

```bash
pandoc --version
```

如果这条命令能正常输出版本号，就说明项目可以直接调用 Pandoc。

如果 Pandoc 已安装，但命令找不到：

- macOS/Linux：确认 Pandoc 已加入 `PATH`
- Windows：先关闭并重新打开终端
- Windows：如果还不行，可手动把 Pandoc 目录加入 `PATH`，常见路径是 `C:\Users\<你的用户名>\AppData\Local\Pandoc`

这个项目查找 Pandoc 的方式是：

- 先直接尝试系统里的 `pandoc`
- 在 Windows 上还会额外检查几个常见安装目录

## 项目如何工作

转换流程如下：

1. 从 GUI 或命令行读取 Markdown。
2. 用 Pandoc 转成独立 HTML。
3. 注入基础样式和你选择的模板覆盖样式。
4. 再做一次后处理，调整多栏布局、表格表现和代码格式。
5. 最终得到一个自包含的 `.html` cheatsheet，可直接浏览或导出 PDF。

## 快速开始

如果你希望直接看面向用户的详细说明，包括 macOS 权限放行、启动失败排查和常见故障，请先看 [使用手册](USAGE_CN.md)。

仓库中已附带可双击启动文件：

- macOS：`markdown2cheatsheet.command`
- Windows：`markdown2cheatsheet.bat`
- Linux：`markdown2cheatsheet.sh`

这些启动文件会先检查 Pandoc 是否已安装，以及版本是否至少为 `3.1.3`。
如果未安装，会引导安装。
如果版本过低，会引导更新。
安装或更新完成后，需要重新运行一次启动器，让新版本被正确识别。

Linux 启动器支持：

- Ubuntu/Debian：使用 `apt-get` 安装 Python 和 Pandoc
- Fedora：使用 `dnf` 安装 Python 和 Pandoc
- Arch/Manjaro：使用 `pacman` 安装 `python` 和 `pandoc-cli`

部分发行版仓库可能只提供低于 `3.1.3` 的 Pandoc。遇到这种情况时，需要手动安装更新版本的 Pandoc，然后重新运行启动器。

macOS 用户如果第一次运行被系统拦截：

1. 先在 Finder 里右键 `markdown2cheatsheet.command` 并选择“打开”
2. 如果仍被拦截，到“系统设置 > 隐私与安全性”里找到对应提示并放行
3. 放行后重新运行启动器

手动启动图形界面：

```bash
python3 gui_app.py
```

图形界面支持：

- 导入本地 Markdown 文件，或直接粘贴内容
- 选择栏数、颜色模板、字体、字号和行间距
- 在浏览器中直接预览生成效果
- 下载最终 HTML 输出

## 命令行使用

基础转换：

```bash
bash md2cheatsheet.sh 你的笔记.md
```

指定输出文件：

```bash
bash md2cheatsheet.sh 你的笔记.md output.html
```

指定模板组合：

```bash
bash md2cheatsheet.sh 你的笔记.md output.html \
  --columns 5 \
  --color-template forest \
  --latin-font helvetica \
  --cjk-font lxgw-wenkai \
  --code-font jetbrains-mono \
  --font-size 6 \
  --line-height 1.1
```

运行仓库示例：

```bash
bash md2cheatsheet.sh examples/test_cheatsheet.md examples/test_cheatsheet.html
```

查看所有可选模板：

```bash
python3 md2cheatsheet.py --list-templates
```

## 模板选项

### 分栏数

- `2`
- `3`
- `4`
- `5`
- `6`

### 颜色模板

- `yubiquitous`：当前项目最初版本
- `grayscale`：纯黑白灰
- `forest`：更柔和的绿色系
- `sunset`：偏暖色的橙红系
- `navy`：深蓝色系
- `plum`：克制的紫灰色系

### 字体选项

- 英文字体：`arial`、`times-new-roman`、`helvetica`、`segoe-ui`、`verdana`
- 中文字体：`microsoft-yahei`、`pingfang-sc`、`kaiti`、`simsun`、`lxgw-wenkai`
- 代码字体：`system-code`、`consolas`、`menlo`、`hack`、`jetbrains-mono`
- 字号：`8`、`7.5`、`7`、`6.5`、`6`、`5.5`、`5`、`4.5`、`4`
- 行间距：`0.9`、`0.95`、`1.0`、`1.05`、`1.1`、`1.15`、`1.2`、`1.25`、`1.3`

## 导出 PDF

1. 用现代浏览器打开生成的 `.html` 文件。
2. 按 `Ctrl+P`，macOS 使用 `Cmd+P`。
3. 设置纸张为 `A4`，方向为 `Landscape` 或“横向”，边距为 `Minimum` 或“最小”。
4. 取消勾选页眉页脚。
5. 保存为 PDF。

## 常见故障

- macOS 双击 `markdown2cheatsheet.command` 被拦截：先右键打开；如果仍失败，到“系统设置 > 隐私与安全性”里放行
- 安装或更新 Pandoc 后仍提示版本不对：关闭当前窗口后重新运行启动器
- Debian/Fedora/Arch 的包管理器安装后版本仍过低：手动安装 Pandoc `3.1.3` 或更高版本，再重新运行启动器
- 浏览器没有自动打开：手动访问 `http://127.0.0.1:8765`
- 启动后提示端口占用：先关闭之前未退出的 markdown2cheatsheet 进程，再重新启动

更完整的故障排除说明见 [使用手册](USAGE_CN.md)。

## 面向开发者

开发、打包、版本号和 GitHub Release 工作流说明见 [docs/DEVELOPMENT_CN.md](DEVELOPMENT_CN.md)。

## 许可证

MIT。详见 [LICENSE](../LICENSE)。
