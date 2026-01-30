/**
 * Intégration Simple - Système de Voix pour speaker-ai.vercel.app
 * 4 voix classiques (1,2,3,4) + Option Custom avec matching
 */

const API_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';

/**
 * Générer de l'audio avec une voix classique (1, 2, 3, ou 4)
 */
async function synthesizeWithClassicVoice(voiceNumber, text, emotion = 'neutral') {
  if (voiceNumber < 1 || voiceNumber > 4) {
    throw new Error('Classic voice must be between 1 and 4');
  }

  const response = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: voiceNumber  // Directement 1, 2, 3, ou 4
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Synthesis failed');
  }

  return await response.blob();
}

/**
 * Générer de l'audio avec une voix custom (via prompt)
 */
async function synthesizeWithCustomVoice(prompt, text, emotion = 'neutral') {
  // Étape 1: Trouver le meilleur speaker pour ce prompt
  const matchResponse = await fetch(`${API_URL}/match_voice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: prompt })
  });

  if (!matchResponse.ok) {
    throw new Error('Voice matching failed');
  }

  const matchData = await matchResponse.json();
  const bestSpeaker = matchData.speaker_nums[0];  // Meilleur match

  console.log(`Custom voice matched to speaker ${bestSpeaker}`);

  // Étape 2: Générer l'audio avec ce speaker
  const synthResponse = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: bestSpeaker
    })
  });

  if (!synthResponse.ok) {
    const error = await synthResponse.json();
    throw new Error(error.error || 'Synthesis failed');
  }

  return await synthResponse.blob();
}

/**
 * Jouer un audio blob
 */
function playAudio(audioBlob) {
  const url = URL.createObjectURL(audioBlob);
  const audio = new Audio(url);
  audio.onended = () => URL.revokeObjectURL(url);
  audio.play();
  return audio;
}

/**
 * Télécharger un audio blob
 */
function downloadAudio(audioBlob, filename = 'speech.wav') {
  const url = URL.createObjectURL(audioBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ==========================================
// EXEMPLES D'UTILISATION
// ==========================================

/**
 * Exemple 1: Utiliser une voix classique
 */
async function example1() {
  const text = "Bonjour, ceci est la voix numéro 1";
  const audioBlob = await synthesizeWithClassicVoice(1, text, 'joy');
  playAudio(audioBlob);
}

/**
 * Exemple 2: Utiliser une voix custom
 */
async function example2() {
  const prompt = "deep powerful male voice";
  const text = "Hello, this is a custom matched voice";
  const audioBlob = await synthesizeWithCustomVoice(prompt, text, 'neutral');
  playAudio(audioBlob);
}

/**
 * Exemple 3: Interface utilisateur complète
 */
class VoiceSystem {
  constructor() {
    this.mode = 'classic';  // 'classic' ou 'custom'
    this.selectedClassicVoice = 1;
    this.customPrompt = '';
  }

  // Sélectionner une voix classique
  selectClassicVoice(voiceNumber) {
    this.mode = 'classic';
    this.selectedClassicVoice = voiceNumber;
  }

  // Activer le mode custom
  selectCustomVoice(prompt) {
    this.mode = 'custom';
    this.customPrompt = prompt;
  }

  // Générer l'audio selon le mode sélectionné
  async generate(text, emotion = 'neutral') {
    if (this.mode === 'classic') {
      return await synthesizeWithClassicVoice(
        this.selectedClassicVoice,
        text,
        emotion
      );
    } else {
      return await synthesizeWithCustomVoice(
        this.customPrompt,
        text,
        emotion
      );
    }
  }
}

/**
 * Exemple 4: Intégration React
 */
function ReactExample() {
  /*
  import React, { useState } from 'react';

  function VoiceSelector() {
    const [mode, setMode] = useState('classic');
    const [classicVoice, setClassicVoice] = useState(1);
    const [customPrompt, setCustomPrompt] = useState('');
    const [text, setText] = useState('');
    const [emotion, setEmotion] = useState('neutral');
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerate = async () => {
      setIsGenerating(true);
      try {
        let audioBlob;

        if (mode === 'classic') {
          audioBlob = await synthesizeWithClassicVoice(classicVoice, text, emotion);
        } else {
          audioBlob = await synthesizeWithCustomVoice(customPrompt, text, emotion);
        }

        playAudio(audioBlob);
      } catch (error) {
        console.error('Error:', error);
        alert(error.message);
      } finally {
        setIsGenerating(false);
      }
    };

    return (
      <div>
        <h2>Voice Selection</h2>

        {/* Mode selector *\/}
        <div>
          <button onClick={() => setMode('classic')}>Classic Voices</button>
          <button onClick={() => setMode('custom')}>Custom Voice</button>
        </div>

        {/* Classic voice selector *\/}
        {mode === 'classic' && (
          <select value={classicVoice} onChange={(e) => setClassicVoice(Number(e.target.value))}>
            <option value={1}>Voice 1</option>
            <option value={2}>Voice 2</option>
            <option value={3}>Voice 3</option>
            <option value={4}>Voice 4</option>
          </select>
        )}

        {/* Custom voice input *\/}
        {mode === 'custom' && (
          <input
            type="text"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Describe the voice (e.g., 'deep male voice')"
          />
        )}

        {/* Text input *\/}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to synthesize..."
        />

        {/* Emotion selector *\/}
        <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
          <option value="neutral">Neutral</option>
          <option value="joy">Joy</option>
          <option value="anger">Anger</option>
          <option value="sadness">Sadness</option>
          <option value="fear">Fear</option>
        </select>

        {/* Generate button *\/}
        <button onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate Speech'}
        </button>
      </div>
    );
  }
  */
}

/**
 * Exemple 5: HTML Vanilla JS
 */
function setupHTMLExample() {
  /*
  <!-- HTML Structure -->
  <div id="voice-app">
    <h2>Voice Selection</h2>

    <!-- Mode Tabs -->
    <div class="mode-tabs">
      <button onclick="setMode('classic')" id="classic-tab">Classic Voices</button>
      <button onclick="setMode('custom')" id="custom-tab">Custom Voice</button>
    </div>

    <!-- Classic Voice Selector (shown when mode === 'classic') -->
    <div id="classic-selector" style="display: block;">
      <select id="classic-voice">
        <option value="1">Voice 1</option>
        <option value="2">Voice 2</option>
        <option value="3">Voice 3</option>
        <option value="4">Voice 4</option>
      </select>
    </div>

    <!-- Custom Voice Input (shown when mode === 'custom') -->
    <div id="custom-selector" style="display: none;">
      <input
        type="text"
        id="custom-prompt"
        placeholder="Describe the voice (e.g., 'young female energetic voice')"
      />
    </div>

    <!-- Common inputs -->
    <textarea id="text-input" placeholder="Enter text to synthesize..."></textarea>

    <select id="emotion-select">
      <option value="neutral">Neutral</option>
      <option value="joy">Joy</option>
      <option value="anger">Anger</option>
      <option value="sadness">Sadness</option>
      <option value="fear">Fear</option>
    </select>

    <button onclick="generateSpeech()">Generate Speech</button>
    <div id="status"></div>
  </div>

  <script>
    let currentMode = 'classic';

    function setMode(mode) {
      currentMode = mode;
      document.getElementById('classic-selector').style.display = mode === 'classic' ? 'block' : 'none';
      document.getElementById('custom-selector').style.display = mode === 'custom' ? 'block' : 'none';
    }

    async function generateSpeech() {
      const text = document.getElementById('text-input').value;
      const emotion = document.getElementById('emotion-select').value;
      const status = document.getElementById('status');

      if (!text) {
        status.textContent = 'Please enter text';
        return;
      }

      status.textContent = 'Generating...';

      try {
        let audioBlob;

        if (currentMode === 'classic') {
          const voiceNum = parseInt(document.getElementById('classic-voice').value);
          audioBlob = await synthesizeWithClassicVoice(voiceNum, text, emotion);
        } else {
          const prompt = document.getElementById('custom-prompt').value;
          if (!prompt) {
            status.textContent = 'Please describe the voice';
            return;
          }
          audioBlob = await synthesizeWithCustomVoice(prompt, text, emotion);
        }

        playAudio(audioBlob);
        status.textContent = 'Audio generated!';
      } catch (error) {
        status.textContent = 'Error: ' + error.message;
        console.error(error);
      }
    }
  </script>
  */
}

// Export pour utilisation ES modules
export {
  synthesizeWithClassicVoice,
  synthesizeWithCustomVoice,
  playAudio,
  downloadAudio,
  VoiceSystem
};
