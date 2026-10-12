# Material för uppstarten på bänken

Vad som behövs för stegen M0, M3, M2a, M4 och M6 i Core `gateware/BRINGUP.md`, utöver en dator med verktygskedjan. En rad per sak: hur många, vilket steg som behöver den först, vad som händer utan den och varifrån uppgiften kommer. Inga butiker, priser eller länkar. Skrivet 2026-10-12 ur Core `main` 3d4ed8f; inget av det här är provat på kortet än.

Stegen i ordning: M0 testbild, M2a minnestest, M3 kopplingsprob, M4 två dekodrar och mixer, M6 meny och mätlogg. M2a kan köras direkt efter M0 (BRINGUP 2.1).

## FPGA-kortet och anslutningar

| Sak | Antal | Första steg | Utan den | Källa |
|---|---:|---|---|---|
| Tang Nano 20K, **rev 3923** (revisionen står på undersidan) | 1 | M0 | Inget går. Rev 3921 fungerar inte med stiftplanen (stift 75 till BL616 BOOT), rev 3850 är inte kontrollerad | BRINGUP 0 "Kortrevision" |
| USB-C-kabel med dataledare | 1 | M0 | Ingen flashning och ingen UART-logg (M2a, M3, M6) | BRINGUP 2 (openFPGALoader, `/dev/ttyUSB1`) |
| HDMI-skärm eller TV som tar 720p60 | 1, gärna 2–3 | M0 | M0 kan inte bedömas. Arbetsplanens mätning M0 är "bild på tre skärmar" | BRINGUP 2; ARBETSPLAN_2026-10-05 "Mätningar när kortet finns" |
| HDMI-kabel | 1 | M0 | Som ovan | BRINGUP 2 |

## Dekodrar och mottagare (M3 och framåt)

| Sak | Antal | Första steg | Utan den | Källa |
|---|---:|---|---|---|
| TVP5150AM1-modul (den vanliga röda) | 2, helst 3 | M3 | M3, M4 och M6 kan inte göras. En tredje är reserv om en skadas vid lödning av resettråden | BRINGUP 0–1; NATTPASS_2026-10-08 M1 |
| Nivåomvandlare TXS0108E, om modulens IO_DVDD (TVP-stift 10) är 1,8 V | 2 per modul (4–6) | M3 | Tang-kortet läser inte 1,8 V-data säkert; proben visar `tog 00 hi 00` | BRINGUP 0 "TVP5150-modulernas spänning", 4 |
| Tunn tråd för RESETB från TVP-stift 8 till J6-18 | 1 per modul | M3 | Dekodern kan inte återställas från FPGA:n (den röda modulen har inget resetstift) | BRINGUP 0 "Reset", 1 "Gemensamt" |
| Pull-up 2,2–4,7 kΩ till 3,3 V på SCL och båda SDA, om modulerna saknar egna | 3 | M3 | I2C svarar inte: proben visar `i2c NA` | BRINGUP 1 "Gemensamt", 4 |
| Kopplingstråd, stiftlister, gemensam jord | cirka 30 ledare (20 för dekoderdata, SCL, RESETB, jord, 3 till RX5808) | M3 | — | BRINGUP 1 (tabellerna för J5, J6) |
| RX5808-mottagare med SPI-moden gjord | 2 | M3 | Utan SPI-moden styrs kanalen av modulens kanalstift, inte av FPGA:n | BRINGUP 1 "RX5808"; Core `gateware/README.md` M6 |
| 5,8 GHz-antenn till varje mottagare | 2 | M3 | Ingen eller svag bild; proben visar låsbitar 0 eller `st` 4–7 | BRINGUP 4 |
| Videokabel från varje mottagares videoutgång till sin TVP-modul | 2 | M3 | Ingen videosignal till dekodern | BRINGUP 1 "RX5808" |
| Separat 5 V-matning till mottagarna, gemensam jord med Tang-kortet | 1 | M3 | Mottagarna har ingen ström | BRINGUP 1 "RX5808" (5 V, GND) |
| Matning till TVP-modulerna enligt deras egen märkning | 1 | M3 | Modulerna startar inte (`no SCLK`) | BRINGUP 0, 4 |

## Signalkälla

| Sak | Antal | Första steg | Utan den | Källa |
|---|---:|---|---|---|
| Analog kamera med 5,8 GHz-sändare, ställd på NTSC, band F kanal 4 (5800 MHz) | 1 | M3 | Ingen bild att låsa på. BRINGUP nämner sändaren LST-S4; hemma finns AIO-kameran S2-OSD | BRINGUP 1 "Sändaren"; `docs/bench/AIO_MONEAGLE_2026-10-09.md` |
| Matning till kameran och sändaren | 1 | M3 | Som ovan. AIO-kameran gav bild vid 4,2 V från bänkaggregat | `docs/bench/AIO_MONEAGLE_2026-10-09.md` |

## M6

| Sak | Antal | Första steg | Utan den | Källa |
|---|---:|---|---|---|
| OLED SSD1306 128×32, I2C adress 3Ch, matad med 3,3 V | 1 | M6 | Menyn syns bara i OSD:n på HDMI | Core `gateware/README.md` M6; BRINGUP 1 "OLED" |
| Knappar | 0 extra | M6 | — M6 använder kortets S1 (OK) och S2 (NEXT). Håll dem släppta när kortet får ström | Core `gateware/README.md` M6; BRINGUP 0 "Knapparna vid start". NATTPASS_2026-10-08 M1 räknade med två knappar; de behövs inte |

## Mät- och felsökningsutrustning

| Sak | Antal | Första steg | Utan den | Källa |
|---|---:|---|---|---|
| Multimeter | 1 | M3 | IO_DVDD på TVP-stift 10 kan inte mätas, och då vet man inte om nivåomvandlare behövs | BRINGUP 0 |
| Oscilloskop | 1 | M3 | SCLK, I2C-flanker och matningsglapp (`ri` stiger) går bara att gissa ur proben | BRINGUP 4; NATTPASS_2026-10-08 M1 |
| Logikanalysator | 1 | M3 | I2C-transaktioner och RX5808-SPI kan inte ses; proben och pull-testet täcker det mesta | BRINGUP 4; NATTPASS_2026-10-08 M1 |
| Lödutrustning | 1 | M3 | Resettråden och RX5808:s SPI-mod kan inte göras | BRINGUP 0 "Reset"; Core README M6 |
| Telefon eller kamera med höghastighetsfilm | 1 | M6 | Ingen glas-till-glas-latens; mätningen "BUF mot HDMI-skärm, upplevd latens" blir en känsla | Core `tests/latency/`; ARBETSPLAN_2026-10-05 "Mätningar när kortet finns" |

## Vad som räcker för vilket steg

| Steg | Behöver |
|---|---|
| M0 | Tang Nano 20K, USB-C, HDMI-skärm och kabel |
| M2a | Tang Nano 20K, USB-C |
| M3 | allt under "FPGA-kortet", "Dekodrar och mottagare", "Signalkälla", plus multimeter och lödutrustning |
| M4 | samma som M3 |
| M6 | samma som M4, plus OLED |
