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

## Krok 4 — HARD APPROVAL (dvoufázový flow, nic se nepublikuje bez Danielova OK)

**Fáze DRAFT (ranní run):** note NEplánuj. Ulož pending draft do souboru
(`ops/tutorial-note-pending.json` v dcw-context-hub: `{date, content, angle, topic_source}`)
a pošli Telegram preview s textem note + instrukcí: *"Odpověz 'ok' pro publikaci
dnes 16:00 CET, 'ne' pro zahození."* Angle = nejbližší label z 15 angle chips
(typicky "Claude Code workflow", "AI tooling trade-off", "Article Forge",
"Drippery", "Substack growth", "Postmortem").

**Fáze APPROVE (odpolední run, ~15:00):** načti pending JSON (když není, skonči).
Přes Telegram `getUpdates` najdi Danielovu odpověď z daného chatu novější než
draft: obsahuje-li "ok"/"ano"/"yes" → `schedule_note` (`content`, `scheduledFor` =
dnes 16:00 CET; léto CEST `T14:00:00Z`, zima `T15:00:00Z`, `angle`) a zaloguj do
mem0 `tutorial-note <YYYY-MM-DD>: <téma>` s metadata
`{"project":"content","category":"fact"}`. Obsahuje-li "ne"/"skip" nebo žádná
odpověď není → NIC neplánuj a pošli Telegram "tutorial note dnes přeskočena (bez
schválení)". Pending soubor po zpracování smaž. Danielova úprava textu v odpovědi
("ok, ale změň X") → aplikuj úpravu a pak naplánuj.

## Krok 5 — Telegram

Credentials (bot token + chat id) dostaneš z routine promptu / lokálního env —
NIKDY je nedávej do tohoto skillu ani je nevypisuj do outputu. Posílej přímo přes
`https://api.telegram.org/bot<TOKEN>/sendMessage` a čti přes `/getUpdates`.

V interaktivním běhu (ne cron) ukaž draft k odsouhlasení v konverzaci a po OK
naplánuj rovnou — dvoufázový Telegram flow je jen pro cron.
