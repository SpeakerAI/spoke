import os
import json

base_audio_dir = "ears_dataset_24k"
transcript_json = os.path.join(base_audio_dir, "transcripts.json")
output_json = "metadata.json"

with open(transcript_json, "r") as f:
    transcripts = json.load(f)

entries = []
for speaker in os.listdir(base_audio_dir):
    speaker_dir = os.path.join(base_audio_dir, speaker)
    if not os.path.isdir(speaker_dir):
        continue
    for wav in os.listdir(speaker_dir):
        if not wav.endswith(".wav"):
            continue
        key = wav[:-4]
        # Filtre uniquement les emo_*_sentences
        if not key.startswith("emo_") or not key.endswith("_sentences"):
            continue
        if key not in transcripts:
            print(f"WARNING: No transcript for {wav}")
            continue
        transcript = transcripts[key].strip().replace("\n", " ")
        # L’émotion est ce qu’il y a entre "emo_" et "_sentences"
        emotion = key[len("emo_") : -len("_sentences")]
        abs_path = os.path.join(base_audio_dir, speaker, wav)
        entries.append({
            "audio_path": abs_path,
            "transcript": transcript,
            "speaker": speaker,
            "emotion": emotion
        })

with open(output_json, "w") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"metadata.json généré ({len(entries)} entrées)")

