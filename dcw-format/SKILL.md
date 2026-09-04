---
name: dcw-format
description: Sdílený FORMÁTOVÝ modul pro Danielovy články — rozhoduje CO a V JAKÉM OBALU se píše, ještě PŘED draftem (dcw-voice řeší JAK to zní). Jedno místo pravdy pro volbu formátu (listicle / how-to / case study s čísly / esej pod otázkou), titulek jako dotaz s čtenářem jako hrdinou, pojmenovaný framework, publikační povrch a paywall pro GEO, beat check a growth kalibraci (likes ≠ subs). Postaveno na datech z 09/2026 (Ahrefs, Semrush, Evertune, Substack Citation Index) + srovnání archivů Finn Tropy / AI Meets Girlboss / 2-Hour Blogger vs. danielrusnok. Načti tento skill VŽDY a PROAKTIVNĚ jako PRVNÍ krok kdykoli Daniel chce brainstormovat, plánovat, briefovat nebo draftovat článek / sérii / post pro Substack, Medium, dev.to nebo Hashnode — před substack-draft-from-session, article-draft-review, substack-draft-review, dcw-new-post-pipeline i před jakýmkoli "vymysli titulky" / "rozvrhni sérii" / "co mám napsat" / "brainstorm článků" / "udělej draft". Pokud brief nebo draft vzniká a tento modul v session ještě není načtený, načti ho dřív, než navrhneš první titulek.
---

# dcw-format — co psát a v jakém obalu

Sourozenec `dcw-voice`. Voice = jak to zní. Format = co to je, jak se to jmenuje, kde to leží. Review skilly (`substack-draft-review` dim 3 + 20, `article-draft-review`) sem odkazují; brief/brainstorm skilly tímhle začínají.

Výstup použití modulu = **Format Brief** (šablona dole), který jde do draftu jako vstup. Bez Format Briefu se draft nezačíná.

---

## 0. Proč to existuje (diagnóza 2026-09-04)

Danielovy posty v 08/2026: 1–5 likes u deníkových titulků ("Four Redraws of a Map It Never Looked At", "Thirty-Three Days, 41,799 Views, and €0"), 12 likes u jediného postu s konfliktem a sázkou ("A Cold DM Wanted $199. I Read 22,000 Words Instead."). Protagonista byl systém, ne čtenář; titulek byl záhada, ne slib.

Tři rychleji rostoucí Substacky ve stejné nice (Finn Tropy ~1k subs / 4,7k followers, AI Meets Girlboss 1,8k, 2-Hour Blogger 1k+; danielrusnok 257) mají shodný vzor: **tutoriály a číslované návody 3–5× engagement oproti esejím** (Finn 253/206/190 vs 114; Lidiya 495/198/143 vs 46/38/35). Finn to Danielovi napsal přímo v DM (2026-08-30): *"I built traffic by writing how-to guides and articles on how/why I built certain tools and the problems they solve."*

---

## 0.5 Project liveness check (POVINNÉ, před vším ostatním)

Než napíšeš první větu draftu, ověř přes `mem0_search` stav KAŽDÉHO Danielova projektu, který se v textu objeví: žije / zabito / pozastaveno, a od kdy.

- **Publikované starší Substack posty nejsou zdroj pravdy o současnosti.** Popisují stav v den vydání. Projekt zmíněný v postu z července může být v září mrtvý.
- Známé případy: **Reads in Motion (RiM) — zabito 2026-08-12** (rutiny vypnuté 08-10 kvůli riziku copyrightu a banu účtu). Nezmiňovat v nových postech, bio ani footeru.
- Když je projekt mrtvý, nepřepisuj jeho starou pointu do přítomného času. Buď ho z textu vyhoď, nebo napiš, že skončil a proč.

## 1. Volba formátu — vyber JEDEN primární, data rozhodují

