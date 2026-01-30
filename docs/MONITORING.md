# Guide de Monitoring du Serveur Spoke TTS

Ce guide vous explique comment surveiller et gérer votre serveur Spoke TTS.

## 🛠️ Outils de Gestion

### 1. Script de Gestion Principal

**Fichier:** `manage_server.sh`

Ce script permet de gérer le serveur facilement.

#### Commandes disponibles:

```bash
# Démarrer le serveur
./manage_server.sh start

# Arrêter le serveur
./manage_server.sh stop

# Redémarrer le serveur
./manage_server.sh restart

# Voir le statut du serveur
./manage_server.sh status

# Voir les logs en temps réel
./manage_server.sh logs

# Voir les statistiques
./manage_server.sh stats

# Afficher l'aide
./manage_server.sh help
```

#### Exemple de sortie du statut:

```
═══════════════════════════════════════
    SPOKE TTS SERVER STATUS
═══════════════════════════════════════
✅ Statut: EN COURS D'EXÉCUTION
   PID: 189739
   Port: 5000
   URL locale: http://localhost:5000
   URL publique: http://51.210.165.192:5000

📝 Derniers logs:
   INFO:__main__:Received ping request
   INFO:werkzeug:127.0.0.1 - - [29/Dec/2025 14:06:49] "GET /ping HTTP/1.1" 200 -
```

---

### 2. Moniteur en Temps Réel

**Fichier:** `monitor.sh`

Dashboard interactif qui se met à jour automatiquement toutes les 2 secondes.

```bash
./monitor.sh
```

**Affiche:**
- Statut du serveur (en ligne/hors ligne)
- Temps de fonctionnement
- Utilisation CPU et mémoire
- Nombre total de requêtes par endpoint
- Nombre de succès et d'erreurs
- Activité récente (10 dernières lignes)

**Pour quitter:** Appuyez sur `Ctrl+C`

---

### 3. Visualisation Simple des Logs

**Fichier:** `view_logs.sh`

Affiche les logs en temps réel.

```bash
./view_logs.sh
```

---

## 📊 Statistiques et Métriques

### Voir les statistiques globales

```bash
./manage_server.sh stats
```

**Affiche:**
- Nombre de requêtes `/ping`
- Nombre de requêtes `/health`
- Nombre de requêtes `/synthesize`
- Nombre d'erreurs
- Dernières requêtes effectuées

### Exemple de sortie:

```
═══════════════════════════════════════
    STATISTIQUES DU SERVEUR
═══════════════════════════════════════
Requêtes /ping: 15
Requêtes /health: 5
Requêtes /synthesize: 23
Erreurs: 2

Dernières requêtes:
INFO:__main__:Synthesis request - Text: 'Hello world...', Emotion: neutral, Speaker: p001
INFO:__main__:Audio generated successfully: abc123.wav
```

---

## 📝 Analyse des Logs

### Voir les logs en temps réel

```bash
./manage_server.sh logs
```

Ou directement:

```bash
tail -f /tmp/claude/-home-ubuntu-spoke/tasks/*.output
```

### Filtrer les logs par type

```bash
# Voir uniquement les erreurs
grep "ERROR" server.log

# Voir uniquement les requêtes de synthèse
grep "Synthesis request" server.log

# Voir les requêtes réussies
grep "Audio generated successfully" server.log

# Voir les requêtes des 5 dernières minutes
grep "$(date '+%Y-%m-%d %H:%M')" server.log
```

### Analyser les performances

```bash
# Compter le nombre de requêtes de synthèse aujourd'hui
grep "Synthesis request" server.log | grep "$(date '+%Y-%m-%d')" | wc -l

# Voir les émotions les plus utilisées
grep "Synthesis request" server.log | grep -o "Emotion: [a-z]*" | sort | uniq -c | sort -nr

# Voir les speakers les plus utilisés
grep "Synthesis request" server.log | grep -o "Speaker: p[0-9]*" | sort | uniq -c | sort -nr
```

---

## 🔍 Informations sur les Requêtes

### Types de logs générés

