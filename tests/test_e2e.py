import json
import pathlib
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src import emailer, site_builder, validate_html
from src.schemas import NAIVE_SCHEMA

FAKE_PROBLEM = {
    "title": "Two Sum",
    "titleSlug": "two-sum",
    "difficulty": "Easy",
    "content": "<p>Given an array...</p>",
    "topicTags": ["Array", "Hash Table"],
    "url": "https://leetcode.com/problems/two-sum/",
    "exampleTestcases": "[2,7,11,15]\\n9",
}

FAKE_NAIVE = {
    "pattern": "Brute Force Nested Loops",
    "why_obvious": "Pairs scream nested loops",
    "why_stalls": ["O(n^2) on n=1e5", "Repeated work"],
    "complexity": "O(n^2) time, O(1) space",
    "starter_code": "for i in range(n):\n    for j in range(i+1, n):\n        if nums[i]+nums[j]==target:\n            return [i,j]",
    "takeaway": "n up to 1e5 -> need hash",
}

FAKE_GOLD = {
    "pattern": "Hash Map One Pass",
    "concept": "A hash map is just a lookup table. If you remember what you've seen, you can ask 'do I already have the number I need?' instantly instead of scanning again.",
    "properties": ["Need pair sum target, unsorted array", "Complement lookup can be O(1) with hash"],
    "triggers": ["target sum", "pair exists", "need O(n)"],
    "first_principles": ["Imagine you see numbers one by one — you could remember each in a table", "When you need target-x, check the table first before scanning the rest", "That check is O(1), so whole pass becomes O(n)"],
    "how_to_start": ["Ask: can I store seen?", "Use complement"],
    "plan": ["Iterate", "Check complement", "Insert"],
    "starter_code": {"language": "python", "code": "def two_sum(nums, target):\n    seen={}\n    for i,x in enumerate(nums):\n        if target-x in seen:\n            return [seen[target-x], i]\n        seen[x]=i\n    return []"},
    "complexity": "O(n) time, O(n) space",
    "checklist": "Need pair with target -> hash complement",
}

FAKE_ALIGN = {
    "contrast": ["Brute O(n^2) vs Hash O(n)", "When n>1e4 switch", "Trigger: target pair"],
    "trigger": "Need pair with target → hash complement",
    "quiz": [
        {"question": "Why does hash work here but not if array was sorted and needed two pointers?", "answer": "Unsorted + O(1) lookup beats sort overhead", "hint": "What property does hash exploit?"},
        {"question": "What breaks if you don't store complement before insert?", "answer": "Misses pair using same element"},
    ],
}


def _mock_client():
    m = MagicMock()

    def _create(**kwargs):
        rf = kwargs.get("response_format")
        if rf is not None:
            name = rf["json_schema"]["name"]
            if name == "naive_lesson":
                content = json.dumps(FAKE_NAIVE)
            elif name == "gold_lesson":
                content = json.dumps(FAKE_GOLD)
            elif name == "alignment":
                content = json.dumps(FAKE_ALIGN)
            else:
                content = json.dumps({})
        else:
            content = json.dumps(FAKE_ALIGN)
        extra = kwargs.get("extra_body") or {}
        assert extra.get("provider", {}).get("require_parameters") is True, "require_parameters must be True"
        resp = MagicMock()
        resp.choices = [MagicMock(message=MagicMock(content=content))]
        return resp

    m.chat.completions.create.side_effect = _create
    return m


def test_site_builder_with_shadcn():
    html = site_builder.build_full_page(FAKE_PROBLEM, FAKE_NAIVE, FAKE_GOLD, FAKE_ALIGN)
    ok, issues = validate_html.validate_html(html)
    assert ok, f"should be valid: {issues}"
    assert "Brute Force" in html
    assert "Hash Map" in html
    assert "View on LeetCode" in html
    # shadcn classes, Tailwind CDN, dark mode, responsive
    assert "rounded-xl border" in html
    assert 'cdn.tailwindcss.com' in html
    assert "Copy</button>" in html
    assert 'dark:bg-slate-950' in html  # dark mode
    assert 'max-w-2xl' in html  # responsive container
    assert html.count("style=") < 5  # KISS: classes not inline styles


