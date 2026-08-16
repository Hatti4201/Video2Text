# Video2Text

*[English](README.md)*

把任意 YouTube 视频变成结构化笔记。

粘贴一个 YouTube 链接，就能得到两个文件：

- `output/transcript.txt` — 视频的完整文字稿
- `output/notes.md` — 一份 Markdown 文档，包含摘要、要点、行动项和完整文字稿

摘要、要点和行动项是由 AI 模型生成的 —— 默认是 Claude，也支持 GPT、Gemini、DeepSeek、通义千问等其他模型。

有三种使用方式：命令行脚本、桌面 GUI，还有一个无需后端、直接读取 YouTube 已有字幕的 Chrome 插件。

---

## 它是做什么的

```
YouTube 链接
    ↓
下载字幕（英文或中文）
    ↓
把原始字幕文件清洗成可读的文字稿
    ↓
把文字稿发给 AI 模型，生成摘要、要点和行动项
    ↓
把 transcript.txt 和 notes.md 保存到 output/ 文件夹
```

如果没有配置任何 AI 模型，工具会退回到一个简单的规则匹配摘要，仍然能生成结果，只是笔记质量会低一些。

---

## 快速开始

**📖 完整的安装步骤、API key 设置（含所有支持的模型）、以及命令行 / 桌面 GUI / Chrome 插件三种使用方式，见 [使用说明](docs/usage.zh-CN.md)。**

---

## 项目结构

```
Video2Text/
├── app/
│   ├── downloader.py     # 从 YouTube 下载字幕
│   ├── transcript.py     # 把 VTT 字幕文件解析成纯文本
│   ├── notes.py          # 调用 AI 模型生成结构化笔记（附带规则匹配的兜底方案）
│   ├── providers.py      # AI 模型注册表（Claude、GPT、Gemini、通义千问、DeepSeek 等）
│   ├── theme.py          # 共用的配色主题（桌面 GUI 用）
│   ├── server.py         # 可选的本地 HTTP 接口
│   ├── gui.py            # 桌面 GUI（Tkinter）
│   └── utils.py          # 公用工具函数
├── extension/            # 纯浏览器 Chrome 插件（读取 YouTube 已有字幕）
│   └── theme.css           # 共用的配色主题（和 app/theme.py 是同一套 token）
├── output/               # 生成的文件保存在这里
├── tests/                # 自动化测试
├── docs/                 # 项目文档，包含使用说明
├── main.py               # 命令行入口
├── ui.py                 # 桌面 GUI 入口
└── requirements.txt
```

---

## 未来规划

```
第 1 阶段 - MVP（当前）
第 2 阶段 - 云端 LLM 笔记（当前）/ 本地 LLM 选项
第 3 阶段 - Whisper（没有字幕时用音频转录）
第 4 阶段 - Notion 集成
第 5 阶段 - Telegram 集成
第 6 阶段 - Docker
第 7 阶段 - Windows 部署
第 8 阶段 - 安全远程访问
第 9 阶段 - 知识管理系统
第 10 阶段 - 个人助理生态
```
