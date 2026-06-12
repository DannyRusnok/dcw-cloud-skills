---
name: weekly-ceo-report
description: Týdenní "CEO report" pro Daniela — cloud routina (NE 08:00 CET) která stáhne čísla ze všech projektů (Article Forge insights, Substack aggregates, Drippery subscribers), vyhodnotí týden proti cílům (Medium $400–1200/m, Substack 700 free subs, Drippery $300–1000 MRR), a pošle na Telegram krátký CZ report: co vydělalo, co umřelo, kam dát příští týden večerní okna. Použij když Daniel řekne "ceo report", "týdenní report", "jak šel týden", "weekly review čísel", "sunday report", nebo když běží jako scheduled cloud routine.
---

# weekly-ceo-report

Jeden report, neděle ráno, max ~30 řádků. Cíl: Daniel v posteli za 2 minuty ví,
co minulý týden reálně udělal s čísly a kam dát večerní okna v tom dalším.
Tone: konkrétně, bez chvály, bez bullet-smogu. Připouštěj nejistotu u sparse dat.

## Data pull (parallel, vše read-only)

1. **Article Forge MCP** — `get_content_insights({days:7, format:"json"})`
   + `get_content_insights({days:28, format:"json"})` (kontext trendu).
   Pokud tool není dostupný, fallback `get_daily_analytics` za posledních 7 dní.
2. **Substack (grownote MCP)** — `get_aggregates()` → sub count, 7d/30d delta;
   `get_note_stats()` / `list_recent_notes({limit:20})` → top note týdne (pokud dostupné).
3. **Drippery MCP** — `list_sequences({environment:"prod"})` → subscriber_count
   per série, součet + delta vs minulý report (minulé číslo z mem0, viz krok Persist).
4. **mem0** — `mem0_search({query:"decision discovery learning <aktuální měsíc>"})`
   → 2–3 klíčové decisions/discoveries týdne; `mem0_search({query:"weekly ceo report numbers"})`
   → minulé snapshot číslo pro delty.
5. **dcw-context-hub** — `get_recent_sessions` → co se reálně dělalo (volitelné, max 5 sessions).

Když kterýkoli zdroj selže: sekci vynech s poznámkou "(zdroj nedostupný)", neblokuj report.

## Report format (CZ, Telegram-friendly, žádný markdown header smog)

```
📊 CEO report — týden <od>–<do>

TL;DR: <2–3 věty: nejdůležitější pohyb týdne + jedno doporučení>

MEDIUM (7d): <views> views (<±%> vs prev | trend n/a pokud sparse), $<earnings>
  top: <title> (<views>)
  rising: <title> / žádný
  died: <title> / žádný

SUBSTACK: <subs> subs (<+7d> týden, <+30d> měsíc) — cíl 700: <pct>%
  top note: <prvních 50 znaků> (<likes/restacks>)

DRIPPERY: <total> subscribers napříč <N> sériemi (<+delta> týden)

CO FUNGOVALO: <1–2 řádky z insights recommendations — jen actionable>
CO UMŘELO: <1 řádek, nebo "nic výrazného">

PŘÍŠTÍ TÝDEN (večerní okna, priorita content > SaaS > hry):
1. <konkrétní akce vázaná na data — např. follow-up na rising článek>
2. <akce>
3. <akce>

CÍLE: Medium $<run-rate>/m (cíl 400–1200) · Substack <subs>/700 · Drippery MRR $<X> (cíl 300–1000)
```

Pravidla:
- Doporučení MUSÍ vycházet z dat v reportu (rising článek → follow-up; evergreen
  winner → repost/série; klesající views → publish cadence), ne z obecných rad.
- Když data nestačí na závěr, napiš to ("substack daily data nemám, jen totals").
- Run-rate = earnings 7d × 4.33. U sparse coverage označ "~odhad".

## Persist + delivery

1. `mem0_add`: "Weekly CEO report <datum>: Medium <views>/7d $<earn>, Substack <subs>,
   Drippery <subs> subscribers. Top: <title>. Doporučení: <1 věta>."
   `{project:"secondbrain", category:"fact"}` — slouží jako baseline pro delty příště.
2. Pošli report přes grownote MCP `send_telegram_message({text:<report>})`.
3. Pokud Telegram selže a routine má `NOTIFY_KEY`: fallback
   `curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -d "<report>"`.
   Bez NOTIFY_KEY: vrať report jako text output (Daniel ho uvidí v session logu).

## Guardrails
- Read-only všude (žádné schedule_note, žádné create_series, žádné update_article).
- Žádné výmysly čísel — co není v tool response, to v reportu není.
- Max 1 mem0_add (snapshot), žádný spam.
