#!/usr/bin/env python3
"""Build Arizona HOA guide HTML pages from content/*.md. Commit both this script and its output."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
LAST_REVIEWED = "November 3, 2026"
LASTMOD = "2026-11-03"
SITE = "https://resolvemyhoa.com"
APP = "https://app.resolvemyhoa.com"

PAGES = {
    "respond-to-hoa-violation-letter-arizona": {
        "title": "How to Respond to an HOA Violation Letter in Arizona",
        "meta": "Got an Arizona HOA violation letter? Learn the 21-day certified-mail reply under A.R.S. 33-1803 and what your HOA must tell you back.",
        "keyword": "how to respond to HOA violation letter Arizona",
        "nav_title": "How to Respond to an HOA Violation Letter in Arizona",
    },
    "arizona-adre-hoa-dispute-petition": {
        "title": "How to File an HOA Dispute Petition with Arizona ADRE",
        "meta": "Arizona homeowners can petition the Department of Real Estate for an HOA hearing. Who qualifies and how it works under 32-2199.01.",
        "keyword": "file HOA complaint Arizona Department of Real Estate",
        "nav_title": "How to File an HOA Dispute Petition with Arizona ADRE",
    },
    "arizona-hoa-board-meetings-open-recording": {
        "title": "Arizona HOA Board Meetings: Your Right to Attend & Record",
        "meta": "Arizona HOA board meetings are open to members, who may speak and record. What A.R.S. 33-1804 says about notice and closed sessions.",
        "keyword": "Arizona HOA open meeting law",
        "nav_title": "Arizona HOA Board Meetings: Your Right to Attend & Record",
    },
    "arizona-hoa-fines-late-fees-limits": {
        "title": "Arizona HOA Fines & Late Fees: What the Law Limits",
        "meta": "What Arizona law says about HOA fines, late fees, and dues increases under A.R.S. 33-1803, in plain English.",
        "keyword": "Arizona HOA fines limits",
        "nav_title": "Arizona HOA Fines & Late Fees: What the Law Limits",
    },
    "arizona-hoa-flags-political-signs": {
        "title": "Arizona HOA Rules on Flags & Political Signs",
        "meta": "Which flags and political signs an Arizona HOA can't ban, and what limits it may set, under A.R.S. 33-1808.",
        "keyword": "Arizona HOA political signs rules",
        "nav_title": "Arizona HOA Rules on Flags & Political Signs",
    },
    "arizona-hoa-lien-foreclosure": {
        "title": "Can an Arizona HOA Foreclose? Liens Explained",
        "meta": "When an Arizona HOA can foreclose on an assessment lien: the 18-month or $10,000 threshold under A.R.S. 33-1807.",
        "keyword": "can an HOA foreclose on my house in Arizona",
        "nav_title": "Can an Arizona HOA Foreclose? Liens Explained",
    },
    "arizona-hoa-solar-panels-law": {
        "title": "Can an Arizona HOA Ban Solar Panels? (A.R.S. 33-1816)",
        "meta": "Arizona HOAs can't prohibit solar energy devices, only adopt reasonable placement rules. What A.R.S. 33-1816 says.",
        "keyword": "can my HOA stop solar panels Arizona",
        "nav_title": "Can an Arizona HOA Ban Solar Panels? (A.R.S. 33-1816)",
    },
    "request-hoa-records-arizona": {
        "title": "How to Request HOA Records in Arizona (A.R.S. 33-1805)",
        "meta": "Arizona homeowners can review HOA records free, with a 10-business-day deadline. Here's how to ask under A.R.S. 33-1805.",
        "keyword": "how to request HOA records in Arizona",
        "nav_title": "How to Request HOA Records in Arizona (A.R.S. 33-1805)",
    },
    "arizona-hoa-faq": {
        "title": "Arizona HOA FAQ: Fines, the Board & the Management Company",
        "meta": "Answers on Arizona HOA fines, who really decides them, and how the board and the management company differ in role, pay, and incentives.",
        "keyword": "Arizona HOA fines FAQ",
        "nav_title": "Arizona HOA FAQ: Fines, the Board & the Management Company",
        "reviewed": "November 8, 2026",
        "lastmod": "2026-11-08",
    },
}

FAQ_PAGE = "arizona-hoa-faq"

HUB = "respond-to-hoa-violation-letter-arizona"

# Related guides shown below the article (layout only; body text stays verbatim).
# Hub lists all others; others always include the hub, plus brief-map extras.
RELATED = {
    HUB: [
        "arizona-adre-hoa-dispute-petition",
        "arizona-hoa-board-meetings-open-recording",
        "arizona-hoa-fines-late-fees-limits",
        "arizona-hoa-flags-political-signs",
        "arizona-hoa-lien-foreclosure",
        "arizona-hoa-solar-panels-law",
        "request-hoa-records-arizona",
        FAQ_PAGE,
    ],
    "arizona-adre-hoa-dispute-petition": [HUB, "request-hoa-records-arizona"],
    "arizona-hoa-board-meetings-open-recording": [HUB, "request-hoa-records-arizona"],
    "arizona-hoa-fines-late-fees-limits": [HUB, "request-hoa-records-arizona", "arizona-adre-hoa-dispute-petition", FAQ_PAGE],
    "arizona-hoa-flags-political-signs": [HUB, "request-hoa-records-arizona"],
    "arizona-hoa-lien-foreclosure": [HUB, "arizona-hoa-fines-late-fees-limits"],
    "arizona-hoa-solar-panels-law": [HUB, "request-hoa-records-arizona"],
    "request-hoa-records-arizona": [
        HUB,
        "arizona-hoa-board-meetings-open-recording",
        "arizona-adre-hoa-dispute-petition",
    ],
    FAQ_PAGE: [
        HUB,
        "arizona-hoa-fines-late-fees-limits",
        "request-hoa-records-arizona",
        "arizona-hoa-board-meetings-open-recording",
        "arizona-adre-hoa-dispute-petition",
    ],
}

# In-body phrase wrapping (exact existing phrases only). Applied after HTML conversion.
INLINE_LINKS = {
    HUB: [
        (
            "See our guide to the ADRE HOA petition.",
            f'<a href="/arizona-adre-hoa-dispute-petition/">See our guide to the ADRE HOA petition.</a>',
        ),
    ],
    "arizona-adre-hoa-dispute-petition": [
        (
            "a 33-1803 reply or a records request",
            f'<a href="/{HUB}/">a 33-1803 reply</a> or a <a href="/request-hoa-records-arizona/">records request</a>',
        ),
    ],
    "arizona-hoa-board-meetings-open-recording": [
        (
            "request the minutes afterward (A.R.S. 33-1805)",
            '<a href="/request-hoa-records-arizona/">request the minutes afterward (A.R.S. 33-1805)</a>',
        ),
        (
            "Request the minutes",
            '<a href="/request-hoa-records-arizona/">Request the minutes</a>',
        ),
        (
            "an ADRE petition",
            '<a href="/arizona-adre-hoa-dispute-petition/">an ADRE petition</a>',
        ),
    ],
    "arizona-hoa-fines-late-fees-limits": [
        (
            "see our violation-letter guide",
            f'<a href="/{HUB}/">see our violation-letter guide</a>',
        ),
        (
            "Request records showing how the fine was decided (A.R.S. 33-1805)",
            '<a href="/request-hoa-records-arizona/">Request records showing how the fine was decided (A.R.S. 33-1805)</a>',
        ),
        (
            "consider an ADRE petition (A.R.S. 32-2199.01)",
            '<a href="/arizona-adre-hoa-dispute-petition/">consider an ADRE petition (A.R.S. 32-2199.01)</a>',
        ),
    ],
    "arizona-hoa-flags-political-signs": [
        (
            "Respond in writing within 21 days (A.R.S. 33-1803(C))",
            f'<a href="/{HUB}/">Respond in writing within 21 days (A.R.S. 33-1803(C))</a>',
        ),
    ],
    "arizona-hoa-lien-foreclosure": [
        (
            "late charges follow A.R.S. 33-1803(A)",
            '<a href="/arizona-hoa-fines-late-fees-limits/">late charges follow A.R.S. 33-1803(A)</a>',
        ),
    ],
    "arizona-hoa-solar-panels-law": [
        (
            "Request the architectural committee's records on your application (A.R.S. 33-1805)",
            '<a href="/request-hoa-records-arizona/">Request the architectural committee\'s records on your application (A.R.S. 33-1805)</a>',
        ),
    ],
    "request-hoa-records-arizona": [
        (
            "closed under 33-1804",
            '<a href="/arizona-hoa-board-meetings-open-recording/">closed under 33-1804</a>',
        ),
        (
            "an ADRE petition (A.R.S. 32-2199.01)",
            '<a href="/arizona-adre-hoa-dispute-petition/">an ADRE petition (A.R.S. 32-2199.01)</a>',
        ),
    ],
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"')
    return meta, body


def anchor(label_html: str, url: str) -> str:
    """Render a link. Marketing-site links land on the analyzer card."""
    if url.rstrip("/") in (SITE, SITE + "/") or url == "https://resolvemyhoa.com":
        url = "/#join"
    cls = ' class="btn"' if url.rstrip("/") == APP else ""
    return f'<a{cls} href="{html.escape(url, quote=True)}">{label_html}</a>'


def inline_md(text: str) -> str:
    """Convert inline markdown; preserve literal text."""
    # Bold-wrapped links: **[label](url)**
    text = re.sub(
        r"\*\*\[([^\]]+)\]\(([^)]+)\)\*\*",
        lambda m: f"\x00STRONG_A\x00{m.group(1)}\x00URL\x00{m.group(2)}\x00STRONG_B\x00",
        text,
    )
    parts: list[str] = []
    last = 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        parts.append(escape_with_bold(text[last : m.start()]))
        parts.append(anchor(escape_with_bold(m.group(1)), m.group(2)))
        last = m.end()
    parts.append(escape_with_bold(text[last:]))
    out = "".join(parts)

    def restore_strong_link(m: re.Match) -> str:
        html_a = anchor(html.escape(m.group(1)), m.group(2))
        if ' class="btn"' in html_a:
            return html_a
        return f"<strong>{html_a}</strong>"

    out = re.sub(
        r"\x00STRONG_A\x00(.*?)\x00URL\x00(.*?)\x00STRONG_B\x00",
        restore_strong_link,
        out,
    )
    return out


def escape_with_bold(text: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("**", i):
            end = text.find("**", i + 2)
            if end != -1:
                out.append("<strong>")
                out.append(html.escape(text[i + 2 : end]))
                out.append("</strong>")
                i = end + 2
                continue
        out.append(html.escape(text[i]))
        i += 1
    return "".join(out)


def md_to_html(body: str) -> tuple[str, str, list[dict]]:
    """Return (article_html, h1_text, faqs)."""
    lines = body.splitlines()
    html_parts: list[str] = []
    faqs: list[dict] = []
    h1 = ""
    i = 0
    in_faq = False
    faq_groups = 0
    in_list: str | None = None  # 'ul' or 'ol'
    in_blockquote = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append(f"</{in_list}>")
            in_list = None

    def close_bq():
        nonlocal in_blockquote
        if in_blockquote:
            html_parts.append("</blockquote>")
            in_blockquote = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "## FAQ" or stripped.startswith("## FAQ: "):
            # "## FAQ" is one section; "## FAQ: Topic" starts a titled group.
            # Every group feeds the same FAQPage JSON-LD.
            close_list()
            close_bq()
            if in_faq:
                html_parts.append("</section>")
            in_faq = True
            faq_groups += 1
            hid = "faq-h" if faq_groups == 1 else f"faq-h{faq_groups}"
            heading = "FAQ" if stripped == "## FAQ" else stripped[len("## FAQ: "):]
            html_parts.append(f'<section class="faq" aria-labelledby="{hid}">')
            html_parts.append(f'<h2 id="{hid}">{html.escape(heading)}</h2>')
            i += 1
            continue

        if stripped.startswith("## Get help") or stripped.startswith("## Use the free"):
            close_list()
            close_bq()
            if in_faq:
                html_parts.append("</section>")
                in_faq = False
            # Product CTA. Wording lives in the markdown; keep it to what is actually offered.
            html_parts.append('<section class="cta-block" aria-labelledby="cta-h">')
            html_parts.append(f'<h2 id="cta-h">{html.escape(stripped[3:])}</h2>')
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("*This is general") or s.startswith("## Sources") or s.startswith("## "):
                    break
                if s:
                    html_parts.append(f"<p>{inline_md(s)}</p>")
                i += 1
            html_parts.append("</section>")
            continue

        if stripped.startswith("*This is general"):
            close_list()
            close_bq()
            # strip surrounding asterisks for italic
            text = stripped.strip("*")
            html_parts.append(f'<p class="page-disc"><em>{html.escape(text)}</em></p>')
            i += 1
            continue

        if stripped == "## Sources":
            close_list()
            close_bq()
            html_parts.append('<section class="sources" aria-labelledby="sources-h">')
            html_parts.append('<h2 id="sources-h">Sources</h2>')
            html_parts.append("<ul>")
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    continue
                if s.startswith("- "):
                    item = s[2:]
                    if ": http" in item:
                        label, url = item.split(": ", 1)
                        html_parts.append(
                            f'<li>{html.escape(label)}: <a href="{html.escape(url, quote=True)}" rel="noopener" target="_blank">{html.escape(url)}</a></li>'
                        )
                    else:
                        html_parts.append(f"<li>{inline_md(item)}</li>")
                    i += 1
                    continue
                break
            html_parts.append("</ul></section>")
            continue

        if stripped.startswith("# "):
            close_list()
            close_bq()
            h1 = stripped[2:]
            html_parts.append(f"<h1>{html.escape(h1)}</h1>")
            i += 1
            continue

        if stripped.startswith("## "):
            close_list()
            close_bq()
            if in_faq:
                in_faq = False
                html_parts.append("</section>")
            html_parts.append(f"<h2>{html.escape(stripped[3:])}</h2>")
            i += 1
            continue

        if in_faq and stripped.startswith("**") and stripped.endswith("**"):
            close_list()
            q = stripped.strip("*")
            i += 1
            # skip blank
            while i < len(lines) and not lines[i].strip():
                i += 1
            a = lines[i].strip() if i < len(lines) else ""
            if a:
                faqs.append({"q": q, "a": a})
                html_parts.append("<div class=\"faq-item\">")
                html_parts.append(f"<h3>{html.escape(q)}</h3>")
                html_parts.append(f"<p>{inline_md(a)}</p>")
                html_parts.append("</div>")
                i += 1
            continue

        if stripped.startswith("> "):
            close_list()
            if not in_blockquote:
                html_parts.append("<blockquote>")
                in_blockquote = True
            html_parts.append(f"<p>{inline_md(stripped[2:])}</p>")
            i += 1
            # continue consecutive blockquote lines
            while i < len(lines) and lines[i].startswith("> "):
                html_parts.append(f"<p>{inline_md(lines[i][2:])}</p>")
                i += 1
            close_bq()
            continue

        if re.match(r"^\d+\. ", stripped):
            close_bq()
            if in_list != "ol":
                close_list()
                html_parts.append("<ol>")
                in_list = "ol"
            item = re.sub(r"^\d+\. ", "", stripped)
            html_parts.append(f"<li>{inline_md(item)}</li>")
            i += 1
            continue

        if stripped.startswith("- "):
            close_bq()
            if in_list != "ul":
                close_list()
                html_parts.append("<ul>")
                in_list = "ul"
            html_parts.append(f"<li>{inline_md(stripped[2:])}</li>")
            i += 1
            continue

        if not stripped:
            close_list()
            close_bq()
            i += 1
            continue

        close_list()
        close_bq()
        html_parts.append(f"<p>{inline_md(stripped)}</p>")
        i += 1

    close_list()
    close_bq()
    if in_faq:
        html_parts.append("</section>")

    return "\n".join(html_parts), h1, faqs


def apply_inline_links(article: str, slug: str) -> str:
    for old, new in INLINE_LINKS.get(slug, []):
        # Match both raw and html.escape()'d apostrophes/quotes in rendered HTML.
        candidates = [old, html.escape(old), html.escape(old, quote=True)]
        for cand in candidates:
            if cand in article:
                # new may contain apostrophes that also need escaping outside tags;
                # replacements are hand-written HTML already.
                article = article.replace(cand, new, 1)
                break
    return article


def related_html(slug: str) -> str:
    links = RELATED.get(slug, [HUB] if slug != HUB else [])
    items = []
    for s in links:
        title = PAGES[s]["nav_title"]
        items.append(f'<li><a href="/{s}/">{html.escape(title)}</a></li>')
    return (
        '<nav class="related" aria-labelledby="related-h">'
        '<h2 id="related-h">Related Arizona HOA guides</h2>'
        f'<ul>{"".join(items)}</ul>'
        "</nav>"
    )


def plain_text(md: str) -> str:
    """Strip inline markdown links and bold for structured data."""
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    return md.replace("**", "")


def json_ld(slug: str, h1: str, meta_desc: str, faqs: list[dict]) -> str:
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": meta_desc,
        "dateModified": PAGES[slug].get("lastmod", LASTMOD),
        "author": {"@type": "Organization", "name": "Resolve My HOA"},
        "publisher": {
            "@type": "Organization",
            "name": "Resolve My HOA",
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE}/assets/logo.png",
            },
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{SITE}/{slug}",
        },
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": plain_text(f["a"])},
            }
            for f in faqs
        ],
    }
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(article, ensure_ascii=False, indent=2)
        + "\n</script>\n"
        + '<script type="application/ld+json">\n'
        + json.dumps(faq_ld, ensure_ascii=False, indent=2)
        + "\n</script>"
    )


SHARED_CSS = """
:root{--teal:#0F766E;--teal-dark:#0B5A54;--ink:#16323A;--muted:#4D6168;--sand:#FFF7EC;--sand-2:#F6EBDD;--line:#E6D8C6;--card:#FFFFFF;--err:#A3361F}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--ink);background:var(--sand);line-height:1.55;font-size:17px}
a{color:var(--teal)}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
header.top{display:flex;align-items:center;justify-content:space-between;gap:12px 16px;flex-wrap:wrap;padding:18px 0}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700;font-size:19px;letter-spacing:-.01em}
.brand img{width:36px;height:36px}
.tools{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}
nav.site{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
nav.site a{text-decoration:none;color:var(--ink);font-size:15px;font-weight:600;padding:8px 12px;border-radius:999px}
nav.site a:hover{color:var(--teal)}
nav.site a.nav-cta{background:var(--teal);color:#fff;font-weight:700}
nav.site a.nav-cta:hover{background:var(--teal-dark);color:#fff}
.xlink{display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--ink);font-size:15px;padding:8px 12px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.6)}
.xlink:hover{border-color:var(--teal);color:var(--teal)}
.xlink svg{width:15px;height:15px}
a:focus-visible{outline:3px solid rgba(15,118,110,.35);outline-offset:2px}
.btn{display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;line-height:1.2;color:#fff;background:var(--teal);text-decoration:none;border-radius:10px;padding:12px 16px}
.btn:hover{background:var(--teal-dark);color:#fff}
.crumb{font-size:14px;color:var(--muted);margin:8px 0 0}
.crumb a{color:var(--muted);text-decoration:none}
.crumb a:hover{color:var(--teal)}
article.guide{max-width:720px;padding:28px 0 8px}
article.guide h1{font-size:clamp(28px,4vw,40px);line-height:1.15;letter-spacing:-.02em;margin:0 0 12px;color:#123E47}
.meta-row{font-size:14.5px;color:var(--muted);margin:0 0 28px}
article.guide h2{font-size:22px;margin:32px 0 10px;color:#123E47;letter-spacing:-.01em}
article.guide h3{font-size:17px;margin:18px 0 6px}
article.guide p{margin:0 0 14px}
article.guide ul,article.guide ol{margin:0 0 16px;padding-left:1.3em}
article.guide li{margin:0 0 8px}
article.guide blockquote{margin:16px 0;padding:14px 18px;border-left:3px solid var(--teal);background:rgba(255,255,255,.65);border-radius:0 12px 12px 0}
article.guide blockquote p{margin:0 0 8px}
article.guide blockquote p:last-child{margin:0}
.faq{margin:28px 0}
.faq-item{margin:0 0 16px;padding-bottom:12px;border-bottom:1px solid var(--line)}
.faq-item:last-child{border-bottom:0}
.cta-block{margin:28px 0;padding:22px 24px;background:var(--card);border:1px solid var(--line);border-radius:18px}
.cta-block h2{margin-top:0}
.page-disc{font-size:15px;color:var(--muted)}
.sources ul{word-break:break-word}
.related{margin:36px 0 16px;padding-top:24px;border-top:1px solid var(--line)}
.related h2{font-size:20px;margin:0 0 12px}
.related ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.related a{text-decoration:none;font-weight:600}
.related a:hover{text-decoration:underline}
footer{border-top:1px solid var(--line);margin-top:40px;padding:26px 0 40px;font-size:14px;color:var(--muted)}
footer .disc{font-weight:600;color:var(--ink);font-size:15px;margin:0 0 8px}
footer p{margin:0 0 6px}
@media (max-width:860px){body{font-size:16px}article.guide{padding-top:18px}}
@media (max-width:520px){.wrap{padding:0 16px}.cta-block{padding:18px}.cta-block a.btn{display:flex}.xlink span{display:none}.tools{width:100%;justify-content:space-between;align-items:flex-start}nav.site{flex:1;min-width:0;gap:4px}nav.site a{padding:10px}}
"""


def page_html(slug: str, meta: dict, article: str, h1: str, faqs: list[dict]) -> str:
    title = meta.get("title") or PAGES[slug]["title"]
    desc = meta.get("meta_description") or PAGES[slug]["meta"]
    canonical = f"{SITE}/{slug}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | Resolve My HOA</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="Resolve My HOA">
<meta name="theme-color" content="#0F766E">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Resolve My HOA">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@resolvemyhoa">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og.jpg">
{json_ld(slug, h1, desc, faqs)}
<style>
{SHARED_CSS.strip()}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="/" aria-label="Resolve My HOA home"><img src="/assets/logo.png" alt="" width="36" height="36">Resolve My HOA</a>
    <div class="tools">
      <nav class="site" aria-label="Site">
        <a href="/#pricing">Pricing</a>
        <a href="/#guides">Guides</a>
        <a href="/{FAQ_PAGE}/">FAQ</a>
        <a class="nav-cta" href="https://app.resolvemyhoa.com">Open the analyzer</a>
      </nav>
      <a class="xlink" href="https://x.com/resolvemyhoa" rel="me noopener" target="_blank" aria-label="@resolvemyhoa on X"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg><span>@resolvemyhoa</span></a>
    </div>
  </header>

  <p class="crumb"><a href="/">Home</a> &middot; <a href="/#guides">Arizona HOA guides</a></p>

  <article class="guide">
    <p class="meta-row">Last reviewed: {PAGES[slug].get("reviewed", LAST_REVIEWED)}</p>
{article}
{related_html(slug)}
  </article>

  <footer>
    <p class="disc">Not a law firm and not legal advice.</p>
    <p>Resolve My HOA is self-help software from Innovative Objects LLC. We are not a law firm, we don&rsquo;t provide legal advice, and using this site doesn&rsquo;t create an attorney-client relationship. For advice about your situation, talk to a licensed Arizona attorney.</p>
    <p>&copy; 2026 Innovative Objects LLC &middot; <a href="https://x.com/resolvemyhoa" rel="noopener" target="_blank">@resolvemyhoa on X</a></p>
  </footer>
</div>
</body>
</html>
"""


def write_sitemap() -> None:
    urls = [""] + list(PAGES.keys())
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        loc = f"{SITE}/" if u == "" else f"{SITE}/{u}"
        parts.append("  <url>")
        parts.append(f"    <loc>{loc}</loc>")
        lastmod = PAGES[u].get("lastmod", LASTMOD) if u else LASTMOD
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
        parts.append("  </url>")
    parts.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_robots() -> None:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://resolvemyhoa.com/sitemap.xml\n",
        encoding="utf-8",
    )


def fix_faq_section_close(article: str) -> str:
    """Ensure FAQ <section> is closed before CTA."""
    if '<section class="faq"' not in article:
        return article
    # If cta-block appears before a closing section after faq, insert close
    faq_pos = article.find('<section class="faq"')
    cta_pos = article.find('<section class="cta-block"')
    if cta_pos == -1:
        if article.rstrip().endswith("</section>"):
            return article
        return article + "\n</section>"
    between = article[faq_pos:cta_pos]
    if "</section>" not in between:
        return article[:cta_pos] + "</section>\n" + article[cta_pos:]
    return article


def build() -> None:
    for slug in PAGES:
        path = CONTENT / f"{slug}.md"
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        article, h1, faqs = md_to_html(body)
        article = fix_faq_section_close(article)
        article = apply_inline_links(article, slug)
        out_dir = ROOT / slug
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(
            page_html(slug, meta, article, h1, faqs), encoding="utf-8"
        )
        print(f"wrote {slug}/index.html ({len(faqs)} FAQs)")
    write_sitemap()
    write_robots()
    print("wrote sitemap.xml and robots.txt")


if __name__ == "__main__":
    build()
