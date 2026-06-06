---
name: foundary-tool-pr
description: |
  Cloud routina, která bere schválené návrhy úprav foundary toolů z Notion "Foundary Tool Backlog" DB (status Approved) — ty plní sister-routine `newsletter-digest` z high-signal newsletterů — a každý zaimplementuje jako minimální change + otevře draft PR v cílovém repu (`DannyRusnok/<repo>`). Po otevření PR přepne řádek na status "PR opened" a doplní odkaz. Gate je ruční: routina sahá JEN na řádky, které Daniel v Notion přepnul z Proposed na Approved. Použij když Daniel řekne: "udělej PRka z backlogu", "zpracuj approved tool ideas", "foundary tool pr", "otevři PR z návrhů", "run foundary-tool-pr", "implementuj schválené návrhy". Běží buď manuálně, nebo jako scheduled cloud routine 6:30 CET (po newsletter-digest).
---

# foundary-tool-pr

Druhá polovina newsletter→PR pipeline. `newsletter-digest` navrhuje (status `Proposed`), Daniel schvaluje (`Approved`), **tato routina implementuje + otevře draft PR**. Vždy draft PR, nikdy merge, nikdy push na `main`.

## Konfigurace (předává routine prompt / env)

- `NOTIFY_KEY` — subhook Telegram relay klíč (stejný jako newsletter-digest). Chybí → Telegram krok přeskoč.
- GitHub přístup: routine prompt musí dodat buď (a) `GH_TOKEN` PAT s `repo` scope pro shell `gh`, nebo (b) připojený GitHub konektor (`plugin_engineering_github` tools). Bez jednoho z nich **nelze otevřít PR** → zapiš to do výstupu a skonči, řádky nech `Approved`.
- Notion connector = **DCW-context-hub** (`notion_query_database` / `notion_update_page` / `notion_get_block_children`). Backlog DB = "Foundary Tool Backlog" (vytvořená sister-routinou, parent page `34d3f179-067e-81f5-bc04-f5a40d5aae6b`).
- Owner všech repů: `DannyRusnok`.

## Krok 1 — Najdi backlog a vytáhni Approved

1. `notion_search` "Foundary Tool Backlog" → database/data_source id. Pokud DB neexistuje, **nic ke zpracování** → skonči tiše (digest ji ještě nevytvořil).
2. `notion_query_database` filtr `Status = "Approved"`. Žádné Approved řádky → skonči tiše (případně Telegram "0 approved" jen pokud `NOTIFY_KEY`).
3. Pro každý řádek vytáhni: `Title`, `Repo`, `Effort`, `Confidence`, `Auto-safe`, `Source`, `Insight`, `Change`, page id (pro pozdější update).

Zpracuj max **3 řádky / běh** (chrání před PR floodem). Zbytek nech na příště, seřaď podle `Auto-safe=true` first, pak `Confidence` high→low.

## Krok 2 — Per řádek: routing podle velikosti

- `Effort = S` **nebo** `Auto-safe = true` → **implementuj + draft PR** (krok 3).
- `Effort = M` → implementuj jen pokud `Change` jasně ukazuje na ≤1–2 soubory; jinak fallback issue (krok 4).
- `Effort = L` nebo nejasný rozsah → **neotvírej PR**, založ GitHub **issue** (krok 4). Velké věci patří k Danielovi lokálně.

## Krok 3 — Implementuj minimální change + draft PR

**Preferuj shell `gh` + git, pokud je `GH_TOKEN` a sandbox má shell.** Jinak GitHub konektor (Contents API: get file → create branch → put updated content → create PR).

