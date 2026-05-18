# dcw-cloud-skills

Public mirror of Claude Code skills consumed by **cloud routines** (claude.ai/code scheduled tasks).

Cloud routines can't read local `~/.claude/skills/` files, so we mirror them here and reference via raw GitHub URL in routine prompts:

```
Fetch https://raw.githubusercontent.com/DannyRusnok/dcw-cloud-skills/main/<skill-name>/SKILL.md and follow it.
```

## Source of truth

Local: `~/.claude/skills/<skill-name>/SKILL.md`

This repo is a **mirror only** — never edit files here directly. Edit the local version, then run the `sync-skill-to-hub` meta-skill to push the update.

## Constraints for skills mirrored here

- No secrets (API keys, tokens) — scanned before each sync
- No local absolute paths (`~/...`, `/Users/...`) that cloud can't resolve — prefer MCP endpoints or HTTPS URLs
- No private project names that violate IP/NDA

## Skills

- `substack-daily-pipeline/` — Daily Substack engine v2 orchestrator (5 originals + 0-N promos + 4 commentary restacks + 8 pure restacks + 4 comments + 1 self-restack)
