---
name: fly-cost-audit
description: Opakovatelný (měsíční) audit Fly.io nákladů napříč Danielovou personal org — enumeruje apps / machines / volumes / IP adresy, identifikuje idle a overprovisioned kandidáty, a navrhne konkrétní úsporná opatření (suspend, scale-to-zero via autostop, destroy sirotčích volumes/IP, downsize machine) BEZ rozbití prod worker cest. Read-only default: skill jen reportuje + navrhne příkazy; nic nevypíná bez explicitního OK. Použij když Daniel řekne: "fly cost audit", "fly se prodražuje", "co na fly vypnout", "kolik mě stojí fly", "projdi fly apps", "fly úklid", "co běží zbytečně na fly", "audit fly nákladů", "fly bill je vysoký", "optimalizuj fly". Aktivuj se i při "kde na fly platím zbytečně" / "můžu něco na fly suspendnout".
---

# fly-cost-audit

Měsíční read-only audit Fly nákladů. **Default = reportuj + navrhni, neměň.** Destruktivní akce (`suspend`, `machines destroy`, `volumes destroy`, `ips release`, downsize) provádět jen po explicitním OK per položku — Daniel platí Fly z osobního účtu a některé "idle" appky jsou úmyslně stopped-but-scale-to-zero worker cesty.

Org: `personal` (jediná). CLI `flyctl` (`/opt/homebrew/bin/flyctl`) na Macu je přihlášený a stačí read scope.

## Co NIKDY nenavrhovat vypnout (prod cesty)

- **substack-mcp** — webhook router pro VŠECHNY Telegram boty (REELS/OPS/THREADS/Craftie/Gaia) + Substack automatizace + Inngest publishDue. `app` i `worker` process group musí žít. Stopped machines v `worker`/`app` skupině = normální autostop, NE mrtvola.
- **article-forge** — prod content app + čte Fly PG, enqueue video_jobs.
- **dcw-foundary-pg** — kanonická Postgres DB (articleforge schema, video_jobs queue). Nikdy.
- **drippery** / **drippery-mcp** — prod SaaS (push = deploy, viz [[feedback_drippery_prod_push]]).
- **grownote**, **mem0-remote**, **umami-mcp** — aktivní deployed služby.

Cokoli `suspended` už úsporu nedělá (suspend = 0 compute) — u těch řešit jen sirotčí **volumes** a **dedikované IP** (ty se účtují i u suspended app).

## Krok 1 — Enumerace (read-only)

```bash
flyctl apps list
```

Pro každou `deployed` app projdi machines + volumes (suspended appky stačí zkontrolovat na volumes/IP):

```bash
for app in $(flyctl apps list --json 2>/dev/null | python3 -c "import json,sys; [print(a['Name']) for a in json.load(sys.stdin)]"); do
  echo "=== $app ==="
  flyctl machines list -a "$app" 2>/dev/null
  flyctl volumes list -a "$app" 2>/dev/null
  flyctl ips list -a "$app" 2>/dev/null
done
```

Sesbírej per app: počet machines + jejich `STATE`/`SIZE`/`REGION`, volumes (SIZE, ATTACHED VM), dedikované IPv4 (`v4` typ `public` = $2/měs each; `v6` je zdarma; shared `v4` zdarma).

## Krok 2 — Klasifikace kandidátů

Flagni tyto vzory:

1. **Overprovisioned machine** — `SIZE` > `shared-cpu-1x:512MB` u nízkotraffic MCP/webhook služby, nebo víc `started` machines než potřeba (2× app + 2× worker u malé služby = kandidát na 1+1).
2. **Sirotčí volume** — `ATTACHED VM` prázdné, nebo volume u suspended/mrtvé app. Účtuje se ~$0.15/GB/měs i nepřipojený.
3. **Placená dedikovaná IPv4** — `public v4` u app, která ji nepotřebuje (interní/flycast-only nebo suspended). $2/měs each.
4. **Zombie deployed app** — `deployed`, ale žádný traffic a není v prod-cestách listu výše (ověř účel přes `flyctl status -a <app>` + poslední deploy stáří). Kandidát na `suspend`.
5. **Always-on bez autostop** — machine `started` 24/7 u služby, co snese scale-to-zero (`min_machines_running=0` + `auto_stop_machines`). Ověř `fly.toml` v příslušném repu než navrhneš — worker pollery scale-to-zero NESMÍ.

## Krok 3 — Report

Vypiš tabulku: `app | stav | kandidát | odhad úspory/měs | akce | riziko`. Seřaď podle úspory sestupně. Odhad počítej hrubě:
- shared-cpu-1x:512MB always-on ≈ $2–4/měs; 1x:1GB ≈ $5–7; performance/2x+ výrazně víc.
- volume ≈ $0.15/GB/měs.
- dedikovaná IPv4 = $2/měs.

Uveď i **celkový odhad měsíční úspory** a označ, co je bezpečné (sirotčí volume/IP) vs. co chce ověření (`fly.toml` autostop, účel zombie app).

## Krok 4 — Provedení (jen po OK, per položka)

Nikdy batch. Pro každou schválenou položku:

```bash
flyctl ips release <ip> -a <app>            # dedikovaná IPv4
flyctl volumes destroy <vol-id>             # sirotčí volume (ptá se na potvrzení)
flyctl apps suspend <app>                   # zombie app
flyctl scale count 1 -a <app>               # snížení počtu machines
flyctl scale vm shared-cpu-1x --memory 512 -a <app>   # downsize
```

Autostop (scale-to-zero) se dělá editem `fly.toml` (`[http_service] auto_stop_machines = "stop"`, `min_machines_running = 0`) + redeploy — to je změna kódu, ne CLI, a u worker apps NEdělej.

## Krok 5 — Log

Po auditu ulož `mem0_add` shrnutí (co flagnuto, co reálně vypnuto, odhad úspory) s `{"project":"infra","category":"decision"}`, ať příští měsíční audit ví, co už bylo řešeno. Report ideálně i do `secondbrain/infra-map.md` (viz [[reference_infra_map_and_tasks]]).

## Známý stav (2026-07-05, baseline)

Deployed: archieve-concierge, article-forge, craft-os, dcw-foundary-pg, drippery, drippery-mcp, grownote, mem0-remote, substack-mcp, umami-mcp. Suspended (compute už = 0, řeš jen volumes/IP): dcw-context-hub-mcp, digitalcraftworkshop-web, echoeswithingames, grownote-mcp, gumroad-mcp, rpk-updates, subhook, umami-foundary. substack-mcp jede 4 machines (2 app + 2 worker, fra, 512MB) — část stopped je normální autostop, neflagovat jako mrtvé.