1. **Načti kontext repu:** `README` + soubor(y), na které `Change` ukazuje. Pokud `Change` nedává přesný soubor, projdi strukturu (root listing + pravděpodobné adresáře jako `lib/`, `app/`, `src/`, `skills/`) a najdi nejlepší místo. Nenajdeš-li jednoznačné místo → fallback issue (krok 4), neimprovizuj rozsáhle.
2. **Branch:** `tool-pr/<kebab-title>` z default branche (`main`).
3. **Změna:** drž ji **minimální a v duchu okolního kódu** (match naming/komentáře/idiom). Žádné formátovací sweepy, žádné nesouvisející soubory. Pokud realizace vyžaduje víc než ~2 soubory nebo netriviální logiku → přeruš a udělej issue místo PR.
4. **Commit message:** `<type>: <title>` (feat/fix/chore dle povahy). Tělo: 1 řádek + `Source: <newsletter URL>`.
5. **Draft PR** proti `main`:
   - Title = `Change` title.
   - Body (markdown):
     ```
     ## Co a proč
     {Insight}

     ## Změna
     {Change}

     ## Provenance
     Návrh z newsletteru: {Source}
     Backlog: {Notion page URL}
     Effort {Effort} · Confidence {Confidence} · {auto-safe ? "auto-safe" : "needs review"}

     🤖 Auto-opened by foundary-tool-pr from an approved newsletter insight. Draft — review before merge.
     ```
   - **Vždy `--draft`.** Nikdy nemerguj.
6. **Self-check před otevřením:** pokud diff vypadá, že nedělá to, co `Change` popisuje, nebo sahá na něco nečekaného → zahoď branch, udělej issue místo toho.

**Repo-specific guardraily (z memory):**
- `drippery`, `framelock` → push/PR na main = prod deploy trigger; proto **jen draft PR, nikdy ne push na main** (to tu beztak neděláme). To je OK — draft PR nemerguje.
- `dcw-cloud-skills` → public repo, žádné secrets/absolutní cesty do změn.

## Krok 4 — Fallback GitHub issue (místo PR)

Když je rozsah moc velký nebo místo změny nejasné: založ issue v `DannyRusnok/<repo>`:
- Title = `Change` title.
- Body = stejné sekce jako PR body (Co a proč / Změna / Provenance), + `(Příliš velké/nejasné na auto-PR — k ručnímu zpracování.)`
- Label `enhancement` pokud existuje (jinak bez labelu).

## Krok 5 — Update Notion řádek

Po úspěšném otevření PR/issue `notion_update_page` na daný řádek:
- `Status` → `PR opened` (pro PR) nebo nech `Approved` + poznámka pokud jen issue (volitelně přidej `Status` hodnotu `Issue` pokud ji DB má; jinak `PR opened` a do `PR` dej issue URL).
- `PR` (url) = PR nebo issue URL.

Když implementace selže (compile/struktura/cokoli) → **nech `Status = Approved`** (ať to příště zkusí nebo Daniel vyřeší ručně) a zaznamenej důvod do výstupu. Nikdy nenech řádek ve falešném "hotovo".

## Krok 6 — Telegram ping

Pokud `NOTIFY_KEY`:
```
POST https://subhook.fly.dev/api/notify?key=$NOTIFY_KEY
Content-Type: application/json
{ "title": "🔧 Foundary tool PRs — YYYY-MM-DD", "text": "{N} draft PR / {M} issue z approved backlogu.\n{seznam: repo — title — PR/issue URL}" }
```
Drž < 3900 znaků.

## Krok 7 — mem0 (volitelně)

Pokud PR řeší netriviální rozhodnutí (nová heuristika, vendor/config volba), `mem0_add` 1 věta, `metadata {project:<repo>, category:"decision"}`. Max 1 call. Běžné copy/prompt tweaky nelogovat.

## Výstup do chatu (manuální běh)

Jeden řádek: `{N} PR · {M} issue · {skipped} skipped (důvod) · backlog: <Notion url>`.

## Edge cases

- **Žádný GitHub přístup** (chybí `GH_TOKEN` i konektor): zapiš do výstupu, řádky nech `Approved`, neměň nic.
- **Repo neexistuje / přejmenované**: skip řádek, poznámka do výstupu, `Status` nech `Approved`.
- **Approved řádek bez `Repo` nebo `Change`**: skip, poznámka — neimprovizuj cílový repo.
- **Idempotence**: pokud řádek už má `PR` URL a `Status = PR opened`, přeskoč (nezakládej druhý PR). Re-run je bezpečný.
- **Rate / flood**: tvrdý strop 3 PR/běh. Víc Approved řádků → zpracuj zbytek příští běh.
