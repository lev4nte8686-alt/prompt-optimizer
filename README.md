# Prompt Optimizer

A tool to optimize prompts for better LLM performance. Supports both CLI and Web UI.

## Features

- Remove filler words and vague language
- Add structure to long prompts
- Improve clarity and formatting
- Analyze prompt quality
- Batch optimize multiple prompts

## Installation

```bash
# Install with pip
pip install -e .

# Install with web UI support
pip install -e ".[web]"
```

## Usage

### CLI

```bash
# Optimize a prompt
prompt-optimizer optimize "your prompt here"

# Optimize with specific level
prompt-optimizer optimize -l aggressive "your prompt here"

# Optimize from file
prompt-optimizer optimize -f prompt.txt

# Analyze a prompt
prompt-optimizer analyze "your prompt here"

# Batch optimize
prompt-optimizer batch prompts.txt -o results.txt
```

### Web UI

```bash
# Run Streamlit app
streamlit run prompt_optimizer/web.py
```

## Optimization Levels

- **minimal**: Basic cleanup (filler words, whitespace)
- **moderate**: Structure suggestions, clarity improvements (default)
- **aggressive**: All optimizations plus tips and constraints

## License

MIT
