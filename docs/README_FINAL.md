# Spoke TTS - Configuration Finale

## Résumé du Système

Ton serveur TTS propose **2 modes** :

### 1. Voix Classiques (Fixes)
- **Voix 1** → Speaker p001
- **Voix 2** → Speaker p002
- **Voix 3** → Speaker p003
- **Voix 4** → Speaker p004

Ces voix sont toujours les mêmes, tu passes directement `speaker_id: 1, 2, 3, ou 4` à `/synthesize`.

### 2. Voix Random (par Genre)
- **Random Homme** → Tire un speaker masculin aléatoire parmi p005-p107
- **Random Femme** → Tire un speaker féminin aléatoire parmi p005-p107

Pour ces voix, tu appelles d'abord `/random_voice` pour obtenir un speaker, puis `/synthesize`.

---

## API Endpoints

### 1. GET /ping
Test de connexion basique.

### 2. GET /health
Vérification de l'état du serveur.

### 3. POST /random_voice
Obtenir un speaker aléatoire par genre.

**Request:**
```json
{
  "gender": "male"  // ou "female"
}
```

**Response:**
```json
{
  "speaker_id": "p046",
  "speaker_num": 46,
  "gender": "male",
  "description": "Male, 26 to 35 years old, White Or Caucasian, Native American English speaker",
  "profile": {
    "age": "26-35",
    "gender": "male",
    "ethnicity": "white or caucasian",
    "native language": "american english",
    "height": "6' - 6'3",
    "weight": "220 - 240 lbs"
  }
}
```

### 4. POST /synthesize
Générer de l'audio avec un speaker spécifique.

**Request:**
```json
{
  "text": "Votre texte ici",
  "emotion": "neutral",  // neutral, joy, anger, sadness, fear
  "speaker_id": 1        // 1-107
}
```

**Response:** Fichier audio WAV

---

## Code JavaScript - Copy/Paste Ready

### Configuration
```javascript
const API_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';
```

### Voix Classique (1, 2, 3, 4)
```javascript
async function synthesizeClassic(voiceNumber, text, emotion = 'neutral') {
  const response = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: voiceNumber  // 1, 2, 3, ou 4
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }

  return await response.blob();
}

// Utilisation
const audio = await synthesizeClassic(1, "Hello world", "joy");
playAudio(audio);
```

### Voix Random (Homme/Femme)
```javascript
async function synthesizeRandom(gender, text, emotion = 'neutral') {
  // Étape 1: Obtenir un speaker random
  const randomResponse = await fetch(`${API_URL}/random_voice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gender: gender })  // "male" ou "female"
  });

  const randomData = await randomResponse.json();
  const speakerNum = randomData.speaker_num;

  // Étape 2: Générer l'audio
  const synthResponse = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: speakerNum
    })
  });

  return await synthResponse.blob();
}

// Utilisation
const audio = await synthesizeRandom("female", "Hello world", "neutral");
playAudio(audio);
```

### Helper Functions
```javascript
function playAudio(audioBlob) {
  const url = URL.createObjectURL(audioBlob);
  const audio = new Audio(url);
  audio.onended = () => URL.revokeObjectURL(url);
  audio.play();
  return audio;
}