| Formát | Kdy | Data |
|---|---|---|
| **Číslovaný / ranked list** ("7 things that break…", "Best X for Y, ranked by…") | GEO priorita, téma má ≥5 diskrétních bodů, máš vlastní čísla ke každému | Evertune 05/2026, ~400M citací: **63 % LLM citací jde na listicly, 71–86 % z nich číslované Top-N** |
| **How-to s výsledkem v titulku** | Engagement priorita, čtenář si na konci něco odnese hotové | 3 archivy výše; AirOps/Evertune: how-to "moderate" pro citace — kombinuj s čísly |
| **Case study s čísly z první ruky** ("33 days, 41,799 views, €0") | Máš unikátní měření, které nikde jinde není | Evertune: data-driven posty "earn persistent citations"; Substack Citation Index: datované primární zdroje = top signál |
| **Esej / teze** | Jen pod otázkovým titulkem a s pojmenovaným frameworkem; publikovat až po 2–3 how-to/list postech na stejné téma | Eseje = spodní kvartil engagementu ve všech třech archivech |

Pravidla:
- **Build-in-public deník není formát.** Je to surovina. Zabal ji do jednoho ze čtyř formátů výše — čísla do titulku v hranatých závorkách à la Lidiya ("July Growth Update [10 Paid Subs, 3x Traffic]"), ne jako záhadu.
- Jeden post = jeden formát. Míchání ("esej s listem uprostřed") vychází jako esej.
- Serializovaná challenge (Day 1…Day N) = **engagement/komunita**, ne GEO. Lidiyiny Day-posty 59–143 likes vs. její standalone tutorial 495. Nemíchat cíle.

## 2. Titulek = dotaz, čtenář = hrdina

Před schválením titulku odpověz na tři otázky. Jedno "ne" = přepsat.

1. **Dá se titulek vygooglit / zeptat se na něj ChatGPT jako na otázku?** ("How to…", "How much does X cost…", "Best X for Y", "7 things that…"). Deníková záhada ("Four Redraws of a Map…") = ne.
2. **Je v titulku, co si čtenář odnese?** (výsledek, číslo, nástroj, čas). "I Switched to Video Covers. My Views Doubled. This Is the 3-Step AI Workflow" ano; "Same Videos. Two Platforms." ne.
3. **Kdo je podmět?** Když je to "my AI / my pipeline / my system", přepiš tak, aby podmět byl čtenář nebo věc, kterou dostane. Danielův hook může zůstat jako subtitle nebo první věta — ne jako titulek.

Hook-titulek (záhada, konflikt) zůstává povolený pro **Notes** a subtitle. Titulek postu nese dotaz. Případ "I Tried X for 30 Days" (Stickman Matt, citovaný Googlem na dotaz, kam Daniel číselně sedí přesně) = dotazový formát s osobou uvnitř; "Thirty-Three Days, 41,799 Views, and €0" je lepší hook a horší dotaz.

## 3. Pojmenovaný framework

Substack Citation Index (4 847 citací, 213 newsletterů, 12/2025–05/2026): citace vyhrávají **named, retrievable frameworks** ("Aggregation Theory", "Napkin Math"). Bez jména LLM tezi nemá jak vytáhnout ani přiřadit autorovi.

- Každá série a každý esej-post musí mít **jednu pojmenovanou věc**: pattern, pravidlo, metriku. Jméno = 2–4 slova, Title Case, použité v titulku nebo prvním H2 a pak konzistentně v každém dílu, v notes i v SEO description.
- Definice pojmu = jeden extrahovatelný odstavec (2–3 věty, bez metafor) hned pod prvním výskytem.
- Příklad pro RPS: tři invarianty (slate → tip → klik; zdarma analýza před placeným generováním; pravomoc ohraničená i mezi rolemi) potřebují jméno dřív, než se napíše první díl.

## 4. Povrch a paywall (GEO)

Fakta 09/2026:
- **Google AI Overviews / AI Mode: 76 % citací jde z organického top-10** (Ahrefs, 15k dotazů). S pozicí ~24 na Substacku tam formát nepomůže. Neměř GEO baseline na AI Mode.
- **ChatGPT / Perplexity: překryv s top-10 jen 6–8 % / 29 %** (Ahrefs). Tady autorita domény nehraje — tohle je Danielův GEO povrch. Baseline měřit tam.
- **Medium je top-5 citovaná doména na ChatGPT; Substack není v top 25 na žádné platformě** (Semrush, 230k promptů). Substack robots.txt AI crawlery neblokuje, takže je *přístupný*, ne *preferovaný*.
- **YouTube = #1 citovaná doména v AI Overviews (20,9 %)**. Případ s čísly, který má videový ekvivalent, patří i na Danielův kanál.
- **Paywalled newslettery "consistently underperform" v citacích bez ohledu na velikost** (Substack Citation Index).

