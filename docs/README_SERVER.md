# Spoke TTS Server - Guide Complet

Bienvenue! Ce serveur permet de générer de la parole synthétique avec différentes émotions via une API HTTP.

## 🚀 Démarrage Rapide

### Statut actuel du serveur

```bash
./manage_server.sh status
```

### Démarrer le serveur

```bash
./manage_server.sh start
```

Le serveur sera accessible sur:
- **URL publique:** `http://51.210.165.192:5000`
- **URL locale:** `http://localhost:5000`

### Tester depuis votre site web

```javascript
// Test de connexion
fetch('http://51.210.165.192:5000/ping')
  .then(response => response.json())
  .then(data => console.log(data))

// Générer un audio
fetch('http://51.210.165.192:5000/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "Bonjour, ceci est un test",
    emotion: "neutral",
    speaker_id: 1
  })
})
.then(response => response.blob())
.then(audioBlob => {
  const audio = new Audio(URL.createObjectURL(audioBlob));
  audio.play();
})
```

---

## 📚 Documentation

### Fichiers disponibles

| Fichier | Description |
|---------|-------------|
| [API_USAGE.md](API_USAGE.md) | Documentation complète de l'API avec exemples |
| [MONITORING.md](MONITORING.md) | Guide de monitoring et gestion du serveur |
| [manage_server.sh](manage_server.sh) | Script de gestion du serveur |
| [monitor.sh](monitor.sh) | Dashboard de monitoring en temps réel |
| [view_logs.sh](view_logs.sh) | Visualisation des logs |

---

## 🛠️ Commandes Essentielles

### Gestion du serveur

```bash
# Démarrer
./manage_server.sh start

# Arrêter
./manage_server.sh stop

# Redémarrer
./manage_server.sh restart

# Voir le statut
./manage_server.sh status
```

### Monitoring

```bash
# Dashboard temps réel (Ctrl+C pour quitter)
./monitor.sh

# Voir les logs en direct
./manage_server.sh logs

# Voir les statistiques
./manage_server.sh stats
```

---

## 🎯 Endpoints API

### 1. GET /ping
Test de connexion

**Réponse:**
```json
{"status": "success", "message": "Spoke TTS server is running"}
```

### 2. GET /health
État du serveur

**Réponse:**
```json
{"status": "healthy", "service": "Spoke TTS"}
```

### 3. POST /synthesize
Génération audio

**Paramètres:**
- `text` (string) - Texte à synthétiser
- `emotion` (string) - Émotion (anger, sadness, joy, fear, neutral, etc.)
- `speaker_id` (number) - ID du speaker (1-10)

**Réponse:** Fichier audio WAV

---

## 🎭 Émotions Disponibles

**Principales:**
- `neutral` - Neutre
- `joy` - Joie
- `anger` - Colère
- `sadness` - Tristesse
- `fear` - Peur

**Complètes (21 émotions):**
adoration, amazement, amusement, anger, confusion, contentment, cuteness, desire, disappointment, disgust, distress, embarassment, extasy, fear, guilt, interest, joy, neutral, pain, pride, sadness

---

## 👥 Voix Disponibles

10 voix différentes (speaker_id de 1 à 10)

**Exemple:**
```json
{
  "text": "Hello world",
  "emotion": "neutral",
  "speaker_id": 3
}
```

---

## 📊 Monitoring en Temps Réel

Utilisez le dashboard de monitoring pour voir:
- Statut du serveur (en ligne/hors ligne)
- Temps de fonctionnement
- Utilisation CPU et mémoire
- Nombre de requêtes par endpoint
- Activité récente

```bash
./monitor.sh
```

**Aperçu:**
```
╔════════════════════════════════════════════════════════════════╗
║         SPOKE TTS SERVER - MONITORING DASHBOARD               ║
╚════════════════════════════════════════════════════════════════╝

● SERVEUR EN LIGNE (PID: 189739)
  Temps de fonctionnement: 02:15:33
  Ressources: 0.5% 2.3% (CPU% MEM%)

─────────────────────────────────────────────────────────────────

📊 STATISTIQUES DES REQUÊTES
  /ping:        15 requêtes
  /health:      5 requêtes
  /synthesize:  23 requêtes
  Succès:       21
  Erreurs:      2
```

---

## 🔍 Analyse des Logs

### Voir les erreurs
```bash
grep "ERROR" server.log
```

### Voir les requêtes de synthèse
```bash
grep "Synthesis request" server.log
```

