---
name: substack-daily-pipeline
description: |
  Single-pass plánovač Danielova denního Substacku — engine v3.3 (2026-07-04, evidence-first anti-halucinace), conversion-driven. Plánuje POUZE 3 originální Notes/den (žádné restacky, komentáře ani self-restacky — ty Daniel dělá ručně). Tři notes = tři archetypy (analýza 401 notes přes /api/v1/note_stats: 0.13% conv, jen 7 notes vůbec získalo suba): (1) personal story / journey, (2) value + "you can do it too", (3) contrarian POV. **Slot A1 je vždy osobní příběh** — narativní a upřímná scéna z reálného života/buildování, ALE musí obsahovat konkrétní kotvící specifikum (číslo / pojmenovaný detail / konkrétní výsledek), ne jen náladu. Aplikuje conversion-format gaty (specificity opener — otevírej konkrétním číslem/detailem/výsledkem; 25–58 slov; first-person; žádná otázka-jako-hook; žádný "check it out"/link v těle; žádná imperativní tip šablona) + memory feedback + tvrdý fact-check (každé číslo z verified zdroje, nikdy vymyšlené). Použij kdykoli Daniel řekne: "naplánuj zítřek", "daily pipeline", "naplánuj čtvrtek/pátek/sobotu/neděli/pondělí/úterý/středu", "spusť denní plán Substack", "připrav substack na zítra", "plán na zítra", "naplánuj 3 notes", "do daily plan". Default časy: 8:30 / 13:30 / 19:30 CET.
---

# substack-daily-pipeline (v3.2 — conversion-driven, notes-only, image-per-note)

**Co se změnilo proti v2:** zahozeny restacky / komentáře / self-restack / feed_pool / promo-batch (Daniel dělá engagement ručně — automatizace nekonvertovala). Zůstávají **3 originální Notes/den**, cílené na formáty, které jako jediné reálně přiváděly subscribery. **v3.1:** každá note má branded grafiku (`imageSpec` → grownote render při publishu) a skill umí `auto` mód pro cloud routinu (bez acku).

**v3.2 (2026-06-15, evidence-based upgrade — deep research 100 agentů, 25 claimů → 5 přežilo adversariální verify):** (1) přidán hard gate **specificity opener** — note otevírá konkrétním číslem / pojmenovaným detailem / specifickým výsledkem (research: specificity opener konvertuje ~20× víc než vague, analýza 9 641 notes 3.13 vs 0.15 subs); (2) word-gate dolní hranice **17 → 25** (sweet spot 31–60); (3) A1 přerámován — story už NENÍ "garantovaně nejlepší engagement"; engagement ≠ conversion, story musí nést konkrétní kotvící specifikum; (4) **fact-check zpřísnější** — každé číslo z verified zdroje (`get_aggregates` / `get_content_insights` / mem0 / dcw-hub), jinak číslo VYNECH, nikdy nevymýšlej; (5) nová sekce **Redraft protocol** pro deterministický Telegram/remote redraft jedné konkrétní noty. Kill-pattern gaty (no link / question-hook / imperative / filler) research POTVRDIL — drží beze změny.

**v3.3 (2026-07-04, anti-halucinace):** Daniel reportoval, že notes halucinují (nepublikuje/maže je). Root cause: specificity-opener tlak + fact-check jako sebe-kontrola v jednom průchodu. Fix = strukturální: (1) nový krok **2.5 Evidence block** — fakta se PŘED draftem vypíšou verbatim jako očíslované E-itemy se zdrojem; (2) draft smí čísla/události/milestones brát JEN z E-bloku (`facts:` per note); (3) fact-check gate = mechanický trace claim→E<n>, ne ověřování po paměti; (4) bez evidence → kvalitativní note bez čísel (validní outcome, ne selhání).

## Proč zrovna tyto 3 archetypy (data, ne dojem)

