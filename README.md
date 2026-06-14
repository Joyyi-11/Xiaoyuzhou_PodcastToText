# Xiaoyuzhou_PodcastToText

小宇宙播客转录工具 —— 输入小宇宙 FM 链接，自动输出结构化 Markdown 文稿。

## 功能

- 爬取小宇宙播客节目信息、Show Notes
- 下载音频并转写为文字（本地 faster-whisper，免费）
- DeepSeek 后处理：标点修正、语义分段、专名纠错、要点提炼、闪光语句提取
- 输出结构化 Markdown：Show Notes → 要点速览 → 闪光语句 → 全文转录

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 DeepSeek API Key
echo "DEEPSEEK_API_KEY=your_key" > .env

# 转录播客
python -m src.main https://www.xiaoyuzhoufm.com/episode/xxxxx --model small
```

## 前置依赖

- Python 3.10+
- ffmpeg（用于音频格式转换）

## 配置

在 `.env` 文件中设置：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `url` | 必填 | 小宇宙播客单集链接 |
| `-o` | `output/` | 输出目录 |
| `--model` | `small` | Whisper 模型大小（tiny/base/small/medium/large-v3） |
| `--no-llm` | 否 | 仅转写，跳过 DeepSeek 后处理 |

## 输出格式

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
（清洗后的完整文稿）
```

## 成本

- 转写：本地免费
- DeepSeek 后处理：约 0.03-0.10 元/期
- 每期总成本通常不超过 0.1 元

## 项目结构

```
src/
├── main.py                 # CLI 入口
├── config.py               # 配置加载
├── audio.py                # 音频下载与格式转换
├── utils.py                # 计时、计费等工具
├── models/schemas.py       # 数据模型
├── scraper/xiaoyuzhou.py   # 小宇宙页面爬取
├── transcriber/local.py    # faster-whisper 本地转写
└── processor/
    ├── prompt.py           # DeepSeek 提示词模板
    └── llm_processor.py    # DeepSeek 后处理
```

## 致谢

- 本项目使用 Claude Code 辅助开发

## License

MIT
