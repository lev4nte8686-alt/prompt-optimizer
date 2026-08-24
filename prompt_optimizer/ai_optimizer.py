"""AI-powered prompt optimizer using OpenAI API."""

import os
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class AIOptimizationResult:
    original: str
    optimized: str
    explanation: str
    model: str

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "optimized": self.optimized,
            "explanation": self.explanation,
            "model": self.model,
        }


class AIPromptOptimizer:
    """AI-powered prompt optimizer using LLM."""

    SYSTEM_PROMPT = """You are an expert prompt engineer. Your job is to optimize prompts for better LLM performance.

Rules:
1. Keep the original intent and language
2. Add specificity and context where missing
3. Structure the prompt clearly
4. Add role/persona if beneficial
5. Include output format expectations if needed
6. Remove ambiguity
7. Keep it concise but complete

Return ONLY the optimized prompt, nothing else."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        if OpenAI is None:
            raise ImportError("Install openai: pip install openai")

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def optimize(
        self,
        prompt: str,
        context: str = None,
        output_format: str = None,
        language: str = None,
    ) -> AIOptimizationResult:
        """Optimize a prompt using AI."""
        user_message = self._build_message(prompt, context, output_format, language)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        optimized = response.choices[0].message.content.strip()

        explanation = self._generate_explanation(prompt, optimized)

        return AIOptimizationResult(
            original=prompt,
            optimized=optimized,
            explanation=explanation,
            model=self.model,
        )

    def _build_message(
        self, prompt: str, context: str, output_format: str, language: str
    ) -> str:
        parts = [f"Original prompt: {prompt}"]

        if context:
            parts.append(f"Context: {context}")

        if output_format:
            parts.append(f"Desired output format: {output_format}")

        if language:
            parts.append(f"Language: {language}")

        parts.append("\nOptimize this prompt for better LLM performance.")
        return "\n".join(parts)

    def _generate_explanation(self, original: str, optimized: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Explain briefly what changes you made to optimize the prompt. Be concise.",
                },
                {
                    "role": "user",
                    "content": f"Original: {original}\nOptimized: {optimized}",
                },
            ],
            temperature=0.5,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    def chat_optimize(self, prompt: str, feedback: str = None) -> AIOptimizationResult:
        """Optimize with follow-up feedback."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Optimize: {prompt}"},
        ]

        if feedback:
            messages.append({"role": "assistant", "content": prompt})
            messages.append({"role": "user", "content": f"Feedback: {feedback}"})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )

        optimized = response.choices[0].message.content.strip()

        return AIOptimizationResult(
            original=prompt,
            optimized=optimized,
            explanation="Optimized with feedback" if feedback else "Initial optimization",
            model=self.model,
        )
