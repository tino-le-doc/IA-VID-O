# IA-VID-O

Générateur de vidéos par IA. Décris ton idée, l'IA crée le script, génère les images et assemble le tout en vidéo.

## Stack

- **Backend** : Python / FastAPI
- **Script IA** : Anthropic Claude API
- **Images** : Pollinations.ai (gratuit, pas de clé API)
- **Vidéo** : FFmpeg (assemblage des images)
- **Frontend** : HTML/CSS/JS

## Installation

```bash
# Cloner le repo
git clone https://github.com/tino-le-doc/IA-VID-O.git
cd IA-VID-O

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec ta clé API Anthropic
```

## Prérequis

- Python 3.11+
- FFmpeg installé (`sudo apt install ffmpeg` ou `brew install ffmpeg`)
- Une clé API Anthropic (pour la génération de scripts)

## Lancement

```bash
python run.py
```

L'app sera disponible sur `http://localhost:8000`

## Fonctionnement

1. Tu entres un prompt décrivant ta vidéo
2. Claude génère un script structuré en scènes
3. Chaque scène est transformée en image via Pollinations.ai
4. Les images sont assemblées en vidéo MP4 avec FFmpeg
5. Tu peux prévisualiser et télécharger la vidéo
