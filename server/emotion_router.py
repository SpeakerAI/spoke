import os
import glob

# Get repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMOTION_MAPPING = {
    "anger": "anger",
    "sadness": "sadness",
    "joy": "amusement",
    "fear": "fear",
    "neutral": "contentment",
    "amusement": "amusement",
    "contentment": "contentment",
    "adoration": "adoration",
    "amazement": "amazement",
    "confusion": "confusion",
    "cuteness": "cuteness",
    "desire": "desire",
    "disappointment": "disappointment",
    "disgust": "disgust",
    "distress": "distress",
    "embarassment": "embarassment",
    "extasy": "extasy",
    "guilt": "guilt",
    "interest": "interest",
    "pain": "pain",
    "pride": "pride"
}

def get_model(emotion: str) -> str:
    emotion = emotion.lower()

    if emotion not in EMOTION_MAPPING:
        raise ValueError(f"Unsupported emotion: {emotion}. Available: {', '.join(EMOTION_MAPPING.keys())}")

    mapped_emotion = EMOTION_MAPPING[emotion]
    emotion_dir = os.path.join(REPO_ROOT, f"emotions/{mapped_emotion}")

    if not os.path.exists(emotion_dir):
        raise FileNotFoundError(f"Emotion directory not found: {emotion_dir}")

    model_files = glob.glob(os.path.join(emotion_dir, "*.pth"))

    if not model_files:
        raise FileNotFoundError(f"No model file found in {emotion_dir}")

    return model_files[0]
