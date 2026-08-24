"""Tests for prompt optimizer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_optimizer.optimizer import OptimizationLevel, PromptOptimizer


def test_basic_optimization():
    optimizer = PromptOptimizer(OptimizationLevel.MINIMAL)
    result = optimizer.optimize("hello world")
    assert result.optimized == "hello world."
    assert result.score > 0


def test_remove_filler_phrases():
    optimizer = PromptOptimizer(OptimizationLevel.MODERATE)
    result = optimizer.optimize("Can you please help me with writing code")
    assert "can you" not in result.optimized.lower()
    assert "please help me with" not in result.optimized.lower()


def test_analyze():
    optimizer = PromptOptimizer()
    analysis = optimizer.analyze("You are a helpful assistant. Write a summary.")
    assert analysis["word_count"] > 0
    assert analysis["has_role"] is True


def test_batch_optimize():
    optimizer = PromptOptimizer()
    prompts = ["hello", "world test"]
    results = optimizer.batch_optimize(prompts)
    assert len(results) == 2


if __name__ == "__main__":
    test_basic_optimization()
    test_remove_filler_phrases()
    test_analyze()
    test_batch_optimize()
    print("All tests passed!")
