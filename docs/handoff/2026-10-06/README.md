# OpenVRX — överlämning till jobblaptopen 2026-10-06

`codex/handoff-2026-10-06` i de tre repona innehåller det accepterade
utvecklingspaketet från den 5 oktober. Denna mapp innehåller granskningen,
arbetsplanen, acceptansloggarna och de fyra byggda bitströmmarna.
**Inget är provat på hårdvara.**

## Hämta arbetsläget

Kör i en ny gemensam mapp, eller hämta brancherna i dina befintliga checkouter:

```sh
git clone --branch codex/handoff-2026-10-06 --recurse-submodules https://github.com/LAP87/OpenVRX-Puck.git
git clone --branch codex/handoff-2026-10-06 https://github.com/LAP87/OpenVRX.git
```

Pucks `core/` är en vanlig submodul på den accepterade commiten `1a1e5c7`.
Den checkouten är detached, vilket är normalt för en pinnad submodul.
För redigering där, skapa en egen arbetsbranch först. En separat Core-klon
kan också hämtas på `codex/handoff-2026-10-06`; båda innehåller samma Core-träd.
Lokala `.venv`- och `.toolchain`-symlänkar överförs inte. Installera verktyg
enligt Core `requirements.txt` och README; sparade Linux-resultat är inte
ett prov av verktyg på jobblaptopens operativsystem.

En [färsk GitHub-klon](evidence/puck_clone_check.json) har kontrollerats:
Puck hämtar rätt Core-commit, båda arbetskatalogerna är rena och båda
jämförelsebrancherna går att hämta.