def test_email_is_minimal_link():
    url = "https://zacharylyh.github.io/5-min-leetcode/two-sum/"
    html = emailer.build_email(FAKE_PROBLEM, FAKE_ALIGN, url)
    assert url in html
    assert "Read 5-min lesson" in html
    assert "Brute Force" not in html  # email is summary only, not full naive
    assert "Spot it:" in html
    # email keeps inline styles for client compat, but lean
    assert 'max-width:560px' in html
    assert html.count("<a href") >= 2


def test_align_templated_flexibility():
    varying = dict(FAKE_ALIGN, quiz=[{"question": "Q?", "answer": "A"}])
    html = site_builder.build_full_page(FAKE_PROBLEM, FAKE_NAIVE, FAKE_GOLD, varying)
    assert html.count("Q1:") == 1
    varying3 = dict(FAKE_ALIGN, quiz=[{"question": f"Q{i}?", "answer": "A"} for i in range(3)])
    html3 = site_builder.build_full_page(FAKE_PROBLEM, FAKE_NAIVE, FAKE_GOLD, varying3)
    assert html3.count("Q3:") == 1


@patch("src.main.fetch_random_problem", return_value=FAKE_PROBLEM)
@patch("src.main.make_client")
@patch("src.main.send_batch")
def test_e2e_dry_run_exercises_all_blocks(mock_send, mock_make, mock_fetch, tmp_path, monkeypatch):
    mock_make.return_value = _mock_client()
    for k, v in {
        "MODEL_PROVIDER_KEY": "sk-test",
        "MODEL_PROVIDER": "https://example.com/v1",
        "MODEL_NAME": "test-model",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "a@b.com",
        "SMTP_PASSWORD": "pw",
        "SMTP_FROM": "a@b.com",
    }.items():
        monkeypatch.setenv(k, v)

    out = tmp_path / "preview.html"
    with patch.object(sys, "argv", ["main.py", "--dry-run", "--output", str(out)]):
        from src.main import main

        main()

    assert out.exists()
    html = out.read_text()
    assert "Two Sum" in html
    assert "cdn.tailwindcss.com" in html
    ok, _ = validate_html.validate_html(html)
    assert ok
    mock_make.assert_called_once()
    client = mock_make.return_value
    assert client.chat.completions.create.call_count >= 3
    mock_send.assert_not_called()
    mock_fetch.assert_called_once()


@patch("src.main.fetch_random_problem", return_value=FAKE_PROBLEM)
@patch("src.main.make_client")
@patch("src.main.send_batch", return_value={"a@b.com": "ok"})
@patch("src.config.Settings.load_recipients", return_value=["a@b.com"])
def test_e2e_batch_send_and_validation_retry(mock_recipients, mock_send, mock_make, mock_fetch, monkeypatch):
    mock_make.return_value = _mock_client()
    for k, v in {
        "MODEL_PROVIDER_KEY": "sk-test",
        "MODEL_PROVIDER": "https://example.com/v1",
        "MODEL_NAME": "test-model",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "a@b.com",
        "SMTP_PASSWORD": "pw",
        "SMTP_FROM": "a@b.com",
    }.items():
        monkeypatch.setenv(k, v)

    orig_validate = validate_html.validate_html
    calls = {"n": 0}

    def _fake_validate(html):
        calls["n"] += 1
        if calls["n"] == 1:
            return False, ["mocked failure"]
        return orig_validate(html)

    with patch("src.main.validate_html", side_effect=_fake_validate), patch.object(sys, "argv", ["main.py"]):
        from src.main import main

        main()

    assert calls["n"] >= 2
    mock_send.assert_called_once()
    # email sent should contain hosted url, not full content
    assert "zacharylyh.github.io/5-min-leetcode/two-sum/" in mock_send.call_args[0][2]


@patch("src.main.call_llm_structured")
@patch("src.main.call_llm")
def test_structured_fallback_path(mock_plain, mock_struct):
    mock_struct.side_effect = RuntimeError("response_format not supported")
    mock_plain.return_value = json.dumps(FAKE_NAIVE)
    from src.main import _get_structured

    client = MagicMock()
    out = _get_structured(client, "m", "prompt", NAIVE_SCHEMA)
    assert out["pattern"] == FAKE_NAIVE["pattern"]
    mock_plain.assert_called_once()
