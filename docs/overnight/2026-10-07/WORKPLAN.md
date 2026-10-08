# Nattplan för OpenVRX, 7–8 oktober 2026

Nattpasset är avslutat före **2026-10-08 08:00 Europe/Stockholm (06:00 UTC)**.
R08 är komplett och automationen är PAUSED. Core `fb6896a` och Puck `8917d27`
är pushade till main, navets slutrapport/evidence i `0865e80`. Fryst
`aece6eb` gav 432 passed, 2 xfailed och oförändrade 171 källhashar; slutlig
Core skiljer bara i tre Markdown-filer. Planen började på `7cc4eda` och
Opus historia till `059aadd` är bevarad. R05 är uppskjutet och R07:s
ägarbeslut samt OVN-F1 är öppna. Allt är simulerat eller byggt; inget har
körts på hårdvara. Se [slutrapporten](FINAL_REPORT.md).

## Granskningsbeslut under körningen

- `cb2c10f`: density/fields behövs för riktade uppspelningar; density 1,0 har samma scenarier på sex representativa frön som basversionen.
- `3ad2c2b`: avvisad. Frö 126 har synlig RGB i BUF före första publicerade fältet. Varje SDRAM-läsnings checksumma ska fortfarande kontrolleras, även utan efterföljande bildbeslut. Se [OVN-F1](LOW_BUF_FINDING.md).
- `ec06c56`: modellens observationslista och minimala #18-scenario används. Root avgränsar xfail till den exakta omarkerade fältstarten; andra modell-/bänkfel ska falla.
- `154f41b`: radantal mäts av bänken för PAL-bilder med blandad radlängd. Små positiva och negativa gränsfall behåller V_TOTAL/MAX_WAIT/HOLD-reglerna.
- Fjärrens senare åldersklassificeringar bevaras som Opus arbete, men generatorns försprång får bara undanta kameraålder, inte fältminnets egen ålder. För liten bildtäckning ska fortfarande vara ett benchfel även vid lägesbyte.
- R05:s breda nya kampanj skjuts upp för att undvika dubbelarbete. R06 använder ett nytt kontrakt, frö 49 och åtta fält i full PAL/LOW-geometri.

## Nuläge och bevisvärde

| Repo | `main` vid start | Status och notering |
|---|---|---|
| OpenVRX | `4d43600` | Ren efter fast-forward; navets nattinstruktioner finns. |
| OpenVRX-Core | `7cc4eda` | Ren efter fast-forward. Senaste ändringen rättar mixerparning när en kanal saknar en rad i det aktuella utfältet. |
| OpenVRX-Puck | `9d2fb57` | Ren; `core/` är detached på `82c4134`, äldre än Core `main`. Root äger eventuell uppdatering. |

Verktygen finns i Core-trädet på denna Linuxvärd (`.venv` och `.tools/iverilog/bin`). WSL-raderna i äldre nattinstruktioner gäller en annan dator. Inget kort finns för hårdvaruverifiering.

Den frysta baslinjen på `7cc4eda` är klar: **395 passed, 1 xfailed på 1:25:56**, totalt 396 test. Xfail gäller Core #17. Den äldre överlämningens 394 var inaktuellt. README-byggtabellen vid start angav M4 från `2a23e05` och M6 från `330cc9a`; root bygger därför om båda efter senaste mixerfixen, ett i taget. Aktuella resultat finns i `STATUS.md` och evidence.

Vid planstart redovisade `gateware/sim/FUZZ_2026-10-07.md` på `main` r1, r2, e0 och e1. Då innehöll fjärrgrenen `origin/fuzz/chain-2026-10-07` senare material som då **inte** ingick i `main`: `cb2c10f` lägger till `density`/`fields`, och `3ad2c2b` ändrar hur checksumfel kopplas till den rad som faktiskt visas. Grenens rapportering nämner r3, d1, f1 och ett d2-fynd. Det är underlag för separat granskning och riktad reproduktion, inte godkännande att merga eller cherry-picka.

