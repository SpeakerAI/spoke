# 🛡️ Guide Rapide - Watchdog de Sécurité

## Qu'est-ce que c'est ?

Le watchdog est un système de surveillance automatique qui :
- ✅ Vérifie toutes les **2 minutes** si le serveur est en ligne
- 🔄 Redémarre automatiquement le serveur s'il crash
- 📝 Enregistre tous les événements dans `watchdog.log`

## Démarrage en 3 commandes

```bash
# 1. Démarrer le watchdog
./watchdog.sh start

# 2. Vérifier le statut
./watchdog.sh status

# 3. Voir les logs en temps réel
./watchdog.sh logs
```

## Test rapide

```bash
# Arrêter manuellement le serveur
./manage_server.sh stop

# Attendre 2 minutes et vérifier
./watchdog.sh status

# ✅ Le serveur devrait être redémarré automatiquement !
```

## Commandes principales

| Commande | Description |
|----------|-------------|
| `./watchdog.sh start` | Démarre le watchdog en arrière-plan |
| `./watchdog.sh stop` | Arrête le watchdog |
| `./watchdog.sh status` | Affiche le statut actuel |
| `./watchdog.sh logs` | Logs en temps réel (Ctrl+C pour quitter) |

## ⚠️ Important

- Si vous voulez arrêter le serveur manuellement, **arrêtez d'abord le watchdog**
- Sinon, le watchdog va automatiquement redémarrer le serveur

```bash
# Arrêt complet (watchdog + serveur)
./watchdog.sh stop
./manage_server.sh stop
```

## 📊 Statistiques

```bash
# Voir le nombre de redémarrages
grep "Redémarrage réussi" watchdog.log | wc -l

# Voir les alertes
grep "ALERTE" watchdog.log
```

## 🚀 Démarrage automatique au boot

Pour que le watchdog démarre automatiquement au boot du serveur, consultez le fichier [WATCHDOG_README.md](WATCHDOG_README.md) section "Utilisation en production".

## Résumé

Le watchdog garantit que votre serveur Spoke TTS reste toujours en ligne, même en cas de crash inattendu. Une fois démarré, vous n'avez plus à vous en soucier !

```bash
# Configuration recommandée
./watchdog.sh start    # Une fois au démarrage
# C'est tout ! Le watchdog s'occupe du reste 🎉
```
