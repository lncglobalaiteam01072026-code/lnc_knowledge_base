"""
Reddit crawler dùng old.reddit.com HTML scraping (BeautifulSoup).
Không cần credentials — scrape trang HTML tĩnh của old Reddit.
"""
import asyncio
import hashlib
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler

# Keyword dài / multi-word: dùng substring match
# Keyword ngắn / acronym: phải match nguyên từ (word-boundary) để tránh false positive
# Ví dụ: "ITA" không được match "inherITAnce", "NOC" không match "innocuous"
_SUBSTRING_KEYWORDS = [
    "AAIP", "Alberta Advantage", "Alberta PNP",
    "BC PNP", "BCPNP", "Skills Immigration",
    "Express Entry", "CRS score",
    "work permit Canada", "PR Canada",
    "processing time", "rejection", "refused", "denied",
    "job offer Canada",
    "dinh cu Canada", "nhap cu Canada",
    "định cư Canada", "nhập cư Canada",
    # NZ keywords
    "AEWV", "Accredited Employer Work Visa", "Accredited Employer",
    "Skilled Migrant Category", "Green List", "INZ",
    "New Zealand visa", "NZ work visa", "NZ PR", "NZ residence",
    "immigration New Zealand", "immigration.govt.nz",
    "RSE scheme", "SMC points",
    "dinh cu New Zealand", "nhap cu New Zealand",
    "định cư New Zealand", "nhập cư New Zealand",
]
_WORD_KEYWORDS = ["IRCC", "ITA", "LMIA", "NOC", "TEER", "SMC"]  # phải match nguyên từ

KEYWORDS = _SUBSTRING_KEYWORDS + _WORD_KEYWORDS

EXCLUDE_BOTS     = {"AutoModerator", "ImmiBot", "VisaBot"}
EXCLUDE_FLAIRS   = {"meme", "rant", "off-topic", "humor"}
EXCLUDE_KEYWORDS = ["illegal", "fake document", "scam me", "cheat", "bypass"]

MIN_POST_SCORE     = 5
MIN_COMMENT_SCORE  = 3
MIN_COMMENT_LENGTH = 80
MAX_COMMENTS       = 30
LOOKBACK_DAYS      = 180

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _hash_user(username: str) -> str:
    return hashlib.sha256(username.encode()).hexdigest()[:8]


def _kw_match(text: str) -> list:
    text_lower = text.lower()
    matched = []
    for k in _SUBSTRING_KEYWORDS:
        if k.lower() in text_lower:
            matched.append(k)
    for k in _WORD_KEYWORDS:
        if re.search(r'\b' + re.escape(k.lower()) + r'\b', text_lower):
            matched.append(k)
    return matched


def _program_tag(kws: list) -> list:
    tags = set()
    if any(k in kws for k in ["AAIP", "Alberta Advantage", "Alberta PNP"]):
        tags.add("aaip")
    if any(k in kws for k in ["BC PNP", "BCPNP", "Skills Immigration"]):
        tags.add("bcpnp")
    if any(k in kws for k in ["Express Entry", "ITA", "CRS score"]):
        tags.add("express_entry")
    if any(k in kws for k in ["LMIA", "work permit Canada"]):
        tags.add("lmia")
    if any(k in kws for k in ["AEWV", "Accredited Employer Work Visa", "Accredited Employer"]):
        tags.add("nzaewv")
    if any(k in kws for k in ["Skilled Migrant Category", "SMC", "SMC points"]):
        tags.add("nzsmc")
    if any(k in kws for k in ["Green List", "NZ residence", "NZ PR"]):
        tags.add("nz_residence")
    return sorted(tags) or ["general"]


def _parse_score(score_text: str) -> int:
    """'42 points' hoặc '1 point' → 42. 'vote' / '' → 0."""
    try:
        return int(score_text.split()[0])
    except (ValueError, IndexError):
        return 0


