import httpx
from pathlib import Path
from app.config import MUSIC_DIR, AUDIO_DIR

# Free ambient music URLs from Pixabay (royalty-free)
MUSIC_TRACKS = {
    "ambient": "https://cdn.pixabay.com/audio/2024/11/28/audio_3a29f68498.mp3",
    "upbeat": "https://cdn.pixabay.com/audio/2024/09/10/audio_6e4e1c50e2.mp3",
    "cinematic": "https://cdn.pixabay.com/audio/2024/10/07/audio_44b0fee24e.mp3",
}

DEFAULT_MOOD = "ambient"


async def download_music(mood: str = DEFAULT_MOOD) -> Path:
    """Download a royalty-free music track based on mood."""
    mood = mood if mood in MUSIC_TRACKS else DEFAULT_MOOD
    filename = f"bg_{mood}.mp3"
    output_path = MUSIC_DIR / filename

    # Use cached version if available
    if output_path.exists() and output_path.stat().st_size > 0:
        return output_path

    url = MUSIC_TRACKS[mood]
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        output_path.write_bytes(response.content)

    return output_path
