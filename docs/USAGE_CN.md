# markdown2cheatsheet 使用手册

这份手册面向普通使用者，重点说明如何启动、如何处理权限提示，以及常见故障排除。

[返回中文 README](README_CN.md)

## 1. 启动前准备

你至少需要准备两样东西：

- Pandoc `3.1.3` 或更高版本
- Python 3

如果你不确定 Pandoc 是否已经安装，可以先检查：

```bash
pandoc --version
```

如果第一行能看到版本号，并且版本不低于 `3.1.3`，就可以直接继续。

## 2. 推荐启动方式

项目自带了可双击启动器：

- macOS：`markdown2cheatsheet.command`
- Windows：`markdown2cheatsheet.bat`
- Linux：`markdown2cheatsheet.sh`

启动器会先检查 Pandoc：

- 未安装：提示你安装
- 版本过低：提示你更新
- 版本符合要求：直接启动本地 GUI

如果 Pandoc 是刚安装或刚更新完成的，请关闭当前启动窗口，再重新运行一次启动器。

## 3. macOS 使用说明

### 第一次运行被系统拦截

macOS 可能会把 `.command` 视为来自未确认来源的文件，这时通常有两种处理方式。

方式一：在 Finder 中右键打开

1. 在 Finder 里找到 `markdown2cheatsheet.command`
2. 右键点击
3. 选择“打开”
4. 再次点击“打开”

方式二：到“隐私与安全性”里放行

1. 打开“系统设置”
2. 进入“隐私与安全性”
3. 下滑到安全性相关提示区域
4. 如果看到和 `markdown2cheatsheet.command` 相关的拦截提示，点击“仍要打开”或同类放行按钮
5. 再回到项目目录重新运行

如果你是从互联网下载的压缩包，系统也可能因为隔离属性阻止运行。此时优先尝试“右键打开”和“隐私与安全性”放行。

### 双击没有反应或一闪而过

常见原因：

- Pandoc 未安装
- Pandoc 版本低于 `3.1.3`
- Python 3 不可用
- 系统权限未放行

建议做法：

1. 先右键打开一次
2. 查看弹出的终端窗口里是否有报错提示
3. 如果提示安装或升级 Pandoc，先完成操作
4. 安装或升级后，关闭窗口并重新启动

### 浏览器没有自动打开

这通常不影响服务本身启动。你可以手动打开浏览器并访问：

```text
http://127.0.0.1:8765
```

如果这个地址能打开页面，说明程序已经正常运行。

## 4. Windows 使用说明

第一次双击 `markdown2cheatsheet.bat` 后，Windows 可能会出现 SmartScreen 提示。

处理方式通常是：

1. 点击“更多信息”
2. 选择“仍要运行”

如果启动器提示安装或升级 Pandoc，并且你同意，程序会尝试调用 `winget`。

如果安装完成后仍然提示找不到 Pandoc：

1. 关闭当前窗口
2. 重新双击启动器
3. 仍不行时，重开系统终端或重启电脑后再试

## 5. Linux 使用说明

如果双击 `markdown2cheatsheet.sh` 没有执行，通常是执行权限问题。

先给脚本加权限：

```bash
chmod +x markdown2cheatsheet.sh
```

然后再运行：

```bash
./markdown2cheatsheet.sh
```

如果系统提示需要安装或更新 Pandoc，按提示确认即可。

Linux 启动器支持这些包管理器：

- Ubuntu/Debian：`apt-get`
- Fedora：`dnf`
- Arch/Manjaro：`pacman`

手动安装命令：

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 pandoc

# Fedora
sudo dnf install -y python3 pandoc

# Arch / Manjaro
sudo pacman -Sy --noconfirm python pandoc-cli
```

安装后检查 Pandoc 版本：

```bash
pandoc --version
```

部分发行版仓库可能只提供低于 `3.1.3` 的 Pandoc。如果系统包管理器装到的版本仍然过低，需要手动安装更新版本的 Pandoc，然后重新运行 `markdown2cheatsheet.sh`。

## 6. GUI 的基本使用流程

启动成功后，浏览器会打开本地页面。

通常按下面步骤使用：

1. 导入一个 Markdown 文件，或直接粘贴 Markdown 内容
2. 设置输出文件名
3. 选择分栏数、颜色模板、字体、字号和行间距
4. 点击 `Generate`
5. 在右侧预览结果
6. 点击 `Download HTML` 保存输出

## 7. 导出 PDF

生成 HTML 后，可以再导出成 PDF：

1. 用浏览器打开生成的 HTML
2. 按 `Cmd+P` 或 `Ctrl+P`
3. 纸张设置为 `A4`
4. 方向设置为横向
5. 边距设置为最小
6. 关闭页眉页脚
7. 保存为 PDF

## 8. 常见问题排除

### 提示 Pandoc 未安装

先确认：

```bash
pandoc --version
```

如果命令不存在，就先安装 Pandoc。

### 提示 Pandoc 版本过低

当前项目要求 Pandoc `3.1.3` 或更高版本。

你可以先检查：

```bash
pandoc --version
```

如果版本过低，先更新，再重新运行启动器。

在 Debian、Fedora、Arch 或 Manjaro 上，启动器会先尝试使用系统包管理器。如果包管理器提供的 Pandoc 仍低于 `3.1.3`，请从其他来源安装更新版本，然后重新运行启动器。

### 安装或更新完成后还是不行

优先按这个顺序试：

1. 关闭当前启动窗口
2. 重新运行启动器
3. 重新打开终端或文件管理器
4. 仍不行时，重启系统后再试

### 提示端口已被占用

默认地址是：

```text
http://127.0.0.1:8765
```

如果这个端口已经被别的程序占用，GUI 可能启动失败。

最直接的处理方式是：

1. 关闭之前已经启动但未退出的 markdown2cheatsheet 进程
2. 再重新启动一次

### 用完以后怎么关闭

如果你是通过启动器打开的，本地服务通常会在终端窗口中保持运行。

使用完后：

1. 回到启动器打开的终端窗口
2. 按 `Ctrl+C`
3. 看到停止提示后再关闭窗口

## 9. 手动启动方式

如果你不想用双击启动器，也可以手动启动：

```bash
python3 gui_app.py
```

然后在浏览器打开：

```text
http://127.0.0.1:8765
```
