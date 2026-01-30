/**
 * Intégration Ultra-Simple - speaker-ai.vercel.app
 *
 * 4 voix classiques (1, 2, 3, 4) + Random Homme/Femme
 */

const API_URL = 'https://thousands-violations-suspension-premiere.trycloudflare.com';

/**
 * Générer de l'audio avec une voix classique (1, 2, 3, ou 4)
 */
async function synthesizeClassic(voiceNumber, text, emotion = 'neutral') {
  if (voiceNumber < 1 || voiceNumber > 4) {
    throw new Error('Voice number must be between 1 and 4');
  }

  const response = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: voiceNumber
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Synthesis failed');
  }

  return await response.blob();
}

/**
 * Générer de l'audio avec une voix random (homme ou femme)
 */
async function synthesizeRandom(gender, text, emotion = 'neutral') {
  if (gender !== 'male' && gender !== 'female') {
    throw new Error('Gender must be "male" or "female"');
  }

  // Étape 1: Obtenir un speaker random
  const randomResponse = await fetch(`${API_URL}/random_voice`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gender: gender })
  });

  if (!randomResponse.ok) {
    throw new Error('Failed to get random voice');
  }

  const randomData = await randomResponse.json();
  const speakerNum = randomData.speaker_num;

  console.log(`Random ${gender} voice: speaker ${speakerNum}`);

  // Étape 2: Générer l'audio avec ce speaker
  const synthResponse = await fetch(`${API_URL}/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      emotion: emotion,
      speaker_id: speakerNum
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
 * Exemple 1: Voix classique
 */
async function example1() {
  const audio = await synthesizeClassic(1, "Bonjour, ceci est la voix 1", "joy");
  playAudio(audio);
}

/**
 * Exemple 2: Voix random homme
 */
async function example2() {
  const audio = await synthesizeRandom("male", "Hello, I'm a random male voice", "neutral");
  playAudio(audio);
}

/**
 * Exemple 3: Voix random femme
 */
async function example3() {
  const audio = await synthesizeRandom("female", "Hello, I'm a random female voice", "joy");
  playAudio(audio);
}

/**
 * Classe pour gérer le système de voix
 */
class SimpleVoiceSystem {
  constructor() {
    this.type = 'classic';  // 'classic' ou 'random'
    this.classicVoice = 1;  // 1, 2, 3, ou 4
    this.randomGender = 'male';  // 'male' ou 'female'
  }

  selectClassic(voiceNumber) {
    this.type = 'classic';
    this.classicVoice = voiceNumber;
  }

  selectRandom(gender) {
    this.type = 'random';
    this.randomGender = gender;
  }

  async generate(text, emotion = 'neutral') {
    if (this.type === 'classic') {
      return await synthesizeClassic(this.classicVoice, text, emotion);
    } else {
      return await synthesizeRandom(this.randomGender, text, emotion);
    }
  }
}

// ==========================================
// INTÉGRATION REACT
// ==========================================

function ReactExample() {
  /*
  import React, { useState } from 'react';

  function VoiceSelector() {
    const [voiceType, setVoiceType] = useState('classic'); // 'classic' ou 'random'
    const [classicVoice, setClassicVoice] = useState(1);
    const [randomGender, setRandomGender] = useState('male');
    const [text, setText] = useState('');
    const [emotion, setEmotion] = useState('neutral');
    const [loading, setLoading] = useState(false);

    const handleGenerate = async () => {
      if (!text) return;

      setLoading(true);
      try {
        let audioBlob;

        if (voiceType === 'classic') {
          audioBlob = await synthesizeClassic(classicVoice, text, emotion);
        } else {
          audioBlob = await synthesizeRandom(randomGender, text, emotion);
        }

        playAudio(audioBlob);
      } catch (error) {
        alert('Error: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="voice-selector">
        <h2>Select Voice Type</h2>

        {/* Type selector *\/}
        <div className="type-buttons">
          <button
            onClick={() => setVoiceType('classic')}
            className={voiceType === 'classic' ? 'active' : ''}
          >
            Classic Voices
          </button>
          <button
            onClick={() => setVoiceType('random')}
            className={voiceType === 'random' ? 'active' : ''}
          >
            Random Voice
          </button>
        </div>

        {/* Classic voice selector *\/}
        {voiceType === 'classic' && (
          <div className="classic-selector">
            <label>Choose a classic voice:</label>
            <select value={classicVoice} onChange={(e) => setClassicVoice(Number(e.target.value))}>
              <option value={1}>Voice 1</option>
              <option value={2}>Voice 2</option>
              <option value={3}>Voice 3</option>
              <option value={4}>Voice 4</option>
            </select>
          </div>
        )}

        {/* Random gender selector *\/}
        {voiceType === 'random' && (
          <div className="random-selector">
            <label>Choose gender:</label>
            <select value={randomGender} onChange={(e) => setRandomGender(e.target.value)}>
              <option value="male">Male Voice</option>
              <option value="female">Female Voice</option>
            </select>
          </div>
        )}

        {/* Text input *\/}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to synthesize..."
          rows={4}
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
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Speech'}
        </button>
      </div>
    );
  }

  export default VoiceSelector;
  */
}

// ==========================================
// HTML VANILLA JS
// ==========================================

function HTMLExample() {
  /*
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Voice Synthesizer</title>
    <style>
      .voice-selector { max-width: 600px; margin: 50px auto; padding: 20px; }
      .type-buttons button { margin: 10px 5px; padding: 10px 20px; }
      .type-buttons button.active { background: #007bff; color: white; }
      select, textarea { width: 100%; margin: 10px 0; padding: 10px; }
      .generate-btn { padding: 15px 30px; background: #28a745; color: white; border: none; cursor: pointer; }
      .generate-btn:disabled { background: #ccc; }
    </style>
  </head>
  <body>
    <div class="voice-selector">
      <h2>Voice Synthesizer</h2>

      <!-- Type Selector -->
      <div class="type-buttons">
        <button id="classic-btn" class="active" onclick="selectType('classic')">Classic Voices</button>
        <button id="random-btn" onclick="selectType('random')">Random Voice</button>
      </div>

      <!-- Classic Selector -->
      <div id="classic-selector">
        <label>Classic Voice:</label>
        <select id="classic-voice">
          <option value="1">Voice 1</option>
          <option value="2">Voice 2</option>
          <option value="3">Voice 3</option>
          <option value="4">Voice 4</option>
        </select>
      </div>

      <!-- Random Selector -->
      <div id="random-selector" style="display: none;">
        <label>Gender:</label>
        <select id="random-gender">
          <option value="male">Male Voice</option>
          <option value="female">Female Voice</option>
        </select>
      </div>

      <!-- Text Input -->
      <textarea id="text-input" placeholder="Enter text to synthesize..." rows="4"></textarea>

      <!-- Emotion Selector -->
      <select id="emotion-select">
        <option value="neutral">Neutral</option>
        <option value="joy">Joy</option>
        <option value="anger">Anger</option>
        <option value="sadness">Sadness</option>
        <option value="fear">Fear</option>
      </select>

      <!-- Generate Button -->
      <button class="generate-btn" onclick="generateSpeech()">Generate Speech</button>
      <div id="status" style="margin-top: 10px;"></div>
    </div>

    <script>
      let currentType = 'classic';

      function selectType(type) {
        currentType = type;

        // Update button styles
        document.getElementById('classic-btn').classList.toggle('active', type === 'classic');
        document.getElementById('random-btn').classList.toggle('active', type === 'random');

        // Show/hide selectors
        document.getElementById('classic-selector').style.display = type === 'classic' ? 'block' : 'none';
        document.getElementById('random-selector').style.display = type === 'random' ? 'block' : 'none';
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

          if (currentType === 'classic') {
            const voiceNum = parseInt(document.getElementById('classic-voice').value);
            audioBlob = await synthesizeClassic(voiceNum, text, emotion);
          } else {
            const gender = document.getElementById('random-gender').value;
            audioBlob = await synthesizeRandom(gender, text, emotion);
          }

          playAudio(audioBlob);
          status.textContent = 'Audio generated successfully!';
        } catch (error) {
          status.textContent = 'Error: ' + error.message;
          console.error(error);
        }
      }

      // Include the synthesizeClassic, synthesizeRandom, and playAudio functions here
    </script>
  </body>
  </html>
  */
}

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    synthesizeClassic,
    synthesizeRandom,
    playAudio,
    downloadAudio,
    SimpleVoiceSystem
  };
}
