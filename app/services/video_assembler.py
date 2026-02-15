import subprocess
import uuid
from pathlib import Path
from app.config import VIDEOS_DIR, IMAGES_DIR


def assemble_video(image_paths: list[Path], durations: list[int], output_name: str | None = None) -> Path:
    """Assemble images into a video using FFmpeg with crossfade transitions."""
    if output_name is None:
        output_name = f"video_{uuid.uuid4().hex[:8]}.mp4"

    output_path = VIDEOS_DIR / output_name

    # Build FFmpeg filter for concatenation with durations
    # Create a temporary file list for concat demuxer
    filelist_path = IMAGES_DIR / f"filelist_{uuid.uuid4().hex[:8]}.txt"

    with open(filelist_path, "w") as f:
        for img_path, duration in zip(image_paths, durations):
            f.write(f"file '{img_path.resolve()}'\n")
            f.write(f"duration {duration}\n")
        # Repeat last image (FFmpeg concat demuxer quirk)
        if image_paths:
            f.write(f"file '{image_paths[-1].resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(filelist_path),
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # Cleanup filelist
    filelist_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")

    return output_path
