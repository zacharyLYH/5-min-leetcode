import requests

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "5-min-leetcode/0.1",
}

RANDOM_QUERY = """
query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) {
  randomQuestion(categorySlug: $categorySlug, filters: $filters) {
    title
    titleSlug
    difficulty
  }
}
"""

DETAIL_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    title
    titleSlug
    difficulty
    content
    isPaidOnly
    topicTags { name slug }
    hints
    exampleTestcases
  }
}
"""

def _post(query: str, variables: dict) -> dict:
    r = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS, timeout=15)
    r.raise_for_status()
    j = r.json()
    if "errors" in j:
        raise RuntimeError(f"LeetCode GraphQL errors: {j['errors']}")
    return j["data"]

def fetch_random_problem(max_tries: int = 10) -> dict:
    """Returns dict with title, titleSlug, difficulty, content, topicTags, url.
    Skips premium (isPaidOnly) / empty content problems.
    """
    last_err: Exception | None = None
    for attempt in range(1, max_tries + 1):
        try:
            data = _post(RANDOM_QUERY, {"categorySlug": "algorithms", "filters": {}})
            rq = data.get("randomQuestion")
            if not rq or not rq.get("titleSlug"):
                raise RuntimeError("randomQuestion returned empty")
            slug = rq["titleSlug"]
            detail = _post(DETAIL_QUERY, {"titleSlug": slug})
            q = detail["question"]
            if not q:
                raise RuntimeError(f"question detail empty for {slug}")
            # skip premium / no content (e.g. Shortest Word Distance III)
            if q.get("isPaidOnly"):
                last_err = RuntimeError(f"skipping premium {slug} (isPaidOnly)")
                continue
            if not q.get("content"):
                last_err = RuntimeError(f"skipping {slug} with empty content")
                continue
            q["url"] = f"https://leetcode.com/problems/{q['titleSlug']}/"
            q["topicTags"] = [t["name"] for t in (q.get("topicTags") or [])]
            if attempt > 1:
                print(f"  (skipped {attempt-1} premium/empty, got {q['title']})")
            return q
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
    raise RuntimeError(f"failed to fetch free problem after {max_tries} tries: {last_err}")
