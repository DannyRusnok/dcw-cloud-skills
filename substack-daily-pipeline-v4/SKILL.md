---
name: substack-daily-pipeline-v4
description: |
  Engine v4 Danielových denních Substack notes (2026-07-23, evidence: analýza 50+50 not @karozieminski/@kevinkermes — templated listicles medián 2 lajky, numbered série a real-number stories 20–50 lajků). 3 noty/den: slot 1 = numbered série z předschváleného banku (TUPÝ scheduler, žádné AI, žádná review), slot 2 = real-number build log (mechanicky dosazená čísla + max 2 rámující věty), slot 3 = střídavě verbatim quote promo článku / contrarian z opinions banku. Slot 2+3 se plánují rovnou (auto-publish) a jdou na Craftie jen jako FYI s opt-outem "ne N". Navíc krok reply-drafts: odpovědi na reakce pod Danielovými notami k odkliknutí. Nahrazuje v3.5 režim (substack-daily-pipeline zůstává jako fallback). Použij když Daniel řekne: "daily pipeline v4", "naplánuj zítřek v4", "spusť v4 notes", "notes engine v4".
---

# substack-daily-pipeline-v4

**Vztah k v3.5:** aditivní větev (feedback_additive_not_rewrite). v3.5 (`substack-daily-pipeline`) zůstává netknutý jako fallback — v4 nepoužívá jeho generic-listicle drafting ani ranní approval gate. Rollback = vypnout schtask `SubstackDailyNotesV4`, zapnout `SubstackDailyNotes`.

**Proč v4 (2026-07-23):** analýza 50+50 not @karozieminski a @kevinkermes — templated listicles medián 2 lajky / 23k followers; numbered série ("Before and after AI #N") a real-number stories 20–50 lajků. Danielovy bolesti v3.5: halucinace/repetice not, ranní review nebaví. v4 = obsah předem schválený nebo mechanicky ukotvený, review nahrazena opt-out FYI.

## Sdílená pravidla (přebírá z v3.5 / dcw-voice — platí pro slot 2+3)

- EN, sentence-per-line (prázdný řádek mezi větami), first-person, žádný series prefix v title smyslu.
- Žádná otázka-jako-hook, žádný "check it out"/holý link v těle (promo jen přes `articleId`), žádný motivational filler, žádná imperativní tip šablona, žádný "Follow me" CTA.
- dcw-voice modul (AI-fráze watchlist, pivot/triplet detektory) na každý AI-generovaný text.
- `angle` povinný z `grownote/lib/angles.ts`.
- **Čísla VÝHRADNĚ z E-bloku, přepis znak-po-znaku** (v3.5 krok 2.5 + gate 4). Žádné číslo mimo E-blok, žádné zaokrouhlování.
- Fact-cooldown: `ops/substack-v4-facts-log.json` (`{facts:[{value,context,usedOn}]}`) — stejné číslo/stat max 1×/7 dní; po naplánování noty zapiš použitá čísla.

## Slot 1 — 08:30 — Numbered série (BEZ AI, BEZ review)

Řeší **`ops/substack-v4-slot1.mjs`** (spouští ho v4 runner .cmd PŘED tímto skillem). Deterministický: další pending entry z `secondbrain/notes-series-bank.md` (střídá S1/S2 podle počtu odeslaných), verbatim INSERT do `grownote.notes_log` (Fly PG přes PC WireGuard, `postgres` modul z article-forge checkoutu; publish dělá substack-mcp worker publishDue), stav v `ops/substack-v4-state.json` (lokální na PC).

**Tento skill slot 1 NEDRAFTUJE, NEEDITUJE a NEREVIEWUJE.** Jediné dovolené interakce:
- Do FYI zprávy (krok 5) přidej řádek co slot 1 poslal (přečti `substack-v4-state.json`).
- Když je bank vyčerpaný nebo `approved: false`, řekni to ve FYI ("slot 1 neběžel — <důvod>, doplň/schval bank").
- Nové entries do banku vznikají JEN na Danielovu žádost v interaktivní session (pravidla v hlavičce banku) a čekají na jeho review.

## Slot 2 — 13:30 — Real-number build log

1. **E-blok ze zdrojů čísel (verbatim, s uvedením toolu):**
   - `mcp__article-forge__list_video_jobs` — reely za posledních 24 h: počet done / failed, kind.
   - `mcp__article-forge__get_daily_analytics` + `mcp__substack-mcp__get_note_stats` / `get_aggregates` — views, subs delta.
   - `git log --since=24.hours --oneline` přes repa v `~/foundary-tools` (PC checkout) — počty commitů (skip merge/wip).
   - Gumroad prodeje: CRM data (substack-mcp /crm zdroje) — jen pokud dostupné, jinak vynech.
2. **Vyber 1–2 čísla**, která (a) nejsou ve fact-cooldown logu za 7 dní, (b) něco vyprávějí (noční render, fail count, commit počet, prodej). Vzor: *"12 reels rendered on my home PC last night. 0 failed. I was asleep the whole time."*
3. **Rigidní šablona:** číslo/pár čísel (mechanicky dosazené z E-bloku) → co to znamená → jedna pointa. AI píše **max 2 rámující věty** kolem čísel. 15–45 slov. `format: "milestone"`, imageSpec `stat_card` jen když čísla stojí za kartu, jinak text-only.
4. **Žádné čerstvé číslo bez cooldownu → slot 2 dnes VYNECH** (napiš to do FYI). Nikdy nerecykluj staré číslo, nikdy nevymýšlej.