Analýza **všech 401 notes (27.3.–2.6.2026)** přes `https://substack.com/api/v1/note_stats/{c-id}` (card `new_subscribers`): **5956 impressions → 8 free subs (0 paid) = 0.13 %**, jen **7 notes** vůbec konvertovalo. **Reach ≠ konverze** — note s 400 impressions (restack-reakce "…Sharing.") = 0 subs. Konvertovaly výhradně osobní/value/POV notes, i při 12–33 impressions. Restacky, gratitude a one-linery farmí lajky, ne suby → proto vypadly z pipeline.

**Externí evidence (deep research 2026-06-15, adversariálně ověřeno — 25 claimů, jen 5 přežilo):**
- **Algoritmus 2026 cílí na subscriptions, ne engagement** (primární zdroj: Mike Cohen, Substack Head of ML — *"goal is to get people to discover, subscribe, and ideally pay"*). Likes/reach jsou inputy, ne cíl.
- **Nejsilnější conversion driver = specificity opener** (konkrétní číslo / credential / pojmenovaný výsledek na začátku). Analýza 9 641 notes: specificity opener **3.13 subs** vs **0.15** u vague (~20×). Tohle je #1 páka — promítá se do gate #1 níže.
- **Engagement ≠ conversion.** Claim "story konvertuje 10× víc než tips" byl VYVRÁCEN (0-3). Archetypy A1/A2/A3 jsou **rozumný prior, ne prokázané optimum** — klíč je specificita uvnitř každého archetypu, ne archetyp sám. Nepiš A1 story jako "emocionální náladu bez čísla" v domnění že to konvertuje; engagement (lajky) a conversion (suby) jsou různé cíle.
- **Kill-patterny potvrzeny** (shodují se s tvými 401-note daty): "Follow me for more", repost headline+link, AI motivational filler — farmí lajky, ne suby. → kryjí current gaty 3–5.
- **Distribuce = cross-publication audience overlap trénovaný restacky** → ruční restacky (mimo tento skill) jsou pro reach not důležité; tady neřešíme, ale neignoruj je.

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
**Osobní příběh s konkrétním kotvícím specifikem.** Narativní first-person scéna z reálného života: večerní okno po práci a dítěti, malý zádrhel a co tě naučil, posun identity, terapie/rodina/únava promítnutá do buildování, malé vítězství nebo selhání. Upřímné, sebeironické, zranitelné. **ALE: story NENÍ garantovaný konverzní formát** (engagement ≠ conversion — viz evidence výše). Aby konvertovala, MUSÍ nést konkrétní kotvící specifikum: číslo, pojmenovaný detail, konkrétní výsledek nebo časový/místní detail — ne jen abstraktní náladu. Čistě emocionální story bez jediného konkrétna = lajky, ne suby.
- Story s konkrétnem (preferuj): *"My daughter fell asleep at 8. By 8:15 I was staring at a bug I'd avoided for three days. I almost closed the laptop. Then I didn't — and shipped the fix in 40 minutes."*
- Milestone-as-story (OK): *"In a month, I went from 'AI Solo Founder' to 'Digital Craft Workshop' — mostly because the first name never felt like me."* · *"I doubled my subscribers today. From 1 to 2 🤪"*
Zdroj: `me.md` (osobní kontext — rodina, terapie, večerní okna, motivace), mem0 personal/learning, `get_aggregates` (sub delta — verified číslo), git milestones, dcw-context-hub state.
**Story slot smí být delší:** word-gate pro A1 je **25–80 slov** (příběh potřebuje místo na scénu); ostatní gaty platí.

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

