# Spoke TTS - Emotional Text-to-Speech API

Spoke is an emotional Text-to-Speech (TTS) API built on top of [StyleTTS 2](https://github.com/yl4579/StyleTTS2). It provides a REST API for synthesizing speech with 21 different emotions and 107 unique speaker voices.

## Features

- **21 Emotions**: anger, sadness, joy, fear, neutral, amusement, contentment, adoration, amazement, confusion, cuteness, desire, disappointment, disgust, distress, embarrassment, ecstasy, guilt, interest, pain, pride
- **107 Speaker Voices**: Diverse voices with different ages, genders, and accents
- **Voice Marketplace**: System for managing premium voice purchases
- **REST API**: Simple HTTP endpoints for integration

## Project Structure

```
spoke/
├── server/                 # TTS Server
│   ├── server.py          # Flask API server
│   ├── inference_engine.py # TTS synthesis engine
│   ├── emotion_router.py   # Emotion to model mapping
│   ├── voice_matcher.py    # Voice matching by description
│   ├── marketplace.py      # Supabase marketplace integration
│   ├── .env               # Environment variables (Supabase credentials)
│   └── supabase_schema.sql # Database schema
│
├── scripts/               # Management scripts
│   ├── manage_server.sh   # Start/stop/restart server
│   ├── monitor.sh         # Real-time monitoring
│   ├── watchdog.sh        # Auto-restart on failure
│   └── view_logs.sh       # View server logs
│
├── docs/                  # Documentation
│   ├── API_USAGE.md       # API documentation
│   ├── MARKETPLACE_GUIDE.md # Marketplace setup
│   ├── SETUP_MARKETPLACE.md # Quick setup guide
│   └── *.js               # JavaScript integration examples
│
├── emotions/              # Emotion models (21 emotions)
│   ├── anger/
│   ├── sadness/
│   ├── joy/
│   └── ...
│
├── Configs/               # StyleTTS2 configuration
├── Modules/               # StyleTTS2 modules
├── Utils/                 # StyleTTS2 utilities
└── env/                   # Python virtual environment
```

## Quick Start

### 1. Start the Server

```bash
./scripts/manage_server.sh start
```

### 2. Start HTTPS Tunnel (for external access)

```bash
cloudflared tunnel --url http://localhost:5000
```

### 3. Test the API

```bash
# Health check
curl http://localhost:5000/ping

# Generate speech
curl -X POST http://localhost:5000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "emotion": "joy", "speaker_id": 1}' \
  --output speech.wav
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ping` | Health check |
| GET | `/health` | Server status |
| POST | `/synthesize` | Generate speech |
| POST | `/random_voice` | Get random speaker by gender |
| GET | `/marketplace/catalog` | List premium voices |
| POST | `/marketplace/purchase` | Purchase a voice |
| GET | `/voices/owned?user_id=xxx` | Get user's owned voices |
| GET | `/voices/available?user_id=xxx` | Get all available voices |

### Synthesize Speech

```javascript
const response = await fetch('https://your-server.com/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello, this is a test!',
    emotion: 'joy',      // One of 21 emotions
    speaker_id: 1,       // 1-107
    user_id: 'user_123'  // Optional: for permission check
  })
});

const audioBlob = await response.blob();
```

### Get Random Voice

```javascript
const response = await fetch('https://your-server.com/random_voice', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    gender: 'female'  // 'male' or 'female'
  })
});

const { speaker_num, profile } = await response.json();
```

## Emotions Available

| Emotion | Description |
|---------|-------------|
| neutral | Neutral tone |
| joy | Happy, joyful |
| anger | Angry |
| sadness | Sad |
| fear | Fearful |
| amusement | Amused |
| contentment | Content, satisfied |
| adoration | Loving |
| amazement | Amazed |
| confusion | Confused |
| cuteness | Cute |
| desire | Desiring |
| disappointment | Disappointed |
| disgust | Disgusted |
| distress | Distressed |
| embarrassment | Embarrassed |
| ecstasy | Ecstatic |
| guilt | Guilty |
| interest | Interested |
| pain | In pain |
| pride | Proud |

## Voice Marketplace

The marketplace system allows users to:

1. **4 Classic Voices (Free)**: Speakers 1-4 are always available
2. **Premium Voices**: Speakers 5-107 can be purchased
3. **Permission System**: API checks if user owns the requested voice

### Setup Supabase

1. Create tables using `server/supabase_schema.sql`
2. Configure `server/.env` with your Supabase credentials

See [docs/MARKETPLACE_GUIDE.md](docs/MARKETPLACE_GUIDE.md) for detailed setup.

## Server Management

```bash
# Start server
./scripts/manage_server.sh start

# Stop server
./scripts/manage_server.sh stop

# Restart server
./scripts/manage_server.sh restart

# View status
./scripts/manage_server.sh status

# View logs
./scripts/manage_server.sh logs

# Real-time monitoring
./scripts/monitor.sh

# Auto-restart watchdog
./scripts/watchdog.sh
```

## Environment Variables

Create `server/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

## Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended)
- ~50GB disk space (for emotion models)

## Installation

```bash
# Clone repository
git clone https://github.com/your-repo/spoke.git
cd spoke

# Create virtual environment
python -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"
```

## Credits

Built on top of [StyleTTS 2](https://github.com/yl4579/StyleTTS2) by Yinghao Aaron Li et al.

## License

See [LICENSE](LICENSE) for details.
