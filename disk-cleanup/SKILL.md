---
name: disk-cleanup
description: Analyzuje Danielův disk a nabízí quick win cleanup když dochází místo. Použij tento skill kdykoli Daniel řekne: "mám málo místa", "dochází mi místo na disku", "co mi žere disk", "vyčisti cache", "co zabírá místo", "disk full", "free up space", "udělej úklid", "co se dá smazat", "low disk space", "co mi narostlo", "narostly cache", "smaž cache". Aktivuj se i při frázích "potřebuju uvolnit místo", "kam zmizel disk", "proč mám plno", "co žere disk" nebo kdykoli Daniel zmíní problém s volným místem na disku. Skill je 2-fázový: nejdřív analýza (df + du top consumers), pak nabídne quick wins (yarn/brew/npm/pip caches, Claude caches, dev tool caches) — destruktivnější akce (Downloads, app data, node_modules nuke) jen po explicitní žádosti.
---

# Disk Cleanup

Když dochází místo, projdi disk a nabídni quick win. Vždy ve 2 krocích: **analýza → nabídka → (čekání na ack) → akce**. Nikdy automaticky nesmaž víc než safe caches.

## Krok 1: Analýza

Spusť tyto checks v jednom Bash callu (chained `;`):

```bash
df -h / | tail -1 | awk '{print "DISK: "$3" used / "$2" total, "$4" free ("$5")"}'
echo "---HOME TOP---"
du -sh ~/* 2>/dev/null | sort -h | tail -15
echo "---LIBRARY---"
du -sh ~/Library/* 2>/dev/null | sort -h | tail -8
echo "---CACHES---"
du -sh ~/Library/Caches/* 2>/dev/null | sort -h | tail -10
echo "---APP SUPPORT---"
du -sh ~/Library/Application\ Support/* 2>/dev/null | sort -h | tail -8
```

Output presentuj jako concise report:
- 1 řádek **disk overview** (used / total / free)
- **Top 5 home dirs** (bullet list)
- **Top 3-5 caches** zvlášť (bullet list)
- **Top 3-5 Application Support** dirs (bullet list)

Max 10-12 řádků celkem. Jen čísla která stojí za to (>500 MB).

## Krok 2: Quick Win nabídka

Po analýze nabídni **safe quick win batch** — věci co se regenerují automaticky a nemají side effects:

| Cíl | Příkaz | Typický zisk |
|---|---|---|
| Yarn cache | `yarn cache clean` | 2-10 GB |
| npm cache | `npm cache clean --force` | 0.5-3 GB |
| pip cache | `pip cache purge` | 0.5-2 GB |
| Homebrew | `brew cleanup -s && rm -rf $(brew --cache)` | 0.3-1.5 GB |
| Google Chrome cache | `rm -rf ~/Library/Caches/Google` | 0.5-2 GB |
| Microsoft Edge cache | `rm -rf ~/Library/Caches/com.microsoft.edgemac` | 0.3-1 GB |
| Spotify cache | `rm -rf ~/Library/Caches/com.spotify.client` | 0.2-1 GB |
| Claude CLI cache | `rm -rf ~/Library/Caches/claude-cli-nodejs` | 0.5-2 GB |
| Claude Desktop ShipIt (installer cache) | `rm -rf ~/Library/Caches/com.anthropic.claudefordesktop.ShipIt` | 0.5-1 GB |
| Claude vm_bundles (sandbox snapshots) | `rm -rf ~/Library/Application\ Support/Claude/vm_bundles` | 5-15 GB |
| Claude Electron caches | `rm -rf ~/Library/Application\ Support/Claude/Cache ~/Library/Application\ Support/Claude/Code\ Cache` | 0.5-2 GB |
| ChatGPT Atlas cache | `rm -rf ~/Library/Caches/com.openai.atlas` | 0.3-1 GB |
| Cursor workspaceStorage | `rm -rf ~/Library/Application\ Support/Cursor/User/workspaceStorage` | 1-3 GB |
| VSCode workspaceStorage | `rm -rf ~/Library/Application\ Support/Code/User/workspaceStorage` | 0.5-2 GB |
| Notion Partitions (Electron webview cache) | `rm -rf ~/Library/Application\ Support/Notion/Partitions` | 3-8 GB |
| Docker (pokud běží) | `docker system prune -a` | 1-10 GB |
| Xcode DerivedData | `rm -rf ~/Library/Developer/Xcode/DerivedData` | 1-10 GB |
| iOS Simulator caches | `xcrun simctl delete unavailable` | 5-30 GB |

