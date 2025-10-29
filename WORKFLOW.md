# Development Workflow Guide

This guide explains the recommended workflow for making changes safely.

## The Two-Stage Workflow

### Stage 1: Test on Hetzner (Skip GitHub)
Test your changes on the production server first without committing to GitHub.

### Stage 2: Commit to GitHub (After Testing)
Once it works, save it to GitHub for backup and version control.

```
┌─────────────────────────────────────────────────────────┐
│                 Development Workflow                     │
└─────────────────────────────────────────────────────────┘

1. Make changes on Mac
         ↓
2. Test deploy to Hetzner (./deploy-test.sh)
         ↓
3. Test in browser / check logs
         ↓
    ┌────┴────┐
    │ Works?  │
    └────┬────┘
         │
    ┌────┴──────────────────────┐
    │ NO                         │ YES
    │ Make more changes          │ Commit to GitHub (./deploy.sh)
    │ Run ./deploy-test.sh       │         ↓
    │ again                      │    ┌────────────┐
    └────────────────────────────┘    │  GitHub    │
                                      │  (Backup)  │
                                      └────────────┘
```

## Workflow Commands

### Option A: Test First, Then Commit (Recommended)

**Use this when making risky changes or debugging:**

```bash
# 1. Make your changes
nano voice-agent/deepinfra_tts.py

# 2. Test on Hetzner (NO GitHub yet)
./deploy-test.sh

# 3. Check if it works
ssh root@37.27.247.64 "docker logs agent_voiceagent_1 -f"
# Open browser: https://szabolcslevai.com

# 4. If it DOESN'T work:
#    - Make more changes
#    - Run ./deploy-test.sh again
#    - Repeat until it works

# 5. If it WORKS:
#    Now save to GitHub
./deploy.sh "Fix audio playback issue"
```

### Option B: Direct to GitHub (When Confident)

**Use this for simple changes you're confident about:**

```bash
# Make your changes
nano README.md

# Deploy directly (commits AND uploads to Hetzner)
./deploy.sh "Update documentation"
```

## Detailed Command Reference

### Test Deploy (No GitHub)

```bash
./deploy-test.sh
```

**What it does:**
- ✅ Uploads changed files to Hetzner using rsync
- ✅ Rebuilds Docker containers
- ✅ Restarts services
- ❌ Does NOT commit to git
- ❌ Does NOT push to GitHub

**When to use:**
- Testing new features
- Debugging issues
- Making experimental changes
- Not sure if code will work

**Pros:**
- Fast iteration (no git commits)
- Keep GitHub clean (no "testing" commits)
- Easy to try multiple versions

**Cons:**
- Changes not backed up to GitHub
- If server crashes, changes are lost

### Full Deploy (With GitHub)

```bash
./deploy.sh "your commit message"
```

**What it does:**
- ✅ Commits changes locally
- ✅ Pushes to GitHub
- ✅ Pulls on Hetzner from GitHub
- ✅ Restarts services

**When to use:**
- Changes are tested and working
- Ready to save permanently
- Want version control backup

## Real-World Examples

### Example 1: Debugging Audio Issue

```bash
# Try fix #1
nano voice-agent/deepinfra_tts.py
./deploy-test.sh
# Check logs... doesn't work

# Try fix #2
nano voice-agent/deepinfra_tts.py
./deploy-test.sh
# Check logs... doesn't work

# Try fix #3
nano voice-agent/deepinfra_tts.py
./deploy-test.sh
# Check logs... IT WORKS!

# Now save to GitHub
./deploy.sh "Fix audio playback by changing MP3 encoding"
```

**Result:** GitHub only gets ONE clean commit with the working fix, not 3 broken attempts.

### Example 2: Update Documentation

```bash
# Simple change, confident it works
nano README.md

# Deploy directly
./deploy.sh "Update setup instructions"
```

**Result:** Fast and simple, goes straight to GitHub.

### Example 3: Add New Feature

