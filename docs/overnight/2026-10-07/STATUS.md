# Nattens status, 7–8 oktober

Uppdaterad 2026-10-08 07:00 Europe/Stockholm. Stopptid: 08:00 (06:00 UTC).
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

## Slutgrind pågår

Opus fjärr-main `0e0bf49` är integrerad med bevarad historik. Codex lokala
Core-commits är `2871bff` och `aece6eb`; de väntar på slutgrind före push.
Fjärren har därefter gått till `059aadd`, enbart med kampanjlogg: slutliga
totalsiffror och Opus egen rättelse som bekräftar OVN-F1. Dessa fyra
commits ändrar ingen kod; loggen integreras efter slutgrinden.
Alla RTL-/byggindata är oförändrade. Den nya frysta sviten startade
05:54 Europe/Stockholm från `final-core-aece6eb`, med **434 insamlade test**.
Runnern sparar returstatus och jämför samtliga 171 frysta källfilers hash
före/efter. Den avslutar sin egen processgrupp senast 07:58 om sviten
inte är klar. [Pågående metadata](evidence/final-suite.json).

De snabba kontrollerna på den integrerade koden gav **249 passed,
15 deselected** på 2,68 s. De tre försvagade upstream-vägarna har
meningsfulla negativa kontroller. Sparade R03-loggar analyserades igen
med den integrerade kontrollen och byte-identiska indata: frö 48 är
grönt med 648 rader, frö 126 har `store/read` och 216 kontrollerade rader.
[Snabbgrind](evidence/integrated-light-gate.log),
[upstream-kontroller](evidence/upstream-oracle-negative-controls.json),
[logganalys](evidence/integrated-retained-log-review.json).

## Samordning och återstående gränser

Hub-checkpoint `454b308` är pushad; navet har därefter fast-forwardats
till Opus dokumentationsrättelse `76a1121`. Core-kod är integrerad lokalt och
väntar på slutverifiering före push. Puck `9d2fb57` har fortfarande rent `core/` på `82c4134`;
gitlänken uppdateras bara till accepterad/pushad Core-revision.

Luna/max sparade planen före kreditfel. Root slutför arbetet; ingen ny
provider, köpta credits eller automatiska omförsök. Användarens Vibe har
överlämnat dokumentation; Codex startar eller styr inte dess session.
[Vibes daterade rapport med root-rättelse](VIBE_REPORT.md) bevaras.

#17 och #18 kräver ägarbeslut om LOW:s start och mixerns F-bit. OVN-F1
har en avgränsad framtida rättningsplan. Inga RTL-regler, bildlägen, stift,
IOB, SDC, licens- eller BOM-beslut ändras i detta pass. R05:s breda nya
fuzz skjuts upp för att undvika Opus redan utförda rundor. Slutlig svit,
commits, push och stoppläge fylls i efter verifiering.
