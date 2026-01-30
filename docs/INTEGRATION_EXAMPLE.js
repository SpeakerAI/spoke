/**
 * Exemple d'intégration du système de matching vocal
 * Pour speaker-ai.vercel.app
 */

const API_BASE_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';

/**
 * Configuration des 4 profils vocaux présentés à l'utilisateur
 */
const VOICE_PROFILES = [
  {
    id: 1,
    name: "Jeune Femme Énergique",
    description: "Voix féminine jeune et dynamique, parfaite pour du contenu énergique",
    prompt: "young energetic female voice with American accent",
    defaultEmotion: "joy"
  },
  {
    id: 2,
    name: "Homme Mature Autoritaire",
    description: "Voix masculine mature et confiante, idéale pour du contenu professionnel",
    prompt: "mature authoritative male voice",
    defaultEmotion: "neutral"
  },
  {
    id: 3,
    name: "Femme Douce et Chaleureuse",
    description: "Voix féminine douce et apaisante, parfaite pour du contenu relaxant",
    prompt: "gentle warm female voice middle-aged",
    defaultEmotion: "neutral"
  },
  {
    id: 4,
    name: "Homme Puissant et Profond",
    description: "Voix masculine grave et puissante, idéale pour des narrations",
    prompt: "deep powerful male voice",
    defaultEmotion: "neutral"
  }
];

/**
 * Cache des speakers matchés pour chaque profil
 * Évite de refaire le matching à chaque fois
 */
let speakerCache = {};

/**
 * Trouve les meilleurs speakers pour un profil vocal
 */
