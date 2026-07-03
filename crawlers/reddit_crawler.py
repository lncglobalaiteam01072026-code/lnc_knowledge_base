"""
Reddit crawler dùng JSON API (www.reddit.com/r/{sub}/new.json).
Không cần credentials — public API với User-Agent đúng format.
old.reddit.com HTML scraping bị block từ cloud IPs (GitHub Actions 403).
"""
import asyncio
import hashlib
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx

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

# Reddit yêu cầu User-Agent format: platform:app_id:version (by /u/username)
# Dùng generic không qua OAuth — rate limit 1 req/s
_HEADERS = {
    "User-Agent": "linux:lnc-kb-crawler:1.0 (immigration knowledge base; contact phi.tran@lncglobal.vn)",
    "Accept": "application/json",
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
        """Fetch new posts via Reddit JSON API (no OAuth, rate-limit 1 req/s)."""
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    [WARN] fetch r/{subreddit}: {e}")
            return []

        posts = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            posts.append({
                "id":           d.get("id", ""),
                "title":        d.get("title", ""),
                "selftext":     d.get("selftext", ""),
                "score":        d.get("score", 0),
                "created_utc":  d.get("created_utc", 0),
                "flair":        d.get("link_flair_text") or "",
                "num_comments": d.get("num_comments", 0),
            })
        return posts

    async def _fetch_comments(self, client: httpx.AsyncClient, subreddit: str, post_id: str):
        """Fetch comments via Reddit JSON API. Returns (comments, selftext)."""
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?sort=top&limit={MAX_COMMENTS}"
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"    [WARN] fetch comments {post_id}: {e}")
            return [], ""

        # data[0] = post listing, data[1] = comments listing
        selftext = ""
        if isinstance(data, list) and data:
            post_children = data[0].get("data", {}).get("children", [])
            if post_children:
                selftext = post_children[0].get("data", {}).get("selftext", "")

        comments = []
        if isinstance(data, list) and len(data) > 1:
            for child in data[1].get("data", {}).get("children", []):
                d = child.get("data", {})
                if not d or d.get("author") in EXCLUDE_BOTS:
                    continue
                score = d.get("score", 0)
                body  = d.get("body", "")
                if score < MIN_COMMENT_SCORE or len(body) < MIN_COMMENT_LENGTH:
                    continue
                comments.append({"author": d.get("author", "[deleted]"), "score": score, "body": body})

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
