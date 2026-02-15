from pathlib import Path
from app.config import AUDIO_DIR


def generate_srt(scenes: list[dict], durations: list[float], job_id: str) -> Path:
    """Generate an SRT subtitle file from scenes and their durations."""
    output_path = AUDIO_DIR / f"{job_id}.srt"

    current_time = 0.0
    lines = []

    for i, (scene, duration) in enumerate(zip(scenes, durations)):
        narration = scene.get("narration", "").strip()
        if not narration:
            current_time += duration
            continue

        start = format_srt_time(current_time)
        end = format_srt_time(current_time + duration)

        lines.append(f"{i + 1}")
        lines.append(f"{start} --> {end}")
        lines.append(narration)
        lines.append("")

        current_time += duration

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def format_srt_time(seconds: float) -> str:
    """Format seconds to SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
