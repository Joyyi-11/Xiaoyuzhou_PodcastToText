"""Tests for the cost tracker utility."""

from src.utils import CostTracker


class TestCostTracker:
    def test_empty(self):
        t = CostTracker()
        assert t.total_yuan == 0.0

    def test_transcription_cost(self):
        t = CostTracker()
        t.add_transcription(0.66)
        assert t.transcription_yuan == 0.66
        assert t.total_yuan == 0.66

    def test_llm_cost(self):
        t = CostTracker()
        t.add_llm_usage(20000, 30000)
        # input: 20000 * 0.5 / 1_000_000 = 0.01
        # output: 30000 * 2.0 / 1_000_000 = 0.06
        assert abs(t.llm_cost_yuan - 0.07) < 0.001
        assert abs(t.total_yuan - 0.07) < 0.001

    def test_total(self):
        t = CostTracker()
        t.add_transcription(0.66)
        t.add_llm_usage(20000, 30000)
        assert abs(t.total_yuan - 0.73) < 0.001
