# LiveKit Voice Agent

A real-time voice AI agent built with LiveKit, featuring custom DeepInfra TTS integration, Groq LLM, and Deepgram STT.

## Features

- Real-time voice conversation using LiveKit
- Custom DeepInfra Kokoro-82M TTS integration
- Groq LLM for natural language understanding
- Deepgram Nova-3 for speech-to-text
- Conversation memory with SQLite
- Web-based client interface
- Docker containerized deployment

## Architecture

- **voice-agent/**: Voice agent service with custom TTS
- **token/**: Token server for LiveKit authentication
- **client/**: Web-based client interface
- **livekit.yaml**: LiveKit server configuration
- **docker-compose.yml**: Multi-container orchestration

## Prerequisites

- Docker and Docker Compose
- LiveKit API keys
- Groq API key
- Deepgram API key
- DeepInfra API key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd agent
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the client:**
   Open your browser to `http://localhost:8080`

## Configuration

### Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`: LiveKit credentials
- `GROQ_API_KEY`: Groq LLM API key
- `DEEPGRAM_API_KEY`: Deepgram STT API key
- `DEEPINFRA_API_KEY`: DeepInfra TTS API key
- `AGENT_MODE`: Set to `direct` or `worker`

### Agent Modes

- **DIRECT mode**: Agent runs directly without job system (simpler setup)
- **WORKER mode**: Agent runs as a worker with job system (production)

## Development

### Voice Agent

The voice agent ([voice-agent/app.py](voice-agent/app.py)) includes:
- Custom DeepInfra TTS integration
- SQLite conversation memory
- Agent lifecycle management

### Custom TTS

The DeepInfra TTS implementation ([voice-agent/deepinfra_tts.py](voice-agent/deepinfra_tts.py)) supports:
- Non-streaming synthesis
- MP3 audio format
- ChunkedStream base class

### Client

The web client ([client/app.js](client/app.js)) provides:
- LiveKit room connection
- Microphone publishing
- Audio track subscription and playback

## Troubleshooting

### No Audio Output

If you experience no audio output:
1. Check browser console for errors
2. Verify audio tracks are subscribed
3. Check browser audio permissions
4. Verify TTS synthesis in agent logs

### Agent Not Responding

If the agent stops responding after first question:
1. Check if Python bytecode cache is causing issues
2. Verify turn detection configuration
3. Check agent logs for exceptions

### Connection Issues

If you can't connect to LiveKit:
1. Verify LiveKit server is running: `docker-compose ps`
2. Check LiveKit logs: `docker-compose logs livekit`
3. Verify API keys in `.env`

## Deployment

For production deployment:

1. **Update PUBLIC_IP** in `.env` to your server's IP
2. **Configure domain** in `Caddyfile` for HTTPS
3. **Use WORKER mode** for better reliability
4. **Set up firewall rules** for ports 7880-7882

## License

MIT

## Credits

Built with:
- [LiveKit](https://livekit.io/)
- [Groq](https://groq.com/)
- [Deepgram](https://deepgram.com/)
- [DeepInfra](https://deepinfra.com/)
