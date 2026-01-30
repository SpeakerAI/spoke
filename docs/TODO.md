# TODO - Spoke TTS Server

## ❌ Problème Actuel: Modèles Non Téléchargés

**État:** Le serveur est configuré mais ne peut pas générer d'audio car les fichiers de modèles ne sont pas présents.

### Diagnostic

Les fichiers `.pth` dans le dossier `emotions/` sont des **pointeurs Git LFS** (135 octets chacun), pas les vrais modèles (~2.2GB chacun).

```bash
# Exemple de fichier actuel
$ cat emotions/contentment/contentment_6sec.pth
version https://git-lfs.github.com/spec/v1
oid sha256:8a490544791d1166ff26e91b9b866f4c2ae70338125cafe4ac687c6ea1cda5e3
size 2242832963
```

**Nombre de modèles manquants:** 21 émotions × ~2.2GB = ~46GB total

### Erreur rencontrée

```
_pickle.UnpicklingError: invalid load key, 'v'.
```

Cette erreur apparaît car PyTorch tente de charger un fichier texte (pointeur LFS) au lieu d'un vrai modèle binaire.

---

## 🔧 Solution: Télécharger les Modèles

### Option 1: Téléchargement Git LFS (Recommandé)

```bash
cd /home/ubuntu/spoke

# Télécharger tous les fichiers LFS
git lfs fetch --all

# Remplacer les pointeurs par les vrais fichiers
git lfs checkout
```

**⚠️ Attention:**
- Taille totale: ~46GB
- Temps estimé: 1-2 heures selon la connexion
- Espace disque requis: Vérifier avec `df -h`

### Option 2: Transférer depuis une autre machine

Si vous avez déjà téléchargé les modèles ailleurs:

```bash
# Sur votre machine locale (avec les vrais modèles)
scp -r emotions/*.pth ubuntu@51.210.165.192:/home/ubuntu/spoke/emotions/

# Ou utiliser rsync
rsync -avz --progress emotions/ ubuntu@51.210.165.192:/home/ubuntu/spoke/emotions/
```

### Vérification après téléchargement

```bash
# Vérifier la taille des fichiers (doivent être > 1GB)
ls -lh emotions/*/*.pth

# Devrait afficher des fichiers comme:
# -rw-rw-r-- 1 ubuntu ubuntu 2.1G Dec 19 13:06 emotions/anger/anger_6sec.pth
```

---

## ✅ État du Serveur

### Ce qui fonctionne:

- ✅ Serveur HTTP Flask opérationnel sur port 5000
- ✅ CORS configuré pour accepter les requêtes du site web
- ✅ Endpoints `/ping` et `/health` fonctionnels
- ✅ Validation des paramètres (text, emotion, speaker_id)
- ✅ Fix PyTorch 2.6 pour le chargement des modèles
- ✅ Patch pour compatibilité Path/string dans styletts2
- ✅ 107 voix disponibles pour chaque émotion
- ✅ 21 émotions supportées

### Ce qui ne fonctionne pas:

- ❌ Génération audio (modèles manquants)
- ❌ Endpoint `/synthesize` (erreur de chargement de modèle)

---

## 📋 Fichiers Modifiés

### Serveur
- `server.py` - Serveur Flask avec 3 endpoints
- `inference_engine.py` - Moteur de synthèse avec patches PyTorch
- `emotion_router.py` - Mapping des 21 émotions

### Bibliothèque tierce (patch appliqué)
- `env/lib/python3.12/site-packages/styletts2/Utils/PLBERT/util.py` (ligne 38)
  - Changé: `checkpoint_path = log_dir / f"step_{iters}.t7"`
  - En: `checkpoint_path = os.path.join(log_dir, f"step_{iters}.t7")`

### Scripts utilitaires
- `manage_server.sh` - Gestion du serveur (start/stop/status/logs/stats)
- `monitor.sh` - Dashboard de monitoring temps réel
- `view_logs.sh` - Visualisation des logs
- `list_available_voices.sh` - Liste des voix par émotion

### Documentation
- `API_USAGE.md` - Documentation API complète
- `MONITORING.md` - Guide de monitoring
- `README_SERVER.md` - Guide de démarrage

---

## 🎯 Prochaines Étapes

### 1. Télécharger les modèles (CRITIQUE)

```bash
cd /home/ubuntu/spoke
git lfs fetch --all
git lfs checkout
```

### 2. Vérifier que les modèles sont téléchargés

```bash
# Vérifier un fichier
ls -lh emotions/contentment/contentment_6sec.pth
# Devrait afficher: ~2.1G au lieu de 135 bytes
```

### 3. Redémarrer le serveur

```bash
./manage_server.sh restart
```

### 4. Tester depuis le site web

```javascript
fetch('http://51.210.165.192:5000/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "This is a test",
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

## 🔍 Vérifications Utiles

### Espace disque disponible

```bash
df -h /home/ubuntu
```

Besoin d'au moins 50GB libres pour les modèles.

### Modèles actuels

```bash
# Compter les pointeurs LFS (devrait être 0 après téléchargement)
find emotions/ -name "*.pth" -size -1k | wc -l

# Compter les vrais modèles (devrait être 21 après téléchargement)
find emotions/ -name "*.pth" -size +1G | wc -l
```

### Status du serveur

```bash
./manage_server.sh status
./manage_server.sh stats
```

---

## 📝 Notes Techniques

### Émotions supportées (21 total)

anger, sadness, joy (→amusement), fear, neutral (→contentment), amusement, contentment, adoration, amazement, confusion, cuteness, desire, disappointment, disgust, distress, embarassment, extasy, guilt, interest, pain, pride, sadness

### Voix disponibles

p001 à p107 (107 voix pour chaque émotion)

### Configuration utilisée

- Config: `Configs/config_libritts.yml`
- PyTorch: Version 2.6 (avec patch `weights_only=False`)
- Port: 5000
- IP publique: 51.210.165.192

---

## ⚠️ Problèmes Connus Résolus

1. ✅ PyTorch 2.6 `weights_only` erreur → Patch appliqué dans `inference_engine.py`
2. ✅ TypeError Path/string division → Patch appliqué dans `util.py`
3. ✅ Import AdamW incorrect → Corrigé dans `inference_engine.py`
4. ✅ Validation speaker_id 1-10 → Étendu à 1-107 dans `server.py`

---

## 📞 Support

En cas de problème après téléchargement des modèles:

1. Vérifier les logs: `./manage_server.sh logs`
2. Vérifier le statut: `./manage_server.sh status`
3. Consulter la documentation: `API_USAGE.md`, `MONITORING.md`

---

**Dernière mise à jour:** 29 Décembre 2025
**Statut:** ⚠️ En attente du téléchargement des modèles
