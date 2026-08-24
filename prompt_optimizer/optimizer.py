"""Core prompt optimization logic."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class OptimizationLevel(Enum):
    """Optimization levels for prompt enhancement."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class OptimizationResult:
    """Result of prompt optimization."""
    original: str
    optimized: str
    improvements: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "optimized": self.optimized,
            "improvements": self.improvements,
            "score": self.score,
        }


class PromptOptimizer:
    """Optimize prompts for better LLM performance."""

    VAGUE_WORDS = [
        "something", " stuff", " things", " maybe", " perhaps",
        " kind of", " sort of", " basically", " just", " really",
        " very", " some", " a bit", " a little",
    ]

    FILLER_PHRASES = [
        "please help me with",
        "I want you to",
        "can you",
        "could you",
        "would you",
        "I need you to",
        "I would like you to",
    ]

    STRUCTURE_KEYWORDS = [
        "step", "first", "second", "third", "then", "finally",
        "example", "for instance", "such as", "including",
    ]

    ROLE_PATTERNS = [
        (r"you are a (.+?)[\.,]", "role"),
        (r"act as (?:a |an )?(.+?)[\.,]", "role"),
        (r"as (?:a |an )(.+?)[\.,]", "role"),
    ]

    def __init__(self, level: OptimizationLevel = OptimizationLevel.MODERATE):
        self.level = level

    def optimize(self, prompt: str) -> OptimizationResult:
        """Optimize a prompt and return the result."""
        improvements = []
        optimized = prompt.strip()

        optimized, imp = self._remove_filler_words(optimized)
        improvements.extend(imp)

        optimized, imp = self._add_structure(optimized)
        improvements.extend(imp)

        optimized, imp = self._improve_clarity(optimized)
        improvements.extend(imp)

        optimized, imp = self._add_context_hints(optimized)
        improvements.extend(imp)

        if self.level in (OptimizationLevel.MODERATE, OptimizationLevel.AGGRESSIVE):
            optimized, imp = self._optimize_formatting(optimized)
            improvements.extend(imp)

        if self.level == OptimizationLevel.AGGRESSIVE:
            optimized, imp = self._add_constraints(optimized)
            improvements.extend(imp)

        score = self._calculate_score(prompt, optimized, improvements)

        return OptimizationResult(
            original=prompt,
            optimized=optimized,
            improvements=improvements,
            score=score,
        )

    def _remove_filler_words(self, text: str) -> tuple[str, list[str]]:
        """Remove unnecessary filler words and phrases."""
        improvements = []
        result = text

        for phrase in self.FILLER_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub("", result)
                improvements.append(f"Removed filler phrase: '{phrase}'")

        for word in self.VAGUE_WORDS:
            if word.lower() in result.lower():
                improvements.append(f"Consider removing vague word: '{word}'")

        result = re.sub(r"\s+", " ", result).strip()
        return result, improvements

    def _add_structure(self, text: str) -> tuple[str, list[str]]:
        """Add structure if prompt is long and unstructured."""
        improvements = []
        has_structure = any(kw in text.lower() for kw in self.STRUCTURE_KEYWORDS)

        if len(text) > 200 and not has_structure:
            if "\n" not in text:
                sentences = re.split(r"(?<=[.!?])\s+", text)
                if len(sentences) > 2:
                    result = "\n".join(f"- {s}" for s in sentences)
                    improvements.append("Added bullet point structure for readability")
                    return result, improvements

        return text, improvements

    def _improve_clarity(self, text: str) -> tuple[str, list[str]]:
        """Improve prompt clarity."""
        improvements = []

        if not text.endswith((".", "!", "?", ":")):
            text = text + "."
            improvements.append("Added ending punctuation")

        if text.startswith(" ") or text.endswith(" "):
            text = text.strip()
            improvements.append("Removed extra whitespace")

        return text, improvements

    def _add_context_hints(self, text: str) -> tuple[str, list[str]]:
        """Add helpful context hints."""
        improvements = []

        has_role = any(re.search(p, text, re.IGNORECASE) for p, _ in self.ROLE_PATTERNS)

        if not has_role and self.level == OptimizationLevel.AGGRESSIVE:
            if "write" in text.lower() or "create" in text.lower():
                improvements.append(
                    "Tip: Consider adding a role like 'Act as an expert writer' for better results"
                )

        return text, improvements

    def _optimize_formatting(self, text: str) -> tuple[str, list[str]]:
        """Optimize text formatting."""
        improvements = []

        if "\n\n" in text:
            text = re.sub(r"\n{3,}", "\n\n", text)
            improvements.append("Cleaned up excessive line breaks")

        if text != text.strip():
            text = text.strip()
            improvements.append("Removed leading/trailing whitespace")

        return text, improvements

    def _add_constraints(self, text: str) -> tuple[str, list[str]]:
        """Add output constraints for aggressive optimization."""
        improvements = []

        length_indicators = ["short", "brief", "concise", "long", "detailed", "verbose"]
        has_length_constraint = any(word in text.lower() for word in length_indicators)

        if not has_length_constraint and len(text) < 100:
            improvements.append(
                "Tip: Consider specifying desired output length (e.g., 'in 2-3 sentences')"
            )

        return text, improvements

    def _calculate_score(
        self, original: str, optimized: str, improvements: list[str]
    ) -> float:
        """Calculate optimization score (0-100)."""
        score = 50.0

        if len(optimized) < len(original):
            score += min(20, (len(original) - len(optimized)) / len(original) * 100)

        score += min(15, len(improvements) * 3)

        if "\n" in optimized and "\n" not in original:
            score += 10

        if optimized.endswith((".", "!", "?")) and not original.endswith((".", "!", "?")):
            score += 5

        return min(100.0, max(0.0, score))

    def batch_optimize(
        self, prompts: list[str], level: Optional[OptimizationLevel] = None
    ) -> list[OptimizationResult]:
        """Optimize multiple prompts."""
        optimizer = PromptOptimizer(level or self.level)
        return [optimizer.optimize(p) for p in prompts]

    def analyze(self, prompt: str) -> dict:
        """Analyze a prompt and return metrics."""
        words = prompt.split()
        sentences = re.split(r"[.!?]+", prompt)
        sentences = [s.strip() for s in sentences if s.strip()]

        has_role = any(re.search(p, prompt, re.IGNORECASE) for p, _ in self.ROLE_PATTERNS)
        has_structure = any(kw in prompt.lower() for kw in self.STRUCTURE_KEYWORDS)

        vague_count = sum(1 for w in self.VAGUE_WORDS if w.lower() in prompt.lower())
        filler_count = sum(
            1 for p in self.FILLER_PHRASES if p.lower() in prompt.lower()
        )

        clarity_score = 100 - (vague_count * 10) - (filler_count * 15)
        clarity_score = max(0, min(100, clarity_score))

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "has_role": has_role,
            "has_structure": has_structure,
            "vague_words": vague_count,
            "filler_phrases": filler_count,
            "clarity_score": clarity_score,
            "readability": "good" if len(words) / max(len(sentences), 1) < 25 else "complex",
        }
