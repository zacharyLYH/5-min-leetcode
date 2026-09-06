from __future__ import annotations

import json
import re as _re
import time
from typing import TYPE_CHECKING

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    if TYPE_CHECKING:
        from openai import OpenAI  # type: ignore
    else:
        OpenAI = object  # type: ignore

def make_client(base_url: str, api_key: str) -> "OpenAI":
    return OpenAI(base_url=base_url, api_key=api_key)  # type: ignore[call-arg,operator]

def _call_with_retry(client: "OpenAI", kwargs: dict, retries: int, backoff: float) -> str:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(**kwargs)  # type: ignore[union-attr]
            content = resp.choices[0].message.content
            if not content:
                raise RuntimeError("Empty LLM response")
            return content.strip()
        except Exception as e:
            last = e
            if attempt == retries:
                break
            time.sleep(backoff**attempt)
    raise RuntimeError(f"LLM failed after {retries} attempts: {last}")


def call_llm(client: "OpenAI", model: str, prompt: str, retries: int = 3, backoff: float = 2.0) -> str:
    return _call_with_retry(
        client,
        {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7},
        retries,
        backoff,
    )


def call_llm_structured(
    client: "OpenAI",
    model: str,
    prompt: str,
    json_schema: dict,
    retries: int = 3,
) -> dict:
    raw = _call_with_retry(
        client,
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {"type": "json_schema", "json_schema": json_schema},  # type: ignore[arg-type]
            "extra_body": {"provider": {"require_parameters": True}},
        },
        retries,
        2.0,
    )
    return json.loads(raw)


_PROMPT_RE = _re.compile(r"\{\{(\w+)\}\}")


def render_prompt(template: str, problem: dict, extra: dict | None = None) -> str:
    ctx = {
        "title": problem.get("title", ""),
        "titleSlug": problem.get("titleSlug", ""),
        "difficulty": problem.get("difficulty", ""),
        "content": problem.get("content", ""),
        "url": problem.get("url", ""),
        "topicTags": ", ".join(problem.get("topicTags", [])),
        "exampleTestcases": problem.get("exampleTestcases", ""),
    }
    if extra:
        ctx.update(extra)
    return _PROMPT_RE.sub(lambda m: str(ctx.get(m.group(1), m.group(0))), template)
