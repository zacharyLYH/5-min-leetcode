from __future__ import annotations

import ast as _ast
import html as html_lib
import json as _json
import re as _re

from .utils import clean as _clean

TEMPLATE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — 5-min LeetCode</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{darkMode:'class'}}</script>
</head>
<body class="bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 antialiased overflow-x-hidden">
<header class="bg-slate-900 dark:bg-black text-white sticky top-0 z-10">
  <div class="max-w-2xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-3">
    <div class="min-w-0 flex-1">
      <div class="text-[10px] tracking-widest opacity-60 uppercase">5-min LeetCode</div>
      <h1 class="text-xl sm:text-2xl font-bold leading-tight break-words [overflow-wrap:anywhere]">{title}</h1>
      <div class="mt-2 flex gap-2 items-center flex-wrap">
        <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold {difficulty_bg} text-white">{difficulty}</span>
        <span class="text-xs text-slate-400 break-words">{topic_tags}</span>
      </div>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <a href="{url}" target="_blank" class="hidden sm:inline-flex items-center justify-center rounded-md bg-blue-600 hover:bg-blue-500 px-3 py-2 text-xs font-medium text-white">LeetCode →</a>
      <button onclick="toggleDark()" aria-label="Toggle dark" class="inline-flex items-center justify-center rounded-md border border-slate-700 bg-slate-800 px-2.5 py-2 text-xs">🌙</button>
    </div>
  </div>
</header>
<main class="max-w-2xl mx-auto px-4 sm:px-6 py-6 space-y-4">
  <!-- Progress: real scroll -->
  <div class="h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden"><div id="progress" class="h-full bg-blue-600 w-0 transition-all duration-150"></div></div>

  <div class="rounded-xl border bg-white dark:bg-slate-900 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-sm">Problem</h2>
      <details>
        <summary class="text-xs font-medium cursor-pointer text-blue-600 dark:text-blue-400 list-none">Show full problem ↕</summary>
        <div class="text-[14px] leading-6 mt-2 break-words [overflow-wrap:anywhere] prose prose-sm dark:prose-invert max-w-none [&_img]:max-w-full [&_img]:h-auto [&_pre]:whitespace-pre-wrap [&_pre]:break-words">{problem_html}</div>
      </details>
      <a href="{url}" target="_blank" class="inline-flex mt-3 text-xs font-medium text-blue-600 dark:text-blue-400">View on LeetCode →</a>
    </div>
  </div>

  <div class="rounded-xl border bg-amber-50 dark:bg-amber-950/30 dark:border-amber-900 shadow-sm overflow-hidden">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-amber-900 dark:text-amber-200 text-sm">TL;DR — 30s scan</h2>
      <div class="text-sm text-amber-900 dark:text-amber-100 mt-2 break-words">{summary_html}</div>
    </div>
  </div>

  <!-- Visual: LLM-generated Tailwind fragment -->
  <div class="rounded-xl border bg-slate-900 text-slate-100 shadow-sm overflow-hidden">
    <div class="p-4">
      <div class="text-[10px] tracking-widest uppercase opacity-60">Visual — {pattern}</div>
      <div class="mt-3 flex items-center justify-center overflow-hidden min-h-[3rem]">{visual_html}</div>
    </div>
  </div>

  <div class="rounded-xl border bg-white dark:bg-slate-900 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800">
      <button id="tab-naive" onclick="showTab('naive')" class="flex-1 rounded-md px-3 py-2 text-xs font-semibold bg-white dark:bg-slate-700 shadow-sm">💡 Your first idea</button>
      <button id="tab-gold" onclick="showTab('gold')" class="flex-1 rounded-md px-3 py-2 text-xs font-semibold opacity-60">⭐ Better pattern</button>
    </div>
    <div id="panel-naive" class="tab-panel p-4 sm:p-5">
      <div class="text-sm leading-6 break-words [overflow-wrap:anywhere]">{naive}</div>
    </div>
    <div id="panel-gold" class="tab-panel p-4 sm:p-5 hidden">
      <div class="text-sm leading-6 break-words [overflow-wrap:anywhere]">{gold}</div>
    </div>
  </div>

  <div class="rounded-xl border bg-blue-50 dark:bg-blue-950/30 dark:border-blue-900 shadow-sm">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-blue-900 dark:text-blue-200 text-sm">✅ Quick check</h2>
      <div class="mt-3 space-y-3 text-sm break-words">{quiz_html}</div>
    </div>
  </div>

  <div class="rounded-xl border bg-white dark:bg-slate-900 dark:border-slate-800 shadow-sm">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-sm">Checklist</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-2 break-words">{checklist}</p>
      <a href="{url}" class="inline-flex items-center justify-center rounded-md bg-slate-900 dark:bg-white dark:text-slate-900 text-white px-4 py-2 text-sm font-medium mt-4">Practice on LeetCode →</a>
    </div>
  </div>

  <div id="artifacts" class="opacity-20 hover:opacity-60 transition">
    <details class="rounded border border-dashed bg-slate-50 dark:bg-slate-900/50">
      <summary class="text-[10px] tracking-widest uppercase cursor-pointer px-3 py-2 opacity-50">artifacts · scrape</summary>
      <div class="p-3 space-y-2">
        <div class="text-[10px] opacity-60">Deterministic ids: #artifact-naive, #artifact-gold, #artifact-align</div>
        <script type="application/json" id="artifact-naive">{naive_json}</script>
        <script type="application/json" id="artifact-gold">{gold_json}</script>
        <script type="application/json" id="artifact-align">{align_json}</script>
      </div>
    </details>
  </div>
