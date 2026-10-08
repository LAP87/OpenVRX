# Nattens status, 7–8 oktober

Uppdaterad 2026-10-08 04:39 Europe/Stockholm. Stopptid: 08:00 (06:00 UTC).
Arbete sker på `main` i alla tre repo. Inget har körts på hårdvara.

## Verifierat

- Core-baslinjen från ett fryst Git-arkiv av
  `7cc4eda2022334ed6f2f618548d59d72a5f6b7c2`: **395 passed, 1 xfailed**
  på 5156,04 s. Returkod 0. Xfail gäller det öppna Core #17.
  [Rå pytest-logg](evidence/baseline-core-7cc4eda.log).
- R02:s små tester för kampanjkontrakt: **28 passed**. De använder
  arbetardubblar och simulerar ingen RTL. Källor, simulator och parametrar
  måste stämma före återupptagning; gamla loggar bevaras.
- M4 byggd 04:11 från samma RTL som `7cc4eda`: alla fem rapporterade
  klockor klarar 75 MHz. SDRAM 101,15 MHz är lägsta maximum.
  Manifestet har verifierats mot artefakter och aktuella byggindata.
  Arbetsträdet var smutsigt av teständringar; inga byggindata ändrades.
  [Byggmanifest](evidence/m4_dual_mix.build.json).
- Density 1,0 ger samma scenarier som basversionen för fröna
  0, 17, 48, 85, 126 och 233. [Hashjämförelse](evidence/density-default-parity.json).

## Samordning och överlämningar

- Vid start fast-forwardades Hub till `4d43600`, Core till `7cc4eda` och
  Puck till `9d2fb57`; arbetskopiorna var rena. Pucks `core/` är fortfarande
  rent och detached på `82c4134`. Inga nya commits/push i detta nattpass ännu.
- Luna på max sparade `WORKPLAN.md` och `tasks.json` före ett kreditfel.
  Codex/root har tagit över planens granskning och kodarbete. Ingen ny
  provider, inga reset credits och inga automatiska Luna-omförsök.
- Användarens befintliga Vibe-session har lämnat [VIBE_REPORT.md](VIBE_REPORT.md)
  och dokumentationsutkast. Root granskar innan commit. Codex extra
  CLI-anrop misslyckades före arbete; det var fel att härleda sessionens
  autentisering från det. Vibe ska inte startas eller styras av Codex.
- Nattgrenen hämtades senast 04:02: tip `6f45f1a`. Dess senare resultat
  tillskrivs inte `main`. Endast `cb2c10f` och `3ad2c2b` är applicerade för
  lokal granskning/reproduktion, ännu inte accepterade eller incheckade.

## Pågår och nästa steg

M6 är klart: SDRAM 100,17 MHz, pixel 120,61 MHz och kontrollogik 117,86 MHz
(mot 75/75/54,05 MHz). Manifestet är verifierat och alla byggindata matchar
det frysta 7cc4eda-arkivet. Riktad mixersvit och displayens negativa RTL-
kontroll kör nu under låset; därefter frön 48/126. Fem små displaytester
provar checksumkontrollen för visad respektive dold rad. Minimalt #18-test
från ec06c56 och modellens observationslista granskas separat; ingen
regel för F-biten eller kedjans ålderskontroll har ändrats. R05:s nya densitetskampanj skjuts upp för
att undvika överlappning med Opus. PAL/LOW full geometri är villkorat av
kvarvarande tid och lyckade föregående grindar.

Core #17 kräver en regel för när LOW får visa video. Core #18 kräver ett
fältstartskontrakt för mixerns F-bit; dess lilla grenreproduktion är nu applicerad för granskning med avgränsat xfail.
Inga sådana beteendebeslut tas i natt. `tasks.json` är körjournalen;
slutstatus och commits fylls i efter verifiering.