async function findSpeakersForProfile(profile) {
  // Vérifier le cache
  if (speakerCache[profile.id]) {
    console.log(`Using cached speakers for profile ${profile.id}`);
    return speakerCache[profile.id];
  }

  try {
    const response = await fetch(`${API_BASE_URL}/match_voice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: profile.prompt
      })
    });

    if (!response.ok) {
      throw new Error(`Voice matching failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Mettre en cache
    speakerCache[profile.id] = data.speaker_nums;

    console.log(`Found speakers for ${profile.name}:`, data.speaker_nums);

    return data.speaker_nums;
  } catch (error) {
    console.error('Error matching voice:', error);
    // Fallback sur des speakers par défaut
    return [1, 2, 3, 4];
  }
}

/**
 * Génère de l'audio avec un profil vocal spécifique
 */
async function synthesizeWithProfile(profileId, text, emotion = null) {
  // Trouver le profil
  const profile = VOICE_PROFILES.find(p => p.id === profileId);
  if (!profile) {
    throw new Error(`Profile ${profileId} not found`);
  }

  // Obtenir les speakers pour ce profil
  const speakers = await findSpeakersForProfile(profile);

  // Utiliser le meilleur speaker (le premier de la liste)
  const bestSpeaker = speakers[0];

  // Utiliser l'émotion par défaut du profil si non spécifiée
  const selectedEmotion = emotion || profile.defaultEmotion;

  console.log(`Synthesizing with profile "${profile.name}" (speaker ${bestSpeaker}, emotion ${selectedEmotion})`);

  try {
    const response = await fetch(`${API_BASE_URL}/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        emotion: selectedEmotion,
        speaker_id: bestSpeaker
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Synthesis failed');
    }

    // Retourner le blob audio
    const audioBlob = await response.blob();
    return audioBlob;
  } catch (error) {
    console.error('Error synthesizing audio:', error);
    throw error;
  }
}

/**
 * Pré-charge les speakers pour tous les profils au démarrage
 */
async function preloadAllVoiceProfiles() {
  console.log('Preloading voice profiles...');

  const promises = VOICE_PROFILES.map(profile =>
    findSpeakersForProfile(profile)
  );

  await Promise.all(promises);

  console.log('All voice profiles preloaded!', speakerCache);
}

/**
 * Joue un audio depuis un blob
 */
function playAudioBlob(blob) {
  const audioUrl = URL.createObjectURL(blob);
  const audio = new Audio(audioUrl);

  audio.onended = () => {
    URL.revokeObjectURL(audioUrl); // Libérer la mémoire
  };

  audio.play();
  return audio;
}

/**
 * Télécharge un audio depuis un blob
 */
function downloadAudioBlob(blob, filename = 'speech.wav') {
  const audioUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = audioUrl;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(audioUrl);
}

// ========================================
// Exemples d'utilisation
// ========================================

/**
 * Exemple 1: Initialisation au chargement de la page
 */
async function initializeVoiceSystem() {
  // Pré-charger tous les profils vocaux
  await preloadAllVoiceProfiles();

  // Maintenant les profils sont prêts à être utilisés instantanément
  console.log('Voice system ready!');
}

/**
 * Exemple 2: Utilisation simple
 */
async function simpleExample() {
  const text = "Bonjour, ceci est un test du système de synthèse vocale.";

  // Utiliser le profil 1 (Jeune Femme Énergique)
  const audioBlob = await synthesizeWithProfile(1, text);

  // Jouer l'audio
  playAudioBlob(audioBlob);
}

/**
 * Exemple 3: Avec sélection d'émotion
 */
async function emotionExample() {
  const text = "Je suis vraiment très en colère !";

  // Utiliser le profil 2 avec l'émotion "anger"
  const audioBlob = await synthesizeWithProfile(2, text, "anger");

  playAudioBlob(audioBlob);
}

/**
 * Exemple 4: Interface utilisateur complète
 */
class VoiceSynthesizer {
  constructor() {
    this.currentProfile = null;
    this.isLoading = false;
  }

  async initialize() {
    await preloadAllVoiceProfiles();
  }

  selectProfile(profileId) {
    this.currentProfile = VOICE_PROFILES.find(p => p.id === profileId);
    console.log('Selected profile:', this.currentProfile?.name);
  }

  async generateSpeech(text, emotion = null) {
    if (!this.currentProfile) {
      throw new Error('No profile selected');
    }

    if (this.isLoading) {
      throw new Error('Already generating speech');
    }

    this.isLoading = true;

    try {
      const audioBlob = await synthesizeWithProfile(
        this.currentProfile.id,
        text,
        emotion
      );

      return audioBlob;
    } finally {
      this.isLoading = false;
    }
  }

  getAvailableProfiles() {
    return VOICE_PROFILES;
  }

  getCurrentProfile() {
    return this.currentProfile;
  }
}

/**
 * Exemple 5: Intégration React
 */
function ReactExample() {
  /*
  import React, { useState, useEffect } from 'react';

  function VoiceSelector() {
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState(null);
    const [text, setText] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
      // Initialiser le système au montage du composant
      preloadAllVoiceProfiles();
      setProfiles(VOICE_PROFILES);
    }, []);

    const handleGenerate = async () => {
      if (!selectedProfile || !text) return;

      setIsGenerating(true);
      try {
        const audioBlob = await synthesizeWithProfile(selectedProfile, text);
        playAudioBlob(audioBlob);
      } catch (error) {
        console.error('Generation failed:', error);
        alert('Erreur lors de la génération audio');
      } finally {
        setIsGenerating(false);
      }
    };

    return (
      <div>
        <h2>Sélectionnez une voix</h2>
        <select
          value={selectedProfile || ''}
          onChange={(e) => setSelectedProfile(Number(e.target.value))}
        >
          <option value="">-- Choisir une voix --</option>
          {profiles.map(profile => (
            <option key={profile.id} value={profile.id}>
              {profile.name} - {profile.description}
            </option>
          ))}
        </select>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Entrez le texte à synthétiser..."
          rows={4}
        />

        <button onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? 'Génération...' : 'Générer la parole'}
        </button>
      </div>
    );
  }
  */
}

// Export pour utilisation dans d'autres fichiers
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    VOICE_PROFILES,
    findSpeakersForProfile,
    synthesizeWithProfile,
    preloadAllVoiceProfiles,
    playAudioBlob,
    downloadAudioBlob,
    VoiceSynthesizer
  };
}
