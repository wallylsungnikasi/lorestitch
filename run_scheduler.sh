#!/usr/bin/env bash
set -euo pipefail
set -a; [ -f "$HOME/.env" ] && . "$HOME/.env"; set +a
{
  echo "[$(date -Is)] DIAG: whoami=$(id -un) HOME=$HOME"
  echo "[$(date -Is)] DIAG: TOKEN_LEN=${#TELEGRAM_TOKEN} CHAT_ID=${TELEGRAM_CHAT_ID:-<empty>}"
} >> /root/lorestitch/cron.log
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
cd /root/lorestitch
/usr/bin/python3 -m auto_updater.scheduler >> /root/lorestitch/cron.log 2>&1
