## Marketplace System - Guide Complet

### Vue d'ensemble

Le système de marketplace permet de :
- **Gérer les voix** possédées par chaque utilisateur
- **Vendre des voix premium** via un catalogue
- **Vérifier les permissions** avant la synthèse
- **Fake purchases** (pas de paiement réel, juste l'ajout en DB)

---

## Configuration Supabase

### 1. Créer les tables

Connecte-toi à ton projet Supabase et exécute le fichier `supabase_schema.sql` :

```sql
-- Copier-coller le contenu de supabase_schema.sql dans l'éditeur SQL de Supabase
```

Cela créera 3 tables :
- `marketplace_voices` - Catalogue des voix premium
- `user_voices` - Voix possédées par chaque user
- `voice_purchases` - Historique des achats

### 2. Configurer les credentials

Créer un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

Éditer `.env` avec tes credentials Supabase :

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

Tu trouveras ces infos dans : **Supabase Dashboard → Settings → API**

---

## Endpoints API

### 1. GET /marketplace/catalog

Récupérer le catalogue des voix premium disponibles.

**Request:**
```http
GET /marketplace/catalog
```

**Response:**
```json
{
  "voices": [
    {
      "id": 1,
      "voice_id": 5,
      "name": "Alex - Young Asian Male",
      "description": "Energetic young voice, perfect for dynamic content",
      "gender": "male",
      "age_range": "18-25",
      "language": "Mandarin",
      "price": 9.99,
      "is_available": true
    },
    ...
  ],
  "total": 20
}
```

---

### 2. POST /marketplace/purchase

"Acheter" une voix (fake purchase - pas de paiement réel).

**Request:**
```json
{
  "user_id": "user_123",
  "voice_id": 25
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully purchased Sarah - Gentle Voice",
  "voice_id": 25
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "You already own this voice"
}
```

---

### 3. GET /voices/owned?user_id=xxx

Récupérer les voix possédées par un utilisateur.

**Request:**
```http
GET /voices/owned?user_id=user_123
```

**Response:**
```json
{
  "user_id": "user_123",
  "voices": [1, 2, 3, 4, 25, 32, 47],
  "total": 7
}
```

Les voix 1-4 sont toujours données automatiquement au premier appel.

---

### 4. GET /voices/available?user_id=xxx

Récupérer toutes les voix disponibles (owned + marketplace).

**Request:**
```http
GET /voices/available?user_id=user_123
```

**Response:**
```json
{
  "owned": [1, 2, 3, 4, 25],
  "marketplace": [
    {
      "voice_id": 5,
      "name": "Alex - Young Asian Male",
      "price": 9.99,
      ...
    },
    ...
  ],
  "total_owned": 5
}
```

---

### 5. POST /synthesize (avec vérification)

La synthèse vérifie maintenant si l'utilisateur possède la voix.

**Request:**
```json
{
  "text": "Hello world",
  "emotion": "joy",
  "speaker_id": 25,
  "user_id": "user_123"  // Nouveau paramètre optionnel
}
```

**Response (Voix non possédée):**
```json
{
  "error": "You don't own this voice. Please purchase it from the marketplace."
}
```
Status: 403 Forbidden

**Note:** Le paramètre `user_id` est **optionnel**. Si tu ne le fournis pas, la vérification est skip pée.

---

## Code JavaScript d'intégration

### Configuration
```javascript
const API_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';
const USER_ID = 'user_123';  // ID de l'utilisateur connecté
```

### Récupérer les voix possédées
```javascript
async function getOwnedVoices(userId) {
  const response = await fetch(`${API_URL}/voices/owned?user_id=${userId}`);
  const data = await response.json();
  return data.voices;  // [1, 2, 3, 4, 25, ...]
}
```

### Récupérer le catalogue marketplace
```javascript
async function getMarketplace() {
  const response = await fetch(`${API_URL}/marketplace/catalog`);
  const data = await response.json();
  return data.voices;
}
```

### Acheter une voix
```javascript
async function purchaseVoice(userId, voiceId) {
  const response = await fetch(`${API_URL}/marketplace/purchase`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      voice_id: voiceId
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Voice purchased!', data.message);
  } else {
    console.error('Purchase failed:', data.error);
  }

  return data;
}
```

### Synthétiser avec vérification
```javascript
async function synthesizeWithCheck(userId, voiceId, text, emotion = 'neutral') {
  const response = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: voiceId,
      user_id: userId  // Ajouter user_id pour vérification
    })
  });

  if (response.status === 403) {
    // L'utilisateur ne possède pas cette voix
    const error = await response.json();
    throw new Error(error.error);
  }

  return await response.blob();
}
```

### Workflow complet
```javascript
// 1. Afficher le marketplace
async function showMarketplace() {
  const owned = await getOwnedVoices(USER_ID);
  const catalog = await getMarketplace();

  // Filtrer les voix pas encore possédées
  const available = catalog.filter(v => !owned.includes(v.voice_id));

  console.log('Available for purchase:', available);
  return available;
}

// 2. Acheter une voix
async function buyVoice(voiceId) {
  try {
    const result = await purchaseVoice(USER_ID, voiceId);
    if (result.success) {
      alert('Voice purchased successfully!');
      // Rafraîchir la liste des voix possédées
      return true;
    }
  } catch (error) {
    alert('Purchase failed: ' + error.message);
    return false;
  }
}

// 3. Utiliser une voix
async function useVoice(voiceId, text) {
  try {
    const audioBlob = await synthesizeWithCheck(USER_ID, voiceId, text);
    playAudio(audioBlob);
  } catch (error) {
    if (error.message.includes("don't own")) {
      // Proposer d'acheter la voix
      const shouldBuy = confirm('You need to purchase this voice. Buy now?');
      if (shouldBuy) {
        const purchased = await buyVoice(voiceId);
        if (purchased) {
          // Réessayer la synthèse
          useVoice(voiceId, text);
        }
      }
    } else {
      console.error('Synthesis error:', error);
    }
  }
}
```

---

## Exemple React Complet

```jsx
import React, { useState, useEffect } from 'react';

function VoiceMarketplace({ userId }) {
  const [ownedVoices, setOwnedVoices] = useState([]);
  const [marketplace, setMarketplace] = useState([]);
  const [loading, setLoading] = useState(false);

  // Charger les données au montage
  useEffect(() => {
    loadVoices();
  }, [userId]);

  const loadVoices = async () => {
    setLoading(true);
    try {
      // Récupérer owned + marketplace en une seule requête
      const response = await fetch(`${API_URL}/voices/available?user_id=${userId}`);
      const data = await response.json();

      setOwnedVoices(data.owned);
      setMarketplace(data.marketplace);
    } catch (error) {
      console.error('Error loading voices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (voiceId) => {
    try {
      const response = await fetch(`${API_URL}/marketplace/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, voice_id: voiceId })
      });

      const data = await response.json();

      if (data.success) {
        alert('Voice purchased!');
        loadVoices();  // Rafraîchir
      } else {
        alert('Purchase failed: ' + data.error);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="voice-marketplace">
      <h2>Your Voices ({ownedVoices.length})</h2>
      <div className="owned-voices">
        {ownedVoices.map(voiceId => (
          <div key={voiceId} className="voice-card owned">
            Voice {voiceId} ✓
          </div>
        ))}
      </div>

      <h2>Available for Purchase</h2>
      <div className="marketplace-voices">
        {marketplace.map(voice => (
          <div key={voice.voice_id} className="voice-card">
            <h3>{voice.name}</h3>
            <p>{voice.description}</p>
            <p className="price">${voice.price}</p>
            <button onClick={() => handlePurchase(voice.voice_id)}>
              Buy Now
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Mode Fallback (Sans Supabase)

Si tu ne configures pas Supabase, le système utilise un fichier JSON local.

### Fichier `local_marketplace.json`
```json
{
  "user_123": {
    "voices": [1, 2, 3, 4, 25, 32]
  }
}
```

Les opérations fonctionnent de la même façon, mais les données sont stockées localement.

---

## Gestion des Voix Premium

### Ajouter une nouvelle voix au marketplace

Option 1 - Via SQL (Supabase):
```sql
INSERT INTO marketplace_voices (voice_id, name, description, gender, age_range, language, price)
VALUES (50, 'Grace - Petite Senior', 'Gentle senior female voice', 'female', '56-65', 'American English', 11.99);
```

Option 2 - Via API (à créer si nécessaire):
```javascript
// POST /admin/marketplace/add
{
  "voice_id": 50,
  "name": "Grace - Petite Senior",
  "description": "Gentle senior female voice",
  "gender": "female",
  "age_range": "56-65",
  "language": "American English",
  "price": 11.99
}
```

---

## Sécurité

### Authentification

Le système actuel utilise un simple `user_id` (string). Pour la production, tu devrais :

1. **Utiliser JWT tokens** pour authentifier les users
2. **Vérifier le token** à chaque requête
3. **Extraire le user_id** du token plutôt que de le recevoir en paramètre

Exemple avec JWT:
```javascript
// Côté client
const token = localStorage.getItem('auth_token');

fetch(`${API_URL}/synthesize`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: "Hello",
    emotion: "joy",
    speaker_id: 25
    // Pas besoin de user_id, extrait du token côté serveur
  })
});
```

---

## Résumé

✅ **Tables Supabase** créées avec `supabase_schema.sql`
✅ **Module Python** `marketplace.py` pour gérer les voix
✅ **4 Endpoints API** : catalog, purchase, owned, available
✅ **Vérification** dans `/synthesize` (si user_id fourni)
✅ **Mode Fallback** (fichier JSON local) si pas de Supabase
✅ **Exemples** JavaScript et React

Le système est prêt ! Il te suffit de :
1. Créer les tables dans Supabase
2. Ajouter tes credentials dans `.env`
3. Redémarrer le serveur
