---
name: reel-kit-launch-pipeline
description: Standalone denní launch-marketing routina pro Reel Pipeline Kit (Gumroad, launch út 2026-07-07). Naplánuje 1 launch-marketing Substack Note/den přes substack-mcp, ODDĚLENĚ od běžného denního 3-notes pipelinu, s brandovaným obrázkem (stat_card s reálnými YouTube čísly nebo quote_card s větou). Fázuje obsah podle data (proof → teaser → ramp → launch week → post-launch) a drží se launch playbooku. Použij když Daniel řekne: "naplánuj launch notes", "reel kit launch routina", "spusť launch marketing", "launch note na dnes/zítra", "reel pipeline promo note", "marketing routina pro reel kit", nebo když to spustí cloud routine (scheduled task). NEPLÁNUJ Reddit. Cílová audience = writers/creators co publikují, NE build-in-public dav.
---

# Reel Pipeline Kit — Launch Marketing Pipeline

Standalone denní routina. Naplánuje **1 launch-marketing Note/den** do Substacku přes
`substack-mcp`, nezávisle na běžném 3-notes denním pipelinu. Každá note nese brandovaný
obrázek (`imageSpec`). Tento skill je self-contained — vše potřebné (fáze, archetypy,
non-negotiables, imageSpec šablony) je níže; není závislý na žádném lokálním souboru.

## Konstanty

- **LAUNCH_DATE = 2026-07-07** (úterý)
- **GREECE_WINDOW = 2026-06-22 … 2026-06-30** (autopilot — pre-schedule celou dávku předem)
- Produkt: $39 one-time / $29 early-bird, local-first, BYO-keys, Gumroad
- Lead hook: *"One HeyGen invoice ≈ Reel Pipeline Kit. Forever."*
- YouTube proof endpoint (tokenless read): `https://article-forge.fly.dev/api/analytics/youtube?persist=0&reelsOnly=1`
- **Běh routiny: 09:00 CET** (generace) → **publikace naplánovaná na 12:00 CET** téhož dne.
  Daniel má 9–12 okno na review/úpravu/komentář. 1 note/den.

## Non-negotiables (z playbooku + Danielových preferencí)