## Slot 3 — 19:30 — střídavě podle dne v měsíci

**Lichý den = (a) Verbatim quote promo:**
1. `mcp__article-forge__list_articles` → nejnovější článek publikovaný ≤7 dní.
2. Vyber nejsilnější VĚTU z těla (doslova). **Mechanický substring check:** normalizuj tělo (strip HTML tagy, dekóduj entity, collapse whitespace) a ověř, že quote je přesný substring. Nesedí → zkus jinou větu; žádná nesedí → skip (a) a spadni na (b).
3. Nota = quote (v uvozovkách) + max 1 rámující věta + `articleId` + `ctaType:"promo"`. `format:"value_invite"`.
4. Žádný článek ≤7 dní → spadni na (b).

**Sudý den = (b) Contrarian z opinions banku:**
1. `secondbrain/notes-opinions-bank.md` → první řádek `OK |`, který není v `substack-v4-state.json.usedOpinions`.
2. Pipeline názor **jen FORMÁTUJE** (sentence-per-line, drobné interpunkční úpravy) — obsah, postoj i čísla zůstávají Danielova slova. Nikdy nevymýšlej postoj, nikdy nedopisuj argumenty. `format:"pov"`.
3. Po naplánování přidej identifikátor řádku (prvních 60 znaků) do `usedOpinions` ve state file.
4. Žádný `OK |` řádek → použij (a); nejde ani (a) → slot 3 dnes vynech (napiš do FYI).

## 4. Schedule (auto-publish — ŽÁDNÝ approval gate pro slot 2+3)

Pro slot 2 a 3: `mcp__substack-mcp__schedule_note({content, scheduledFor, format, angle, imageSpec?, articleId?, ctaType?})` rovnou (obsazený slot → +1 h). Ulož `scheduledItemId`. Grownote cron publikuje v čase slotu. *(Změna proti v3.5 zákonu propose-only: rozhodnutí Daniela 2026-07-23 — slot 2+3 jsou mechanicky ukotvené, review nahrazuje opt-out okno do času publikace.)*

## 5. FYI na Craftie (ne approval — auto-publish s opt-outem)

Jedna zpráva `mcp__substack-mcp__send_telegram_message({text, register:"passive"})` s CELÝMI těly (nikdy ořez):

```
📝 Notes v4 — <date> (AUTO — publikují se samy, "ne N" do času slotu = skip)

1️⃣ 08:30 série: <S1-05 odesláno scriptem / neběžel — důvod>
2️⃣ 13:30 build log [#<id>]:
"<CELÉ tělo>"
čísla: <E-zdroje>
3️⃣ 19:30 <quote promo "<title>" / opinion>[#<id>]:
"<CELÉ tělo>"

💬 Reply drafts (nic se neposílá bez tebe):
R1 @<autor>: "<jejich text ≤120 zn>" → "<draft odpovědi>"
R2 …

Reply na tuhle zprávu: `ne N` (odplánuje notu N) · `edit N <text>` · `redraft N <hint>` · `send R1` / `edit R1 <text>`.
```

`messageId` + noty + replyDrafts zapiš do `ops/substack-v4-pending.json`:
```json
{ "date":"YYYY-MM-DD", "engine":"v4", "tgMessageId":<int>, "tgMessageIds":[],
  "notes":[{"slot":2,"scheduledItemId":<id>,"scheduledFor":"<ISO>","content":"<celé tělo>","facts":["..."]},{"slot":3,...}],
  "replyDrafts":[{"idx":"R1","noteId":<id|null>,"commentId":<id|null>,"author":"@handle","theirText":"...","draft":"...","status":"pending"}] }
```
Zpracování odpovědí (`ne`/`edit`/`redraft`/`send`) dělá `substack-redraft-watch` (sekce "v4 branch"). Bez odpovědi noty odejdou samy — to je záměr.

## 6. Reply drafts (náhrada denní komentářové kvóty)

1. `mcp__substack-mcp__get_recent_replies` + `search_activity_replies` + `get_recent_interactors` → reakce/reply na Danielovy vlastní noty za ~24 h, na které neodpověděl.
2. Pro každou (max 5) napiš krátký draft odpovědi: plain simple EN (feedback_engagement_simple_english), 1–3 věty, konkrétní reakce na jejich text, žádné šablony "Thanks for sharing".
3. Drafty jdou do FYI zprávy + pending souboru (viz výše). **NIKDY neposílej komentář bez Danielova `send RN`.**
4. Restacky sem NEPATŘÍ — Daniel je dělá ručně v nedělní dávce.

## Failure guarantee

Cokoli tvrdě selže (cookie expired, žádná evidence, schedule_note error) → dotčený slot vynech, ostatní dokonči, VŽDY pošli FYI s tím co neběželo. Slot 1 je nezávislý (script). Nikdy nefabrikuj obsah, aby "něco odešlo" — prázdnější den je validní outcome.

## Interaktivní mód (Mac session)

Stejný postup, ale před krokem 4 ukaž plán a počkej na `ok` (Daniel je přítomen — opt-out model je pro headless běh; v interakci se prostě zeptej).

## Sister
- `substack-daily-pipeline` (v3.5) — fallback engine, nespouštět souběžně (2 schtasky na stejné sloty = duplicitní noty).
- `substack-daily-review`, `substack-cookie-heal`.
