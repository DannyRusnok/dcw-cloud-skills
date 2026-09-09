# essay-to-youtube

Jedna esej týdně → jedno YouTube long-form video. Cíl: **≤90 min Danielova času** na video.

## ⚠️ IMPLEMENTACE = `~/foundary-tools/dcw-longform/compose/` (spustitelná šablona)

Tenhle skill NEIMPLEMENTUJE assembly ručně. Video se staví POUZE přes compose pipeline
(`compose/README.md` = závazný kontrakt s kroky a zafixovanými konstantami). Nové video =
nová složka `videos/<slug>/` se 4 vstupy (scenario.json, shots.json, cards.json, av.json)
+ posbírané assety. Referenční hotové video vč. všech configů: `videos/four-redraws/`
(final.mp4 = schválený vzhled — porovnávej frame-grid proti němu).

Craft konstanty (voice Daniel Slavic 2, anti-jitter zoompan, avatar 700px, amber captions,
hudba loop -18dB, texturované bg-studio pozadí, identity karta) žijí V KÓDU compose skriptů —
neopisuj je, spouštěj je. Když při stavbě narazíš na nový craft fix, zapracuj ho DO compose
skriptů (ne do textu skillu) a ověř přeběhnutím referenčního videa.

## Formát videa (fixní kostra, 8–12 min @ ~150 wpm ⇒ skript 1 300–1 700 slov)

| # | Sekce | Délka | Obraz |
|---|---|---|---|
| 1 | Cold open — hlavní číslo/kontradikce z eseje | 0:00–0:30 | Chart nebo screenshot s TÍM číslem, žádné intro, žádné "hey guys" |
| 2 | Kontext — co je experiment, můj kanál jako laboratoř | 0:30–2:00 | Kanál grid / IG profil / reálná analytika |
| 3–5 | Tělo — H2 sekce eseje = kapitoly (3–4 × ~2 min) | 2:00–8:00 | Per sekce z asset menu (níže) |
| 6 | The honest part — co nevyšlo, co jsem čekal špatně | ~1,5 min | Rozbité rendery, špatné pokusy — retention kotva |
| 6b | **Identity / medailonek (POVINNÝ)** | ~10–15 s | `card-id.png` (foto + "Daniel Rusnok / Software engineer…") — VO: "I'm Daniel. I'm a software engineer, and I built…" |
| 7 | Co z toho plyne + CTA | poslední min | End card (CTA karta, RPS paleta, **text vlevo — pravý dolní roh nechat volný pro avatara**) |

## Avatar overlay (POVINNÝ — vzor tmp/yt/shorts-26x/compose9.py)

- **Malovaný avatar** z pose library `~/foundary-tools/faceless-breakdown/poses/cut-*.png` (34 póz) se overlayuje bottom-right (`scale=-2:600, overlay=W-w-40:H-h`) na 4–6 scén (hook, context, honest part, CTA + dle obsahu).
- Pózy se přepínají na FRÁZE z ElevenLabs word timestamps (`word_time()` pattern z compose9.py); **žádná póza 2× v jednom videu**.
- Obsahové karty pod avatarem: diagramy/text posunout doleva-nahoru, pravý dolní roh volný.
- Identity karta `card-id.png` + outro vzor `card-outro.png` žijí v `tmp/yt/shorts-26x/assets/` — kopírovat, ne znovu vyrábět.
- Gotcha: Playwright `newPage` bere `viewport`, NE `viewportSize` (jinak default 1280×720 a 1920px karty se ořežou).
- Gotcha: tts.mjs merge mód (jen vybrané scény) musí APPENDOVAT nové scene id, jinak je zahodí.

## Pravidla skriptu (VO)

1. Adaptace, ne čtení eseje: mluvené věty, kratší než psané; čísla vyslovená slovy tam, kde je to přirozené.
2. Platí `dcw-voice` + humanity linter (`--platform substack` postačí) — spustit na skript PŘED generováním VO.
3. **VO musí sedět s framem** (feedback): každé vyslovené číslo/titul je v tu chvíli čitelné na obrazovce. Skript se píše ve dvou sloupcích: `[SAY]` / `[SHOW]`.
4. Žádné URL nahlas — "link in the description".
5. EN only.

## Asset menu pro [SHOW] (od nejlevnějšího)

