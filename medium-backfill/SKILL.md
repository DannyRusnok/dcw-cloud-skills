---
name: medium-backfill
description: Spustí kompletní Medium analytics backfill přes Article Forge Chrome extension — naplní `article_analytics_daily` (per-day views/reads/earnings + feed clickthrough + read ratio) a `article_traffic_sources_daily` pro zadané měsíce. Skill jen otevře JEDEN Chrome tab s trigger URL; extension si sama natáhne frontu článků z `/api/analytics/backfill-queue` a prochází je jeden po druhém v tom samém tabu (self-navigating, žádné open/close per článek). Běží na Danielově home PC (desktop-smcnedq), kde je nainstalovaný Chrome + Article Forge extension v1.7.0+ a přihlášený Medium účet. Spouští se na dálku přes SSH. Použij když Daniel řekne: "spusť medium backfill", "backfill medium statistik", "naplň medium analytics", "stáhni historii medium", "medium backfill za <měsíce>", "backfill na PC", "spusť backfill přes ssh". Default měsíce: aktuální + předchozí měsíc.
---

# medium-backfill

Single-tab self-navigating Medium analytics backfill. Skill = thin launcher; extension = orchestrator.

## Předpoklady (na PC `desktop-smcnedq`)

- Google Chrome nainstalovaný.
- Article Forge extension **v1.7.0+** loadnutá (Developer mode → Load unpacked z `article-forge/chrome-extension/`).
- Extension popup nakonfigurovaný: `apiUrl` = `https://article-forge.fly.dev`, `apiToken`, `userId`.
- Medium účet přihlášený v tom Chrome profilu.

## Vstup

`měsíce` — comma-separated `YYYY-MM` (např. `2026-05,2026-04`). Pokud Daniel nezadá, default = **aktuální měsíc + předchozí měsíc**.

Výpočet defaultu:
```bash
CUR=$(date +%Y-%m)
PREV=$(date -d "$(date +%Y-%m-01) -1 month" +%Y-%m 2>/dev/null || date -v-1m +%Y-%m)
MONTHS="$CUR,$PREV"
```

## Workflow

### 1. Sestav trigger URL

```
https://medium.com/me/stats#af-backfill=<MONTHS>
```

Hash fragment (ne query) — Medium SPA query stripuje, hash ne.

### 2. Spusť Chrome s trigger URL

Detekuj OS a použij odpovídající příkaz:

- **Windows** (cmd/PowerShell): `start chrome "https://medium.com/me/stats#af-backfill=<MONTHS>"`
- **Windows přes WSL**: `cmd.exe /c start chrome "https://medium.com/me/stats#af-backfill=<MONTHS>"`
- **Linux**: `google-chrome "https://medium.com/me/stats#af-backfill=<MONTHS>" &`
- **macOS**: `open -a "Google Chrome" "https://medium.com/me/stats#af-backfill=<MONTHS>"`

Po otevření `/me/stats` content script detekuje `af-backfill`, zavolá `/api/analytics/backfill-queue`, naseeduje frontu do `chrome.storage.local` a začne se sám proklikávat článek po článku (`af-queue=1`).

### 3. Sleduj progress

Skill nemá přímý přístup do Chrome — sleduj přírůstek řádků v DB. Potřebuješ `DATABASE_URL` (Neon) — z `~/foundary-tools/article-forge/.env.local` pokud je repo na PC, jinak požádej Daniela.

Baseline před spuštěním:
```bash
psql "$DATABASE_URL" -t -A -c "SELECT count(*) FROM articleforge.article_analytics_daily;"
```

Pak polluj každých ~30s. Fronta = `count(queue)` článků × ~12s/článek. Pro 60 článků × 2 měsíce ≈ 24 min.

Hotovo když počet řádků přestane růst 2 cykly po sobě.

### 4. Output

```
✅ Medium backfill done
   Months: <MONTHS>
   article_analytics_daily: +<N> rows
   Verify: https://article-forge.fly.dev/analytics/medium
```

## Edge cases

- **Extension není v1.7.0+** — `af-backfill` se ignoruje, nic se nestane. Poll timeoutuje. Oznámit Danielovi ať reloadne extension.
- **Chrome už běží** — nový tab se přidá do existujícího okna, extension funguje stejně.
- **Medium odhlášený** — článkové stránky redirectnou na login, scrape selže tiše. Pokud po 2 min 0 přírůstek, oznámit "zkontroluj Medium login".
- **Měsíc bez dat u článku** — extension warne v console a pokračuje na další (graceful skip).
- **PC nemá psql / DATABASE_URL** — vynech polling, jen oznam "spuštěno, ověř na /analytics/medium za ~25 min".

## Architektura (proč to takhle)

Skill je záměrně tenký — veškerá logika (fronta, navigace, scrape, month-switch) je v extensioně (`content-medium.js`). Skill jen zapálí jeden URL. Tím je skill OS-agnostic a přenositelný; extension se stará o vše ostatní.

Backend dependencies:
- `GET /api/analytics/backfill-queue?platform=medium&months=<csv>` — vrací `[{externalId, month}]`
- `POST /api/analytics/ingest-daily` — per-day points + funnel metriky
- `POST /api/analytics/ingest-traffic-sources` — referrer breakdown
