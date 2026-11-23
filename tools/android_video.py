"""Android GitHub Actions wrapper for the existing PurffleShorts CLI."""
import os
import subprocess
import sys
from pathlib import Path

VOICES = {"guy": "en-US-GuyNeural", "jenny": "en-US-JennyNeural",
          "ryan": "en-GB-RyanNeural", "sonia": "en-GB-SoniaNeural"}

def main():
    mode = os.environ.get("MODE", "demo")
    layout = os.environ.get("LAYOUT", "full")
    voice = VOICES[os.environ.get("VOICE", "guy")]
    captions = os.environ.get("CAPTIONS", "karaoke")
    background = os.environ.get("BACKGROUND", "random")
    args = [sys.executable, "-m", "purffle_shorts", mode if mode == "demo" else "make",
            "--style", "reddit", "--layout", layout, "--voice", voice,
            "--tts", "edge", "--caption-style", captions, "--resolution", "720x1280",
            "--no-upload", "--no-music"]
    if mode == "script":
        script = Path(os.environ.get("SCRIPT_PATH", "examples/android-story.json"))
        if not script.is_file() or script.suffix.lower() != ".json":
            raise SystemExit(f"Script JSON does not exist: {script}")
        args.extend(["--script", str(script)])
    if background == "random":
        folder = Path("media/backgrounds")
        clips = sorted(p for p in folder.glob("*") if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} and p.is_file())
        if clips:
            # The native engine randomly chooses one of these clips.
            args.extend(["--background", str(folder)])
            print(f"Found {len(clips)} licensed user-provided gameplay clip(s)", flush=True)
        else:
            print("No gameplay clips supplied; demo will use generated visuals, not Minecraft.", flush=True)
    print("Running native PurffleShorts:", " ".join(args), flush=True)
    subprocess.run(args, check=True)

if __name__ == "__main__":
    main()
