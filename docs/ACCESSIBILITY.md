# Accessibilité - Spoke TTS API

## Conformité WCAG 2.1 AA

Ce document définit la stratégie d'accessibilité pour l'API Spoke TTS et les interfaces qui l'utilisent.

---

## 1. Vue d'ensemble

Spoke TTS est une API de synthèse vocale. L'accessibilité est critique car:
- Le TTS est lui-même une technologie d'assistance
- L'API doit être utilisable par tous les développeurs
- Les interfaces construites avec l'API doivent être accessibles

### Niveaux de conformité ciblés

| Composant | Niveau WCAG | Justification |
|-----------|-------------|---------------|
| Documentation API | AA | Utilisable par tous les développeurs |
| Réponses JSON | A | Structurées et prévisibles |
| Codes d'erreur | AA | Messages clairs et actionnables |

---

## 2. Principes WCAG appliqués

### 2.1 Perceptible

#### 2.1.1 Alternatives textuelles (1.1.1)

**API Responses:**
```json
{
  "status": "success",
  "message": "Audio généré avec succès",
  "audio_url": "/audio/output.wav",
  "duration_seconds": 2.5,
  "speaker_name": "Voix masculine classique"
}
```

**Bonnes pratiques:**
- Tous les champs JSON ont des noms descriptifs
- Les messages d'erreur sont en texte clair
- Les métadonnées audio incluent la durée

#### 2.1.2 Contenu audio (1.2.1)

L'API génère du contenu audio. Pour l'accessibilité:
- Le texte source est toujours retourné avec l'audio
- Les métadonnées incluent la transcription
- Le format de sortie est standardisé (WAV 24kHz)

### 2.2 Utilisable

#### 2.2.1 Accessibilité au clavier (2.1.1)

**Pour les développeurs frontend:**
```html
<!-- Exemple de lecteur audio accessible -->
<div role="region" aria-label="Lecteur audio TTS">
  <audio
    controls
    aria-describedby="audio-description"
    tabindex="0">
    <source src="/audio/output.wav" type="audio/wav">
  </audio>
  <p id="audio-description">
    Audio généré: "Bonjour le monde" - Voix neutre, 2.5 secondes
  </p>
</div>
```

#### 2.2.2 Temps suffisant (2.2.1)

**Configuration API:**
- Timeout par défaut: 60 secondes pour la synthèse
- Pas de limite de session
- Les fichiers audio restent disponibles pour téléchargement

### 2.3 Compréhensible

#### 2.3.1 Lisibilité (3.1.1)

**Messages d'erreur standardisés:**
```json
{
  "error": "emotion_invalid",
  "message": "L'émotion 'xyz' n'est pas valide",
  "valid_options": ["neutral", "joy", "anger", "sadness", "fear"],
  "suggestion": "Utilisez 'neutral' pour une voix standard"
}
```

#### 2.3.2 Prévisibilité (3.2.1)

**Cohérence des endpoints:**

| Endpoint | Méthode | Réponse |
|----------|---------|---------|
| `/health` | GET | `{"status": "healthy"}` |
| `/ping` | GET | `{"status": "success"}` |
| `/synthesize` | POST | `{"audio_url": "...", "status": "success"}` |

### 2.4 Robuste

#### 2.4.1 Compatibilité (4.1.1)

**Standards respectés:**
- JSON valide (RFC 8259)
- HTTP/1.1 et HTTP/2
- Codes de statut HTTP standards
- CORS configuré pour l'accès cross-origin

---

## 3. Checklist d'accessibilité pour les intégrateurs

### 3.1 Interface utilisateur

- [ ] Les contrôles audio ont des labels accessibles
- [ ] Le texte synthétisé est affiché comme transcription
- [ ] Les erreurs sont annoncées aux lecteurs d'écran
- [ ] La navigation au clavier fonctionne entièrement
- [ ] Le contraste des couleurs est >= 4.5:1

### 3.2 Lecteur audio

```html
<!-- Template accessible recommandé -->
<div class="tts-player" role="application" aria-label="Synthèse vocale">

  <!-- Zone de texte -->
  <label for="tts-input">Texte à synthétiser</label>
  <textarea
    id="tts-input"
    aria-describedby="tts-help"
    maxlength="5000"></textarea>
  <p id="tts-help">Maximum 5000 caractères</p>

  <!-- Sélection d'émotion -->
  <fieldset>
    <legend>Émotion de la voix</legend>
    <select id="emotion-select" aria-label="Choisir l'émotion">
      <option value="neutral">Neutre</option>
      <option value="joy">Joie</option>
      <option value="sadness">Tristesse</option>
      <option value="anger">Colère</option>
      <option value="fear">Peur</option>
    </select>
  </fieldset>

  <!-- Sélection de voix -->
  <fieldset>
    <legend>Voix</legend>
    <select id="voice-select" aria-label="Choisir la voix">
      <option value="1">Voix classique 1</option>
      <option value="2">Voix classique 2</option>
      <option value="3">Voix classique 3</option>
      <option value="4">Voix classique 4</option>
    </select>
  </fieldset>

  <!-- Bouton de génération -->
  <button
    type="button"
    id="generate-btn"
    aria-busy="false"
    aria-live="polite">
    Générer l'audio
  </button>

  <!-- Lecteur audio -->
  <div id="audio-output" aria-live="polite">
    <audio controls aria-label="Audio généré">
      <!-- Source ajoutée dynamiquement -->
    </audio>
  </div>

  <!-- Zone de statut -->
  <div
    id="status"
    role="status"
    aria-live="polite"
    aria-atomic="true">
  </div>

</div>
```

