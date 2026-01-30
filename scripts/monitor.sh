#!/bin/bash

# Moniteur en temps réel pour le serveur Spoke TTS

REFRESH_RATE=2  # Secondes entre les rafraîchissements

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

function get_log_file() {
    LOG_FILE=$(ls -t /tmp/claude/-home-ubuntu-spoke/tasks/*.output 2>/dev/null | head -1)
    if [ -z "$LOG_FILE" ]; then
        LOG_FILE="server.log"
    fi
    echo "$LOG_FILE"
}

function show_dashboard() {
    clear

    LOG_FILE=$(get_log_file)
    SERVER_PID=$(pgrep -f "python.*server.py" | head -1)

    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         SPOKE TTS SERVER - MONITORING DASHBOARD               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Statut du serveur
    if [ -n "$SERVER_PID" ]; then
        echo -e "${GREEN}● SERVEUR EN LIGNE${NC} (PID: $SERVER_PID)"

        # Temps de fonctionnement
        UPTIME=$(ps -p $SERVER_PID -o etime= 2>/dev/null | tr -d ' ')
        if [ -n "$UPTIME" ]; then
            echo -e "  Temps de fonctionnement: ${CYAN}$UPTIME${NC}"
        fi

        # Utilisation CPU et mémoire
        CPU_MEM=$(ps -p $SERVER_PID -o %cpu,%mem 2>/dev/null | tail -1)
        if [ -n "$CPU_MEM" ]; then
            echo -e "  Ressources: ${CYAN}$CPU_MEM${NC} (CPU% MEM%)"
        fi
    else
        echo -e "${RED}● SERVEUR HORS LIGNE${NC}"
    fi

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────${NC}"
    echo ""

    # Statistiques
    if [ -f "$LOG_FILE" ]; then
        PING_COUNT=$(grep -c "Received ping request" "$LOG_FILE" 2>/dev/null || echo 0)
        HEALTH_COUNT=$(grep -c "Health check request" "$LOG_FILE" 2>/dev/null || echo 0)
        SYNTH_COUNT=$(grep -c "Synthesis request" "$LOG_FILE" 2>/dev/null || echo 0)
        ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo 0)
        SUCCESS_COUNT=$(grep -c "Audio generated successfully" "$LOG_FILE" 2>/dev/null || echo 0)

        echo -e "${YELLOW}📊 STATISTIQUES DES REQUÊTES${NC}"
        echo -e "  /ping:        ${CYAN}$PING_COUNT${NC} requêtes"
        echo -e "  /health:      ${CYAN}$HEALTH_COUNT${NC} requêtes"
        echo -e "  /synthesize:  ${CYAN}$SYNTH_COUNT${NC} requêtes"
        echo -e "  Succès:       ${GREEN}$SUCCESS_COUNT${NC}"
        echo -e "  Erreurs:      ${RED}$ERROR_COUNT${NC}"
    else
        echo -e "${YELLOW}📊 STATISTIQUES: Aucun log disponible${NC}"
    fi

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────${NC}"
    echo ""

    # Activité récente
    echo -e "${YELLOW}📝 ACTIVITÉ RÉCENTE (10 dernières lignes)${NC}"
    if [ -f "$LOG_FILE" ]; then
        tail -10 "$LOG_FILE" | grep -E "(INFO|ERROR|WARNING)" | while IFS= read -r line; do
            if echo "$line" | grep -q "ERROR"; then
                echo -e "  ${RED}$line${NC}"
            elif echo "$line" | grep -q "WARNING"; then
                echo -e "  ${YELLOW}$line${NC}"
            elif echo "$line" | grep -q "Synthesis request"; then
                echo -e "  ${CYAN}$line${NC}"
            elif echo "$line" | grep -q "Audio generated"; then
                echo -e "  ${GREEN}$line${NC}"
            else
                echo -e "  $line"
            fi
        done
    else
        echo -e "  ${RED}Aucun log disponible${NC}"
    fi

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────────────${NC}"
    echo ""
    echo -e "${CYAN}Rafraîchissement: ${REFRESH_RATE}s | Appuyez sur Ctrl+C pour quitter${NC}"
}

# Boucle principale
echo "Démarrage du moniteur..."
trap 'echo -e "\n${GREEN}Moniteur arrêté.${NC}"; exit 0' INT

while true; do
    show_dashboard
    sleep $REFRESH_RATE
done
