"""Cost tracking for API calls."""

import time
from dataclasses import dataclass, field


@dataclass
class CostTracker:
    transcription_yuan: float = 0.0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    llm_cost_yuan: float = 0.0

    DEEPSEEK_INPUT_PRICE = 0.5   # 元/百万 tokens
    DEEPSEEK_OUTPUT_PRICE = 2.0  # 元/百万 tokens

    def add_transcription(self, cost: float) -> None:
        self.transcription_yuan += cost

    def add_llm_usage(self, input_tokens: int, output_tokens: int) -> None:
        self.llm_input_tokens += input_tokens
        self.llm_output_tokens += output_tokens
        self.llm_cost_yuan += (
            input_tokens * self.DEEPSEEK_INPUT_PRICE
            + output_tokens * self.DEEPSEEK_OUTPUT_PRICE
        ) / 1_000_000

    @property
    def total_yuan(self) -> float:
        return self.transcription_yuan + self.llm_cost_yuan

    def summary(self) -> str:
        return (
            f"转录: {self.transcription_yuan:.4f} 元, "
            f"LLM: {self.llm_cost_yuan:.4f} 元 "
            f"(输入 {self.llm_input_tokens} / 输出 {self.llm_output_tokens} tokens), "
            f"合计: {self.total_yuan:.4f} 元"
        )


class Timer:
    """Simple timer context manager."""
    def __init__(self):
        self.start = 0.0
        self.elapsed = 0.0

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self.start


def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}分{s}秒"
