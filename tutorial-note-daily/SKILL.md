---
name: tutorial-note-daily
description: Denní routina — 1 obecná "AI for normals" tutoriálová Substack Note navíc ke 3-notes pipelinu (4. slot, publikace 16:00 CET). Téma bere z reálné nedávné práce (mem0 learnings, DCW Context Hub commits/PRs), ale ABSTRAHUJE ho na obecný princip pro běžného AI uživatele — žádný kód, žádné názvy nástrojů z infry. Tyhle praktické "jak používat AI" notes konvertují na subscribery líp než engagement posty — tohle je conversion slot, ne engagement slot. Použij když Daniel řekne: "tutorial note", "naplánuj tutoriál", "tutorial slot", "udělej how-to note", nebo když to spustí cloud routine (scheduled task).
---

# Tutorial Note Daily — 4. denní slot

Naplánuje **1 obecnou "AI for normals" tutoriálovou Note/den** přes `substack-mcp`, odděleně od
běžného 3-notes pipelinu (8:30/13:30/19:30) i launch routiny (12:00). Publikace **16:00 CET**.

Proč: dřív skill generoval tech deep-dive ("jak cachuju Haiku prompty na 12GB GPU") —
Danielovi followers (writers/creators, ne devs) tomu nerozumí a nic jim to neřekne.
Nově: zdroj zůstává Danielova reálná práce (mem0), ale každý learning se **přeloží na obecný
princip použitelný pro kohokoli, kdo používá AI** — bez kódu, bez tech žargonu. Cíl: subs, ne likes.

## Krok 1 — Najdi RAW learning z reálné práce (priorita zdrojů)

1. `mem0_search` query "learning discovery how-to" (limit 10) + `mem0_search` "tutorial note topic" (dedup proti minulým runům).
2. DCW Hub `get_context` pro 2–3 aktivní projekty (article-forge, grownote, subhook) → recent commits/PRs za 7 dní.
3. Hub Notion proxy `search_notion` (session recaps, research reporty, playbooky).
4. Fallback: starší mem0 learnings (vyhledej podle projektů).

Vyber **JEDEN konkrétní learning / discovery / trade-off** z reálné práce. V téhle fázi je
ještě tech-specific (názvy nástrojů, čísla) — to je OK, abstrakce přijde v Kroku 1.5.

## Krok 1.5 — Abstrahuj na obecný princip (AI for normals)

Z raw learningu vydestiluj: **"co se z toho může naučit někdo, kdo nekóduje a jen používá AI?"**

- Zahoď názvy nástrojů z infry (Haiku, Wan, ComfyUI, mem0, queue, GPU, R2…), čísla z infry, kód.
- Nech jádro principu = obecné chování při práci s AI, které platí pro běžného člověka.
- Doplň **lidský, relatable příklad** (psaní mailu, plánování, učení, organizace), ne dev příklad.

Příklady transformace:
- raw: *"cachuju Haiku prompty, platím 1/10"* → princip: *"Když AI dáváš pořád to samé zadání, napiš kontext jednou a měň jen detail — ušetříš čas i peníze."*
- raw: *"video render jedu přes queue ať neblokuje"* → princip: *"Nech AI dělat dlouhé úkoly na pozadí, nečekej u obrazovky."*
- raw: *"Haiku ztrácel nit na multi-step bězích, přepnul jsem na Sonnet"* → princip: *"Na složitější vícekrokové úkoly nasaď silnější model — levnější model se na dlouhé trati ztratí."*

Pokud z learningu NEJDE udělat obecný princip bez tech žargonu (je čistě infra), zahoď ho a
vezmi další kandidát z Kroku 1. NIKDY vágní advice ("be consistent"). NIKDY vymyšlená čísla.

## Krok 2 — Dedup

- `list_scheduled_items` → žádná druhá tutorial note na stejný den.
- `list_recent_notes` (limit 30) + mem0 záznamy `tutorial-note:` → stejné téma max 1× za 30 dní.

## Krok 3 — Draft (format gaty)

- Angličtina, first-person, jednoduchá engagement-grade EN. **Žádný kód, žádný tech žargon.**
- **One sentence per line** (prázdný řádek mezi větami).
- 40–100 slov. Hook = konkrétní outcome/princip, NE otázka ("Most people use AI like a search box. Here's the shift that doubled what I get out of it.").
- Tělo = 2–4 kroky, každý krok obecná akce + relatable (ne-dev) příklad. **BEZ pořadových čísel a BEZ odrážek** — každý krok jako samostatná věta na vlastním řádku (prázdný řádek mezi kroky). Pořadové číslo na začátku řádku Substack renderuje jako ordered-list a odsadí text — proto ne.
- Závěr = "tohle zvládneš taky" beat (bez imperativní tip-šablony).
- Mám-li chuť napsat název nástroje z infry nebo číslo z GPU/queue/modelu → STOP, to je signál že abstrakce z Kroku 1.5 selhala.
- Žádný link v těle, žádné "check it out", žádné banned fráze.