Användarens redan körande Vibe-session har lämnat `VIBE_REPORT.md` och ändrat navets två dokumentationsfiler. Root granskar dem före commit. Codex extra CLI-anrop misslyckades före arbete; det säger inget om den befintliga sessionens autentisering. Codex ska inte starta eller styra Vibe. Luna på max sparade denna plan och tasklistan innan ett kreditfel avbröt agenten; root slutför granskning och genomförande utan ny provider eller köpta credits.

## Prioritering och kända risker

1. Behåll en sann körjournal. Baslinjen och byggverifieringen efter senaste Core-ändringen väger tyngre än fler slumpfrön.
2. Förbättra kampanjens resumning innan en ny lång körning. Vid start hoppade `fuzz_campaign.py` över poster efter `key`/frö utan att kontrollera geometri, störningsklasser, densitet, fältantal eller exakt källkod. Samma round-namn kunde därför ge falsk färdigstatus med andra indata. R02 rättar detta.
3. Granska branchskillnader separat, och spela om bara relevanta frön på `main`. Kör inte om gamla hela rundor om en agent redan utför samma runda.
4. Bekräfta att den senaste parningsfixen har symmetrisk täckning och aktuella M4/M6-byggen.
5. Lägg eventuell återstående nattid på riktad tätare fuzz och en PAL/LOW-körning med full geometri. Stoppa vid för litet återstående tidsfönster.

| Prioritet | Risk eller lucka | Belägg och gräns |
|---|---|---|
| P0 | Falsk återupptagning av fuzzrundor | `gateware/sim/fuzz_campaign.py:44-47` använder bara `key`/frö i `done`; `:99-117` tar parametrar men sparar inte körkontraktet. Olika geometri, density, fields, classes, force eller RTL kan därför återanvända gamla resultat. |
| P1 | LOW→BUF kan visa innehåll före första publicerade fältet | Frö 126 och observationskörningen motbevisar grenens antagande om en bild utan video. Alla 72 aktiva RGB-prov avviker från blankbilden. Strikt checksumkontroll behålls; RTL-fynd och framtida rättningspaket finns i `LOW_BUF_FINDING.md`. |
| P1 | LOW visar video innan genlock/ring är redo efter BUF→LOW | 14 av 18 riktade switchfrön rapporteras i `gateware/sim/FUZZ_2026-10-07.md:33`; `fb_display.v:87-94` väljer `have_video` ur `ll_alive`, och `fb_backend.v:193-200` räknar livstecken från triggern. Core #17 är öppet. Detta kräver ett tydligt beteendekontrakt; ingen tyst policyändring. |
| P1 | En ny mixerfältstart syns inte nedströms om F och radnummer inte markerar den | Core #18 är öppet. Reproduktionen i ec06c56 granskas separat: modellens observationslista får tas in utan regeländring och xfail måste avgränsas till just den kända fältmarkeringen. Ingen ålderskontroll försvagas. |
| P1 | Senaste mixerfixen saknar spegeltest för B som återvänder | `line_mixer.v:156-162` byter domarkanal med `c_alt`. `test_mixer.py:532-551` testar A:s återkomst och dess gamla RTL-kontroll; ingen motsvarande B-följd syns i testerna. Det är en täckningslucka, inte ett observerat nytt RTL-fel. |
| P1 | Full geometri och PAL i LOW är svagt belagt på `main` | Huvudloggen beskriver skalad geometri. `fuzz_stream.py:17-25` säger att PAL+LOW kan köras i full geometri; `test_fuzz_chain.py:38-45` uppskattar cirka sju minuter per standardfrö. Branchens f1 har åtta frön och en `bench/few_lines`-avvikelse; det visar inte i sig att PAL LOW har verifierats. |
| P2 | Fuzzresultatens historik skiljer sig mellan `main` och nattgrenen | Granskad diff omfattar `cb2c10f` och `3ad2c2b`; rapporterade r3/d1/f1/d2-resultat är inte automatiskt belägg för `7cc4eda`. D1/48 är redan åtgärdat av pair-join-fixen; d2/126 gäller testets rad-/visningskoppling. |
| P2 | Formella CDC-bevis omfattar inte alla verkliga förhållanden | `gateware/formal/README.md:12` utesluter reset mitt i drift; `:36-38` lämnar timingmarginal för nivåer, SDRAM-radskrivning och LOW-ringen utanför beviset. Simulering kan minska osäkerhet, men ersätter inte hårdvarumätning. |
| P2 | Senaste brus-, låsförlust- och fältfasbeteenden saknar signalverifiering | `gateware/README.md:302` säger att brusmåttets förmåga att skilja signal från bildinnehåll är oprövad på riktig signal; M6-låsflaggan och `field_phase` är också bara simulerade. |
| P3 | En dubbeldålig utelämnad sista rad kan korta fältets radantal | Navets `docs/ARBETSPLAN_2026-10-05.md:129` beskriver fält på 242 i stället för 243 rader i två fält. Det är en följd av den uttryckliga mixerregeln och får inte ändras utan separat ägarbeslut. |

