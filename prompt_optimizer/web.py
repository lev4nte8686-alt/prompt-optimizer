"""Web UI for prompt optimizer using Streamlit."""

import streamlit as st

from .optimizer import OptimizationLevel, PromptOptimizer


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

        level = st.select_slider(
            "Optimization Level",
            options=["minimal", "moderate", "aggressive"],
            value="moderate",
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            optimize_btn = st.button("Optimize", type="primary", use_container_width=True)
        with col_btn2:
            analyze_btn = st.button("Analyze", use_container_width=True)

    with col2:
        st.subheader("Output")

        if optimize_btn and prompt_input:
            optimizer = PromptOptimizer(OptimizationLevel(level))
            result = optimizer.optimize(prompt_input)

            st.markdown("**Optimized Prompt:**")
            st.code(result.optimized, language=None)

            st.metric("Score", f"{result.score:.1f}/100")

            if result.improvements:
                st.markdown("**Improvements:**")
                for imp in result.improvements:
                    st.markdown(f"- {imp}")

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
    st.markdown("Built with Streamlit | [GitHub](https://github.com/yourusername/prompt-optimizer)")


if __name__ == "__main__":
    main()