- **Existující**: chart PNG z eseje (re-render 1920×1080 přes inline-image-render styl), GIF cover, hotové reely (Bohemia klipy jako b-roll), teaser záběry z `tmp/rpk-demo/frames-*`.
- **Screen capture**: Playwright driver pattern z `tmp/rpk-demo/driver-studio-v6.mjs` (CDP screencast → ffconcat) na RPS/dashboard/analytiku. Nový capture = nový krátký driver, testidy ne text-selektory.
- **Title cards**: HTML → screenshot v RPS paletě (`--accent #e14b4b`, `--bg #0a1220`, amber #ebc766), vzor `tmp/rpk-demo/cta/c-product.html`.
- ZÁKAZ: stock footage, generic b-roll. Všechno na obrazovce je reálný artefakt projektu.

## Workflow

0a. **Fact gate (POVINNÝ, před psaním skriptu)**: každý projekt, nástroj a číslo, které ve skriptu zazní, ověř proti realitě — `mem0_search` na stav projektu (žije / zabito / přejmenováno) a `docs/` daného repa na to, co produkt umí DNES. Nepiš popis produktu z hlavy ani ze staršího článku. Precedent: RPS bylo ve skriptu popsáno jako "pětikrokový pipeline", ve skutečnosti má pět AI rolí (scriptwriter / dramaturg / art director / voice director / ⟐ analyze & align) a pět průchodů je až render pod tím.

0b. **Přečti si tenhle soubor z disku, ne z paměti session.** V dlouhé session máš v kontextu starou kopii; skill se mezitím mohl změnit. Precedent 2026-09-09: tvrdil jsem blokátor "chybí YouTube kanál a credentials", zatímco sekce Kanál níž má obojí vypsané.

0. **Search intent gate (POVINNÝ)**: najdi konkrétní dotaz, na který video odpovídá — ověř v YouTube autocomplete + view counts top výsledků za poslední rok. Title a cold open se rámují na TEN dotaz; esej je materiál, ne obal. Když se esej na žádný hledaný dotaz nemapuje, video se NEDĚLÁ (esej zůstane esejí). Příklad: 26x esej → "why are my youtube shorts not getting views" / "instagram reels vs youtube shorts", NE esejový titul.
1. **Skript**: načti esej → dvousloupcový skript [SAY]/[SHOW] → dcw-voice pass → humanity linter → **Daniel review (gate 1, ~20 min)**.
2. **VO**: `compose/tts-vd.mjs` (NE `tts.mjs`) — Voice Director port: syntéza po VĚTÁCH + pauzy. VŽDY voice **"Daniel Slavic 2"** (`dQiqIc8lgjluOOoQMW5b`), NE starý "Daniel Slavic" (NbhHUgq5HMG0XyuWwmFg — zní hůř, pozor: je hardcoded v tmp/rpk-demo/tts.mjs). Schválené nastavení (A/B s Danielem 2026-09-08): `VD_STABILITY=0.65 VD_STYLE=0 VD_SPEED_VARY=0`. Přegenerovat jen vadné scény (`node compose/tts-vd.mjs videos/<slug> 3 5`), ne celek. Proč a detaily v `dcw-longform/compose/README.md`.
3. **Visuals**: posbírat/natočit [SHOW] položky; každá sekce = složka `sec-N/` s klipy/PNG.
4. **Assembly**: ffmpeg — per sekce ffconcat (VFR stills + klipy), VO stopa, hudba z `gen-music.mjs` na −24 dB pod VO, fade-out; end card ze CTA karty s nájezdem (vzor compose-teaser.py).
5. **Thumbnail**: varianta CTA karty s velkým číslem eseje (1280×720, text ≤4 slova).
6. **Metadata**: title = search fráze + číslo (např. "Same Videos, 26x More Views: Instagram vs YouTube Shorts"); description = 2 věty + chapters timestamps + waitlist link nahoře; pinned comment = waitlist link.
7. **Výstup**: MP4 + thumbnail + metadata.md do `tmp/yt/<slug>/` → **Daniel review (gate 2)**. Upload ručně nebo přes yt publish queue až po schválení.

## Kanál (vyřešeno 2026-08-24)

Videa jdou na YouTube kanál **Digital Craft Workshop**, id `UCBo1ccVZyTuDEqadx1XBMdg`.
OAuth refresh token: `~/foundary-tools/tmp/yt/shorts-26x/.env.dcw` (per-channel, sdílený s RPS;
Bohemia token zůstává odděleně v `histreel/.env.local` — nesahat na něj).
Publikovat jde i přes `foundary-tools/youtube-mcp` (Fly). Precedent: první video
(26x IG vs YT, 5:39) nahráno 2026-08-24 jako private → https://youtube.com/watch?v=1l8ksunO-Tw.
Bohemia Chronicles je pro tenhle obsah špatný brand — tam nic z tohohle workflow nechodí.
Druhý precedent: long-form 8:19 "Wan 2.2 on a 12GB Card" nahráno 2026-09-09 jako
**public** → https://youtu.be/EXST3-rq1CM (upload přes resumable API + `.env.dcw`,
thumbnail přes `thumbnails/set`, kapitoly z `chapters.txt` v popisu).

