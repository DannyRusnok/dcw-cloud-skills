---
name: substack-daily-pipeline
description: |
  Single-pass plánovač Danielova denního Substacku — engine v3.4 (2026-07-09, fact-cooldown proti opakování čísel + povinná obecná note + Hermés delivery), conversion-driven. Plánuje POUZE 3 originální Notes/den (žádné restacky, komentáře ani self-restacky — ty Daniel dělá ručně). Tři notes = tři archetypy (analýza 401 notes přes /api/v1/note_stats: 0.13% conv, jen 7 notes vůbec získalo suba): (1) personal story / journey, (2) value + "you can do it too", (3) contrarian POV. **Slot A1 je vždy osobní příběh** — narativní a upřímná scéna z reálného života/buildování, ALE musí obsahovat konkrétní kotvící specifikum (číslo / pojmenovaný detail / konkrétní výsledek), ne jen náladu. Aplikuje conversion-format gaty (specificity opener — otevírej konkrétním číslem/detailem/výsledkem; 25–58 slov; first-person; žádná otázka-jako-hook; žádný "check it out"/link v těle; žádná imperativní tip šablona) + memory feedback + tvrdý fact-check (každé číslo z verified zdroje, nikdy vymyšlené). Použij kdykoli Daniel řekne: "naplánuj zítřek", "daily pipeline", "naplánuj čtvrtek/pátek/sobotu/neděli/pondělí/úterý/středu", "spusť denní plán Substack", "připrav substack na zítra", "plán na zítra", "naplánuj 3 notes", "do daily plan". Default časy: 8:30 / 13:30 / 19:30 CET.
---

# substack-daily-pipeline (v3.4 — conversion-driven, notes-only, image-per-note)

**Co se změnilo proti v2:** zahozeny restacky / komentáře / self-restack / feed_pool / promo-batch (Daniel dělá engagement ručně — automatizace nekonvertovala). Zůstávají **3 originální Notes/den**, cílené na formáty, které jako jediné reálně přiváděly subscribery. **v3.1:** každá note má branded grafiku (`imageSpec` → grownote render při publishu) a skill umí `auto` mód pro cloud routinu (propose-only od 2026-07-04 — navrhne + čeká na `ok`, viz sekce auto mode).

**v3.2 (2026-06-15, evidence-based upgrade — deep research 100 agentů, 25 claimů → 5 přežilo adversariální verify):** (1) přidán hard gate **specificity opener** — note otevírá konkrétním číslem / pojmenovaným detailem / specifickým výsledkem (research: specificity opener konvertuje ~20× víc než vague, analýza 9 641 notes 3.13 vs 0.15 subs); (2) word-gate dolní hranice **17 → 25** (sweet spot 31–60); (3) A1 přerámován — story už NENÍ "garantovaně nejlepší engagement"; engagement ≠ conversion, story musí nést konkrétní kotvící specifikum; (4) **fact-check zpřísnější** — každé číslo z verified zdroje (`get_aggregates` / `get_content_insights` / mem0 / dcw-hub), jinak číslo VYNECH, nikdy nevymýšlej; (5) nová sekce **Redraft protocol** pro deterministický Telegram/remote redraft jedné konkrétní noty. Kill-pattern gaty (no link / question-hook / imperative / filler) research POTVRDIL — drží beze změny.

**v3.3 (2026-07-04, anti-halucinace):** Daniel reportoval, že notes halucinují (nepublikuje/maže je). Root cause: specificity-opener tlak + fact-check jako sebe-kontrola v jednom průchodu. Fix = strukturální: (1) nový krok **2.5 Evidence block** — fakta se PŘED draftem vypíšou verbatim jako očíslované E-itemy se zdrojem; (2) draft smí čísla/události/milestones brát JEN z E-bloku (`facts:` per note); (3) fact-check gate = mechanický trace claim→E<n>, ne ověřování po paměti; (4) bez evidence → kvalitativní note bez čísel (validní outcome, ne selhání).

