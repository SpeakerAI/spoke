# Spoke TTS Server API

Le serveur Spoke TTS est maintenant en cours d'exécution et prêt à recevoir des requêtes de votre site web.

## Adresse du serveur

```
http://51.210.165.192:5000
```

## Endpoints disponibles

### 1. Ping - Test de connexion
Vérifier que le serveur est accessible.

**Méthode:** `GET`
**URL:** `/ping`

**Exemple avec fetch (JavaScript):**
```javascript
fetch('http://51.210.165.192:5000/ping')
  .then(response => response.json())
  .then(data => console.log(data))
```

**Réponse:**
```json
{
  "status": "success",
  "message": "Spoke TTS server is running"
}
```

---

### 2. Health Check - État du serveur
Vérifier la santé du serveur.

**Méthode:** `GET`
**URL:** `/health`

**Exemple avec fetch (JavaScript):**
```javascript
fetch('http://51.210.165.192:5000/health')
  .then(response => response.json())
  .then(data => console.log(data))
```

**Réponse:**
```json
{
  "status": "healthy",
  "service": "Spoke TTS"
}
```

---

### 3. Match Voice - Trouver les meilleures voix
Trouve automatiquement les 4 meilleures voix parmi les 107 speakers disponibles selon une description en langage naturel.

**Méthode:** `POST`
**URL:** `/match_voice`
**Content-Type:** `application/json`

**Paramètres requis:**
- `prompt` (string) - Description de la voix souhaitée (âge, genre, qualités vocales, etc.)

**Mots-clés supportés:**
- **Âge:** young, teen, adult, middle, mature, old, elderly, senior
- **Genre:** male, man, masculine, female, woman, feminine, neutral
- **Ethnicité:** white, caucasian, black, african, hispanic, latino, asian
- **Langue:** american, english, british, spanish, german, french, mandarin, russian
- **Qualité:** deep, soft, authoritative, gentle, energetic, calm, powerful, warm

**Exemple avec fetch (JavaScript):**
```javascript
fetch('https://thousands-violations-suspension-premiere.trycloudflare.com/match_voice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: "young energetic female voice with American accent"
  })
})
.then(response => response.json())
.then(data => {
  console.log("Meilleurs speakers:", data.speaker_nums); // [3, 4, 9, 11]
  console.log("Descriptions:", data.matches);

  // Utiliser le premier speaker pour la synthèse
  const bestSpeaker = data.speaker_nums[0];
})
```

**Réponse:**
```json
{
  "matches": [
    {
      "speaker_id": "p003",
      "speaker_num": 3,
      "score": 10.8,
      "description": "Female, 26 to 35 years old, Black Or African American, Native American English speaker",
      "profile": {
        "age": "26-35",
        "gender": "female",
        "ethnicity": "black or african american",
        "native language": "american english",
        "height": "5'4 - 5'7",
        "weight": "100 - 120 lbs"
      }
    },
    ...
  ],
  "speaker_ids": ["p003", "p004", "p009", "p011"],
  "speaker_nums": [3, 4, 9, 11]
}
```

**Documentation complète:** Voir [VOICE_MATCHING.md](VOICE_MATCHING.md) pour plus de détails et d'exemples.

---

### 4. Synthesize - Générer de la parole
Générer un fichier audio à partir de texte avec une émotion et un locuteur spécifiés.

**Méthode:** `POST`
**URL:** `/synthesize`
**Content-Type:** `application/json`

**Paramètres requis:**
- `text` (string) - Le texte à synthétiser
- `emotion` (string) - L'émotion désirée (voir liste ci-dessous)
- `speaker_id` (number) - ID du locuteur entre 1 et 107

**Émotions disponibles:**
- `anger` - Colère
- `sadness` - Tristesse
- `joy` - Joie (mappé à "amusement")
- `fear` - Peur
- `neutral` - Neutre (mappé à "contentment")
- `amusement` - Amusement
- `contentment` - Contentement
- `adoration` - Adoration
- `amazement` - Émerveillement
- `confusion` - Confusion
- `cuteness` - Mignonnerie
- `desire` - Désir
- `disappointment` - Déception
- `disgust` - Dégoût
- `distress` - Détresse
- `embarassment` - Embarras
- `extasy` - Extase
- `guilt` - Culpabilité
- `interest` - Intérêt
- `pain` - Douleur
- `pride` - Fierté

