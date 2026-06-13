---
name: substack-daily-pipeline
description: |
  Single-pass plánovač Danielova denního Substacku — engine v3 (2026-06-02), conversion-driven. Plánuje POUZE 3 originální Notes/den (žádné restacky, komentáře ani self-restacky — ty Daniel dělá ručně). Tři notes = tři archetypy, které jako jediné historicky reálně konvertovaly subscribery (analýza 401 notes přes /api/v1/note_stats: 0.13% conv, jen 7 notes vůbec získalo suba): (1) personal story / journey, (2) value + "you can do it too", (3) contrarian POV. **Slot A1 je vždy osobní příběh** — narativní, upřímný, scéna z reálného života/buildování (ne jen suchý milestone-s-číslem); osobní příběhy historicky farmí největší engagement. Aplikuje conversion-format gaty (17–58 slov, first-person, žádná otázka-jako-hook, žádný "check it out"/link v těle, žádná imperativní tip šablona) + memory feedback + fact-check. Použij kdykoli Daniel řekne: "naplánuj zítřek", "daily pipeline", "naplánuj čtvrtek/pátek/sobotu/neděli/pondělí/úterý/středu", "spusť denní plán Substack", "připrav substack na zítra", "plán na zítra", "naplánuj 3 notes", "do daily plan". Default časy: 8:30 / 13:30 / 19:30 CET.
---

# substack-daily-pipeline (v3.2 — Hub session-feed grounded A1)

**Co se změnilo proti v3.1:** A1 personal-story slot už **nesmí halucinovat** ("I write at 6 AM…") — povinně se opírá o **posledních 7 dní session summaries z Hubu** (`GET /api/sessions?since=7d`). Hub vrací summary + facts + ended_at per session — model si z toho poskládá konkrétní moment (kdy se to dělo, na čem, co se zaseklo, co dopadlo). mem0 zůstává jen jako safety-net doplněk pro decisions/preferences. Pokud 7d feed = prázdný a žádný session moment nematchuje target date → **A1 hard-skip + Telegram alert přes subhook relay**. Radši 2 notes než vymyšlená scéna.

**Co dál zůstává z v3.1:** zahozeny restacky / komentáře / self-restack / feed_pool / promo-batch (Daniel dělá engagement ručně). **3 originální Notes/den** (méně jen pokud A1 skip), conversion-driven archetypy, branded `imageSpec` per note, `auto` mód pro cloud routinu, closed-loop insights gate.

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

### A1 — Personal story / journey  (`format: "milestone"`)
**Vždy osobní příběh ukotvený v REÁLNÉM session momentu z posledních 7 dní.** Narativní first-person scéna, ne jen suché číslo. Konkrétní moment z buildování: jaký bug se řešil v úterý večer, který commit dopadl jak, kdy se zaseklo na čem, malý zádrhel a co tě naučil. Upřímné, klidně sebeironické a zranitelné. Číslo/milestone je **volitelné koření**, ne jádro; když ho má, zarámuj ho příběhem ("Po hodině, co dcera usnula, jsem…"), ne holým statem.

**Primární zdroj (POVINNÝ):** Hub session feed posledních 7 dní — `GET https://dcw-context-hub.vercel.app/api/sessions?since=7d&limit=50` s `Authorization: Bearer $CONTEXT_HUB_API_TOKEN` (token dodá routine prompt, nikdy ho nedávej do skill MD). Vrací `{generated_at, since, count, sessions: [{ended_at, project, summary, facts: [{text, scope, category}], ...}, ...]}`. Model si z `ended_at + summary + facts` poskládá konkrétní moment pro target date (preferuj **včerejšek**, fallback předvčerejšek, fallback poslední pracovní den v rámci 7d okna). Vyber 1 session jako kotvu příběhu, ostatní jako kontext.

**Sekundární zdroj (safety-net):** `mcp__c59fb103…__mem0_search({query:"personal moment OR personal", user_id:"daniel"})` — jen pokud Hub feed je řídký nebo nematchuje. mem0 nikdy není primární — vrací staré decisions, ne čerstvé sessions.

**Doplňky (jako koření, ne základ):** `me.md` (osobní kontext — rodina, terapie, večerní okna), `get_aggregates` (sub delta), nejnovější článek, dcw-context-hub `get_context` pro projekt, na kterém session běžela.

