---
name: pc-routine-audit
description: Audit VŠECH Danielových automatizací napříč dvěma běhovými prostředími — PC Windows scheduled tasks (přes aivideo-pc SSH) + claude.ai cloud routines — a jejich cross-match podle účelu, aby vypadly duplicity, mrtvé/failující tasky a překryvy (stejná práce PC i cloud). `pc-scheduled-routine` umí jen VYTVÁŘET; tenhle skill INVENTARIZUJE a diagnostikuje. Read-only default: reportuje + navrhne enable/disable/delete, ale nic nemění bez explicitního OK per položka. Použij když Daniel řekne: "co běží kde", "mám zdvojenou rutinu", "audit rutin", "projdi scheduled tasky", "co všechno mám naplánované", "nemám duplicitní rutiny?", "co běží na PC vs cloud", "pc routine audit", "úklid rutin", "která rutina failuje". Aktivuj se i při "běží scheduled task na X?" / "asi mám tu samou rutinu 2×".
---

# pc-routine-audit

Inventura + diagnostika automatizací. **Default = reportuj, neměň.** Enable/disable/delete jen po explicitním OK per task. SSH na PC: `ssh -o BatchMode=yes aivideo-pc '<PowerShell>'` (skill `homepc-ssh`, host `100.113.86.52`, user `danie`, remote = PowerShell).

## Krok 1 — Enumerace PC scheduled tasks

```bash
ssh -o BatchMode=yes aivideo-pc 'schtasks /query /fo table /nh 2>$null | Where-Object { $_ -notmatch "\\Microsoft\\" -and $_ -notmatch "OneDrive|NVIDIA|Edge|Adobe" -and $_.Trim() -ne "" }'
```

Pro každý podezřelý/relevantní task vytáhni detail (co spouští + poslední výsledek):
```bash
ssh aivideo-pc 'schtasks /query /tn <TaskName> /v /fo list 2>$null | Select-String "TaskName|Status|Schedule|Task To Run|Next Run|Last Run|Last Result|Scheduled Task State"'
```
`Last Result` ≠ 0 (a ≠ 267009 = "currently running") → task failuje. `Disabled` → mrtvý kandidát. `Task To Run` odkazuje na `ops\<name>.cmd` v dcw-context-hub — účel poznáš z názvu + `ops/<name>-prompt.md`.

## Krok 2 — Enumerace cloud routines

Cloud routiny (claude.ai) nejsou přes SSH — jejich seznam žije v `~/foundary-tools/dcw-cloud-skills/ROUTINES.md` (sekce cloud vs PC). Přečti ho:
```bash
cat ~/foundary-tools/dcw-cloud-skills/ROUTINES.md 2>/dev/null
```
Pozn.: claude.ai routine seznam nejde číst programaticky (žádné MCP) — ROUTINES.md je jediný zdroj pravdy, který Daniel udržuje. Pokud je stale, flagni to a spolehni se na PC-side signály.

## Krok 3 — Cross-match a klasifikace

Postav mapu `účel → kde běží`. Flagni:

1. **Duplicita PC×cloud** — stejná práce plánovaná na PC i jako cloud routine (např. daily notes na obou). Cloud má strop ~15 runs/den → preferuj PC verzi, cloud vypnout (viz [[feedback_routines_on_pc_not_mac.md]]).
2. **Duplicita PC×PC** — dva tasky se stejným `Task To Run` nebo překrývajícím účelem/časem.
3. **Failující** — `Last Result` nenulový opakovaně (ověř přes `ops/<name>.log` tail).
4. **Mrtvý** — `Disabled`, nebo runner `.cmd`/`-prompt.md` už v repu neexistuje, nebo cíl (skill/endpoint) zrušený.
5. **Sirotek** — task existuje, ale runner soubor v `ops/` chybí (nebo naopak `ops/*.cmd` bez registrovaného tasku).

Sirotčí runnery: porovnej `ops/*.cmd` v hubu se seznamem tasků:
```bash
ls ~/foundary-tools/dcw-context-hub/ops/*.cmd | xargs -n1 basename | sed 's/.cmd$//' | sort
```

## Krok 4 — Report

Tabulka: `rutina | běží kde (PC/cloud) | schedule | poslední stav | verdikt (OK/duplicita/failuje/mrtvá/sirotek) | návrh`. Seřaď: nejdřív problémové (failuje/duplicita), pak OK. Uveď počty (X OK, Y problémů) a explicitní seznam navržených akcí.

## Krok 5 — Provedení (jen po OK, per položka)

```bash
ssh aivideo-pc 'schtasks /change /tn <TaskName> /disable'   # deaktivace (reverzibilní)
ssh aivideo-pc 'schtasks /delete /tn <TaskName> /f'         # smazání (po disable + ověření)
```
Cloud routine se z CLI vypnout nedá → napiš Danielovi konkrétní instrukci ("vypni routine X v claude.ai UI"). Preferuj `disable` před `delete` — reverzibilní; delete až když je runner i účel prokazatelně mrtvý.

## Guardrails
- Nikdy nesmaž/nedisabluj **infra-critical** tasky bez OK: `pc-mcp`, `PCTaskWorker`, `PcDashboard`, `GaiaSdk`, `ClaudeConfigBackupPC`, `ClaudeOrphanWatchdog`, `SubstackSidKeepalive`, `HistReelRender`, `loop-revive`, `ComfyGate`/`ComfyUI*` (running/infra, ne content rutiny).
- Microsoft/NVIDIA/Edge/Adobe/OneDrive systémové tasky ignoruj úplně (nefiltruj je do reportu).
- `Running`/`267009` = běží teď, NE failure.

## Baseline (2026-07-05, ~55 content/ops tasků)
Infra (nesahej): pc-mcp, PCTaskWorker, PcDashboard, GaiaSdk, HistReelRender, loop-revive, ClaudeConfigBackupPC, ClaudeOrphanWatchdog, SubstackSidKeepalive, ComfyGate, rpk/rpkserver. Disabled: EliUriSceneGen, RpkLaunchPipeline, RpkOutreachReels (ověř zda záměrně). Content/ops rutiny (kandidáti auditu): AF-MediumBackfill, AttributionWeekly, CodexRefactor, CollabScout, DcwWebSync, EvergreenRepost, Hashnode/Medium/Histreel publish runnery, ReadsInMotionBig, RimTopReelsWeekly, Substack* (AutoLike/DailyNotes/RepostOldArticle/SchemaWatch/RedraftWatch), Threads* (Daily/PublishAM/PublishPM), reelrun. Cloud routines viz ROUTINES.md.
