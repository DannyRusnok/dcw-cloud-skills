---
name: dcw-voice
description: Sdílený voice & anti-AI modul pro VEŠKERÝ Danielův publikační/mluvený obsah — články (article-draft-review, substack-draft-review), Substack notes, a video scénáře (dcw-longform VO). Jedno místo pravdy pro "jak psát/mluvit, aby to znělo jako Daniel a ne jako AI": voice fingerprint, AI-fráze watchlist, causal-pivot / triplet-fatigue / bridge / cadence detektory, humanity linter. Načti tento skill kdykoli generuješ nebo reviduješ text určený k publikaci nebo k namluvení (VO), než ho finalizuješ. Article/Substack/video skilly tento modul REFERENCUJÍ místo aby pravidla duplikovaly. Načti tento skill VŽDY a PROAKTIVNĚ (bez vyžádání) kdykoli Daniel chce napsat, přepsat nebo zreviduovat jakýkoli publikační text — email, welcome email, newsletter, web/landing copy, About page, bio, tagline, Substack příspěvek/note, sociální post, marketing copy. Spouštěcí fráze: "napiš text", "vymysli text", "vymysli email", "uprav text", "přepiš to", "copy pro web", "about page", "welcome email", "bio", "příspěvek", "post", "newsletter", "promise". Pokud Daniel žádá generování či revizi textu k publikaci a tento skill ještě není v této session načtený, načti ho jako PRVNÍ krok, ještě než cokoli napíšeš.
---

# dcw-voice — sdílený voice & anti-AI modul

Jedno místo pravdy. `article-draft-review`, `substack-draft-review`, `substack-notes-draft` a video script-gen (`dcw-longform`) sem odkazují místo aby pravidla kopírovaly.

## Co je text vs. VO (mluvené slovo)

Většina pravidel platí pro OBOJÍ. Výjimky pro **VO / video scénář** (mluvené slovo):
- Em-dash budget, image captions, anchor links, HTML struktura → **N/A** (mluvené slovo).
- Plochá pasáž, punchline budget, pivot/triplet/AI-fráze, voice fingerprint → **platí stejně** (a o to víc — ucho AI-tells slyší).
- VO navíc: žádné "in this video", "let's dive in", "make sure to", "stick around"; mluv jako bys to vysvětloval kolegovi u stolu.

---

## Voice fingerprint (Danielův styl, z 25+ pre-AI článků 2019–2022 + audit 88 ručních Substack notes 2026-08/09)

- Krátké, deklarativní věty. "It is a plug-in system." NE "This elegant plug-in system beautifully orchestrates…"
- Časová značka BEZ scény v openingu: "Today,", "Yesterday,", "Last week", "Wednesday's reel" + fakt (notes 24 %). Scénické openery ("A couple of evenings ago I opened…") a vymyšlené časy ("at 4:23") ❌ — i pro notes. *(Audit notes 2026-09-08.)*
- Long-short střídání — složený odstavec + krátká puenta.
- Osobní preference jako důvod: "I find it helpful when…" / "That's how I like it."
- Mluví za sebe: "For Article Forge specifically, I keep choosing…" NE "You should always…"
- Přímé instrukce: "Look at line 8." / "Take a look below."
- Suchý humor, self-deprecation — v notes jako sebeoslovení / přiznání, ne rétorická figura: "Bruh, Anthropic has a VS Code extension that does exactly this. Sometimes, Daniel… sometimes...", "15% went straight down the drain", "I forgot. 😂", "It sounds cocky, but…".
- *(Jen články, v notes ~0 %)* Absurdní eskalace, bait-and-switch humor.
- Konkrétní čísla: "$0/month", "40 lines", "two minutes per commit".
- *(Jen články, v notes 5 %)* Workshop / bench metafory: "from the bench", "I keep reaching for", "fits in my head". V notes NEvnucovat.
- *(Jen články, v notes 0 %)* Anti-textbook framing: "The textbook answer is X. Here's what I do instead."
- Žádné přechodové věty mezi sekcemi. Nikdy se nestaví nad čtenáře — fellow-learner framing.

**Danielův podpis v notes (audit 88 ručních notes, 2026-09-08 — korektura ani review to NESMÍ vyhladit):**
- **Otázka na čtenáře jako CLOSER**, ne hook: "Has AI made you feel more free in your work as well?", "Do you build too much too?" (12,5 % notes, 5 z 10 nejlepších). Detektor rétorických otázek ji nepočítá.
- **Otevřená nejistota**: "I think", "I guess", "I'm not completely sure yet", "I'm still figuring out" (~15 % notes). Není to hedging-tell, je to podpis; nepřepisovat na jistotu.
- **Ledger note**: řádky `Label: číslo` bez komentáře, plochý konec ("Saturday: 4 new subscribers / Sunday: 0 / Monday: 2 unsubscribed"). 3 z 10 nejlepších notes.
- **Život mimo workshop** (~25 % notes: dcera, terapie, stehy, gril, workoholismus) — nejlepší note měsíce (21 ❤) byla "I'm slowing down." Persona není jen tech-writer.
- **Plochý konec** — 72 % notes končí obyčejnou větou ("But it's still usable.", "I think it is average."). Puenta ≈ 6 %. V notes NEdopisovat pointu.

❌ **Anti-patterns (banned):**
- "We"/"let's"/"you should" jako default (Daniel mluví za sebe).
- Floral metafory ("dance of code", "symphony of design").
- "Imagine if…" / "What if I told you…".
- Motivational closing ("you can do it too", "go forth and build").
- Tutorial mode ("Step 1: do X. Step 2: do Y.").
- Padding ("It's important to note", "It's worth mentioning").

