#!/usr/bin/env python3
"""Fail if published pages advertise unavailable products or drop required limits."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = [ROOT / "index.html"] + sorted(ROOT.glob("*/index.html"))
# Moved-page stubs (meta refresh to the new URL) are checked separately below.
REDIRECTS = {"arizona-hoa-faq": "hoa-board-vs-management-company-arizona"}
HTML = [p for p in HTML if p.parent.name not in REDIRECTS]

# Retired or over-broad offers. Match visible copy, not the image bytes.
FORBIDDEN = [
    r"waitlist",
    r"flat[- ]price",
    r"case tracker",
    r"mailing receipts",
    r"occasional tips",
    r"settled calmly",
    r"first in line",
    r"write a clear reply",
    r"on paper, on time",
    r"Case Pass",
]

REQUIRED_HOME = [
    "https://app.resolvemyhoa.com",
    "Open the free analyzer",
    "Create an account",
    "Coming soon",
    "No date is set",
    "nothing to buy",
    "Not offered",
    "Not a law firm and not legal advice.",
    "id=\"join\"",
    "id=\"pricing\"",
    "id=\"updates\"",
    "feature-updates",
]

GUIDE_URLS = [
    "respond-to-hoa-violation-letter-arizona",
    "request-hoa-records-arizona",
    "arizona-hoa-fines-late-fees-limits",
    "arizona-hoa-board-meetings-open-recording",
    "arizona-adre-hoa-dispute-petition",
    "arizona-hoa-lien-foreclosure",
    "arizona-hoa-flags-political-signs",
    "arizona-hoa-solar-panels-law",
    "hoa-board-vs-management-company-arizona",
]


def main() -> int:
    errors: list[str] = []
    if len(HTML) != 11:
        errors.append(f"expected 11 HTML pages, found {len(HTML)}")

    for path in HTML:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for pattern in FORBIDDEN:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(f"{rel} still contains {pattern!r}")
        if "Not a law firm and not legal advice." not in text:
            errors.append(f"{rel} is missing the not-a-law-firm line")
        if "https://app.resolvemyhoa.com" not in text:
            errors.append(f"{rel} is missing the app URL")
        if rel != "index.html":
            if "Open the analyzer" not in text:
                errors.append(f"{rel} is missing the analyzer CTA")
            if rel != "guides/index.html" and "azleg.gov" not in text:
                errors.append(f"{rel} is missing Arizona statute links")
            if 'rel="canonical"' not in text and "canonical" not in text:
                errors.append(f"{rel} is missing a canonical link")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for needle in REQUIRED_HOME:
        if needle not in home:
            errors.append(f"homepage is missing {needle!r}")
    if 'href="/guides/"' not in home:
        errors.append("homepage is missing the link to /guides/")
    hub = (ROOT / "guides" / "index.html").read_text(encoding="utf-8")
    for slug in GUIDE_URLS:
        if f"/{slug}/" not in hub:
            errors.append(f"guides page is missing /{slug}/")

    # The opt-in must stay explicit and unchecked. "checkbox" contains the letters
    # "checked", so look for the attribute rather than that substring.
    consent = re.search(r'<input id="consent"[^>]*>', home)
    if consent is None or re.search(r"(?:^|\s)checked(?:\s|=|>)", consent.group(0)):
        errors.append("feature-update consent must be an unchecked checkbox")

    for old, target in REDIRECTS.items():
        stub = ROOT / old / "index.html"
        text = stub.read_text(encoding="utf-8") if stub.exists() else ""
        if f'url=/{target}/"' not in text or "noindex" not in text:
            errors.append(f"/{old}/ must redirect to /{target}/ with noindex")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"ok: {len(HTML)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