## Körregler och återupptagning

- Läs `COORDINATION.md`, `tasks.json`, `STATUS.md` om root hunnit skapa den och aktuell `git status` före varje paket. Bekräfta levande processer och låset innan ett tungt jobb.
- Högst ett tungt test- eller byggjobb åt gången, mellan alla tre repona. Kör det under `flock /home/lenny/openvrx-review/build.lock <kommando>`. Rootens pågående baslinje har företräde.
- Använd en ny round-identitet för varje kombination av geometri, density, fältantal, klasser, force och källversion. Nuvarande runner kan annars hoppa över frön med fel kontrakt. Bevara äldre JSONL och misslyckade simkataloger.
- Ingen parallell fuzz från två arbetare. Kontrollera status innan en runda; om samma fröintervall och kontrakt redan körs, invänta det och läs resultatet i stället för att starta en kopia. Vibe är tilldelad dokumentation och kör inga tunga jobb.
- Ändringar ska vara lokala. Vid RTL-fel ändras modellen först eller samtidigt, sedan riktat regressionstest, meningsfull negativ kontroll, relevanta tester och M4/M6-bygge för den ändrade vägen. Mixer/fältminnes-RTL berör M4 och M6; M6 UI/dekoderlogik berör M6. Inga stora omskrivningar.
- Stoppa ett paket när orsaken är oklar, resultatet kräver nytt beteendekontrakt, eller tidsmarginalen inte räcker för acceptance. Dokumentera reproduktion och vad som återstår. Ingen Git-reset eller stash av någon annans ändringar. Root återställer enbart egna commits med `git revert` om en revert behövs; ingen reset mot tidigare nattgrenar.
- Alla tester och simloggar sparas med revision, kommando, kontrakt, första avvikelse, status samt körningstid. Root äger slutlig Git-status, commits, push, dokumentationsstatus och Puck-submoduleuppdatering.

## Paket i ordning

### R00 — fryst baslinje och startgrind

**Ägare:** Codex/root. **Status:** klart, 395 passed och 1 väntat xfail. **Filer:** fryst arkiv `private/notes/overnight_2026-10-07/baseline-core-7cc4eda/`; rootens `docs/overnight/2026-10-07/STATUS.md` och evidence.

Root kör den frysta Core-sviten och låter processen slutföras innan nästa tungt jobb. Baslinjen ska knytas till `7cc4eda`, spara rå utdata och avgöra om 396 test faktiskt samlades och passerade. Om sviten misslyckas ska första avvikelsen ringas in före ändringar; inga beroenden eller verktyg installeras på chans.

**Acceptance:** revision och renhetsstatus framgår av evidence; rå pytest-returkod, samlat/passerat/xfail/skip-antal och varaktighet finns; låset är släppt. Om räkningen är 394 eller 396 ska avvikelsen mot README uttryckligen anges.

**Checkpoint/rollback:** fryst arkiv lämnas orört. Vid avbruten körning spara logg och exakt kommando, och fortsätt först efter att process/lås kontrollerats. Inga filer återställs.

### R01 — navets dokumentationsgranskning

**Ägare:** användarens Mistral Vibe CLI för utkast, Codex/root för slutgranskning. **Status:** rapport och utkast överlämnade; root granskar. **Filer:** endast `OpenVRX/REVIEW.md`, `OpenVRX/AGENTS.md` och `OpenVRX/docs/overnight/2026-10-07/VIBE_REPORT.md`.

