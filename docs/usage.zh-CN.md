# 使用说明

*[English](usage.md)* · [← 返回 README](../README.zh-CN.md)

如何安装 Video2Text，以及怎么用命令行、桌面 GUI 或 Chrome 插件三种方式来使用它。

---

## 环境要求

- **Python 3.12 或更新版本** —— 运行 `python3 --version` 查看你的版本
- 一个终端（Mac 用 Terminal，Windows 用 Command Prompt 或 PowerShell）
- 网络连接（用于下载字幕和调用 AI 模型的 API）
- 至少一个 **AI 模型的 API key** —— 用于生成摘要、要点和行动项，见下面的模型对照表。没有 key 也能用，只是笔记会是简单的规则匹配版本。

视频必须要有字幕（手动添加的或自动生成的都行）。支持英文和中文字幕。

---

## 安装

只需要做一次。

**第一步 — 下载项目文件**

如果你安装了 Git：

```bash
git clone <repository-url>
cd Video2Text
```

或者从项目页面下载 ZIP 并解压，然后在该文件夹中打开终端。

**第二步 — 创建虚拟环境**

虚拟环境可以让这个项目的依赖和你系统里的其他东西隔离开。

```bash
python3.12 -m venv .venv
```

现在项目目录里应该会出现一个 `.venv` 文件夹。

**第三步 — 激活虚拟环境**

Mac 或 Linux：

```bash
source .venv/bin/activate
```

Windows（Command Prompt）：

```bash
.venv\Scripts\activate.bat
```

Windows（PowerShell）：

```bash
.venv\Scripts\Activate.ps1
```

终端提示符前面会出现 `(.venv)` —— 说明环境已经激活。

**第四步 — 安装依赖**

```bash
pip install -r requirements.txt
```

**第五步 — 设置一个 API key**

把环境变量 `ANTHROPIC_API_KEY` 设置为你在 [console.anthropic.com](https://console.anthropic.com/) 获取的 API key。

Mac 或 Linux：

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Windows（Command Prompt）：

```bash
set ANTHROPIC_API_KEY=your-key-here
```

Windows（PowerShell）：

```bash
$env:ANTHROPIC_API_KEY="your-key-here"
```

这样设置只在当前终端会话有效。如果想永久生效，把这一行加到你 shell 的启动文件里（例如 `~/.zshrc` 或 `~/.bashrc`），或者加到系统的环境变量设置中。

### 其他 AI 模型（可选）

`ANTHROPIC_API_KEY` 是默认选项，不过现在也支持其他好几家模型。设置对应的环境变量就能让那家模型可用。命令行和桌面 GUI 会自动使用下表里第一个配置好的模型；Chrome 插件则额外提供了一个下拉框可以手动选。如果一个都没配置，或者选中的模型调用失败，都会自动退回规则匹配版本：

| 模型 | 环境变量 |
|---|---|
| Claude (Anthropic) | `ANTHROPIC_API_KEY` |
| GPT (OpenAI) | `OPENAI_API_KEY` |
| Gemini (Google) | `GOOGLE_API_KEY` |
| 通义千问 Qwen (Alibaba) | `DASHSCOPE_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| 豆包 Doubao (ByteDance) | `ARK_API_KEY` |
| Kimi (Moonshot) | `MOONSHOT_API_KEY` |
| 智谱 GLM (Zhipu) | `ZHIPU_API_KEY` |
| 文心一言 Ernie (Baidu) | `BAIDU_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |

在 Chrome 插件里，模型下拉框会用 ✅ 标出已配置的、🔒 标出还没配置的。

---

## 使用方法（命令行）

确保虚拟环境已激活（提示符里能看到 `(.venv)`）。然后运行：

```bash
python main.py <youtube_url>
```

把 `<youtube_url>` 换成任意 YouTube 链接，两种格式都可以：

```bash
python main.py https://www.youtube.com/watch?v=zjkBMFhNj_g
python main.py https://youtu.be/zjkBMFhNj_g
```

**终端输出示例：**

```
Reading video information...
Downloaded subtitles (en).
Generating transcript...
Generating notes with Claude...
Done.
Created output/transcript.txt
Created output/notes.md
```

打开 `output/` 文件夹就能找到生成的文件。

---

## 使用方法（桌面 GUI）

```bash
python ui.py
```

跟命令行是同一套逻辑，多了一个窗口：粘贴链接、在下拉框里选一个模型（只列出已配置的）、点 Generate、切换 Notes/Transcript 两个标签页浏览结果。配色读的是 `app/theme.py`，会自动跟随系统的浅色/深色模式。模型列表是启动时读一次的，设置新的 API key 之后需要重启一下程序。

---

## 使用方法（Chrome 插件）

一个嵌在 YouTube 侧边栏最上面的纯浏览器扩展。它直接读取当前视频已有的字幕，不需要 Python、本地服务、API key 或云服务器。

**1. 在 Chrome 里加载插件**

- 打开 `chrome://extensions`
- 打开右上角的「开发者模式」
- 点「加载已解压的扩展程序」，选择 `extension/` 文件夹

**2. 开始使用**

打开带字幕的 YouTube 视频，面板会自动出现在侧边栏里。点「提取现有字幕」后，可以直接复制文字稿或下载 TXT。没有字幕的视频会显示提示；扩展不会下载音频，也不会进行语音识别或生成 AI 笔记。面板配色读的是 `extension/theme.css`，会自动跟随系统的浅色/深色模式。

---

## 输出文件

**`output/transcript.txt`**

视频的完整口语内容，清洗成可读文本。字幕文件里的时间戳和格式代码都会被去掉，并且会自动按句数分段（不是按语义分的，就是每隔几句分一段），不会是一行一句字幕堆在一起的样子——不管有没有配置 AI 模型都会这样处理。

**`output/notes.md`**

一份结构化的 Markdown 文档：

```
# 视频标题

## Summary
AI 写的一段简短摘要，涵盖主要内容和结论。

## Key Points
- ...
- ...
- ...

## Action Items
- ...
- ...

## Transcript
完整的文字稿内容。
```

`.md` 文件可以用任意文本编辑器打开，也可以用 Obsidian、Notion、Typora 或 VS Code 之类的应用打开，获得排版好看的效果。

---

## 故障排查

**"No English or Chinese subtitles were found for this video."**

这个视频没有支持语言的字幕。换一个视频试试，或者找一个开启了自动生成字幕的视频。

**"Invalid YouTube URL."**

确认你输入的是完整链接，而不只是视频 ID。链接必须以 `https://` 开头，指向 `youtube.com/watch?v=...` 或 `youtu.be/...`。

**"Could not read video information."**

视频可能是私享、年龄限制，或者在你所在地区不可用。换一个视频试试。

**笔记看起来只是文字稿里摘出来的普通句子（没有 AI 摘要）**

说明没有配置任何模型的 API key，或者调用失败了。工具会退回到简单的规则匹配笔记，保证能完成任务。检查一下安装步骤第五步里模型对照表中的环境变量是否设置好了，以及 key 是否有效、账户是否还有余额。

**找不到 `python3.12`**

从 python.org 安装 Python 3.12。Mac 上也可以用 `brew install python@3.12`。

**虚拟环境没有激活**

如果看到「找不到某个包」之类的报错，重新执行第三步里的激活命令。每次打开新的终端窗口都需要重新激活一次。

---

## 运行测试

```bash
pytest
```