- **Reddit NIKDY.** Žádné r/* zmínky, žádné "post it on Reddit".
- **Audience = writers/creators co publikují** (jeho trh), NE build-in-public dav.
- **Proof = malá čísla chytře:** prodávej *výsledek kupujícího* (ušetřený čas) a fakt, že
  *vyrenderovaný reel SÁM je důkaz*. Reálná malá čísla (7 reelů, 355 views) jsou
  transparency beat, NE headline. Nepřeháněj social proof.
- **Jen reálná čísla** z proof fetche. NIKDY si nevymýšlej metriky.
- **Žádný link v těle note** (Substack penalizuje), žádné "check it out".
- Publikační jazyk: **angličtina** (default pro všechny outputy).
- Conversion-format gaty: 17–58 slov, first-person, hook NENÍ otázka, žádná imperativní tip-šablona.

## Krok 0 — Urči fázi podle dnešního data

| Fáze | Okno | Cíl | Archetyp | imageSpec |
|---|---|---|---|---|
| **proof-building** | do 2026-06-30 | budovat důvěru + zvedat reálná čísla | struggle-moment / behind-the-scenes | `stat_card` (YouTube čísla) ob den, jinak `quote_card` |
| **teaser** | 07-01 … 07-07 | "launching soon", behind-the-scenes | milestone / contrarian | `quote_card` (POV věta) |
| **ramp** | 07-08 … 07-13 | early-bird $29 awareness, objection handling | contrarian / value | `stat_card` (HeyGen $29/mo vs $39 once) |
| **launch-week** | 07-13 … 07-19 | konverze v 72h okně | milestone "it's live" (BEZ linku v těle) | `quote_card` nebo `stat_card` |
| **post-launch** | 07-20+ | buyer results, evergreen | behind-the-scenes / value | `quote_card` |

Pokud dnešek spadá do **GREECE_WINDOW**, nic živě neřeš — předpokládá se, že tyhle dny
byly **pre-scheduled předem**. Při běhu PŘED Řeckem (≤ 06-21) naplánuj rovnou celé
Greece okno dopředu (1 note/den, scheduledFor na 11:00 CET každého dne).

## Krok 1 — Pull proof dat

1. `curl -s "https://article-forge.fly.dev/api/analytics/youtube?persist=0&reelsOnly=1"` →
   vezmi `proof.totalViews`, `proof.videoCount`, `proof.avgViews`, `proof.topVideos[0]`.
   (Pokud fetch selže, použij jen Substack metriky a `quote_card`, ne `stat_card`.)
2. `list_recent_notes` (limit 20) + `get_aggregates` → co rezonovalo, ať neopakuješ stejný úhel.
3. `list_scheduled_items` → ať neplánuješ duplicitní launch note na stejný den.

## Krok 2 — Voice

Zavolej `get_voice_profile`. **Fallback:** pokud vrátí "unknown tool" / chybu, odvoď hlas
z posledních ~15 `list_recent_notes` (krátké deklarativní věty, čísla, first-person, bez fluff).
Drž Danielův hlas; engagement-grade jednoduchá angličtina.

## Krok 3 — Vyber archetyp (rotace)

Z tabulky fáze vyber archetyp. **Nikdy 2× za sebou stejný** — zkontroluj poslední 3
launch notes (`list_recent_notes` + `list_scheduled_items`, filtruj `angle` prefixem `launch:`).
Archetypy (plné znění v playbooku §5):
- **struggle-moment** — konkrétní scéna frustrace ("4 hodiny ruční captioning pro 38 views")
- **milestone / soft-sell** — "just shipped … here's the first reel it made" (žádný pitch/link)
- **contrarian POV** — anti-subscription ("expensive part was never the AI")
- **behind-the-scenes / vulnerability** — přiznej malá čísla, ukaž proč jsi tool postavil

## Krok 4 — Nadraftuj 1 note

Aplikuj non-negotiables + conversion gaty. One-sentence-per-line formát (prázdný řádek
mezi větami). Drž se fáze a vybraného archetypu.

## Krok 4.5 — Vygeneruj AI pozadí (pc-mcp)

Pozadí karty = **bohatý tématický obrázek** (jako article cover), NE plochý gradient.
Generuj přes **pc-mcp** (Danielův PC, Codex/ComfyUI, $0). Pozadí pak dostane SVG vrstvu
(headline/stats/quote) + tmavý scrim — proto **vždy nech klidnější/tmavší plochu na text**
(typicky levá třetina nebo horní polovina).

1. `generate_image`, `useAvatar:true`, `aspect:"1:1"`, prompt = **workshop/maker scéna
   s Danielovým avatarem** (krátké vousy, navy snapback s malou červenou hvězdou, červená
   bunda přes tmavou mikinu), deep navy #0B1221 atmosféra, teal + warm orange rim light,
   soft depth of field, premium build-in-public mood, **no text no logos no watermark**.
   Scénu laď podle note/archetypu, např.:
   - struggle-moment → maker pozdě v noci u laptopu, ruční editace, unavený
   - milestone/launch → maker spokojeně sleduje hotový 9:16 reel zářící vedle něj
   - contrarian → maker odmítá "subscription" UI panely, drží vlastní klíče
   - behind-the-scenes → workshop stůl, laptop, článek → video pipeline, floating UI
   Vždy doplň: *"keep the left third (or top half) calmer/darker for text overlay"*.
2. Polluj `generate_image_status` à ~10s dokud `status:"done"` (~30–120s; codex→ComfyUI
   fallback; pozn. ComfyUI ignoruje referenci, ale avatar utáhne z popisu). Vezmi `url`.
3. URL → `imageSpec.backgroundUrl` (Krok 5). Když gen selže/timeout (>3 min), pokračuj
   BEZ pozadí (gradient fallback OK) — nikdy kvůli pozadí neblokuj naplánování note.

## Krok 5 — Postav imageSpec

- **stat_card** (proof čísla):
  ```json
  { "template": "stat_card",
    "headline": "What the reel pipeline made",
    "accentWord": "made",
    "stats": [
      { "label": "reels from articles", "value": "<videoCount>" },
      { "label": "total views", "value": "<totalViews>", "accent": true },
      { "label": "cost per render", "value": "$0" } ] }
  ```
- **quote_card** (POV/věta): `{ "template": "quote_card", "quote": "<jedna úderná věta z note>", "attribution": "Daniel · Reel Pipeline Kit" }`
- **ramp fáze** stat_card varianta: `HeyGen $29/mo` vs `$39 once` vs `break-even ~6 weeks`.
- **backgroundUrl**: přidej `"backgroundUrl": "<url z Kroku 4.5>"` do imageSpec (jakýkoli
  template ho podporuje; render fetchne + složí pod text s tmavým scrimem). Vynech, když gen selhal.

Použij JEN reálná čísla z Kroku 1.

## Krok 6 — Schedule

`schedule_note` s:
- `content` = draft
- `scheduledFor` = **dnešní den 12:00 CET** (ISO; 12:00 CET = 10:00Z mimo DST / 10:00Z; v létě CEST = 10:00Z). Použij 2026-MM-DDT10:00:00Z pro letní čas.
- `angle` = `launch:<archetyp>` (pro dedup/rotaci)
- `imageSpec` = z Kroku 5

## Krok 7 — Telegram notifikace (review okno)

Po naplánování pošli Danielovi preview přes **subhook Telegram relay** (stejně jako
ostatní routiny). `NOTIFY_KEY` dostaneš z routine promptu — NIKDY ho nedávej do hub skillu.
Relay je text-only (drží bot token v subhooku), takže pošli text + bg URL inline:
```
curl -s -X POST "https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY" -H "Content-Type: application/json" \
  -d '{"title":"📅 Reel Kit launch note — <YYYY-MM-DD>","text":"<note text>\n\n— publikace 12:00 CET · scheduled id <id> · archetyp <x>\npozadí: <imageSpec.backgroundUrl nebo \"gradient\">\nuprav/zruš v grownote /schedule do 12:00"}'
```

Output Danielovi: fáze, archetyp, text note, imageSpec, kdy naplánováno + že odešel Telegram.
V interaktivním běhu (ne cron) nejdřív ukaž draft k odsouhlasení; v cron módu naplánuj rovnou,
pošli Telegram a jen reportuj.

## Po-launch poznámka

Po 2026-07-07 přepni stat_card na **buyer results** (rating count, sales count z Gumroadu)
jakmile budou dostupné — do té doby drž YouTube proof + quote_card.