Granska att navets status och gamla kända-fel-listor skiljer dagens `main` från äldre underlag. Skriv öppet om Core #17 och #18; märk grenens tester och resultat som grenuppgifter tills de har reproducerats på `main`. Rätta för starka påståenden om brusmått, SDRAM och formella bevis. Ändra inga BOM- eller hårdvarubeslut.

**Acceptance:** rapport och dokument finns, root har granskat påståendena mot koden och körjournalen. #18-testet ska tydligt beskrivas som ännu bara på nattgrenen. Vibes historiska rapport bevaras med datum och attribution.

**Återupptagning:** läs rapporten och aktuellt filägarskap. Starta ingen Vibe-process; root granskar det överlämnade utkastet.

### R02 — strikt kontrakt för fuzz-resumning

**Ägare:** Codex/root. **Status:** 28 små kontraktstest samt riktig process-pool-körning/resume är klara; hela integrationssviten körs i R08. **Filer:** `OpenVRX-Core/gateware/sim/fuzz_campaign.py` och nytt riktat test `OpenVRX-Core/gateware/sim/test_fuzz_campaign.py`.

Ändra inte bildlogik. Spara ett kanoniskt körkontrakt intill round-JSONL: geometry, density, fields, classes, force samt Core-revision och hash för relevanta RTL-, bench- och modellfiler. Resumning med samma kontrakt ska hoppa över färdiga seeds och fortsätta återstående; återanvändning med annat kontrakt ska avvisas före skrivning eller simstart med tydlig instruktion att skapa ett nytt round-namn. Äldre JSONL utan kontrakt får sammanfattas men inte återupptas som verifierade. De saknar det ursprungliga kontraktet; skriv inte över dem.

**Acceptance:** små enhetstester visar att samma kontrakt bara kör saknade nycklar. Ändrad `geometry`, `density`, `fields`, `classes`, `force`, källhash eller simulator avvisas före arbetaren och lämnar resultatevidence orörd. Äldre loggar kan sammanfattas men inte återupptas. Lås, ändring under körning och budget för full geometri provas med arbetardubblar; testerna simulerar ingen RTL.

**Kommando:** `.venv/bin/python -m pytest -q gateware/sim/test_fuzz_campaign.py`

**Checkpoint/rollback:** behåll äldre JSONL och manifest. Gissa inte deras körinställningar. Vid ändrat kontrakt används nytt rundnamn; `narrow --round NAME` ger samma möjlighet för reduktionskörningar.

### R03 — granskning av nattgrenens ändringar och riktad reproduktion

**Ägare:** Codex/root. **Depends on:** R00. **Filer:** läs-only jämförelse av `OpenVRX-Core/gateware/model/fuzz_stream.py`, `gateware/sim/fuzz_campaign.py`, `gateware/sim/test_fuzz_chain.py`, `gateware/sim/FUZZ_2026-10-07.md`; eventuell ändring får bara ske i de enskilt motiverade filerna efter reproduktion.

Granska diffen `main..origin/fuzz/chain-2026-10-07` commit för commit, särskilt `cb2c10f` och `3ad2c2b`. Byt inte till grenen och merga/cherry-picka inte paketet som helhet. Efter R00:s låsfria checkpoint körs först d1-frö 48 på `main` för att bekräfta den redan inlagda pair-join-fixen. Kör d2-frö 126 separat för att fastställa om nuvarande checksumkontroll fäller på en icke visad rad. Använd unika arbetskataloger och unika resultatrundor. Om ett annat jobb har samma seed/kontrakt, läs dess resultat i stället.

**Kör seedarna var för sig under flock.** Använd en ny, ännu ej existerande katalog för varje seed; `test_chain_seed` utan egen work-path använder standardkatalogen `build/fuzz/seed<id>` och den tas bort före körning.

