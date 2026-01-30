import sys
import os

# Add parent directory to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from styletts2 import tts
import nltk
from server.emotion_router import get_model, EMOTION_MAPPING
import torch
import torch.optim.lr_scheduler
from collections import defaultdict

# Fix pour PyTorch 2.6 - Patch torch.load pour forcer weights_only=False
_original_load = torch.load
def patched_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_load(*args, **kwargs)
torch.load = patched_load

nltk.download("punkt", quiet=True)

CONFIG_PATH = os.path.join(REPO_ROOT, "Configs/config_libritts.yml")

def synthesize(emotion, speaker_id, text, output="output.wav"):
    model_path = get_model(emotion)

    # Get the actual emotion folder name
    mapped_emotion = EMOTION_MAPPING.get(emotion.lower(), emotion.lower())

    # Check multiple possible paths
    speaker_file_options = [
        os.path.join(REPO_ROOT, f"emotions/{mapped_emotion}/{speaker_id}_emo_{mapped_emotion}_sentences.wav"),
        os.path.join(REPO_ROOT, f"emotions/{emotion}/{speaker_id}_emo_{emotion}_sentences.wav"),
    ]

    speaker_file = None
    for option in speaker_file_options:
        if os.path.exists(option):
            speaker_file = option
            break

    if speaker_file is None:
        raise FileNotFoundError(f"Speaker file not found for {speaker_id} with emotion {emotion} (mapped to {mapped_emotion})")

    engine = tts.StyleTTS2(
        model_checkpoint_path=model_path,
        config_path=CONFIG_PATH
    )

    engine.inference(
        text,
        target_voice_path=speaker_file,
        diffusion_steps=100,
        alpha=0.5,
        beta=0.5,
        output_wav_file=output
    )
