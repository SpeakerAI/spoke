# Watchdog - Surveillance automatique du serveur

Le watchdog est un système de surveillance qui vérifie automatiquement toutes les 2 minutes si le serveur Spoke TTS est en ligne et le redémarre en cas de crash.

## 🚀 Démarrage rapide

### Démarrer le watchdog
```bash
./watchdog.sh start
```

Le watchdog se lance en arrière-plan et surveille le serveur automatiquement.

### Vérifier le statut
```bash
./watchdog.sh status
```

### Voir les logs en temps réel
```bash
./watchdog.sh logs
```

### Arrêter le watchdog
```bash
./watchdog.sh stop
```

## 📋 Commandes disponibles

| Commande | Description |
|----------|-------------|
| `start` | Démarre le watchdog en arrière-plan |
| `stop` | Arrête le watchdog |
| `status` | Affiche le statut du watchdog |
| `logs` | Affiche les logs en temps réel |
| `run` | Lance le watchdog en mode interactif (foreground) |
| `help` | Affiche l'aide |

## 🔧 Fonctionnement

### Vérifications effectuées
1. **Processus** : Vérifie si le processus Python du serveur existe
2. **Health check** : Teste l'endpoint `/health` pour s'assurer que le serveur répond
3. **Auto-redémarrage** : Si une vérification échoue, le watchdog :
   - Arrête les processus zombies
   - Redémarre le serveur
   - Vérifie que le redémarrage a réussi

### Fréquence
- Vérification toutes les **2 minutes** (120 secondes)
- En cas d'échec de redémarrage, réessaie après 10 secondes

### Logs
- Fichier : `watchdog.log`
- Rotation automatique à 10MB
- Format : `[YYYY-MM-DD HH:MM:SS] message`

## 📊 Exemples d'utilisation

### Scénario 1 : Démarrage initial
```bash
# Démarrer le watchdog
./watchdog.sh start

# Vérifier qu'il tourne
./watchdog.sh status
```

### Scénario 2 : Surveillance en temps réel
```bash
# Voir les logs en direct
./watchdog.sh logs
```

### Scénario 3 : Test de crash
```bash
# Arrêter manuellement le serveur pour tester
./manage_server.sh stop

# Attendre 2 minutes et vérifier les logs
./watchdog.sh logs

# Le watchdog devrait automatiquement redémarrer le serveur
```

## 🎯 Utilisation en production

### Démarrage au boot (systemd)

Pour démarrer automatiquement le watchdog au démarrage du système, créez un service systemd :

1. Créer le fichier service :
```bash
sudo nano /etc/systemd/system/spoke-watchdog.service
```

2. Contenu du fichier :
```ini
[Unit]
Description=Spoke TTS Watchdog
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/spoke
ExecStart=/home/ubuntu/spoke/watchdog.sh run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Activer et démarrer :
```bash
sudo systemctl enable spoke-watchdog
sudo systemctl start spoke-watchdog
sudo systemctl status spoke-watchdog
```

### Vérification des logs systemd
```bash
sudo journalctl -u spoke-watchdog -f
```

## ⚙️ Configuration

Pour modifier l'intervalle de vérification, éditez le fichier `watchdog.sh` :

```bash
# Ligne 14
CHECK_INTERVAL=120  # Changer la valeur (en secondes)
```

Exemples :
- 60 = 1 minute
- 120 = 2 minutes (par défaut)
- 300 = 5 minutes

## 🐛 Dépannage

### Le watchdog ne démarre pas
```bash
# Vérifier les permissions
ls -l watchdog.sh
chmod +x watchdog.sh

# Vérifier que l'environnement Python existe
ls -la env/
```

### Le serveur redémarre en boucle
```bash
# Voir les erreurs du serveur
tail -100 server.log

# Vérifier les dernières erreurs
./watchdog.sh logs
```

### Arrêt complet
```bash
# Arrêter le watchdog
./watchdog.sh stop

# Arrêter le serveur
./manage_server.sh stop
```

## 📈 Monitoring

### Statistiques du watchdog
```bash
# Nombre de redémarrages
grep "Redémarrage réussi" watchdog.log | wc -l

# Nombre d'alertes
grep "ALERTE" watchdog.log | wc -l

# Dernières 20 lignes
tail -20 watchdog.log
```

## 🔐 Sécurité

- Le watchdog tourne sous l'utilisateur actuel (pas root)
- Logs automatiquement rotatés pour éviter la saturation du disque
- Processus isolé du serveur principal
- Arrêt propre avec `kill` avant `kill -9`

## 📝 Notes

- Le watchdog est indépendant du serveur
- Si vous arrêtez manuellement le serveur avec `./manage_server.sh stop`, le watchdog le redémarrera automatiquement
- Pour éviter cela, arrêtez d'abord le watchdog avec `./watchdog.sh stop`