```sh
flock /home/lenny/openvrx-review/build.lock .venv/bin/python - <<'PY'
import json
from pathlib import Path
from gateware.sim.test_fuzz_chain import run_seed
work = Path('gateware/sim/build/fuzz/overnight-main-pair-join-48')
assert not work.exists(), work
print(json.dumps(run_seed(48, work=work, keep=True, density=2.5)))
PY
flock /home/lenny/openvrx-review/build.lock .venv/bin/python - <<'PY'
import json
from pathlib import Path
from gateware.sim.test_fuzz_chain import run_seed
work = Path('gateware/sim/build/fuzz/overnight-main-read-check-126')
assert not work.exists(), work
print(json.dumps(run_seed(126, work=work, keep=True, density=2.5)))
PY
```

**Acceptance och utfall:** seed 48 matchar RTL och modell på `7cc4eda` (648 rader). Seed 126 har en checksumavvikelse före första BUF-beslutet och synlig RGB innan publicerat fält. `3ad2c2b` avvisas; resultatet med det experimentella oraklet sparas som experiment, inte godkänd grön verifiering. Befintlig negativ displaykontroll fälls fortfarande. Branchens rundresultat tillskrivs sina egna orakelversioner.

**Villkorat:** density/fields-funktionerna i `cb2c10f` tas bara in om de behövs för riktade körningar efter egen granskning. För density 1 ska representativa seedscenarier och klassurval vara identiska med basversionen. För olika round-kontrakt ska R02 avvisa resumning. Annars lämnas ändringarna på nattgrenen.

### R04 — parets domarkanal i båda riktningarna och aktuella byggen

**Ägare:** Codex/root. **Depends on:** R00. **Filer:** `OpenVRX-Core/gateware/rtl/line_mixer.v`, `gateware/model/line_mixer_ref.py`, `gateware/sim/test_mixer.py`, samt vid behov `gateware/README.md`.

Kör befintligt positivt test `test_returning_channel_starts_the_next_field` och dess negativa kontroll. Lägg till spegeltest där B saknar rader i ett utfält, A bär fältet och B sedan återvänder som vald kanal. Jämför varje beslut och utord med modellen; negativ kontroll ska tvinga tillbaka den gamla bedömningen som bara använder aktuell kanal och då avvika. Låt regler om fältstart, F-bit och dubbeldålig rad vara oförändrade. Modellens nya `newfield`-lista är endast observation för R07, från ec06c56; ingen modellregel eller RTL ändras.

**Riktade tester:**

```sh
flock /home/lenny/openvrx-review/build.lock .venv/bin/python -m pytest -q gateware/sim/test_mixer.py::test_returning_channel_starts_the_next_field gateware/sim/test_mixer.py::test_returning_channel_check_is_tested
flock /home/lenny/openvrx-review/build.lock .venv/bin/python -m pytest -q gateware/sim/test_mixer.py
```

Bygg M4 och M6 från ändringen, ett bygge i taget, och verifiera färsk manifest/PNR-logg utan `ERROR`. M6 innehåller samma mixer och kan inte åberopa README:s äldre M6-build som verifiering av pair-join-ändringen.

**Acceptance:** A- och B-återkomstfallen går igenom, negativa kontroller faller av rätt beslut, RTL/modell matchar, riktad mixerfil är grön och båda berörda byggen kommer från den granskade källrevisionen. Om ny RTL-rättning behövs gäller modell-först och root väljer exakt filägarskap; ingen samtidig edit.

### R05 — selektiv tät fuzz på `main`

**Ägare:** Codex/root. **Depends on:** R02 och R03. **Filer:** `OpenVRX-Core/gateware/sim/fuzz_campaign.py`, kontraktsmanifest och endast den nya roundens JSONL/workkataloger.

Starta inte om gamla rundor för totalsiffran. Nattgrenen fortsatte till `6f45f1a` vid kontroll 04:02 och har fler densitetsrundor än planutkastet kände till. R05 skjuts därför upp för att undvika överlappning. Exemplet nedan får bara användas efter en ny jämförelse som visar att intervallet och kontraktet inte redan ägs av Opus. Riktade reproduktionsfrön i R03 har företräde.

```sh
flock /home/lenny/openvrx-review/build.lock .venv/bin/python gateware/sim/fuzz_campaign.py run overnight-density25-s50-99-main-7cc4eda 50-99 --density 2.5 --fields 10 --jobs 1 --budget 540
flock /home/lenny/openvrx-review/build.lock .venv/bin/python gateware/sim/fuzz_campaign.py summary overnight-density25-s50-99-main-7cc4eda
```

