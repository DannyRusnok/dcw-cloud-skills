---
name: git-local-exclude
description: Přidá soubor nebo cestu do lokálního git exclude (.git/info/exclude) — netrackovaný, čistě lokální ignore bez zásahu do sdíleného .gitignore a bez commitu. Použij kdykoli Daniel řekne "přidej do local exclude", "netrackuj tenhle soubor", "ať to git nevidí", "git exclude", "lokální gitignore", "nechci to commitnout ani dávat do .gitignore", "vylouč to lokálně", "skryj to z git status", nebo když má rozpracovaný lokální soubor (service-account key, .env, dev script, dump, scratch), který nesmí do repa ani do sdíleného ignore. Preferuj tento skill před editací .gitignore, když soubor patří jen na Danielův stroj.
---

# git-local-exclude

Lokální, per-repo, netrackovaný ignore přes `.git/info/exclude`. Na rozdíl od `.gitignore` se necommituje a neovlivní ostatní vývojáře — ideální pro soubory specifické jen pro Danielův stroj (secrets, service-account keys, dev scripty, dumpy, scratch).

## Kdy tenhle skill vs. .gitignore

- **`.git/info/exclude` (tento skill):** soubor patří jen sem na tenhle stroj, nemá logický důvod být ve sdíleném ignore (konkrétní key file, osobní dev script, lokální SQL). Default volba pro PF repa — Daniel tak už drží scripty a Claude context soubory.
- **`.gitignore`:** vzor relevantní pro celý tým (build artefakty, `node_modules`, obecné `*.log`). Sem jen když to dává smysl commitnout.

Při pochybnosti a u citlivých souborů (klíče, `.env`) → `.git/info/exclude`.

## Postup

1. **Zjisti repo root a cestu.** Cesta v exclude je relativní k rootu repa (ne ke cwd):
   ```bash
   git rev-parse --show-toplevel
   git ls-files --others --exclude-standard | grep <hledaný soubor>
   ```
   Pokud je soubor pod `src/`, zapiš `src/<soubor>` — přesně jak ho ukazuje `git status --short`.

2. **Přečti stávající exclude** a najdi vhodnou sekci (v `application` existují sekce jako `# Lokální dev scripty`, `# Claude context files`, `# Local secrets / service account keys`). Přidej do odpovídající, nebo založ novou s krátkým `#` popiskem.
   ```
   .git/info/exclude
   ```

3. **Přidej řádek.** Přesná cesta (ne glob), pokud Daniel nechce vzor. Pro rodinu souborů (např. všechny GCP keys) lze glob typu `src/gen-lang-client-*.json` — ale jen když to Daniel řekne nebo je to zjevně bezpečné.

4. **Ověř, že git soubor přestal vidět:**
   ```bash
   git status --short | grep <soubor> || echo "OK — vyloučeno"
   ```
   Prázdný výstup = hotovo.

## Když je soubor už tracked

`.git/info/exclude` ignoruje jen **untracked** soubory. Pokud je soubor už v indexu, nejdřív ho odtrackuj (bez smazání z disku), pak přidej do exclude:
```bash
git rm --cached <soubor>
```
Pozor: `git rm --cached` je změna, kterou je potřeba commitnout, aby zmizel z repa u ostatních — u secretu, který už byl commitnutý, upozorni Daniela, že klíč je v historii a měl by se rotovat.

## Poznámky

- Nikdy necommituj `.git/info/exclude` — je mimo working tree, git ho netrackuje z principu.
- U secretů (service-account JSON, `.env`, tokeny): potvrď, že soubor ještě nebyl nikdy commitnutý (`git log --all --oneline -- <soubor>`). Pokud byl, klíč je kompromitovaný → doporuč rotaci.
- V PF repu `application` je exclude jediné správné místo pro lokální scripty a Claude context soubory — drž konzistenci s existujícími sekcemi.
