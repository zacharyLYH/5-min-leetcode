"""JSON Schemas for structured outputs.

OpenRouter: response_format json_schema + provider.require_parameters=true ensures routing to
supporting endpoints (see docs/guides/routing/provider-selection). OpenAI native strict mode
similar; Anthropic/Groq differ — see README.

HTML is also structured: ALIGN_SCHEMA -> templated rendering in emailer.py. Keeps email
safe (inline CSS) while allowing flexible per-question quiz/visual tweaks via data, not raw HTML.
"""

NAIVE_SCHEMA = {
    "name": "naive_lesson",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Name of naive pattern (e.g. brute-force)"},
            "why_obvious": {"type": "string", "description": "Why this feels obvious from statement"},
            "why_stalls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2 bullets: what makes it explode",
            },
            "complexity": {"type": "string", "description": "Time & space, e.g. O(n^2) time, O(1) space"},
            "starter_code": {"type": "string", "description": "5-15 line Python sketch"},
            "takeaway": {"type": "string", "description": "1-line signal to abandon this approach"},
        },
        "required": ["pattern", "why_obvious", "why_stalls", "complexity", "starter_code", "takeaway"],
        "additionalProperties": False,
    },
}

GOLD_SCHEMA = {
    "name": "gold_lesson",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Gold pattern name, most reusable"},
            "concept": {
                "type": "string",
                "description": "Beginner-friendly 2-3 sentence explanation of pattern assuming no experience, conversational tone, what it does in plain English",
            },
            "properties": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Properties of THIS problem that make pattern work (e.g. sorted, monotonic, overlapping subproblems)",
            },
            "triggers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3 tight bullets: wording/constraints that scream this pattern vs distractor",
            },
            "first_principles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2-3 conversational steps as if telling a student how they could have derived insight themselves from scratch, beginner-friendly",
            },
            "how_to_start": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2 concrete first moves when stuck",
            },
            "plan": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 high-level steps, not full code",
            },
            "starter_code": {
                "type": "object",
                "description": "Optional code block; use null if not needed. MUST be valid Python with real newlines, not /n, ast.parse-able",
                "properties": {
                    "language": {"type": "string", "description": "e.g. python"},
                    "code": {"type": "string", "description": "≤12 line skeleton, core loop only, valid Python with newlines"},
                },
                "required": ["language", "code"],
            },
            "complexity": {"type": "string", "description": "e.g. O(n) time, O(1) space"},
            "checklist": {"type": "string", "description": '1-line: next time see X -> try Y'},
        },
        "required": [
            "pattern",
            "concept",
            "properties",
            "triggers",
            "first_principles",
            "how_to_start",
            "plan",
            "starter_code",
            "complexity",
            "checklist",
        ],
        "additionalProperties": False,
    },
}

ALIGN_SCHEMA = {
    "name": "alignment",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "contrast": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2-3 bullets contrasting naive vs gold, when to switch — plain English for beginners, no jargon like prefix/suffix/mono",
            },
            "trigger": {"type": "string", "description": "#1 trigger to spot gold next time — plain words, e.g. 'need pair sum -> think hash'"},
            "quiz": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Insight Q that makes user apply pattern, not define it (e.g. why does monotonicity allow stack?)",
                        },
                        "answer": {"type": "string", "description": "Succinct insight, not textbook def"},
                        "hint": {"type": "string", "description": "Optional nudge"},
                    },
                    "required": ["question", "answer"],
                    "additionalProperties": False,
                },
                "description": "2 insight-prompting Qs",
            },
        },
        "required": ["contrast", "trigger", "quiz"],
        "additionalProperties": False,
    },
}

VIZ_SCHEMA = {
    "name": "visual",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "html": {
                "type": "string",
                "description": "Tailwind HTML fragment (no <html>/<head>/<body>/<script>), ~150-400 chars, visual that teaches the pattern. Use only div/span/svg/p with Tailwind classes. Static, no JS.",
            },
        },
        "required": ["html"],
        "additionalProperties": False,
    },
}
