from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
from app.config import AUDIO_DIR


def generate_narration(text: str, filename: str, lang: str = "fr") -> Path:
    """Generate speech audio from text using Google TTS (free)."""
    output_path = AUDIO_DIR / filename

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(str(output_path))

    return output_path


def get_audio_duration(audio_path: Path) -> float:
    """Get the duration of an audio file in seconds."""
    audio = AudioSegment.from_mp3(str(audio_path))
    return len(audio) / 1000.0


def generate_all_narrations(scenes: list[dict], job_id: str) -> list[dict]:
    """Generate narration audio for all scenes, adjusting durations to match audio."""
    results = []

    for i, scene in enumerate(scenes):
        narration_text = scene.get("narration", "")
        if not narration_text:
            results.append({
                "audio_path": None,
                "duration": scene.get("duration_seconds", 4),
            })
            continue

        filename = f"{job_id}_narration_{i + 1}.mp3"
        audio_path = generate_narration(narration_text, filename)
        audio_duration = get_audio_duration(audio_path)

        # Use the longer of: script duration or audio duration (+ small buffer)
        scene_duration = max(scene.get("duration_seconds", 4), audio_duration + 0.5)

        results.append({
            "audio_path": audio_path,
            "duration": scene_duration,
        })

    return results
