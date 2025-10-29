# Deployment Guide

This guide explains how to keep your code synchronized between your Mac, GitHub, and Hetzner server.

## Three-Way Sync Architecture

```
┌──────────────────┐
│   MacBook Pro    │
│ (Development)    │
└────────┬─────────┘
         │
         │ git push/pull
         ↓
┌──────────────────┐
│     GitHub       │
│  (Source of      │
│     Truth)       │
└────────┬─────────┘
         │
         │ git pull
         ↓
┌──────────────────┐
│ Hetzner Server   │
│  (Production)    │
└──────────────────┘
```

## Files Overview

### Tracked by Git (synced automatically)
- All code files (`.py`, `.js`, `.yaml`, etc.)
- Configuration templates (`.env.example`)
- Docker configurations
- Documentation

### NOT Tracked by Git (manual sync required)
- `.env` - Contains your API keys (security risk if committed!)
- `__pycache__/` - Python bytecode
- `*.db` - Database files
- Docker volumes

## Quick Start: Making Changes

### Method 1: Using the Deploy Script (Recommended)

```bash
cd /Users/szabolcs.levai/Desktop/agent

# Make your changes to code files
# ... edit files ...

# Deploy everything with one command
./deploy.sh "your commit message here"
```

This script automatically:
1. ✓ Stages all changes (excluding .env)
2. ✓ Commits locally
3. ✓ Pushes to GitHub
4. ✓ Pulls on Hetzner server
5. ✓ Restarts services

### Method 2: Manual Deployment

```bash
cd /Users/szabolcs.levai/Desktop/agent

# 1. Check what changed
git status

# 2. Stage changes
git add .

# 3. Commit
git commit -m "your message"

# 4. Push to GitHub
git push

# 5. Deploy to server
ssh root@37.27.247.64 "cd /opt/agent && git pull origin main && docker-compose up -d --build"
```

## Updating .env File

Since `.env` contains secrets, it's NOT in git. Update it separately:

```bash
# Edit .env locally
nano /Users/szabolcs.levai/Desktop/agent/.env

# Copy to server
scp /Users/szabolcs.levai/Desktop/agent/.env root@37.27.247.64:/opt/agent/.env

# Restart services to apply changes
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart"
```

## Common Tasks

### View Server Logs

```bash
# Voice agent logs (real-time)
ssh root@37.27.247.64 "docker logs agent_voiceagent_1 -f"

# Last 50 lines only
ssh root@37.27.247.64 "docker logs agent_voiceagent_1 --tail 50"

# All services
ssh root@37.27.247.64 "cd /opt/agent && docker-compose logs"
```

### Restart Services

```bash
# Restart all services
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart"

# Restart only voice agent
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart voiceagent"

# Full rebuild (use after dependency changes)
ssh root@37.27.247.64 "cd /opt/agent && docker-compose up -d --build"
```

### Check Service Status

```bash
ssh root@37.27.247.64 "cd /opt/agent && docker-compose ps"
```

### Pull Latest Code on Server

```bash
ssh root@37.27.247.64 "cd /opt/agent && git pull origin main"
```

## Workflow Examples

### Example 1: Fix a bug in deepinfra_tts.py

```bash
# On your Mac
cd /Users/szabolcs.levai/Desktop/agent
nano voice-agent/deepinfra_tts.py  # Make your fix

# Deploy
./deploy.sh "Fix audio playback issue in DeepInfra TTS"

# Monitor logs
ssh root@37.27.247.64 "docker logs agent_voiceagent_1 -f"
```

### Example 2: Update environment variables

```bash
# Edit .env locally
nano .env

# Sync to server
scp .env root@37.27.247.64:/opt/agent/.env

# Restart to apply
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart voiceagent"
```

### Example 3: Update LiveKit version

```bash
# Edit docker-compose.yml
nano docker-compose.yml  # Change livekit image version

# Deploy with rebuild
./deploy.sh "Upgrade LiveKit to v1.9.3"

# Or manually:
git add docker-compose.yml
git commit -m "Upgrade LiveKit"
git push
ssh root@37.27.247.64 "cd /opt/agent && git pull && docker-compose pull && docker-compose up -d"
```

## Troubleshooting

### "Changes not showing on server"

1. Check if you pushed to GitHub:
   ```bash
   git status
   git log --oneline -5
   ```

2. Pull on server:
   ```bash
   ssh root@37.27.247.64 "cd /opt/agent && git pull origin main"
   ```

3. Rebuild containers:
   ```bash
   ssh root@37.27.247.64 "cd /opt/agent && docker-compose up -d --build"
   ```

### "Merge conflicts"

This happens if you edited files directly on the server:

```bash
# On server
ssh root@37.27.247.64
cd /opt/agent

# Discard server changes and use GitHub version
git fetch origin
git reset --hard origin/main
```

**Best practice:** Only edit on your Mac, never on the server.

### "Permission denied (publickey)"

Your SSH key needs to be added to ssh-agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

## Current Setup

**Local (Mac):**
- Path: `/Users/szabolcs.levai/Desktop/agent`
- Git remote: `git@github.com:KamkaONE/Szabi-voice-agent.git`

**GitHub:**
- Repository: https://github.com/KamkaONE/Szabi-voice-agent
- Branch: `main`

**Hetzner Server:**
- Host: `root@37.27.247.64`
- Path: `/opt/agent`
- Git remote: `https://github.com/KamkaONE/Szabi-voice-agent.git`

## Key Files

| File | Purpose | Synced via Git? |
|------|---------|-----------------|
| `.env` | API keys and secrets | ❌ No (use scp) |
| `voice-agent/app.py` | Main agent code | ✅ Yes |
| `voice-agent/deepinfra_tts.py` | Custom TTS | ✅ Yes |
| `client/app.js` | Browser client | ✅ Yes |
| `docker-compose.yml` | Service config | ✅ Yes |
| `livekit.yaml` | LiveKit config | ✅ Yes |
| `deploy.sh` | Deployment script | ✅ Yes |

## Best Practices

1. **Always edit on Mac, never on server** - Keep server as deployment target only
2. **Use descriptive commit messages** - Makes it easy to track changes
3. **Test locally first** - Use `docker-compose up` on your Mac if possible
4. **Monitor logs after deployment** - Check for errors immediately
5. **Backup .env file** - It's not in git, so back it up separately

## Need Help?

- View this guide: `cat DEPLOYMENT.md`
- Check deploy script: `cat deploy.sh`
- View git history: `git log --oneline -10`
- Check what changed: `git diff`
