# Contributing to LiveKit Voice Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to:
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/livekit-voice-agent.git
   cd livekit-voice-agent
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/livekit-voice-agent.git
   ```

## Development Setup

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to `.env`:**
   - LiveKit API key and secret
   - Groq API key
   - Deepgram API key
   - DeepInfra API key

3. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f voiceagent
   ```

## Making Changes

### Before You Start

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Keep your branch up to date:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Types of Changes

- **Features**: New functionality or enhancements
- **Bugfixes**: Fixes for existing issues
- **Documentation**: Improvements to README, comments, or guides
- **Refactoring**: Code improvements without changing functionality
- **Tests**: Adding or improving tests

## Submitting Changes

### Pull Request Process

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

2. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template
   - Submit the PR

### Pull Request Guidelines

- Use a clear, descriptive title
- Reference any related issues (e.g., "Fixes #123")
- Describe what changes you made and why
- Include screenshots for UI changes
- Update documentation if needed
- Ensure all tests pass

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

Example:
```python
async def synthesize_speech(text: str, voice: str = "af_heart") -> bytes:
    """
    Synthesize speech from text using DeepInfra TTS.

    Args:
        text: The text to convert to speech
        voice: The voice ID to use

    Returns:
        Audio data as bytes
    """
    # Implementation
```

### JavaScript

- Use ES6+ features
- Use camelCase for variables and functions
- Add JSDoc comments for functions
- Handle errors appropriately
- Use async/await for asynchronous code

Example:
```javascript
/**
 * Connect to LiveKit room
 * @param {string} url - LiveKit server URL
 * @param {string} token - Authentication token
 * @returns {Promise<Room>} Connected room instance
 */
async function connectToRoom(url, token) {
    // Implementation
}
```

### Docker

- Keep Dockerfiles minimal
- Use multi-stage builds when possible
- Pin version numbers
- Clean up in the same layer

## Testing

### Manual Testing

1. **Test voice agent:**
   ```bash
   docker-compose up -d
   # Open browser to http://localhost:8080
   # Test voice interaction
   ```

2. **Check logs for errors:**
   ```bash
   docker-compose logs -f voiceagent
   ```

3. **Test different scenarios:**
   - First question response
   - Multiple questions in sequence
   - Connection recovery
   - Audio playback

### Automated Testing

Currently, the project focuses on manual testing. Contributions to add automated tests are welcome!

## Project Structure

```
.
├── voice-agent/          # Voice agent service
│   ├── app.py           # Main agent application
│   ├── deepinfra_tts.py # Custom TTS implementation
│   └── memory_sql.py    # Conversation memory
├── token/               # Token server
│   └── app.py          # Token generation service
├── client/             # Web client
│   ├── index.html      # Client UI
│   ├── app.js          # Client logic
│   └── style.css       # Client styles
├── docker-compose.yml  # Container orchestration
└── livekit.yaml       # LiveKit configuration
```

## Common Tasks

### Adding a New Feature

1. Identify where the feature belongs (agent/client/token)
2. Update relevant files
3. Test thoroughly
4. Update documentation
5. Submit PR

### Fixing a Bug

1. Reproduce the bug
2. Identify the root cause
3. Create a fix
4. Test the fix
5. Submit PR with issue reference

### Updating Dependencies

1. Update version in `requirements.txt` or `package.json`
2. Test thoroughly
3. Update documentation if needed
4. Submit PR

## Getting Help

- Check existing issues and discussions
- Read the documentation
- Ask questions in issues (label them as "question")
- Be specific about your problem

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to LiveKit Voice Agent!
