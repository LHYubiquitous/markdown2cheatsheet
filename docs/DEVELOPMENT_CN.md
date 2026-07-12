# 开发说明

本文件面向维护者和贡献者。

[用户说明](../README.md)

## 项目结构

```text
markdown2cheatsheet/
├── README.md
├── LICENSE
├── start.command
├── start.bat
├── start.sh
├── build_release.py
├── version.py
├── .github/workflows/
│   └── build-release.yml
├── cheatsheet.css
├── converter_core.py
├── gui_app.py
├── md2cheatsheet.py
├── md2cheatsheet.sh
├── postprocess.py
├── template_presets.py
├── gui/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs/
│   ├── DEVELOPMENT.md
│   └── README_CN.md
└── examples/
    └── test_cheatsheet.md
```

## 本地开发

本地启动 GUI：

```bash
python3 gui_app.py
```

运行示例转换：

```bash
bash md2cheatsheet.sh examples/test_cheatsheet.md examples/test_cheatsheet.html
```

查看当前模板元数据：

```bash
python3 md2cheatsheet.py --list-templates
```

## 发布版打包

在当前系统上构建本平台发布版：

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

## 版本号

- 版本号逻辑在 [version.py](../version.py)
- 如果当前提交正好对应一个 Git tag，就直接使用该 tag
- 否则回退为带短提交哈希的开发版号

示例：

- 正式 tag：`v1.0.0`
- 未打 tag：`0.0.0-dev+abc1234`

## GitHub Actions

工作流文件：

- `.github/workflows/build-release.yml`

行为：

- `workflow_dispatch`：手动构建
- 推送匹配 `v*` 的 tag：构建所有平台并自动创建 GitHub Release

发布产物：

- 一个 macOS `.zip`
- 一个 Windows `.zip`
- 一个 Linux `.zip`