## Krok 3.5 — Branded step-card image (POVINNÁ příloha)

Tutorial note se VŽDY publikuje s brandovaným step-card obrázkem (1080×1080, DCW
styl) — renderuje ho substack-mcp server-side z `imageSpec`, žádný Codex/R2/upload.
Postav `imageSpec` z draftu:

```json
{
  "template": "steps_card",
  "headline": "<3–7 slov, jádro principu; NE celý hook>",
  "accentWord": "<1–2 slova z headline k obarvení oranžově, volitelné>",
  "steps": ["<krok 1, ≤12 slov>", "<krok 2>", "<krok 3>", "<krok 4 volitelně>"]
}
```

Pravidla: `steps` = 2–4 položky (víc se ořízne), každý krok krátká obecná akce (bez
čísla na začátku — číslo dokresluje badge). `headline` ≠ první věta těla, ať se
obrázek a text neopakují 1:1. Text v `steps` může být stručnější přeformulování
kroků z těla note (obrázek = vizuální shrnutí, ne doslovná kopie). `imageSpec`
předej do `schedule_note` (param `imageSpec`) ve fázi APPROVE.

## Krok 4 — HARD APPROVAL (dvoufázový flow, nic se nepublikuje bez Danielova OK)

**Fáze DRAFT (ranní run):** note NEplánuj. Ulož pending draft do souboru
(`ops/tutorial-note-pending.json` v dcw-context-hub: `{date, content, angle, topic_source, imageSpec}`
— `imageSpec` z Kroku 3.5) a pošli Telegram preview s textem note + instrukcí:
*"Odpověz 'ok' pro publikaci dnes 16:00 CET, 'ne' pro zahození."* Angle = nejbližší label z 15 angle chips
(typicky "Claude Code workflow", "AI tooling trade-off", "Article Forge",
"Drippery", "Substack growth", "Postmortem").

**Fáze APPROVE (odpolední run, ~15:00):** načti pending JSON (když není, skonči).
Přes substack-mcp `get_recent_replies` (automation bot, webhook-persisted — NE
`getUpdates`, ten 409) najdi Danielovu odpověď novější než draft: obsahuje-li "ok"/"ano"/"yes" → `schedule_note` (`content`, `scheduledFor` =
dnes 16:00 CET; léto CEST `T14:00:00Z`, zima `T15:00:00Z`, `angle`, `imageSpec` z pending JSON) a zaloguj do
mem0 `tutorial-note <YYYY-MM-DD>: <téma>` s metadata
`{"project":"content","category":"fact"}`. Obsahuje-li "ne"/"skip" nebo žádná
odpověď není → NIC neplánuj a pošli Telegram "tutorial note dnes přeskočena (bez
schválení)". Pending soubor po zpracování smaž. Danielova úprava textu v odpovědi
("ok, ale změň X") → aplikuj úpravu a pak naplánuj.

## Krok 5 — Telegram (VŽDY automation bot, NIKDY Gaia)

Approve notifikace (draft preview i approve potvrzení) jdou **VŽDY na automation
bota** — `TELEGRAM_BOT_API` + `TELEGRAM_CHAT_ID` z `dcw-context-hub/.env.local`
(stejný bot, který používají ostatní scheduled workeři: CEO report, attribution,
collab-scout…). Tohle je záměrně NE interaktivní Gaia bot (`channels/telegram`),
ať approve pingy nezaplevelují hlavní Gaia konverzaci.

- **Posílání** přes substack-mcp `send_telegram_message` (čte token z env sám) —
  NEBO raw `https://api.telegram.org/bot<TELEGRAM_BOT_API>/sendMessage`. NIKDY
  nevypisuj token do outputu.
- **Čtení odpovědi** přes substack-mcp `get_recent_replies` (webhook-persisted).
  NEPOUŽÍVEJ `getUpdates` — automation bot má aktivní webhook → 409.
- **Interaktivní běh (Gaia):** approve preview přesto pošli na automation bota
  (8863), NE do téhle konverzace přes reply tool. Dvoufázový flow zůstává jen pro
  cron; v interaktivu můžeš po Danielově OK naplánovat rovnou.
