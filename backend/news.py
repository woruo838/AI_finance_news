import datetime as dt
import re
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EIXIC&region=US&lang=en-US",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EDJI&region=US&lang=en-US",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
]

STOPWORDS = {
    "the",
    "and",
    "a",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "as",
    "at",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "it",
    "that",
    "this",
    "an",
    "or",
    "its",
    "has",
    "have",
    "after",
    "than",
    "up",
    "down",
    "over",
    "about",
    "into",
}


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    text = _clean_text(text)
    if not text:
        return []
    candidates = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in candidates if s.strip()]


def _word_scores(text: str) -> dict[str, int]:
    words = re.findall(r"[A-Za-z]{3,}", text.lower())
    scores: dict[str, int] = {}
    for word in words:
        if word in STOPWORDS:
            continue
        scores[word] = scores.get(word, 0) + 1
    return scores


def summarize(text: str, max_sentences: int = 2) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return ""
    scores = _word_scores(text)
    ranked = sorted(
        sentences,
        key=lambda s: sum(scores.get(word, 0) for word in re.findall(r"[A-Za-z]{3,}", s.lower())),
        reverse=True,
    )
    picked = ranked[:max_sentences]
    return " ".join(picked)


def _parse_pub_date(date_text: str) -> str:
    if not date_text:
        return ""
    try:
        parsed = dt.datetime.strptime(date_text[:25], "%a, %d %b %Y %H:%M:%S")
        return parsed.isoformat()
    except ValueError:
        return date_text


def _parse_rss(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, str]] = []
    for item in root.findall(".//item"):
        title = _clean_text(item.findtext("title", default=""))
        link = item.findtext("link", default="").strip()
        published = _parse_pub_date(item.findtext("pubDate", default=""))
        description = _clean_text(item.findtext("description", default=""))
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "published": published,
                "description": description,
            }
        )
    return items


def fetch_news(limit: int = 20, timeout: int = 12) -> list[dict[str, str]]:
    all_items: list[dict[str, str]] = []
    for feed in FEEDS:
        try:
            with urllib.request.urlopen(feed, timeout=timeout) as response:
                xml_text = response.read().decode("utf-8", errors="ignore")
            all_items.extend(_parse_rss(xml_text))
        except (urllib.error.URLError, ET.ParseError):
            continue
    unique = {}
    for item in all_items:
        unique[item["link"]] = item
    items = list(unique.values())
    items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return items[:limit]


def build_digest(limit: int = 10) -> dict[str, object]:
    items = fetch_news(limit=limit)
    enriched = []
    for item in items:
        summary = summarize(item.get("description", ""))
        enriched.append({**item, "summary": summary})
    highlights = " ".join(
        [summary for summary in (item["summary"] for item in enriched) if summary]
    ).strip()
    if highlights:
        highlights = summarize(highlights, max_sentences=3)
    return {
        "date": dt.date.today().isoformat(),
        "highlights": highlights,
        "articles": enriched,
    }
