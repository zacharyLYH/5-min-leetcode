import html as html_lib
import json as _json

# shadcn + Tailwind, dark-first, mobile-first, KISS. Wordy content chunked via tabs/details, break-words, responsive.
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
  <!-- Problem: keep short, clamp, link out -->
  <div class="rounded-xl border bg-white dark:bg-slate-900 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-sm">Problem</h2>
      <div class="text-[14px] leading-6 mt-2 break-words [overflow-wrap:anywhere] prose prose-sm dark:prose-invert max-w-none [&_img]:max-w-full [&_img]:h-auto [&_pre]:whitespace-pre-wrap [&_pre]:break-words">{problem_html}</div>
      <a href="{url}" target="_blank" class="sm:hidden inline-flex mt-3 text-xs font-medium text-blue-600 dark:text-blue-400">View on LeetCode →</a>
    </div>
  </div>

  <!-- TL;DR: 2 bullets max, high contrast -->
  <div class="rounded-xl border bg-amber-50 dark:bg-amber-950/30 dark:border-amber-900 shadow-sm overflow-hidden">
    <div class="p-4 sm:p-5">
      <h2 class="font-semibold text-amber-900 dark:text-amber-200 text-sm">TL;DR</h2>
      <div class="text-sm text-amber-900 dark:text-amber-100 mt-2 break-words">{summary_html}</div>
    </div>
  </div>

  <!-- Tabs: Naive vs Gold — less wall, pick one -->
  <div class="rounded-xl border bg-white dark:bg-slate-900 dark:border-slate-800 shadow-sm overflow-hidden">
    <div class="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800">
      <button id="tab-naive" onclick="showTab('naive')" class="flex-1 rounded-md px-3 py-2 text-xs font-semibold bg-white dark:bg-slate-700 shadow-sm">💡 Naive Solution</button>
      <button id="tab-gold" onclick="showTab('gold')" class="flex-1 rounded-md px-3 py-2 text-xs font-semibold opacity-60">⭐ Gold Pattern</button>
    </div>
    <div id="panel-naive" class="tab-panel p-4 sm:p-5 hidden">
      <div class="text-sm leading-6 break-words [overflow-wrap:anywhere]">{naive}</div>
    </div>
    <div id="panel-gold" class="tab-panel p-4 sm:p-5">
      <div class="text-sm leading-6 break-words [overflow-wrap:anywhere]">{gold}</div>
    </div>
  </div>

  {code_blocks}

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

  <!-- obscure artifacts for future scraping — deterministic ids, collapsed -->
  <div id="artifacts" class="opacity-20 hover:opacity-60 transition">
    <details class="rounded border border-dashed bg-slate-50 dark:bg-slate-900/50">
      <summary class="text-[10px] tracking-widest uppercase cursor-pointer px-3 py-2 opacity-50">artifacts · scrape</summary>
      <div class="p-3 space-y-2">
        <div class="text-[10px] opacity-60">Deterministic ids: #artifact-naive, #artifact-gold, #artifact-align (also -data divs)</div>
        <script type="application/json" id="artifact-naive">{naive_json}</script>
        <script type="application/json" id="artifact-gold">{gold_json}</script>
        <script type="application/json" id="artifact-align">{align_json}</script>
        <div id="artifact-naive-data" class="hidden">{naive_json_esc}</div>
        <div id="artifact-gold-data" class="hidden">{gold_json_esc}</div>
        <div id="artifact-align-data" class="hidden">{align_json_esc}</div>
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
</script>
</body></html>
"""

def _clean(s: str) -> str:
    return str(s).replace("$","")

def _code_block(code: str, lang: str = "python", block_id: str = "code") -> str:
    if not code.strip():
        return ""
    esc = html_lib.escape(code)
    return f'<div class="relative mt-3"><button id="{block_id}-btn" onclick="copyCode(\'{block_id}\')" class="absolute right-2 top-2 inline-flex items-center justify-center rounded-md bg-slate-800 text-white px-2 py-1 text-xs font-medium">Copy</button><pre id="{block_id}" class="bg-slate-950 text-slate-50 p-4 rounded-lg overflow-auto text-xs whitespace-pre-wrap break-words [overflow-wrap:anywhere]"><code class="language-{html_lib.escape(lang)}">{esc}</code></pre></div>'

def build_full_page(problem: dict, naive: dict, gold: dict, align: dict) -> str:
    title = html_lib.escape(_clean(str(problem.get("title") or "")))
    diff = str(problem.get("difficulty") or "")
    diff_bg = {"easy":"bg-green-600","medium":"bg-amber-600","hard":"bg-red-600"}.get(diff.lower(),"bg-slate-600")
    raw_tags = problem.get("topicTags") or []
    if raw_tags and isinstance(raw_tags[0], dict):
        raw_tags = [t.get("name","") for t in raw_tags]  # type: ignore
    topic_tags = html_lib.escape(", ".join(str(t) for t in raw_tags))
    url = html_lib.escape(str(problem.get("url") or "#"))
    problem_html = (problem.get("content") or "")[:9000]
    slug = html_lib.escape(str(problem.get("titleSlug") or "lesson"))

    contrast = align.get("contrast") or []
    trigger = _clean(str(align.get("trigger") or ""))
    summary_html = ""
    if contrast:
        summary_html += "<ul class='list-disc pl-5 space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in contrast) + "</ul>"
    if trigger:
        summary_html += f"<div class='mt-3 text-xs'><span class='font-semibold'>Spot next time:</span> {html_lib.escape(trigger)}</div>"

    # Naive: keep ultra concise, single card not 2-col wall
    n_parts = []
    n_parts.append(f"<div class='font-medium'>{html_lib.escape(_clean(str(naive.get('pattern',''))))} <span class='opacity-60'>— {html_lib.escape(_clean(str(naive.get('why_obvious',''))))}</span></div>")
    stalls = naive.get("why_stalls") or []
    if stalls:
        n_parts.append("<ul class='list-disc pl-5 mt-2 text-xs opacity-80'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in stalls) + "</ul>")
    n_parts.append(f"<div class='mt-2 text-xs'><span class='font-semibold'>Complexity:</span> {html_lib.escape(_clean(str(naive.get('complexity',''))))}</div>")
    # hide takeaway in collapsible to reduce wordiness
    takeaway = _clean(str(naive.get('takeaway','')))
    if takeaway:
        n_parts.append(f"<details class='mt-2'><summary class='text-xs font-medium cursor-pointer opacity-70'>Takeaway</summary><div class='text-xs mt-1 italic'>{html_lib.escape(takeaway)}</div></details>")
    naive_html = "<div class='space-y-2'>" + "".join(n_parts) + "</div>"

    # Gold: chunk into collapsibles, not wall
    g_parts = []
    g_parts.append(f"<div class='font-medium'>{html_lib.escape(_clean(str(gold.get('pattern',''))))}</div>")
    props = gold.get("properties") or []
    if props:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Why it fits ({len(props)})</summary><ul class='list-disc pl-5 mt-1 text-xs'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in props) + "</ul></details>")
    triggers = gold.get("triggers") or []
    if triggers:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Spot it ({len(triggers)})</summary><ul class='list-disc pl-5 mt-1 text-xs'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in triggers) + "</ul></details>")
    fps = gold.get("first_principles") or []
    if fps:
        g_parts.append(f"<details open><summary class='text-xs font-semibold cursor-pointer mt-2'>From first principles</summary><ol class='list-decimal pl-5 mt-1 text-xs space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in fps) + "</ol></details>")
    plan = gold.get("plan") or []
    if plan:
        g_parts.append(f"<details><summary class='text-xs font-semibold cursor-pointer mt-2'>Plan ({len(plan)} steps)</summary><ol class='list-decimal pl-5 mt-1 text-xs space-y-1'>" + "".join(f"<li>{html_lib.escape(_clean(str(x)))}</li>" for x in plan) + "</ol></details>")
    starts = gold.get("how_to_start") or []
    if starts:
        g_parts.append("<div class='mt-2 text-xs'><span class='font-semibold'>Start:</span> " + html_lib.escape(_clean(" · ".join(str(x) for x in starts))) + "</div>")
    g_parts.append(f"<div class='mt-2 text-xs'><span class='font-semibold'>Complexity:</span> {html_lib.escape(_clean(str(gold.get('complexity',''))))}</div>")
    gold_html = "<div class='space-y-2'>" + "".join(g_parts) + "</div>"

    code_blocks = ""
    sc_g = gold.get("starter_code")
    if isinstance(sc_g, dict) and str(sc_g.get("code") or "").strip():
        code_blocks += _code_block(str(sc_g.get("code")), str(sc_g.get("language") or "python"), "gold-code")
    sc_n = naive.get("starter_code")
    if isinstance(sc_n, str) and sc_n.strip():
        code_blocks += _code_block(sc_n, "python", "naive-code")
    elif isinstance(sc_n, dict) and str(sc_n.get("code") or "").strip():
        code_blocks += _code_block(str(sc_n.get("code")), str(sc_n.get("language") or "python"), "naive-code")

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

    # deterministic artifacts for scraping — raw JSON, escaped for script
    def _dump(obj: dict) -> str:
        raw = _json.dumps(obj, ensure_ascii=False)
        return raw.replace("</", "<\\/")

    naive_json = _dump(naive)
    gold_json = _dump(gold)
    align_json = _dump(align)

    return TEMPLATE.format(
        title=title, difficulty=html_lib.escape(_clean(diff)), difficulty_bg=diff_bg,
        topic_tags=topic_tags, url=url, problem_html=problem_html,
        summary_html=summary_html, naive=naive_html, gold=gold_html,
        code_blocks=code_blocks, quiz_html=quiz_html, checklist=checklist, slug=slug,
        naive_json=naive_json, gold_json=gold_json, align_json=align_json,
        naive_json_esc=html_lib.escape(naive_json), gold_json_esc=html_lib.escape(gold_json), align_json_esc=html_lib.escape(align_json),
    )
