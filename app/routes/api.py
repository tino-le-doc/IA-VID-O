import asyncio
import uuid
import traceback
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse

from app.models import GenerateRequest, VideoStatus
from app.services.script_generator import generate_script
from app.services.image_generator import generate_image
from app.services.video_assembler import assemble_video
from app.services.tts_generator import generate_all_narrations
from app.services.subtitle_generator import generate_srt
from app.services.music_provider import download_music
from app.config import VIDEOS_DIR

router = APIRouter(prefix="/api")

# In-memory job storage
jobs: dict[str, VideoStatus] = {}


def update_job(job_id: str, **kwargs):
    if job_id in jobs:
        for k, v in kwargs.items():
            setattr(jobs[job_id], k, v)


async def process_video(
    job_id: str,
    prompt: str,
    num_scenes: int,
    enable_narration: bool,
    enable_subtitles: bool,
    enable_music: bool,
    music_mood: str,
):
    """Background task to generate the full video pipeline."""
    try:
        # Step 1: Generate script
        update_job(job_id, status="generating_script", progress=5, message="Génération du script avec Claude...")
        script = generate_script(prompt, num_scenes)
        update_job(job_id, script=script, progress=15, message="Script généré !")

        scenes = script.get("scenes", [])

        # Step 2: Generate narration audio (TTS)
        narration_paths = [None] * len(scenes)
        durations = [s.get("duration_seconds", 4) for s in scenes]

        if enable_narration:
            update_job(job_id, status="generating_narration", progress=18, message="Génération de la narration audio...")
            narration_results = generate_all_narrations(scenes, job_id)
            narration_paths = [r["audio_path"] for r in narration_results]
            durations = [r["duration"] for r in narration_results]

        # Step 3: Generate images for each scene
        update_job(job_id, status="generating_images", progress=25, message="Génération des images...")
        image_paths: list[Path] = []

        for i, scene in enumerate(scenes):
            progress = 25 + int((i / len(scenes)) * 40)
            update_job(job_id, progress=progress, message=f"Génération image {i + 1}/{len(scenes)}...")
            filename = f"{job_id}_scene_{i + 1}.jpg"
            path = await generate_image(scene["visual_prompt"], filename)
            image_paths.append(path)

        # Step 4: Generate subtitles
        subtitle_path = None
        if enable_subtitles:
            update_job(job_id, progress=68, message="Génération des sous-titres...")
            subtitle_path = generate_srt(scenes, durations, job_id)

        # Step 5: Download background music
        music_path = None
        if enable_music:
            update_job(job_id, status="downloading_music", progress=72, message="Téléchargement de la musique de fond...")
            music_path = await download_music(music_mood)

        # Step 6: Assemble final video
        update_job(job_id, status="assembling_video", progress=78, message="Assemblage de la vidéo finale...")
        video_name = f"{job_id}.mp4"
        video_path = assemble_video(
            image_paths=image_paths,
            durations=durations,
            output_name=video_name,
            narration_paths=narration_paths,
            subtitle_path=subtitle_path,
            music_path=music_path,
        )

        update_job(
            job_id,
            status="done",
            progress=100,
            message="Vidéo terminée !",
            video_url=f"/api/video/{job_id}",
        )

    except Exception as e:
        traceback.print_exc()
        update_job(job_id, status="error", message=f"Erreur : {str(e)}")


@router.post("/generate")
async def generate_video(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Start video generation pipeline."""
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = VideoStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Démarrage...",
    )
    background_tasks.add_task(
        process_video,
        job_id,
        req.prompt,
        req.num_scenes,
        req.enable_narration,
        req.enable_subtitles,
        req.enable_music,
        req.music_mood,
    )
    return {"job_id": job_id}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a video generation job."""
    if job_id not in jobs:
        return {"error": "Job not found"}, 404
    return jobs[job_id]


@router.get("/video/{job_id}")
async def get_video(job_id: str):
    """Download the generated video."""
    video_path = VIDEOS_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        return {"error": "Video not found"}, 404
    return FileResponse(video_path, media_type="video/mp4", filename=f"{job_id}.mp4")
