"""小宇宙播客转录工具 CLI.

Usage:
    python -m src.main https://www.xiaoyuzhoufm.com/episode/xxx
    python -m src.main https://www.xiaoyuzhoufm.com/episode/xxx -o output/
"""

import argparse
import logging
import sys
from pathlib import Path

# Windows terminal encoding fix
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.audio import convert_to_wav, download_audio, get_duration_seconds
from src.config import get_deepseek_api_key
from src.models.schemas import OutputDoc
from src.processor import llm_processor
from src.scraper.xiaoyuzhou import scrape_episode
from src.transcriber.local import LocalTranscriber
from src.utils import CostTracker, Timer, fmt_time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("podcast-to-text")


def build_output_markdown(doc: OutputDoc) -> str:
    """Build the final markdown document."""
    lines = [
        f"# {doc.title}",
        "",
        f"> 来源：{doc.podcast_name}  |  {doc.pub_date}",
    ]
    if doc.show_notes:
        lines += ["", "# Show Notes", "", doc.show_notes]

    lines += ["", "## 内容提要", ""]
    for kp in doc.key_points:
        lines.append(f"- **{kp.point}**{kp.evidence}")

    if doc.highlight_quotes:
        lines += ["", "## 闪光语句", ""]
        for q in doc.highlight_quotes:
            lines.append(f'- "{q}"')

    lines += ["", "## 全文转录", "", doc.full_text]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="小宇宙播客转录工具 — 输入链接，输出结构化 Markdown"
    )
    parser.add_argument("url", help="小宇宙播客单集链接")
    parser.add_argument("-o", "--output", default="output", help="输出目录 (默认: output/)")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Whisper 模型大小 (默认: small)")
    parser.add_argument("--no-llm", action="store_true", help="仅转录，不进行 LLM 后处理")
    args = parser.parse_args()

    # Check DeepSeek key
    deepseek_key = get_deepseek_api_key()
    if not deepseek_key:
        print(
            "错误：DEEPSEEK_API_KEY 未设置\n"
            "请设置环境变量 DEEPSEEK_API_KEY=your_key",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    tracker = CostTracker()
    timers = {}

    try:
        # --- Step 1: Scrape ---
        with Timer() as t:
            logger.info("Step 1/5: 爬取节目信息...")
            episode = scrape_episode(args.url)
            print(f"  → {episode.title}")
            print(f"  播客: {episode.podcast_name}")
        timers["scrape"] = t.elapsed

        # --- Step 2: Download audio ---
        with Timer() as t:
            logger.info("Step 2/5: 下载音频...")
            audio_file = download_audio(episode.audio_url, output_dir)
            wav_file = convert_to_wav(audio_file, output_dir)
            duration_sec = get_duration_seconds(wav_file)
            print(f"  → 音频时长: {fmt_time(duration_sec)}")
        timers["download"] = t.elapsed

        # --- Step 3: Transcribe ---
        with Timer() as t:
            logger.info(f"Step 3/5: 本地转录中（faster-whisper {args.model}, CPU）...")
            transcriber = LocalTranscriber(model_size=args.model)
            transcript = transcriber.transcribe(wav_file, duration_sec)
            tracker.add_transcription(transcript.cost_yuan)
        timers["transcribe"] = t.elapsed
        char_count = len(transcript.raw_text)
        rtf = t.elapsed / duration_sec if duration_sec else 0
        est_2h = int(7200 * rtf)
        print(f"  → 转录完成：{char_count} 字, {fmt_time(t.elapsed)}, RTF={rtf:.2f}")
        print(f"  → [估算] 2小时节目约需 {fmt_time(est_2h)}（当前模型: {args.model}）")

        if args.no_llm:
            # Output raw transcript
            output_path = output_dir / f"{episode.title}_raw.txt"
            output_path.write_text(transcript.raw_text, encoding="utf-8")
            print(f"\n原始转录已保存到: {output_path}")
        else:
            # --- Step 4: LLM Process ---
            with Timer() as t:
                logger.info("Step 4/5: DeepSeek 后处理中...")
                doc, inp_tok, out_tok = llm_processor.process(
                    deepseek_key,
                    episode.title,
                    episode.podcast_name,
                    episode.pub_date,
                    episode.show_notes,
                    transcript.raw_text,
                )
                tracker.add_llm_usage(inp_tok, out_tok)
            timers["process"] = t.elapsed

            # --- Step 5: Write output ---
            with Timer() as t:
                logger.info("Step 5/5: 写入 Markdown...")
                doc.costs = {"transcription": tracker.transcription_yuan, "llm": tracker.llm_cost_yuan}
                doc.timings = timers
                md_content = build_output_markdown(doc)
                safe_name = episode.title.replace("/", "_").replace("\\", "_").replace('"', '').replace('"', '').replace("|", "_").replace("?", "_").replace("*", "_").replace(":", "_")[:80]
                output_path = output_dir / f"{safe_name}.md"
                output_path.write_text(md_content, encoding="utf-8")
            timers["write"] = t.elapsed

            total_time = sum(timers.values())
            print(f"\n{'='*50}")
            print("[OK] 完成！")
            print(f"  输出文件: {output_path}")
            print(f"  总耗时: {fmt_time(total_time)}")
            print(f"  费用: {tracker.summary()}")
            print(f"  要点数: {len(doc.key_points)}")
            print(f"  闪光语句: {len(doc.highlight_quotes)}")
            print(f"{'='*50}")

    except Exception as e:
        logger.exception("处理失败")
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