**Hard rule — zákaz halucinace:** Pokud `Hub /api/sessions?since=7d` vrátí `count: 0` NEBO žádná session se nehodí jako kotva → **A1 hard-skip**: nikdy nevracej fake scénu typu "I write at 6 AM…". V `auto` módu pošli Telegram alert přes subhook relay (viz Cloud mode). Plánuj jen A2 + A3 (2 notes je OK). V interaktivním módu surface Danielovi jako: `A1 SKIPPED — no Hub session moment last 7d. Plánuju 2 notes.`

- Story-first (preferuj): *"My daughter fell asleep at 8. By 8:15 I was staring at a Wan render timeout I'd been ignoring for three days. Bumped it to 900s. It worked. Felt dumb it took me that long."*
- Milestone-as-story (OK): *"I doubled my subscribers today. From 1 to 2 🤪"*

**Story slot smí být delší:** word-gate pro A1 je **17–80 slov** (příběh potřebuje místo na scénu); ostatní gaty platí.

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

1. **17–58 slov** (A2/A3). **A1 personal story: 17–80 slov** — příběh potřebuje místo na scénu. Reject <17 (one-linery = lajky, ne suby); reject A2/A3 >70, A1 >85.
2. **First-person povinně** (I / my / we).
3. **Žádná otázka jako hook ani jako jediné CTA.** (Měkká otázka uvnitř těla OK, default žádná.)
4. **Žádný "check it out" / holý link v těle.** Výjimka: A2 promo varianta, kde link renderuje platforma přes `articleId` (ne nalepený "check it out").
5. **Žádná imperativní tip šablona** ("Set X", "Wire Y", "Use X", "Leverage X" jako otevírka).
6. **Sentence-per-line** — prázdný řádek mezi každou větou.
7. **EN, žádný series prefix.**
8. Dedup proti posledním 15 originálům (`list_recent_notes`) — žádné opakování otevíracího slova ani úhlu 3× po sobě.

## Image element per note (povinné — každá note má grafiku)

Každá ze 3 not dostane `imageSpec` (JSON), který grownote vyrenderuje jako branded 1080×1080 PNG a připne k notě **až při publishu** (z `notes_log.image_spec`). Tři šablony (`grownote/lib/note-image/templates.ts`), DCW paleta:

- **`stat_card`** — `{template:"stat_card", headline, accentWord?, stats:[{label,value,accent?}]}` → nadpis (serif) + řádek statů. **Pro A1 milestone** s konkrétními čísly.
- **`quote_card`** — `{template:"quote_card", quote, attribution?}` → jedna klíčová věta/přesvědčení (serif). **Pro A3 pov a A2** bez čísel. `quote` = nejsilnější věta noty, ≤120 znaků.
- **`journey`** — `{template:"journey", headline?, accentWord?, steps:[{label,value}], highlight?}` → 2–4 kroky s šipkami, `highlight` = index oranžového. **Pro A1**, když má note progres (např. 42→64→74).

Heuristika výběru: A1 story bez tvrdého čísla → `quote_card` (nejsilnější věta příběhu); A1 s konkrétním číslem/progresem → `stat_card`/`journey`. A2 → `stat_card` (má-li číslo) jinak `quote_card`, A3 → `quote_card`.

**imageSpec je VOLITELNÝ — připoj ho jen když má note reálný vizuální payload:** konkrétní číslo/stat (`stat_card`/`journey`) nebo silnou samostatnou citaci ≤120 znaků (`quote_card`). Pokud note nic takového nemá (abstraktní/tenká myšlenka), **imageSpec VYNECH úplně** a naplánuj note jako text-only (`schedule_note` bez `imageSpec`). **Nikdy negeneruj prázdnou kartu** — žádný blank/whitespace `quote`, žádné `stats:[]`, žádné `steps:[]`. Lepší text-only note než blank obrázek.

Pravidla obsahu obrázku: `headline`/`quote` parafráze noty (ne celé tělo), čísla MUSÍ sedět s textem noty i fact-checkem, accentWord = 1 slovo. Náhled (volitelně): `POST /api/mcp/preview-note-image {spec}` (Bearer `GROWNOTE_MCP_TOKEN`) → PNG.

## Workflow