1. **Specificity opener (NEJSILNĚJŠÍ gate, ~20× lift).** První věta každé noty MUSÍ obsahovat konkrétní specifikum: číslo, credential, pojmenovaný nástroj/výsledek, časový nebo místní detail. Reject vague/generic-thought opener ("I've been thinking about…", "There's something about…", "Lately I realized…") bez jakéhokoli konkrétna. A1 story smí otevřít scénou, ale to konkrétno musí padnout do prvních ~2 vět. **Každé číslo v openeru projde fact-check gate (krok 4) — žádné vymyšlené číslo jen kvůli specificitě.**
2. **25–58 slov** (A2/A3). **A1 personal story: 25–80 slov** — příběh potřebuje místo na scénu. Reject <25 (one-linery / příliš krátké = lajky, ne suby; sweet spot 31–60); reject A2/A3 >70, A1 >85.
3. **First-person povinně** (I / my / we).
4. **Žádná otázka jako hook ani jako jediné CTA.** (Měkká otázka uvnitř těla OK, default žádná.)
5. **Žádný "check it out" / holý link v těle.** Výjimka: A2 promo varianta, kde link renderuje platforma přes `articleId` (ne nalepený "check it out").
6. **Žádná imperativní tip šablona** ("Set X", "Wire Y", "Use X", "Leverage X" jako otevírka).
7. **Žádný "Follow me for more" / subscribe-bait CTA** (research: farmí lajky, ne suby).
8. **Sentence-per-line** — prázdný řádek mezi každou větou.
9. **EN, žádný series prefix.**
10. Dedup proti posledním 15 originálům (`list_recent_notes`) — žádné opakování otevíracího slova ani úhlu 3× po sobě.

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
- **mem0**: `mcp__c59fb103…__mem0_search({query:"decision OR discovery OR learning", user_id:"daniel"})` → filtr posledních 7d, category∈{decision,discovery,learning} → palivo pro A2/A3
- **git**: `git -C ~/foundary-tools/<repo> log --since=7.days --oneline` pro grownote, drippery, article-forge, archieve-concierge, subhook (skip docs/wip/merge) → milestones (A1) + value (A2)
- **articles**: `mcp__eb89b7e1…__list_articles` → nejnovější publikovaný; pokud ≤3 dny starý → promo kandidát pro A2
- **dcw-context-hub**: `get_context({project:"grownote"})` pro recent state (volitelně)
- **insights (closed loop, povinné)**: `mcp__eb89b7e1…__get_content_insights({days:28, format:"markdown"})` → co reálně performuje (top articles, risers, evergreen, tag performance, recommendations). Použij při volbě témat: téma rising/top článku s vysokým read ratio → follow-up angle pro A2/A3; evergreen winner → promo kandidát pro A2 (má přednost před náhodným nejnovějším článkem, pokud insights neukazují opak). Pokud tool selže, pokračuj bez něj — nesmí zablokovat denní output.
- **attribution pravidla (povinné)**: `mem0_search({query:"attribution"})` → aplikuj poslední týdenní akční pravidla (co reálně konvertuje subscribery) na výběr archetypů, hooky i formát
- **Notion proxy**: `search_notion` (session recaps, research reporty, playbooky) pro fakta a čísla k tématům

### 2.5 Evidence block (HARD — sestav PŘED draftem)
Z výstupů kroků 1–2 sestav očíslovaný seznam faktů, jediný povolený sklad pro krok 3:
```
E1: "subs 214, +3 za 7d" (get_aggregates)
E2: "2026-07-03 dokončen Threads growth engine, 3 PC tasky" (hub sessions)
E3: "'Same 26 Views…' — video reached 3x more strangers" (list_articles)
```
Pravidla: každý E-item = VERBATIM přepis z tool outputu (čísla nikdy neparafrázuj ani nezaokrouhluj), u každého uveď zdrojový tool. Co není v E-bloku, NEEXISTUJE — žádná čísla, události ani milestones z paměti nebo trénink dat. Prázdný/tenký E-blok je validní stav → notes budou kvalitativní (viz krok 3).