### Compter les requêtes du jour
```bash
grep "$(date '+%Y-%m-%d')" server.log | wc -l
```

---

## ⚠️ Dépannage

### Le serveur ne démarre pas

1. Vérifiez les logs:
   ```bash
   tail -50 server.log
   ```

2. Vérifiez que le port 5000 n'est pas déjà utilisé:
   ```bash
   lsof -i :5000
   ```

3. Vérifiez les dépendances:
   ```bash
   env/bin/pip list
   ```

### Erreur "Module not found"

Réinstallez les dépendances:
```bash
env/bin/pip install -r requirements.txt
```

### Le serveur est lent

1. Vérifiez l'utilisation des ressources:
   ```bash
   ./manage_server.sh status
   ```

2. Vérifiez l'espace disque:
   ```bash
   df -h
   du -sh output_audio/
   ```

---

## 🔧 Configuration

### Fichiers importants

- `server.py` - Serveur Flask principal
- `inference_engine.py` - Moteur de synthèse vocale
- `emotion_router.py` - Gestion des émotions
- `Configs/config.yml` - Configuration StyleTTS2

### Modifier le port

Éditez `server.py` ligne 108:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Ajouter des logs personnalisés

Le serveur utilise le module `logging` de Python:
```python
logger.info("Message d'information")
logger.error("Message d'erreur")
logger.warning("Avertissement")
```

---

## 🚀 Production

Pour déployer en production:

1. **Désactivez le mode debug** dans `server.py`:
   ```python
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

2. **Utilisez un serveur WSGI** comme Gunicorn:
   ```bash
   env/bin/pip install gunicorn
   env/bin/gunicorn -w 4 -b 0.0.0.0:5000 server:app
   ```

3. **Configurez HTTPS** avec un reverse proxy (Nginx/Apache)

4. **Mettez en place une rotation des logs**

5. **Ajoutez une authentification** si nécessaire

---

## 📦 Structure des Fichiers

```
spoke/
├── server.py                 # Serveur Flask
├── inference_engine.py       # Moteur TTS
├── emotion_router.py         # Gestion émotions
├── manage_server.sh          # Script de gestion ⭐
├── monitor.sh               # Dashboard monitoring ⭐
├── view_logs.sh             # Visualisation logs ⭐
├── API_USAGE.md             # Doc API ⭐
├── MONITORING.md            # Doc monitoring ⭐
├── README_SERVER.md         # Ce fichier ⭐
├── Configs/                 # Configuration
├── emotions/                # Modèles par émotion
├── output_audio/           # Fichiers générés
└── env/                    # Environnement virtuel
```

---

## 🎓 Exemples d'Utilisation

### Exemple Python

```python
import requests

response = requests.post('http://51.210.165.192:5000/synthesize',
    json={
        'text': 'Bonjour le monde',
        'emotion': 'joy',
        'speaker_id': 3
    }
)

with open('output.wav', 'wb') as f:
    f.write(response.content)
```

### Exemple JavaScript

```javascript
async function synthesize(text, emotion, speaker) {
  const response = await fetch('http://51.210.165.192:5000/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, emotion, speaker_id: speaker })
  });

  const blob = await response.blob();
  const audio = new Audio(URL.createObjectURL(blob));
  audio.play();
}

// Utilisation
synthesize("Hello world", "neutral", 1);
```

### Exemple cURL

```bash
curl -X POST http://51.210.165.192:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello", "emotion":"neutral", "speaker_id":1}' \
  -o output.wav
```

---

## 📞 Support

Pour toute question ou problème:

1. Consultez [API_USAGE.md](API_USAGE.md) pour l'utilisation de l'API
2. Consultez [MONITORING.md](MONITORING.md) pour le monitoring
3. Vérifiez les logs avec `./manage_server.sh logs`
4. Redémarrez le serveur avec `./manage_server.sh restart`

---

## ✅ Checklist de Démarrage

- [ ] Le serveur est démarré: `./manage_server.sh start`
- [ ] Le statut est OK: `./manage_server.sh status`
- [ ] Le ping fonctionne: `curl http://localhost:5000/ping`
- [ ] La synthèse fonctionne: tester avec l'exemple ci-dessus
- [ ] Le monitoring est configuré: `./monitor.sh`

---

**Serveur prêt à l'emploi!** 🎉

Pour toute assistance, consultez la documentation ou vérifiez les logs.
