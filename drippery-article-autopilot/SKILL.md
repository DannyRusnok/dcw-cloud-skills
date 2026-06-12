---
name: drippery-article-autopilot
description: Autopilot pro Drippery growth funnel — z publikovaného (nebo finálního draft) článku automaticky vyrobí tematicky matchující gated email sérii v Drippery (create_series → publish_sequence přes drippery MCP), a zapojí ji do článku jako mid-post + P.S. CTA podle pravidel z article-draft-review. Použij když Daniel řekne "autopilot na článek", "udělej gated sérii k článku", "drippery autopilot", "napoj článek na drippery", "vyrob funnel k článku", nebo automaticky jako krok v article-draft-review když žádná tematicky blízká série neexistuje. Skill NIKDY nesahá na subscribers ani email_queue — jen sequences/emails/embeds (create) a article content (update_article).
---

# drippery-article-autopilot

Cíl: **každý článek má gated sérii + subscribe funnel.** Místo jednoho default
lead magnetu (Memory Starter) dostane článek tematicky vlastní 5-email sérii,
nebo se napojí na existující blízkou.

## Inputs
- `articleId` (Article Forge UUID) nebo title — povinné
- `mode`: `auto` (default — vše bez ptaní) | `draft-only` (vytvoř sérii jako draft, nepublishuj, neměň článek)

## Workflow

### 1. Načti článek
`get_article(articleId)` z Article Forge MCP → title, content, tags, platform.

### 2. Match proti existujícím sériím (dedup gate)
`list_sequences({environment:"prod", status:"published"})` z Drippery MCP.
- Tematický match = série jejíž název/téma pokrývá hlavní téma článku (ne jen
  stejný obor). Příklad: článek o Claude Code memory → "Claude Code Memory
  Starter" = match. Článek o Wan video pipeline → Memory Starter ≠ match.
- **Match nalezen** → NOVOU sérii nevytvářej. Pokračuj krokem 5 s existující
  (embed id z `get_sequence`).
- Žádný match → krok 3.

### 3. Draft 5-email gated série
Sérii navrhni jako **rozšíření článku** (gated extension pattern z
`drippery-series-create`), ne jeho kopii:
- Email 1 (welcome, day 0): doruč slíbený "bigger picture" — frame tématu,
  co série pokryje, 1 okamžitě použitelný tip.
- Emaily 2–5 (day 1–4): každý jeden sub-topic do hloubky; konkrétní, praktické,
  Danielův first-person voice, EN (publikační default).
- Poslední email: soft CTA na Substack (danielrusnok.substack.com) + relevantní
  produkt (Drippery / Reel Pipeline Kit) pokud tematicky sedí.
- HTML omezené na: h1-h3, p, ul/ol/li, a, strong, em, u, hr, blockquote.
  Merge tags: `{{email}}`, `{{sequence_name}}`, `{{unsubscribe_url}}` (poslední
  email MUSÍ mít `{{unsubscribe_url}}`).
- **Subjects**: pro každý email vygeneruj subject A + subject B (jiný úhel,
  ne synonymum). Do `create_series` jde subject A. Varianty B ulož do mem0
  (`project:drippery, category:fact`, "A/B kandidáti pro sérii <název>") —
  nasadí se přes `subject_b` až Daniel schválí A/B deploy (feature
  `feature/ab-subject-lines`, čeká na migraci + deploy OK).

### 4. Vytvoř a publikuj
- `create_series({environment:"prod", name, emails, embed:{heading, description, buttonText}})`
  — embed copy piš k tématu článku (ne generické "Subscribe").
- `mode=draft-only` → STOP, vrať dashboardUrl, sérii nepublishuj.
- Jinak `publish_sequence(sequenceId)` → série je subscribable. (Publish
  neposílá nic existujícím subscriberům — bezpečné.)
- Embed id vezmi z `get_sequence(sequenceId)`.

### 5. Zapoj CTA do článku
Podle pravidel z `article-draft-review` (sekce CTA, změna 2026-06-11):
- **Medium**: mid-post CTA = samostatný `<p>` s holou URL
  `https://drippery.app/subscribe/<embed-id>` (extension ji převede na mixtape
  kartu) + end P.S. kombinovaný se Substackem (jeden italic odstavec).
- **Substack**: inline sidebar po hook paragraphu + P.S. (viz article-draft-review).
- Použij `update_article` / section-scoped edit; **HTML verbatim** (žádný
  markdown přes update_article).
- Pokud článek už CTA na jinou Drippery sérii má, nahraď ji jen pokud je nová
  série tematicky bližší; jinak nech být.

### 6. Záznam
`mem0_add`: "Článek <title> napojen na Drippery sérii <name> (sequenceId,
embed id, nová/reuse)." `{project:"drippery", category:"fact"}`

### 7. Output (1 zpráva)
```
<article title>
→ série: <name> (nová ✚ / reuse ↻), 5 emailů, published
→ subscribe: https://drippery.app/subscribe/<embed-id>
→ CTA: mid-post + P.S. vloženy (medium) / sidebar + P.S. (substack)
→ A/B subject kandidáti uloženy v mem0 (čekají na A/B deploy)
```

## Guardrails (hard)
- NIKDY insert do `drippery_email_queue`, NIKDY update/delete `drippery_subscribers` — viz prod SQL pravidla v drippery/CLAUDE.md.
- NIKDY nemazat/needitovat existující série a emaily (kromě vlastních draftů v téže session).
- Max 1 nová série na článek; když si nejsi jistý matchem, vytvoř novou (lepší specifická série než špatný reuse).
- Free tier limit 1 série se přes MCP obchází (direct DB) — Daniel je operátor vlastního produktu, OK.

## Sister skills
- `drippery-series-create` — interaktivní verze s 3-round review (pro ručně kurátorované série).
- `article-draft-review` — volá tento skill jako krok 6.6 (po cover image), když nenajde tematicky blízkou sérii.
