#!/bin/bash

# Watchdog pour le serveur Spoke TTS
# Vérifie toutes les 2 minutes si le serveur tourne et le redémarre si nécessaire

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CHECK_INTERVAL=120  # 2 minutes en secondes
LOG_FILE="watchdog.log"
MAX_LOG_SIZE=10485760  # 10MB

# Fonction pour logger avec timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Fonction pour nettoyer les vieux logs si trop gros
rotate_log() {
    if [ -f "$LOG_FILE" ]; then
        SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
        if [ "$SIZE" -gt "$MAX_LOG_SIZE" ]; then
            mv "$LOG_FILE" "$LOG_FILE.old"
            log "Log rotaté (taille dépassée)"
        fi
    fi
}

# Fonction pour vérifier si le serveur répond
check_server_health() {
    # Vérifier d'abord si le processus existe
    SERVER_PID=$(pgrep -f "python.*server.py" | head -1)

    if [ -z "$SERVER_PID" ]; then
        return 1  # Processus non trouvé
    fi

    # Vérifier si le serveur répond sur le endpoint /health
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null)

    if [ "$HTTP_CODE" = "200" ]; then
        return 0  # Serveur OK
    else
        return 1  # Serveur ne répond pas
    fi
}

# Fonction pour démarrer le serveur
start_server() {
    log "🚀 Démarrage du serveur..."
    nohup env/bin/python server.py > server.log 2>&1 &

    # Attendre que le serveur démarre (Flask debug mode prend du temps)
    local max_attempts=10
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        sleep 2
        attempt=$((attempt + 1))

        if check_server_health; then
            SERVER_PID=$(pgrep -f "python.*server.py" | head -1)
            log "✅ Serveur démarré avec succès (PID: $SERVER_PID, tentative $attempt/$max_attempts)"
            return 0
        fi

        log "⏳ Attente du démarrage... ($attempt/$max_attempts)"
    done

    log "❌ Échec du démarrage du serveur après $max_attempts tentatives"
    return 1
}

# Fonction pour arrêter le serveur
stop_server() {
    SERVER_PID=$(pgrep -f "python.*server.py" | head -1)

    if [ -n "$SERVER_PID" ]; then
        log "🛑 Arrêt du serveur zombie (PID: $SERVER_PID)..."
        kill $SERVER_PID
        sleep 2

        # Vérifier si le processus est toujours là
        if pgrep -f "python.*server.py" > /dev/null; then
            log "⚠️  Arrêt forcé du serveur..."
            pkill -9 -f "python.*server.py"
            sleep 1
        fi
    fi
}

# Fonction principale de surveillance
watch_server() {
    log "👁️  Watchdog démarré - Vérification toutes les ${CHECK_INTERVAL}s"

    while true; do
        rotate_log

        if check_server_health; then
            SERVER_PID=$(pgrep -f "python.*server.py" | head -1)
            log "✅ Serveur OK (PID: $SERVER_PID)"
        else
            log "⚠️  ALERTE: Serveur non disponible!"

            # Arrêter tout processus zombie
            stop_server

            # Attendre un peu
            sleep 2

            # Redémarrer le serveur
            if start_server; then
                log "🔄 Redémarrage réussi"
            else
                log "❌ ERREUR: Impossible de redémarrer le serveur"
                # Attendre avant de réessayer
                sleep 10
            fi
        fi

        sleep $CHECK_INTERVAL
    done
}

# Fonction pour afficher l'aide
show_help() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}    SPOKE TTS WATCHDOG - AIDE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    echo "Usage: ./watchdog.sh [commande]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start     - Démarrer le watchdog en arrière-plan"
    echo "  stop      - Arrêter le watchdog"
    echo "  status    - Afficher le statut du watchdog"
    echo "  logs      - Afficher les logs du watchdog"
    echo "  run       - Lancer le watchdog en mode interactif (foreground)"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Le watchdog vérifie toutes les 2 minutes si le serveur est actif"
    echo "et le redémarre automatiquement en cas de crash."
    echo ""
}

# Fonction pour démarrer le watchdog en arrière-plan
start_watchdog() {
    WATCHDOG_PID=$(pgrep -f "bash.*watchdog.sh run" | head -1)

    if [ -n "$WATCHDOG_PID" ]; then
        echo -e "${YELLOW}⚠️  Le watchdog est déjà en cours d'exécution (PID: $WATCHDOG_PID)${NC}"
        return
    fi

    echo -e "${BLUE}🚀 Démarrage du watchdog en arrière-plan...${NC}"
    nohup bash "$0" run > /dev/null 2>&1 &
    sleep 1

    WATCHDOG_PID=$(pgrep -f "bash.*watchdog.sh run" | head -1)
    if [ -n "$WATCHDOG_PID" ]; then
        echo -e "${GREEN}✅ Watchdog démarré avec succès (PID: $WATCHDOG_PID)${NC}"
        echo -e "   Logs: tail -f $LOG_FILE"
    else
        echo -e "${RED}❌ Échec du démarrage du watchdog${NC}"
    fi
}

# Fonction pour arrêter le watchdog
stop_watchdog() {
    WATCHDOG_PID=$(pgrep -f "bash.*watchdog.sh run" | head -1)

    if [ -z "$WATCHDOG_PID" ]; then
        echo -e "${YELLOW}⚠️  Le watchdog n'est pas en cours d'exécution${NC}"
        return
    fi

    echo -e "${BLUE}🛑 Arrêt du watchdog (PID: $WATCHDOG_PID)...${NC}"
    kill $WATCHDOG_PID
    sleep 1

    # Vérifier si le processus est toujours là
    if pgrep -f "bash.*watchdog.sh run" > /dev/null; then
        echo -e "${YELLOW}⚠️  Arrêt forcé...${NC}"
        pkill -9 -f "bash.*watchdog.sh run"
    fi

    echo -e "${GREEN}✅ Watchdog arrêté${NC}"
}

# Fonction pour afficher le statut
show_status() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}    WATCHDOG STATUS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"

    WATCHDOG_PID=$(pgrep -f "bash.*watchdog.sh run" | head -1)

    if [ -n "$WATCHDOG_PID" ]; then
        echo -e "${GREEN}✅ Statut: EN COURS D'EXÉCUTION${NC}"
        echo -e "   PID: $WATCHDOG_PID"

        # Temps de fonctionnement
        UPTIME=$(ps -p $WATCHDOG_PID -o etime= 2>/dev/null | tr -d ' ')
        if [ -n "$UPTIME" ]; then
            echo -e "   Uptime: $UPTIME"
        fi

        # Dernières lignes du log
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo -e "${YELLOW}📝 Derniers logs:${NC}"
            tail -5 "$LOG_FILE" | sed 's/^/   /'
        fi
    else
        echo -e "${RED}❌ Statut: ARRÊTÉ${NC}"
    fi
    echo ""
}

# Fonction pour afficher les logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 Logs du watchdog (Ctrl+C pour quitter):${NC}"
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}❌ Fichier de logs non trouvé${NC}"
    fi
}

# Menu principal
case "$1" in
    start)
        start_watchdog
        ;;
    stop)
        stop_watchdog
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    run)
        # Mode interactif (appelé par start en arrière-plan)
        watch_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