Pravidla:
- Pořadí publikace se nemění: Substack → Medium cross-post s canonicalem na Substack (čistá URL, bez `?r=`). "Medium first" = *GEO priorita*, ne časová.
- GEO-cílené posty na Medium **plnotextově, bez member-only paywallu, do 48 h od Substacku**. Nezkracovat.
- GEO-cílené série na Substacku **free**, ne paid.
- Odkazy z Medium/dev.to na Substack jsou `nofollow ugc` — jsou pro lidi (referral), ne pro autoritu. Dofollow zdroje: Hashnode, GitHub README, cizí Substacky (AI vs Author collab), vlastní doména až bude.

## 5. Beat check

Substack Citation Index: engines "route by who owns the topic" — jeden beat držený roky. Danielův beat: **automatizovaná video produkce z textu (Substack → reel → YouTube), stavěná solo vedle full-time práce**.

- SEO title + první odstavec každého postu musí být zařaditelný do tohoto beatu na první pohled. Posty mimo beat (Games That Shaped Me, Membership) zůstávají, ale nedostávají GEO investici.
- Entity anchor v každém postu: kdo píše a proč má data ("solo dev running an automated faceless channel for 8 months"), ne "software engineer".

## 6. Growth kalibrace — co formát umí a co ne

- **Likes na postech ≠ subs.** AI Meets Girlboss připisuje skok 64→200 za 2 týdny vizuálnímu rebrandu a 13 collab postům, ne titulkům. 40 % nových subs na Substacku jde ze sítě; u early-stage publikací údajně >90 % z Notes (jeden zdroj, ber s rezervou).
- Formát postu tedy mění: (a) co se stane, když někdo z Note klikne, (b) citovatelnost. Nemění přímo akvizici — ta zůstává na Notes, recommendations a collabech.
- Neslibuj v briefu "tenhle formát zvedne subs". Slibuj open/like/restack a citaci.

## 7. Prázdná citace ≠ poptávka

Nula citací v AI odpovědi na konkrétní formulaci může znamenat nulovou poptávku, ne mezeru. Před investicí do "gap" postu ověř, že sousední formulace mají existující obsah (YouTube, Reddit, Gumroad šablony). Když ano, mezera je reálná; když je ticho i kolem, nejdřív dotaz, který lidé prokazatelně kladou, a Danielova unikátní data jako odpověď.

---

## Format Brief (šablona — výstup tohoto modulu)

```
FORMAT BRIEF
Téma:            <1 věta>
Formát:          listicle | how-to | case-study | esej-pod-otázkou
Titulek (dotaz): <…>
Co si odnese:    <výsledek/číslo/nástroj v titulku>
Podmět titulku:  čtenář | věc, kterou dostane   (NE "my AI")
Framework:       <Jméno Patternu> — definice 2–3 věty
Čísla z 1. ruky: <seznam>
Beat anchor:     <1 věta entity anchor>
Povrch:          Substack (free) → Medium plnotext ≤48h | + YouTube video? ano/ne
GEO cíl:         ChatGPT/Perplexity dotaz: "<…>"
Cíl metriky:     open/like/restack/citace   (ne subs)
```

## Zdroje (načteno 2026-09-04)

- Ahrefs, AI search overlap, 15 000 dotazů: https://ahrefs.com/blog/ai-search-overlap/
- Semrush, most-cited domains, 230k promptů: https://www.semrush.com/blog/most-cited-domains-ai/
- Evertune, ~400M citací, listicly 63 %: https://www.evertune.ai/resources/ai-search-statistics-for-generative-engine-optimization
- AirOps, content types for AEO: https://www.airops.com/blog/aeo-content-types
- Substack Citation Index 2026: https://everything-pr.com/the-substack-citation-index-2026
- AI Overviews source index (YouTube 20,9 %): https://everything-pr.com/google-ai-overviews-citation-source-index-2026
- AI Meets Girlboss, 0→450 za 90 dní: https://aimeetsgirlboss.substack.com/p/from-0-to-450-subscribers-in-90-days
- Archivy: https://finntropy.substack.com/archive?sort=top · https://aimeetsgirlboss.substack.com/archive?sort=top · https://2hourblogger.substack.com/archive?sort=top
- Finn Tropy DM 2026-08-30, thread 3426d147-4d7c-4713-b9e3-a41b4d8f30b0
