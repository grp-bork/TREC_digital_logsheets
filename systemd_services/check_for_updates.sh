#!/bin/bash
cd $REPO_PATH

# Fetch remote changes
git fetch origin

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "[Watcher] New commits found. Pulling updates..."
  git pull origin main

  echo "[Watcher] Restarting main daemon..."
  sudo systemctl restart process_new_submissions.service
else
  echo "[Watcher] No updates."
fi
