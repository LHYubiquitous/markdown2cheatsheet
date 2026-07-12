# markdown2cheatsheet

将 Markdown 笔记转换为高密度、可打印的 cheatsheet，并且可以直接选择模板参数，还支持本地图形界面。

[English README](../README.md)

## 效果预览

![效果预览](../outputview.jpg)

## 功能特点

- 支持 `4 / 5 / 6` 栏输出，适合不同密度的复习资料。
- 无需手改 `cheatsheet.css`，可直接通过命令行选择颜色模板、字体、字号和行间距。
- 通过 Pandoc 生成自包含 HTML，样式和资源会嵌入输出文件。
- 提供本地图形界面，可导入 Markdown、选择模板、预览结果并下载 HTML。
- 命令行和图形界面共用同一套转换核心，行为保持一致。

## 依赖

| 工具 | 用途 | 安装方式 |
| --- | --- | --- |
| [Pandoc](https://pandoc.org) | Markdown 转独立 HTML | macOS: `brew install pandoc` · Ubuntu: `sudo apt install pandoc` · Windows: `winget install JohnMacFarlane.Pandoc` |
| Python 3 | 运行转换器、后处理脚本和图形界面 | macOS/Linux 通常自带；Windows 可从 [python.org](https://python.org) 安装 |

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
  --font-size large \
  --line-height balanced
```

查看所有可选模板：

```bash
python3 md2cheatsheet.py --list-templates
```

运行仓库示例：

```bash
bash md2cheatsheet.sh examples/test_cheatsheet.md examples/test_cheatsheet.html
```

## 图形界面使用

启动本地图形界面：

```bash
python3 gui_app.py
```

仓库内已附带可双击启动文件：

- macOS：`start.command`
- Windows：`start.bat`
- Linux：`start.sh`

自定义端口，且不自动打开浏览器：

```bash
python3 gui_app.py --port 9000 --no-browser
```

界面支持：

- 导入本地 Markdown 文件，或直接粘贴内容
- 选择栏数、颜色模板、字体、字号和行间距
- 在浏览器中直接预览生成效果
- 下载最终 HTML 输出

## 发布版打包

在当前系统上构建可分发的图形界面发布版：

```bash
python3 -m pip install pyinstaller
python3 build_release.py
```

输出位置：

- 应用原始产物：`dist/`
- 发布目录和压缩包：`release/`

命名规则：

- `markdown2cheatsheet-gui-v1.0.0-macos-arm64.zip`
- `markdown2cheatsheet-gui-v1.0.0-windows-x64.zip`
- `markdown2cheatsheet-gui-v1.0.0-linux-x64.zip`

启动方式：

- macOS：解压后运行 `start.command`
- Windows：解压后运行 `start.bat`
- Linux：解压后运行 `start.sh`

说明：

- 打包结果和当前系统绑定。要发 macOS 版就在 macOS 上打包，要发 Windows 版就在 Windows 上打包，要发 Linux 版就在 Linux 上打包。
- 打包时会自动带上 GUI 静态资源、默认示例 Markdown 和样式文件。
- 对 macOS，推荐从解压后的目录中运行 `start.command`，而不是直接双击 `.app`。
- 如果当前提交正好对应一个 Git tag，就会直接使用该 tag 作为版本号；否则会回退到带短提交哈希的本地开发版本号。

## GitHub Actions

仓库已附带跨平台自动构建工作流：

- 工作流文件：`.github/workflows/build-release.yml`
- 触发方式：手动运行，或推送匹配 `v*` 的 tag
- 输出结果：每个平台都会在 `release/` 目录生成并上传一个压缩包
- 推送 tag 时：会自动构建各平台产物，并自动创建一个 GitHub Release，把生成的 `.zip` 附件挂上去

## 模板选项

### 分栏数

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

## 仓库结构

```text
markdown2cheatsheet/
├── README.md
├── LICENSE
├── start.command
├── start.bat
├── start.sh
├── build_release.py           # 基于 PyInstaller 的发布版打包脚本
├── .github/workflows/
│   └── build-release.yml      # 跨平台发布版自动构建工作流
├── cheatsheet.css              # 基础样式，使用 CSS 变量驱动模板
├── converter_core.py           # 命令行和图形界面共用的转换核心
├── gui_app.py                  # 本地图形界面服务
├── md2cheatsheet.py            # Python 命令行入口
├── md2cheatsheet.sh            # Bash 包装脚本
├── postprocess.py              # Pandoc HTML 后处理脚本
├── template_presets.py         # 分栏、颜色、字体模板定义
├── gui/
│   ├── index.html              # 图形界面结构
│   ├── styles.css              # 图形界面样式
│   └── app.js                  # 图形界面交互逻辑
├── docs/
│   └── README_CN.md
└── examples/
    └── test_cheatsheet.md
```

## 工作原理

```text
Markdown 文件
    |
    v
命令行或图形界面
    - 选择栏数
    - 选择颜色模板
    - 选择字体
    - 选择字号
    - 选择行间距
    |
    v
Pandoc
    - 生成 standalone HTML
    - 嵌入样式和资源
    |
    v
postprocess.py
    - 删除 Pandoc 表格 colgroup 宽度覆盖
    - 压缩代码块缩进
    - 用 .content-wrapper 包裹 body 内容
    |
    v
自包含 cheatsheet HTML
```

## 导出 PDF

1. 用现代浏览器打开生成的 `.html` 文件。
2. 按 `Ctrl+P`，macOS 使用 `Cmd+P`。
3. 设置纸张为 `A4`，方向为 `Landscape` 或“横向”，边距为 `Minimum` 或“最小”。
4. 取消勾选页眉页脚。
5. 保存为 PDF。

## 许可证

MIT。详见 [LICENSE](../LICENSE)。