</main>
<footer class="max-w-2xl mx-auto px-4 sm:px-6 py-6 text-xs text-slate-400 text-center break-words">zacharylyh.github.io/5-min-leetcode/{slug}/ · 8am SGT</footer>
<script>
(function(){{const t=localStorage.getItem('theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.classList.add('dark')}})();
function toggleDark(){{document.documentElement.classList.toggle('dark');localStorage.setItem('theme',document.documentElement.classList.contains('dark')?'dark':'light')}}
function copyCode(id){{const el=document.getElementById(id);navigator.clipboard.writeText(el.innerText);const b=document.getElementById(id+'-btn');b.innerText='Copied!';setTimeout(()=>b.innerText='Copy',1500)}}
function toggleAnswer(id){{document.getElementById(id).classList.toggle('hidden')}}
function showTab(which){{document.querySelectorAll('.tab-panel').forEach(e=>e.classList.add('hidden'));document.getElementById('panel-'+which).classList.remove('hidden');document.getElementById('tab-naive').classList.toggle('bg-white',which==='naive');document.getElementById('tab-naive').classList.toggle('dark:bg-slate-700',which==='naive');document.getElementById('tab-naive').classList.toggle('opacity-60',which!=='naive');document.getElementById('tab-gold').classList.toggle('bg-white',which==='gold');document.getElementById('tab-gold').classList.toggle('dark:bg-slate-700',which==='gold');document.getElementById('tab-gold').classList.toggle('opacity-60',which!=='gold');}}
(function(){{const b=document.getElementById('progress');if(!b)return;function upd(){{const h=document.documentElement;const p=(h.scrollTop/(h.scrollHeight-h.clientHeight))*100;b.style.width=p+'%'}}window.addEventListener('scroll',upd,{{passive:true}});upd()}})();
</script>
</body></html>
"""

def _norm_code(code: str) -> str:
    # fix LLM bug where "/n" appears instead of "\n" (slash-n vs backslash-n)
    if "/n" in code and "\n" not in code:
        code = code.replace("/n", "\n")
    # also handle escaped "\\n" literal
    if "\\n" in code and "\n" not in code:
        code = code.replace("\\n", "\n")
    return code

def _prettify_code(code: str) -> str:
    """Turn minified ';'-joined code into readable multi-line form."""
    code = _norm_code(code)
    if not code.strip():
        return code
    # If no newlines but semicolons present, split on ';' and handle 'def foo():bar' inline bodies
    if "\n" not in code and ";" in code:
        parts = [p.strip() for p in code.split(";") if p.strip()]
        out_lines: list[str] = []
        indent = 0
        for p in parts:
            # If part contains ':', but code after ':' (e.g. 'def f():x=1' or 'for i in range(n):s=str(i)')
            # split into header and body so indent is correct — only for def/for/while/with/class
            if ":" in p and not p.rstrip().endswith(":"):
                colon_idx = p.find(":")
                header = p[: colon_idx + 1].strip()
                tail = p[colon_idx + 1 :].strip()
                low_h = header.lstrip()
                # only split for block headers that should be multiline; keep 'if cond: continue' inline
                if low_h.startswith(("def ", "for ", "while ", "with ", "class ")):
                    if low_h.startswith(("else", "elif ", "except", "finally")) and indent > 0:
                        indent -= 1
                    out_lines.append("    " * indent + header)
                    indent += 1
                    if tail:
                        low_t = tail.lstrip()
                        if low_t.startswith(("else", "elif ", "except", "finally")) and indent > 0:
                            indent -= 1
                        out_lines.append("    " * indent + tail)
                        if tail.rstrip().endswith(":"):
                            indent += 1
                    continue
                # for if/elif inline single statement, keep as one line
                # fall through to normal handling
            low = p.lstrip()
            if low.startswith(("else", "elif ", "except", "finally")) and indent > 0:
                indent -= 1
            out_lines.append("    " * indent + p)
            if p.rstrip().endswith(":"):
                indent += 1
        code = "\n".join(out_lines)
    try:
        tree = _ast.parse(code)
        pretty = _ast.unparse(tree)  # type: ignore
        if "\n" in code and "\n" not in pretty:
            return code
        return pretty
    except Exception:
        return code

_VISUAL_BLOCKED_RE = _re.compile(r"<(script|iframe|object)\b|javascript:|on\w+\s*=", _re.IGNORECASE)


def _sanitize_visual(html: str) -> str:
    """Allow only safe Tailwind fragments."""
    if not html or not html.strip():
        return ""
    html = html.strip()[:2000]
    if _VISUAL_BLOCKED_RE.search(html):
        return ""
    low = html.lower()
    if not any(t in low for t in ("<div", "<span", "<svg", "<p")):
        return ""
    return html

def _dump(obj: dict) -> str:
    raw = _json.dumps(obj, ensure_ascii=False)
    return raw.replace("</", "<\\/")


def _extract_code(starter_code) -> tuple[str, str]:
    """Normalize naive(str) / gold(dict) starter_code to (code, lang)."""
    if isinstance(starter_code, dict):
        return str(starter_code.get("code") or ""), str(starter_code.get("language") or "python")
    if isinstance(starter_code, str):
        return starter_code, "python"
    return "", "python"


def _code_block(code: str, lang: str = "python", block_id: str = "code") -> str:
    code = _prettify_code(code)
    if not code.strip():
        return ""
    esc = html_lib.escape(code)
    return f'<div class="relative mt-3"><button id="{block_id}-btn" onclick="copyCode(\'{block_id}\')" class="absolute right-2 top-2 inline-flex items-center justify-center rounded-md bg-slate-800 text-white px-2 py-1 text-xs font-medium">Copy</button><pre id="{block_id}" class="bg-slate-950 text-slate-50 p-4 rounded-lg overflow-auto text-xs whitespace-pre-wrap break-words [overflow-wrap:anywhere]"><code class="language-{html_lib.escape(lang)}">{esc}</code></pre></div>'

def build_full_page(problem: dict, naive: dict, gold: dict, align: dict, visual: dict | None = None) -> str:
    title = html_lib.escape(_clean(str(problem.get("title") or "")))
    diff = str(problem.get("difficulty") or "")
    diff_bg = {"easy":"bg-green-600","medium":"bg-amber-600","hard":"bg-red-600"}.get(diff.lower(),"bg-slate-600")
    topic_tags = html_lib.escape(", ".join(str(t) for t in (problem.get("topicTags") or [])))
    url = html_lib.escape(str(problem.get("url") or "#"))
    raw_html = problem.get("content") or ""
    if len(raw_html) > 9000:
        cut = raw_html[:9000]
        last = cut.rfind("</")
        problem_html = cut[: cut.rfind(">", last) + 1] if last != -1 else cut
    else:
        problem_html = raw_html
    slug = html_lib.escape(str(problem.get("titleSlug") or "lesson"))

    contrast = align.get("contrast") or []
    trigger = _clean(str(align.get("trigger") or ""))
    summary_html = ""
    if contrast:
        summary_html += "<ul class='list-disc pl-5 space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in contrast) + "</ul>"
    if trigger:
        summary_html += f"<div class='mt-3 text-xs'><span class='font-semibold'>Spot next time:</span> {html_lib.escape(trigger)}</div>"

    n_code = ""
    code, lang = _extract_code(naive.get("starter_code"))
    if code.strip():
        n_code = _code_block(code, lang, "naive-code")

    n_parts = []
    n_parts.append(f"<div class='font-medium'>{html_lib.escape(_clean(str(naive.get('pattern',''))))} <span class='opacity-60'>— {html_lib.escape(_clean(str(naive.get('why_obvious',''))))}</span></div>")
    stalls = naive.get("why_stalls") or []
    if stalls:
        n_parts.append("<ul class='list-disc pl-5 mt-2 text-xs opacity-80'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in stalls) + "</ul>")
    n_parts.append(f"<div class='mt-2 text-xs'><span class='font-semibold'>Complexity:</span> {html_lib.escape(_clean(str(naive.get('complexity',''))))}</div>")
    if n_code:
        n_parts.append(n_code)
    takeaway = _clean(str(naive.get('takeaway','')))
    if takeaway:
        n_parts.append(f"<details class='mt-2'><summary class='text-xs font-medium cursor-pointer opacity-70'>Takeaway</summary><div class='text-xs mt-1 italic'>{html_lib.escape(takeaway)}</div></details>")
    naive_html = "<div class='space-y-2'>" + "".join(n_parts) + "</div>"

    # gold - with concept for beginners
    g_parts = []
    g_parts.append(f"<div class='font-medium'>{html_lib.escape(_clean(str(gold.get('pattern',''))))}</div>")
    concept = _clean(str(gold.get("concept") or ""))
    if concept:
        g_parts.append(f"<div class='mt-2 text-xs leading-5 bg-slate-50 dark:bg-slate-800 p-3 rounded-lg border dark:border-slate-700'>{html_lib.escape(concept)}</div>")
    props = gold.get("properties") or []
    if props:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Why it fits ({len(props)}) — properties</summary><ul class='list-disc pl-5 mt-1 text-xs'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in props) + "</ul></details>")
    triggers = gold.get("triggers") or []
    if triggers:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Spot it ({len(triggers)})</summary><ul class='list-disc pl-5 mt-1 text-xs'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in triggers) + "</ul></details>")
    fps = gold.get("first_principles") or []
    if fps:
        g_parts.append(f"<details open><summary class='text-xs font-semibold cursor-pointer mt-2'>How you'd derive it (first principles)</summary><ol class='list-decimal pl-5 mt-1 text-xs space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in fps) + "</ol></details>")
    plan = gold.get("plan") or []
    if plan:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Plan ({len(plan)} steps)</summary><ol class='list-decimal pl-5 mt-1 text-xs space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in plan) + "</ol></details>")
    starts = gold.get("how_to_start") or []
    if starts:
        g_parts.append("<div class='mt-2 text-xs'><span class='font-semibold'>Start when stuck:</span> " + html_lib.escape(_clean(" · ".join(str(x) for x in starts))) + "</div>")
    code_g, lang_g = _extract_code(gold.get("starter_code"))
    g_code = _code_block(code_g, lang_g, "gold-code") if code_g.strip() else ""
    if g_code:
        g_parts.append(g_code)
    g_parts.append(f"<div class='mt-2 text-xs'><span class='font-semibold'>Complexity:</span> {html_lib.escape(_clean(str(gold.get('complexity',''))))}</div>")
    gold_html = "<div class='space-y-2'>" + "".join(g_parts) + "</div>"

    quiz = align.get("quiz") or []
    quiz_html = ""
    for i, q in enumerate(quiz, 1):
        ques = html_lib.escape(_clean(str(q.get("question",""))))
        ans = html_lib.escape(_clean(str(q.get("answer",""))))
        hint = html_lib.escape(_clean(str(q.get("hint","")))) if q.get("hint") else ""
        quiz_html += f"<div class='rounded-lg border bg-white dark:bg-slate-800 dark:border-slate-700 p-3'><div class='font-medium text-xs'>Q{i}: {ques}</div>"
        if hint:
            quiz_html += f"<div class='text-xs opacity-60 mt-1'>Hint: {hint}</div>"
        quiz_html += f"<button onclick=\"toggleAnswer('ans-{i}')\" class='mt-2 inline-flex items-center justify-center rounded-md bg-blue-600 text-white px-2 py-1 text-xs font-medium'>Reveal answer</button><div id='ans-{i}' class='hidden mt-2 bg-slate-50 dark:bg-slate-900 border dark:border-slate-700 rounded p-2 text-xs break-words'>{ans}</div></div>"

    checklist = html_lib.escape(_clean(str(gold.get("checklist",""))))
    pattern = html_lib.escape(_clean(str(gold.get("pattern") or "Pattern")))

    # visual html - sanitized raw injection (no escaping)
    raw_visual = ""
    if visual and isinstance(visual, dict):
        raw_visual = str(visual.get("html") or "")
    visual_html = _sanitize_visual(raw_visual)
    if not visual_html:
        # fallback: simple pattern badge when LLM fails/empty
        visual_html = f'<div class="text-xs opacity-60 font-mono">{pattern}</div>'

    naive_json = _dump(naive)
    gold_json = _dump(gold)
    align_json = _dump(align)

    return TEMPLATE.format(
        title=title, difficulty=html_lib.escape(_clean(diff)), difficulty_bg=diff_bg,
        topic_tags=topic_tags, url=url, problem_html=problem_html,
        summary_html=summary_html, naive=naive_html, gold=gold_html,
        quiz_html=quiz_html, checklist=checklist, slug=slug, pattern=pattern,
        visual_html=visual_html,
        naive_json=naive_json, gold_json=gold_json, align_json=align_json,
    )
