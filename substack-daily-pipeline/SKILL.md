---
name: substack-daily-pipeline
description: |
  Single-pass plánovač Danielova denního Substacku — engine v3 (2026-06-02), conversion-driven. Plánuje POUZE 3 originální Notes/den (žádné restacky, komentáře ani self-restacky — ty Daniel dělá ručně). Tři notes = tři archetypy, které jako jediné historicky reálně konvertovaly subscribery (analýza 401 notes přes /api/v1/note_stats: 0.13% conv, jen 7 notes vůbec získalo suba): (1) milestone/journey, (2) value + "you can do it too", (3) contrarian POV. Aplikuje conversion-format gaty (17–58 slov, first-person, žádná otázka-jako-hook, žádný "check it out"/link v těle, žádná imperativní tip šablona) + memory feedback + fact-check. Použij kdykoli Daniel řekne: "naplánuj zítřek", "daily pipeline", "naplánuj čtvrtek/pátek/sobotu/neděli/pondělí/úterý/středu", "spusť denní plán Substack", "připrav substack na zítra", "plán na zítra", "naplánuj 3 notes", "do daily plan". Default časy: 8:30 / 13:30 / 19:30 CET.
---

# substack-daily-pipeline (v3 — conversion-driven, notes-only)

**Co se změnilo proti v2:** zahozeny restacky / komentáře / self-restack / feed_pool / promo-batch (Daniel dělá engagement ručně — automatizace nekonvertovala). Zůstávají **3 originální Notes/den**, cílené na formáty, které jako jediné reálně přiváděly subscribery.

## Proč zrovna tyto 3 archetypy (data, ne dojem)

Analýza **všech 401 notes (27.3.–2.6.2026)** přes `https://substack.com/api/v1/note_stats/{c-id}` (card `new_subscribers`): **5956 impressions → 8 free subs (0 paid) = 0.13 %**, jen **7 notes** vůbec konvertovalo. **Reach ≠ konverze** — note s 400 impressions (restack-reakce "…Sharing.") = 0 subs. Konvertovaly výhradně osobní/value/POV notes, i při 12–33 impressions. Restacky, gratitude a one-linery farmí lajky, ne suby → proto vypadly z pipeline.

## Inputs

- **Target date** (default: zítra). "zítřek" / "čtvrtek" / "2026-06-05".
- **Time override** (volitelně): "notes 9/14/20".

## Mandatory memory checks (read at start, apply silently)

- `feedback_publishing_language_english.md` → vše EN
- `feedback_notes_sentence_per_line.md` → prázdný řádek mezi každou větou
- `feedback_no_series_prefix_in_titles.md` → žádný `[From the Workshop]` apod.
- `feedback_notes_angle_required.md` → každá note má angle z `grownote/lib/angles.ts` (ulož do výstupu)
- Conversion learning (mem0, project=grownote): reach ≠ konverze; piš osobní POV / milestone / value-s-pozvánkou

## Tři archetypy (1× každý, povinně různé angles)

### A1 — Milestone / journey  (`format: "milestone"`)
First-person pokrok nebo posun identity, ideálně s číslem. Upřímné, klidně sebeironické.
Konvertovaly: *"In a month, I transformed from 'AI Solo Founder' to 'Digital Craft Workshop'."* · *"I doubled count of my subscribers today. From 1 to 2 🤪"* · *"17 views of last post and 17 subs already."*
Zdroj: `get_aggregates` (sub count + 7d/30d delta), git milestones, shipnuté featury, dcw-context-hub state.

### A2 — Value + "you can do it too"  (`format: "value_invite"`)
Jedna konkrétní užitečná věc, kterou jsi udělal/zjistil, podaná jako sdílený insight s pozvánkou ji zopakovat. **Ne imperativ** ("Set X", "Wire Y" = mrtvý formát, 0 konverzí).
Konvertovaly: *"I improved visualization of my Drippery series and you can do it too. It is completely customizable."* · *"Prompt caching can cut Claude API costs by up to 90% on multi-turn agents. The rule is simple."*
Zdroj: mem0 last 7d (decision/discovery/learning), git commits 7d, nejnovější článek.
**Promo varianta:** pokud v posledních ~3 dnech vyšel článek → tento slot může být osobně-rámcované promo (`articleId` set, `ctaType: "promo"`). Pořád se počítá jako 1 ze 3 (žádné extra promo notes).

### A3 — Contrarian POV / filozofie  (`format: "pov"`)
First-person přesvědčení / pohled na AI / building / craft, který zve čtenáře do tvého světa.
Konvertovala: *"Most people use AI as a faster Google. That's fine. But it's not why I use it. I use it as the…"*
Zdroj: `me.md` principy, opakující se témata, mem0 preferences/learnings.

## Conversion-format gaty (hard, z dat)

