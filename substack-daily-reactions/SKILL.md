---
name: substack-daily-reactions
description: Denní reakční rutina na Substacku — ráno vybere 3–5 postů a 10–20 notes od Substack creatorů z reaction poolu (+ 3 discovery), ke každé položce dá CZ překlad, úhel, otázku a příklad; Daniel ve STEJNÉ session odpoví vlastními komentáři a rutina je naplánuje rozložené přes den. Cíl = noví subs (komentář vidí čtenáři cílového autora → návštěva profilu). Použij když běží cloud routine "Substack daily reactions", nebo když Daniel řekne "reakce na dnes", "reakční rutina", "koho dnes komentovat", "naplánuj moje komentáře".
---

# Substack Daily Reactions

Cloud routine (claude.ai, 1×/den ráno). Žádný Telegram, schvalování probíhá odpovědí
v této session (Claude app na mobilu). Vše přes konektor **substack-mcp**.

## Proč takhle (neměnit bez Danielova OK)

- **Cíl je získat nové subs.** Ty nepřicházejí od autora, ale od jeho čtenářů, kteří uvidí
  Danielův komentář a kliknou na profil. Výběr proto řadí podle **viditelnosti**
  (engagement + čerstvost + velikost publika). Kdo je autor, je až druhotné.
- **Publikum = Substack creators s libovolným tématem**, kteří Substack a další sítě
  používají k šíření vlastní tvorby. NE autoři, kteří píšou o Substack growth.
- **Vlastní subs se nekomentují**, protože nepřinesou nové subs. Pool je odmítá už při přidání.
- **Rotace:** stejný autor z poolu max 1× za 7 dní. Výjimkou je **core** (~10 lidí,
  cooldown 2 dny), kde jde o vztahy, doporučení a restacky.
- **Komentáře píše Daniel.** Claude dává překlad, úhel, otázku a příklad a pak Danielův text
  převede do jednoduché angličtiny. Nikdy nepublikuj text, který Daniel neschválil.

## Režim A — ranní běh (scheduled)

### A1. Stav poolu
`reaction_pool` `{action:"list"}` (volej ho samostatně, ne paralelně s A2). Zapamatuj si `total`, `eligibleNow` a `lastWeek`.
Pokud `total < 60`, na konci výstupu přidej sekci **Rozšíření poolu** (viz A5).

### A2. Kandidáti
`get_reaction_candidates` `{notes:20, posts:5, discoveryNotes:6}`.
- Pokud se vrátí chyba auth nebo prázdné výsledky s podezřením na cookie, zkus
  `substack-cookie-heal` (helper skill ve stejném repu) a volání zopakuj 1×.
- Pokud je pool prázdný, pokračuj jen s discovery a Rozšířením poolu.

