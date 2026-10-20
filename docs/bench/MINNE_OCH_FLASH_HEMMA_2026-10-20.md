# Tang Nano 20K hemma: flashstart bekräftad, minnesprov ej avgjort

**Senare samma kväll:** den ursprungliga testbildens ruta fastnade vid vänsterkanten efter en stund. Den bitström som beskrivs nedan har ersatts i flash av en rättad privat bänkversion, bekräftad efter strömcykel. Se [rörelsefelet och den aktuella bitströmmen](M0_RORELSEFEL_2026-10-20.md). Minnesprovets ej avgjorda resultat är oförändrat.

Den 20 oktober 2026 visade kortet färgfält och en rörlig ruta på ägarens HDMI-skärm. Samma M0-bitström skrevs därefter till kortets flash med ägarens uttryckliga godkännande. Programmerarens skrivning och återläsningskontroll avslutades med rc0. Ägaren drog ur och anslöt USB-strömmen igen, utan intryckta knappar, och bekräftade: ”Ja, samma testbild kommer tillbaka”.

Detta är ett faktiskt start- och bildresultat på det aktuella kortet. Skärmmodell och skärmens rapporterade bildläge är inte dokumenterade. Testbilden bevisar inte radiomottagning, SDRAM-funktion eller den kompletta videokedjan.

## Bitströmmen som finns i flash

- M0 från tidigare accepterat standardbygge av Core `bf05ac0feed58c3295949a6f3b4ee55c886cd1e2`, seed 0, IOREG 0, DVI-standard (`HDMI=0`). Inget nytt M0-bygge.
- SHA256: `13c180ff4b9fff7dd6a6085216fb6e3f8e107615c886521193b784ac7fa7d466`, 839 054 byte. Sju artifacthashar och 50 källinputs kontrollerades före den första SRAM-laddningen.
- openFPGALoader 1.1.1, `-b tangnano20k --ftdi-serial 2025030317 -f --verify`. Det tidigare startprogrammet ersattes. Kontrollen var programmerarens återläsningskontroll; ingen separat fullständig flashdump gjordes.
- Tidigare SRAM-observation finns i [M0-rapporten](M0_HEMMA_2026-10-20.md). Denna rapport kompletterar den med beständig skrivning och bekräftad start efter strömcykel.

## M2a: byggt och laddat, men ingen giltig minneslogg

Ett första standardbygge av oförändrad Core `8dff8d1b4d5f1987a23c3f332f730119fccbd909`, tree `ff3ad9fc5cb54dc58a93d3a410e1e88ea6cbfe40`, avslutades rc0 på 73,011 s. Toppen var `m2a_memtest`, seed 0, IOREG 1, standardfas 10/16 (225°), VINTERP 0, HDMI 0 och MSPI 0. Byggkravet var 75 MHz; sista routade timingrapporten angav 81,84 MHz för `sd_clk`. Källans nominella SDRAM-klocka är 64,8 MHz, inte en uppmätt frekvens.

212 Gitblob-/arkivbundna källfiler var oförändrade efter försöket. Manifestets 51 inputs och sju artifacthashar kontrollerades. M2a-bitströmmen har SHA256 `0a58ea6c343733af65df18a32135bac38916215a297763140ae110efa86819b6`. SRAM-laddningen avslutades rc0. Det var ett bygge och en M2a-laddning, utan omförsök eller ändrad RTL/fas för att få ett godkänt resultat.

Första USB-UART-avläsningen vid 115200 8N1 samlade 6 232 byte på 20 sekunder, men inga kompletta giltiga M2a-rader. Originalbytes och läshjälpare är bevarade. Två avgränsade mottagardiagnoser provade totalt åtta andra baudinställningar på samma körande FPGA-design, utan omprogrammering eller sända UART-payloads. Inte heller dessa gav giltiga rader. Diagnoserna styrker inte en viss felorsak.

Sipeeds [kortdokumentation](https://wiki.sipeed.com/hardware/en/tang/tang-nano-20k/nano-20k.html) beskriver att debuggerns UART kan ge förvrängda tecken, men det fastställer inte orsaken på detta kort. Ingen BL616-firmware, drivrutin eller klockgenerator ändrades.

**SDRAM-resultatet är ej avgjort.** Det finns inget belagt `rs=5 err=00000000`, och S2-felinjektionen utfördes inte när loggen inte gick att tolka. Faktisk källkod växlar mellan läspunkterna 4, 5 och 6. Vi drar varken slutsatsen att minnet fungerar eller att det är trasigt.

## Nästa inkoppling på jobbet

Kortet startar nu med den bekräftade testbilden. Behåll M2a-loggarna för en separat UART-diagnos, exempelvis med en oberoende serieadapter och verifierad signalväg, innan minnesresultatet används för M4. TVP-modulen och övrig utrustning finns på jobbet; RX5808 har ännu inte mottagits. Ingen TVP-, RF-, dubbelvideo- eller ny menyfunktion testades här.

Privata original, kontrakt, byggmanifest, programmeringsloggar, nio UART-captures, ägarens observationer och rootgranskningen finns i `private/notes/bench_home_2026-10-20/`. Automationen återupptogs inte genom detta manuella bänkprov.
