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
| ~~Reads in Motion - big newsletters~~ RETIRED 2026-08-31 (RiM zabanován 8/2026; PC schtask smazán, smaž i cloud routinu) | `reads-in-motion-big/SKILL.md` | — | NOTIFY_KEY | substack-mcp, pc-mcp |
| ~~Reels from top foreign articles (RPK outreach)~~ RETIRED 2026-08-31 (PC schtask smazán, smaž i cloud routinu) | `rpk-outreach-reels/SKILL.md` | — | NOTIFY_KEY | substack-mcp, pc-mcp |
| ~~Reel Pipeline Kit launch notes~~ → přesunuto na PC (viz níže) | `reel-kit-launch-pipeline/SKILL.md` | — | NOTIFY_KEY | substack-mcp, pc-mcp, mem0, dcw-context-hub |
| ~~Substack auto-like~~ → přesunuto na PC (viz níže) | `substack-auto-like/SKILL.md` | — | NOTIFY_KEY | substack-mcp |
| mem0 weekly consolidation | `mem0-weekly-consolidation/SKILL.md` | NE 09:00 CEST | NOTIFY_KEY, HEARTBEAT_TOKEN | mem0, dcw-context-hub (optional) |
| ~~Substack daily notes v3.1~~ RETIRED 2026-08-31 (SubstackDailyNotes/V4 schtask smazán, smaž i cloud routinu) | `substack-daily-pipeline/SKILL.md` | — | NOTIFY_KEY | substack-mcp, mem0, article-forge, dcw-context-hub |
| newsletter digest | `newsletter-digest/SKILL.md` | 1×/den 06:00 CET | NOTIFY_KEY | Gmail, dcw-context-hub (Notion proxy), mem0 |
| foundary tool PR | `foundary-tool-pr/SKILL.md` | on-demand / scheduled | NOTIFY_KEY | GitHub, dcw-context-hub (Notion proxy) |
| ~~weekly CEO report~~ RETIRED 2026-08-31 (PC schtask smazán; smaž routinu i v claude.ai) | `weekly-ceo-report/SKILL.md` | — | NOTIFY_KEY (jen fallback) | article-forge, substack-mcp (grownote), drippery-mcp, mem0, dcw-context-hub, gumroad-mcp (revenue sekce; bez connectoru se sekce vynechá) |

## Helper skilly (nejsou samostatné routiny)

- `substack-cookie-heal/SKILL.md` — self-healing krok pro libovolnou routinu při Substack auth_expired.

## PC scheduled tasks (mirror, běží lokálně na PC, ne claude.ai)

- `tutorial-note-daily/SKILL.md`, `substack-daily-review/SKILL.md`, `article-to-reel-auto/SKILL.md`,
  `medium-backfill/SKILL.md`, `homepc-ssh/SKILL.md`, `disk-cleanup/SKILL.md`.
- **RpkLaunchPipeline** (schtask, denně 9:07 CET) — `reel-kit-launch-pipeline/SKILL.md`.
  Přesunuto z claude.ai 2026-06-18 (vyčerpaný 15-run/den cap). Runner
  `dcw-context-hub/ops/reel-kit-launch-pipeline.cmd` fetchuje SKILL.md a běží cron/auto
  mode (Sonnet, zdarma na subscription). Sunset po 2026-08-01.
- **SubstackAutoLike** (schtask, 5×/den 6:37/9:37/12:37/15:37/18:37 CET, jeden task
  `/sc daily /st 06:37 /ri 180 /du 0012:00`) — `substack-auto-like/SKILL.md`. Přesunuto
  z claude.ai 2026-06-18 (15-run/den cap). Runner `dcw-context-hub/ops/substack-auto-like.cmd`
  fetchuje SKILL.md (Sonnet, zdarma na subscription). Cloud routine vypnutá (ověřeno
  2026-07-26) — PC schtask je jediný běžící zdroj. Od 2026-07-26 mutual-recommendation-first
  s deterministickým bucketem (index % 5 === runIndex), cap 7 likes/run.
- **SubstackDailyNotes** (schtask, denně 7:15 CET) — `substack-daily-pipeline/SKILL.md` v `auto`
  mode pro target_date=TODAY. Přesunuto z claude.ai 2026-06-18 (15-run/den cap). Runner
  `dcw-context-hub/ops/substack-daily-notes.cmd` fetchuje SKILL.md + inline fallback (Sonnet,
  zdarma na subscription). Cloud routinu vypnuto 2026-06-18.
- **ReadsInMotionBig** (1 task, 5 daily triggerů 7:11/11:11/14:11/18:11/21:11 CET) —
  `reads-in-motion-big/SKILL.md`, Substack MCP + PC MCP. Přesunuto z claude.ai 2026-06-18.
  Runner `dcw-context-hub/ops/reads-in-motion-big.cmd`. Registrováno přes Register-ScheduledTask
  (multi-trigger; MSA účet → bez explicitního -Principal). Cloud po ověření vypnout.
- **RpkOutreachReels** (1 task, 3 daily triggery 7:13/13:13/19:13 CET) —
  `rpk-outreach-reels/SKILL.md`, Substack MCP + PC MCP. Přesunuto z claude.ai 2026-06-18.
  Runner `dcw-context-hub/ops/rpk-outreach-reels.cmd`. Cloud po ověření vypnout.

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

## Purge 2026-08-31

Smazáno 58 PC schtasků (103 → 44). Odstraněné rutiny: celý RiM blok (projekt zabanován
8/2026), ~31 doběhlých one-time tasků (`Golem*`, `SF*`, `*DL`, `SubsSprint*`, …),
`DcwWebSync`, sunset RPK/ReadsInMotion/CollabScout/CrmSuggest/EliUriSceneGen/WeekendBoostPwa,
**Threads** (`ThreadsDaily`, `ThreadsPublishAM/PM` — Threads opuštěny),
`HistReelRender`, `FlyCostAudit`, `SubstackDailyNotes(V4)`, `SubstackRedraftWatch`,
`TutorialNoteDaily/Approve`, `EngagementPinger`, `WeeklyCeoReport`.
Runner .cmd/.md soubory v `dcw-context-hub/ops/` zůstávají (obnovitelné).