**v3.4 (2026-07-09, anti-repetice + obecné notes + Hermés delivery):** Daniel reportoval, že notes se pořád točí kolem stejných čísel (specificity-opener gate tlačí každý den na tytéž agregáty — sub count, views) a čísla jsou navíc často špatně. Fix: (1) nový hard gate **fact-cooldown** (#11) — číslo/stat použité v notě za posledních 7 dní je zakázaný anchor, dokud se hodnota nezmění; sub/follower count max 1× týdně; max 1 nota denně kotvená na opakující se metrice; (2) nový gate **≥1 obecná note denně** (#12) — aspoň jedna ze 3 not je universal insight bez jakéhokoli Danielova čísla/metriky; (3) čísla se z E-bloku přepisují **znak-po-znaku** — žádné zaokrouhlování, přepočty ani parafráze; když si dva E-itemy protiřečí, číslo úplně vynech; (4) auto-mode Telegram delivery jde přes **Hermés** (@DcwThreadsBot, stejný bot jako Threads drafty) s `tgMessageId` pro reply-based approval.

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
**General-value varianta (rotuj ji, ~2–3× týdně):** insight, který platí obecně — technika, princip nebo pozorování užitečné každému builderovi, bez Danielových metrik (např. *"Prompt caching can cut Claude API costs by up to 90%…"* je obecný — funguje i bez osobního čísla). Splňuje gate #12.
**Promo varianta:** pokud v posledních ~3 dnech vyšel článek → tento slot může být osobně-rámcované promo (`articleId` set, `ctaType: "promo"`). Pořád se počítá jako 1 ze 3 (žádné extra promo notes).

### A3 — Contrarian POV / filozofie  (`format: "pov"`)
First-person přesvědčení / pohled na AI / building / craft, který zve čtenáře do tvého světa.
Konvertovala: *"Most people use AI as a faster Google. That's fine. But it's not why I use it. I use it as the…"*
Zdroj: `me.md` principy, opakující se témata, mem0 preferences/learnings.
**Defaultně bez čísel** — POV stojí na přesvědčení a zkušenosti, ne na statech; to z něj dělá přirozeného kandidáta na gate #12 (obecná note).

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
10. Dedup proti posledním 15 originálům (`list_recent_notes`) — žádné opakování otevíracího slova ani úhlu 3× po sobě, žádné stejné téma jako včera.
11. **Fact-cooldown (anti-repetice čísel).** Číslo/stat z fact-cooldown listu (krok 1) NESMÍ být anchor nové noty, dokud se jeho hodnota nezmění (nový milestone = OK — pak uveď posun, ne jen stav). Sub count / follower count smí kotvit notu max **1× týdně**. Max **1 ze 3** denních not smí stát na opakující se metrice — zbytek staví na jednorázových faktech (co jsi dnes postavil/zjistil) nebo je obecný (gate #12). Když E-blok nenabízí žádné čerstvé číslo, je to signál pro kvalitativní/obecnou notu, NE pro recyklaci starého čísla.
12. **≥1 obecná note denně.** Aspoň jedna ze 3 not neobsahuje ŽÁDNÉ Danielovo osobní číslo ani metriku — je to universal first-person insight o craftu / AI / buildování / solo práci (pozorování, přesvědčení, princip vyzkoušený v praxi). Specificity opener splň pojmenovaným nástrojem/konceptem/situací, ne číslem. Defaultní kandidát: A3 (pov); alternativně A2 v general-value variantě. Obecná ≠ vágní — pořád konkrétní teze, jen bez osobních dat.

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
- `mcp__2bd50541…__list_recent_notes({limit:30})` — dedup base + cookie health (pokud volání selže na auth → **STOP**, surface: "Cookie expired — refresh v grownote /settings.")
- **Fact-cooldown list (z `list_recent_notes`, HARD):** vypiš každé číslo/stat, které se objevilo v originálních notách za posledních 7 dní (sub count, views, MRR, počty článků/reelů, časy, procenta) + u každého datum posledního použití. Tenhle seznam je vstup pro gate #11 — hodnota na seznamu je zakázaný anchor, dokud se nezmění.

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
Aplikuj všechny gaty (sekce výše). **Rozlož den podle gate #11 a #12:** max 1 nota na opakující se metrice, ≥1 nota úplně bez osobních čísel; čísla z fact-cooldown listu nepoužívej. **Grounding pravidlo:** každé číslo, událost ("I shipped/built/fixed X", "yesterday/this week"), doba, milestone i pojmenovaný výsledek smí pocházet POUZE z E-bloku (krok 2.5) a číslo se přepisuje **znak-po-znaku** — žádné zaokrouhlení, přepočet ("~", "almost", "over") ani parafráze; ke každé notě si poznamenej `facts: [E1, E3]`. Scéna a pocit v A1 smí být rekonstruované, ale událost uvnitř musí být z E-bloku. Pokud pro slot není použitelná evidence → note je kvalitativní: specificity opener splň pojmenovaným nástrojem/akcí/detailem (ne číslem) a text neobsahuje ŽÁDNÉ číslo — to je lepší výsledek než vymyšlený stat. Každá jiný angle z `lib/angles.ts`. Žádný motivational filler ("you've got this", "unlock", "game-changer"). **A1 musí být osobní příběh** — konkrétní scéna/moment/pocit, ne výčet úspěchů; otevírej scénou nebo napětím, ne "Just shipped / Today I". Pozor: zákaz otevírek "This morning / Today I / Just shipped" platí dál — story otevírej situací ("My daughter fell asleep at 8…"), ne časovým razítkem. Ke každé notě sestav i `imageSpec` (viz „Image element per note") — pro A1 story bez tvrdého čísla použij `quote_card` s nejsilnější větou.

### 4. Fact-check gate (HARD — mechanický trace proti E-bloku)
**Postup, ne sebe-ujištění:** z finálních textů (vč. `imageSpec`) vypiš KAŽDÝ faktický claim — číslo, datum, událost, milestone, název, dobu trvání — jako samostatný řádek a ke každému přiřaď E<n> z kroku 2.5. Claim bez odpovídajícího E-itemu = ❌, bez výjimky: přepiš notu bez toho claimu, nebo notu dropni (auto mód; radši 2 notes než halucinace). U čísel navíc porovnej **znak-po-znaku** s E-itemem — 214 ≠ "~200" ≠ "over 210"; jakýkoli rozdíl = ❌. Když si dva E-itemy protiřečí (různé zdroje, různé hodnoty), číslo úplně vynech. Nikdy neověřuj "po paměti" — jediná autorita je E-blok.

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

## Cloud / autonomous mode (`auto` = PROPOSE-ONLY)

> **Zákon (rozhodnutí 2026-07-02, potvrzeno 2026-07-04):** cloud routina **NIKDY neplánuje ani nepublikuje bez Danielova explicitního schválení.** Auto mód = **navrhni a čekej**, ne "naplánuj a oznam po faktu". `schedule_note` v auto módu je ZAKÁZÁN — volá se až po Danielově `ok` (řídí to `substack-redraft-watch`).

Když je skill invokován s argem `auto` (denní cloud routina, ne interaktivní):
- **NEPLÁNUJ.** Připrav 3 notes (draft → gaty → fact-check → light review) přesně jako v interaktivním módu, ale **nevolej `schedule_note`** ani žádný publish. Výstupem je **návrh**, ne naplánovaná nota.
- **Zdroje jen cloud-safe**: mem0 + `get_aggregates` + `list_articles` + dcw-context-hub. **Přeskoč lokální `git log`** (cloud stroj repo nemá) — milestones ber z `get_aggregates` (sub delta) + nejnovějšího článku + mem0 decisions.
- Fact-check gate platí dál (mem0 + dcw-context-hub). Když ❌ contradicts a nejde auto-rewritnout do gatů → tu notu **dropni** (radši 2 notes než halucinace), zaloguj.
- **Zapiš návrh do pending souboru** (Write tool) `%USERPROFILE%\foundary-tools\dcw-context-hub\ops\substack-daily-notes-pending.json` — přepiš celý soubor tímto tvarem (to je jediný zdroj pravdy pro schvalovací krok; `substack-redraft-watch` z něj plánuje po `ok`):
  ```json
  {
    "date": "<YYYY-MM-DD>",
    "createdIso": "<ISO now>",
    "status": "proposed",
    "tgMessageId": null,
    "notes": [
      { "slot": 1, "scheduledFor": "<ISO 08:30 CET>", "format": "milestone",     "angle": "<angle>", "content": "<CELÉ tělo noty 1>", "imageSpec": <obj|null>, "factCheck": "<zdroj/⚠️>", "dropped": false },
      { "slot": 2, "scheduledFor": "<ISO 13:30 CET>", "format": "value_invite", "angle": "<angle>", "content": "<CELÉ tělo noty 2>", "imageSpec": <obj|null>, "factCheck": "<zdroj/⚠️>", "dropped": false },
      { "slot": 3, "scheduledFor": "<ISO 19:30 CET>", "format": "pov",          "angle": "<angle>", "content": "<CELÉ tělo noty 3>", "imageSpec": <obj|null>, "factCheck": "<zdroj/⚠️>", "dropped": false }
    ]
  }
  ```
  (Obsazené sloty z `list_scheduled_items` posuň na další volnou hodinu stejně jako v interaktivním módu a promítni do `scheduledFor`.)
- Pak pošli **návrhový Telegram preview přes Hermés** (@DcwThreadsBot — stejný bot a chat, kam chodí Threads drafty): zapiš celou zprávu do temp souboru (UTF-8) a spusť `python %USERPROFILE%\foundary-tools\dcw-context-hub\ops\threads\threads_client.py send-telegram --file <soubor>`. Z JSON outputu (`{"ok":true,"message_id":N}`) vezmi `message_id` a **dopiš ho do pending souboru jako `tgMessageId`** — `substack-redraft-watch` podle něj páruje reply-based approval. Fallback (jen když Hermés send selže — chybějící token/síť): substack-mcp `send_telegram_message` jako dřív a `tgMessageId` nech `null`. Pro každou notu uveď slot + čas + archetyp label, **CELÉ tělo noty — NIKDY ne ořez / prvních N znaků / `…`** (Daniel schvaluje podle úplného textu; useknuté tělo je bug), řádek s grafikou (`🖼 stat_card: <stat>` / `🖼 quote_card: "<quote>"` / `🖼 text-only`) a fact-check řádek. Header nese počet subů z `get_aggregates`. Formát:
  ```
  📝 Substack notes PROPOSAL — <YYYY-MM-DD> | <N> subs  (nic není naplánováno, čeká na tvoje ok)

  1️⃣ 08:30 CET — Personal Story
  "<CELÉ tělo noty 1>"
  🖼 stat_card: <stat>
  ✅ Fact-check: <zdroj>

  2️⃣ 13:30 CET — Value + Invite
  "<CELÉ tělo noty 2>"
  🖼 stat_card: <stat>
  ✅ Fact-check: <zdroj>

  3️⃣ 19:30 CET — Contrarian POV
  "<CELÉ tělo noty 3>"
  🖼 text-only
  ✅ Fact-check: <zdroj>

  Odpověz REPLYEM na tuhle zprávu: "ok" (naplánuje všechny 3 na jejich sloty) · "edit N <text>" · "redraft N <hint>" · "drop N". Dokud nedáš ok, nic se nepublikuje. (Bare "ok" bez replye projde jen když zrovna nečeká i Threads draft — v tomhle chatu bydlí oba.)
  ```
  Číslování 1/2/3 = `slot` v pending souboru = stabilní index pro `substack-redraft-watch`. Pošli i ntfy souhrn (topic `daniel-substack`) jako dřív, ale formulace **"proposed, awaiting approval"**, ne "scheduled".
- imageSpec se generuje stejně jako v interaktivním módu.
- **Guarantee:** když cokoli selže (cookie expired, fact-check drop na 0 not, Write pending selže), **radši nenaplánuj nic** a oznam to na Telegram — bezpečný failure mode je „nic nepublikováno", ne „publikováno bez schválení".

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
- Nikdy notu kotvenou na čísle, které už v notách běželo v posledních 7 dnech beze změny hodnoty (gate #11) — recyklace stejných statů je přesně to, co Daniel maže.
- Nikdy všechny 3 notes postavené na osobních metrikách — aspoň 1 obecná bez Danielových čísel (gate #12).
- Nikdy číslo zaokrouhlené/parafrázované proti E-bloku — přepis znak-po-znaku, jinak vynech.
- Nikdy imperativní tip ("Set X / Wire Y") — historicky 0 konverzí.
- Nikdy otázka jako hook ani "Follow me for more" CTA.
- Nikdy "check it out" / holý link v těle (kromě A2 promo přes articleId).
- Nikdy motivational filler ani "This morning / Today I / Just shipped" otevírky.
- Nikdy neplánuj před ackem.
- Redraft: nikdy nehádej target notu — při nejednoznačnosti se zeptej.

## Sister skills
- `substack-daily-review` — batch review naplánovaných items (stále funguje na notes).
- `substack-add-handle <handle>` — wantlist (jen pro ruční engagement discovery).
