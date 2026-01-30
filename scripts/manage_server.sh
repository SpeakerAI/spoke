#!/bin/bash

# Script de gestion du serveur Spoke TTS

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_status() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}    SPOKE TTS SERVER STATUS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"

    SERVER_PID=$(pgrep -f "python.*server.server" | head -1)

    if [ -n "$SERVER_PID" ]; then
        echo -e "${GREEN}✅ Statut: EN COURS D'EXÉCUTION${NC}"
        echo -e "   PID: $SERVER_PID"
        echo -e "   Port: 5000"
        echo -e "   URL locale: http://localhost:5000"
        echo -e "   URL publique: http://51.210.165.192:5000"

        # Afficher les dernières lignes de log
        LOG_FILE=$(ls -t /tmp/claude/-home-ubuntu-spoke/tasks/*.output 2>/dev/null | head -1)
        if [ -n "$LOG_FILE" ]; then
            echo ""
            echo -e "${YELLOW}📝 Derniers logs:${NC}"
            tail -5 "$LOG_FILE" | sed 's/^/   /'
        fi
    else
        echo -e "${RED}❌ Statut: ARRÊTÉ${NC}"
    fi
    echo ""
}

function start_server() {
    SERVER_PID=$(pgrep -f "python.*server.server" | head -1)

    if [ -n "$SERVER_PID" ]; then
        echo -e "${YELLOW}⚠️  Le serveur est déjà en cours d'exécution (PID: $SERVER_PID)${NC}"
        return
    fi

    echo -e "${BLUE}🚀 Démarrage du serveur Spoke TTS...${NC}"
    nohup env/bin/python -m server.server > server.log 2>&1 &
    sleep 2

    SERVER_PID=$(pgrep -f "python.*server.server" | head -1)
    if [ -n "$SERVER_PID" ]; then
        echo -e "${GREEN}✅ Serveur démarré avec succès (PID: $SERVER_PID)${NC}"
        echo -e "   URL: http://51.210.165.192:5000"
    else
        echo -e "${RED}❌ Échec du démarrage du serveur${NC}"
        echo -e "${YELLOW}Vérifiez les logs: tail -f server.log${NC}"
    fi
}

function stop_server() {
    SERVER_PID=$(pgrep -f "python.*server.server" | head -1)

    if [ -z "$SERVER_PID" ]; then
        echo -e "${YELLOW}⚠️  Le serveur n'est pas en cours d'exécution${NC}"
        return
    fi

    echo -e "${BLUE}🛑 Arrêt du serveur (PID: $SERVER_PID)...${NC}"
    kill $SERVER_PID
    sleep 1

    # Vérifier si le processus est toujours là
    if pgrep -f "python.*server.server" > /dev/null; then
        echo -e "${YELLOW}⚠️  Arrêt forcé...${NC}"
        pkill -9 -f "python.*server.server"
    fi

    echo -e "${GREEN}✅ Serveur arrêté${NC}"
}

function restart_server() {
    echo -e "${BLUE}🔄 Redémarrage du serveur...${NC}"
    stop_server
    sleep 1
    start_server
}

function show_logs() {
    LOG_FILE=$(ls -t /tmp/claude/-home-ubuntu-spoke/tasks/*.output 2>/dev/null | head -1)

    if [ -z "$LOG_FILE" ]; then
        LOG_FILE="server.log"
    fi

    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📋 Logs du serveur (Ctrl+C pour quitter):${NC}"
        echo -e "${BLUE}═══════════════════════════════════════${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}❌ Fichier de logs non trouvé${NC}"
    fi
}

function show_stats() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}    STATISTIQUES DU SERVEUR${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"

    LOG_FILE=$(ls -t /tmp/claude/-home-ubuntu-spoke/tasks/*.output 2>/dev/null | head -1)

    if [ -z "$LOG_FILE" ]; then
        LOG_FILE="server.log"
    fi

    if [ -f "$LOG_FILE" ]; then
        echo -e "${GREEN}Requêtes /ping:${NC}"
        grep "Received ping request" "$LOG_FILE" | wc -l

        echo -e "${GREEN}Requêtes /health:${NC}"
        grep "Health check request" "$LOG_FILE" | wc -l

        echo -e "${GREEN}Requêtes /synthesize:${NC}"
        grep "Synthesis request" "$LOG_FILE" | wc -l

        echo -e "${GREEN}Erreurs:${NC}"
        grep "ERROR" "$LOG_FILE" | wc -l

        echo ""
        echo -e "${YELLOW}Dernières requêtes:${NC}"
        grep -E "(Received ping request|Health check request|Synthesis request)" "$LOG_FILE" | tail -5
    else
        echo -e "${RED}❌ Fichier de logs non trouvé${NC}"
    fi
    echo ""
}

function show_help() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}    SPOKE TTS SERVER - AIDE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    echo "Usage: ./manage_server.sh [commande]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start     - Démarrer le serveur"
    echo "  stop      - Arrêter le serveur"
    echo "  restart   - Redémarrer le serveur"
    echo "  status    - Afficher le statut du serveur"
    echo "  logs      - Afficher les logs en temps réel"
    echo "  stats     - Afficher les statistiques"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./manage_server.sh start"
    echo "  ./manage_server.sh logs"
    echo "  ./manage_server.sh status"
    echo ""
    echo -e "${YELLOW}🛡️  Surveillance automatique:${NC}"
    echo "  Pour un redémarrage automatique en cas de crash:"
    echo "  ./watchdog.sh start"
    echo ""
    echo "  Documentation: QUICK_START_WATCHDOG.md"
    echo ""
}

# Menu principal
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
