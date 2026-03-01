"""
Extract structured AI insights from raw text using an LLM.
Supports Gemini Flash (default), DeepSeek, and Anthropic.
"""
import os
import json
import re
from config import LLM_PROVIDER

EXTRACTION_PROMPT = """You are an AI analyst focused on agentic coding, work automation, and how AI transforms knowledge work.

Extract structured insights from the following content. Only extract insights relevant to:
- Agentic coding tools (Claude Code, Cursor, Copilot, Windsurf, Devin, etc.)
- AI-assisted development workflows and practices
- LLM model releases that meaningfully change what practitioners can do (skip minor benchmarks)
- Work automation: AI agents, pipelines, MCP servers, tool use
- AI for knowledge worker productivity (writing, analysis, research, code review)
- Practical tips, workflows, or techniques for using AI tools effectively

SKIP: pure ML research/theory, image generation, robotics, self-driving, AI policy/regulation, minor benchmark shuffles, sponsor reads, personal anecdotes.

Return ONLY a JSON array. Each item must have:
- "category": one of "agentic_coding", "model_release", "workflow", "tool", "productivity", "other"
- "model_or_tool": name of the model/tool (null if general insight)
- "summary": 1-2 sentence factual summary. Be specific — include version numbers, tool names, concrete capabilities.
- "significance": "major" (changes how you work), "minor" (useful to know), or "incremental" (small update)

If nothing relevant is found, return: []

Content:
---
{text}
---

JSON array:"""


def extract_insights_gemini(text: str) -> list[dict]:
    from google import genai
    from google.genai import types

    client = genai.Client()  # reads GEMINI_API_KEY from env
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=EXTRACTION_PROMPT.format(text=text),
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=4096),
    )
    return _parse_json_response(response.text)


def extract_insights_deepseek(text: str) -> list[dict]:
    import requests
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("Set DEEPSEEK_API_KEY environment variable")
    
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}],
            "temperature": 0.1,
            "max_tokens": 4096,
        },
    )
    resp.raise_for_status()
    return _parse_json_response(resp.json()["choices"][0]["message"]["content"])


def extract_insights_anthropic(text: str) -> list[dict]:
    import requests
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Set ANTHROPIC_API_KEY environment variable")
    
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}],
        },
    )
    resp.raise_for_status()
    return _parse_json_response(resp.json()["content"][0]["text"])


def _parse_json_response(text: str) -> list[dict]:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError as e:
        print(f"  ⚠ Failed to parse LLM JSON: {e}")
        print(f"  Raw response (first 200 chars): {text[:200]}")
        return []


# Dispatcher
_PROVIDERS = {
    "gemini": extract_insights_gemini,
    "deepseek": extract_insights_deepseek,
    "anthropic": extract_insights_anthropic,
}


def extract_insights(text: str) -> list[dict]:
    provider = LLM_PROVIDER
    fn = _PROVIDERS.get(provider)
    if not fn:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use: {list(_PROVIDERS.keys())}")
    return fn(text)
