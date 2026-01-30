#!/bin/bash

# Script pour voir les logs du serveur Spoke TTS

# Trouver le PID du serveur
SERVER_PID=$(pgrep -f "python.*server.py" | head -1)

if [ -z "$SERVER_PID" ]; then
    echo "❌ Le serveur n'est pas en cours d'exécution"
    exit 1
fi

echo "✅ Serveur trouvé (PID: $SERVER_PID)"
echo "📊 Affichage des logs en temps réel..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Trouver le fichier de log le plus récent
LOG_FILE=$(ls -t /tmp/claude/-home-ubuntu-spoke/tasks/*.output 2>/dev/null | head -1)

if [ -n "$LOG_FILE" ]; then
    tail -f "$LOG_FILE"
else
    echo "⚠️  Fichier de logs non trouvé"
    echo "Le serveur doit être démarré en arrière-plan pour générer des logs"
fi
