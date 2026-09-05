"""Best-effort HTML validation.

No tool can 100% guarantee "complete/correct" HTML (HTML is forgiving),
but we can catch truncated, unbalanced, or LLM-broken output before sending.
Checks:
  - required scaffolding (doctype, html, head, body)
  - tag balance via html.parser (stack for non-void elements)
  - presence of expected 5-min-leetcode sections (problem link, naive, gold)
  - length / truncation heuristics
"""

from html.parser import HTMLParser

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

REQUIRED_FRAGMENTS = [
    "5-min LeetCode",
    "View on LeetCode",
    "Naive Solution",
    "Gold Pattern",
]


class _StackParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.seen_tags: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.seen_tags.add(tag)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        self.seen_tags.add(tag)
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}> with empty stack")
            return
        # pop until we find matching (report mismatch but recover)
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            # look for tag deeper in stack -> unclosed intermediate
            if tag in self.stack:
                idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
                unclosed = self.stack[idx + 1 :]
                self.errors.append(f"unclosed {unclosed} before </{tag}>")
                self.stack = self.stack[:idx]
            else:
                self.errors.append(f"mismatched </{tag}>; stack={self.stack[-3:]}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.seen_tags.add(tag.lower())


def validate_html(html: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    low = html.lower()

    # 1. scaffolding
    if "<!doctype html" not in low:
        issues.append("missing <!DOCTYPE html>")
    for tag in ("<html", "<head", "<body"):
        if tag not in low:
            issues.append(f"missing {tag}>")
    for tag in ("</html>", "</body>"):
        if tag not in low:
            issues.append(f"missing {tag}")

    # 2. tag balance
    parser = _StackParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as e:  # noqa: BLE001
        issues.append(f"parser error: {e}")
    if parser.errors:
        issues.extend(parser.errors)
    if parser.stack:
        issues.append(f"unclosed tags at EOF: {parser.stack[-5:]}")

    # 3. expected sections
    for frag in REQUIRED_FRAGMENTS:
        if frag.lower() not in low:
            issues.append(f'missing expected section: "{frag}"')

    # 4. length / truncation
    if len(html) < 1500:
        issues.append(f"suspiciously short ({len(html)} bytes) — likely truncated")
    if len(html) > 200_000:
        issues.append(f"suspiciously large ({len(html)} bytes) — likely runaway LLM")
    # unbalanced details/summary is common LLM failure
    if low.count("<details") != low.count("</details>"):
        issues.append("mismatched <details> count")

    return (len(issues) == 0, issues)
