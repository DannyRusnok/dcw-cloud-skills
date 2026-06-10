---
name: tutorial-note-daily
description: Denní routina — 1 step-by-step tutoriálová Substack Note navíc ke 3-notes pipelinu (4. slot, publikace 16:00 CET). Téma bere z reálné nedávné práce: mem0 (learnings/discoveries z Claude sessions), DCW Context Hub (recent commits/PRs). Tutoriálové "how I did X" notes mají dle research nejvyšší konverzi na subscribery — tohle je conversion slot, ne engagement slot. Použij když Daniel řekne: "tutorial note", "naplánuj tutoriál", "tutorial slot", "udělej how-to note", nebo když to spustí cloud routine (scheduled task).
---

# Tutorial Note Daily — 4. denní slot

Naplánuje **1 step-by-step tutoriálovou Note/den** přes `substack-mcp`, odděleně od
běžného 3-notes pipelinu (8:30/13:30/19:30) i launch routiny (12:00). Publikace **16:00 CET**.

Proč: analýza 10k-subs Substacku ukázala, že step-by-step tutoriálové notes ("how I did X,
kroky 1-2-3") konvertují na subscribery výrazně líp než engagement posty. Tohle je
conversion slot — měří se subs, ne likes.

## Krok 1 — Najdi téma z reálné práce (priorita zdrojů)

1. `mem0_search` query "learning discovery how-to" (limit 10) + `mem0_search` "tutorial note topic" (dedup proti minulým runům).
2. DCW Hub `get_context` pro 2–3 aktivní projekty (article-forge, grownote, subhook) → recent commits/PRs za 7 dní.
3. Fallback: starší mem0 learnings (vyhledej podle projektů).

Vyber **JEDNO konkrétní, replikovatelné "how I did X"** s reálnými čísly a názvy nástrojů
(např. "jak jsem snížil cost reelu na $0 přes Wan 2.2 na 12GB GPU", "jak cachuju Haiku
prompty a platím 1/10"). NIKDY vágní advice ("be consistent"). NIKDY vymyšlená čísla.

## Krok 2 — Dedup

- `list_scheduled_items` → žádná druhá tutorial note na stejný den.
- `list_recent_notes` (limit 30) + mem0 záznamy `tutorial-note:` → stejné téma max 1× za 30 dní.

## Krok 3 — Draft (format gaty)

- Angličtina, first-person, jednoduchá engagement-grade EN.
- **One sentence per line** (prázdný řádek mezi větami).
- 40–100 slov. Hook = outcome statement, NE otázka ("I render AI reels for $0 on a 3-year-old GPU.").
- Tělo = 2–4 očíslované kroky, každý krok konkrétní nástroj/akce/číslo.
- Závěr = výsledek + "you can do it too" beat (bez imperativní tip-šablony).
- Žádný link v těle, žádné "check it out", žádné banned fráze.

## Krok 4 — Schedule

`schedule_note`:
- `content` = draft
- `scheduledFor` = dnes **16:00 CET** (léto CEST: `2026-MM-DDT14:00:00Z`, zima: `15:00:00Z`)
- `angle` = nejbližší label z 15 angle chips (typicky "Claude Code workflow",
  "AI tooling trade-off", "Article Forge", "Drippery", "Substack growth", "Postmortem")

Po naplánování zaloguj do mem0: `mem0_add` text `tutorial-note <YYYY-MM-DD>: <téma>`
s metadata `{"project":"content","category":"fact"}` (dedup pro budoucí runy).

## Krok 5 — Telegram notifikace

`NOTIFY_KEY` dostaneš z routine promptu — NIKDY ho nedávej do tohoto skillu.

```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H "Content-Type: application/json" \
  -d '{"title":"📚 Tutorial note — <YYYY-MM-DD>","text":"<note text>\n\n— publikace 16:00 CET · scheduled id <id> · angle <x>\nuprav/zruš v grownote /schedule do 16:00"}'
```

V interaktivním běhu (ne cron) nejdřív ukaž draft k odsouhlasení; v cron módu naplánuj
rovnou, pošli Telegram a jen reportuj (téma, zdroj tématu, text, id).
