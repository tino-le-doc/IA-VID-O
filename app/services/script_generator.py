import anthropic
import json
from app.config import ANTHROPIC_API_KEY


def generate_script(prompt: str, num_scenes: int = 5) -> dict:
    """Generate a video script from a prompt using Claude."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = """Tu es un scénariste professionnel pour vidéos courtes.
À partir de l'idée donnée, génère un script vidéo structuré en scènes.

Réponds UNIQUEMENT en JSON valide avec ce format :
{
  "title": "Titre de la vidéo",
  "description": "Description courte",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "Texte de narration pour cette scène",
      "visual_prompt": "Description détaillée en anglais de l'image à générer pour cette scène",
      "duration_seconds": 4
    }
  ]
}

Règles :
- Génère exactement le nombre de scènes demandé
- Les visual_prompt doivent être en anglais, détaillés et descriptifs (style, couleurs, composition)
- La narration doit être en français
- Chaque scène dure entre 3 et 6 secondes"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"Crée un script vidéo de {num_scenes} scènes sur le thème : {prompt}",
            }
        ],
        system=system_prompt,
    )

    response_text = message.content[0].text

    # Extract JSON from response
    try:
        script = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            script = json.loads(response_text[start:end])
        else:
            raise ValueError("Could not parse script from Claude response")

    return script
