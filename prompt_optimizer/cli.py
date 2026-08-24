"""Command-line interface for prompt optimizer."""

import argparse
import json
import os
import sys
from pathlib import Path

from .optimizer import OptimizationLevel, PromptOptimizer


def main():
    parser = argparse.ArgumentParser(
        prog="prompt-optimizer",
        description="Optimize prompts for better LLM performance",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    optimize_parser = subparsers.add_parser("optimize", help="Optimize a prompt")
    optimize_parser.add_argument("prompt", nargs="?", help="Prompt to optimize")
    optimize_parser.add_argument(
        "-f", "--file", help="Read prompt from file"
    )
    optimize_parser.add_argument(
        "-l", "--level",
        choices=["minimal", "moderate", "aggressive"],
        default="moderate",
        help="Optimization level (default: moderate)",
    )
    optimize_parser.add_argument(
        "-o", "--output", help="Output file path"
    )
    optimize_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    optimize_parser.add_argument(
        "--ai", action="store_true", help="Use AI-powered optimization (OpenAI)"
    )
    optimize_parser.add_argument(
        "--opencode", action="store_true", help="Use OpenCode AI (local, no API key)"
    )
    optimize_parser.add_argument(
        "--model", default="gpt-4o-mini", help="AI model (default: gpt-4o-mini)"
    )
    optimize_parser.add_argument(
        "--context", help="Additional context for AI optimization"
    )

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a prompt")
    analyze_parser.add_argument("prompt", nargs="?", help="Prompt to analyze")
    analyze_parser.add_argument("-f", "--file", help="Read prompt from file")

    batch_parser = subparsers.add_parser("batch", help="Batch optimize prompts from file")
    batch_parser.add_argument("file", help="File with prompts (one per line)")
    batch_parser.add_argument(
        "-l", "--level",
        choices=["minimal", "moderate", "aggressive"],
        default="moderate",
    )
    batch_parser.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "optimize":
        handle_optimize(args)
    elif args.command == "analyze":
        handle_analyze(args)
    elif args.command == "batch":
        handle_batch(args)


def get_prompt(args) -> str:
    """Get prompt from argument or file."""
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    elif args.prompt:
        return args.prompt
    else:
        print("Enter your prompt (Ctrl+D or Ctrl+Z to finish):")
        return sys.stdin.read()


def handle_optimize(args):
    """Handle optimize command."""
    prompt = get_prompt(args)
    if not prompt.strip():
        print("Error: Empty prompt", file=sys.stderr)
        sys.exit(1)

    if args.opencode:
        try:
            from .opencode_optimizer import OpenCodePromptOptimizer
            optimizer = OpenCodePromptOptimizer()
            result = optimizer.optimize(prompt, context=args.context)

            output = format_opencode_result(result)

        except ConnectionError:
            print("Error: OpenCode is not running. Start OpenCode first.", file=sys.stderr)
            sys.exit(1)
        except ImportError:
            print("Error: Install requests: pip install requests", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.ai:
        try:
            from .ai_optimizer import AIPromptOptimizer
            optimizer = AIPromptOptimizer(model=args.model)
            result = optimizer.optimize(prompt, context=args.context)

            if args.json:
                output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
            else:
                output = format_ai_result(result)

        except ImportError:
            print("Error: Install openai: pip install openai", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        level = OptimizationLevel(args.level)
        optimizer = PromptOptimizer(level)
        result = optimizer.optimize(prompt)

        if args.json:
            output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        else:
            output = format_result(result)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Result saved to {args.output}")
    else:
        print(output)


def handle_analyze(args):
    """Handle analyze command."""
    prompt = get_prompt(args)
    if not prompt.strip():
        print("Error: Empty prompt", file=sys.stderr)
        sys.exit(1)

    optimizer = PromptOptimizer()
    analysis = optimizer.analyze(prompt)

    print("=" * 50)
    print("PROMPT ANALYSIS")
    print("=" * 50)
    print(f"Word count:        {analysis['word_count']}")
    print(f"Sentence count:    {analysis['sentence_count']}")
    print(f"Has role:          {'Yes' if analysis['has_role'] else 'No'}")
    print(f"Has structure:     {'Yes' if analysis['has_structure'] else 'No'}")
    print(f"Vague words:       {analysis['vague_words']}")
    print(f"Filler phrases:    {analysis['filler_phrases']}")
    print(f"Clarity score:     {analysis['clarity_score']}/100")
    print(f"Readability:       {analysis['readability']}")
    print("=" * 50)


def handle_batch(args):
    """Handle batch command."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    prompts = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    level = OptimizationLevel(args.level)
    optimizer = PromptOptimizer(level)
    results = optimizer.batch_optimize(prompts, level)

    output_lines = []
    for i, result in enumerate(results, 1):
        output_lines.append(f"--- Prompt {i} ---")
        output_lines.append(f"Original:\n{result.original}")
        output_lines.append(f"\nOptimized:\n{result.optimized}")
        output_lines.append(f"Score: {result.score:.1f}/100")
        if result.improvements:
            output_lines.append("Improvements:")
            for imp in result.improvements:
                output_lines.append(f"  - {imp}")
        output_lines.append("")

    output = "\n".join(output_lines)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Results saved to {args.output}")
    else:
        print(output)


def format_result(result) -> str:
    """Format optimization result for display."""
    lines = [
        "=" * 50,
        "PROMPT OPTIMIZATION RESULT",
        "=" * 50,
        "",
        "ORIGINAL:",
        result.original,
        "",
        "-" * 50,
        "OPTIMIZED:",
        result.optimized,
        "",
        "-" * 50,
        f"Score: {result.score:.1f}/100",
        "",
    ]

    if result.improvements:
        lines.append("IMPROVEMENTS:")
        for imp in result.improvements:
            lines.append(f"  + {imp}")
        lines.append("")

    lines.append("=" * 50)
    return "\n".join(lines)


def format_ai_result(result) -> str:
    """Format AI optimization result for display."""
    lines = [
        "=" * 50,
        "AI PROMPT OPTIMIZATION RESULT",
        "=" * 50,
        "",
        "ORIGINAL:",
        result.original,
        "",
        "-" * 50,
        "OPTIMIZED:",
        result.optimized,
        "",
        "-" * 50,
        f"Model: {result.model}",
        "",
        "EXPLANATION:",
        result.explanation,
        "",
        "=" * 50,
    ]
    return "\n".join(lines)


def format_opencode_result(result) -> str:
    """Format OpenCode optimization result for display."""
    lines = [
        "=" * 50,
        "OPENCODE AI OPTIMIZATION RESULT",
        "=" * 50,
        "",
        "ORIGINAL:",
        result.original,
        "",
        "-" * 50,
        "OPTIMIZED:",
        result.optimized,
        "",
        "-" * 50,
        "EXPLANATION:",
        result.explanation,
        "",
        "=" * 50,
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