**Pozn. k Claude/Notion:**
- `Claude/vm_bundles` = per-repo sandbox snapshots, regenerují se při dalším použití agent mode.
- `Claude/Cache/Cache_Data` často zůstane (file lock když Claude běží) — to je OK, drobnost.
- **Nikdy nesahat na** `Claude/claude-code-sessions` (historie), `Claude/local-agent-mode-sessions` (běžící agenti), `Notion/notion.db` (sign-in + offline data).

Vyber **jen ty co dávají smysl podle analýzy** (např. nemá smysl nabízet yarn clean když yarn cache je 50 MB). Skládej do jednoho chained příkazu s `BEFORE`/`AFTER` measure:

```bash
df -h / | tail -1 | awk '{print "BEFORE: "$4" free"}'
yarn cache clean 2>&1 | tail -2
brew cleanup -s 2>&1 | tail -3
rm -rf ~/Library/Caches/Google
df -h / | tail -1 | awk '{print "AFTER: "$4" free"}'
```

Zeptej se **"Spustit quick win? (a/n)"** a počkej na ack než spustíš.

## Krok 2b: App full removal

Pokud Daniel řekne "odstranit X" / "smaž X aplikaci" / "X mi nestojí za místo", smaž v jednom batchu:

```bash
rm -rf /Applications/<App>.app
rm -rf ~/Library/Application\ Support/<App>
rm -rf ~/Library/Caches/com.*<app>*
rm -rf ~/Library/Preferences/*<app>*
```

Vždy ukaž BEFORE/AFTER `df -h /`. Pro známé velké appky (Spotify, Steam, Cursor, Code, Notion, ChatGPT Atlas) typicky uvolní 2-5 GB každá.

## Krok 3: Po quick winu — riskantnější možnosti

Pokud quick win uvolnil < 5 GB a disk je stále tight (<10 GB free / >85% full), nabídni **review-needed kategorie**:

1. **`~/Downloads`** — fastest manual review wins, ale potřebuje Daniel rozhodnout co smáznout
2. **`~/Library/Application Support/<largest>`** — desktop app data (Claude, Cursor, VS Code můžou mít gigy)
3. **node_modules audit** — `find ~ -name node_modules -type d -prune` v projektech co dlouho needitoval
4. **Old git worktrees / clones** — staré checkouts co už nepotřebuje
5. **Docker images / volumes** — pokud má Docker

Pro každou kategorii uveď **co je tam** + **velikost** + **risk** ("safe to delete" / "review first" / "destructive"). NIKDY nesmaž bez explicitní žádosti.

## Pravidla

- **Concise mode**: report ≤12 řádků, žádný úvod/závěr, jen čísla a akce
- **Vždy 2 fáze**: analýza → ack → akce. Nikdy nesmaž v stejném callu jako analýza
- **Safe-only auto**: yarn/npm/pip/brew caches + browser caches jsou OK pro nabídku, ale NIKDY auto-spuštění bez Danielova "a" / "spusť" / "OK"
- **Nikdy `rm -rf ~/*` / wildcardy**: vždy explicit cesty
- **Nikdy `node_modules` auto-purge**: může vzít aktivní projekt
- **Měř BEFORE/AFTER**: `df -h /` před a po, ukaž delta v jednom řádku
- **Concise-mode follow-up**: zakonči "Pokračovat? (1=X, 2=Y, 3=Z)" nebo "Spustit? (a/n)"

## Anti-patterns

❌ Analyzovat → rovnou mazat ve stejném tool callu
❌ Nabízet `rm -rf ~/Library/Application Support/Claude` bez upozornění že to nuke session history
❌ `find ~ -name node_modules -exec rm -rf {} +` bez review listu projektů
❌ Dlouhý report s 30 řádky du output — Daniel to nečte
❌ Použít skill proaktivně po editu kódu — pouze on-demand