Kör dessa rader bara om de granskade flaggorna finns på `main`, kontraktet fungerar och ingen annan kör samma seeds/kontrakt. Om ändringen inte tas in ersätts inte det med en hel 50-seedsrunda; spara tiden eller kör ett enda reproduktionsfrö med godkänt kontrakt.

**Acceptance:** varje JSONL-resultat anger rätt revisions- och run-kontrakt, alla startade frön har en slutstatus, första avvikelse har triagerats, och kampanjen gick inte samtidigt med annan tung körning. Pausläge går att återuppta med identiskt kontrakt.

### R06 — PAL/LOW med full bildgeometri

**Ägare:** Codex/root. **Depends on:** R02, R03. **Filer:** ny round och workkatalog under `OpenVRX-Core/gateware/sim/build/fuzz/`; endast om fel uppstår får motsvarande test/model/RTL-filer öppnas för ett separat avgränsat paket.

Gör en riktad fullgeometrikörning som tvingar PAL och lägesbyte till LOW. Frö 49 väljs framför 17: bytet kommer efter 34,68 ms och lämnar cirka 108 ms i LOW, så fler hela LOW-bilder hinner observeras. Kör minst 8 fält så att byte/start inte förbrukar nästan hela det observerbara fönstret. I denna branch `run_seed` tar `n_fields` direkt om CLI-flaggan `--fields` inte har godkänts; använd unik work-katalog som inte finns sedan tidigare. Ett 4-fältsfrö i full geometri är uppskattat till cirka 7 minuter; 8 fält kan ta runt 14 minuter.

Om CLI-stödet fortfarande saknas, använd:

```sh
flock /home/lenny/openvrx-review/build.lock .venv/bin/python - <<'PY'
from pathlib import Path
from gateware.sim.test_fuzz_chain import run_seed
r = run_seed(49, ['pal', 'mode_switch'], force=('pal', 'mode_switch'), geometry='full', n_fields=8,
             keep=True,
             work=Path('gateware/sim/build/fuzz/overnight-pal-low-full-20261008'))
print(r)
PY
```

Verifiera att scenariot faktiskt är PAL, att LOW förekommer och att minst två hela utbilder har kontrollerats. `bench/few_lines` ska leda till fler fält eller klassjustering, aldrig till att kontrollgränsen sänks. Fynd som faller inom #17 rapporteras som kända med orsak, inte som oberoende grönt.

**Acceptance:** sammanhängande JSON-resultat med geometri, fältantal, påtvingade störningar, `checked`-antal, kända #17-händelser och första avvikelse; inga okända benchfel förklaras bort. Börja inte om mindre än 25 minuter före stopptid.

### R07 — Core #17, diagnostik utan policyändring

**Ägare:** Codex/root för diagnostik; beteendebeslut ligger hos projektägaren. **Depends on:** R00, R03. **Filer:** `OpenVRX-Core/gateware/sim/test_fb.py`, `gateware/sim/test_fuzz_chain.py`, `gateware/sim/FUZZ_2026-10-07.md`; RTL får endast ändras efter att ett beteendebeslut och lokal orsak finns.

Det riktade #17-scenariot ingick i den frysta baslinjen och ska inte dubbleras enbart för räkningen. #17 och #18 är bekräftat OPEN. Granska och ta vid godkänd simulering in Opus lilla #18-reproduktion och modellens observationslista från ec06c56. Xfail ska bara acceptera den särskilda avvikelsen `UnmarkedOutputField`; modell-, bänk- och overflowfel ska fortfarande fälla. Importera inte grenens bredare åldersklassificering utan separat belägg. Paketet får inte välja nytt beteendekontrakt för `have_video`, genlock eller mixerns F-bit.

**Acceptance:** xfailen visar den kända avvikelsen på nytt med reproduktionsdata, eller motbevisas med rätt revision och testbevis; inga andra fel göms i bred `xfail`. Om ägarbeslut saknas vid stopptid lämnas #17 öppet och tydligt blockerat.

