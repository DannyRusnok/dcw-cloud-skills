---
name: histreel-render-doctor
description: Diagnostika a oprava selhání HistReel / Bohemia Chronicles render pipeline (Wan reely z historie), kterou `reel-routine-doctor` NEpokrývá — HistReel má vlastní render cestu (dashboard/Telegram enqueue → `render-queue.json` JSON fronta → `scripts/run_render_job.py` FÁZE B deterministický Python → lokální ComfyUI → R2). Symptom: "reel se nevyrenderoval", "ráno chyba na Telegram", tichý fail. Skill má DIAGNOSE → ROOT CAUSE → FIX → VERIFY: ověří queue stav, stale lock, ComfyUI, cutoff, dashboard R2 drain, a re-enqueue konkrétní pilot. Použij když Daniel řekne: "histreel render failnul", "bohemia chronicles reel se nevyrobil", "golem reel se nic nestalo", "histreel doctor", "render-queue zaseknutá", "histreel se nevyrenderoval", "diagnostikuj histreel render", "reel z historie nedojel". Jede přes `aivideo-pc-ssh` (host `aivideo-pc`, PowerShell). Sister k `reel-routine-doctor` (Substack reely), ale HistReel-specific.
---

# histreel-render-doctor

HistReel render = **FÁZE A** (headless `claude -p` jen matchuje Telegram approvals do `histreel-pending.json`) + **FÁZE B** (`scripts/run_render_job.py`, čistý Python, protože ~1h Wan render claude -p neublbabysituje — golem-prague umřel přesně takhle, viz [[project_histreel_render_faze_b_python]]). Task `HistReelRender` (běží ~každých 5 min). Fronta je **JSON soubor** `histreel/render-queue.json`, NE Postgres tabulka.

SSH: `ssh -o BatchMode=yes aivideo-pc '<PowerShell>'`. Repo na PC: `%USERPROFILE%\foundary-tools\histreel`. Log: `dcw-context-hub\ops\histreel-render.log`.

## Diagnose (spusť vše, přečti výstup)

```bash
# 1. task žije + poslední výsledek
ssh aivideo-pc 'schtasks /query /tn HistReelRender /v /fo list 2>$null | Select-String "Status|Last Run|Last Result|Next Run"'
# 2. tail render logu (kde to spadlo)
ssh aivideo-pc 'Get-Content "$env:USERPROFILE\foundary-tools\dcw-context-hub\ops\histreel-render.log" -Tail 40'
# 3. stav fronty — job statusy, attempts, error
ssh aivideo-pc 'Get-Content "$env:USERPROFILE\foundary-tools\histreel\render-queue.json" -Raw'
# 4. stale lock? (LOCK_STALE_H=2 → lock starší 2h = mrtvý)
ssh aivideo-pc 'Get-Item "$env:USERPROFILE\foundary-tools\histreel\.render-job.lock" -ErrorAction SilentlyContinue | Select-Object LastWriteTime,Length'
# 5. ComfyUI reachable + idle?
ssh aivideo-pc 'try { $r=Invoke-WebRequest "http://127.0.0.1:8188/system_stats" -UseBasicParsing -TimeoutSec 5; "COMFY_OK "+$r.StatusCode } catch { "COMFY_DOWN "+$_.Exception.Message }'
# 6. dashboard render requesty na R2 nedrainované? (rychlý peek do queue "note":"dashboard")
```

## Root causes (mapuj symptom → příčina)

1. **Job `status:"failed"`, `attempts>=2`** — render spadl 2× (Wan OOM, ComfyUI eviction pod paralelním load, chybný pilot asset). Příčina v `error` poli jobu + logu. HistReel sdílí GPU s reel-pool → paralelní job evikne `/history`.
2. **Job `status:"rendering"` ale žádný fresh mp4** — proces umřel mid-render (crash/reboot/turn-kill). Skript to sám detekuje a přebere, POKUD lock nedrží mrtvá PID.
3. **Stale lock** — `.render-job.lock` drží PID, který už neběží (nebo starší 2h). Blokuje pickup → fronta stojí, task self-exituje "nic k práci".
4. **ComfyUI down/busy** — `system_stats` neodpovídá → GPU joby skript přeskočí (guard). Task `ComfyUI`/`ComfyUIAutoStart` neběží nebo visí.
5. **20:30 Wan cutoff** — po 20:30 CET skript GPU render odloží (kolize s reel-pool oknem). Není to bug; večerní ruční run = `--force`.
6. **Dashboard request neproputoval** — R2 `histreel/dashboard/render-requests.json` se nedrainoval do `render-queue.json` (R2 auth/network). Job pak ve frontě vůbec není.

## Fix (per root cause)

```bash
# stale lock → smaž a spusť
ssh aivideo-pc 'Remove-Item "$env:USERPROFILE\foundary-tools\histreel\.render-job.lock" -Force -ErrorAction SilentlyContinue'
# ComfyUI down → nastartuj
ssh aivideo-pc 'schtasks /run /tn ComfyUI'
# re-enqueue / retry: přepni failed job zpět na queued (attempts=0), pak spusť FÁZE B ručně s --force
ssh aivideo-pc 'cd "$env:USERPROFILE\foundary-tools\histreel"; python scripts\run_render_job.py --dry-run'   # ověř, který job vezme
ssh aivideo-pc 'cd "$env:USERPROFILE\foundary-tools\histreel"; python scripts\run_render_job.py --force'      # skutečný render
```
Failed→queued reset: edituj `render-queue.json` (dané job `status:"queued"`, `attempts:0`, smaž `error`) přes PowerShell nebo lokální edit + `git push`; skript pak drží queue v gitu, takže po ruční editě commitni. Konkrétní pilot re-enqueue z dashboardu: znovu klikni render button (zapíše R2 request → drain → queue).

## Verify

```bash
ssh aivideo-pc 'cd "$env:USERPROFILE\foundary-tools\histreel"; python scripts\run_render_job.py --force >> "$env:USERPROFILE\foundary-tools\dcw-context-hub\ops\histreel-render.log" 2>&1; Get-Content "$env:USERPROFILE\foundary-tools\dcw-context-hub\ops\histreel-render.log" -Tail 15'
```
Úspěch = job `status:"done"` v `render-queue.json` + Telegram zpráva s videem a 2 check-frames. Pokud opět fail, přečti `error` + log tail a jdi na odpovídající root cause.

## Guardrails
- Nespouštěj GPU render když běží reel-pool okno bez `--force` důvodu (kolize o GPU).
- `render-queue.json` je verzovaný v gitu — po ruční editě VŽDY commit+push, jinak `git pull --autostash` v runneru edit přepíše.
- Nevytvářej druhý paralelní `run_render_job.py` — lock je singleton guard; když se zdá zaseklý, řeš stale lock, ne druhou instanci.
