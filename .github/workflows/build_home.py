#!/usr/bin/env python3
"""Build the artwork-led I NASTRI homepage after Quartz finishes."""

from __future__ import annotations

import html
import argparse
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import date as calendar_date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"


STYLE = r"""@import url('https://fonts.googleapis.com/css2?family=Gilda+Display&family=IBM+Plex+Mono:wght@300;400&family=Source+Sans+3:wght@400;600&display=swap');
:root {
  --milk: #f7f7f7;
  --black: #080808;
  --quiet: #080808;
  --rule: #080808;
  --hairline: #080808;
  --display: "Gilda Display", "Iowan Old Style", "Baskerville", serif;
  --ui: "IBM Plex Mono", "Courier New", monospace;
  --humanist: "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
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
a:hover { opacity: 1; text-decoration: underline; text-underline-offset: 3px; }
img { display: block; max-width: 100%; }
img,
img:hover,
a:hover img {
  opacity: 1 !important;
  filter: none !important;
  transform: none !important;
  mix-blend-mode: normal !important;
  transition: none !important;
}
.site-header {
  width: min(1120px, calc(100% - 128px));
  margin: 42px auto 68px;
  padding: 19px 0 18px;
  display: flex;
  align-items: center;
}
.identity { display: flex; align-items: center; gap: clamp(24px, 4vw, 58px); }
.wordmark {
  font: 700 clamp(2rem, 3.65vw, 3.2rem)/.98 var(--display);
  letter-spacing: .165em;
  white-space: nowrap;
}
.title-mark { display: block; width: clamp(138px, 18vw, 232px); height: auto; flex: 0 0 auto; }
.shell {
  width: min(1120px, calc(100% - 128px));
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 600px) 363px;
  grid-template-areas: "feed sidebar";
  gap: clamp(32px, 4vw, 56px);
  align-items: start;
}
.feed {
  grid-area: feed;
  min-width: 0;
}
.post {
  padding: 0 0 clamp(31px, 3.5vw, 47px);
  margin: 0 0 clamp(36px, 4.5vw, 58px);
  border-bottom: 1px solid var(--rule);
}
.post:nth-child(3n + 2) { padding-bottom: clamp(36px, 4vw, 53px); }
.post:nth-child(4n) { margin-bottom: clamp(41px, 5vw, 62px); }
.post[hidden] { display: none; }
.post-date {
  margin: 0 0 17px;
  color: var(--black);
  font: 300 .69rem/1.4 var(--ui);
  letter-spacing: .045em;
}
.inventory { width: min(100%, 520px); margin: 27px 0 0; }
.post h1 {
  margin: 0 0 13px;
  font: 400 clamp(1.06rem, 1.6vw, 1.38rem)/1.15 var(--display);
  letter-spacing: .075em;
}
.completion-date {
  display: block;
  margin: 0;
  color: var(--black);
  font: 300 .64rem/1.5 var(--ui);
  letter-spacing: .045em;
  text-transform: lowercase;
}
.artwork { display: block; width: 100%; background: transparent; }
.artwork:hover { opacity: 1 !important; text-decoration: none !important; }
.artwork img { width: auto; height: auto; max-width: 100%; max-height: none; margin: 0; object-fit: initial; }
.post.drawing .artwork img { border: 1px solid var(--black); }
.inventory-data { display: grid; justify-items: start; gap: 2px; color: var(--black); font: 300 .69rem/1.65 var(--ui); }
.inventory-data span { display: block; }
.sold { margin-top: 5px; letter-spacing: .09em; text-transform: lowercase; }
.sidebar {
  grid-area: sidebar;
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  padding: 18px 17px 3px;
  color: var(--black);
  border: 1px solid var(--hairline);
  font: 400 .76rem/1.65 var(--humanist);
  line-height: 1.7;
  letter-spacing: .025em;
}
.sidebar section { padding: 0 0 17px; margin: 0 0 18px; border-bottom: 1px solid var(--hairline); }
.sidebar section:last-child { border-bottom: 0; }
.sidebar p { margin-top: 0; }
.archive-copy { font: 400 .78rem/1.65 var(--humanist); }
.archive-copy > p { text-align: left; hyphens: none; }
.archive-copy strong { font-weight: 600; }
.nowrap { white-space: nowrap; }
.archive-copy a { color: var(--black); border-bottom: 1px solid var(--hairline); }
.archive-copy .email-line { display: block; margin-top: 4px; font-family: var(--ui); font-size: .72rem; border-bottom: 0; }
.eyebrow { display: block; margin-bottom: 12px; color: var(--black); font: 400 .88rem/1 var(--display); letter-spacing: .055em; text-transform: none; }
.search { display: flex; border-bottom: 1px solid var(--hairline); }
.search input { min-width: 0; width: 100%; padding: 8px 0; border: 0; outline: 0; color: var(--black); background: transparent; font: 300 .67rem var(--ui); }
.search input::placeholder { color: var(--quiet); }
.search button { border: 0; color: var(--black); background: transparent; cursor: pointer; }
.browse-list { padding: 0; margin: 0; list-style: none; }
.browse-list { counter-reset: track; }
.browse-list li { counter-increment: track; display: grid; grid-template-columns: 22px 1fr auto; padding: 5px 0; border-bottom: 1px solid var(--hairline); }
.browse-list li::before { content: counter(track, decimal-leading-zero); color: var(--quiet); font-family: var(--ui); font-size: .63rem; }
.browse-list span { color: var(--quiet); }
.years { display: flex; flex-wrap: wrap; gap: 8px 14px; font-family: var(--ui); font-size: .67rem; }
.tag-cloud { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 12px; }
.tag-cloud a { font-family: var(--display); font-size: calc(.67rem + (var(--weight) * .09rem)); line-height: 1.35; }
.tag-cloud small { margin-left: 2px; color: var(--quiet); font-size: .52rem; }
.site-footer {
  width: min(1120px, calc(100% - 128px));
  margin: 8px auto 38px;
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--hairline);
  color: var(--quiet);
  font: 300 .62rem/1.4 var(--ui);
  text-transform: lowercase;
}
@media (max-width: 980px) {
  .site-header { margin-top: 24px; }
  .shell { grid-template-columns: 1fr; grid-template-areas: "sidebar" "feed"; }
  .sidebar { position: static; max-height: none; overflow: visible; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 34px; margin-bottom: 68px; }
  .sidebar section { margin-bottom: 25px; }
}
@media (max-width: 620px) {
  .site-header, .shell, .site-footer { width: min(100% - 30px, 1180px); }
  .site-header { margin-bottom: 52px; }
  .wordmark { white-space: normal; }
  .identity { gap: 22px; }
  .title-mark { width: 138px; }
  .inventory { margin-top: 21px; }
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
    completion_date: str
    post_date: str
    post_sort_date: str
    year: int
    month: int
    image: str
    url: str
    facts: str
    place: str
    sold: bool
    tags: tuple[str, ...]
    image_size: str


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


def frontmatter_tags(text: str) -> tuple[str, ...]:
    """Read both YAML list and inline tags without adding a YAML dependency."""
    if not text.startswith("---\n") or (end := text.find("\n---", 4)) < 0:
        return ()
    lines = text[4:end].splitlines()
    tags: list[str] = []
    reading_tags = False
    for line in lines:
        if re.match(r"^tags\s*:", line, re.I):
            reading_tags = True
            inline = line.split(":", 1)[1].strip().strip("[]")
            if inline:
                tags.extend(part.strip().strip("'\"") for part in inline.split(","))
            continue
        if reading_tags and (match := re.match(r"^\s*-\s*(.+?)\s*$", line)):
            tags.append(match.group(1).strip().strip("'\""))
            continue
        if reading_tags and line and not line[0].isspace():
            break
    return tuple(dict.fromkeys(tag.lower() for tag in tags if tag))


def display_date(value: str) -> str:
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", value)
    if not match:
        return value
    year, month, day = (int(part) for part in match.groups())
    names = ("", "January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December")
    weekday = calendar_date(year, month, day).strftime("%A")
    return f"{weekday}, {day} {names[month]} {year}"


def publication_sort_date(path: Path, frontmatter: dict[str, str]) -> str:
    explicit = frontmatter.get("published") or frontmatter.get("publishdate")
    if explicit:
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", explicit)
        if match:
            return match.group(1)
    try:
        relative = path.relative_to(ROOT)
        result = subprocess.run(
            ["git", "log", "--follow", "--diff-filter=A", "--format=%cs", "--", str(relative)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        dates = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if dates:
            return dates[-1]
    except (OSError, ValueError):
        pass
    return calendar_date.today().isoformat()


def publication_date(path: Path, frontmatter: dict[str, str]) -> str:
    return display_date(publication_sort_date(path, frontmatter))


def image_size(frontmatter: dict[str, str]) -> str:
    value = (
        frontmatter.get("image_size")
        or frontmatter.get("image-size")
        or frontmatter.get("imagesize")
        or "auto"
    )
    normalized = value.strip().lower().rstrip("%")
    aliases = {"large": "full", "100": "full", "1": "full", "half": "50", "quarter": "25"}
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in {"auto", "full", "75", "50", "25"} else "auto"


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
    date_line = next((line for line in clean_lines if re.search(r"\b(?:19|20)\d{2}\b", line)), "Undated")
    date_fragment = re.search(
        r"\b(?:" + "|".join(MONTHS) + r")\b\s*,?\s*(?:19|20)\d{2}\b|\b(?:19|20)\d{2}\b",
        date_line, re.I,
    )
    completion_date = date_fragment.group(0) if date_fragment else date_line
    year_match = re.search(r"\b((?:19|20)\d{2})\b", completion_date)
    year = int(year_match.group(1)) if year_match else 0
    lower_date = completion_date.lower()
    month = next((number for name, number in MONTHS.items() if name in lower_date), 0)
    place_lines = []
    for line in clean_lines:
        if any(word in line.lower() for word in ("museum", "paris", "france", "new york")):
            place_value = line
            if line == date_line and date_fragment:
                place_value = (line[: date_fragment.start()] + line[date_fragment.end() :]).strip(" ,")
            if place_value:
                place_lines.append(place_value)
    place = " · ".join(place_lines)
    fact_lines = [
        line.rstrip(".") for line in clean_lines
        if line != date_line and line not in place_lines and "sold" not in line.lower()
    ]
    facts = " · ".join(fact_lines)
    sold = "sold" in body.lower()
    tags = frontmatter_tags(raw)
    if category not in tags:
        tags = (category, *tags)
    folder = path.parent.name.lower()
    url = f"{folder}/{slug_part(path.stem)}"
    post_sort_date = publication_sort_date(path, frontmatter)
    return Post(title, category, completion_date, display_date(post_sort_date), post_sort_date, year, month,
                image, url, facts, place, sold, tags, image_size(frontmatter))


def post_html(post: Post, anchor: str) -> str:
    title = html.escape(post.title)
    search_terms = " ".join((post.title, post.category, post.facts, post.place, *post.tags)).lower()
    facts = "".join(
        f"<span>{html.escape(item)}</span>"
        for item in post.facts.split(" · ") if item
    )
    place = "".join(
        f'<span class="place">{html.escape(item)}</span>'
        for item in post.place.split(" · ") if item
    )
    sold = '<span class="sold">sold</span>' if post.sold else ""
    return f"""<article class="post {html.escape(post.category)}"{anchor} data-search="{html.escape(search_terms)}" data-image-size="{html.escape(post.image_size)}">
  <p class="post-date">{html.escape(post.post_date)}</p>
  <a class="artwork" href="{html.escape(post.url)}" aria-label="View {title}"><img src="{html.escape(post.image)}" alt="{title}" loading="lazy"></a>
  <div class="inventory"><h1><a href="{html.escape(post.url)}">{title}</a></h1><div class="inventory-data">{facts}{place}<span class="completion-date">{html.escape(post.completion_date)}</span>{sold}</div></div>
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
    posts.sort(key=lambda p: (p.post_sort_date, p.year, p.month, p.title.lower()), reverse=True)
    counts = Counter(post.category for post in posts)
    tag_counts = Counter(tag for post in posts for tag in post.tags)
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
    low = min(tag_counts.values(), default=1)
    high = max(tag_counts.values(), default=1)
    tag_links = []
    for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0])):
        weight = 2 if high == low else 1 + round((count - low) / (high - low) * 3)
        tag_links.append(
            f'<a href="#" data-tag="{html.escape(tag)}" style="--weight:{weight}">'
            f'{html.escape(tag)} <small>{count}</small></a>'
        )
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>I NASTRI — Richmond Jeffrey</title><meta name="description" content="Drawings, paintings, and notes by Richmond Jeffrey.">
<link rel="stylesheet" href="inastri-home.css"></head><body>
<header class="site-header"><a class="identity" href="./" aria-label="I Nastri home"><span class="wordmark">I Nastri</span><img class="title-mark" src="assets/site-logo.gif" alt="Circular artwork detail"></a></header>
<main class="shell" id="work"><aside class="sidebar" id="archive">
<section class="archive-copy"><p><strong>I NASTRI</strong> is the personal website of <span class="nowrap">Richmond Jeffrey</span>. This page is an ongoing log of my paintings, drawings, writings, and other media. You can browse works broadly by tags using the menu below in this sidebar, or simply scroll through to enjoy the most recent posts. Any work with a price is for sale: if you are interested in buying a piece, please send me a message at:<a class="email-line" href="mailto:richmondjeffrey0@gmail.com">richmondjeffrey0@gmail.com</a></p><p>For my portfolio, as well as featured works and official information, please visit <a href="https://richmondjeffrey.com">richmondjeffrey.com</a>.</p></section>
<section><p class="eyebrow">Tags</p><div class="tag-cloud">{''.join(tag_links)}</div></section>
<section><p class="eyebrow">Archive</p><div class="years">{year_links}</div></section>
<section><p class="eyebrow">Links</p><a href="index.xml">rss feed</a></section></aside>
<section class="feed" aria-label="Recent work">{''.join(rendered)}</section></main>
<footer class="site-footer"><span>© 2026 Richmond Jeffrey</span></footer>
<script>const posts=[...document.querySelectorAll('.post')];const applyFilter=v=>posts.forEach(p=>p.hidden=v&&!((p.dataset.search+' '+p.textContent).toLowerCase().includes(v)));document.querySelectorAll('[data-year],[data-tag]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();applyFilter((a.dataset.year||a.dataset.tag).toLowerCase());}}));document.querySelector('[data-reset]')?.addEventListener('click',()=>applyFilter(''));const artworkImages=[...document.querySelectorAll('.artwork img')];const pct={{full:1,75:.75,50:.5,25:.25}};const sizeArtwork=img=>{{if(!img.naturalWidth)return;const post=img.closest('.post');const setting=post?.dataset.imageSize||'auto';const container=img.closest('.artwork');const max=container.clientWidth;if(pct[setting]){{img.style.width=Math.round(max*pct[setting])+'px';img.style.height='auto';return;}}const ratio=img.naturalWidth/img.naturalHeight;let scale=1;if(ratio<.8)scale=.52;else if(ratio<1)scale=.62;else if(ratio<1.2)scale=.7;img.style.width=Math.round(max*scale)+'px';img.style.height='auto';}};artworkImages.forEach(img=>{{if(img.complete)sizeArtwork(img);else img.addEventListener('load',()=>sizeArtwork(img),{{once:true}});}});window.addEventListener('resize',()=>artworkImages.forEach(sizeArtwork));</script>
</body></html>"""
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "index.html").write_text(page, encoding="utf-8")
    (PUBLIC / "inastri-home.css").write_text(STYLE, encoding="utf-8")
    print(f"Built I NASTRI homepage with {len(posts)} artwork posts")


if __name__ == "__main__":
    main()