### R08 — stoppgrind och handoff

**Ägare:** Codex/root. **Depends on:** R00–R07 där R07 får stängas som blockerad. **Filer:** rootens `STATUS.md` och evidence; relevanta Core README/loggfiler bara om de sakligt behöver uppdateras. Root äger Git, commits, push och eventuell Puck-submoduleuppdatering.

Root granskar egna diffar, alla claims mot rå evidence och Vibe-rapporten om den finns; kör lämplig slutkontroll efter kodändring. Vid varje RTL-fix ska modell, negativ kontroll, riktad sim och M4/M6-buildresultat namnges. Om sista kompletta test/buildgate inte ryms före stopptiden ska ändringen lämnas utan merge/push enligt rootens beslut; tidsgränsen flyttas inte.

**Definition of done:** (1) rootens status visar exakt Core-revision och om arbetsträdet är rent/smutsigt; (2) aktuell baslinjeräkning kommer från fryst körning; (3) inga branch-only results tillskrivs `main` utan reproduktion; (4) test- eller RTL-ändringar har angivna acceptance-bevis; (5) pair-join-fixens M4/M6-buildgrind är passerad om testpaketet accepteras; (6) #17, hårdvarublockerare och ägarbeslut kvarstår öppet där de ska; (7) alla pågående processer avslutas eller lämnas med exakt checkpoint före 08:00; (8) inga nya paket startas efter stopptiden.

**Rollback:** återställ endast egna incheckade ändringar med `git revert` och granska revert-diffen. Återställ inte andras filer för att försöka "städa". Om något eget behöver tas tillbaka, gör en ny commit som bara återställer den egna ändringen. Kör aldrig `reset --hard`, `git clean` eller `stash` i den delade arbetskopian.

## Kopierbart uppdrag för fortsatt arbete

```text
Fortsätt OpenVRX-nattplanen till 2026-10-08 08:00 Europe/Stockholm. Läs COORDINATION.md, STATUS.md och tasks.json före varje paket. Arbeta på main; root äger granskning, verifiering, Git och push. Luna på max har lämnat planen men avbröts av kreditfel: gör inga automatiska omförsök eller providerbyten. Användarens Vibe-session arbetar självständigt; starta eller styr den inte. Ett tungt sim- eller byggjobb åt gången under /home/lenny/openvrx-review/build.lock. Återanvänd inte resultat med ändrade källor eller inställningar. Reproducera relevanta frön och kontrollera pair-join med modell, negativ kontroll och aktuella M4/M6-byggen. Rätta lokal RTL bara med belägg och berörda acceptanstester. Ändra inte bildlägen, IOB, SDC, stift, licens eller BOM. Lämna #17 och #18 utan ny beteendepolicy. Starta inga paket efter 08:00; spara checkpoint, slutrapport och avsluta automationen. Påstå ingen hårdvaruverifiering och använd inte reset/stash/force-push.
```

## Små, färdiga Luna-prompter

Dessa är överlämningsprompter för avgränsade paket; de aktiverar inte arbetet här. Luna sparade planfilerna före kreditfelet; root har nu tagit över deras granskning och uppdatering enligt `COORDINATION.md`. Inga nya agentförsök startas.

**R02 — kampanjkontrakt:**

```text
Granska bara OpenVRX-Core/gateware/sim/fuzz_campaign.py. Lägg till strict resume-provenance för geometry, density, fields, classes, force, Core-revision och hash för RTL/bench/model-indata. Samma kontrakt ska resume:a och bara starta saknade keys; ändrat kontrakt eller gammal JSONL utan manifest ska avvisas före simstart och före filändring. Äg bara fuzz_campaign.py och nytt test_fuzz_campaign.py. Lägg till små tester för samma/olika kontrakt och oförändrad fil vid avvisning. Kör endast .venv/bin/python -m pytest -q gateware/sim/test_fuzz_campaign.py. Bevara befintliga JSONL. Ingen Icarus, bygg, Git-mutation eller broad refactor. Om ägarskap inte har överförts av root, rapportera patchplan i stället för att editera.
```

