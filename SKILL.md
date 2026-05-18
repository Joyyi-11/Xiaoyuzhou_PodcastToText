---
name: xiaoyuzhou-podcast-to-text
description: 小宇宙播客转录工具 —— 输入小宇宙 FM 播客链接，自动下载音频、转写为文字、用 DeepSeek 后处理生成结构化 Markdown 文稿
---

# podcast-to-text

小宇宙播客转录工具，一键将播客节目转为结构清晰的 Markdown 文档，含要点速览、闪光语句、全文转录。

## When to use

当用户想要：
- 将小宇宙 FM 播客转写成文字稿
- 提取播客要点和核心观点
- 保存播客 Show Notes
- "帮我转录播客"、"转写这期播客"、"把播客转成文字"、"生成播客文稿"

## How to use

当前目录必须是项目根目录 `Xiaoyuzhou_PodcastToText/`。

```bash
# 基本用法
python -m src.main <小宇宙播客链接>

# 指定输出目录
python -m src.main <小宇宙播客链接> -o output/

# 使用 larger 模型提高准确率（耗时更长）
python -m src.main <小宇宙播客链接> --model small
```

### 前置要求

1. 安装依赖：`pip install -r requirements.txt`
2. 设置环境变量 `DEEPSEEK_API_KEY`（可在 `.env` 文件中配置）
3. 确保系统已安装 ffmpeg

### 输出结构

```
# 节目标题
> 来源：播客名称 | 发布日期

# Show Notes
（完整保留的节目介绍）

## 要点速览
- **要点名称**：支撑证据

## 闪光语句
> 核心洞见引用

## 全文转录
（清洗后的完整文稿，关键句已加粗）
```

## Instructions

1. 确认当前在 `Xiaoyuzhou_PodcastToText/` 目录
2. 运行 `python -m src.main <url>` 启动转录
3. 前三个步骤自动运行：爬取节目信息 → 下载音频 → 本地 Whisper 转写
4. 转写完成后自动调用 DeepSeek 进行后处理（标点修正、分段、要点提炼、闪光语句提取）
5. 最终 Markdown 文件输出到指定目录（默认 `output/`）
6. 输出文件路径和费用统计会在终端显示

### 参数说明

- `--model`：Whisper 模型大小（tiny/base/small/medium/large-v3），默认 tiny，推荐 small
- `--no-llm`：仅转写，跳过 DeepSeek 后处理
- `-o`：输出目录，默认为 `output/`

### 成本

- 转写：本地 faster-whisper，免费
- 后处理：DeepSeek API，约 0.03-0.10 元/期（按 tokens 计费）
- 每期总成本通常不超过 0.1 元
