# Git Workflows

## Feature Branch Flow
1. `git checkout -b feature/name`
2. Make commits with clear messages
3. `git push -u origin feature/name`
4. Open PR, get review
5. Squash and merge

## Useful Commands
- `git stash -u` - Stash including untracked
- `git log --oneline -10` - Quick history
- `git rebase -i HEAD~3` - Interactive rebase last 3

## Commit Message Format
```
type(scope): subject

body (optional)
```
Types: feat, fix, docs, style, refactor, test, chore