1. **17–58 slov.** Reject <17 (one-linery = lajky, ne suby) i >70.
2. **First-person povinně** (I / my / we).
3. **Žádná otázka jako hook ani jako jediné CTA.** (Měkká otázka uvnitř těla OK, default žádná.)
4. **Žádný "check it out" / holý link v těle.** Výjimka: A2 promo varianta, kde link renderuje platforma přes `articleId` (ne nalepený "check it out").
5. **Žádná imperativní tip šablona** ("Set X", "Wire Y", "Use X", "Leverage X" jako otevírka).
6. **Sentence-per-line** — prázdný řádek mezi každou větou.
7. **EN, žádný series prefix.**
8. Dedup proti posledním 15 originálům (`list_recent_notes`) — žádné opakování otevíracího slova ani úhlu 3× po sobě.

## Workflow

### 1. Pre-flight (silent, parallel)
- `mcp__2bd50541…__trigger_substack_sync()` — čerstvá data
- `mcp__2bd50541…__get_aggregates()` — sub count + delta (palivo pro A1)
- `mcp__2bd50541…__list_scheduled_items({actionType:"note", status:"scheduled", fromIso:<den 00:00>, toIso:<den 23:59>})` — obsazené sloty
- `mcp__2bd50541…__list_recent_notes({limit:20})` — dedup base + cookie health (pokud volání selže na auth → **STOP**, surface: "Cookie expired — refresh v grownote /settings.")

### 2. Source material (parallel, silent)
- **mem0**: `mcp__c59fb103…__mem0_search({query:"decision OR discovery OR learning", user_id:"daniel"})` → filtr posledních 7d, category∈{decision,discovery,learning} → palivo pro A2/A3
- **git**: `git -C ~/foundary-tools/<repo> log --since=7.days --oneline` pro grownote, drippery, framelock, article-forge, archieve-concierge, subhook (skip docs/wip/merge) → milestones (A1) + value (A2)
- **articles**: `mcp__eb89b7e1…__list_articles` → nejnovější publikovaný; pokud ≤3 dny starý → promo kandidát pro A2
- **dcw-context-hub**: `get_context({project:"grownote"})` pro recent state (volitelně)

### 3. Draft 3 notes (1× A1, 1× A2, 1× A3)
Aplikuj všechny gaty (sekce výše). Každá jiný angle z `lib/angles.ts`. Žádný motivational filler ("you've got this", "unlock", "game-changer"). Žádné otevírky "This morning / Today I / Just shipped".

### 4. Fact-check gate
Každé osobní tvrzení s číslem / názvem toolu / dobou trvání → ověř paralelně proti **mem0 + dcw-context-hub** (+ Notion pokud třeba). ✅ verified / ❌ contradicts → auto-rewrite / ⚠️ unverifiable → flag, Daniel potvrdí. Hlavní riziko: A1 čísla (sub count, počty článků) — vždy proti `get_aggregates`.

### 5. Light review (internal, max 2 kola)
Round 1 = critique proti gatům. Round 2 = rewrite failing. 3. kolo → drop. Žádné 3-round ceremony.

### 6. Output (single message)
```
[TARGET DATE]   (cookie OK / ⚠️ expired)
Sub count: <N>  (+<d7> 7d / +<d30> 30d)

  08:30  A1 milestone     #<angle>   "<prvních 70 znaků…>"   [fact-check]
  13:30  A2 value-invite  #<angle>   "<prvních 70 znaků…>"   [fact-check]   (promo→"<title>" pokud aplikováno)
  19:30  A3 pov           #<angle>   "<prvních 70 znaků…>"   [fact-check]

Fact-check: ✅ N / ⚠️ N / ❌ N
```
End: **"Pošli `ok` / `drop N` / `edit N <text>` / `stop`."**

### 7. Po ack — schedule
- `ok` → pro každou notu `mcp__2bd50541…__schedule_note({content, scheduledFor:<ISO CET slot>, format:<archetyp>, articleId?, ctaType?})`. Sloty obsazené z kroku 1 → posuň na další volný (8:30→9:30, 13:30→14:30, 19:30→20:30).
- `drop N` → tu notu nescheduluj.
- `edit N <text>` → swap obsah, re-gate, pak schedule.
- `stop` → nic nescheduluj, vrať 3 drafty jako markdown.

Cron `scheduledItemsCron` v grownote (1 min) auto-publikuje v `scheduledFor`.

## Anti-patterns
- Nikdy neplánuj restacky / komentáře / self-restacky — Daniel je dělá ručně (záměr v3).
- Nikdy <3 nebo >3 notes (pokud Daniel explicitně neřekne jinak).
- Nikdy one-liner (<17 slov) jako originál — farmí lajky, ne suby.
- Nikdy imperativní tip ("Set X / Wire Y") — historicky 0 konverzí.
- Nikdy otázka jako hook.
- Nikdy "check it out" / holý link v těle (kromě A2 promo přes articleId).
- Nikdy motivational filler ani "This morning / Today I / Just shipped" otevírky.
- Nikdy neplánuj před ackem.

## Sister skills
- `substack-daily-review` — batch review naplánovaných items (stále funguje na notes).
- `substack-add-handle <handle>` — wantlist (jen pro ruční engagement discovery).
