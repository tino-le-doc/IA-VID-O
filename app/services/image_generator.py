import httpx
import urllib.parse
from pathlib import Path
from app.config import IMAGES_DIR


async def generate_image(prompt: str, filename: str, width: int = 1280, height: int = 720) -> Path:
    """Generate an image using Pollinations.ai (free, no API key needed)."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

    output_path = IMAGES_DIR / filename

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        output_path.write_bytes(response.content)

    return output_path
