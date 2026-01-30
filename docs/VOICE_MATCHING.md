# Voice Matching API

## Overview

Le système de matching vocal permet de trouver automatiquement les 4 meilleures voix parmi les 107 speakers disponibles, basé sur une description en langage naturel.

## Endpoint

**POST** `/match_voice`

## Request Body

```json
{
  "prompt": "description de la voix souhaitée"
}
```

## Response

```json
{
  "matches": [
    {
      "speaker_id": "p032",
      "speaker_num": 32,
      "score": 10.3,
      "description": "Female, 56 to 65 years old, White Or Caucasian, Native American English speaker",
      "profile": {
        "age": "56-65",
        "ethnicity": "white or caucasian",
        "gender": "female",
        "weight": "160 - 180 lbs",
        "native language": "american english",
        "height": "5'8 - 5'11"
      }
    },
    ...
  ],
  "speaker_ids": ["p032", "p011", "p028", "p035"],
  "speaker_nums": [32, 11, 28, 35]
}
```

## Keywords Supportés

### Âge
- **young/youth/teen** → 18-25 ans
- **adult** → 26-45 ans
- **middle/mature** → 36-65 ans
- **old/elderly/senior** → 56-75 ans

### Genre
- **male/man/masculine** → voix masculine
- **female/woman/feminine** → voix féminine
- **neutral** → voix non-binaire

### Ethnicité
- **white/caucasian** → Blanc/Caucasien
- **black/african** → Noir/Afro-américain
- **hispanic/latino** → Hispanique/Latino
- **asian** → Asiatique

### Langue Maternelle
- **american/english** → Anglais américain
- **british** → Anglais britannique
- **spanish** → Espagnol
- **german** → Allemand
- **french** → Français
- **mandarin** → Mandarin
- **russian** → Russe

### Qualité Vocale (descriptifs)
- **deep** → Voix grave (généralement masculine, mature)
- **soft** → Voix douce (généralement féminine, jeune)
- **authoritative** → Voix autoritaire (mature)
- **gentle** → Voix douce/gentille
- **energetic** → Voix énergique (jeune)
- **calm** → Voix calme
- **powerful** → Voix puissante
- **warm** → Voix chaleureuse

## Exemples d'Utilisation

### Exemple 1: Jeune voix féminine

```bash
curl -X POST https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I need a young female voice with an American accent"
  }'
```

**Résultat**: Retourne des speakers féminins de 18-35 ans avec accent américain

### Exemple 2: Voix masculine autoritaire

```bash
curl -X POST https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Looking for a mature male voice, authoritative"
  }'
```

**Résultat**: Retourne des speakers masculins de 46-65 ans

### Exemple 3: Voix douce et féminine

```bash
curl -X POST https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Soft feminine young voice"
  }'
```

**Résultat**: Retourne des speakers féminins jeunes

### Exemple 4: Voix puissante et grave

```bash
curl -X POST https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Deep powerful male voice"
  }'
```

**Résultat**: Retourne des speakers masculins de 36-65 ans

## Utilisation depuis JavaScript

```javascript
async function matchVoice(description) {
  const response = await fetch('https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: description
    })
  });

  const data = await response.json();
  return data;
}

// Exemple d'utilisation
const result = await matchVoice("young energetic female voice");
console.log("Top speakers:", result.speaker_nums); // [11, 28, 35, 56]

// Utiliser le premier speaker pour la synthèse
const bestSpeaker = result.speaker_nums[0];
```

## Workflow Complet

1. **Obtenir les voix matchées**
   ```javascript
   const matches = await matchVoice("gentle mature female voice");
   const topSpeaker = matches.speaker_nums[0]; // Meilleur match
   ```

2. **Générer l'audio avec le speaker trouvé**
   ```javascript
   const audioResponse = await fetch('https://thousands-violations-suspension-premiere.trycloudflare.com/synthesize', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       text: "Hello, this is a test",
       emotion: "joy",
       speaker_id: topSpeaker
     })
   });

   const audioBlob = await audioResponse.blob();
   ```

## Score System

Le système attribue des points selon les critères :
- **Genre** : 4 points (critère le plus important)
- **Âge** : 3 points
- **Langue** : 3 points
- **Ethnicité** : 2 points
- **Qualité vocale** : 0.5 points (bonus)
- **Accent américain** : 0.3 points (bonus pour la langue la plus commune)

Plus le score est élevé, meilleur est le match.

## Notes

- Le système retourne toujours 4 voix, même si certaines ont des scores faibles
- Les profils "prefer not to answer" reçoivent une pénalité de -2 points
- Vous pouvez combiner plusieurs mots-clés dans un même prompt pour affiner les résultats
- Le matching est insensible à la casse
