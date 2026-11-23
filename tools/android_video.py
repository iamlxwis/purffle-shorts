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
    if os.environ.get("GAMEPLAY_RIGHTS", "false").lower() != "true":
        raise SystemExit("Check gameplay_rights to confirm you may reuse the YouTube footage")
    folder.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "yt_dlp", "--no-playlist", "--max-filesize", "350M",
                    "--match-filter", "duration <= 1800", "--merge-output-format", "mp4",
                    "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
                    "-o", str(folder / "youtube-gameplay.%(ext)s"), url], check=True)
    if not any(p.suffix.lower() == ".mp4" for p in folder.iterdir()):
        raise SystemExit("YouTube download did not produce an MP4; check the URL and yt-dlp logs")


VOICES = {"guy": "en-US-GuyNeural", "jenny": "en-US-JennyNeural",
          "ryan": "en-GB-RyanNeural", "sonia": "en-GB-SoniaNeural"}

def main():
    mode = os.environ.get("MODE", "script")
    if mode != "script":
        raise SystemExit("Production workflow requires script mode; demo rendering is disabled")
    layout = os.environ.get("LAYOUT", "full")
    voice = VOICES[os.environ.get("VOICE", "guy")]
    captions = os.environ.get("CAPTIONS", "karaoke")
    background = os.environ.get("BACKGROUND", "random")
    args = [sys.executable, "-m", "purffle_shorts", "make",
            "--style", "reddit", "--layout", layout, "--voice", voice,
            "--tts", "edge", "--caption-style", captions, "--resolution", "720x1280",
            "--no-upload", "--no-music"]
    if mode == "script":
        script = Path(os.environ.get("SCRIPT_PATH", "examples/android-story.json"))
        if not script.is_file() or script.suffix.lower() != ".json":
            raise SystemExit(f"Script JSON does not exist: {script}")
        args.extend(["--script", str(script)])
    youtube_url = os.environ.get("YOUTUBE_GAMEPLAY_URL", "").strip()
    if youtube_url and background != "random":
        raise SystemExit("Set background to random to use a YouTube gameplay URL")
    if background == "random":
        folder = Path("media/backgrounds")
        if youtube_url:
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
