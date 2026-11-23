# Android-only GitHub Actions video generator

Open **Actions → Android - Generate Reddit Short → Run workflow** on your Android browser. Choose `demo` (no API keys) or `script` (uses `examples/android-story.json`). Defaults: random gameplay, full-screen, Guy voice, karaoke captions. The workflow uses PurffleShorts' **existing** renderer, not a separate imitation.

**Gameplay:** The repository contains no verified reusable Minecraft footage. Upload your own or properly licensed gameplay MP4 files to `media/backgrounds/` using GitHub's web interface. Random selects from those files. If none exists, the demo uses generated visuals instead; it does not falsely label them Minecraft. Do not scrape copyrighted gameplay from YouTube.

**Free:** The demo and committed script require no paid AI API. Edge TTS uses an online service, which can be unavailable or rate-limited. Script mode reads the JSON already committed in the repository. Real Reddit fetching is not enabled by this workflow; only use Reddit content with permission and approved access.

**Output:** A successful run checks that an actual 720x1280 MP4 was rendered and uploads an artifact called `android-reddit-short` containing the video, captions, cover and metadata where produced. Tap the run, download the ZIP artifact, and extract it on Android. Nothing is automatically published.

**Troubleshooting:** Open the failed Actions job to see the step and error. Python syntax, FFmpeg subtitle filter, rendering, and output checks are included.

This workflow is distinct from upstream CI and leaves the upstream test suite intact.

## Fix log
- Fixed GitHub Actions output directory mismatch: PurffleShorts writes to `output_videos/`, not `DATA_DIR`. Commit `f134c4556aa61a44c6884ca3a8dcb49d810d818c`. The first demo successfully rendered before the artifact verification step failed. Re-run the workflow to verify the fix.

## YouTube gameplay (Android)
In Actions → Android - Generate Reddit Short → Run workflow, paste an HTTPS YouTube video link into **youtube_gameplay_url**, select **background: random**, and check **gameplay_rights** only when you own the footage or have permission to reuse it. The runner uses yt-dlp to download a single MP4, then passes it to the original background renderer. Downloads can fail if YouTube restricts access; no bypass is guaranteed. Without a gameplay file or URL, random mode now fails clearly. To render without gameplay, select **generated**.

Change log: 11:30 PM PHT, November 24, 2026 — added YouTube gameplay URL and rights confirmation, preserved original rendering, and corrected cover/metadata artifact paths. Status: committed; cloud render with YouTube URL not yet verified.

## Production mode (current)
The Android workflow now uses `purffle_shorts make --script ...` exclusively. The sample JSON is an original fictional story, not a fetched Reddit post; edit the committed script for your desired content. A gameplay MP4 is required, either from an authorized YouTube URL or from `media/backgrounds/`. The workflow creates an actual finished MP4 artifact, with no demo fallback. Automatic Reddit story fetching is not configured. Status: production-mode changes committed; a successful run with gameplay footage has not yet been verified.

## Automatic real Reddit stories
Production workflow default is now `mode: reddit`. Choose `reddit_subreddit` for a random eligible public self-post, or supply `reddit_post_url` for one specific public post. The original post's title and first 155 body words are narrated as an attributed excerpt; this may end before the original post does. It does not fabricate an ending or generate a fake Reddit story. Reddit's public JSON endpoints may reject GitHub-hosted requests (including HTTP 403 or 429); the workflow fails explicitly in that case. No Reddit credentials or bypasses are used. Choose `mode: script` to render your own committed script instead. For real gameplay also supply an authorized YouTube gameplay URL and confirm rights.

Status: Reddit source implementation committed, end-to-end production rendering with Reddit access not yet verified.

## Reddit share links without credentials
Use `mode: reddit` and paste the Reddit `/r/.../s/...` share URL into `reddit_post_url`. If Reddit blocks API access, paste the actual title into `reddit_manual_title` and the actual post text into `reddit_manual_body` as well. Providing both manual fields bypasses the Reddit network request entirely; do not invent or paraphrase the source text. The fixed gameplay video is `https://youtu.be/s3_xa3qdsks` and requires the gameplay rights checkbox. Automatic Reddit extraction still requires approved Reddit API credentials; a share URL alone does not remove Reddit access restrictions. Status: implementation committed; full video generation not yet confirmed.

## Two-field production workflow (current)
Open Actions > Android - Generate Reddit Short > Run workflow. Enter only **Video title** and **Post text**. The workflow uses Guy narration, karaoke captions, 720x1280 full gameplay, and the fixed YouTube source `https://youtu.be/s3_xa3qdsks`. You must have permission to reuse the gameplay and story. YouTube may block automated GitHub downloads, so a successful render is not guaranteed until a complete run passes.
