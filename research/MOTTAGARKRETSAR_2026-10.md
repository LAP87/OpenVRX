# Mottagarkretsen i de dyra analoga mottagarna (2026-10-17)

Uppgift 30 i [docs/ARBETSPLAN.md](../docs/ARBETSPLAN.md). Joshua Bardwell sade i ett klipp 2026-10-17 att de bra mottagarna har en annan, känsligare krets än den i RX5808, men mindes inte namnet (sammanfattat sist i [RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md](RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md)). Frågan är om rev B behöver en annan mottagarkrets eller bara en bättre omgivning runt RTC6715. Allt är läst 2026-10-17; inget är mätt.

Belägg: **[FCC]** FCC-ansökan, **[T]** tillverkarens dokument, **[K]** källkod, **[F]** foto där märkningen ska kunna läsas, **[R]** eget resonemang. Forumpåståenden räknas inte som belägg.

## Slutsats

| Enhet | Mottagarkrets | Belägg | LNA eller filter före kretsen | MF-filter | Tillverkarens känslighet | Samma krets som RX5808 (RTC6715)? |
|---|---|---|---|---|---|---|
| HDZero Goggle 2 och BoxPro (Divimath), analoga delen | RTC6715, en mottagare | [K]: firmware kallar kretsen RTC6715 och skriver dess register 00h, 01h och 0Ah via FPGA:n | obelagt | obelagt | ingen siffra för den analoga delen hittad | **ja** |
| Skyzone SteadyView (goggle-modulen och SteadyView X) | obelagt; modulen styrs med RTC6715:s ram och register och svarar på läsning | [K] ExpressLRS Backpack; [F] mottagarkortet under skärmkåpa | obelagt | obelagt | −98 dBm ±1 dB, utan mätvillkor [T] | gränssnittet ja, kretsen obelagd |
| ImmersionRC rapidFIRE (nu Orqa) | obelagt; två skärmade mottagarmoduler mellan två kort, styrda av en processor med eget kommandoprotokoll | [T] manual v1.6; [F] mottagarna syns bara från sidan; [K] eget protokoll i ExpressLRS Backpack | obelagt | obelagt | "stable image at close to −100dBm", utan mätvillkor [T] | obelagt |
| TBS Fusion, också mottagarkorten från 2025 | obelagt; mottagarkorten under skärmkåpor, styrda via CRSF | [T] manual 2025-11-13; [K] CRSF-ram i ExpressLRS Backpack | obelagt | obelagt | −96 dBm, utan mätvillkor [T] | obelagt |
| Fat Shark Scout och Attitude-modulen | obelagt | inget hittat | obelagt | obelagt | ingen siffra hittad | obelagt |

Det som går att belägga talar för samma krets och olika omgivning, men det avgör inte frågan för rapidFIRE, Fusion och Fat Shark:

- **Där kretsen syns är det RTC6715.** HDZero namnger den i koden. SteadyView styrs med RTC6715:s ram och registerkarta (databladets registernamn) och svarar när register läses; en annan krets med samma gränssnitt är möjlig men inte känd [R].
- **RichWave har ingen annan mottagare för 5,8 GHz.** Tillverkarens lista har RTC6715 som enda mottagare i bandet; RTC6716S är mottagare för 1,2/6,5 GHz. Någon känsligare RichWave-krets för 5,8 GHz finns alltså inte att köpa. En krets från en annan tillverkare har ingen av källorna visat.
- **Tillverkarna själva säger att känsligheten ändras med kortet, inte med produkten.** Fusions mottagarkort från före april 2020 byttes mot "a newer revision with higher sensitivity" [T]. rapidFIRE:s andra tillverkningsomgång har "slightly better sensitivity" än den första [T]. SteadyView X för 5 GHz tar också 5,8 GHz men med 1–2 dB sämre känslighet än 5,8 GHz-versionen [T], alltså en annan anpassning framför samma sorts mottagare [R].
- **Siffrorna går inte att jämföra.** RTC6715 anges till −85 dBm med en 15 kHz-ton, ±2,5 MHz deviation och 43 dB SNR; RX5808 till −90 dBm typiskt utan villkor (RF-underlaget avsnitt 1). De dyra mottagarna anger −96, −98 och "nära −100 dBm" för stabil bild, utan villkor. Skillnaden på 6–15 dB kan vara definition lika väl som hårdvara [R].
- **Bardwells påstående är varken belagt eller motbevisat.** Inget dokument, ingen kod och inget foto som går att läsa visar en annan krets.

För rev B: inget pekar på en annan mottagarkrets att välja. Det som skiljer, enligt tillverkarnas egna uppgifter, sitter runt kretsen: filter och eventuell LNA före den, MF-filtret, kortet och matningen. Jämförelsen med en färdig mottagare ska mätas med samma kriterium på bänken ([MATPROTOKOLL.md](../docs/MATPROTOKOLL.md) blad 15) [R].