---

## 1. AI-fráze detektor — vypiš a odstraň KAŽDÝ výskyt

Watchlist:
- "leverage", "synergy", "ecosystem", "transformative", "game-changer", "revolutionize", "groundbreaking"
- "delve into", "dive deep", "unpack", "in today's fast-paced world", "in the digital age"
- "it's worth noting that", "it's important to note that"
- "insidious" (Daniel-specific red flag)
- Dramatické metafory jako vata ("tried to take off", "space heater", "fork bomb" jako metafora)
- Literární slovesa: "wedges", "obliterates", "devours", "lurks"
- Over-polished similes, fake suspense ("It worked beautifully. For about a week.")
- Redundantní emphasis (bold + krátký odstavec + dramatická věta najednou)

## 2. Causal Pivot Detector

Rétorická AI-tell figura. Počítej VŠECHNY formy dohromady:
- "not just X — it's Y" / "it isn't X — it's Y" / "není to X, je to Y"
- "less about X; more about Y" / "you're not buying X, you're investing in Y"
- Negace + redefinice přes dvě věty: "X is not Y. It is Z."
- "Not because X, but because Y"
- Reframe: "Those numbers aren't the interesting part. The interesting part is…"
- Antithesis pár: "The first is static. The second is behavior."

Thresholds: ✅ 0–1 · ⚠️ 2 · ❌ 3+ = rewrite. Každý pivot přepiš do přímého tvrzení.

## 3. Triplet Fatigue Check

Rule-of-three — AI rhythmic tell. Počítej KDEKOLI vč. anaforických. **U notes počítej JEN anaforické/rytmické triplety** ("Zero X. Zero Y. Zero Z.") — přirozený výčet tří položek ("gaming, Netflix, and Eminem") se nepočítá:
- Výčet: "a loop, a hot fan, a drained wallet"
- Anaforický triplet: "Zero clicks. Zero copy-paste. Zero chance."
- Trojice sloves: "loop, cook, or bill"

Thresholds: ✅ 0–1 · ⚠️ 2 · ❌ 3+ = rewrite. Rozbij do prózy s jiným rytmem (dvojice, čtyřka, embedded list).

## 4. Bridge Check (cognitive teleporting)

- Industry shorthand bez inline definice ("priced in", "structural shift", "second-order effects") kde audience není garantovaně senior.
- Authoritative conclusion bez "proto" / "what this means is" mostu.
- Consultant-speak akumulace (3+ buzzwords v odstavci).
→ Definuj term inline / přidej bridging větu / nahraď konkrétním příkladem.

## 5. Cadence & Punchline Budget

Uniformní punchiness je sama AI-tell — lidský text má i ploché pasáže.
- **Punchline budget**: ✅ ≤30 % sekcí končí quotable aforismem, ⚠️ 30–50 %, ❌ >50 %. **Notes: ≤15 %** (reálně 6 %).
- **Jednověté dramatické odstavce/věty**: ✅ ≤4, ⚠️ 5–6, ❌ 7+. **Pro notes N/A** — jednověté odstavce jsou nativní formát Notes.
- **Em-dash budget** (jen psaný text): ✅ ≤5 /1000 slov, ⚠️ 5–8, ❌ >8.
- **Plochá pasáž povinná**: aspoň 2 souvislé úseky čistého vysvětlování bez boldu/punchline/metafory.
- **Manufactured specificity**: vymyšlené přesné časy ("at 9:47 PM on a Tuesday", "rebooted at 4:23 one night in July") = ❌, v článcích i notes. Vágní opener ("One evening", "Today,") = ✅. Reálný log timestamp je povolený jen když nese informaci, kterou text dál používá.

## 6. Fix-my-EN korektura (notes) — co korektura NESMÍ přidat

Audit 2026-09-08: ručně psané notes mají 15 % viditelných typo, ale korigované mají uniformní stopu, která je prozradí. Při opravě angličtiny:
- **Žádná Oxford comma** ("gaming, Netflix and Eminem", ne "gaming, Netflix, and Eminem") — 12/12 výčtů ji mělo, čeština ji nemá.
- **Žádné "So, " / "That's why " jako opener věty s čárkou.**
- **Žádná čárka po úvodním adverbiálu** ("Today I got 3…", ne "Today, I got 3…").
- **Nezavádět ", which" vedlejší věty** — rozděl na dvě věty.
- **Rovné apostrofy** (`'`), ne typografické (`’`) — smíšené apostrofy v jedné note = vložený AI výstup vedle ručního textu.
- **Nevyhlazovat** "I think / I guess / not sure yet" ani otázku-closer (viz podpis výše).
- Opravuj gramatiku a pravopis; nepřepisuj rytmus, nepřidávej pointu, nedělej z 8 krátkých odstavců 3 dlouhé.

## 7. Humanity linter (deterministický gate)

Po finálním draftu spusť:
```
python3 ~/foundary-tools/skills/humanity-linter/humanity_linter.py <soubor>
```
Exit 0 = PASS · 1 = WARN (vypiš metriky) · 2 = FAIL → jedna cílená iterace na failed metriky (pivot_count, triplet_count, em_dash, punchline_section_ratio), re-run. 2× FAIL → flag Danielovi.

---

## Použití (pro odkazující skilly)

Při review/generování textu nebo VO: projeď sekce 1–5 per odstavec/segment, odstraň nálezy, aplikuj voice fingerprint, u notes navíc sekci 6 (Fix-my-EN), pak gate sekcí 7 (u psaného textu). Reportuj nálezy stručně (fráze + lokace + náhrada), neopisuj celý text.
