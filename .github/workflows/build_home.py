#!/usr/bin/env python3
"""Build the artwork-led I NASTRI homepage after Quartz finishes."""

from __future__ import annotations

import html
import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"


STYLE = r"""@import url('https://fonts.googleapis.com/css2?family=Gilda+Display&family=IBM+Plex+Mono:wght@300;400&display=swap');
:root {
  --milk: #fdfff5;
  --black: #080808;
  --quiet: rgba(8, 8, 8, .62);
  --rule: rgba(8, 8, 8, .28);
  --hairline: rgba(8, 8, 8, .14);
  --display: "Gilda Display", "Iowan Old Style", "Baskerville", serif;
  --ui: "IBM Plex Mono", "Courier New", monospace;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; background: var(--milk); }
body {
  margin: 0;
  color: var(--black);
  background-color: var(--milk);
  background-image: radial-gradient(rgba(8, 8, 8, .025) .45px, transparent .55px);
  background-size: 4px 4px;
  font: 300 12px/1.72 var(--ui);
  letter-spacing: .012em;
}
a { color: inherit; text-decoration: none; }
a:hover { opacity: .52; }
img { display: block; max-width: 100%; }
.site-header {
  width: min(1180px, calc(100% - 64px));
  margin: 42px auto 68px;
  padding: 22px 0 20px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 44px;
  border-top: 1px solid var(--black);
  border-bottom: 1px solid var(--rule);
}
.identity { display: grid; gap: 8px; }
.wordmark {
  font: 400 clamp(2.35rem, 4.4vw, 3.9rem)/.95 var(--display);
  letter-spacing: .13em;
  white-space: nowrap;
}
.byline {
  color: var(--quiet);
  font: 300 .64rem/1.4 var(--ui);
  letter-spacing: .08em;
}
.site-header nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 9px 28px;
  padding-bottom: 4px;
  font: 300 .7rem/1 var(--ui);
  letter-spacing: .035em;
  text-transform: lowercase;
}
.site-header nav a { padding-bottom: 7px; border-bottom: 1px solid transparent; }
.site-header nav a:hover { opacity: 1; border-color: var(--black); }
.shell {
  width: min(1180px, calc(100% - 64px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 820px) 238px;
  gap: clamp(70px, 8vw, 122px);
  align-items: start;
}
.post {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px;
  grid-template-areas: "art header" "art notes";
  gap: 22px 34px;
  align-items: start;
  padding: 0 0 78px;
  margin: 0 0 78px;
  border-bottom: 1px solid var(--rule);
}
.post[hidden] { display: none; }
.post-header { grid-area: header; padding-top: 4px; }
.post h1 {
  margin: 17px 0 0;
  font: 400 clamp(1.45rem, 2.4vw, 2rem)/1.12 var(--display);
  letter-spacing: .065em;
}
.date {
  margin: 0;
  color: var(--quiet);
  font: 300 .64rem/1.5 var(--ui);
  letter-spacing: .045em;
  text-transform: lowercase;
}
.artwork { grid-area: art; display: block; background: rgba(8, 8, 8, .035); }
.artwork img { width: 100%; max-height: 760px; object-fit: contain; }
.post-notes { grid-area: notes; align-self: end; padding-bottom: 2px; }
.facts, .place { margin: 0 0 12px; font: 300 .68rem/1.7 var(--ui); }
.place { color: var(--quiet); }
.facts::after { content: ""; display: block; width: 16px; margin-top: 14px; border-top: 1px solid var(--black); }
.sold { display: block; margin-top: 9px; font-size: .62rem; letter-spacing: .09em; text-transform: lowercase; }
.details { display: inline-block; margin-top: 28px; padding-bottom: 5px; border-bottom: 1px solid var(--black); font-size: .64rem; }
.sidebar { position: sticky; top: 24px; font-size: .7rem; }
.sidebar section { padding: 0 0 28px; margin: 0 0 28px; border-bottom: 1px solid var(--hairline); }
.sidebar p { margin-top: 0; }
.eyebrow { display: block; margin-bottom: 14px; color: var(--black); font: 400 .62rem/1 var(--ui); letter-spacing: .08em; text-transform: lowercase; }
.search { display: flex; border-bottom: 1px solid var(--black); }
.search input { min-width: 0; width: 100%; padding: 8px 0; border: 0; outline: 0; color: var(--black); background: transparent; font: 300 .67rem var(--ui); }
.search input::placeholder { color: var(--quiet); }
.search button { border: 0; color: var(--black); background: transparent; cursor: pointer; }
.browse-list { padding: 0; margin: 0; list-style: none; }
.browse-list li { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid var(--hairline); }
.browse-list span { color: var(--quiet); }
.years { display: flex; flex-wrap: wrap; gap: 9px 16px; }
.site-footer {
  width: min(1180px, calc(100% - 64px));
  margin: 8px auto 38px;
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--black);
  color: var(--quiet);
  font: 300 .62rem/1.4 var(--ui);
  text-transform: lowercase;
}
@media (max-width: 840px) {
  .site-header { margin-top: 24px; display: grid; }
  .site-header nav { justify-content: flex-start; }
  .shell { grid-template-columns: 1fr; }
  .sidebar { position: static; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px; }
  .sidebar section { margin: 0; }
}
@media (max-width: 620px) {
  .site-header, .shell, .site-footer { width: min(100% - 30px, 1180px); }
  .wordmark { white-space: normal; }
  .byline { max-width: 38ch; }
  .post { grid-template-columns: 1fr; grid-template-areas: "header" "art" "notes"; gap: 18px; }
  .post h1 { margin-top: 8px; }
  .post-notes { padding-top: 3px; }
  .sidebar { grid-template-columns: 1fr; }
}
"""


MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12, "winter": 1, "spring": 4,
    "summer": 7, "autumn": 10, "fall": 10,
}


@dataclass
class Post:
    title: str
    category: str
    date: str
    year: int
    month: int
    image: str
    url: str
    facts: str
    place: str
    sold: bool


def slug_part(value: str) -> str:
    return re.sub(r"\s+", "-", value.strip().lower())


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip().strip('"\'')
    return data, text[end + 4 :].lstrip()


def normalize_notes() -> None:
    """Add dependable Quartz metadata without changing the source vault."""
    for path in CONTENT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"!\[\[assets/", "![[Assets/", text, flags=re.I)
        if text.startswith("---\n") and (end := text.find("\n---", 4)) >= 0:
            lines = text[4:end].splitlines()
            body = text[end + 4 :].lstrip()
        else:
            lines, body = [], text
        keys = {line.split(":", 1)[0].strip().lower() for line in lines if ":" in line}
        heading = re.search(r"^#\s+(.+?)\s*$", body, re.M)
        title = heading.group(1).strip() if heading else path.stem
        if heading:
            body = body[: heading.start()] + body[heading.end() :]
            body = body.lstrip("\n")
        additions = []
        if "title" not in keys:
            additions.append('title: "' + title.replace('"', '\\"') + '"')
        note_type = next((line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("type:")), None)
        if not note_type and path.parent.name.lower() in {"drawings", "paintings"}:
            note_type = path.parent.name.lower().rstrip("s")
            additions.append(f"type: {note_type}")
        if "date" not in keys:
            date_match = re.search(r"\b(" + "|".join(MONTHS) + r")\b\s*,?\s*((?:19|20)\d{2})\b", body, re.I)
            if date_match:
                additions.append(f"date: {date_match.group(2)}-{MONTHS[date_match.group(1).lower()]:02d}-01")
            elif year_match := re.search(r"(?m)^\s*((?:19|20)\d{2})\s*$", body):
                additions.append(f"date: {year_match.group(1)}-01-01")
        if note_type and "tags" not in keys:
            additions.extend(["tags:", f"  - {note_type}"])
        if "sold" in body.lower() and "status" not in keys:
            additions.append("status: sold")
        path.write_text("---\n" + "\n".join([*lines, *additions]) + "\n---\n\n" + body.strip() + "\n", encoding="utf-8")


def parse_post(path: Path) -> Post | None:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)
    category = frontmatter.get("type", path.parent.name.rstrip("s").lower())
    if category not in {"drawing", "painting"}:
        return None
    heading = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    title = frontmatter.get("title") or (heading.group(1) if heading else path.stem)
    image_match = re.search(r"!\[\[([^]|]+)(?:\|[^]]+)?\]\]", body)
    if not image_match:
        return None
    image_name = Path(image_match.group(1)).name
    image = "assets/" + slug_part(image_name)
    clean_lines = []
    for line in body.splitlines():
        value = line.strip()
        if not value or value.startswith("#") or value.startswith("![[") or value == "RDJ":
            continue
        clean_lines.append(value)
    date = next((line for line in clean_lines if re.search(r"\b(?:19|20)\d{2}\b", line)), "Undated")
    year_match = re.search(r"\b((?:19|20)\d{2})\b", date)
    year = int(year_match.group(1)) if year_match else 0
    lower_date = date.lower()
    month = next((number for name, number in MONTHS.items() if name in lower_date), 0)
    place_lines = [line for line in clean_lines if any(word in line.lower() for word in ("museum", "paris", "france", "new york"))]
    place = " · ".join(place_lines)
    fact_lines = [
        line.rstrip(".") for line in clean_lines
        if line != date and line not in place_lines and "sold" not in line.lower()
    ]
    facts = " · ".join(fact_lines)
    sold = "sold" in body.lower()
    folder = path.parent.name.lower()
    url = f"{folder}/{slug_part(path.stem)}"
    return Post(title, category, date, year, month, image, url, facts, place, sold)


