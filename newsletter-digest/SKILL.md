---
name: newsletter-digest
description: |
  Denní cloud routina — projde nové (unread) Substack newslettery v Danielově Gmailu, shrne každý, ohodnotí relevanci 1–5 vůči jeho projektům (content/Substack growth, AI/agents/Claude/MCP, SaaS = Drippery + Article Forge, solo-builder/indie, gamedev Eli&Uri), vyrobí denní Notion digest page a pošle Telegram ping s odkazem na tu page. Drží jen score ≥3, zbytek shrne do "Dropped" řádku. Navíc z high-signal (score 4–5) newsletterů vygeneruje strukturované návrhy úprav konkrétních foundary toolů a zapíše je do Notion "Foundary Tool Backlog" DB (status Proposed) — sister-routine `foundary-tool-pr` je pak po Danielově schválení implementuje + otevře PR. Po zpracování označí maily jako přečtené (dedup pro příští běh). Použij když Daniel řekne: "projdi newslettery", "udělej digest", "shrň substack newslettery", "newsletter digest", "co přišlo za newslettery", "run newsletter digest". Primárně běží jako scheduled cloud routine 6:00 CET.
---

# newsletter-digest

Denní souhrn odebíraných Substack newsletterů + relevance scoring vůči Danielovým projektům. Output = Notion page + Telegram ping. Navazuje na dřívější `📰 Substack Digest` series (parent page `34d3f179-067e-81f5-bc04-f5a40d5aae6b`) — drž **identický formát**.

## Konfigurace (předává routine prompt / env)

- `NOTIFY_KEY` — klíč pro subhook Telegram relay. **NENÍ v tomto skillu** (public repo) — routine prompt ho dodá. Pokud chybí, Telegram krok přeskoč a jen zaznamenej Notion URL do výstupu.
- Gmail label pro Substack newslettery: `Label_4290506968513556957`. Pokud by neseděl, `list_labels` → najdi label s názvem "Substack".
- Notion parent page (digesty): `34d3f179-067e-81f5-bc04-f5a40d5aae6b`.
- Notion connector v cloudu = **DCW-context-hub** (`notion_create_page` / `notion_search` / `notion_get_block_children`). NEPOUŽÍVEJ firemní/oficiální Notion konektor.

## Krok 1 — Načti kontext projektů (pro scoring)

Před scoringem si připomeň, na čem Daniel teď dělá, aby relevance nebyla od oka:
- `mem0_search` 2–3 dotazy: "current projects priorities", "drippery article-forge grownote", "AI agents claude mcp learnings".
- Profil je v `me.md` (auto-loaded): priority = **(1) content/Substack growth → (2) SaaS (Drippery MRR, Article Forge) → (3) games (Eli&Uri)**. Solo builder, večerní okna, build-in-public, Claude/MCP heavy stack.

## Krok 2 — Vytáhni nové newslettery

`search_threads` query: `label:Substack newer_than:1d` (pageSize 50). **Pozn.:** tento Gmail MCP `label:` operator bere **název** labelu, ne ID (`label:Label_4290...` vrací `{}`). Fallback když label query selže: `from:substack.com newer_than:1d` (mine custom-domain newslettery, ale pokryje 95 %).

**Dedup (Gmail konektor je READ-ONLY — nelze spoléhat na mark-read):**
- Primární okno = `newer_than:1d` (routina běží denně 6:00, takže 24h okno = 1 den newsletterů).
- **Cross-check proti včerejší digest page:** najdi předchozí `📰 Substack Digest` page (notion_search "Substack Digest", seřaď podle data), vytáhni všechny `Read` URL z ní, a v dnešním běhu **přeskoč jakýkoli newsletter, jehož canonical URL už tam je** (chrání před boundary duplikáty na hraně 24h okna).
- Pokud Daniel reconnectne Gmail s write scope, krok 6 (mark-read) pak dedup zpřesní — ale skill funguje i bez toho.

**Extrakce těla (DŮLEŽITÉ — emaily jsou 80–330K HTML, netahej je do kontextu):**
- `get_thread` s `FULL_CONTENT` přeteče limit a uloží se do souboru. Z toho souboru ber pole **`plaintextBody`** (camelCase, ne `plaintext_body`).
- Canonical post URL = řádek na začátku `plaintextBody`: `View this post on the web at <URL>`. Z něj vezmi URL, ten řádek strip.
- Vyhoď `[ https://substack.com/redirect/... ]` tracking linky. Python regex, ne bash. Vezmi prvních ~1000–1400 znaků pro summary.