| Repo | Accepterad utvecklingscommit | Branch på GitHub |
|---|---|---|
| Core | `1a1e5c7fb7b8f9a991e27cd70f871a923f42ce7b` | [OpenVRX-Core](https://github.com/LAP87/OpenVRX-Core/tree/codex/handoff-2026-10-06) |
| Puck | `e65cd8e25e40712d7c76075931b7715defc85474` | [OpenVRX-Puck](https://github.com/LAP87/OpenVRX-Puck/tree/codex/handoff-2026-10-06) |
| Hub | `e4244600485145a3591ab69227b5dabaf624de54`, följd av denna överlämningsdokumentation | [OpenVRX](https://github.com/LAP87/OpenVRX/tree/codex/handoff-2026-10-06) |

## Jämför arbetet

De accepterade Core-/Puck-commitsen innehåller både kvarlämnade arbetsfiler
och senare Codex-ändringar. Deras commitförfattare skiljer därför inte
arbetet åt. I Core och Puck finns `codex/inherited-claude-2026-10-05`, en
rekonstruktion av filerna från övertagandet. Alla 23 ändrade/nya Core-filer
och två Puck-filer är verifierade mot den sparade kopians SHA-256.
Oförändrade filer kommer från respektive ursprungscommit. Exakta referenser
och filhashar finns i [provenance.json](provenance.json).

Detta avgränsar arbetslägena i tid. Det bevisar inte vem som skrev varje rad.
Jämförelsebrancherna är historiskt underlag och har kvar de då kända felen.

Kör i Core-klonen eller Pucks `core/` för att skilja kvarlämnat arbete från
Codex förändringar:

```sh
git fetch origin
git diff --stat dec88d6a6ad7a9b9bb197f2c50142d46c47abcc3 origin/codex/inherited-claude-2026-10-05
git diff origin/codex/inherited-claude-2026-10-05 origin/codex/handoff-2026-10-06
```

För Puck, kör i dess rot:

```sh
git fetch origin
git diff --stat bdee8e46719713163edaa7c2d27adc07377020dd origin/codex/inherited-claude-2026-10-05
git diff origin/codex/inherited-claude-2026-10-05 origin/codex/handoff-2026-10-06
```

Använd vanlig `git diff A B` för de två filträden. Jämförelsebrancherna är
syskon i historiken; en jämförelse med tre punkter tar även med ändringar
från deras gemensamma förälder. Hubben var ren vid övertagandet: där börjar
Codex förändringar efter `4fd0f119f6de6aa44840d518ba974f6cc7b37faa`.

Kvarlämnat arbete omfattar RESETB/SPI-stift, kanalomsändning, TVP-statusbit,
bring-up och M4/M6-klockkrav. Codex tillägg omfattar radnumrering vid konstant
F, helradsförlust, frisk/bortvald kanal och ordning vid lagg/återkomst,
modeller och negativa kontroller, funktionskontroll av stiften, Puck-export,
latensparning och byggskriptets slututskrift. Filträdsjämförelsen visar
avgränsningen även där båda arbetslägena ändrade samma fil.

## Läsordning och acceptans

1. [AUDIT.md](AUDIT.md): rapporten från övertagandeläget, före rättningarna.
2. [RESULTAT.md](RESULTAT.md): exakt vad det accepterade paketet ändrar och dess gränser.
3. [WORKPLAN.md](WORKPLAN.md): D00–D11 med ägda filer, beroenden och acceptanskrav. Nästa utvecklingspaket är D01.
4. [Maskinläsbar acceptans](evidence/acceptance.json) och [byggmanifest](evidence/build_manifest.json).

Core: **78 passerade tester** på 710,42 s. Puck: **en regression** på 1,28 s,
med negativa kontroller. Schemaexport: 110 delar, 83 anslutna nät, ERC 0 fel
och 0 varningar. M0/M3/M4/M6 klarar sina slutliga interna klockkrav efter
routning. M4:s historiska exit 141 kom efter packning i en rättad
slututskrift; detaljerna finns i RESULTAT och manifestet.

SDRAM:s verkliga samplingsmarginal, buffertägarskap, genlock-minperiod,
I2C/TVP-återhämtning, M4/M6 under sammanhängande fel och fysisk bildfas mellan
två dekodrar återstår. Inget av resultaten är en hårdvaruacceptans.

## Byggarkiv och historiskt underlag

[core-builds-1a1e5c7.tar.gz](artifacts/core-builds-1a1e5c7.tar.gz) innehåller de
fyra bitströmmarna, deras ursprungliga loggar, stift-/klockkrav,
källkodshashar, körda byggscript och manifest. Arkivet är verifierat mot
manifestets SHA-256. [SHA256SUMS](artifacts/SHA256SUMS) gäller själva arkivet.

```sh
tar -xzf docs/handoff/2026-10-06/artifacts/core-builds-1a1e5c7.tar.gz
```

Loggar och [historiska scripts](evidence/historical_scripts/) bevarar
originalmaskinens sökvägar. De är underlag för genomgången; scripts måste
anpassas före körning på annan dator. [Motexempel före ändringarna](evidence/audit_before_changes/)
bevaras separat från slutacceptansen. Råa datablad, oklar tredjepartskod,
privata LT8618SX-sekvenser samt butiks-/pris-/orderunderlag ligger kvar i
projektägarens lokala arkiv enligt repoets AGENTS.md.

## Uppdrag att ge Claude på jobblaptopen

```text
Läs OpenVRX/AGENTS.md och docs/handoff/2026-10-06/README.md, AUDIT.md,
RESULTAT.md och WORKPLAN.md på codex/handoff-2026-10-06.
Jämför först codex/inherited-claude-2026-10-05 mot handoff-branchen i
OpenVRX-Core och OpenVRX-Puck med vanlig git diff mellan de två filträden.
Rapportera vilka kvarlämnade ändringar som bevarats, vilka Codex ändringar
som är korrekta och vilka som behöver ändras. Kontrollera särskilt
modellernas oberoende, negativa kontroller, CDC och påståendena om återkomst.
Använd testloggarna som tidigare lokal acceptans, inte som bevis för
hårdvara eller för andra checkouter. Börja med granskningen innan ny
funktionalitet eller sammanslagning till main. Om nya kontroller körs:
ett tungt jobb åt gången. Nästa planerade utvecklingspaket är D01.
```
