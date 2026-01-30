"""
Voice Matcher - Match user prompts to speaker profiles
Uses speaker_statistics.json to find the best matching voices
"""

import json
import re
import os
from typing import List, Dict, Tuple

# Get repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load speaker data
with open(os.path.join(REPO_ROOT, 'speaker_statistics.json'), 'r') as f:
    SPEAKERS = json.load(f)

# Keyword mappings for matching
AGE_KEYWORDS = {
    'young': ['18-25', '26-35'],
    'youth': ['18-25'],
    'teen': ['18-25'],
    'adult': ['26-35', '36-45'],
    'middle': ['36-45', '46-55'],
    'mature': ['46-55', '56-65'],
    'old': ['56-65', '66-75'],
    'elderly': ['66-75'],
    'senior': ['66-75']
}

GENDER_KEYWORDS = {
    'male': ['male'],
    'man': ['male'],
    'masculine': ['male'],
    'female': ['female'],
    'woman': ['female'],
    'feminine': ['female'],
    'neutral': ['non-binary / third gender', 'prefer not to answer']
}

ETHNICITY_KEYWORDS = {
    'white': ['white or caucasian'],
    'caucasian': ['white or caucasian'],
    'black': ['black or african american'],
    'african': ['black or african american'],
    'hispanic': ['hispanic or latino'],
    'latino': ['hispanic or latino'],
    'asian': ['asian']
}

LANGUAGE_KEYWORDS = {
    'american': ['american english'],
    'english': ['american english', 'british english'],
    'british': ['british english'],
    'spanish': ['spanish'],
    'german': ['german'],
    'french': ['french'],
    'mandarin': ['mandarin'],
    'russian': ['russian'],
    'ukrainian': ['ukrainian'],
    'dari': ['dari']
}

# Voice quality keywords (soft scoring)
VOICE_QUALITY = {
    'deep': {'gender': 'male', 'age': ['36-45', '46-55', '56-65']},
    'soft': {'gender': 'female', 'age': ['18-25', '26-35']},
    'authoritative': {'gender': 'male', 'age': ['46-55', '56-65']},
    'gentle': {'gender': 'female', 'age': ['26-35', '36-45']},
    'energetic': {'age': ['18-25', '26-35']},
    'calm': {'age': ['36-45', '46-55']},
    'powerful': {'gender': 'male', 'age': ['36-45', '46-55', '56-65']},
    'warm': {'gender': 'female', 'age': ['36-45', '46-55']}
}


def extract_keywords(prompt: str) -> Dict[str, List[str]]:
    """
    Extract matching keywords from user prompt
    Returns dict with categories: age, gender, ethnicity, language, quality
    """
    prompt_lower = prompt.lower()
    extracted = {
        'age': [],
        'gender': [],
        'ethnicity': [],
        'language': [],
        'quality': []
    }

    # Match age keywords
    for keyword, ages in AGE_KEYWORDS.items():
        if keyword in prompt_lower:
            extracted['age'].extend(ages)

    # Match gender keywords
    for keyword, genders in GENDER_KEYWORDS.items():
        if keyword in prompt_lower:
            extracted['gender'].extend(genders)

    # Match ethnicity keywords
    for keyword, ethnicities in ETHNICITY_KEYWORDS.items():
        if keyword in prompt_lower:
            extracted['ethnicity'].extend(ethnicities)

    # Match language keywords
    for keyword, languages in LANGUAGE_KEYWORDS.items():
        if keyword in prompt_lower:
            extracted['language'].extend(languages)

    # Match voice quality keywords
    for keyword, criteria in VOICE_QUALITY.items():
        if keyword in prompt_lower:
            extracted['quality'].append(keyword)
            # Add indirect criteria from quality
            if 'gender' in criteria and criteria['gender'] not in extracted['gender']:
                extracted['gender'].append(criteria['gender'])
            if 'age' in criteria:
                extracted['age'].extend(criteria['age'])

    # Remove duplicates
    for key in extracted:
        extracted[key] = list(set(extracted[key]))

    return extracted


def score_speaker(speaker_id: str, speaker_data: Dict, keywords: Dict[str, List[str]]) -> float:
    """
    Score a speaker based on how well they match the keywords
    Higher score = better match
    """
    score = 0.0

    # Age matching (weight: 3)
    if keywords['age']:
        if speaker_data['age'] in keywords['age']:
            score += 3.0

    # Gender matching (weight: 4)
    if keywords['gender']:
        if speaker_data['gender'] in keywords['gender']:
            score += 4.0

    # Ethnicity matching (weight: 2)
    if keywords['ethnicity']:
        if speaker_data['ethnicity'] in keywords['ethnicity']:
            score += 2.0

    # Language matching (weight: 3)
    if keywords['language']:
        if speaker_data['native language'] in keywords['language']:
            score += 3.0

    # Quality keywords (already factored into age/gender)
    # Add small bonus if quality keywords were used
    if keywords['quality']:
        score += 0.5

    # Bonus for American English speakers (most common)
    if speaker_data['native language'] == 'american english':
        score += 0.3

    # Penalty for "prefer not to answer" profiles
    if speaker_data['age'] == 'prefer not to answer':
        score -= 2.0

    return score


def match_voices(prompt: str, top_n: int = 4) -> List[Dict[str, any]]:
    """
    Match user prompt to best speaker profiles
    Returns list of top N speakers with their IDs and scores
    """
    keywords = extract_keywords(prompt)

    # Score all speakers
    scored_speakers = []
    for speaker_id, speaker_data in SPEAKERS.items():
        score = score_speaker(speaker_id, speaker_data, keywords)
        scored_speakers.append({
            'speaker_id': speaker_id,
            'score': score,
            'profile': speaker_data
        })

    # Sort by score (descending)
    scored_speakers.sort(key=lambda x: x['score'], reverse=True)

    # Return top N
    return scored_speakers[:top_n]


def match_voices_simple(prompt: str) -> List[str]:
    """
    Simple version that just returns the top 4 speaker IDs
    """
    matches = match_voices(prompt, top_n=4)
    return [match['speaker_id'] for match in matches]


def get_voice_description(speaker_id: str) -> str:
    """
    Generate a human-readable description of a speaker
    """
    if speaker_id not in SPEAKERS:
        return "Unknown speaker"

    data = SPEAKERS[speaker_id]

    # Handle prefer not to answer
    if data['age'] == 'prefer not to answer':
        return f"Speaker {speaker_id} (Profile private)"

    # Build description
    age = data['age'].replace('-', ' to ')
    gender = data['gender'].title()
    ethnicity = data['ethnicity'].title()
    language = data['native language'].title()

    return f"{gender}, {age} years old, {ethnicity}, Native {language} speaker"


# Test examples
if __name__ == "__main__":
    test_prompts = [
        "I need a young female voice with an American accent",
        "Looking for a mature male voice, authoritative",
        "Gentle female voice, middle-aged",
        "Deep powerful male voice",
        "Soft feminine young voice"
    ]

    print("Voice Matcher Test Results\n" + "="*50)
    for prompt in test_prompts:
        print(f"\nPrompt: '{prompt}'")
        matches = match_voices(prompt, top_n=4)
        print(f"Top 4 matches:")
        for i, match in enumerate(matches, 1):
            desc = get_voice_description(match['speaker_id'])
            print(f"  {i}. {match['speaker_id']} (score: {match['score']:.1f}) - {desc}")
