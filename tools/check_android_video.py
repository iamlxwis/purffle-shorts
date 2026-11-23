"""Reject workflow success unless an actual playable vertical MP4 exists."""
import json
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(sys.argv[1])
    videos = list(root.rglob("*.mp4"))
    if not videos:
        raise SystemExit(f"No MP4 output found in {root}")
    for video in videos:
        probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-show_entries", "format=duration",
             "-of", "json", str(video)], text=True)
        data = json.loads(probe)
        streams = data.get("streams", [])
        duration = float(data.get("format", {}).get("duration", 0))
        if not streams or streams[0]["width"] != 720 or streams[0]["height"] != 1280 or duration < 2:
            raise SystemExit(f"Invalid vertical MP4: {video} ({data})")
        print(f"Verified {video}: 720x1280, {duration:.1f} seconds", flush=True)

if __name__ == "__main__":
    main()
