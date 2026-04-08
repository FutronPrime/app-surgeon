#!/usr/bin/env python3
"""futron-mcp-code-translate — Local AI code translator MCP server.

Translates code between ANY programming languages using local Ollama (zero cost).
Based on aiTrans architecture with Ollama connector replacing OpenAI.

Also works as standalone CLI:
    futron-mcp-code-translate --cli -s input.py -l rust
    futron-mcp-code-translate --cli -s design.txt -l python --allfile
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request

# ── LLM Connector (LLM-agnostic) ─────────────────────────────────

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("CODE_TRANSLATE_MODEL", "avani-uncensored-v4")

# Supported providers: ollama (default), openai, anthropic, any OpenAI-compatible
PROVIDER = os.environ.get("CODE_TRANSLATE_PROVIDER", "ollama")
API_KEY = os.environ.get("CODE_TRANSLATE_API_KEY", "")


def call_llm(prompt: str, system: str = "") -> str:
    """Call the configured LLM provider. Returns generated text."""
    if not system:
        system = (
            "You are an expert programmer and code translator. "
            "Write ONLY the raw code output, no explanations, no markdown fences, "
            "no backticks. Include comments on each function. "
            "The output must be valid, ready-to-execute code."
        )

    if PROVIDER == "ollama":
        return _call_ollama(prompt, system)
    elif PROVIDER in ("openai", "openai-compatible"):
        return _call_openai_compatible(prompt, system)
    else:
        return _call_ollama(prompt, system)  # default fallback


def _call_ollama(prompt: str, system: str) -> str:
    """Call local Ollama API."""
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 4096},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("message", {}).get("content", "")
    except Exception as e:
        return f"// ERROR: LLM call failed: {e}"


def _call_openai_compatible(prompt: str, system: str) -> str:
    """Call any OpenAI-compatible API (OpenAI, OpenRouter, Together, etc.)."""
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"// ERROR: API call failed: {e}"


def remove_code_blocks(code: str) -> str:
    """Strip markdown code fences from LLM output."""
    lines = []
    for line in code.splitlines():
        if not line.strip().startswith("```"):
            lines.append(line)
    return "\n".join(lines)


def translate_code(source_code: str, target_lang: str, source_lang: str = "") -> str:
    """Translate source code to target language."""
    if source_lang:
        prompt = (
            f"Translate this {source_lang} code to valid {target_lang} code. "
            f"Output ONLY the translated code, no explanations:\n\n{source_code}"
        )
    else:
        prompt = (
            f"Write valid {target_lang} code for the following. "
            f"Output ONLY the code, ready to execute, with comments:\n\n{source_code}"
        )
    result = call_llm(prompt)
    return remove_code_blocks(result)


def translate_file(filepath: str, target_lang: str, allfile: bool = True) -> str:
    """Translate a source file to target language."""
    with open(filepath) as f:
        source = f.read()

    # Detect source language from extension
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".rs": "Rust", ".go": "Go", ".java": "Java", ".c": "C",
        ".cpp": "C++", ".cs": "C#", ".rb": "Ruby", ".php": "PHP",
        ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
        ".r": "R", ".sh": "Bash", ".ps1": "PowerShell",
        ".sql": "SQL", ".html": "HTML", ".css": "CSS",
        ".ai": "English description", ".txt": "English description",
    }
    ext = os.path.splitext(filepath)[1].lower()
    source_lang = ext_map.get(ext, "")

    if allfile:
        return translate_code(source, target_lang, source_lang)
    else:
        # Line-by-line mode (for English descriptions / pseudocode)
        output = []
        for line in source.splitlines():
            if line.strip().startswith("#") or not line.strip():
                output.append(line)
            else:
                translated = translate_code(line, target_lang)
                output.append(translated)
        return "\n".join(output)


# ── MCP Server ────────────────────────────────────────────────────

def run_mcp_server():
    """Run as MCP server (stdio transport)."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("futron-code-translate", instructions="""
    AI Code Translator — translate code between ANY programming languages
    using local Ollama (zero cost). Supports: Python, JavaScript, TypeScript,
    Rust, Go, Java, C, C++, C#, Ruby, PHP, Swift, Kotlin, Scala, R, Bash,
    PowerShell, SQL, HTML, CSS, and more. Can also convert English descriptions
    into working code.
    """)

    @mcp.tool()
    def translate(source_code: str, target_language: str, source_language: str = "") -> str:
        """Translate code from one language to another.
        source_code: the code to translate
        target_language: language to translate TO (e.g. 'rust', 'python', 'go')
        source_language: optional, language translating FROM (auto-detected if empty)"""
        return translate_code(source_code, target_language, source_language)

    @mcp.tool()
    def translate_file_tool(file_path: str, target_language: str) -> str:
        """Translate an entire source file to another language.
        file_path: path to the source file
        target_language: language to translate TO"""
        if not os.path.exists(file_path):
            return f"ERROR: File not found: {file_path}"
        return translate_file(file_path, target_language, allfile=True)

    @mcp.tool()
    def english_to_code(description: str, language: str) -> str:
        """Convert an English description into working code.
        description: natural language description of what the code should do
        language: target programming language"""
        return translate_code(description, language, "English description")

    @mcp.tool()
    def supported_languages() -> str:
        """List all supported programming languages for translation."""
        langs = [
            "Python", "JavaScript", "TypeScript", "Rust", "Go", "Java",
            "C", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala",
            "R", "Bash", "PowerShell", "SQL", "HTML", "CSS", "Lua",
            "Perl", "Haskell", "Elixir", "Dart", "Objective-C",
            "Assembly", "COBOL", "Fortran", "MATLAB", "Julia",
        ]
        return "Supported languages:\n" + ", ".join(langs) + "\n\nAny language the LLM knows can be used as source or target."

    mcp.run(transport="stdio")


# ── CLI Mode ──────────────────────────────────────────────────────

def run_cli():
    """Run as standalone CLI tool."""
    parser = argparse.ArgumentParser(
        description="AI Code Translator — translate code between any languages (local Ollama)"
    )
    parser.add_argument("-s", "--source", required=True, help="Source file to translate")
    parser.add_argument("-l", "--language", default="python", help="Target language")
    parser.add_argument("-a", "--allfile", action="store_true", help="Translate entire file at once")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    result = translate_file(args.source, args.language, args.allfile or True)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Translated to {args.output}", file=sys.stderr)
    else:
        print(result)


# ── Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        run_cli()
    else:
        run_mcp_server()
