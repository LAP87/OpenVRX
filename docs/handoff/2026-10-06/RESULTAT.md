# OpenVRX — accepterat utvecklingspaket 2026-10-05

D00 är accepterat genom lokal simulering, routning och schemaexport. **Inget är provat på hårdvara.** Utvecklingspaketet och denna överlämning publiceras på `codex/handoff-2026-10-06` i de tre repona. Inga ärenden har stängts och inga inköp har gjorts av Codex.

## Versioner

| Repo | Lokal branch vid acceptans | Commit | Arbetskatalog |
|---|---|---|---|
| OpenVRX-Core | `bringup-pins` | `1a1e5c7fb7b8f9a991e27cd70f871a923f42ce7b` | Ren |
| OpenVRX-Puck | `resetb-j6-18` | `e65cd8e25e40712d7c76075931b7715defc85474` | Ren |
| OpenVRX | `main` | `e4244600485145a3591ab69227b5dabaf624de54` | Ren |

Pucks Core-submodul är pinnad till `1a1e5c7fb7b8f9a991e27cd70f871a923f42ce7b`. Core publicerades före Puck. En färsk GitHub-klon av Puck med submoduler hämtar exakt den accepterade Core-versionen, och båda arbetskatalogerna är rena: [klonkontroll](evidence/puck_clone_check.json). Detta provar hämtningen på utvecklingsmaskinen, inte jobblaptopens verktyg eller hårdvaran.

## Vad paketet ändrar

