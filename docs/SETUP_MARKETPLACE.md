# Setup Marketplace - Guide Rapide

## ✅ Ce qui est déjà fait

- ✅ Serveur Python configuré avec Supabase
- ✅ Fichier `.env` créé avec tes credentials
- ✅ Endpoints API créés (`/marketplace/catalog`, `/voices/owned`, etc.)
- ✅ Module `marketplace.py` prêt
- ✅ Serveur redémarré

## 🔧 Étape suivante : Créer les tables dans Supabase

### 1. Accéder au SQL Editor

1. Va sur https://efjiohqairparynbfdbv.supabase.co
2. Clique sur **SQL Editor** dans la sidebar (icône </> )
3. Clique sur **New query**

### 2. Exécuter le script SQL

Copie-colle le contenu du fichier [`supabase_schema.sql`](supabase_schema.sql) et clique sur **Run**.

Cela va créer :
- ✅ Table `marketplace_voices` (catalogue de voix premium)
- ✅ Table `user_voices` (voix possédées par chaque user)
- ✅ Table `voice_purchases` (historique des achats)
- ✅ 20 voix premium pré-remplies dans le catalogue

### 3. Vérifier que ça a marché

Dans Supabase, va dans **Table Editor** et vérifie que les 3 tables sont créées.

## 🧪 Tester le système

### Test 1: Voir le catalogue
```bash
curl http://localhost:5000/marketplace/catalog | jq .
```

Tu devrais voir 20 voix premium.

### Test 2: Voir les voix d'un utilisateur
```bash
curl "http://localhost:5000/voices/owned?user_id=test_user" | jq .
```

Tu devrais voir `[1, 2, 3, 4]` (les 4 voix classiques).

### Test 3: Acheter une voix
```bash
curl -X POST http://localhost:5000/marketplace/purchase \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "voice_id": 25}' | jq .
```

Tu devrais voir `{"success": true, "message": "Successfully purchased..."}`.

### Test 4: Vérifier que la voix a été ajoutée
```bash
curl "http://localhost:5000/voices/owned?user_id=test_user" | jq .
```

Tu devrais voir `[1, 2, 3, 4, 25]`.

### Test 5: Synthétiser avec vérification
```bash
# Avec une voix possédée (devrait marcher)
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "speaker_id": 1, "text": "Hello", "emotion": "joy"}' \
  --output test.wav

# Avec une voix non possédée (devrait échouer)
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "speaker_id": 50, "text": "Hello", "emotion": "joy"}'
```

Le deuxième devrait retourner une erreur 403.

## 📊 Voir les données dans Supabase

Une fois les tables créées, tu peux :
- **Voir les achats** : Ouvre la table `voice_purchases`
- **Voir les voix des users** : Ouvre la table `user_voices`
- **Modifier le catalogue** : Ouvre la table `marketplace_voices`

## 🔌 Intégration sur ton site

### Code JavaScript minimal

```javascript
const API_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';

// 1. Récupérer les voix possédées par l'utilisateur
async function getMyVoices(userId) {
  const res = await fetch(`${API_URL}/voices/owned?user_id=${userId}`);
  const data = await res.json();
  return data.voices;  // [1, 2, 3, 4, ...]
}

// 2. Récupérer le catalogue marketplace
async function getMarketplace() {
  const res = await fetch(`${API_URL}/marketplace/catalog`);
  const data = await res.json();
  return data.voices;
}

// 3. Acheter une voix
async function buyVoice(userId, voiceId) {
  const res = await fetch(`${API_URL}/marketplace/purchase`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, voice_id: voiceId })
  });
  return await res.json();
}

// 4. Synthétiser (avec vérification automatique)
async function synthesize(userId, voiceId, text, emotion = 'neutral') {
  const res = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      speaker_id: voiceId,
      text: text,
      emotion: emotion
    })
  });

  if (res.status === 403) {
    throw new Error('You need to purchase this voice first!');
  }

  return await res.blob();
}
```

## 📝 Fichiers importants

- [`supabase_schema.sql`](supabase_schema.sql) - Script SQL à exécuter
- [`marketplace.py`](marketplace.py) - Module Python qui gère tout
- [`MARKETPLACE_GUIDE.md`](MARKETPLACE_GUIDE.md) - Documentation complète
- [`.env`](.env) - Credentials Supabase (déjà configuré)

## 🎯 Résumé

**Ce que le système fait :**
1. Chaque user a automatiquement les voix 1, 2, 3, 4
2. Les autres voix (5-107) sont dans le marketplace
3. L'utilisateur peut acheter des voix premium
4. La synthèse vérifie que l'user possède la voix

**Prochaines étapes :**
1. ✅ Créer les tables dans Supabase
2. ✅ Tester les endpoints
3. ✅ Intégrer sur ton site React

Tout est prêt ! 🚀
