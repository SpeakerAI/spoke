import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import uuid
from dotenv import load_dotenv
from server.inference_engine import synthesize
from server.voice_matcher import match_voices, match_voices_simple, get_voice_description
from server.marketplace import MarketplaceManager

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory relative to repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "output_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/ping', methods=['GET'])
def ping():
    logger.info("Received ping request")
    return jsonify({
        "status": "success",
        "message": "Spoke TTS server is running"
    }), 200

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check request")
    return jsonify({
        "status": "healthy",
        "service": "Spoke TTS"
    }), 200

@app.route('/random_voice', methods=['POST'])
def random_voice():
    """
    Get a random speaker by gender
    Request body: { "gender": "male" or "female" }
    Response: { "speaker_id": "p032", "speaker_num": 32, "profile": {...} }
    """
    try:
        import random
        import json

        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        gender = data.get('gender', '').lower()
        if gender not in ['male', 'female']:
            return jsonify({"error": "gender must be 'male' or 'female'"}), 400

        logger.info(f"Random voice request - Gender: {gender}")

        # Charger les speaker statistics
        with open('speaker_statistics.json', 'r') as f:
            speakers = json.load(f)

        # Filtrer les speakers 5-107 par genre
        available_speakers = []
        for speaker_id, profile in speakers.items():
            speaker_num = int(speaker_id[1:])  # p032 -> 32
            if speaker_num >= 5 and speaker_num <= 107:
                if profile['gender'] == gender:
                    available_speakers.append({
                        'speaker_id': speaker_id,
                        'speaker_num': speaker_num,
                        'profile': profile
                    })

        if not available_speakers:
            return jsonify({"error": f"No {gender} speakers found"}), 404

        # Choisir un speaker aléatoire
        selected = random.choice(available_speakers)

        logger.info(f"Random {gender} voice selected: {selected['speaker_id']}")

        return jsonify({
            "speaker_id": selected['speaker_id'],
            "speaker_num": selected['speaker_num'],
            "gender": gender,
            "profile": selected['profile'],
            "description": get_voice_description(selected['speaker_id'])
        }), 200

    except Exception as e:
        import traceback
        logger.error(f"Error getting random voice: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Random voice failed: {str(e)}"
        }), 500

@app.route('/marketplace/catalog', methods=['GET'])
def marketplace_catalog():
    """
    Get the catalog of available premium voices
    Response: List of voices available for purchase
    """
    try:
        logger.info("Marketplace catalog request")
        voices = MarketplaceManager.get_marketplace_voices(limit=50)

        return jsonify({
            "voices": voices,
            "total": len(voices)
        }), 200
    except Exception as e:
        logger.error(f"Error getting marketplace catalog: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/marketplace/purchase', methods=['POST'])
def marketplace_purchase():
    """
    Purchase a voice (fake purchase)
    Request: { "user_id": "xxx", "voice_id": 25 }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_id = data.get('user_id')
        voice_id = data.get('voice_id')

        if not user_id or not voice_id:
            return jsonify({"error": "Missing user_id or voice_id"}), 400

        logger.info(f"Purchase request - User: {user_id}, Voice: {voice_id}")

        success, message = MarketplaceManager.purchase_voice(user_id, voice_id)

        if success:
            return jsonify({
                "success": True,
                "message": message,
                "voice_id": voice_id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400

    except Exception as e:
        logger.error(f"Error purchasing voice: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/voices/available', methods=['GET'])
def user_available_voices():
    """
    Get all voices available for a user (owned + marketplace)
    Query param: user_id
    """
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        logger.info(f"Available voices request for user: {user_id}")

        # S'assurer que l'utilisateur a les voix classiques
        MarketplaceManager.init_user(user_id)

        # Récupérer toutes les voix disponibles
        result = MarketplaceManager.get_available_voices_for_user(user_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting available voices: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/voices/owned', methods=['GET'])
def user_owned_voices():
    """
    Get voices owned by a user
    Query param: user_id
    """
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        logger.info(f"Owned voices request for user: {user_id}")

        # S'assurer que l'utilisateur a les voix classiques
        MarketplaceManager.init_user(user_id)

        voices = MarketplaceManager.get_user_voices(user_id)

        return jsonify({
            "user_id": user_id,
            "voices": voices,
            "total": len(voices)
        }), 200

    except Exception as e:
        logger.error(f"Error getting owned voices: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/synthesize', methods=['POST'])
def synthesize_audio():
    try:
        data = request.get_json()

        # Validation des paramètres
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        text = data.get('text')
        emotion = data.get('emotion')
        speaker_id = data.get('speaker_id')
        user_id = data.get('user_id')  # Optionnel pour vérification

        if not text:
            return jsonify({"error": "Missing 'text' parameter"}), 400
        if not emotion:
            return jsonify({"error": "Missing 'emotion' parameter"}), 400
        if not speaker_id:
            return jsonify({"error": "Missing 'speaker_id' parameter"}), 400

        # Validation de speaker_id (doit être entre 1 et 107)
        try:
            speaker_num = int(speaker_id)
            if speaker_num < 1 or speaker_num > 107:
                return jsonify({"error": "speaker_id must be between 1 and 107"}), 400
        except ValueError:
            return jsonify({"error": "speaker_id must be a number"}), 400

        # Vérifier que l'utilisateur possède cette voix (si user_id fourni)
        if user_id:
            if not MarketplaceManager.has_voice(user_id, speaker_num):
                return jsonify({
                    "error": "You don't own this voice. Please purchase it from the marketplace."
                }), 403

        # Format speaker_id en p001, p002, etc.
        speaker_id_formatted = f"p{speaker_num:03d}"

        # Validation de l'émotion (toutes les 21 émotions disponibles)
        valid_emotions = [
            "anger", "sadness", "joy", "fear", "neutral",
            "amusement", "contentment", "adoration", "amazement",
            "confusion", "cuteness", "desire", "disappointment",
            "disgust", "distress", "embarassment", "extasy",
            "guilt", "interest", "pain", "pride"
        ]
        if emotion.lower() not in valid_emotions:
            return jsonify({
                "error": f"Invalid emotion. Must be one of: {', '.join(valid_emotions)}"
            }), 400

        logger.info(f"Synthesis request - Text: '{text[:50]}...', Emotion: {emotion}, Speaker: {speaker_id_formatted}")

        # Générer un nom de fichier unique
        output_filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Appeler la fonction de synthèse
        synthesize(
            emotion=emotion.lower(),
            speaker_id=speaker_id_formatted,
            text=text,
            output=output_path
        )

        logger.info(f"Audio generated successfully: {output_filename}")

        # Renvoyer le fichier audio
        return send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=output_filename
        )

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            "error": f"Speaker or emotion file not found: {str(e)}"
        }), 404
    except Exception as e:
        import traceback
        logger.error(f"Error during synthesis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Synthesis failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("Starting Spoke TTS server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
