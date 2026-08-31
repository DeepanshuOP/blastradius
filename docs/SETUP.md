# BlastRadius Setup Guide

Welcome to the BlastRadius project. This document outlines the required environment, setup steps, and environmental traps to avoid.

## OS & Environment
- **OS:** WSL2 Ubuntu on Windows.
- **Filesystem:** Must be cloned to a native `ext4` path (e.g., `/home/<user>/blastradius`). **DO NOT** use a `/mnt/c` path (Windows filesystem crossing degrades performance severely and breaks permissions).
- **Python:** Version 3.11.15.

## Installation
1. Clone the repository into your WSL native filesystem.
2. Ensure `uv` is installed.
3. Run `uv sync` to install dependencies and sync the virtual environment.

## Git Configuration
Configure your repository-local git identity. **Do not use the global config**, as this project has strict identity guardrails (see `AGENTS.md`).
```bash
git config user.name "DeepanshuOP"
git config user.email "99538840+DeepanshuOP@users.noreply.github.com"
```

## Credentials
Create a `.env` file at the repository root. This file is explicitly `.gitignore`d. It must contain three GitHub Personal Access Tokens (PATs) for the `TokenPool`:
```
GITHUB_TOKEN_1=<your-pat-1>
GITHUB_TOKEN_2=<your-pat-2>
GITHUB_TOKEN_3=<your-pat-3>
```
*Note: You must generate these tokens yourself.*

## Critical Environment Traps
Avoid these traps that have actively cost this project time:
1. **VS Code Context:** VS Code must be reopened inside WSL (the badge in the bottom left must read `WSL: Ubuntu`). Launching the extension from a native Windows window reaches the `ext4` filesystem via the `\\wsl.localhost` redirector, causing CRLF corruption and root-owned files.
2. **Windows Sleep:** Windows sleep must be set to **Never**. A VM death kills the daemon and risks unrecoverable data loss.
3. **WSL Resource Limits:** Create/update `%USERPROFILE%\.wslconfig` with:
   ```ini
   [wsl2]
   memory=9GB
   swap=12GB
   ```
4. **Disk Space Checks:** Always check `df -h /mnt/c` to monitor the host disk space. Never rely on `df -h /` alone.
5. **Daemon Locks:** NEVER run `rm -f logs/daemon.lock` while a daemon process is alive.