**Hned vyřaď jako system/noise (nedávej do scoringu, jdou do "Dropped" countu):**
- `no-reply@substack.com` — verification codes, "Shareable assets for…", "Your … stats in review".
- `danielrusnok@substack.com` / `on@substack.com` / `on+product@substack.com` — vlastní posty + Substack product announcementy (pokud nejde o feature přímo relevantní k jeho workflow — pak score normálně).
- Cokoli bez čitelného newsletter obsahu.

## Krok 3 — Shrň + oskóruj každý newsletter (1–5)

Pro každý reálný newsletter napiš **2–4 věty EN summary** — ne generický abstract, ale **co z toho plyne pro Daniela / jeho projekty** (jako v prior digestech: "aligns with Daniel's daily Notes pipeline", "relevant signal for the context-layer thesis"). Vždy ulož `Read` URL (canonical post link z těla, ne tracking link když to jde).

**Scoring rubrika (relevance k Danielovým projektům, ne kvalita článku):**
- **5** — přímo actionable pro běžící projekt teď: konkrétní taktika pro Substack growth/Notes konverzi, Claude/MCP/agent technika použitelná v jeho toolingu, email/drip insight pro Drippery, content-pipeline nebo monetizace pro solo buildera.
- **4** — silně relevantní, ne okamžitě actionable: trend/signál v AI agents, Substack algoritmu, indie SaaS, který ovlivní rozhodnutí.
- **3** — tematicky blízko (writing craft, build-in-public, gamedev narrative), užitečný úhel pro vlastní obsah.
- **≤2** — generické, promo-heavy, mimo jeho domény. → **Dropped**, nepiš plný summary.

Buď přísný — radši míň keepů s vysokým signálem.

## Krok 3.5 — Vygeneruj návrhy úprav foundary toolů (jen z score 4–5)

Pro newslettery se **score 4 nebo 5**, které nesou **konkrétní, přenositelnou techniku** (ne obecný trend), zvaž jestli z toho plyne **konkrétní úprava nějakého foundary toolu**. Buď velmi přísný: většina dnů = 0–2 návrhy, klidně 0. Radši žádný než vatový.

**Mapa foundary toolů → repo (`DannyRusnok/<repo>`):** `drippery` (email drip SaaS), `framelock`, `article-forge` (content pipeline), `archieve-concierge`, `grownote` + `grownote-mcp` (Substack notes engine), `substack-mcp`, `subhook` (email→API orchestrator), `drippery-mcp`, `dcw-context-hub` / `dcw-context-hub-mcp`, `craft-os`, `umami-mcp`, `pc-mcp`, `finance-manager`, `dph-asistent`, `reel-pipeline-kit`. Pokud insight nesedí na žádný konkrétní tool, návrh **nedělej**.

**Kvalifikační gate (návrh dělej JEN když platí vše):**
- Insight je actionable a **mapuje na jeden konkrétní repo** z mapy výše.
- Změna je věrohodně malá a lokalizovaná (prompt/copy/config/heuristika/jeden util), ne "přepiš architekturu".
- Nejde o duplicitu — pokud podobný řádek už v backlogu je (viz krok 3.6 lookup), přeskoč.

**Pro každý kvalifikovaný návrh vyrob strukturovaný objekt:**
- `title` — imperativ, < 80 znaků (např. "Add unsubscribe-reason capture to Drippery drip exit").
- `repo` — přesný slug z mapy.
- `insight` — 1 věta: co newsletter říká a proč to platí pro Daniela.
- `change` — 2–4 věty: **co/kde/proč** změnit (soubor/oblast pokud tušíš, jinak chování). Konkrétně, ať to umí sister-routine zaimplementovat bez dohadování.
- `effort` — `S` / `M` / `L`. (Auto-PR bere jen `S`.)
- `confidence` — `high` / `med` / `low`.
- `auto_safe` — `true` jen pokud `effort=S` a změna je single-file low-risk (copy, prompt text, konstanta, heuristika), kterou jde otevřít jako draft PR bez review rizika. Jinak `false`.
- `source_url` — canonical URL toho newsletteru.

## Krok 3.6 — Zapiš návrhy do Foundary Tool Backlog (Notion DB)

Návrhy z kroku 3.5 ulož do trvalé Notion DB (sister-routine `foundary-tool-pr` z ní čte).

