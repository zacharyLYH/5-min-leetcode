import argparse
import json
import pathlib
import sys
from .config import Settings
from .leetcode import fetch_random_problem
from .llm import call_llm, call_llm_structured, make_client, render_prompt
from .emailer import build_email, send_batch
from .schemas import ALIGN_SCHEMA, GOLD_SCHEMA, NAIVE_SCHEMA
from .site_builder import build_full_page
from .validate_html import validate_html

PROMPT_DIR = pathlib.Path(__file__).parent.parent / "prompts"
MAX_ALIGN_ATTEMPTS = 3
HOSTED_BASE = "https://zacharylyh.github.io/5-min-leetcode"


def load_prompt(name: str) -> str:
    p = PROMPT_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing prompt: {p}")
    return p.read_text(encoding="utf-8")


def _code_ok(data: dict) -> bool:
    import ast

    sc = data.get("starter_code")
    code = ""
    if isinstance(sc, dict):
        code = str(sc.get("code") or "")
    elif isinstance(sc, str):
        code = sc
    if not code.strip():
        return True  # empty is allowed
    try:
        ast.parse(code)
        return "\n" in code  # must have newlines, not minified
    except SyntaxError:
        return False


def _get_structured(client, model, prompt, schema) -> dict:
    """Try structured output; fallback to plain + json.loads for providers that don't support it."""
    try:
        return call_llm_structured(client, model, prompt, schema)
    except Exception as e:  # noqa: BLE001
        msg = str(e).lower()
        if "response_format" in msg or "json_schema" in msg or "structured" in msg:
            raw = call_llm(client, model, prompt)
            return json.loads(raw)
        raise


def _get_with_code_check(client, model, prompt, schema, label: str) -> dict:
    data = _get_structured(client, model, prompt, schema)
    if _code_ok(data):
        return data
    print(f"  ⚠ {label} code failed ast.parse or minified, retrying...", file=sys.stderr)
    retry_prompt = prompt + "\n\n[RETRY: starter_code must be valid Python with newlines+indent, ast.parse-able, not single-line. Fix only that field.]"
    data2 = _get_structured(client, model, retry_prompt, schema)
    if not _code_ok(data2):
        print(f"  ⚠ {label} still invalid after retry, keeping anyway", file=sys.stderr)
    return data2


def main() -> None:
    parser = argparse.ArgumentParser(description="5-min-leetcode daily sender")
    parser.add_argument("--dry-run", action="store_true", help="Generate HTML but don't send email")
    parser.add_argument("--output", type=str, default="preview.html", help="Dry-run output file")
    args = parser.parse_args()

    print("→ Loading config...")
    settings = Settings()
    print(f"  {settings}")

    print("→ Fetching random LeetCode problem...")
    problem = fetch_random_problem()
    print(f"  {problem['title']} [{problem['difficulty']}] {problem['url']}")

    client = make_client(settings.model_provider, settings.model_key)

    naive_tpl = load_prompt("naive.txt")
    gold_tpl = load_prompt("gold.txt")
    align_tpl = load_prompt("align_html.txt")

    print("→ Generating naive lesson (structured JSON 1/3)...")
    naive: dict = _get_with_code_check(client, settings.model_name, render_prompt(naive_tpl, problem), NAIVE_SCHEMA, "naive")
    print(f"  naive pattern: {naive.get('pattern')}")

    print("→ Generating gold lesson (structured JSON 2/3)...")
    gold: dict = _get_with_code_check(client, settings.model_name, render_prompt(gold_tpl, problem), GOLD_SCHEMA, "gold")
    print(f"  gold pattern: {gold.get('pattern')}")

    # alignment (structured) + build full page + validate in retry loop
    align_prompt_base = render_prompt(
        align_tpl, problem, extra={"naive": json.dumps(naive, indent=2), "gold": json.dumps(gold, indent=2)}
    )
    full_html = ""
    align: dict = {}
    issues: list[str] = []
    for attempt in range(1, MAX_ALIGN_ATTEMPTS + 1):
        print(f"→ Generating alignment (structured JSON 3/3, attempt {attempt}/{MAX_ALIGN_ATTEMPTS})...")
        prompt = align_prompt_base
        if attempt > 1:
            prompt += f"\n\n[RETRY {attempt}: previous HTML failed validation {issues} — keep JSON tight, succinct.]"
        align = _get_structured(client, settings.model_name, prompt, ALIGN_SCHEMA)
        print(f"  align contrast: {len(align.get('contrast', []))} bullets, quiz: {len(align.get('quiz', []))}")

        print("→ Building full page (Tailwind)...")
        full_html = build_full_page(problem, naive, gold, align)

        print("→ Validating HTML...")
        ok, issues = validate_html(full_html)
        if ok:
            print(f"  ✓ HTML valid ({len(full_html)} bytes)")
            break
        print(f"  ⚠ HTML invalid (attempt {attempt}): {issues}", file=sys.stderr)
        if attempt == MAX_ALIGN_ATTEMPTS:
            print(f"✗ HTML validation failed after {MAX_ALIGN_ATTEMPTS} attempts: {issues}", file=sys.stderr)
            sys.exit(1)
        print("  → retrying alignment...")

    slug = str(problem.get("titleSlug") or "lesson")
    hosted_url = f"{HOSTED_BASE.rstrip('/')}/{slug}/"
    subject = f"5-min LeetCode: {problem['title']} [{problem['difficulty']}]"

    # write site for Pages + preview for local
    site_dir = pathlib.Path("site") / slug
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "index.html").write_text(full_html, encoding="utf-8")
    print(f"  site → {site_dir / 'index.html'} ({hosted_url})")

    if args.dry_run:
        pathlib.Path(args.output).write_text(full_html, encoding="utf-8")
        print(f"✓ Dry run: wrote {args.output} + site ({len(full_html)} bytes), no email/deploy.")
        return

    # email is just summary + link
    email_html = build_email(problem, align, hosted_url)
    recipients = settings.load_recipients()
    print(f"→ Sending batch to {len(recipients)} recipient(s) via {settings.smtp_host}:{settings.smtp_port} ...")
    results = send_batch(settings, subject, email_html, recipients)
    for email, status in results.items():
        print(f"  {email}: {status}")
    failed = [e for e, s in results.items() if s != "ok"]
    if failed:
        print(f"✗ {len(failed)} sends failed: {failed}", file=sys.stderr)
        sys.exit(1)
    print(f"✓ Batch sent to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        print(f"✗ Failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