```bash
# Add feature locally
nano voice-agent/app.py

# Test first
./deploy-test.sh
# Test in browser... works!

# Add more improvements
nano voice-agent/app.py
./deploy-test.sh
# Test again... even better!

# Save final version to GitHub
./deploy.sh "Add conversation history feature"
```

**Result:** Multiple test iterations, one clean commit.

## Syncing .env File

The `.env` file is NOT synced by either script (security). Update manually when needed:

```bash
# Edit locally
nano .env

# Upload to server
scp .env root@37.27.247.64:/opt/agent/.env

# Restart to apply
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart"
```

## Checking Sync Status

### View what's different locally vs GitHub

```bash
git status          # See modified files
git diff            # See actual changes
git log --oneline   # See recent commits
```

### View what's on Hetzner vs GitHub

```bash
ssh root@37.27.247.64 "cd /opt/agent && git status"
ssh root@37.27.247.64 "cd /opt/agent && git log --oneline -5"
```

### If Hetzner is out of sync with GitHub

```bash
# Pull latest from GitHub
ssh root@37.27.247.64 "cd /opt/agent && git pull origin main"

# Or force reset to match GitHub exactly
ssh root@37.27.247.64 "cd /opt/agent && git fetch origin && git reset --hard origin/main"
```

## Common Scenarios

### "I made changes on Hetzner directly by SSH"

```bash
# On Hetzner, copy changes to local file, then:
ssh root@37.27.247.64 "cat /opt/agent/voice-agent/app.py" > voice-agent/app.py

# Now deploy properly
./deploy.sh "Apply changes from server testing"
```

**Better:** Don't edit on server. Use `./deploy-test.sh` instead.

### "I want to undo my local changes"

```bash
# Discard all local changes
git reset --hard HEAD

# Discard specific file
git checkout -- voice-agent/app.py
```

### "I want to test old version"

```bash
# Save current changes first
git stash

# Go back to previous commit
git log --oneline    # Find commit hash
git checkout abc123  # Use the hash

# Test it
./deploy-test.sh

# Return to latest
git checkout main
git stash pop        # Restore your changes
```

## Best Practices

1. **Use `./deploy-test.sh` for debugging**
   - Iterate quickly without cluttering git history
   - Only commit when it works

2. **Use `./deploy.sh` for final working code**
   - Clean commit messages
   - GitHub is your backup

3. **Never edit directly on Hetzner**
   - Always edit on Mac
   - Use scripts to deploy

4. **Test after every deploy**
   - Check browser functionality
   - Monitor logs for errors

5. **Commit messages should be descriptive**
   - Bad: "fix stuff"
   - Good: "Fix audio playback by correcting MP3 MIME type"

## Monitoring & Troubleshooting

```bash
# Watch logs in real-time
ssh root@37.27.247.64 "docker logs agent_voiceagent_1 -f"

# Check service status
ssh root@37.27.247.64 "cd /opt/agent && docker-compose ps"

# Restart if needed
ssh root@37.27.247.64 "cd /opt/agent && docker-compose restart voiceagent"

# Full rebuild
ssh root@37.27.247.64 "cd /opt/agent && docker-compose down && docker-compose up -d --build"
```

## Quick Reference

| Task | Command |
|------|---------|
| Test changes on Hetzner | `./deploy-test.sh` |
| Deploy to GitHub + Hetzner | `./deploy.sh "message"` |
| Watch logs | `ssh root@37.27.247.64 "docker logs agent_voiceagent_1 -f"` |
| Sync .env | `scp .env root@37.27.247.64:/opt/agent/.env` |
| Check status | `git status` |
| View changes | `git diff` |
| Undo local changes | `git checkout -- filename` |

## Summary

**Development workflow:**
1. Edit on Mac
2. Test with `./deploy-test.sh`
3. Iterate until it works
4. Commit with `./deploy.sh "message"`

**This keeps:**
- GitHub clean (only working code)
- Fast iteration (no git overhead while testing)
- Safe backups (working code saved)