### 3.3 JavaScript accessible

```javascript
// Exemple d'implémentation accessible
class AccessibleTTSPlayer {
  constructor() {
    this.statusElement = document.getElementById('status');
    this.generateBtn = document.getElementById('generate-btn');
    this.audioElement = document.querySelector('audio');
  }

  async synthesize(text, emotion, speakerId) {
    // Annoncer le début du chargement
    this.announce('Génération de l\'audio en cours...');
    this.generateBtn.setAttribute('aria-busy', 'true');
    this.generateBtn.disabled = true;

    try {
      const response = await fetch('/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, emotion, speaker_id: speakerId })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Erreur de synthèse');
      }

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      this.audioElement.src = audioUrl;
      this.announce('Audio prêt. Appuyez sur Espace pour écouter.');

    } catch (error) {
      this.announce(`Erreur: ${error.message}`);
    } finally {
      this.generateBtn.setAttribute('aria-busy', 'false');
      this.generateBtn.disabled = false;
    }
  }

  announce(message) {
    // Met à jour la zone de statut pour les lecteurs d'écran
    this.statusElement.textContent = message;
  }
}
```

---

## 4. Tests d'accessibilité

### 4.1 Tests automatisés

**Outils recommandés:**
- axe-core pour les tests automatisés
- WAVE pour l'analyse visuelle
- Lighthouse pour l'audit global

**Script de test:**
```javascript
// tests/accessibility/a11y.test.js
const { axe, toHaveNoViolations } = require('jest-axe');

expect.extend(toHaveNoViolations);

describe('TTS Player Accessibility', () => {
  test('should have no accessibility violations', async () => {
    document.body.innerHTML = `
      <div class="tts-player">
        <!-- HTML du player -->
      </div>
    `;

    const results = await axe(document.body);
    expect(results).toHaveNoViolations();
  });
});
```

### 4.2 Tests manuels

**Checklist de test manuel:**

| Test | Méthode | Critère de succès |
|------|---------|-------------------|
| Navigation clavier | Tab/Shift+Tab | Tous les contrôles accessibles |
| Lecteur d'écran | NVDA/VoiceOver | Tous les éléments annoncés |
| Zoom 200% | Browser zoom | Interface utilisable |
| Mode sombre | prefers-color-scheme | Contraste maintenu |
| Focus visible | Tab navigation | Indicateur visible |

### 4.3 Test avec lecteurs d'écran

**Scénarios de test:**

1. **NVDA (Windows)**
   - Naviguer vers le champ de texte
   - Sélectionner une émotion
   - Lancer la synthèse
   - Écouter le résultat

2. **VoiceOver (macOS)**
   - Mêmes étapes avec VO+Flèches

3. **TalkBack (Android)**
   - Test sur version mobile

---

## 5. API accessible

### 5.1 Codes d'erreur HTTP

| Code | Signification | Message utilisateur |
|------|---------------|---------------------|
| 200 | Succès | Audio généré avec succès |
| 400 | Requête invalide | Paramètre manquant ou invalide |
| 401 | Non autorisé | Authentification requise |
| 404 | Non trouvé | Ressource introuvable |
| 429 | Trop de requêtes | Veuillez patienter |
| 500 | Erreur serveur | Erreur temporaire, réessayez |

### 5.2 Format des erreurs

```json
{
  "error": {
    "code": "INVALID_EMOTION",
    "message": "L'émotion spécifiée n'est pas valide",
    "details": {
      "provided": "happiness",
      "valid_options": ["neutral", "joy", "anger", "sadness", "fear"]
    },
    "help_url": "https://docs.spoke.ai/emotions"
  }
}
```

---

## 6. Ressources

### 6.1 Documentation

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WAI-ARIA Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

### 6.2 Outils

- [axe DevTools](https://www.deque.com/axe/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [pa11y](https://pa11y.org/)

---

## 7. Déclaration d'accessibilité

### Niveau de conformité

Spoke TTS API vise la conformité WCAG 2.1 niveau AA pour:
- La documentation de l'API
- Les messages d'erreur
- Les guides d'intégration

### Limitations connues

1. **Audio uniquement**: Le contenu généré est audio; une transcription doit être fournie par l'intégrateur
2. **Synthèse temps réel**: Latence variable selon la longueur du texte

### Contact

Pour signaler un problème d'accessibilité:
- Email: accessibility@spoke.ai
- GitHub Issues: [Créer un ticket](https://github.com/spoke/tts-api/issues)

---

*Document mis à jour: Janvier 2026*
*Version: 1.0*
