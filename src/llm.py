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

def call_llm(client: "OpenAI", model: str, prompt: str, retries: int = 3, backoff: float = 2.0) -> str:
    last = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = resp.choices[0].message.content
            if not content:
                raise RuntimeError("Empty LLM response")
            return content.strip()
        except Exception as e:
            last = e
            if attempt == retries:
                break
            time.sleep(backoff ** attempt)
    raise RuntimeError(f"LLM failed after {retries} attempts: {last}")

def call_llm_structured(
    client: "OpenAI",
    model: str,
    prompt: str,
    json_schema: dict,  # e.g. {"name": "lesson", "strict": True, "schema": {...}}
    retries: int = 3,
) -> dict:
    """Structured output helper returning parsed JSON dict.
    Uses OpenRouter/OpenAI `response_format` syntax — other providers differ.
    See README Structured Outputs warning before switching providers.
    """
    import json

    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(  # type: ignore[union-attr]
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_schema", "json_schema": json_schema},  # type: ignore[arg-type]
                extra_body={"provider": {"require_parameters": True}},
            )
            content = resp.choices[0].message.content
            if not content:
                raise RuntimeError("Empty structured response")
            return json.loads(content.strip())
        except Exception as e:
            last = e
            if attempt == retries:
                break
            time.sleep(2.0**attempt)
    raise RuntimeError(f"Structured LLM failed after {retries}: {last}")


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
    # simple {{key}} replacement, keep unknown placeholders
    out = template
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out