### 1. Pre-flight (silent, parallel)
- `mcp__2bd50541…__trigger_substack_sync()` — čerstvá data
- `mcp__2bd50541…__get_aggregates()` — sub count + delta (palivo pro A1)
- `mcp__2bd50541…__list_scheduled_items({actionType:"note", status:"scheduled", fromIso:<den 00:00>, toIso:<den 23:59>})` — obsazené sloty
- `mcp__2bd50541…__list_recent_notes({limit:20})` — dedup base + cookie health (pokud volání selže na auth → **STOP**, surface: "Cookie expired — refresh v grownote /settings.")

### 2. Source material (parallel, silent)
- **Hub session feed (POVINNÉ pro A1)**: `GET https://dcw-context-hub.vercel.app/api/sessions?since=7d&limit=50` s `Authorization: Bearer $CONTEXT_HUB_API_TOKEN`. Tohle je primární palivo pro A1 personal-story (viz „A1 — Personal story" pravidla výše). Když API selže nebo `count: 0` → **A1 skip** (nedrafťuj fake story).
- **mem0**: `mcp__c59fb103…__mem0_search({query:"decision OR discovery OR learning", user_id:"daniel"})` → filtr posledních 7d, category∈{decision,discovery,learning} → palivo pro A2/A3. **Safety-net pro A1**: jen pokud Hub feed neposkytl kotvu (např. session bez summary).
- **git**: `git -C ~/foundary-tools/<repo> log --since=7.days --oneline` pro grownote, drippery, article-forge, archieve-concierge, subhook (skip docs/wip/merge) → milestones + value (A2). V `auto` módu vynech (cloud stroj nemá repa).
- **articles**: `mcp__eb89b7e1…__list_articles` → nejnovější publikovaný; pokud ≤3 dny starý → promo kandidát pro A2
- **dcw-context-hub**: `get_context({project:"grownote"})` pro recent state (volitelně)
- **insights (closed loop, povinné)**: `mcp__eb89b7e1…__get_content_insights({days:28, format:"markdown"})` → co reálně performuje (top articles, risers, evergreen, tag performance, recommendations). Použij při volbě témat: téma rising/top článku s vysokým read ratio → follow-up angle pro A2/A3; evergreen winner → promo kandidát pro A2 (má přednost před náhodným nejnovějším článkem, pokud insights neukazují opak). Pokud tool selže, pokračuj bez něj — nesmí zablokovat denní output.
- **attribution pravidla (povinné)**: `mem0_search({query:"attribution"})` → aplikuj poslední týdenní akční pravidla (co reálně konvertuje subscribery) na výběr archetypů, hooky i formát
- **Notion proxy**: `search_notion` (session recaps, research reporty, playbooky) pro fakta a čísla k tématům

### 3. Draft 3 notes (1× A1 personal story, 1× A2, 1× A3)
Aplikuj všechny gaty (sekce výše). Každá jiný angle z `lib/angles.ts`. Žádný motivational filler ("you've got this", "unlock", "game-changer"). **A1 musí být osobní příběh ukotvený v konkrétní session z Hub feedu** (krok 2) — konkrétní scéna/moment/pocit, ne výčet úspěchů; otevírej scénou nebo napětím, ne "Just shipped / Today I". Pozor: zákaz otevírek "This morning / Today I / Just shipped" platí dál — story otevírej situací ("My daughter fell asleep at 8…"), ne časovým razítkem. **Pokud Hub feed prázdný / žádný moment nematchuje → A1 SKIP** (viz pravidla A1, hard rule) a pokračuj jen s A2 + A3. Ke každé notě sestav i `imageSpec` (viz „Image element per note") — pro A1 story bez tvrdého čísla použij `quote_card` s nejsilnější větou.

### 4. Fact-check gate
Každé osobní tvrzení s číslem / názvem toolu / dobou trvání → ověř paralelně proti **mem0 + dcw-context-hub** (+ Notion pokud třeba). ✅ verified / ❌ contradicts → auto-rewrite / ⚠️ unverifiable → flag, Daniel potvrdí. Hlavní riziko: A1 čísla (sub count, počty článků) — vždy proti `get_aggregates`.

### 5. Light review (internal, max 2 kola)
Round 1 = critique proti gatům. Round 2 = rewrite failing. 3. kolo → drop. Žádné 3-round ceremony.

### 6. Output (single message)
```
[TARGET DATE]   (cookie OK / ⚠️ expired)
Sub count: <N>  (+<d7> 7d / +<d30> 30d)

  08:30  A1 story         #<angle>   "<prvních 70 znaků…>"   [fact-check]
  13:30  A2 value-invite  #<angle>   "<prvních 70 znaků…>"   [fact-check]   (promo→"<title>" pokud aplikováno)
  19:30  A3 pov           #<angle>   "<prvních 70 znaků…>"   [fact-check]

Fact-check: ✅ N / ⚠️ N / ❌ N
```
End: **"Pošli `ok` / `drop N` / `edit N <text>` / `stop`."**

### 7. Po ack — schedule
- `ok` → pro každou notu `mcp__2bd50541…__schedule_note({content, scheduledFor:<ISO CET slot>, format:<archetyp>, imageSpec:<viz výše>, articleId?, ctaType?})`. Sloty obsazené z kroku 1 → posuň na další volný (8:30→9:30, 13:30→14:30, 19:30→20:30).
- `drop N` → tu notu nescheduluj.
- `edit N <text>` → swap obsah, re-gate, pak schedule.
- `stop` → nic nescheduluj, vrať 3 drafty jako markdown.

Cron `scheduledItemsCron` v grownote (1 min) auto-publikuje v `scheduledFor`.

## Cloud / autonomous mode (`auto`)

Když je skill invokován s argem `auto` (denní cloud routina, ne interaktivní):
- **Přeskoč ack-gate** (krok 6 výstup + čekání) — rovnou naplánuj všechny notes (krok 7 `ok` větev) hned po light review.
- **Zdroje jen cloud-safe**: **Hub `/api/sessions?since=7d` (POVINNÉ pro A1)** + mem0 + `get_aggregates` + `list_articles` + dcw-context-hub. **Přeskoč lokální `git log`** (cloud stroj repo nemá) — A1 milestones ber z Hub session feedu, A2 value z mem0 + nejnovějšího článku + `get_aggregates` + `get_content_insights`.
- Fact-check gate platí dál (mem0 + dcw-context-hub). Když ❌ contradicts a nejde auto-rewritnout do gatů → tu notu **dropni** (radši 2 notes než halucinace), zaloguj.
- **A1 hard-skip protokol**: pokud Hub `/api/sessions?since=7d` vrátí `count: 0` nebo neposkytne kotvu → A1 SKIP a do Telegram souhrnu připoj řádek `A1 dropped: no session moment in last 7d`. Plánuj jen A2 + A3.
- Po naplánování pošli souhrn přes subhook Telegram relay (`NOTIFY_KEY` dodá routine
  prompt — NIKDY ho nedávej do tohoto public skillu):
  `curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -d "Substack notes scheduled — <YYYY-MM-DD>: <N> notes at <slots> CET (images only when meaningful). <A1-skip flag if any>. Review in grownote /schedule."`
- imageSpec se generuje stejně jako v interaktivním módu.
- Stop POUZE na cookie-expired při pre-flightu — surface error (Telegram relay) a skonči.

## Anti-patterns
- **Nikdy nedrafťuj A1 personal story bez Hub session feedu kotvy** — žádné "I write at 6 AM…" fantazie. Když není reálný moment, A1 SKIP.
- Nikdy neplánuj restacky / komentáře / self-restacky — Daniel je dělá ručně (záměr v3).
- Nikdy >3 notes. Méně než 3 (typicky 2) OK jen pokud A1 SKIP (Hub feed prázdný).
- Nikdy one-liner (<17 slov) jako originál — farmí lajky, ne suby.
- Nikdy imperativní tip ("Set X / Wire Y") — historicky 0 konverzí.
- Nikdy otázka jako hook.
- Nikdy "check it out" / holý link v těle (kromě A2 promo přes articleId).
- Nikdy motivational filler ani "This morning / Today I / Just shipped" otevírky.
- Nikdy neplánuj před ackem (mimo `auto` mód).

## Sister skills
- `substack-daily-review` — batch review naplánovaných items (stále funguje na notes).
- `substack-add-handle <handle>` — wantlist (jen pro ruční engagement discovery).
