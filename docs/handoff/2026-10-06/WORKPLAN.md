# OpenVRX — fortsatt utveckling efter övertagandet

Underlag: [övertagandegranskningen](AUDIT.md), nya riktade simuleringar från den 5 oktober. **Ingen hårdvara har körts.**


## D00 — dagens utvecklingspaket

Status: **lokalt accepterat** — 78 Core-tester, Puck-regression och ERC, fyra routade bitströmmar samt rena lokala commits. Exakta versioner, hashvärden, exitkoder och begränsningar finns i [RESULTAT.md](RESULTAT.md). Ingen hårdvara är accepterad.

- Claudes 23 ändrade/nya Core-filer och två Puck-filer finns på `codex/inherited-claude-2026-10-05` i respektive repo, med SHA-256 i [provenance.json](provenance.json). Granskningsunderlaget har inte skrivits över.
- Core: radnumreringen startar om efter vertikal blankning även när F ligger still. En förlorad SAV reserverar fortfarande rätt radnummer.
- Mixer: kanalens tidsgräns är 262144 systemcykler, cirka 4,05 ms vid 64,8 MHz, så normal PAL/NTSC-blankning ryms. Parningen väntar högst 4096 cykler, cirka 63,2 µs, på en saknad motpart, förutsatt att utgången kan ta emot data.
- Alla beslut kontrollerar kanalhälsa. Två dåliga rader släpps. Felstatus vid fångst lagras även om kanalen sedan återhämtar sig; ny felstatus spärrar redan köade rader. Redan visade och äldre rader släpps med en utmatningsgräns per fältepoch och rad. En återkommande kanal kan återställa sin epochrelation vid färska matchande rader.
- Ringbufferten publicerar bara hela rader med sammanhängande ordindex. Frigjord plats mitt i en tappad rad får inte återanvända gammalt RAM-innehåll. Input-FIFO-förlust ingår i den sticky overflow-signalen.
- Tidsmedveten referensmodell och regressioner: 20–25 blankrader, 2/5/7 raders eftersläpning, tvingat A/B, förlorade ord, sista ensamma rader, flera missade fält och konstant F. Avsiktligt trasiga varianter kontrollerar att acceptanskraven kan upptäcka felen.
- Reset/SPI på LED-stiften uttrycks som separata tilldelningar. Pucks kontroll kräver rätt funktion i den pinnade Core-koden, och kan inte längre godkänna LED3=`~cur` som RESETB. Puck-utdata ska regenereras efter Core-bump.
- Latensanalysen förbrukar varje skärmkant en gång och avvisar negativ fördröjning.

Begränsningar: modellen beskriver beslut på radnivå, inte varje CDC-/emissionscykel. Källorna måste vara samma bildsignal. Epochjämförelsen är modulär över 8 bitar; återkomst efter avbrott måste gå genom färsk parning. De simulerade fallen bevisar inte korrekt bildfas mellan två riktiga dekodrar eller hela M4/M6-systemet. Overflow har ännu ingen egen rad i M6-loggen/OSD. Dessa förändringar rättar alltså delar av Core #1–#5; ärendena stängs inte automatiskt.

## Körordning och acceptans

Ett paket åt gången. Ett tungt jobb åt gången: ingen parallell simulering och routning. Varje paket lämnar en liten commit, loggar med faktisk exitkod, negativa kontroller och en uppdaterad status. En ny funktion får inte låna ett gammalt byggresultat. De tre repona hålls åtskilda; ingen Git-init i den privata projektroten.

Core-sökvägar som `rtl/`, `sim/`, `top/`, `formal/` och `tools/` i tabellen är relativa till `OpenVRX-Core/gateware/`. Puck-sökvägarna är relativa till `OpenVRX-Puck/`.

