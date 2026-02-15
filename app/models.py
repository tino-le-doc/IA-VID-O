from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    num_scenes: int = 5
    enable_narration: bool = True
    enable_subtitles: bool = True
    enable_music: bool = True
    music_mood: str = "ambient"  # ambient, upbeat, cinematic


class SceneResponse(BaseModel):
    scene_number: int
    narration: str
    visual_prompt: str
    duration_seconds: int


class ScriptResponse(BaseModel):
    title: str
    description: str
    scenes: list[SceneResponse]


class VideoStatus(BaseModel):
    job_id: str
    status: str  # pending, generating_script, generating_images, assembling_video, done, error
    progress: int  # 0-100
    message: str
    script: dict | None = None
    video_url: str | None = None
