#!/usr/bin/env python3
"""Build a trimmed copy of the Authority PM blog RSS feed (newest 10 items). Stdlib only."""
import re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

SRC = "https://www.authoritypm.com/feed/rss2"
SELF = "https://pirateblackspot.github.io/apm-blog-feed/feed.xml"
MAX_ITEMS, MAX_BYTES = 10, 400 * 1024
# Only posts published strictly AFTER this moment are included (9:00 AM PT, Oct 11 2026).
CUTOFF = "2026-10-11T16:00:00Z"

req = urllib.request.Request(SRC, headers={"User-Agent": "Mozilla/5.0 (apm-blog-feed)"})
raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
ET.fromstring(raw.encode())  # source must parse

# Work on raw text so namespaces, CDATA and attributes are preserved byte-for-byte.
first = raw.find("<item")
if first < 0: first = raw.rfind("</channel>")
end = raw.rfind("</channel>")
head, tail = raw[:first], raw[end:]
items = re.findall(r"<item\b.*?</item>", raw[first:end], re.S)

def date(it):
    m = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
    try: return parsedate_to_datetime(m.group(1).strip()).timestamp()
    except Exception: return 0
CUTOFF_TS = datetime.fromisoformat(CUTOFF.replace("Z", "+00:00")).timestamp()
items = [i for i in items if date(i) > CUTOFF_TS]
items = sorted(items, key=date, reverse=True)[:MAX_ITEMS]

# Point atom:link rel=self at the Pages URL.
selflink = f'<atom:link href="{SELF}" type="application/rss+xml" rel="self" />'
head, n = re.subn(r'<atom:link\b[^>]*rel="self"[^>]*/>', selflink, head, count=1)
if not n:
    head = head.replace("</description>", "</description>\n    " + selflink, 1)
if "xmlns:atom=" not in head:
    head = head.replace("<rss ", '<rss xmlns:atom="http://www.w3.org/2005/Atom" ', 1)

def build(its): return head.rstrip() + "\n    " + "\n    ".join(its) + "\n  " + tail
out = build(items)
if len(out.encode()) >= MAX_BYTES:
    out = build([re.sub(r"\s*<content:encoded>.*?</content:encoded>", "", i, flags=re.S) for i in items])

root = ET.fromstring(out.encode())
assert len(root.findall("./channel/item")) == len(items)
with open("feed.xml", "w", encoding="utf-8") as f: f.write(out)
print(f"feed.xml: {len(items)} items, {len(out.encode())} bytes")
