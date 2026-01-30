#!/bin/bash

# Script pour lister tous les fichiers audio disponibles par émotion

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        SPOKE TTS - FICHIERS AUDIO DISPONIBLES                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd /home/ubuntu/spoke

for emotion_dir in emotions/*/; do
    emotion=$(basename "$emotion_dir")

    # Compter les fichiers disponibles
    wav_files=$(find "$emotion_dir" -name "p*_emo_${emotion}_sentences.wav" | sort)
    count=$(echo "$wav_files" | grep -c ".")

    if [ $count -gt 0 ]; then
        echo -e "${YELLOW}━━━ ${emotion^^} (${count} voix disponibles) ━━━${NC}"

        # Extraire les IDs des speakers
        speakers=$(echo "$wav_files" | grep -o "p[0-9]*_emo" | sed 's/_emo//' | sort -u)

        # Afficher les speakers par ligne de 10
        echo -n "  Speakers: "
        counter=0
        for speaker in $speakers; do
            echo -n "${GREEN}$speaker${NC} "
            counter=$((counter + 1))
            if [ $((counter % 10)) -eq 0 ]; then
                echo ""
                echo -n "            "
            fi
        done
        echo ""
        echo ""
    fi
done

echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Usage dans l'API:${NC}"
echo -e '  {"text": "Hello", "emotion": "anger", "speaker_id": 1}'
echo ""
echo -e "${YELLOW}Note:${NC} speaker_id doit être un nombre entre 1 et le nombre de voix disponibles"
echo ""