#### 1. Requête /ping
```
INFO:__main__:Received ping request
INFO:werkzeug:127.0.0.1 - - [29/Dec/2025 14:06:49] "GET /ping HTTP/1.1" 200 -
```

#### 2. Requête /health
```
INFO:__main__:Health check request
INFO:werkzeug:127.0.0.1 - - [29/Dec/2025 14:06:49] "GET /health HTTP/1.1" 200 -
```

#### 3. Requête /synthesize réussie
```
INFO:__main__:Synthesis request - Text: 'Hello world...', Emotion: neutral, Speaker: p001
INFO:__main__:Audio generated successfully: abc123.wav
INFO:werkzeug:127.0.0.1 - - [29/Dec/2025 14:06:49] "POST /synthesize HTTP/1.1" 200 -
```

#### 4. Requête /synthesize avec erreur
```
INFO:__main__:Synthesis request - Text: 'Hello world...', Emotion: neutral, Speaker: p001
ERROR:__main__:File not found: emotions/neutral.pth
INFO:werkzeug:127.0.0.1 - - [29/Dec/2025 14:06:49] "POST /synthesize HTTP/1.1" 404 -
```

---

## 🚨 Surveillance des Erreurs

### Voir toutes les erreurs

```bash
grep "ERROR" server.log
```

### Erreurs courantes et solutions

#### 1. "ModuleNotFoundError: No module named 'styletts2'"
**Cause:** Le module styletts2 n'est pas installé dans l'environnement virtuel

**Solution:**
```bash
env/bin/pip install styletts2
```

#### 2. "File not found: emotions/..."
**Cause:** Le fichier de modèle ou de speaker n'existe pas

**Solution:**
- Vérifier que l'émotion existe: `ls emotions/`
- Vérifier que le speaker existe: `ls emotions/anger/p*.wav`

#### 3. "Speaker or emotion file not found"
**Cause:** Le speaker_id demandé n'a pas de fichier pour cette émotion

**Solution:**
- Vérifier les speakers disponibles pour cette émotion
- Utiliser un speaker_id entre 1 et 10

---

## 📈 Monitoring de la Performance

### Vérifier l'utilisation des ressources

```bash
# CPU et mémoire du serveur
ps aux | grep "python.*server.py"

# Utilisation détaillée
top -p $(pgrep -f "python.*server.py")
```

### Vérifier l'espace disque (fichiers audio générés)

```bash
# Taille du dossier output_audio
du -sh output_audio/

# Nombre de fichiers générés
ls output_audio/ | wc -l

# Nettoyer les anciens fichiers (plus de 24h)
find output_audio/ -name "*.wav" -mtime +1 -delete
```

---

## 🔄 Automatisation

### Démarrage automatique au boot

Créer un service systemd:

```bash
sudo nano /etc/systemd/system/spoke-tts.service
```

Contenu:
```ini
[Unit]
Description=Spoke TTS Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/spoke
ExecStart=/home/ubuntu/spoke/env/bin/python /home/ubuntu/spoke/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable spoke-tts
sudo systemctl start spoke-tts
```

Vérifier:
```bash
sudo systemctl status spoke-tts
```

---

## 📊 Tableau de bord Web (Optionnel)

Pour un monitoring plus avancé, vous pouvez intégrer des outils comme:

1. **Prometheus + Grafana** - Monitoring et visualisation
2. **ELK Stack** - Analyse de logs avancée
3. **Netdata** - Monitoring temps réel

---

## 💡 Conseils

1. **Rotation des logs**: Configurez une rotation des logs pour éviter qu'ils ne deviennent trop volumineux
2. **Alertes**: Mettez en place des alertes pour être notifié en cas d'erreur
3. **Backup**: Sauvegardez régulièrement les modèles et fichiers audio
4. **Sécurité**: En production, utilisez HTTPS et ajoutez une authentification
5. **Performance**: Surveillez l'utilisation CPU/RAM pendant les pics de charge

---

## 🆘 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs: `./manage_server.sh logs`
2. Vérifiez le statut: `./manage_server.sh status`
3. Redémarrez le serveur: `./manage_server.sh restart`
4. Consultez les statistiques: `./manage_server.sh stats`
