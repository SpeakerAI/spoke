"""
Marketplace Module - Gestion des voix premium avec Supabase
"""

import os
import json
from typing import List, Dict, Optional
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Client Supabase (initialisé si credentials disponibles)
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class MarketplaceManager:
    """Gestionnaire du marketplace de voix"""

    @staticmethod
    def init_user(user_id: str) -> bool:
        """
        Initialiser un nouvel utilisateur avec les 4 voix classiques
        """
        if not supabase:
            return False

        try:
            # Donner les 4 voix classiques
            classic_voices = [
                {'user_id': user_id, 'voice_id': 1, 'is_classic': True},
                {'user_id': user_id, 'voice_id': 2, 'is_classic': True},
                {'user_id': user_id, 'voice_id': 3, 'is_classic': True},
                {'user_id': user_id, 'voice_id': 4, 'is_classic': True}
            ]

            supabase.table('user_voices').upsert(classic_voices, on_conflict='user_id,voice_id').execute()
            return True
        except Exception as e:
            print(f"Error initializing user: {e}")
            return False

    @staticmethod
    def get_user_voices(user_id: str) -> List[int]:
        """
        Récupérer toutes les voix possédées par un utilisateur
        Retourne: Liste des voice_id (ex: [1, 2, 3, 4, 25, 32])
        """
        if not supabase:
            # Fallback: retourner les 4 voix classiques si pas de DB
            return [1, 2, 3, 4]

        try:
            response = supabase.table('user_voices')\
                .select('voice_id')\
                .eq('user_id', user_id)\
                .execute()

            return [voice['voice_id'] for voice in response.data]
        except Exception as e:
            print(f"Error getting user voices: {e}")
            return [1, 2, 3, 4]  # Fallback

    @staticmethod
    def has_voice(user_id: str, voice_id: int) -> bool:
        """
        Vérifier si un utilisateur possède une voix spécifique
        """
        voices = MarketplaceManager.get_user_voices(user_id)
        return voice_id in voices

    @staticmethod
    def get_marketplace_voices(limit: int = 50) -> List[Dict]:
        """
        Récupérer le catalogue des voix premium disponibles
        """
        if not supabase:
            return []

        try:
            response = supabase.table('marketplace_voices')\
                .select('*')\
                .eq('is_available', True)\
                .order('price')\
                .limit(limit)\
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting marketplace voices: {e}")
            return []

    @staticmethod
    def get_voice_details(voice_id: int) -> Optional[Dict]:
        """
        Récupérer les détails d'une voix du marketplace
        """
        if not supabase:
            return None

        try:
            response = supabase.table('marketplace_voices')\
                .select('*')\
                .eq('voice_id', voice_id)\
                .single()\
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting voice details: {e}")
            return None

    @staticmethod
    def purchase_voice(user_id: str, voice_id: int) -> tuple[bool, str]:
        """
        Acheter une voix (fake purchase - pas de paiement réel)
        Retourne: (success: bool, message: str)
        """
        if not supabase:
            return False, "Database not configured"

        try:
            # Vérifier que la voix existe et est disponible
            voice = MarketplaceManager.get_voice_details(voice_id)
            if not voice:
                return False, "Voice not found or not available"

            # Vérifier que l'utilisateur ne possède pas déjà cette voix
            if MarketplaceManager.has_voice(user_id, voice_id):
                return False, "You already own this voice"

            # Ajouter la voix à l'utilisateur
            supabase.table('user_voices').insert({
                'user_id': user_id,
                'voice_id': voice_id,
                'is_classic': False
            }).execute()

            # Enregistrer l'achat
            supabase.table('voice_purchases').insert({
                'user_id': user_id,
                'voice_id': voice_id,
                'price': voice['price']
            }).execute()

            return True, f"Successfully purchased {voice['name']}"
        except Exception as e:
            print(f"Error purchasing voice: {e}")
            return False, str(e)

    @staticmethod
    def get_purchased_voices(user_id: str) -> List[Dict]:
        """
        Récupérer les voix premium achetées par un utilisateur (pas les classiques)
        """
        if not supabase:
            return []

        try:
            response = supabase.table('user_voices')\
                .select('voice_id, acquired_at, marketplace_voices(*)')\
                .eq('user_id', user_id)\
                .eq('is_classic', False)\
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting purchased voices: {e}")
            return []

    @staticmethod
    def get_available_voices_for_user(user_id: str) -> Dict:
        """
        Récupérer toutes les voix disponibles pour un utilisateur
        Retourne: {
            "owned": [1, 2, 3, 4, 25, 32],
            "marketplace": [...],  # Voix pas encore achetées
            "total_owned": 6
        }
        """
        owned_voices = MarketplaceManager.get_user_voices(user_id)
        all_marketplace = MarketplaceManager.get_marketplace_voices()

        # Filtrer les voix du marketplace que l'user ne possède pas
        available_marketplace = [
            voice for voice in all_marketplace
            if voice['voice_id'] not in owned_voices
        ]

        return {
            'owned': owned_voices,
            'marketplace': available_marketplace,
            'total_owned': len(owned_voices)
        }


# ============================================
# Fonctions utilitaires pour fallback
# ============================================

def get_speaker_info(voice_id: int) -> Optional[Dict]:
    """
    Récupérer les infos d'un speaker depuis speaker_statistics.json
    """
    try:
        with open('speaker_statistics.json', 'r') as f:
            speakers = json.load(f)
            speaker_id = f"p{voice_id:03d}"
            return speakers.get(speaker_id)
    except Exception as e:
        print(f"Error reading speaker info: {e}")
        return None


def create_marketplace_voice_from_speaker(voice_id: int) -> Optional[Dict]:
    """
    Créer une entrée marketplace à partir des stats du speaker
    """
    speaker = get_speaker_info(voice_id)
    if not speaker:
        return None

    # Générer un nom basé sur les caractéristiques
    gender = speaker.get('gender', 'Unknown').title()
    age = speaker.get('age', 'Unknown')
    language = speaker.get('native language', 'Unknown').title()

    name = f"Speaker {voice_id} - {gender}, {age}"

    return {
        'voice_id': voice_id,
        'name': name,
        'description': f"{gender} voice, {age} years old, native {language} speaker",
        'gender': speaker.get('gender'),
        'age_range': age,
        'language': language,
        'price': 9.99  # Prix par défaut
    }


# ============================================
# Mode Fallback (sans Supabase)
# ============================================

class LocalMarketplace:
    """
    Marketplace local (fichier JSON) pour développement sans Supabase
    """

    DATA_FILE = 'local_marketplace.json'

    @staticmethod
    def _load_data():
        if os.path.exists(LocalMarketplace.DATA_FILE):
            with open(LocalMarketplace.DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_data(data):
        with open(LocalMarketplace.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def get_user_voices(user_id: str) -> List[int]:
        data = LocalMarketplace._load_data()
        user_data = data.get(user_id, {})
        return user_data.get('voices', [1, 2, 3, 4])

    @staticmethod
    def purchase_voice(user_id: str, voice_id: int) -> tuple[bool, str]:
        data = LocalMarketplace._load_data()

        if user_id not in data:
            data[user_id] = {'voices': [1, 2, 3, 4]}

        if voice_id in data[user_id]['voices']:
            return False, "Voice already owned"

        data[user_id]['voices'].append(voice_id)
        LocalMarketplace._save_data(data)

        return True, f"Voice {voice_id} purchased"