1. **Najdi DB:** `notion_search` "Foundary Tool Backlog" (data_source/database). Pokud existuje, použij její id.
2. **Pokud neexistuje, vytvoř ji** přes `notion_create_database`, parent page `34d3f179-067e-81f5-bc04-f5a40d5aae6b` (stejná parent jako digest pages). Properties:
   - `Title` (title), `Repo` (select), `Status` (select: `Proposed` / `Approved` / `PR opened` / `Done` / `Rejected`), `Effort` (select S/M/L), `Confidence` (select high/med/low), `Auto-safe` (checkbox), `Source` (url), `Insight` (rich_text), `Change` (rich_text), `PR` (url).
3. **Dedup:** než přidáš řádek, `notion_query_database` filtr `Title` ~ podobný / stejný `Source` + `Repo`. Pokud duplicita (jakýkoli status kromě `Rejected`), přeskoč.
4. Pro každý nový návrh vytvoř page v té DB, `Status = Proposed`. `Auto-safe` checkbox dle `auto_safe`.

Pokud Notion DB krok selže, **nesmí to shodit digest** — zaznamenej do výstupu "backlog write skipped" a pokračuj krokem 4.

## Krok 4 — Postav Notion digest page

`notion_create_page`, parent `{ "type": "page_id", "page_id": "34d3f179-067e-81f5-bc04-f5a40d5aae6b" }`, icon emoji `📰`, title `📰 Substack Digest — YYYY-MM-DD` (dnešní datum CET).

Children bloky (přesně tento tvar — match prior art):
1. `paragraph` bold: `"{scanned} scanned · {kept} kept (≥3)"` (scanned = všechny reálné newslettery vč. dropped, kept = score ≥3).
2. `divider`.
3. Pro score 5,4,3 (sestupně, jen neprázdné): `heading_2` text `"Score N"`, pak per item `bulleted_list_item` rich_text:
   - sender display name **bold**
   - `" — "` plain
   - title *italic*
   - `" — "` + summary plain
   - `"Read"` s `link.url` = post URL
4. `divider`.
5. **Jen pokud krok 3.5 vyrobil ≥1 návrh:** `heading_2` text `"🔧 Tool improvement ideas"`, pak per návrh `bulleted_list_item` rich_text:
   - `repo` **bold** + `" — "` + `title` plain
   - nový řádek (nebo `" · "`): `change` plain
   - `" ["` + `effort`/`confidence` + `auto_safe ? ", auto-safe" : ""` + `"]"` plain
   - `"Source"` s `link.url` = `source_url`
   - Pod sekcí jeden `paragraph` italic: `"Schval v 'Foundary Tool Backlog' DB (Status → Approved); foundary-tool-pr pak otevře PR."`
6. `divider`.
7. `paragraph` italic: `"Dropped (score ≤2): {krátký výčet co a proč}, plus N Substack system notifications."`

## Krok 5 — Telegram ping

Pokud je `NOTIFY_KEY` k dispozici:
```
POST https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY
Content-Type: application/json
{ "title": "📰 Newsletter digest — YYYY-MM-DD", "text": "{kept} keepů z {scanned} newsletterů{, N tool ideas pokud >0}. Top: {1-2 nejvyšší score tituly}.\n{Notion page URL}" }
```
Drž text < 3900 znaků. Notion URL z odpovědi create_page (`url` field).

## Krok 6 — Mark as read (best-effort)

Pro každou zpracovanou message zkus odebrat UNREAD: `unlabel_message` messageId=<id> labelIds=["UNREAD"]. **Nedělej** dřív než po úspěšném vytvoření Notion page.
- **Pokud vrátí "connector requires additional permissions"** = Gmail je read-only → krok přeskoč, dedup zajišťuje time-window + cross-check z kroku 2. Nezpomaluj se opakováním, jen to jednou zaznamenej do výstupu.

## Krok 7 — mem0 (volitelně, jen silné signály)

Pokud score-5 newsletter obsahuje konkrétní actionable insight pro projekt (taktika, nástroj, číslo), `mem0_add` 1 větu s `metadata {project, category:"learning"}`. Nelogovat celý digest, jen ojedinělé high-value věci. Max 1–2 calls.

## Výstup do chatu (když běží manuálně)

Jednořádkové shrnutí: `{kept}/{scanned} keepů · Notion: <url> · Telegram: sent/skipped`. Žádný dlouhý dump — vše je v Notion page.

## Edge cases

- **0 nových newsletterů**: nevytvářej prázdnou page, pošli Telegram "Žádné nové newslettery dnes" jen pokud `NOTIFY_KEY` je, jinak skonči tiše.
- **Gmail/Notion connector chybí v cloudu**: zapiš to do výstupu a skonči — neměň stav (nemarkuj read).
- **Tracking linky**: Substack maily mají redirect URL; preferuj canonical `*.substack.com/p/...` z těla.
