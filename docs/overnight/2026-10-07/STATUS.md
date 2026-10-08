# Nattens status, 7–8 oktober

Uppdaterad 2026-10-08 07:43 Europe/Stockholm. Stopptid: 08:00 (06:00 UTC).
Arbete sker på `main` i alla tre repo. Inget har körts på hårdvara.

## Verifierat

- Fryst Core-baslinje `7cc4eda`: **395 passed, 1 xfailed** på 5156,04 s.
  Returkod 0. Xfail gäller det öppna Core #17.
  [Rå pytest-logg](evidence/baseline-core-7cc4eda.log).
- R02: **28 små kontraktstest** passerar, med arbetardubblar. Återupptagning
  kräver samma parametrar, käll-/simulatorhashar och seeddefinitioner.
  Äldre loggar bevaras; de saknar kontrakt och får bara sammanfattas.
- Färska M4/M6-byggen: alla rapporterade klockor klarar sina krav.
  M4: SDRAM 101,15 MHz, pixel 123,69 MHz, 8 236 LUT.
  M6: SDRAM 100,17 MHz, pixel 120,61 MHz, kontrollogik 117,86 MHz,
  12 542 LUT, seed 2. Båda har 25 BSRAM. Manifesten verifierar, alla
  byggindata matchar det frysta 7cc4eda-arkivet. HDMI-parens IOB-fuses
  matchar M0. [M4](evidence/m4_dual_mix.build.json),
  [M6](evidence/m6_puck_proto.build.json), [IOB](evidence/tmds-fuses.log).
- Mixerfil och displayens negativa RTL-kontroll: **29 passed, 1 xfailed
  (#18)** på 1325,61 s. A- och B-återkomst testas mot modellen; gamla
  domarregeln och felaktig displayadress fångas.
  [Rålogg](evidence/targeted-mixer-display.log).
- #18: 124 beslut och 21 960 utord matchar RTL/modell. Nytt utfält vid
  `(F=1, rad=15)` efter `(F=1, rad=3)` markeras inte nedströms. Xfail
  avgränsas till detta fynd, efter modelljämförelse; andra fel får falla.
  [Evidence](evidence/issue18.json).
- R03 frö 48: 648 visade rader, inga modellavvikelser eller strikta
  checksumfynd i sparade loggar. Density 1,0 gav samma scenarier som
  basversionen på sex frön före den senare observationsmetadataändringen.
- **OVN-F1:** frö 126 motbevisar antagandet om blank LOW→BUF-bild.
  Alla 72 aktiva RGB-prov avviker från blankbilden; i början visas BUF
  innan något fält har publicerats. Strikt checksum hittar buffert 0/rad 5
  läst under omskrivning. `3ad2c2b` avvisas som kontrolländring.
  [Fynd och nästa rättningspaket](LOW_BUF_FINDING.md),
  [råvärden](evidence/transition-probe-126.json).

## PAL/LOW och återupptagning, klart

R06: full PAL, frö 49, åtta fält och LOW-byte vid 34,68 ms.
**Fyra hela LOW-bilder och 2 880 bildrader** kontrollerades på 1160,8 s.
Bara det kända #17-fyndet `display/switch_video`; inga nya avvikelser.
Samma källor/kontrakt återupptogs genom riktiga process-pool-runnern:
**ran 0, 0 left**. Ingen ny simulering startade.
[Resultat/kontrakt](evidence/r06-pal-low-full.json),
[körlogg](evidence/r06-pal.log), [resume](evidence/r06-pal-resume.log).

## Slutgrind godkänd och kod pushad

Fryst Core `aece6eb`: **432 passed, 2 xfailed (#17/#18)** på 5162,59 s
(1:26:02), returstatus 0. Körningen avslutades 07:20 Europe/Stockholm.
Samtliga 171 källhashar var oförändrade före/efter. Båda xfail är väntade;
OVN-F1 är fortfarande öppet och fångas i den riktade uppspelningen av frö
126, som inte är ett av regressionssvitens fasta frön.
[Slutmetadata](evidence/final-suite.json), [rålogg](evidence/final-suite.log).

Opus loggcommits till `059aadd` är integrerade med bevarad historik,
inklusive hans egen OVN-F1-rättelse. Core **`fb6896a` är pushad till main**.
Bara tre Markdown-filer skiljer den från den frysta testade revisionen;
alla 168 övriga filer är byte-identiska. M4/M6-manifesten verifierar även
mot denna slutliga Core-kod.
[Integration/källjämförelse](evidence/final-integration.json),
[manifestverifiering](evidence/final-build-verification.log).

Puck **`8917d27` är pushad till main** med `core/` på `fb6896a`.
Schema-/gateware-kontraktet med negativa kontroller: **1 passed på 1,35 s**,
returstatus 0. Enda Puck-ändringen är gitlänken. Core, Puck och submodulen
är rena. [Testmetadata](evidence/final-puck.json), [rålogg](evidence/final-puck.log).

De snabba kontrollerna på den integrerade koden gav **249 passed,
15 deselected** på 2,68 s. De tre försvagade upstream-vägarna har
meningsfulla negativa kontroller. Sparade R03-loggar analyserades igen
med den integrerade kontrollen och byte-identiska indata: frö 48 är
grönt med 648 rader, frö 126 har `store/read` och 216 kontrollerade rader.
[Snabbgrind](evidence/integrated-light-gate.log),
[upstream-kontroller](evidence/upstream-oracle-negative-controls.json),
[logganalys](evidence/integrated-retained-log-review.json).

## Samordning och återstående gränser

Navets föregående checkpoint `2793051` är pushad. R08:s slutrapport,
status och råevidence granskas och pushas i detta avslut. Fullsvitens
process och bygglåset är avslutade; ingen kopia har startats.

Luna/max sparade planen före kreditfel. Root slutför arbetet; ingen ny
provider, köpta credits eller automatiska omförsök. Användarens Vibe har
överlämnat dokumentation; Codex startar eller styr inte dess session.
[Vibes daterade rapport med root-rättelse](VIBE_REPORT.md) bevaras.

#17 och #18 kräver ägarbeslut om LOW:s start och mixerns F-bit. OVN-F1
har en avgränsad framtida rättningsplan. Inga RTL-regler, bildlägen, stift,
IOB, SDC, licens- eller BOM-beslut ändras i detta pass. R05:s breda nya
fuzz skjuts upp för att undvika Opus redan utförda rundor. Alla verifierbara
nattpaket är accepterade; R05 är uppskjutet och R07:s beteendebeslut är öppna. Automationen stoppas efter navets slutpush.
[Slutrapport](FINAL_REPORT.md).