- Claudes kvarlämnade reset/SPI-, kanalomsändnings-, statusbit- och klockkravsarbete har bevarats och ingår i Core-commiten. Ursprungliga arbetsfiler och patchar finns i [Git-jämförelsen och filhasharna](README.md#jämför-arbetet).
- Radnumrering startar om på vertikal blankning även med konstant F. Förlorad SAV reserverar fortfarande radpositionen.
- Mixern väntar ett begränsat fönster på en saknad motpart, kontrollerar hälsa på varje beslutsväg och släpper gamla/upprepade utmatningsnycklar. Kanalhälsan ryms genom normal VBI.
- Fyraplatsringen publicerar bara fullständiga rader. Överfull kö eller förlorat ord kan inte återanvända gammalt RAM som en hel rad. Felstatus vid radmarkören lagras genom återhämtning; ny status spärrar även väntande rader.
- Puck kontrollerar RESETB/SPI-funktion, inte enbart portnamnets stiftnummer. Äldre Core utan kontraktet avvisas före export. RESETB ligger i både kod och export på J6-18.
- Latensanalysen använder varje skärmkant högst en gång och tillåter inte en skärmkant före LED-kanten.

## Acceptans

Core: **78 passed in 710.42s**. Kommando: `.venv/bin/python -m pytest -q -p no:cacheprovider tests/latency mixer gateware/model gateware/sim gateware/tools`. [Slutlogg](evidence/core_pytest.log). Den tidigare 75-testkörningen före tillägget för lagrad felstatus finns separat; den lånas inte som slutacceptans.

Puck: **1 passed in 1.28s**. Regressionen innehåller fel RESETB-funktion, flyttad klockingång och saknat Core-kontrakt. [Logg](evidence/puck_pytest.log). Även en faktisk körning mot den gamla submodulen gav exit 1 och oförändrade hashvärden på alla tre sparade exportfiler: [kontroll](evidence/puck_reject_old_core.json).

Negativa RTL-kontroller återinför delvis publicerad rad, den gamla VBI-tidsgränsen och förlust av lagrad felstatus; varje variant måste falla i samma scoreboard. Orderkontrollen avvisar både bakvänd och upprepad rad. Färska laggfall jämför visade beslut och alla utmatade ord med radmodellen. Modellen beskriver inte alla CDC-/emissionscykler.

### Samma typ av laggfel före/efter

Tre källfält med 24 aktiva och 20 blankrader, B fem rader senare och spärrad som olåst. Den äldre kolumnen kommer från [övertagandegranskningen](AUDIT.md); den nya från slutkörningens spår.

| Egenskap | Före | Efter |
|---|---:|---:|
| Visade rader från spärrad B | 65 | 0 |
| Bakvänd/upprepad rad med samma F | 56 bakvända | 0 |
| Fältstarter enligt backendens regel på utströmmen | 59 | 3 |

Det är en kontroll av mixer2-utströmmen, inte en körning av SDRAM/HDMI i detta motexempel. Alla fem fall (2/5/7 raders lagg, tvingat A/B och normal blandning) har tre fältstarter och inga bakvända/upprepade rader: [senaste spårsammanställning](evidence/mixer_regressions.json).

## FPGA-byggen

| Top | LUT4 / 20736 | BSRAM / 46 | Slutlig fmax / krav, MHz |
|---|---:|---:|---|
| `m0_testpattern` | 792 | 0 | pixel 138.81 / 75.0 |
| `m3_probe` | 2379 | 0 | långsammaste domän 129.23 / 75 |
| `m4_dual_mix` | 7782 | 24 | SDRAM 88.05 / 64.8; pixel 109.13 / 74.25 |
| `m6_puck_proto` | 11000 | 24 | SDRAM 98.73 / 64.8; pixel 128.12 / 74.25 |

Alla listade slutliga klockkrav passerar. M0/M3 använder det konservativa standardkravet 75 MHz; M4/M6 har egna 64,8/74,25/27 MHz-krav. Intern timing bevisar inte SDRAM-DQ:s samplingsmarginal, kablarnas signalintegritet, HDMI-låsning eller bildkvalitet.

M4 gav ursprungligen exit 141 **efter lyckad syntes, routning och packning**: slututskriftens `tac | awk` fick SIGPIPE under `pipefail`. Utskriften är rättad och provad med verkliga M0/M3/M4-loggar, samtliga exit 0; M6 körde därefter hela korrigerade scriptet med exit 0. Ingen PnR har körts om enbart för utskriften. Manifestet sparar körd scriptversion och kontrollerar att alla kommandon till och med packningen är identiska med den committade versionen. Alla kompilerade RTL-/stift-/klockkrav matchar Core-commiten. [Exitkontroll](evidence/summary_exit_check.json).

De fyra bitströmmarna och deras oförändrade byggloggar finns i [byggarkivet](artifacts/core-builds-1a1e5c7.tar.gz). [Manifestet](evidence/build_manifest.json) innehåller SHA-256, Core-commit, verktygsversioner, källkodshashar, stiftkrav och sista klockresultatet per domän. Äldre bitströmmar är bevarade och ingår inte i dagens uppstartsunderlag.

## Schemaexport

110 delar, 83 anslutna nät. ERC: **0 fel, 0 varningar**. Netlista/BOM/kopplingsrapport är regenererade; exportkontrollen bekräftar RESETB på J6-18 och ingen reset på J6-10. Två verkliga körningar ger identiskt innehåll bortsett från datumet. BOM har LF-radslut. [Hashar och jämförelse](evidence/puck_export_evidence.json). Scriptet som användes är bevarat bland [historiska scripts](evidence/historical_scripts/). Dess sökvägar behöver anpassas före en körning i en separat checkout; det ersätter inte sin första jämförelseexport.

Netlistegenereringen lämnar separata SKiDL-varningar om saknade KiCad-footprintbibliotek och den tomma rot-tagg som KiCad kräver. Inga slumpmässiga del-/nättaggar genereras. Footprints, KiCad-import, layout, DRC, mekanik och hårdvara är fortfarande inte verifierade. ERC-resultatet får inte användas som tillverkningsacceptans.

## Nästa steg

Utvecklingsordning och kopierbart nästa uppdrag: [WORKPLAN.md](WORKPLAN.md). D01 är timingmedveten SDRAM-modell och fristående minnestest med UART. Därefter buffertägarskap/fältgeometri, genlock-minperiod, I2C/TVP-återhämtning och sammanhängande M4/M6-feltester. Overflow syns ännu inte i M6-logg/OSD. 8-bitars epochjämförelse och krav på färsk återparning begränsar återhämtningspåståendet. Verklig bildfas mellan två dekodrar och RF-mixnytta måste mätas.


Inga råa datablad eller privata LT8618SX-initsekvenser har lagts in i repona. Denna acceptans gäller simulering, intern timing och schemaexport. Hårdvarukraven återstår.
