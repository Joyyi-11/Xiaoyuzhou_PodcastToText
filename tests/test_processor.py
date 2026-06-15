"""Tests for the LLM processor module."""

from src.processor.llm_processor import _parse_output


class TestParseOutput:
    def test_parse_basic(self):
        content = """# Test Title

> Source

## 内容提要

- **核心观点一**：这是支撑证据第一句。这是第二句。
- **重要数据**：数据显示增长50%。

## 全文转录

这是全文第一段。

这是全文第二段。"""
        doc = _parse_output(content, "Test Title", "Test Podcast", "2026-01-01", "notes")
        assert doc.title == "Test Title"
        assert doc.podcast_name == "Test Podcast"
        assert len(doc.key_points) == 2
        assert doc.key_points[0].point == "核心观点一"
        assert doc.key_points[1].point == "重要数据"
        assert "全文第一段" in doc.full_text

    def test_no_key_points(self):
        content = """Some random text without proper headers."""
        doc = _parse_output(content, "Title", "Podcast", "2026-01-01", "")
        assert len(doc.key_points) == 0
        assert doc.full_text == content

    def test_with_highlight_quotes(self):
        content = """# Test Title

## 内容提要

- **核心观点**：证据文本。

## 闪光语句

- "这是第一句闪光语句。"
- "这是第二句闪光语句。"

## 全文转录

这是全文。"""
        doc = _parse_output(content, "Title", "Podcast", "2026-01-01", "")
        assert len(doc.key_points) == 1
        assert len(doc.highlight_quotes) == 2
        assert doc.highlight_quotes[0] == "这是第一句闪光语句。"
        assert "全文" in doc.full_text

    def test_clean_duplicated_point(self):
        """Evidence should not contain duplicated point title."""
        content = """# Test

## 内容提要

- **核心观点A**：核心观点A**：这是支撑证据。

## 全文转录

全文。"""
        doc = _parse_output(content, "T", "P", "2026-01-01", "")
        assert len(doc.key_points) == 1
        assert doc.key_points[0].point == "核心观点A"
        # The duplicated title should be cleaned from evidence
        assert "核心观点A" not in doc.key_points[0].evidence or doc.key_points[0].evidence.count("核心观点A") == 0

    def test_with_speaker_intro(self):
        """Parse 人物介绍 section between 闪光语句 and 全文转录."""
        content = """# Test

## 内容提要

- **核心观点**：证据文本。

## 闪光语句

- 闪光语句一
- 闪光语句二

## 人物介绍

> **主持人**：Nina，主播
> **嘉宾**：Guest，title

## 全文转录

主持人Nina：这是第一段。

嘉宾Guest：这是第二段。"""
        doc = _parse_output(content, "T", "P", "2026-01-01", "")
        assert len(doc.key_points) == 1
        assert len(doc.highlight_quotes) == 2
        assert doc.highlight_quotes[0] == "闪光语句一"
        assert "主持人" in doc.speaker_intro
        assert "嘉宾" in doc.speaker_intro
        assert "Nina" in doc.speaker_intro
        assert "这是第一段" in doc.full_text
