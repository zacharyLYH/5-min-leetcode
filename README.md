# 5-min-leetcode

A daily 5-minute LeetCode lesson — **we email you a link** to a lesson hosted on GitHub Pages, so expect a GitHub Pages URL in your inbox. Full lesson (not just email) has:
- Link to the problem
- Naive pattern (why it stalls)
- Gold pattern (properties, first-principles, how to start)
- Quiz to test insight
- Copyable code block

Delivered via GitHub Actions cron every day at **8am SGT (00:00 UTC)**. Email is minimal summary + CTA → `https://zacharylyh.github.io/5-min-leetcode/<slug>/`.

Add yourself to the mailing list by adding your email to `subscribers.csv` and make a PR.

# Development

## How it works

1. **Fetch** a random LeetCode question (any difficulty, skip premium) via GraphQL.
2. **Generate** structured JSON: `prompts/naive.txt`/`gold.txt` → `NAIVE_SCHEMA`/`GOLD_SCHEMA` (terse, pattern-focused, `first_principles`).
3. **Align** structured JSON: `prompts/align_html.txt` → `ALIGN_SCHEMA` (`contrast`/`trigger`/`quiz`) — insight Qs, not definitions.
4. **Build** full Tailwind page (`src/site_builder.py:1`, shadcn Card/Badge/Button, `cdn.tailwindcss.com`) → `site/<slug>/index.html` → `https://zacharylyh.github.io/5-min-leetcode/<slug>/`; validate HTML; **email** is tiny summary + link (`src/emailer.py:14` `build_email`).
5. **Send** batch via SMTP + deploy Pages (`keep_files: true` keeps archive).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in values
python -m src.main --dry-run # writes preview.html + site/<slug>/ (Tailwind, open locally)
open preview.html # opens up the preview.html generated. this is what the gh pages will look like
```

### GitHub Pages integration (one-time)

1. **Enable Pages:** Repo Settings → Pages → Source: `gh-pages` branch, `/ (root)`. Workflow already has `permissions: contents: write`.
2. **No token needed:** `GITHUB_TOKEN` is auto-provided by Actions — just use `github_token: ${{ secrets.GITHUB_TOKEN }}` in `.github/workflows/daily.yml:23` (already set).
3. **Deploy:** Daily cron (`0 0 * * *` 8am SGT) + `workflow_dispatch` runs `python -u -m src.main`, writes `site/<slug>/index.html`, then `peaceiris/actions-gh-pages@v4` pushes `publish_dir: ./site` to `gh-pages` with `keep_files: true` (keeps archive).
4. **URL:** `https://zacharylyh.github.io/5-min-leetcode/<titleSlug>/` (e.g. `.../two-sum/`). Email CTA points there; inbox is not full lesson.
5. **First run:** `gh-pages` branch auto-created on first successful deploy. For fork, update `HOSTED_BASE` in `src/main.py:13` if different user/repo.

### Env

| Var | Required | Example | Notes |
|-----|----------|---------|-------|
| `MODEL_PROVIDER_KEY` | yes | `sk-or-v1-...` | OpenAI-compatible API key (OpenRouter etc) |
| `MODEL_PROVIDER` | yes | `https://openrouter.ai/api/v1` | Base URL for OpenAI SDK |
| `MODEL_NAME` | yes | `openrouter/free` | Model ID |
| `SMTP_HOST` | yes | `smtp.gmail.com` |  |
| `SMTP_PORT` | yes | `587` | STARTTLS |
| `SMTP_USER` | yes | `you@gmail.com` | SMTP login |
| `SMTP_PASSWORD` | yes | `app password` | Gmail needs App Password |
| `SMTP_FROM` | yes | `you@gmail.com` | From address |

`SMTP_PORT=465` also works (SSL). See `.env.example`.

