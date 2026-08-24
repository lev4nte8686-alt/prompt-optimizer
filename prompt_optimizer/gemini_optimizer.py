"""AI-powered prompt optimizer using Google Gemini API (free tier)."""

from dataclasses import dataclass

try:
    import google.generativeai as genai
except ImportError:
    genai = None


@dataclass
class GeminiOptimizationResult:
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


class GeminiPromptOptimizer:
    """AI-powered prompt optimizer using Google Gemini API (free tier)."""

    SYSTEM_PROMPT = """You are an expert prompt engineer. Optimize the given prompt for better LLM performance.

Rules:
1. Keep the original intent and language (Vietnamese, English, etc.)
2. Add specificity and context where missing
3. Structure the prompt clearly
4. Add role/persona if beneficial
5. Include output format expectations if needed
6. Remove ambiguity
7. Keep it concise but complete

Return ONLY the optimized prompt, nothing else."""

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        if genai is None:
            raise ImportError("Install google-generativeai: pip install google-generativeai")

        genai.configure(api_key=api_key)
        self.model = model
        self.generative_model = genai.GenerativeModel(model)

    def optimize(
        self,
        prompt: str,
        context: str = None,
    ) -> GeminiOptimizationResult:
        """Optimize a prompt using Gemini."""
        user_message = self._build_message(prompt, context)

        response = self.generative_model.generate_content(user_message)
        optimized = response.text.strip()

        explanation_resp = self.generative_model.generate_content(
            f"Explain briefly what changes you made to optimize this prompt:\n\n"
            f"Original: {prompt}\nOptimized: {optimized}"
        )
        explanation = explanation_resp.text.strip()

        return GeminiOptimizationResult(
            original=prompt,
            optimized=optimized,
            explanation=explanation,
            model=self.model,
        )

    def _build_message(self, prompt: str, context: str) -> str:
        parts = [f"{self.SYSTEM_PROMPT}\n\nOptimize this prompt:"]
        parts.append(f"Prompt: {prompt}")
        if context:
            parts.append(f"Context: {context}")
        return "\n".join(parts)

    def chat_optimize(self, prompt: str, feedback: str = None) -> GeminiOptimizationResult:
        """Optimize with follow-up feedback."""
        message = f"Optimize: {prompt}"
        if feedback:
            message += f"\n\nFeedback: {feedback}"

        response = self.generative_model.generate_content(message)
        optimized = response.text.strip()

        return GeminiOptimizationResult(
            original=prompt,
            optimized=optimized,
            explanation="Optimized with feedback" if feedback else "Initial optimization",
            model=self.model,
        )