| ID | Paket | Beroende | Ägda filer / ansvar | Klart när |
|---|---|---|---|---|
| D01 | SDRAM-modell och minnestesttop | D00 | Core `rtl/sdram_burst.v`, `rtl/clocks_sdram.v`, `sim/sdram_model.v`, `sim/test_sdram.py`; ny `top/m2a_memtest.v`, dess CST/SDC och test | CL2 läses med rätt burstposition; för tidig ACT/PRE/REF och fel samplingsfas upptäcks; minnestest rapporterar fel per bit/adress över UART; bygget klarar rätt klockkrav |
| D02 | Bildbuffertens ägarskap och fältgeometri | D01 | Core `rtl/fb_sdram.v`, `rtl/fb_display.v`, `rtl/fb_backend.v`, `sim/test_m2.py` och buffertmodell | Skrivaren äger aldrig visad eller reserverad buffert; systematiska klockfas/frekvensfall visar inga rivningar; bob/paritet och gemensamt aktivt radantal är definierade |
| D03 | LOW: giltiga bildperioder och återlåsning | D00; kör efter D02 | Core `rtl/genlock_timing.v`, LOW-delen av `rtl/fb_backend.v`, `formal/`, `sim/test_m2.py` | Trigger under aktiv bild kan inte ge en för kort bild; min/max-perioder bevisas med negativa kontroller; NTSC/PAL-byte och signalbortfall håller rimlig utgångstiming |
| D04 | TVP/I2C och mottagaråterhämtning | D00 | Core `rtl/i2c_master.v`, `rtl/tvp_ctrl.v`, `rtl/rx_tune.v`, `rtl/puck_ui.v`, deras slavmodeller och tester | Låg SCL får ett ändligt avslut; NACK ogiltigförklarar status; återkommen TVP får init/readback och frisk status; sena RX-starter har definierat beteende medan en annan RX håller lås |
| D05 | Sammanhängande M4/M6-feltester | D02–D04 | Core `sim/` med toppnära bänkar; ändra RTL bara för reproducerade fel | Två oberoende videoklockor med bortfall/återstart, fel/statusbyte och utgångsbuffertering provas tillsammans; outputfält/rad/pixel jämförs mot källan; inget färdigt funktionspåstående bygger bara på ett modulprov |
| D06 | Diagnostik som går att använda på bänken | D04–D05 | Core `rtl/mixer2.v`, `rtl/puck_ui.v`, `top/m6_puck_proto.v`, `tools/snowlog.py` och tester | Tappade rader/overflow och kanalstatus syns; trasig/avhuggen UART-rad avbryter inte mätningen; återställning och mätintervall är dokumenterade |
| D07 | Tang-revision och M0/M3 på hårdvara | D00 + levererat material | Privata bänkanteckningar; Core `BRINGUP.md` om pinplan behöver ändras | Faktisk revision, IO_DVDD, adresser och matning dokumenterade; M0 ger stabil HDMI på skärmen; M3 visar båda dekodrarnas klocka, databitaktivitet och lås |
| D08 | Minnestest → BUF via M4(A) → M4(A+B) → M6 | D01–D07 | Privata mätloggar; Core-fixar endast efter separat reproduktion | Minnestest passerar på kortet; riktig färgbild; A/B/MIX, kanalbyte, frånkoppling/återkomst och OLED/UART provade; varje mätning har bitströmhash och kopplingsrevision |
| D09 | Mixnytta, glas-till-glaslatens och EMI | D08 | Privata inspelningar/CSV och mätprotokoll; eventuell kalibrering av mixerregeln | Samma RF-fall jämförs i A/B/MIX; bildfas/blandningsartefakter bedöms; hela kedjan mäts; HDMI/FPGA/SDRAM och 479 MHz-IF-frågan ingår i kontrollerad på/av-jämförelse |
| D10 | Välj 1080p/XR-väg | D08–D09 | Hub-research och separat avgränsad Core-top | Vald sink och 50/60 Hz provas; initsekvensens ursprung/licens är klar; publik checkout kan återskapa vägen; faktisk återlåsning och latens dokumenterade |
| D11 | Rev A, strömförsörjning och mekanik | D09; D10 före slutligt skal | Puck `design/rev_a/`, senare KiCad; privata inköps-/bänkunderlag | PTC hold/trip och värme räknade med mätt last; temperaturklass, PLL-avkoppling, ESD och jord kontrollerade; livscykelkontroll av hela BOM; schema/DRC/fit accepterade före beställning |

För fristående moduler används M4 med bara dekoder A som första färg/BUF-test; den gamla M2-Moneagle-toppen saknar modulernas init/resetkoppling. D07:s M0/M3 kan göras medan D01–D06 utvecklas, när materialet levererats. D08 och LOW får däremot inte ärva acceptans från D00. Core #16, visning av fältet medan det skrivs, väntar till efter D02/D08. Windows-portning av loggverktyget och GW5A/ESP32-C5 är senare paket.

### D01: minsta konkreta arbetsuppdrag

