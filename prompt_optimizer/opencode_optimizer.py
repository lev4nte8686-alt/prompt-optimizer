"""AI-powered prompt optimizer using OpenCode API."""

import json
from dataclasses import dataclass

try:
    import requests
except ImportError:
    requests = None


@dataclass
class OpenCodeOptimizationResult:
    original: str
    optimized: str
    explanation: str

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "optimized": self.optimized,
            "explanation": self.explanation,
        }


class OpenCodePromptOptimizer:
    """AI-powered prompt optimizer using local OpenCode API."""

    SYSTEM_PROMPT = """You are an expert prompt engineer. Optimize the given prompt for better LLM performance.

Rules:
1. Keep the original intent and language
2. Add specificity and context where missing
3. Structure the prompt clearly
4. Add role/persona if beneficial
5. Include output format expectations if needed
6. Remove ambiguity
7. Keep it concise but complete

Return ONLY the optimized prompt, nothing else."""

    def __init__(self, base_url: str = "http://localhost:4096"):
        if requests is None:
            raise ImportError("Install requests: pip install requests")

        self.base_url = base_url
        self._check_connection()

    def _check_connection(self):
        """Check if OpenCode server is running."""
        try:
            resp = requests.get(f"{self.base_url}/global/health", timeout=5)
            if resp.status_code != 200:
                raise ConnectionError("OpenCode server not responding")
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to OpenCode at {self.base_url}. "
                "Make sure OpenCode is running."
            )

    def optimize(
        self,
        prompt: str,
        context: str = None,
    ) -> OpenCodeOptimizationResult:
        """Optimize a prompt using OpenCode API."""
        user_message = self._build_message(prompt, context)

        response = self._chat(user_message)

        explanation_resp = self._chat(
            f"Explain briefly what changes you made to optimize this prompt:\n\n"
            f"Original: {prompt}\nOptimized: {response}"
        )

        return OpenCodeOptimizationResult(
            original=prompt,
            optimized=response,
            explanation=explanation_resp,
        )

    def _build_message(self, prompt: str, context: str) -> str:
        parts = [f"{self.SYSTEM_PROMPT}\n\nOptimize this prompt:"]
        parts.append(f"Prompt: {prompt}")
        if context:
            parts.append(f"Context: {context}")
        return "\n".join(parts)

    def _chat(self, message: str) -> str:
        """Send a chat message to OpenCode and get response."""
        payload = {
            "parts": [{"type": "text", "text": message}],
        }

        resp = requests.post(
            f"{self.base_url}/session",
            json={"title": "Prompt Optimization"},
            timeout=10,
        )
        session_id = resp.json()["id"]

        resp = requests.post(
            f"{self.base_url}/session/{session_id}/message",
            json=payload,
            timeout=60,
        )

        data = resp.json()
        parts = data.get("parts", [])
        text_parts = [p["text"] for p in parts if p.get("type") == "text"]
        return "\n".join(text_parts) if text_parts else ""

    def chat_optimize(self, prompt: str, feedback: str = None) -> OpenCodeOptimizationResult:
        """Optimize with follow-up feedback."""
        message = f"Optimize: {prompt}"
        if feedback:
            message += f"\n\nFeedback: {feedback}"

        response = self._chat(message)

        return OpenCodeOptimizationResult(
            original=prompt,
            optimized=response,
            explanation="Optimized with feedback" if feedback else "Initial optimization",
        )
