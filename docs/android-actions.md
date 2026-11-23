# Android-only GitHub Actions video generator

Open **Actions → Android - Generate Reddit Short → Run workflow** on your Android browser. Choose `demo` (no API keys) or `script` (uses `examples/android-story.json`). Defaults: random gameplay, full-screen, Guy voice, karaoke captions. The workflow uses PurffleShorts' **existing** renderer, not a separate imitation.

**Gameplay:** The repository contains no verified reusable Minecraft footage. Upload your own or properly licensed gameplay MP4 files to `media/backgrounds/` using GitHub's web interface. Random selects from those files. If none exists, the demo uses generated visuals instead; it does not falsely label them Minecraft. Do not scrape copyrighted gameplay from YouTube.

**Free:** The demo and committed script require no paid AI API. Edge TTS uses an online service, which can be unavailable or rate-limited. Script mode reads the JSON already committed in the repository. Real Reddit fetching is not enabled by this workflow; only use Reddit content with permission and approved access.

**Output:** A successful run checks that an actual 720x1280 MP4 was rendered and uploads an artifact called `android-reddit-short` containing the video, captions, cover and metadata where produced. Tap the run, download the ZIP artifact, and extract it on Android. Nothing is automatically published.

**Troubleshooting:** Open the failed Actions job to see the step and error. Python syntax, FFmpeg subtitle filter, rendering, and output checks are included.

This workflow is distinct from upstream CI and leaves the upstream test suite intact.

## Fix log
- Fixed GitHub Actions output directory mismatch: PurffleShorts writes to `output_videos/`, not `DATA_DIR`. Commit `f134c4556aa61a44c6884ca3a8dcb49d810d818c`. The first demo successfully rendered before the artifact verification step failed. Re-run the workflow to verify the fix.
