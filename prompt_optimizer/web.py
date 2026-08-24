"""Web UI for prompt optimizer using Streamlit."""

import os
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

import streamlit as st

try:
    from .optimizer import OptimizationLevel, PromptOptimizer
except ImportError:
    from optimizer import OptimizationLevel, PromptOptimizer


def main():
    st.set_page_config(
        page_title="Prompt Optimizer",
        page_icon=":zap:",
        layout="wide",
    )

    st.title("Prompt Optimizer")
    st.markdown("Optimize your prompts for better LLM performance")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input")
        prompt_input = st.text_area(
            "Enter your prompt:",
            height=200,
            placeholder="Type or paste your prompt here...",
        )

        mode = st.radio(
            "Optimization Mode",
            ["Rule-based", "Google Gemini (Free)", "OpenAI"],
            horizontal=True,
        )

        if mode == "Rule-based":
            level = st.select_slider(
                "Optimization Level",
                options=["minimal", "moderate", "aggressive"],
                value="moderate",
            )
        elif mode == "Google Gemini (Free)":
            api_key = st.text_input(
                "Gemini API Key (Free)",
                type="password",
                value=os.getenv("GEMINI_API_KEY", ""),
                help="Get free key from https://aistudio.google.com/apikey",
            )
            st.success("Free tier: 250 req/ngay, không cần credit card")
        else:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="Get your key from https://platform.openai.com/api-keys",
            )

        context = st.text_input(
            "Context (optional)",
            placeholder="Additional context for optimization...",
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            optimize_btn = st.button("Optimize", type="primary", use_container_width=True)
        with col_btn2:
            analyze_btn = st.button("Analyze", use_container_width=True)

    with col2:
        st.subheader("Output")

        if optimize_btn and prompt_input:
            if mode == "Rule-based":
                optimizer = PromptOptimizer(OptimizationLevel(level))
                result = optimizer.optimize(prompt_input)

                st.markdown("**Optimized Prompt:**")
                st.code(result.optimized, language=None)

                st.metric("Score", f"{result.score:.1f}/100")

                if result.improvements:
                    st.markdown("**Improvements:**")
                    for imp in result.improvements:
                        st.markdown(f"- {imp}")

            elif mode == "Google Gemini (Free)":
                if not api_key:
                    st.error("Please enter your Gemini API key")
                    st.info("Get free key: https://aistudio.google.com/apikey")
                else:
                    try:
                        try:
                            from .gemini_optimizer import GeminiPromptOptimizer
                        except ImportError:
                            from gemini_optimizer import GeminiPromptOptimizer

                        with st.spinner("Optimizing with Gemini..."):
                            ai_optimizer = GeminiPromptOptimizer(api_key=api_key)
                            result = ai_optimizer.optimize(prompt_input, context=context)

                        st.markdown("**AI-Optimized Prompt:**")
                        st.code(result.optimized, language=None)

                        st.markdown(f"**Model:** {result.model}")

                        with st.expander("Explanation"):
                            st.write(result.explanation)

                    except ImportError:
                        st.error("Install: `pip install google-generativeai`")
                    except Exception as e:
                        st.error(f"Error: {e}")

            else:
                if not api_key:
                    st.error("Please enter your OpenAI API key")
                else:
                    try:
                        try:
                            from .ai_optimizer import AIPromptOptimizer
                        except ImportError:
                            from ai_optimizer import AIPromptOptimizer

                        os.environ["OPENAI_API_KEY"] = api_key
                        with st.spinner("Optimizing with OpenAI..."):
                            ai_optimizer = AIPromptOptimizer(model="gpt-4o-mini")
                            result = ai_optimizer.optimize(prompt_input, context=context)

                        st.markdown("**AI-Optimized Prompt:**")
                        st.code(result.optimized, language=None)

                        with st.expander("Explanation"):
                            st.write(result.explanation)

                    except ImportError:
                        st.error("Install: `pip install openai`")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif analyze_btn and prompt_input:
            optimizer = PromptOptimizer()
            analysis = optimizer.analyze(prompt_input)

            st.markdown("**Analysis Results:**")

            cols = st.columns(3)
            with cols[0]:
                st.metric("Words", analysis["word_count"])
                st.metric("Sentences", analysis["sentence_count"])
            with cols[1]:
                st.metric("Clarity Score", f"{analysis['clarity_score']}/100")
                st.metric("Readability", analysis["readability"])
            with cols[2]:
                st.metric("Has Role", "Yes" if analysis["has_role"] else "No")
                st.metric("Has Structure", "Yes" if analysis["has_structure"] else "No")

            if analysis["vague_words"] > 0:
                st.warning(f"Found {analysis['vague_words']} vague word(s)")
            if analysis["filler_phrases"] > 0:
                st.warning(f"Found {analysis['filler_phrases']} filler phrase(s)")

        elif not prompt_input:
            st.info("Enter a prompt and click Optimize or Analyze")

    st.markdown("---")
    st.markdown("Built with Streamlit | [GitHub](https://github.com/lev4nte8686-alt/prompt-optimizer)")


if __name__ == "__main__":
    main()