### 3. Draft 3 notes (1× A1 personal story, 1× A2, 1× A3)
Aplikuj všechny gaty (sekce výše). **Grounding pravidlo:** každé číslo, událost ("I shipped/built/fixed X", "yesterday/this week"), doba, milestone i pojmenovaný výsledek smí pocházet POUZE z E-bloku (krok 2.5); ke každé notě si poznamenej `facts: [E1, E3]`. Scéna a pocit v A1 smí být rekonstruované, ale událost uvnitř musí být z E-bloku. Pokud pro slot není použitelná evidence → note je kvalitativní: specificity opener splň pojmenovaným nástrojem/akcí/detailem (ne číslem) a text neobsahuje ŽÁDNÉ číslo — to je lepší výsledek než vymyšlený stat. Každá jiný angle z `lib/angles.ts`. Žádný motivational filler ("you've got this", "unlock", "game-changer"). **A1 musí být osobní příběh** — konkrétní scéna/moment/pocit, ne výčet úspěchů; otevírej scénou nebo napětím, ne "Just shipped / Today I". Pozor: zákaz otevírek "This morning / Today I / Just shipped" platí dál — story otevírej situací ("My daughter fell asleep at 8…"), ne časovým razítkem. Ke každé notě sestav i `imageSpec` (viz „Image element per note") — pro A1 story bez tvrdého čísla použij `quote_card` s nejsilnější větou.

### 4. Fact-check gate (HARD — mechanický trace proti E-bloku)
**Postup, ne sebe-ujištění:** z finálních textů (vč. `imageSpec`) vypiš KAŽDÝ faktický claim — číslo, datum, událost, milestone, název, dobu trvání — jako samostatný řádek a ke každému přiřaď E<n> z kroku 2.5. Claim bez odpovídajícího E-itemu = ❌, bez výjimky: přepiš notu bez toho claimu, nebo notu dropni (auto mód; radši 2 notes než halucinace). Nikdy neověřuj "po paměti" — jediná autorita je E-blok.

Mapování zdrojů (kde co ověřit):
- **Sub count / delta** → `get_aggregates` (jediný zdroj pravdy, nikdy nehádej).
- **Article metriky** (views, reads, read ratio, top/rising) → `get_content_insights` / `list_articles`.
- **Build fakta / rozhodnutí / časy / názvy** → mem0 (`mem0_search`) + dcw-context-hub (`get_context`) + git log (interaktivní mód) + Notion (`search_notion`).
- **Cokoli neověřitelné z těchto zdrojů** → ⚠️ flag. Interaktivní mód: Daniel potvrdí. `auto` mód: tvrzení **přeformuluj bez čísla** nebo notu **dropni** (radši 2 notes než halucinace).

Verdikty: ✅ verified → ponech · ❌ contradicts → auto-rewrite na verified hodnotu nebo vynech · ⚠️ unverifiable → viz výše. Hlavní riziko: A1 čísla (sub count, počty článků) — vždy proti `get_aggregates`, nikdy "z hlavy".

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
Grounding (fakta slovy, ne kódy — Daniel je musí umět zkontrolovat na první pohled):
  A1 ← "subs 214, +3/7d" (get_aggregates)
  A2 ← "'Same 26 Views' top riser, 61% read ratio" (insights)
  A3 ← žádná — jen názor/scéna
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
- **Přeskoč ack-gate** (krok 6 výstup + čekání) — rovnou naplánuj všechny 3 notes (krok 7 `ok` větev) hned po light review.
- **Zdroje jen cloud-safe**: mem0 + `get_aggregates` + `list_articles` + dcw-context-hub. **Přeskoč lokální `git log`** (cloud stroj repo nemá) — milestones ber z `get_aggregates` (sub delta) + nejnovějšího článku + mem0 decisions.
- Fact-check gate platí dál (mem0 + dcw-context-hub). Když ❌ contradicts a nejde auto-rewritnout do gatů → tu notu **dropni** (radši 2 notes než halucinace), zaloguj.
- Po naplánování pošli **Telegram preview se sloty** přes `send_telegram_message` (tool čte token z env sám) — formát pro redraft referenci:
  ```
  📝 Substack plán <YYYY-MM-DD>
  1 · 8:30  story  "<prvních 60 znaků…>"
  2 · 13:30 value  "<prvních 60 znaků…>"
  3 · 19:30 pov    "<prvních 60 znaků…>"
  Redraft: odpověz `redraft 2` (+ volitelně hint, např. `redraft 2 víc osobní`).
  ```
  Číslování 1/2/3 = pořadí podle času = stabilní index pro `substack-redraft-watch` (čte `list_scheduled_items` seřazené podle `scheduledFor`). Pošli i ntfy souhrn (topic `daniel-substack`) jako dřív.
- imageSpec se generuje stejně jako v interaktivním módu.

## Redraft protocol (Telegram / remote — DETERMINISTICKÝ, sahej jen na jednu notu)

**Účel:** když Daniel z Telegramu (nebo kdekoli remote) řekne "redraftni notu 2" / "uprav 1" / "přepiš tu story", redraftuj **právě tu jednu** konkrétní naplánovanou notu — NIKDY nehádej, NIKDY nesahej na ostatní, NIKDY nezahoď celý plán.

**Identifikace target noty (povinné, v tomto pořadí):**
1. Načti dnešní/cílové naplánované notes: `list_scheduled_items({actionType:"note", status:"scheduled", fromIso:<den 00:00>, toIso:<den 23:59>})`. Seřaď podle `scheduledFor` → to je stabilní index **1/2/3** = sloty 8:30 / 13:30 / 19:30.
2. Z příkazu vytáhni **explicitní identifikátor**: číslo slotu (1/2/3), čas (8:30…), archetyp (A1/story, A2/value, A3/pov), nebo `scheduledItemId`. Namapuj na konkrétní item.
3. **Pokud je target nejednoznačný** (žádné číslo/čas/archetyp, nebo víc kandidátů) → **NEHÁDEJ**. Pošli zpět Telegram dotaz: "Kterou notu? 1 (8:30 story) / 2 (13:30 value) / 3 (19:30 pov)?" a skonči bez změny. Lepší se zeptat než redraftnout náhodnou.

**Provedení redraftu (jen na matchnutém item):**
4. **Fresh draft, ne kosmetický rewrite** (per `feedback_restack_redraft_fresh_reaction` / `feedback_comment_redraft_fresh_reaction`): drž **archetyp + angle** původní noty, ale napiš nový obsah od nuly podle případného hintu ("víc osobní", "jiný úhel"). Pokud Daniel dal konkrétní text → použij ho jako základ.
5. Projeď **všechny gaty** (specificity opener, word-band, kill-patterny) + **fact-check gate** (krok 4 — každé číslo verified, nikdy vymyšlené). imageSpec přegeneruj jen pokud se změnila čísla/quote.
6. Zapiš **výhradně** na ten jeden item: `update_scheduled_item({id:<scheduledItemId>, content, imageSpec?})` (nebo `redraft_scheduled_item`). Ostatní 2 notes se nedotýkej.
7. Pošli Telegram potvrzení: "✏️ Redraft slot <N> (<archetyp>, <čas>): '<prvních 70 znaků…>' — fact-check ✅". Při ❌/⚠️ čísle to v potvrzení uveď.

**Hard pravidla:** nikdy nepřeplánuj čas (drž `scheduledFor`), nikdy neredraftuj víc než žádanou notu, nikdy nevytvářej novou notu místo úpravy existující, nikdy neredraftuj už publikovanou notu (status ≠ `scheduled` → odmítni a oznam).

## Anti-patterns
- Nikdy neplánuj restacky / komentáře / self-restacky — Daniel je dělá ručně (záměr v3).
- Nikdy <3 nebo >3 notes (pokud Daniel explicitně neřekne jinak).
- Nikdy one-liner (<25 slov) jako originál — farmí lajky, ne suby.
- Nikdy vague/generic-thought opener bez konkrétna — porušuje gate #1 (specificity).
- Nikdy vymyšlené číslo kvůli "specificitě" — každé číslo z verified zdroje (fact-check gate).
- Nikdy imperativní tip ("Set X / Wire Y") — historicky 0 konverzí.
- Nikdy otázka jako hook ani "Follow me for more" CTA.
- Nikdy "check it out" / holý link v těle (kromě A2 promo přes articleId).
- Nikdy motivational filler ani "This morning / Today I / Just shipped" otevírky.
- Nikdy neplánuj před ackem.
- Redraft: nikdy nehádej target notu — při nejednoznačnosti se zeptej.

## Sister skills
- `substack-daily-review` — batch review naplánovaných items (stále funguje na notes).
- `substack-add-handle <handle>` — wantlist (jen pro ruční engagement discovery).
