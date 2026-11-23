"""Android GitHub Actions wrapper for the existing PurffleShorts CLI."""
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def download_authorized_gameplay(url: str, folder: Path) -> None:
    """Download one user-authorized YouTube clip without shell interpolation."""
    host = (urlparse(url).hostname or "").lower()
    if urlparse(url).scheme != "https" or host not in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}:
        raise SystemExit("Gameplay URL must be an HTTPS YouTube video link")
    print("Ensure you have permission to reuse the configured gameplay footage.", flush=True)
    folder.mkdir(parents=True, exist_ok=True)
    errors = []
    for command in (
        ["node", "tools/download_gameplay.cjs", str(folder / "youtube-gameplay.mp4")],
        [sys.executable, "-m", "yt_dlp", "--no-playlist", "--max-filesize", "350M",
         "--match-filter", "duration <= 1800", "--merge-output-format", "mp4",
         "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
         "-o", str(folder / "youtube-gameplay.%(ext)s"), url],
    ):
        try:
            subprocess.run(command, check=True)
            if any(p.suffix.lower() == ".mp4" and p.stat().st_size > 100000 for p in folder.iterdir()):
                return
            errors.append("Downloader produced no valid MP4")
        except (subprocess.CalledProcessError, OSError) as exc:
            errors.append(str(exc))
    raise SystemExit("Both npm and yt-dlp downloads failed. YouTube may require authentication on GitHub-hosted runners. " + "; ".join(errors))



VOICES = {"guy": "en-US-GuyNeural", "jenny": "en-US-JennyNeural",
          "ryan": "en-GB-RyanNeural", "sonia": "en-GB-SoniaNeural"}

def main():
    mode = os.environ.get("MODE", "reddit")
    if mode not in {"reddit", "script"}:
        raise SystemExit("Production workflow requires reddit or script mode")
    layout = os.environ.get("LAYOUT", "full")
    voice = VOICES[os.environ.get("VOICE", "guy")]
    captions = os.environ.get("CAPTIONS", "karaoke")
    background = os.environ.get("BACKGROUND", "random")
    args = [sys.executable, "-m", "purffle_shorts", "make",
            "--style", "reddit", "--layout", layout, "--voice", voice,
            "--tts", "edge", "--caption-style", captions, "--resolution", "720x1280",
            "--no-upload", "--no-music"]
    if mode in {"reddit", "script"}:
        script = Path("android-output/reddit-script.json") if mode == "reddit" else Path(os.environ.get("SCRIPT_PATH", "examples/android-story.json"))
        if mode == "reddit":
            subprocess.run([sys.executable, "tools/reddit_story.py", str(script)], check=True)
        if not script.is_file() or script.suffix.lower() != ".json":
            raise SystemExit(f"Script JSON does not exist: {script}")
        args.extend(["--script", str(script)])
    youtube_url = os.environ.get("YOUTUBE_GAMEPLAY_URL", "").strip()
    if youtube_url and background != "random":
        raise SystemExit("Set background to random to use a YouTube gameplay URL")
    if background == "random":
        folder = Path("media/backgrounds")
        clips = sorted(p for p in folder.glob("*") if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} and p.is_file())
        if clips:
            print("Using supplied gameplay file; skipping blocked YouTube download", flush=True)
        elif youtube_url:
            download_authorized_gameplay(youtube_url, folder)
            clips = sorted(p for p in folder.glob("*") if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} and p.is_file())
        if clips:
            # The native engine randomly chooses one of these clips.
            args.extend(["--background", str(folder)])
            print(f"Found {len(clips)} licensed user-provided gameplay clip(s)", flush=True)
        else:
            raise SystemExit("No gameplay MP4 found. Supply an authorized YouTube URL or add media/backgrounds/*.mp4; production runs require real footage.")
    print("Running native PurffleShorts:", " ".join(args), flush=True)
    subprocess.run(args, check=True)

if __name__ == "__main__":
    main()