## FCC

Ingen av de fem mottagarna har ett FCC-ID [FCC]. En apparat som bara tar emot behöver i USA ingen certifiering med FCC-ID (Part 15 B, tillverkarens egen försäkran), så interiörfoton finns bara när apparaten också sänder.

| Tillverkare | Grantee-kod | Ansökningar | Videomottagare bland dem |
|---|---|---|---|
| TBS (Blacksheep IP Holding) | [QOS](https://fccid.io/QOS) | 9: Crossfire-sändare och -mottagare för styrlänken (915 MHz, 2,4 GHz), Tango 2, en videosändare 2012 | nej. Fusion har wifi enligt manualen men ingen egen ansökan under QOS |
| Fat Shark (Shenzhen Fatshark) | [2ABYQ](https://fccid.io/2ABYQ) | 2: sändare FSV2461 och kamera FSV1251, 2014 | nej |
| Divimath (Shenzhen) | [2A2O6](https://fccid.io/2A2O6) | 1: HDZero-sändare HDZ3100, 2021 | nej |
| Divimath, Inc. (Fremont) | [2BS8S](https://fccid.io/2BS8S) | 1: "Divimath Long Range VTX" DVM3130, 2026-01-15, 5769 MHz, interiörfoton offentliga | nej; om sändaren är analog är inte kontrollerat |
| Skyzone | ingen ([sökning](https://fccid.io/search?q=Skyzone)) | — | — |
| ImmersionRC | ingen ([sökning](https://fccid.io/search?q=ImmersionRC)) | — | — |

## Per enhet

### HDZero Goggle 2 och BoxPro (Divimath)

Firmware ([hdzero-goggle, MIT][hdz-rtc]) har en drivrutin `rtc6715.c` som skriver register 00h (värdet 08h), 01h (kanaltabellen) och 0Ah (10DF3h för ljud av, 10C13h för ljud på). Skrivningen går som I2C till FPGA:n, som lägger ut den på kretsens SPI; Goggle 2 och BoxPro har var sin registeradress i FPGA:n. RSSI läses med en 12-bitars ADC. I BoxPro har kretsen en egen påslagssignal (`GPIO_RTC6715_ON`, [gpio.c][hdz-gpio]). Den analoga videon avkodas av en Techpoint TP2825 i båda ([hardware-goggle2.c][hdz-hw2], [hardware-boxpro.c][hdz-hwbp]). Koden nämner ingen LNA eller filter för den analoga delen; raderna om LNA i `dm6302.c` gäller den digitala mottagaren DM6302 och är bortkommenterade. Koden har en enda RTC6715, alltså ingen diversity i den analoga delen.

### Skyzone SteadyView och SteadyView X

ExpressLRS Backpack ([steadyview.h][elrs-svh], [steadyview.cpp][elrs-svc]; GPL-3.0, här bara citerad) definierar för SteadyView registren 00h–0Ah och 0Fh med samma namn som RTC6715-databladet (Synthesizer Register A–D, VCO Switch-Cap Control, DFC Control, 6M och 6M5 Audio Demodulator Control, Receiver Control 1 och 2, Power Down Control, State; [datablad s. 7–11][rtc]). Ramen är RX5808:s (25 bitar, LSB först). Backpack skriver register 00h och 01h, med LO = f − 479 MHz, och läser register tillbaka, vilket RTC6715 klarar (s. 6). Läget Mix väljs med en puls på klockledningen, inte med ett register.

Modulen består av två kort: överst Skyzones "Fusion"-kort (bildbehandlingen; version V3.3 enligt artikeln från december 2022), underst mottagarkortet, märkt RX5G, under en skärmkåpa ([foto][oscar-sv]). Mellan antennkontakterna sitter en komponent i metallkapsel vars märkning inte går att läsa i bilden. Tillverkaren anger "-98dBm±1dBm" utan villkor ([produktsida][skyzone]), att 5G-versionen ("X band") tar 5,8 GHz med "1 or 2 db" sämre känslighet, och säljer en 7,5G-version för 6,5–8,5 GHz. Den versionen ligger långt utanför RTC6715:s 5725–5865 MHz, så Skyzone har minst en annan mottagardel; vilken är obelagt.

### ImmersionRC rapidFIRE (Orqa)

ImmersionRC har upphört; dokumentation och firmware ligger hos Orqa ([meddelandet][irc]). Manualen v1.6, februari 2026 ([Orqa][orqa]): 5,3–6,0 GHz, "Best In Class (stable image at close to -100dBm)" utan mätvillkor (s. 4), två mottagarmoduler, tre tillverkningsomgångar: den första försvunnen, den andra (2019–2022) med "slightly better sensitivity", den tredje tillverkad i EU från januari 2023 med samma prestanda (s. 24). Frekvensområdet 5,3–6,0 GHz ligger utanför RTC6715-databladets; om kretsen går att ställa så långt är inte undersökt. Mottagarmodulerna sitter mellan två kort och syns bara från sidan ([foto][oscar-rf]). Modulen styrs med ett eget kommandoprotokoll ('B', 'C', 'S' med CRC8; [rapidfire.h][elrs-rf]), alltså genom en processor; protokollet säger inget om kretsen.

### TBS Fusion

Manualen, revision 2025-11-13 ([TBS][tbs]): "RF Sensitivity: -96 dBm" utan villkor (s. 1). Mottagarkort köpta före april 2020 ersattes av "a newer revision with higher sensitivity"; tillverkarens bild visar båda korten under skärmkåpor (s. 7). Kort med holografisk etikett, från 2025, har banden M/H/Y/T och "No Audio on newer boards. Due to a global shortage of key filter components" (s. 4). Fusion har wifi för 2,4 GHz. Backpack styr den med en CRSF-ram med frekvensen ([tbs_fusion.cpp][elrs-tbs]), alltså genom en processor.

### Fat Shark Scout och Attitude-modulen

Ingen FCC-ansökan, inget foto med läsbar märkning och ingen källkod hittad. Scout-manualen (revision D) gick inte att läsa ut här, så tillverkarens känslighetsuppgift, om den finns, saknas.

## RichWave, mottagare för video (tillverkarens sida 2026-10-17)

[RichWave Wireless Video/Audio][rw]: tabellen har kolumnerna sändare och mottagare. Ingen rad är märkt ny, NRND eller EOL.

| Krets | Funktion | Band | Kapsel |
|---|---|---|---|
| RTC6711 | mottagare | 2,4 GHz, FM/FSK | 48L QFN 7×7 |
| **RTC6715** | **mottagare** | **5,8 GHz, FM** | 48L QFN 7×7 |
| RTC67133 | mottagare | 1,2/3,3 GHz, FM | 48L QFN 7×7 |
| RTC6716S | mottagare | 1,2/6,5 GHz, FM | 48L QFN 7×7 |

Sändarna i samma tabell: RTC6701 (2,4 GHz), RTC6705 (5,8 GHz), RTC67033 (1,2/3,3 GHz), RTC6706S (1,2/6,5 GHz). Om RTC6716S täcker 5,8 GHz och är stiftkompatibel med RTC6715 går inte att se utan databladet, som ligger bakom inloggning.

## Obelagt

- Kretsen i rapidFIRE, Fusion (alla kortrevisioner), SteadyView och Fat Shark Scout.
- Om någon av dem har LNA eller filter före kretsen, och vilket MF-filter de har.
- Mätvillkoren bakom −96, −98 och "nära −100 dBm".
- Vilken krets Skyzones 7,5G-version använder.
- Om Divimaths sändare DVM3130 är analog.

[rtc]: https://opendevices.ru/wp-content/uploads/2015/02/7058r.pdf
[rw]: https://www.richwave.com.tw/en/page_prd_new.aspx?Id=8
[hdz-rtc]: https://github.com/hd-zero/hdzero-goggle/blob/7f5feac42c/src/driver/rtc6715.c
[hdz-gpio]: https://github.com/hd-zero/hdzero-goggle/blob/7f5feac42c/src/driver/gpio.c
[hdz-hw2]: https://github.com/hd-zero/hdzero-goggle/blob/7f5feac42c/src/driver/hardware-goggle2.c
[hdz-hwbp]: https://github.com/hd-zero/hdzero-goggle/blob/7f5feac42c/src/driver/hardware-boxpro.c
[elrs-svh]: https://github.com/ExpressLRS/Backpack/blob/d15ed3057e/src/steadyview.h
[elrs-svc]: https://github.com/ExpressLRS/Backpack/blob/d15ed3057e/src/steadyview.cpp
[elrs-rf]: https://github.com/ExpressLRS/Backpack/blob/d15ed3057e/src/rapidfire.h
[elrs-tbs]: https://github.com/ExpressLRS/Backpack/blob/d15ed3057e/src/tbs_fusion.cpp
[oscar-sv]: https://oscarliang.com/skyzone-steadyview-module-fusion-v3-3/
[oscar-rf]: https://oscarliang.com/immersionrc-rapidfire-module/
[skyzone]: https://www.skyzonefpv.com/products/skyzone-steadyview-x-5-8ghz-ips-screen-receiver-module
[irc]: https://www.immersionrc.com/fpv-products/rapidfire/
[orqa]: https://orqafpv.freshdesk.com/support/solutions/articles/48001280674-rapidfire
[tbs]: https://www.team-blacksheep.com/media/files/tbs-fusion-manual.pdf
