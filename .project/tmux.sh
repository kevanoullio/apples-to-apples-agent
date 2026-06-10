#!/usr/bin/env bash

SESSION="apples"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Check if session already exists
tmux has-session -t "$SESSION" 2>/dev/null

if [ $? != 0 ]; then
    # Create first window: git
    tmux new-session -d -s "$SESSION" -n "git" -c "$PROJECT_ROOT"
    tmux send-keys -t "$SESSION:git" "lazygit" C-m

    # frontend
    tmux new-window -t "$SESSION" -n "frontend" -c "$PROJECT_ROOT"
    tmux send-keys -t "$SESSION:frontend" "pnpm dev"

    # backend
    tmux new-window -t "$SESSION" -n "backend" -c "$PROJECT_ROOT"

    # ai
    tmux new-window -t "$SESSION" -n "ai" -c "$PROJECT_ROOT"
    tmux send-keys -t "$SESSION:ai" "opencode"

    # nvim
    tmux new-window -t "$SESSION" -n "nvim" -c "$PROJECT_ROOT"
    tmux send-keys -t "$SESSION:nvim" "nvim" C-m

    # bash
    tmux new-window -t "$SESSION" -n "bash" -c "$PROJECT_ROOT"
fi

# Start on lazygit window
tmux select-window -t "$SESSION:git"

# Attach
tmux attach-session -t "$SESSION"
