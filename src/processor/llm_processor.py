"""DeepSeek LLM processor for cleaning and structuring transcripts."""

import logging
import re

from openai import OpenAI

from src.models.schemas import KeyPoint, OutputDoc
from src.processor.prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

# DeepSeek API 配置
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


def process(
    api_key: str,
    title: str,
    podcast_name: str,
    pub_date: str,
    show_notes: str,
    transcript_text: str,
) -> tuple[OutputDoc, int, int]:
    """Send to DeepSeek for cleaning and structuring.

    Returns:
        (OutputDoc, input_tokens, output_tokens)
    """
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        show_notes=show_notes or "（无）",
        transcript_text=transcript_text,
    )

    logger.info("Sending to DeepSeek (input ~%d chars)...", len(user_prompt))

    resp = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=16384,
    )

    content = resp.choices[0].message.content or ""
    usage = resp.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    logger.info(
        "DeepSeek done: %d in + %d out tokens", input_tokens, output_tokens
    )

    # Parse the structured output
    doc = _parse_output(content, title, podcast_name, pub_date, show_notes)
    return doc, input_tokens, output_tokens


def _clean_evidence(evidence: str, point_title: str) -> str:
    """Remove duplicated point title from the start of evidence text."""
    text = evidence.strip()
    # Remove opening punctuation like ：:、,，
    text = text.lstrip("：:、,， ")
    # If evidence starts with the point title, remove it
    if point_title and text.startswith(point_title):
        text = text[len(point_title):]
    # Clean up stray markdown bold markers at the start
    text = text.lstrip("*").lstrip("：:、,， ")
    return text.strip()


def _parse_output(
    content: str,
    title: str,
    podcast_name: str,
    pub_date: str,
    show_notes: str,
) -> OutputDoc:
    """Parse LLM output into OutputDoc structure.

    The LLM output follows the template format:
      # Title
      ## 内容提要
      - **point**: evidence
      ## 闪光语句
      - "quote"
      ## 全文转录
      ...
    """
    key_points: list[KeyPoint] = []
    highlight_quotes: list[str] = []

    # --- Parse 内容提要 section ---
    m_toc = re.search(r"##\s*内容提要\s*\n(.*?)(?=##\s*(?:闪光语句|全文转录)|$)", content, re.DOTALL)
    if m_toc:
        toc_section = m_toc.group(1)
        for line in toc_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                # Extract bold text as point title
                bold_m = re.search(r"\*\*(.*?)\*\*", line)
                if bold_m:
                    point_title = bold_m.group(1).strip()
                    # Everything after the bold closing marker
                    after_bold = line[bold_m.end():].strip()
                    evidence = _clean_evidence(after_bold, point_title)
                    key_points.append(KeyPoint(point=point_title, evidence=evidence))

    # --- Parse 闪光语句 section ---
    m_quotes = re.search(r"##\s*闪光语句\s*\n(.*?)(?=##\s*全文转录|$)", content, re.DOTALL)
    if m_quotes:
        quotes_section = m_quotes.group(1)
        for line in quotes_section.strip().split("\n"):
            raw = line.strip()
            # Remove leading list marker (- or *) and surrounding quotes
            if raw.startswith("- "):
                raw = raw[2:]
            elif raw.startswith("* "):
                raw = raw[2:]
            raw = raw.strip("\"'").strip("“”").strip()
            if raw and len(raw) >= 5:  # skip empty or too-short lines
                highlight_quotes.append(raw)

    # --- Parse 全文转录 section ---
    m_full = re.search(r"##\s*全文转录\s*\n(.*)", content, re.DOTALL)
    full_text = m_full.group(1).strip() if m_full else content.strip()

    return OutputDoc(
        title=title,
        podcast_name=podcast_name,
        pub_date=pub_date,
        show_notes=show_notes,
        key_points=key_points,
        highlight_quotes=highlight_quotes,
        full_text=full_text,
    )
