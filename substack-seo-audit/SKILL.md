---
name: substack-seo-audit
description: Auditne SEO meta všech publikovaných Substack postů (danielrusnok i readsinmotion) přes veřejné archive API — najde chybějící/špatné search_engine_title, search_engine_description, social_title, tagy a thin content — pak vygeneruje konkrétní návrhy v Danielově voice a po schválení je zapíše přes substack-mcp set_post_meta. Použij kdykoli Daniel řekne "seo audit", "meta audit", "zkontroluj seo na substacku", "chybí mi meta description", "projdi seo postů", "oprav seo title", "substack seo", "geo audit", "jak jsem na tom se seo". Aktivuj se i jako součást týdenní SEO rutiny nebo když Daniel řeší, proč posty nerankují v Google.
---

# Substack SEO meta audit

Substack ti dá kontrolu nad čtyřmi věcmi: `search_engine_title`, `search_engine_description`,
`social_title`, `slug`. Zbytek (sitemap, canonical, schema) drží Substack. Tenhle skill řeší
právě ty čtyři + tagy a thin content.

Když `search_engine_title` / `search_engine_description` chybí, Google si snippet postaví
z `title` + `subtitle`. To funguje, ale ztrácíš keyword targeting — a hlavně u titulků,
které jsou napsané jako hook (číslo + zvědavost), ne jako dotaz, který někdo googlí.

## Krok 1 — audit

Script `audit.py` leží vedle tohoto SKILL.md. V cloud routine (kde lokální kopie není)
si ho stáhni z hubu:

```bash
S=audit.py; [ -f "$S" ] || curl -sfO https://raw.githubusercontent.com/DannyRusnok/dcw-cloud-skills/main/substack-seo-audit/audit.py
python3 "$S" danielrusnok
python3 "$S" readsinmotion
```

Script tahá veřejné `/api/v1/archive` (žádná auth), vypíše posty s problémy a uloží
raw JSON do `/tmp/seo-audit-<account>.json`.

Kontrolované dimenze:

| Issue | Práh | Proč |
|---|---|---|
| `no-seo-title` | prázdné | Google padá na `title`, který je hook, ne query |
| `seo-title-long` | >60 znaků | usekne se v SERPu |
| `no-seo-desc` | prázdné | žádná kontrola nad snippetem |
| `seo-desc-short` | <70 znaků | Google ji zahodí a vygeneruje vlastní |
| `seo-desc-long` | >165 znaků | usekne se v půlce věty |
| `no-social-title` | prázdné | OG title = `title`, na X/LinkedInu často nesedí |
| `no-tags` | 0 tagů | mizí ze Substack topic feedů |
| `thin` | <400 slov | nemá šanci rankovat, přeskoč SEO fix |

## Krok 2 — návrhy

Pro každý post s `no-seo-title` / `no-seo-desc` (a NE `thin`) vygeneruj návrh.

**SEO title (50–60 znaků):**
- Píše se jako fráze, kterou někdo napíše do Googlu — ne jako hook.
- Původní titulek `53 Reels Rendered. 9 Published. So I Flipped the Order.`
  → SEO title `Why I Stopped Batch-Rendering AI Reels (Workflow Fix)`
- Drž jeden konkrétní nástroj/koncept v titulku (`ComfyUI`, `Wan 2.2`, `Substack API`,
  `faceless channel`, `Claude Code`) — to je to, co lidi hledají.
- Žádné dvojtečkové "X: Y" konstrukce, pokud pravá strana nenese keyword.

**SEO description (120–155 znaků):**
- První věta = odpověď, ne teaser. Musí dávat smysl vytržená z kontextu.
- Obsahuje čísla, pokud v postu jsou (`41,799 views`, `€0`, `26x`) — CTR driver i GEO signál.
- Končí konkrétním výstupem, ne otázkou.
- Špatně: `A story about what happened when I tried automating my channel.`
- Dobře: `33 days of automated faceless video: 41,799 views, €0 revenue, and the three
  pipeline decisions that caused both.`

**GEO poznámka:** SEO description je zároveň to, co LLM (ChatGPT, Perplexity, AI Overviews)
nejčastěji zvedne jako citaci. Proto ta první věta musí být samostatně pravdivé tvrzení
s konkrétním číslem nebo definicí — ne narativní hook. To je jediné místo, kde SEO a GEO
píšeš stejným tahem.

**Social title:** nastav jen když se liší od `title` (typicky když je `title` >60 znaků
nebo se opírá o kontext, který v timeline chybí). Jinak nech prázdné.

## Krok 3 — review table

Výstup vždy jako tabulka, ne prózou:

| id | current title | → SEO title | → SEO description | znaků |
|---|---|---|---|---|

Daniel schvaluje po řádcích ("všechny", "1,3,5", "kromě 4"). **Bez explicitního schválení nezapisuj.**

## Krok 4 — zápis

```
mcp__substack-mcp__set_post_meta(postId=<id>, seoTitle="…", seoDescription="…")
```

`account` param vynech pro danielrusnok, `'readsinmotion'` pro RiM.

Poznámky:
- `set_post_meta` míří na draft entity; publikovaný post je stále draft s `is_published=true`,
  takže zápis prochází. **Ověř první post samostatně** a znovu stáhni archive API, jestli se
  hodnota propsala, než pustíš batch.
- Nikdy neměň `slug` u publikovaného postu — rozbiješ existující odkazy a Substack
  neredirectuje.
- Po batchi spusť audit znovu a nahlas diff.

## Krok 5 — tagy

Posty s `no-tags`: navrhni 2–4 tagy z existující sady (`list_substack_tags` v article-forge MCP),
nezakládej nové. Tagy se zapisují v Substack editoru, ne přes `set_post_meta` — vypiš je
Danielovi jako seznam k ručnímu doplnění.

## Co tenhle skill NEŘEŠÍ

- Search Console data (pozice, impressions, CTR) — na to je samostatná GSC rutina.
- Obsah postu, H2 strukturu, interní prolinkování.
- Thin content posty — u nich je fix napsat víc, ne přepsat meta.