def post_html(post: Post, anchor: str) -> str:
    title = html.escape(post.title)
    sold = '<span class="sold">Sold</span>' if post.sold else ""
    place = f'<p class="place">{html.escape(post.place)}</p>' if post.place else ""
    facts = f'<p class="facts">{html.escape(post.facts)}{sold}</p>' if post.facts or sold else ""
    return f"""<article class="post"{anchor} data-search="{html.escape(post.title.lower())}">
  <header class="post-header"><p class="date">{html.escape(post.date)}</p><h1><a href="{html.escape(post.url)}">{title}</a></h1></header>
  <a class="artwork" href="{html.escape(post.url)}" aria-label="View {title}"><img src="{html.escape(post.image)}" alt="{title}" loading="lazy"></a>
  <div class="post-notes">{facts}{place}<a class="details" href="{html.escape(post.url)}">view details&nbsp; ⟶</a></div>
</article>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        normalize_notes()
        print("Prepared I NASTRI content metadata")
        return
    posts = [post for path in CONTENT.rglob("*.md") if (post := parse_post(path))]
    featured = {"Portrait of Carolina": 4, "Satyr and Bather": 3, "Slimness of Comforts": 2, "Forsythia": 1}
    posts.sort(key=lambda p: (featured.get(p.title, 0), p.year, p.month, p.title.lower()), reverse=True)
    counts = {kind: sum(post.category == kind for post in posts) for kind in ("painting", "drawing")}
    years = sorted({post.year for post in posts if post.year}, reverse=True)
    used_anchors: set[str] = set()
    rendered = []
    for post in posts:
        anchor_name = post.category + "s"
        anchor = ""
        if anchor_name not in used_anchors:
            anchor = f' id="{anchor_name}"'
            used_anchors.add(anchor_name)
        rendered.append(post_html(post, anchor))
    year_links = "".join(f'<a href="#" data-year="{year}">{year}</a>' for year in years)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>I NASTRI — Richmond Jeffrey</title><meta name="description" content="Drawings, paintings, and notes by Richmond Jeffrey.">
<link rel="stylesheet" href="inastri-home.css"></head><body>
<header class="site-header"><a class="identity" href="./" aria-label="I Nastri home"><span class="wordmark">I Nastri</span><span class="byline">painting, drawing, and writing by Richmond Jeffrey</span></a>
<nav aria-label="Primary navigation"><a href="#work">recent work</a><a href="#paintings">paintings</a><a href="#drawings">drawings</a><a href="writing/">writing</a><a href="#archive">archive</a></nav></header>
<main class="shell" id="work"><section class="feed" aria-label="Recent work">{''.join(rendered)}</section>
<aside class="sidebar" id="archive"><section><p class="eyebrow">archive</p><p>I Nastri is an ongoing record of paintings, drawings, and the thoughts surrounding their making. Presence over purpose.</p></section>
<section><label class="eyebrow" for="archive-search">search the archive</label><div class="search"><input id="archive-search" type="search" placeholder="title, medium, place…"><button type="button" aria-label="Search">⟶</button></div></section>
<section><p class="eyebrow">browse</p><ul class="browse-list"><li><a href="paintings/">paintings</a><span>{counts['painting']}</span></li><li><a href="drawings/">drawings</a><span>{counts['drawing']}</span></li><li><a href="writing/">writing</a><span>1</span></li></ul></section>
<section><p class="eyebrow">years</p><div class="years">{year_links}</div></section><section><p class="eyebrow">follow</p><a href="index.xml">rss feed</a></section></aside></main>
<footer class="site-footer"><span>© 2026 Richmond Jeffrey</span><a href="writing/">writing</a></footer>
<script>const q=document.querySelector('#archive-search');const posts=[...document.querySelectorAll('.post')];q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();posts.forEach(p=>p.hidden=v&&!p.textContent.toLowerCase().includes(v));}});document.querySelectorAll('[data-year]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();q.value=a.dataset.year;q.dispatchEvent(new Event('input'));}}));</script>
</body></html>"""
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "index.html").write_text(page, encoding="utf-8")
    (PUBLIC / "inastri-home.css").write_text(STYLE, encoding="utf-8")
    print(f"Built I NASTRI homepage with {len(posts)} artwork posts")


if __name__ == "__main__":
    main()
