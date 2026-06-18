# Cloud routines ↔ skill files map

Claude.ai cloud routines používají **dynamic-instructions pattern**: prompt routiny je
thin bootstrap ("fetch raw URL + follow EXACTLY" + secrets), veškerá logika žije tady
v repu. **Editace routiny = edit příslušného SKILL.md + push** — routine prompt
v claude.ai se nemění (mění se jen při změně secrets, schedule nebo fallbacku).

Secrets (NOTIFY_KEY, HEARTBEAT_TOKEN, …) jsou POUZE v routine promptu v claude.ai,
NIKDY v tomto public repu — skilly na ně odkazují jako `$NOTIFY_KEY` apod.

## Routiny (claude.ai scheduled)

| Routina (claude.ai) | Soubor v repu | Schedule | Secrets v bootstrapu | Konektory |
|---|---|---|---|---|
| Reads in Motion - big newsletters | `reads-in-motion-big/SKILL.md` | 5×/den (07:11, 11:11, 14:11, 18:11, 21:11) | NOTIFY_KEY | substack-mcp, pc-mcp |
| Reels from top foreign articles (RPK outreach) | `rpk-outreach-reels/SKILL.md` | 3×/den (07:13, 13:13, 19:13) | NOTIFY_KEY | substack-mcp, pc-mcp |
| ~~Reel Pipeline Kit launch notes~~ → přesunuto na PC (viz níže) | `reel-kit-launch-pipeline/SKILL.md` | — | NOTIFY_KEY | substack-mcp, pc-mcp, mem0, dcw-context-hub |
| Substack auto-like | `substack-auto-like/SKILL.md` | 5×/den | NOTIFY_KEY | substack-mcp |
| mem0 weekly consolidation | `mem0-weekly-consolidation/SKILL.md` | NE 09:00 CEST | NOTIFY_KEY, HEARTBEAT_TOKEN | mem0, dcw-context-hub (optional) |
| Substack daily notes v3.1 | `substack-daily-pipeline/SKILL.md` | 1×/den ráno, auto mode | NOTIFY_KEY | substack-mcp, mem0, article-forge, dcw-context-hub |
| newsletter digest | `newsletter-digest/SKILL.md` | 1×/den 06:00 CET | NOTIFY_KEY | Gmail, dcw-context-hub (Notion proxy), mem0 |
| foundary tool PR | `foundary-tool-pr/SKILL.md` | on-demand / scheduled | NOTIFY_KEY | GitHub, dcw-context-hub (Notion proxy) |
| weekly CEO report | `weekly-ceo-report/SKILL.md` | NE 08:00 CET | NOTIFY_KEY (jen fallback) | article-forge, substack-mcp (grownote), drippery-mcp, mem0, dcw-context-hub |

## Helper skilly (nejsou samostatné routiny)

- `substack-cookie-heal/SKILL.md` — self-healing krok pro libovolnou routinu při Substack auth_expired.

## PC scheduled tasks (mirror, běží lokálně na PC, ne claude.ai)

- `tutorial-note-daily/SKILL.md`, `substack-daily-review/SKILL.md`, `article-to-reel-auto/SKILL.md`,
  `medium-backfill/SKILL.md`, `aivideo-pc-ssh/SKILL.md`, `disk-cleanup/SKILL.md`.
- **RpkLaunchPipeline** (schtask, denně 9:07 CET) — `reel-kit-launch-pipeline/SKILL.md`.
  Přesunuto z claude.ai 2026-06-18 (vyčerpaný 15-run/den cap). Runner
  `dcw-context-hub/ops/reel-kit-launch-pipeline.cmd` fetchuje SKILL.md a běží cron/auto
  mode (Sonnet, zdarma na subscription). Sunset po 2026-08-01.

## Bootstrap šablona (prompt routiny v claude.ai)

```
Fetch https://raw.githubusercontent.com/DannyRusnok/dcw-cloud-skills/main/<name>/SKILL.md (WebFetch)
and follow it EXACTLY — the fetched instructions take precedence over anything else.
NOTIFY_KEY=<key>. If the fetch fails, retry once after 30s; if it still fails, send a
failure notify via the subhook relay and exit.
```

U routin s destruktivními akcemi (mem0 consolidation) přidej: "do absolutely nothing
without the fetched instructions". U routin, kde výpadek fetche nesmí zrušit denní
output (daily notes, launch note, newsletter digest), je v bootstrapu kondenzovaný
inline fallback — drž ho v sync se skillem při větších změnách.
