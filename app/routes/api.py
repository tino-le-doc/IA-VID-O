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
from app.config import VIDEOS_DIR

router = APIRouter(prefix="/api")

# In-memory job storage
jobs: dict[str, VideoStatus] = {}


def update_job(job_id: str, **kwargs):
    if job_id in jobs:
        for k, v in kwargs.items():
            setattr(jobs[job_id], k, v)


async def process_video(job_id: str, prompt: str, num_scenes: int):
    """Background task to generate the full video pipeline."""
    try:
        # Step 1: Generate script
        update_job(job_id, status="generating_script", progress=10, message="Génération du script avec Claude...")
        script = generate_script(prompt, num_scenes)
        update_job(job_id, script=script, progress=20, message="Script généré !")

        # Step 2: Generate images for each scene
        update_job(job_id, status="generating_images", progress=25, message="Génération des images...")
        scenes = script.get("scenes", [])
        image_paths: list[Path] = []
        durations: list[int] = []

        for i, scene in enumerate(scenes):
            progress = 25 + int((i / len(scenes)) * 50)
            update_job(
                job_id,
                progress=progress,
                message=f"Génération image {i + 1}/{len(scenes)}...",
            )
            filename = f"{job_id}_scene_{i + 1}.jpg"
            path = await generate_image(scene["visual_prompt"], filename)
            image_paths.append(path)
            durations.append(scene.get("duration_seconds", 4))

        # Step 3: Assemble video
        update_job(job_id, status="assembling_video", progress=80, message="Assemblage de la vidéo...")
        video_name = f"{job_id}.mp4"
        video_path = assemble_video(image_paths, durations, video_name)

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
    background_tasks.add_task(process_video, job_id, req.prompt, req.num_scenes)
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