**Exemple avec fetch (JavaScript):**
```javascript
fetch('http://51.210.165.192:5000/synthesize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: "Hello world, this is a test of the text to speech system.",
    emotion: "neutral",
    speaker_id: 1
  })
})
.then(response => response.blob())
.then(audioBlob => {
  // Créer une URL pour l'audio
  const audioUrl = URL.createObjectURL(audioBlob);

  // Jouer l'audio
  const audio = new Audio(audioUrl);
  audio.play();

  // Ou télécharger le fichier
  const a = document.createElement('a');
  a.href = audioUrl;
  a.download = 'speech.wav';
  a.click();
})
.catch(error => console.error('Erreur:', error));
```

**Exemple avec curl:**
```bash
curl -X POST http://51.210.165.192:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "emotion": "neutral", "speaker_id": 1}' \
  --output output.wav
```

**Exemple avec Python:**
```python
import requests

response = requests.post('http://51.210.165.192:5000/synthesize',
    json={
        'text': 'Hello world',
        'emotion': 'neutral',
        'speaker_id': 1
    }
)

if response.status_code == 200:
    with open('output.wav', 'wb') as f:
        f.write(response.content)
    print("Audio saved to output.wav")
else:
    print(f"Error: {response.json()}")
```

**Réponse en cas de succès:**
Le serveur retourne un fichier audio WAV (format audio/wav) qui peut être joué ou téléchargé.

**Réponses d'erreur:**

400 Bad Request - Paramètres manquants ou invalides:
```json
{
  "error": "Missing 'text' parameter"
}
```

404 Not Found - Fichier de locuteur ou d'émotion non trouvé:
```json
{
  "error": "Speaker or emotion file not found: ..."
}
```

500 Internal Server Error - Erreur pendant la synthèse:
```json
{
  "error": "Synthesis failed: ..."
}
```

---

## Exemple d'utilisation complet dans une page HTML

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Spoke TTS Demo</title>
</head>
<body>
    <h1>Spoke TTS Demo</h1>

    <textarea id="text" rows="4" cols="50" placeholder="Entrez le texte à synthétiser..."></textarea><br>

    <select id="emotion">
        <option value="neutral">Neutre</option>
        <option value="joy">Joie</option>
        <option value="anger">Colère</option>
        <option value="sadness">Tristesse</option>
        <option value="fear">Peur</option>
    </select>

    <input type="number" id="speaker" min="1" max="107" value="1" placeholder="Speaker ID (1-107)">

    <button onclick="synthesize()">Générer la parole</button>

    <div id="status"></div>
    <audio id="audioPlayer" controls style="display:none;"></audio>

    <script>
        async function synthesize() {
            const text = document.getElementById('text').value;
            const emotion = document.getElementById('emotion').value;
            const speaker_id = parseInt(document.getElementById('speaker').value);
            const status = document.getElementById('status');
            const audioPlayer = document.getElementById('audioPlayer');

            if (!text) {
                status.textContent = 'Veuillez entrer du texte';
                return;
            }

            status.textContent = 'Génération en cours...';
            audioPlayer.style.display = 'none';

            try {
                const response = await fetch('http://51.210.165.192:5000/synthesize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text, emotion, speaker_id })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Erreur de synthèse');
                }

                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);

                audioPlayer.src = audioUrl;
                audioPlayer.style.display = 'block';
                status.textContent = 'Audio généré avec succès!';
            } catch (error) {
                status.textContent = `Erreur: ${error.message}`;
                console.error(error);
            }
        }
    </script>
</body>
</html>
```

## Notes importantes

1. **CORS**: Le serveur est configuré avec CORS activé, donc les requêtes depuis votre site web fonctionneront.

2. **Performance**: La génération audio peut prendre quelques secondes selon la longueur du texte.

3. **Format audio**: Les fichiers sont générés en format WAV à 24kHz.

4. **Limites**:
   - speaker_id doit être entre 1 et 107
   - Le texte ne doit pas être vide
   - L'émotion doit être dans la liste des émotions disponibles

## Démarrage du serveur

Pour démarrer le serveur manuellement:
```bash
cd /home/ubuntu/spoke
env/bin/python server.py
```

Le serveur sera accessible sur `http://51.210.165.192:5000`
