# Copilot instructions

## Commits

- Use the repository's configured identity (`git config user.name` / `user.email`). Do not override it with a bot, tool, or placeholder identity.
- Do not add `Co-authored-by:` trailers.
- Do not commit on your own initiative unless asked; leave changes in the working tree for review.

## Branches and worktrees

- Do not create branches, worktrees, or checkpoint refs unless explicitly asked.
- Clean up after yourself: no leftover `.git/worktrees`, `refs/copilot/*`, or detached worktrees pointing at old commits.

## Files

- `docs/` is user-facing documentation. Do not add review notes, meeting minutes, dispatch logs, or internal process records there.
- Do not mention unreleased projects, internal tooling, private sources, or personal context in public files.
- Text that ships with the package must read as documentation, not as a work log.
