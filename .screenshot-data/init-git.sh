#!/bin/bash
# Initialize the sample data as a git repo with backdated commits
# This creates realistic stats for dashboard screenshots

set -e
cd "$(dirname "$0")/athena"

# Skip if already initialized
if [ -d ".git" ]; then
    echo "Git repo already initialized"
    exit 0
fi

git init
git config user.email "sample@example.com"
git config user.name "Sample User"
# Allow any user to access this repo (needed for Docker volume mounts)
git config core.sharedRepository world

# Base files from a month ago
GIT_AUTHOR_DATE="2025-12-23T10:00:00" GIT_COMMITTER_DATE="2025-12-23T10:00:00" \
git add AGENTS.md GARDENER.md
GIT_AUTHOR_DATE="2025-12-23T10:00:00" GIT_COMMITTER_DATE="2025-12-23T10:00:00" \
git commit -m "Initial setup"

# Project notes from 3 weeks ago
GIT_AUTHOR_DATE="2026-01-02T14:00:00" GIT_COMMITTER_DATE="2026-01-02T14:00:00" \
git add atlas/projects/
GIT_AUTHOR_DATE="2026-01-02T14:00:00" GIT_COMMITTER_DATE="2026-01-02T14:00:00" \
git commit -m "Add project notes"

# Tech and reading from 2 weeks ago
GIT_AUTHOR_DATE="2026-01-09T09:00:00" GIT_COMMITTER_DATE="2026-01-09T09:00:00" \
git add atlas/tech/ atlas/reading/
GIT_AUTHOR_DATE="2026-01-09T09:00:00" GIT_COMMITTER_DATE="2026-01-09T09:00:00" \
git commit -m "Add tech and reading notes"

# Journal and wellness from last week
GIT_AUTHOR_DATE="2026-01-16T11:00:00" GIT_COMMITTER_DATE="2026-01-16T11:00:00" \
git add atlas/journal/ atlas/wellness/
GIT_AUTHOR_DATE="2026-01-16T11:00:00" GIT_COMMITTER_DATE="2026-01-16T11:00:00" \
git commit -m "Add journal and wellness notes"

# People and home from this week
GIT_AUTHOR_DATE="2026-01-20T15:00:00" GIT_COMMITTER_DATE="2026-01-20T15:00:00" \
git add atlas/people/ atlas/home/
GIT_AUTHOR_DATE="2026-01-20T15:00:00" GIT_COMMITTER_DATE="2026-01-20T15:00:00" \
git commit -m "Add people and home notes"

# Inbox archive from today
git add inbox/
git commit -m "Archive captured thought"

# Remaining files
git add .gardener/
git commit -m "Add branding and state"

echo "Sample data git repo initialized with $(git rev-list --count HEAD) commits"
