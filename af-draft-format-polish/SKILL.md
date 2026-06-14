---
name: af-draft-format-polish
description: Lehký format+cleanup pass nad EXISTUJÍCÍM Article Forge draftem — převede tělo na čisté sémantické HTML a aplikuje lightweight cleanup (anti-AI fráze, mobile odstavce, anti-pivot, skim bold) v NEUTRÁLNÍM/brand voice. NENÍ to plná osobní-voice pipeline (na Danielovy osobní Substack eseje použij `substack-draft-review`). Použij pro automated / brand / utility drafty (Reads in Motion leaderboard, changelog, data digest, brand newsletter) když Daniel řekne "naformátuj draft", "vyčisti draft", "převeď na HTML", "format polish", "draft je neformátovaný", "uprav formátování draftu", "fix formatting", nebo když to zavolá routine (např. rim-top-reels-weekly) jako post-create krok. Bere `articleId` (+ volitelně brand/voice poznámku). Zachovává VŠECHNA reálná data, čísla, odkazy a pořadí — nic nevymýšlí ani nemaže. NEPUBLIKUJE.
---

# af-draft-format-polish

Cílený format + lightweight cleanup pass nad existujícím Article Forge draftem. Jedna iterace, ne 3kolová pipeline. Drží **neutrální/brand voice** — NEaplikuje Danielova osobní-esej voice pravidla (hook patterns, restack-bait, cover/avatar, cross-link na danielrusnok Substack, "I/my" framing).

## Kdy tento skill vs `substack-draft-review`
- **Tento skill**: automated / brand / utility drafty (Reads in Motion, changelog, data digest) → jen format→HTML + lehký cleanup.
- **`substack-draft-review`**: Danielovy osobní Substack eseje → plná 5-agent 3-kolová voice pipeline.

## Vstup
- `articleId` (UUID) — povinné.
- volitelně: brand/voice poznámka (např. "Reads in Motion, 3rd-person curation voice"). Default = neutrální informativní voice, drž ten, co už v draftu je.

## Tooling
Article Forge MCP tools jsou deferred — načti přes ToolSearch:
`ToolSearch query="select:mcp__eb89b7e1-c220-4a17-aaba-c461f4eb91f9__get_article,mcp__eb89b7e1-c220-4a17-aaba-c461f4eb91f9__update_article"`

## Postup

1. `get_article(articleId)` → přečti title, subtitle, content. Zjisti jestli je content markdown (`## `, `**`, `[t](u)`, `- ` / `> ` na začátku řádku) nebo už HTML.

2. **Převod na čisté sémantické HTML** (HARD RULE: `update_article` ukládá verbatim a NEKONVERTUJE — musíš poslat HTML, ne markdown):
   - odstavce → `<p>…</p>`
   - sekce → `<h2>…</h2>`, podsekce → `<h3>…</h3>`
   - klíčová čísla / claim věty → `<strong>…</strong>` (cca 1 bold na odstavec, pro skim-readery; ne over-bold)
   - odkazy → `<a href="url">text</a>` (inline, kontextuální)
   - seznamy → `<ul><li>…</li></ul>`
   - oddělovač → `<hr />`
   - zvýrazněná/citovaná pointa → `<em>…</em>`
   - v outputu NESMÍ zůstat `##`, `**`, `[text](url)`.

3. **Lightweight cleanup** (zachovej VŠECHNA reálná data, čísla, odkazy a pořadí — nic nevymýšlej, nic nemaž):
   - **Anti-AI fráze** → odstraň: "delve", "leverage", "dive deep", "unpack", "in today's…", "it's worth noting / important to note", "transformative / game-changer / revolutionize", over-polished similes, fake suspense ("It worked. For about a week.").
   - **Causal pivot** ("not just X — it's Y" / "isn't about A, it's about B" / "X is not Y. It is Z.") → přepiš na přímé tvrzení.
   - **Triplet fatigue** (3+ rule-of-three konstrukcí) → rozbij na jiný rytmus.
   - **Mobile**: odstavce max 2–3 věty; věty pod ~25 slov; 4+ čárkové kaskády rozbít.
   - **Em-dash budget**: ≤5 na 1000 slov; přebytek → čárka / závorka / nová věta.
   - **Neutrální/brand voice**: žádné "I/my" personal framing, žádný restack-bait, žádné motivational closing, žádný cover/avatar, žádná injekce cross-linků na cizí posty. Drž voice konzistentní s tím, co v draftu je.

4. `update_article(articleId, content=<HTML>)` (+ `subtitle` pokud ho lehce vylepšíš; title/subtitle vždy do dedicated polí). Platform neměň.

5. **Verify**: znovu `get_article(articleId)` → `content` musí obsahovat `<p>` a `<h2>` a NEsmí začínat `##`/`**`. Pokud markdown prosákl verbatim → oprav payload a `update_article` jednou zopakuj.

6. Vrať stručný report: co se změnilo (formát, počet odstraněných AI frází / pivotů / tripletů), potvrzení že HTML landed, a prvních ~150 znaků finálního HTML jako důkaz.

## Guardrails
- NEPUBLIKUJ (jen draft).
- NEMĚŇ význam, NEPŘIDÁVEJ ani NEMAŽ data/čísla/odkazy.
- NEAPLIKUJ Danielova osobní-esej voice pravidla — tohle je brand/utility post.
- Jedna format+cleanup iterace, ne multi-round critique.
