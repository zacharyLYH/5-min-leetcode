import html as html_lib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .utils import clean as _clean


_DIFF_COLOR = {"easy": "#16a34a", "medium": "#d97706", "hard": "#dc2626"}


def difficulty_color(d: str) -> str:
    return _DIFF_COLOR.get((d or "").lower(), "#64748b")


EMAIL_TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#f8fafc;font-family:sans-serif">
<div style="max-width:560px;margin:0 auto;padding:24px">
<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
<div style="background:#0f172a;color:white;padding:18px 20px">
<div style="font-size:11px;opacity:0.6;letter-spacing:0.08em">5-MIN LEETCODE</div>
<div style="font-size:18px;font-weight:700;margin-top:4px">{title}</div>
<div style="margin-top:8px"><span style="background:{difficulty_color};color:white;font-size:11px;padding:3px 8px;border-radius:999px">{difficulty}</span> <span style="color:#94a3b8;font-size:11px;margin-left:6px">{topic_tags}</span></div>
</div>
<div style="padding:20px">
<p style="font-size:13px;color:#334155;margin:0 0 12px">{summary}</p>
<div style="margin:12px 0;padding:10px 12px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;font-size:12px;color:#92400e">{trigger_block}</div>
<a href="{hosted_url}" style="display:block;text-align:center;background:#2563eb;color:white;text-decoration:none;padding:12px;border-radius:8px;font-weight:700;font-size:14px;margin-top:14px">Read 5-min lesson →</a>
<div style="text-align:center;margin-top:10px"><a href="{hosted_url}" style="font-size:11px;color:#64748b">{hosted_url}</a> · <a href="{url}" style="font-size:11px;color:#64748b">LeetCode</a></div>
</div></div>
<div style="text-align:center;font-size:11px;color:#94a3b8;margin-top:10px">Daily 8am SGT · zacharylyh.github.io/5-min-leetcode/{slug}/</div>
</div></body></html>"""


def build_email(problem: dict, align: dict, hosted_url: str) -> str:
    title = html_lib.escape(_clean(str(problem.get("title") or "")))
    diff = str(problem.get("difficulty") or "")
    topic_tags = html_lib.escape(", ".join(str(t) for t in (problem.get("topicTags") or [])))
    contrast = align.get("contrast") or []
    summary = " · ".join(_clean(str(x)) for x in contrast[:2]) if contrast else html_lib.escape(_clean(str(align.get("trigger", ""))))
    if not summary:
        summary = "Today's pattern in 5 minutes — open the lesson."
    trigger = _clean(str(align.get("trigger") or ""))
    trigger_block = f"<b>Spot it:</b> {html_lib.escape(trigger)}" if trigger else "Open for TL;DR + 2 insight Qs"
    slug = html_lib.escape(str(problem.get("titleSlug") or ""))
    return EMAIL_TEMPLATE.format(
        title=title,
        difficulty=html_lib.escape(_clean(diff)),
        difficulty_color=difficulty_color(diff),
        topic_tags=topic_tags,
        summary=html_lib.escape(summary),
        trigger_block=trigger_block,
        hosted_url=html_lib.escape(hosted_url),
        url=html_lib.escape(str(problem.get("url") or "#")),
        slug=slug,
    )


def _send_one(settings, to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText("View this email in an HTML-capable client. " + html_body[:200], "plain"))
    msg.attach(MIMEText(html_body, "html"))
    smtp_cls = smtplib.SMTP_SSL if settings.smtp_port == 465 else smtplib.SMTP  # type: ignore
    with smtp_cls(settings.smtp_host, settings.smtp_port) as s:  # type: ignore
        if settings.smtp_port != 465:
            s.ehlo()
            s.starttls()
        s.login(settings.smtp_user, settings.smtp_password)
        s.sendmail(settings.smtp_from, [to], msg.as_string())


def send_batch(settings, subject: str, html_body: str, recipients: list[str]) -> dict[str, str]:
    """Batch send one-by-one so recipients don't see each other."""
    results: dict[str, str] = {}
    for rcpt in recipients:
        try:
            _send_one(settings, rcpt, subject, html_body)
            results[rcpt] = "ok"
        except Exception as e:  # noqa: BLE001
            results[rcpt] = f"error: {e}"
    return results
