"""Convert an accessible public Reddit self-post to a PurffleShorts script.
No credentials or access-control bypass; fail if Reddit denies access.
"""
import html
import json
import os
import random
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from base64 import b64encode

USER_AGENT = "PurffleShorts/1.0 (public-story attribution; contact repository owner)"
def fetch_json(url):
    client_id = os.environ.get("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("Reddit blocks unauthenticated GitHub Actions requests (HTTP 403). Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET repository secrets for approved Reddit API access, or use script mode.")
    token_req = Request("https://www.reddit.com/api/v1/access_token",
                        data=urlencode({"grant_type": "client_credentials"}).encode(),
                        headers={"User-Agent": USER_AGENT,
                                 "Authorization": "Basic " + b64encode(f"{client_id}:{client_secret}".encode()).decode()})
    with urlopen(token_req, timeout=25) as response:
        token = json.load(response)["access_token"]
    path = urlparse(url)
    oauth_url = "https://oauth.reddit.com" + path.path + ("?" + path.query if path.query else "")
    req = Request(oauth_url, headers={"User-Agent": USER_AGENT,
                                     "Authorization": "bearer " + token, "Accept": "application/json"})
    with urlopen(req, timeout=25) as response:
        return json.load(response)

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(s)))
    s = re.sub(r"\s+", " ", s).strip()
    return s

def choose_post():
    direct = os.environ.get("REDDIT_POST_URL", "").strip()
    title = os.environ.get("REDDIT_MANUAL_TITLE", "").strip()
    body = os.environ.get("REDDIT_MANUAL_BODY", "").strip()
    if title or body:
        if not title or not body:
            raise ValueError("Manual fallback requires both Reddit title and body")
        if len(title) > 300 or len(body) > 15000:
            raise ValueError("Manual story is too long")
        if direct:
            u = urlparse(direct)
            if u.scheme != "https" or u.hostname not in {"reddit.com", "www.reddit.com", "old.reddit.com"} or not re.match(r"^/r/[A-Za-z0-9_]+/(?:s/[A-Za-z0-9]+|comments/[A-Za-z0-9]+)", u.path):
                raise ValueError("Invalid Reddit post URL")
            subreddit = u.path.split("/")[2]
            permalink = u.path
        else:
            subreddit = os.environ.get("REDDIT_SUBREDDIT", "stories").strip().removeprefix("r/")
            if not re.fullmatch(r"[A-Za-z0-9_]{2,21}", subreddit):
                raise ValueError("Invalid subreddit name")
            permalink = ""
        return {"title": title, "selftext": body, "subreddit": subreddit,
                "author": "unknown", "permalink": permalink, "manual_source": True}
    if direct:
        u = urlparse(direct)
        if u.scheme != "https" or u.hostname not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
            raise ValueError("Invalid Reddit URL")
        if re.match(r"^/r/[A-Za-z0-9_]+/s/[A-Za-z0-9]+/?$", u.path):
            with urlopen(Request(direct, headers={"User-Agent": USER_AGENT}), timeout=25) as response:
                u = urlparse(response.url)
            if u.hostname not in {"reddit.com", "www.reddit.com", "old.reddit.com"}:
                raise ValueError("Share link redirected outside Reddit")
        if not re.match(r"^/r/[A-Za-z0-9_]+/comments/[A-Za-z0-9]+(?:/|$)", u.path):
            raise ValueError("Could not resolve Reddit share link")
        url = "https://www.reddit.com" + u.path.rstrip("/") + ".json?raw_json=1"
        data = fetch_json(url)
        return data[0]["data"]["children"][0]["data"]
    sub = os.environ.get("REDDIT_SUBREDDIT", "stories").strip().removeprefix("r/")
    if not re.fullmatch(r"[A-Za-z0-9_]{2,21}", sub):
        raise ValueError("Invalid subreddit name")
    data = fetch_json(f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=50&raw_json=1")
    posts = [x["data"] for x in data["data"]["children"]]
    eligible = [p for p in posts if p.get("is_self") and not p.get("over_18") and not p.get("stickied")
                and not p.get("removed_by_category") and 90 <= len(clean(p.get("selftext", ""))) <= 6500
                and p.get("selftext") not in ("[removed]", "[deleted]")]
    if not eligible:
        raise ValueError("No eligible public text posts; choose another subreddit or direct post URL")
    return random.choice(eligible)

def build(post):
    title = clean(post.get("title", ""))
    body = clean(post.get("selftext", ""))
    if not title or len(body) < 90:
        raise ValueError("Post has no usable story text")
    words = body.split()
    # Keep a short-form excerpt, without inventing an ending or rewriting the author.
    words = words[:155]
    chunks = [" ".join(words[i:i+30]) for i in range(0, len(words), 30)]
    community = post.get("subreddit", "stories")
    permalink = "https://www.reddit.com" + post.get("permalink", "")
    if post.get("permalink") and not permalink.startswith("https://www.reddit.com/r/"):
        raise ValueError("Invalid Reddit permalink")
    return {
        "topic": title[:100], "title": title[:100], "hook_text": title[:45],
        "style": "reddit", "language": "en", "category": "entertainment",
        "cast": ["r/" + community, "u/" + post.get("author", "unknown")],
        "scenes": [{"speaker": "A", "narration": title, "search_query": "minecraft parkour",
                    "image_prompt": "", "emphasis": [], "emoji": ""}]
                  + [{"speaker": "A", "narration": chunk, "search_query": "minecraft parkour",
                      "image_prompt": "", "emphasis": [], "emoji": ""} for chunk in chunks],
        "description": f"Excerpt of a public Reddit post by u/{post.get('author','unknown')} in r/{community}. Source: {permalink}. The narration may be truncated.",
        "hashtags": ["#reddit", "#redditstories", "#shorts"],
        "tags": ["reddit story", community, "minecraft gameplay"],
    }

def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "android-output/reddit-script.json")
    try:
        post = choose_post()
        script = build(post)
    except Exception as exc:
        raise SystemExit(f"Reddit retrieval failed: {exc}. Reddit may restrict automated access; no fabricated fallback will be used.") from exc
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Selected public Reddit story:", script["description"], flush=True)

if __name__ == "__main__":
    main()