### A3. Filtr podle úsudku (vyřaď, nepiš o tom)
Vyřaď položky, ke kterým Daniel nemůže nic přidat:
- čistý promo nebo odkaz bez obsahu („check out my new post"), giveaway, sbírka linků;
- politika, konspirace, investiční tipy, krypto hype, medicínské rady;
- neanglický text;
- discovery autory, kteří zjevně nejsou creator s vlastní tvorbou (anonymní citátové účty
  a podobně). Z discovery nech **max 3** nejlepší.

Po filtru se drž cíle: 3–5 postů a 10–20 notes. Když jich je méně, nevadí, kvalita má přednost před počtem.

### A4. Příprava položek
U postů je celý čitelný text přímo v poli `text` kandidáta (server ho stáhl). `WebFetch` na
publikační domény NEPOUŽÍVEJ, protože cloud egress proxy je blokuje.

Každá položka má ID `P1…`, `N1…` nebo `D1…` (post / note / discovery) a tento formát:

```
**N3 · @handle** (12k followers · core | pool | discovery) · před 5 h · ❤ 84 · 💬 12
<URL>
🇨🇿 Překlad: <celý note přeložený do češtiny; u postu shrnutí ve 3–4 větách + hlavní teze>
🎯 Úhel: <1 věta česky — kde může Daniel přidat vlastní zkušenost (build in public, automatizace,
   tvorba, distribuce, táta + side projekty, AI v praxi). Když se to nehodí, reaguj přímo na
   téma autora.>
❓ Otázka: <1 otázka česky, která Danielovi pomůže najít vlastní myšlenku>
✏️ Příklad: <1–3 krátké věty v jednoduché angličtině jako inspirace, NE hotový koment>
```

Pravidla pro příklad: jednoduchá angličtina, krátké věty, žádné metafory a žargon, žádné
„Great post!", žádné odkazy, žádná zmínka o Danielových nástrojích ani produktech. Nesmí
obsahovat fakta o Danielovi, která neznáš. Když potřebuješ jeho zkušenost, napiš
`[tvoje zkušenost]`.

Pořadí: nejdřív posty, pak notes podle `score`, na konec discovery.

### A5. Rozšíření poolu (jen když total < 60, nebo v neděli)
`discover_reaction_pool` `{source:"subscriptions", sample:25}`, a až **po jeho dokončení**
`{source:"explore", sample:30}`. NIKDY je nevolej paralelně: Substack pak vrací 429 a
výsledek je prázdný. Když obě volání vrátí 0 kandidátů, napiš jednu větu „discovery dnes
nic nenašla (pravděpodobně rate limit)" a pokračuj.
Proveď stejný filtr jako v A3 a ukaž max 15 kandidátů jako `C1…`, každého na jeden řádek:
`C4 · @handle · 8k followers · <publikace> · <proč sedí, 6–10 slov česky>`.

### A6. Závěr výstupu
Na konci napiš návod k odpovědi. Musí se vejít na obrazovku telefonu:

```
Odpověz třeba:
N1: <tvůj komentář — česky nebo anglicky>
P2 ok        ← použij příklad tak, jak je
N4 core      ← autor do core
vyhoď @handle
přidej C1,C3
Zbytek přeskočím.
```

Režim A NIC nepublikuje ani neplánuje.

## Režim B — Daniel odpověděl v této session

1. Rozparsuj odpověď. Položky, které nezmínil, přeskoč.
2. **Finální text komentáře:**
   - Pokud Daniel napsal česky, přelož do jednoduché angličtiny, zachovej jeho význam a nic nepřidávej.
   - Pokud napsal anglicky, oprav jen gramatiku a překlepy.
   - `ok` znamená použít příklad beze změny. Když obsahuje `[tvoje zkušenost]`, NEPOUŽÍVEJ ho a zeptej se.
   - Max ~1000 znaků, bez odkazů, pokud je Daniel výslovně nenapsal.
3. Naplánuj všechno **jedním** voláním `schedule_reactions`:
   `items:[{targetUrl, authorHandle, body, kind, discovery:true jen pro D*}]`. Pořadí zachovej podle
   Danielovy odpovědi. Nástroj sám rozloží komentáře po 25–55 min v okně 07–22 h (Praha).
4. `N4 core` → `reaction_pool {action:"set_role", handles:[…], role:"core"}`.
   `vyhoď @x` → `reaction_pool {action:"remove", handles:["x"]}`.
   `přidej C1,C3` → `reaction_pool {action:"add", handles:[…], source:"discovery"}`.
5. Odpověz stručně tabulkou `ID · čas (Praha) · finální EN text · actionId` a přidej řádek
   „Zrušit: napiš `zruš N3`". Zrušení = `delete_scheduled_item {id: actionId, actionType:"comment"}`,
   funguje jen před časem publikace.
6. Když `schedule_reactions` vrátí `skipped`, napiš proč, jednou větou na položku.

## Neděle — týdenní ohlédnutí (přidej k Režimu A)

- Z `reaction_pool list` → `lastWeek` napiš 2–3 věty: kolik reakcí, kolik z core a kolik discovery, kolik různých autorů.
- Spusť A5 vždy, i když pool už má 60 a víc autorů.
- Autory z poolu, kteří mají ≥4 reakce a nikdy nereagovali zpět, navrhni na vyhození. Zpětnou
  reakci ověříš přes `get_recent_replies`, pokud je to jednoduché. Jinak tento krok přeskoč.

## Nikdy

- Nepublikuj ani neplánuj nic, co Daniel v této session výslovně neschválil.
- Nekomentuj vlastní subs, vlastní účty (danielrusnok, readsinmotion) ani Danielovy zákazníky.
- Nepoužívej `find_fresh_engagement_note`. To je starý „komentuj všechny" flow.
- Neposílej nic na Telegram.
