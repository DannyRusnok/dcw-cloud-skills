---
name: aivideo-pc-ssh
description: Jak se SPRÁVNĚ a hned napoprvé připojit přes SSH na Danielův home PC (Windows, RTX 3060, ComfyUI, Tailscale). Obsahuje ověřený host alias, username, klíč a Windows/PowerShell gotchas — aby se neopakovalo zdlouhavé debugování špatného hostu/usera. Použij kdykoli Daniel řekne: "ssh na PC", "připoj se na PC", "spusť něco na PC", "na home PC", "desktop-smcnedq", "aivideo-pc", "ovládej PC přes ssh", "remote na PC", nebo když jakýkoli jiný skill (medium-backfill, ComfyUI render) potřebuje běžet na PC. Aktivuj se i při frázích "to spusť na PC", "na tom druhém stroji".
---

# aivideo-pc-ssh

Ověřené připojení na Danielův home PC. **Nehádej host ani usera** — použij přesně tohle.

## Správné připojení (jediná funkční varianta)

```bash
ssh -o BatchMode=yes aivideo-pc '<powershell-command>'
```

Host alias `aivideo-pc` je v `~/.ssh/config`:
- **HostName**: `100.113.86.52` (Tailscale IP)
- **User**: `danie` (NE `danielrusnok`)
- **IdentityFile**: `~/.ssh/id_ed25519_aivideo`
- Remote account: `desktop-smcnedq\danie`

### Časté chyby (NEDĚLEJ)

- ❌ `ssh desktop-smcnedq` → připojí se jako `danielrusnok` → `Permission denied`. Hostname `desktop-smcnedq` má špatného defaultního usera.
- ❌ Hádat klíč — jediný relevantní je `id_ed25519_aivideo`.
- ✅ Vždy `ssh aivideo-pc`.

## Remote shell = PowerShell (Windows)

Příkazy přes SSH běží v **PowerShell**, ne bash. Bash syntax selže:

| Bash (NEFUNGUJE) | PowerShell (správně) |
|---|---|
| `cmd 2>/dev/null` | `cmd 2>$null` nebo `-ErrorAction SilentlyContinue` |
| `a || b` | `a; if (-not $?) { b }` |
| `ls path` | `Test-Path path` / `Get-ChildItem path` |
| `~/foo` | `"$env:USERPROFILE\foo"` |
| `grep` | `Select-String` / `findstr` |
| `tail -3` | `Select-Object -Last 3` |

Multi-příkaz: oddělit `;` (PowerShell statement separator).

## Ověřené PC facts

- **Chrome**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
  - Spuštění: `Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "<url>"`
- **Claude skills dir**: `$env:USERPROFILE\.claude\skills`
- **foundary-tools repos**: `$env:USERPROFILE\foundary-tools\` (vč. `dcw-cloud-skills`)
- **SSH admin key file** (Windows OpenSSH, admin účet): `C:\ProgramData\ssh\administrators_authorized_keys` — user `~/.ssh/authorized_keys` se pro účty v Administrators grupě IGNORUJE.

## Smoke test

```bash
ssh -o BatchMode=yes aivideo-pc 'whoami; hostname'
```
Očekávaný output: `desktop-smcnedq\danie` + `desktop-smcnedq`.

Pokud `Permission denied`:
1. Ověř že používáš `aivideo-pc` (ne `desktop-smcnedq`).
2. `ssh-add -l` na Macu — agent může být prázdný, ale `-i` v configu to řeší.
3. Klíč `id_ed25519_aivideo.pub` musí být v PC `C:\ProgramData\ssh\administrators_authorized_keys` s právy jen pro Administrators+SYSTEM (`icacls ... /inheritance:r /grant Administrators:F /grant SYSTEM:F`).
4. PF VPN připojení neblokuje (Tailscale jede paralelně).

## Pozn.

PC nemá heslo k textovému loginu (Daniel má jen Windows PIN) — password SSH auth není použitelná, **jedině klíč**.
