from styletts2 import tts
import torch

import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.tokenize import sent_tokenize, word_tokenize

# Fix pour le bug 'punkt_tab'
nltk.download("punkt", quiet=True)

# (Optionnel mais propre) redéfinir sent_tokenize pour éviter des bugs futurs
nltk.tokenize.sent_tokenize = lambda text, language='english': PunktSentenceTokenizer().tokenize(text)

my_tts = tts.StyleTTS2(
    model_checkpoint_path="Models/Emotion/angry_49.pth",
    config_path="Models/LibriTTS/config.yml"
)

# Générer audio
# on devra rajouter ici une variable emotion pour le style
out = my_tts.inference(
    "This violent delights have violent end.",
    target_voice_path="ears_dataset_24k/p001/emo_neutral_sentences.wav",
    diffusion_steps=100,
    alpha=0.5,
    beta=0.5,
    output_wav_file="after_finetune.wav"
)