function downloadAudio(audioBlob, filename = 'speech.wav') {
  const url = URL.createObjectURL(audioBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

---

## Exemple React Complet

```jsx
import React, { useState } from 'react';

function VoiceSelector() {
  const [voiceType, setVoiceType] = useState('classic');
  const [classicVoice, setClassicVoice] = useState(1);
  const [randomGender, setRandomGender] = useState('male');
  const [text, setText] = useState('');
  const [emotion, setEmotion] = useState('neutral');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!text) return;

    setLoading(true);
    try {
      let audioBlob;

      if (voiceType === 'classic') {
        audioBlob = await synthesizeClassic(classicVoice, text, emotion);
      } else {
        audioBlob = await synthesizeRandom(randomGender, text, emotion);
      }

      playAudio(audioBlob);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Voice Selection</h2>

      {/* Type Toggle */}
      <div>
        <button onClick={() => setVoiceType('classic')}>
          Classic Voices
        </button>
        <button onClick={() => setVoiceType('random')}>
          Random Voice
        </button>
      </div>

      {/* Classic Selector */}
      {voiceType === 'classic' && (
        <select value={classicVoice} onChange={(e) => setClassicVoice(Number(e.target.value))}>
          <option value={1}>Voice 1</option>
          <option value={2}>Voice 2</option>
          <option value={3}>Voice 3</option>
          <option value={4}>Voice 4</option>
        </select>
      )}

      {/* Random Selector */}
      {voiceType === 'random' && (
        <select value={randomGender} onChange={(e) => setRandomGender(e.target.value)}>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      )}

      {/* Text Input */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
        rows={4}
      />

      {/* Emotion Selector */}
      <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
        <option value="neutral">Neutral</option>
        <option value="joy">Joy</option>
        <option value="anger">Anger</option>
        <option value="sadness">Sadness</option>
        <option value="fear">Fear</option>
      </select>

      {/* Generate Button */}
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Speech'}
      </button>
    </div>
  );
}
```

---

## Émotions Disponibles

- `neutral` - Neutre
- `joy` - Joie
- `anger` - Colère
- `sadness` - Tristesse
- `fear` - Peur

---

## Profils des Voix Classiques

### Voix 1 (p001)
- Genre: Homme
- Âge: 36-45 ans
- Ethnicité: Caucasien
- Langue native: Allemand

### Voix 2 (p002)
- Genre: Femme
- Âge: 46-55 ans
- Ethnicité: Caucasienne
- Langue native: Anglais américain

### Voix 3 (p003)
- Genre: Femme
- Âge: 26-35 ans
- Ethnicité: Afro-américaine
- Langue native: Anglais américain

### Voix 4 (p004)
- Genre: Homme
- Âge: 18-25 ans
- Ethnicité: Caucasien
- Langue native: Anglais américain

---

## Voix Random

Le système sélectionne aléatoirement parmi **103 speakers** (p005 à p107) :
- Environ **60 voix masculines**
- Environ **43 voix féminines**

Chaque appel à `/random_voice` retourne un speaker différent (aléatoire).

---

## Fichiers de Code

1. **[FINAL_INTEGRATION.js](FINAL_INTEGRATION.js)** - Code complet avec exemples React et Vanilla JS
2. **[server.py](server.py)** - Serveur Flask avec tous les endpoints
3. **[API_USAGE.md](API_USAGE.md)** - Documentation complète de l'API

---

## Gestion du Serveur

### Démarrer le serveur
```bash
./manage_server.sh start
```

### Arrêter le serveur
```bash
./manage_server.sh stop
```

### Redémarrer le serveur
```bash
./manage_server.sh restart
```

### Voir les logs
```bash
./manage_server.sh logs
```

### Statut du serveur
```bash
./manage_server.sh status
```

### Monitoring en temps réel
```bash
./monitor.sh
```

---

## URL du Serveur

**Production (HTTPS via Cloudflare Tunnel):**
```
https://thousands-violations-suspension-premiere.trycloudflare.com
```

**Note:** Cette URL Cloudflare est temporaire. Pour une URL permanente, il faudrait utiliser un domaine personnalisé ou ngrok.

---

## Tests Rapides

### Test voix classique
```bash
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "emotion": "neutral", "speaker_id": 1}' \
  --output test.wav
```

### Test voix random
```bash
# Obtenir un speaker random
curl -X POST http://localhost:5000/random_voice \
  -H "Content-Type: application/json" \
  -d '{"gender": "female"}'

# Utiliser le speaker_num retourné pour la synthèse
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "emotion": "joy", "speaker_id": 33}' \
  --output test.wav
```

---

## Notes Importantes

1. **Performance:** La génération audio prend 3-10 secondes selon la longueur du texte
2. **CORS:** Activé, donc les requêtes depuis ton site web fonctionneront
3. **Format audio:** WAV à 24kHz
4. **Limite de texte:** Pas de limite stricte, mais les textes très longs prendront plus de temps
5. **Voix random:** Chaque appel retourne un speaker différent (aléatoire)

---

## Support

En cas de problème :
- Logs: `./manage_server.sh logs`
- Monitoring: `./monitor.sh`
- Redémarrer: `./manage_server.sh restart`