## Ověřovací disciplína (2026-09-09)

Chyby, které projdou přes vizuální kontrolu a Daniel je najde místo tebe:
- **Zvuk vs. titulek.** Titulek může být správně a hlas špatně. Jediný platný test je
  vytisknout payload posílaný do TTS, nebo si výsledek poslechnout. Precedent:
  `Wan 2.2` → splitter vět rozsekl "2.2" na "2." + "2" dřív než substituce, do API
  šel rozbitý text, ale caption vypadal správně (merge tokenů ho slepil zpátky).
- **Špatná instance.** Když screenshot ukazuje míň dat, než tvrdí skript (3 epizody
  proti 33 dnům denního publikování), koukáš na jinou instanci. Produkční RPS je
  `http://100.113.86.52:3030`, ne localhost.
- **Akumulovaný drift.** U karaoke porovnej reziduum na krátké i dlouhé scéně.
  Konstantní = OK, rostoucí s délkou = chyba se sčítá.
- **Hotový render rovnou otevři** (`open <cesta>`), ne jen nahlas cestu.

## Otevřené

- Burned captions: nechat YouTube auto-captions, burnovat jen klíčová čísla (ASS pipeline existuje).

## Časový rozpočet (cíl)

Skript review 20–30 min + VO poslech 10 min + visuals gaps 20–30 min + thumbnail/metadata review 10 min ≈ **60–80 min/video**. Vše ostatní automatizované.

## Vztah k dcw-longform (dedup 2026-08-30)

Tenhle skill je JEDINÝ kanonický workflow pro esej → YouTube long-form. Repo `~/foundary-tools/dcw-longform` je knihovna (research, starší pipeline skripty), NE druhý workflow — jeho README na to upozorňuje. Vzorové implementace: `tmp/yt/shorts-26x` (avatar/pose/karty) a `tmp/yt/four-redraws` (kompletní build.py + build2.py).

## Anti-jitter Ken Burns (POVINNÉ)

Zoompan na stillech: vstup supersample na 3840×2160 a AKUMULOVANÝ zoom `z='min(zoom+INC,1.05)'` (INC=0.05/frames), `x='iw/2-(iw/zoom/2)'`. NIKDY `z='1+k*on/d'` na malém vstupu — per-frame přepočet + subpixel rounding = viditelný jitter (vzor: article-forge lib/video/compose.ts).

## Post-publish distribuce

Samostatný skill `anchor-essay-distribute` (RPS epizoda v digital-craft-workshop + YT komentář + note + embed do eseje). Tenhle skill končí u MP4 draftu.

**Note s videem = nativní attachment, NIKDY jen YouTube odkaz** (Daniel, 2026-09-09).
Odkaz v note je horší dosah — Substack přehraje video přímo ve feedu. Cesta:

```
cd ~/foundary-tools/article-forge && npx tsx scripts/up-mp4.ts <mp4>   # -> R2 URL
upload_reel_video({ videoUrl, videoDurationSeconds })                  # -> jobId
get_video_upload_status({ jobId })                                     # -> attachmentId (~15 s)
publish_note({ content, attachmentId })
```
`scripts/up-mp4.ts` je jednorázový wrapper nad `uploadArticleVideo` z `lib/r2`
(upload-video.ts vyžaduje existující `article_videos` řádek, na tohle se nehodí).
Pozor: publikovanou note substack-mcp neumí smazat — pořadí kroků si rozmysli předem.

**Embed do Substack postu**: `<sub-youtube id="<videoId>"/>` a `update_post_draft`
s `republish: true` (u publikovaného postu se propíše živá verze, mail se neposílá).
Umístit ZA hook / pull quote, ne nad něj.
