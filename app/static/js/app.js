const form = document.getElementById('generate-form');
const promptInput = document.getElementById('prompt');
const numScenesInput = document.getElementById('num-scenes');
const scenesCount = document.getElementById('scenes-count');
const generateBtn = document.getElementById('generate-btn');

const inputSection = document.getElementById('input-section');
const progressSection = document.getElementById('progress-section');
const scriptSection = document.getElementById('script-section');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');

const progressFill = document.getElementById('progress-fill');
const progressMessage = document.getElementById('progress-message');
const progressPercent = document.getElementById('progress-percent');

// Update scenes count display
numScenesInput.addEventListener('input', () => {
    scenesCount.textContent = numScenesInput.value;
});

// Form submit
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const prompt = promptInput.value.trim();
    if (!prompt) return;

    generateBtn.disabled = true;
    progressSection.classList.remove('hidden');
    scriptSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    try {
        // Start generation
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                num_scenes: parseInt(numScenesInput.value),
                enable_narration: document.getElementById('enable-narration').checked,
                enable_subtitles: document.getElementById('enable-subtitles').checked,
                enable_music: document.getElementById('enable-music').checked,
                music_mood: document.getElementById('music-mood').value,
            }),
        });

        const data = await res.json();
        const jobId = data.job_id;

        // Poll for status
        pollStatus(jobId);
    } catch (err) {
        showError(err.message);
    }
});

async function pollStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${jobId}`);
            const status = await res.json();

            // Update progress
            progressFill.style.width = status.progress + '%';
            progressMessage.textContent = status.message;
            progressPercent.textContent = status.progress + '%';

            // Show script when available
            if (status.script) {
                showScript(status.script);
            }

            // Check if done
            if (status.status === 'done') {
                clearInterval(interval);
                showResult(status.video_url);
                generateBtn.disabled = false;
            } else if (status.status === 'error') {
                clearInterval(interval);
                showError(status.message);
                generateBtn.disabled = false;
            }
        } catch (err) {
            clearInterval(interval);
            showError(err.message);
            generateBtn.disabled = false;
        }
    }, 2000);
}

function showScript(script) {
    scriptSection.classList.remove('hidden');
    document.getElementById('script-title').textContent = script.title || 'Script';
    document.getElementById('script-description').textContent = script.description || '';

    const scenesList = document.getElementById('scenes-list');
    scenesList.innerHTML = '';

    (script.scenes || []).forEach((scene) => {
        const div = document.createElement('div');
        div.className = 'scene-card';
        div.innerHTML = `
            <div class="scene-number">Scène ${scene.scene_number}</div>
            <div class="narration">${scene.narration}</div>
            <div class="visual">${scene.visual_prompt}</div>
        `;
        scenesList.appendChild(div);
    });
}

function showResult(videoUrl) {
    progressSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    const video = document.getElementById('result-video');
    video.src = videoUrl;

    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.href = videoUrl;
}

function showError(message) {
    progressSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    document.getElementById('error-message').textContent = message;
    generateBtn.disabled = false;
}

function resetUI() {
    progressSection.classList.add('hidden');
    scriptSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

// Toggle music mood selector visibility
const enableMusicCheckbox = document.getElementById('enable-music');
const musicMoodGroup = document.getElementById('music-mood-group');

enableMusicCheckbox.addEventListener('change', () => {
    musicMoodGroup.style.display = enableMusicCheckbox.checked ? 'block' : 'none';
});
