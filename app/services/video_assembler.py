import subprocess
import uuid
from pathlib import Path
from pydub import AudioSegment
from app.config import VIDEOS_DIR, IMAGES_DIR, AUDIO_DIR


def _run_ffmpeg(cmd: list[str], timeout: int = 600):
    """Run an FFmpeg command and raise on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[-500:]}")
    return result


def assemble_video(
    image_paths: list[Path],
    durations: list[float],
    output_name: str | None = None,
    narration_paths: list[Path | None] | None = None,
    subtitle_path: Path | None = None,
    music_path: Path | None = None,
    music_volume: float = 0.15,
) -> Path:
    """Assemble images + narration + subtitles + music into a final video."""
    if output_name is None:
        output_name = f"video_{uuid.uuid4().hex[:8]}.mp4"

    uid = uuid.uuid4().hex[:8]
    output_path = VIDEOS_DIR / output_name
    silent_video_path = VIDEOS_DIR / f"_silent_{uid}.mp4"

    # --- Step 1: Create silent video from images ---
    filelist_path = IMAGES_DIR / f"filelist_{uid}.txt"
    with open(filelist_path, "w") as f:
        for img_path, duration in zip(image_paths, durations):
            f.write(f"file '{img_path.resolve()}'\n")
            f.write(f"duration {duration}\n")
        if image_paths:
            f.write(f"file '{image_paths[-1].resolve()}'\n")

    vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p"

    # Add subtitles to video filter if available
    if subtitle_path and subtitle_path.exists():
        srt_escaped = str(subtitle_path.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        vf += f",subtitles='{srt_escaped}':force_style='FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=30'"

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(filelist_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-movflags", "+faststart",
        str(silent_video_path),
    ]
    _run_ffmpeg(cmd)
    filelist_path.unlink(missing_ok=True)

    # --- Step 2: Build combined audio track (narration + music) ---
    has_narration = narration_paths and any(p is not None for p in narration_paths)
    has_music = music_path and music_path.exists()

    if not has_narration and not has_music:
        # No audio, just rename silent video
        silent_video_path.rename(output_path)
        return output_path

    total_duration_ms = int(sum(durations) * 1000)

    # Build narration track
    narration_track = AudioSegment.silent(duration=total_duration_ms)
    if has_narration:
        offset_ms = 0
        for i, (nar_path, dur) in enumerate(zip(narration_paths, durations)):
            if nar_path and nar_path.exists():
                clip = AudioSegment.from_mp3(str(nar_path))
                narration_track = narration_track.overlay(clip, position=offset_ms)
            offset_ms += int(dur * 1000)

    # Build music track (looped and lowered volume)
    if has_music:
        music_clip = AudioSegment.from_mp3(str(music_path))
        music_clip = music_clip - (20 * (1 - music_volume))  # Lower volume

        # Loop music to fill the entire video
        loops_needed = (total_duration_ms // len(music_clip)) + 1
        music_track = (music_clip * loops_needed)[:total_duration_ms]

        # Fade in/out
        music_track = music_track.fade_in(2000).fade_out(3000)
    else:
        music_track = AudioSegment.silent(duration=total_duration_ms)

    # Mix narration and music
    final_audio = narration_track.overlay(music_track)

    # Export combined audio
    audio_path = AUDIO_DIR / f"_combined_{uid}.mp3"
    final_audio.export(str(audio_path), format="mp3")

    # --- Step 3: Merge video + audio ---
    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path),
    ]
    _run_ffmpeg(cmd)

    # Cleanup temp files
    silent_video_path.unlink(missing_ok=True)
    audio_path.unlink(missing_ok=True)

    return output_path