**R03 — nattgrenskillnader:**

```text
Utgå från OpenVRX-Core main 7cc4eda. Läs diffen mot origin/fuzz/chain-2026-10-07, särskilt cb2c10f och 3ad2c2b; merga eller cherry-picka inte. Efter att root gett arbetskopian, spela endast seed 48 och 126 på main under gemensamt flock, en åt gången, och rapportera första avvikelse med om raden faktiskt visades. Ändra ingen RTL om inte lokal orsak är bevisad. Om testoraklet ändras, bevara kontrollen att en visad felrad fortfarande fälls. Använd ny round/work-path. Inga parallella fuzzjobb. Om ägarskap saknas, lämna endast en read-only rapport.
```

**R04 — spegelvänd pair-join:**

```text
Läs line_mixer.v, line_mixer_ref.py och sim/test_mixer.py på main. Lägg till bara ett symmetriskt B-returnerar-test för senaste pair-join-fixen, model-vs-RTL på varje beslut/utord och en negativ kontroll med gammal domarkanal. Låt fält/F/dubbeldålig-regler vara oförändrade. Om RTL visar motexempel: modell först och minimal RTL-rättning; kör riktade mixersim och berörda M4 plus M6-build under flock. Skriv exakt första felet; ingen bred refactor eller Git-mutation. Vänta på rootens ägarskap om filerna inte har överförts.
```

**R06 — full PAL/LOW:**

```text
Kör en enda riktad fullgeometrisim på main, PAL+mode_switch, minst 8 fält. Kontrollera att LOW verkligen förekommer och att minst två hela utbilder räknas; om bench/few_lines uppstår, öka fält eller förbättra exakt testgräns utan att sänka invarianten. Använd unik round/work-path och samma låskontrakt, flock, inga parallella jobb. Ingen RTL-ändring utan lokal reproduktion, modell, negativ kontroll, riktat sim och berörda M4/M6-builds. Spara stderr/JSONL och första avvikelse. Starta inte om mindre än 25 minuter före stopptid. Ändra inte #17-regeln utan ägarbeslut.
```

## Checkpoint inför slutgrinden, 2026-10-08 06:03

R00–R04 och R06:s verifierbara del är klara. PAL/LOW full geometri
kontrollerade fyra hela LOW-bilder och 2 880 rader, bara känt #17.
R03:s integrerade kontroll hittar fortfarande seed 126:s `store/read`;
frö 48 är grönt med 648 rader. R05 är avsiktligt uppskjutet och #17/#18
samt OVN-F1 ligger kvar som dokumenterade beteendefrågor/fynd.

R08 kör hela sviten från fryst Core `aece6eb` (434 insamlade test), en
process under låset. Vänta på slutresultat och oförändrade källhashar.
Pusha sedan granskad Core main, flytta en ren Puck-gitlänk till den
accepterade revisionen, kör Puck-testet och pusha dess main. Uppdatera
slutresultat i navet, granska/checka in endast ägda filer och pusha.
Om sviten faller, spara första avvikelsen och triagera före kodpush.
Avsluta automationen efter acceptance eller vid 08:00. Starta inget nytt
paket efter stopptiden; runnern avbryter sin egen grupp vid 07:58 om nödvändigt.

## Slutacceptance, 2026-10-08 07:43

Fryst `aece6eb`: 432 passed, 2 xfailed (#17/#18), returstatus 0;
alla 171 källhashar oförändrade. Core `fb6896a` och Puck `8917d27` är
pushade till main. Core skiljer bara i tre Markdown-filer från den testade
revisionen; Pucks kontraktstest passerar. R05 är uppskjutet för att undvika
Opus överlapp; R07:s ägarbeslut och OVN-F1 är öppna. Navets slutrapport
och evidence pushas i avslutet, därefter stoppas automationen.
[Slutrapport](FINAL_REPORT.md), [integration](evidence/final-integration.json).

## Avslut, 2026-10-08 07:47

Navets slutrapport och evidence är pushade i `0865e80`. Automationen är
PAUSED och R08 är komplett; [avslutsmetadata](evidence/final-checkpoint.json).
Inga nya paket startas av nattkörningen.