1. Läs [Core #7](https://github.com/LAP87/OpenVRX-Core/issues/7) och jämför SDRAM-modellen med den faktiska minnesdelen på Tang. Använd tillverkarens tidsvärden och skilj intern statisk timing från DQ:s I/O-fönster.
2. Återskapa det gamla modellfelet: rätt CL2-position och burstlängd ska skilja sig från dagens förenklade acceptans. Lägg en negativ kontroll där fel dataposition eller för kort kommandoavstånd måste fallera.
3. Gör samplingsfasen explicit och testbar. Välj inte 180° eller 225° genom att kopiera en föregångares kommentar; dokumentera vad modellen kan avgöra och vad kortet måste mäta.
4. Ny minnestesttop skriver/läser walking-one/zero, adressmönster och flera bank/radövergångar. Bounded körning med UART: totalt testade ord, fel per DQ-bit och första feladress/förväntat/läst. RX/TVP behöver inte vara anslutna.
5. Kör riktade minnestester, sedan relevant fullsvit, sedan ett bygge. Spara bitströmmanifest. D07/D08 använder den på riktig hårdvara innan BUF godkänns.

D02 får välja fyra buffertar eller en förbättrad trebuffertshandskakning utifrån ett konkret ägarskapsbevis. Antalet buffertar i sig är inte acceptans. Svep både inkommande fältperiod och pixelklockans fas, inklusive källan lite snabbare än utgången och byte från tom till fylld buffert.

D03:s minperiod ska utgå från aktiv bild + minsta giltiga blankning. En trigger på rad 2 i en liten bänk är en negativ kontroll: före övertagandet gav den 56 cykler mot normalperiod 168. Bevisa den nya gränsen från reset, inte bara genom att anta att `lock` eller `trig` alltid är välformade.

D04 ska även beskriva en fysisk gräns: de två RX5808 delar DATA/SEL/CLK. Oberoende retuning kräver annan styrning eller en verifierad gemensam omskrivning. En menyändring kan inte ge separat chip-select med dagens koppling.

## Återställning och versioner

- Ursprung: Core `dec88d6`, Puck `bdee8e4`, hub `4fd0f11` plus de sparade arbetsfilerna. Återskapa i en separat checkout från de publicerade jämförelsebrancherna; använd inte `git reset --hard` i en arbetskatalog med nya filer.
- Accepterade commits och testloggar finns i [RESULTAT.md](RESULTAT.md). Core har publicerats före Puck, vars submodul är pinnad till `1a1e5c7`. Hämta `codex/handoff-2026-10-06` enligt [README.md](README.md).
- Varje hårdvaruprovares bitström får ett eget versionsnamn, SHA-256, Core-commit, verktygsversioner, top/parametrar och stiftplan. De gamla filerna i `private/bitstreams/` bevaras som äldre underlag och ska inte väljas genom att bara ta första `.fs`-filen.
- Vid regression: spara stimulus/logg, återgå till senast accepterad version i separat checkout och jämför. Radera inte motexemplet eller ersätt det med ett enklare fall.
- Köp-, order- och prisuppgifter stannar i `private/`. Inga råa datablad, oklar tredjepartskod eller privata initsekvenser läggs till i de tre repona.

## Kopierbart uppdrag för nästa kodningsagent

```text
Arbeta i din checkout av OpenVRX-Core eller OpenVRX-Puck/core.
Läs OpenVRX/AGENTS.md och docs/handoff/2026-10-06/WORKPLAN.md
samt RESULTAT.md i hub-repot. Utför endast D01: timingmedveten SDRAM-modell
med negativa kontroller och en självständig m2a_memtest-top med UART-resultat.
Äg endast de filer D01 anger; andra ändringar kräver först ett reproducerat fel.
Det finns andra författares arbete: återställ eller skriv inte över deras filer.
Ett tungt jobb åt gången. Använd ingen signerad RTL-aritmetik. Ingen hårdvara
finns att certifiera i en simulering. Ändra inte global verktygskonfiguration,
köp inget, publicera inget och ta inte in privat LT8618SX-kod. Kör relevanta
simuleringar och negativkontroller innan PnR. Avsluta med lokal commit, exakta
acceptansresultat, kvarvarande hårdvarukrav och en återupptagbar arbetsanteckning.
Om tillverkaruppgifter saknas: fortsätt övrig avgränsad implementering men
markera just timingbeslutet öppet. Hitta inte på ett godkänt minnestest.
```