class RedditCrawler(BaseCrawler):
    def __init__(self, source: dict, output_root: Path):
        super().__init__(source, output_root)
        self._province   = source["province"]
        self._subreddits = source["subreddits"]

    async def run(self) -> list:
        written = []
        cutoff  = datetime.now(tz=timezone.utc) - timedelta(days=LOOKBACK_DAYS)
        out_dir = self.output_root / "03_province_community" / self._province
        out_dir.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(
            headers=_HEADERS, timeout=30, follow_redirects=True
        ) as client:
            for sr_name in self._subreddits:
                sr_clean = sr_name.lstrip("r/")
                print(f"  Crawling r/{sr_clean} -> {self._province}/...")
                posts = await self._fetch_posts(client, sr_clean)
                print(f"    Found {len(posts)} posts to check")

                for post in posts:
                    post_time = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)
                    if post_time < cutoff or post["score"] < MIN_POST_SCORE:
                        continue

                    flair = (post.get("flair") or "").lower()
                    if any(ex in flair for ex in EXCLUDE_FLAIRS):
                        continue

                    full_text = f"{post['title']} {post.get('selftext', '')}"
                    if any(bad in full_text.lower() for bad in EXCLUDE_KEYWORDS):
                        continue

                    matched = _kw_match(full_text)
                    if not matched:
                        continue

                    path = out_dir / f"r_{sr_clean}_{post['id']}.md"
                    if path.exists():
                        written.append(path)
                        continue

                    await asyncio.sleep(1.5)
                    comments, selftext = await self._fetch_comments(client, sr_clean, post["id"])
                    post["selftext"] = selftext

                    # Re-verify với full text (title + body) sau khi lấy được body
                    full_text_with_body = f"{post['title']} {selftext}"
                    matched = _kw_match(full_text_with_body)
                    if not matched:
                        print(f"    Skip (no keyword in full text): {post['id']}")
                        continue

                    # Bỏ qua post không có comment nào đủ tiêu chuẩn (thường là pinned/megathread rỗng)
                    if not comments and not selftext.strip():
                        print(f"    Skip (no body + no comments): {post['id']}")
                        continue

                    post_date = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc).strftime("%Y-%m-%d")
                    content   = self._build_body(post, comments)
                    self.write_markdown(path, content, extra_meta={
                        "source_id":          f"reddit_{sr_clean}_{post['id']}",
                        "source_url":         f"https://old.reddit.com/r/{sr_clean}/comments/{post['id']}/",
                        "subreddit":          f"r/{sr_clean}",
                        "program_tag":        _program_tag(matched),
                        "trust_level":        "LOW",
                        "use_for":            ["objection_handling", "sentiment", "case_study"],
                        "NOT_use_for":        ["policy_citation", "official_numbers", "legal_advice"],
                        "post_score":         post["score"],
                        "reddit_comment_count": post.get("num_comments", 0),
                        "saved_comments":     len(comments),
                        "post_date":          post_date,
                    })
                    written.append(path)
                    print(f"    Saved: r_{sr_clean}_{post['id']}.md")

                await asyncio.sleep(2)

        return written

    async def _fetch_posts(self, client: httpx.AsyncClient, subreddit: str) -> list:
        """Scrape old Reddit hot listing HTML."""
        url = f"https://old.reddit.com/r/{subreddit}/hot/"
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"    [WARN] fetch r/{subreddit}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        posts = []

        for thing in soup.find_all("div", attrs={"data-fullname": True}):
            classes = thing.get("class", [])
            if "thing" not in classes or "link" not in classes:
                continue

            post_id = thing.get("data-fullname", "").replace("t3_", "")
            if not post_id:
                continue

            title_tag = thing.find("a", class_="title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            score_tag = thing.find("div", class_="score")
            score = _parse_score(score_tag.get_text(strip=True)) if score_tag else 0

            timestamp = int(thing.get("data-timestamp", 0)) // 1000  # ms -> s

            flair_tag = thing.find("span", class_="linkflairlabel")
            flair = flair_tag.get_text(strip=True) if flair_tag else ""

            selftext = ""  # old Reddit listing doesn't include body — fetched later if needed

            comments_tag = thing.find("a", class_="comments")
            num_comments = 0
            if comments_tag:
                ctext = comments_tag.get_text(strip=True)
                try:
                    num_comments = int(ctext.split()[0])
                except (ValueError, IndexError):
                    pass

            posts.append({
                "id": post_id,
                "title": title,
                "selftext": selftext,
                "score": score,
                "created_utc": timestamp,
                "flair": flair,
                "num_comments": num_comments,
            })

        return posts

    async def _fetch_comments(self, client: httpx.AsyncClient, subreddit: str, post_id: str):
        """Scrape old Reddit post page. Returns (comments, selftext)."""
        url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}/?sort=top&limit={MAX_COMMENTS}"
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except Exception as e:
            print(f"    [WARN] fetch comments {post_id}: {e}")
            return [], ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract post body
        selftext = ""
        body_div = soup.find("div", class_="expando")
        if body_div:
            md_div = body_div.find("div", class_="md")
            if md_div:
                selftext = md_div.get_text(separator="\n", strip=True)

        comments = []
        for cdiv in soup.find_all("div", class_="comment"):
            author_tag = cdiv.find("a", class_="author")
            author     = author_tag.get_text(strip=True) if author_tag else "[deleted]"
            if author in EXCLUDE_BOTS:
                continue

            score_tag  = cdiv.find("span", class_="score")
            score      = _parse_score(score_tag.get_text(strip=True)) if score_tag else 0
            if score < MIN_COMMENT_SCORE:
                continue

            body_tag = cdiv.find("div", class_="md")
            body     = body_tag.get_text(separator="\n", strip=True) if body_tag else ""
            if len(body) < MIN_COMMENT_LENGTH:
                continue

            comments.append({"author": author, "score": score, "body": body})

        return sorted(comments, key=lambda x: x["score"], reverse=True)[:MAX_COMMENTS], selftext

    def _build_body(self, post: dict, comments: list) -> str:
        lines = [
            "## Post\n",
            f"**Title:** {post['title']}\n",
            f"**Body:**\n{post.get('selftext') or '_(see source URL)_'}\n",
            "---\n",
            f"## Top comments (score >= {MIN_COMMENT_SCORE}, length >= {MIN_COMMENT_LENGTH} chars)\n",
        ]
        for i, c in enumerate(comments, 1):
            author = _hash_user(c["author"]) if c["author"] != "[deleted]" else "deleted"
            lines.append(f"### Comment {i} . score: {c['score']} . u/{author}\n{c['body']}\n")
        lines += [
            "---\n",
            "## AI annotation\n",
            "**Pain points detected:** _[chua xu ly]_\n",
            "**Objections detected:** _[chua xu ly]_\n",
            "**Sentiment:** _[chua xu ly]_\n",
            "**Key facts mentioned:** _[chua xu ly]_\n",
        ]
        return "\n".join(lines)
