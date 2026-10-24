# Komponent- och arkitekturkatalog för OpenVRX (2026-10-24)

Underlag och komponentresearch för OpenVRX rev B, Puck och framtida goggle-/dockningsvarianter.
Dokumentet kartlägger komponenter, kretsar, processorer och arkitekturer för att utvärdera:
1. **RF-mottagning:** Från klassisk RichWave RTC6715/RX5808 till mjukvarudefinierad radio (ESP32-C5 och diskreta SDR-frontends).
2. **Signalöverföring:** Analog CVBS vs. direkt digital buss (PARLIO / BT.656 / MIPI-CSI / I/Q).
3. **Signalbehandling & Linjemixning:** FPGA (Gowin/Lattice/Efinix) vs. högpresterande applikationsprocessor (ESP32-P4 / RP2350 / Linux-SoC).
4. **Videoutgång & Displaykompatibilitet:** Från 720p60 till native 1080p60 HDMI/DVI samt USB-C DisplayPort Alt Mode för XR-glasögon (XREAL, Viture, Rokid), FPV-glasögon, fältmonitorer och TV.

---

## 1. Kravprofil per målenhet (Display Matrix)

| Enhetstyp | Typiska modeller | Ingångsformat | Krav på tidsbas / synk | Känslighet för signalbortfall |
|---|---|---|---|---|
| **XR-glasögon** | XREAL Air / Air 2 Pro, Viture Pro XR, Rokid Max | Strikt 1080p60 (CEA-861 VIC 16, 148,5 MHz pixelklocka) via DP Alt Mode / HDMI-adapter | Extremt strikt: konstant radantal (1125 rader), tolererar ej varierande radlängd | Kraschar/visar "rainbow screen" eller "no signal" vid minsta synkglitch. Kräver full TBC och fältbuffert |
| **FPV-goggles (HDMI)** | Walksnail Avatar HD, HDZero Goggles, Skyzone SKY04X, Fat Shark HDO2 | 720p60 eller 1080p60 HDMI | Måttlig till strikt: HDMI-mottagarkretsarna låser snabbt, men vill ha standardtiming | Föredrar låg latens (<20 ms) framför avancerad deinterlacing |
| **Fältmonitorer** | Eachine, Feelworld, Lilliput | 720p50/60, 1080p50/60 HDMI | Förlåtande: accepterar ofta små avvikelser i radantal | Visar blåskärm vid totalt synktapp om ingen stabil TBC finns |
| **Vanlig TV / Datorskärm** | Alla moderna HDMI-skärmar | 720p60, 1080p60 | Standard EDID-timing | Fördröjer ofta bild vid lägesbyten (100–500 ms handskakning) |

---

## 2. Kategori 1: 5,8 GHz RF-Frontends & Mottagarchip

### 2.1 Analoga FM-mottagarchip (Superheterodyn)

| Komponent / Modul | Typ / Funktion | Frekvensband | Gränssnitt | Känslighet (typ) | Styrkor & Svagheter | Lämplighet |
|---|---|---|---|---|---|---|
| **RichWave RTC6715** | Integrerad FM-mottagare (QFN-48) | 5,725–5,875 GHz (kan trimmas bredare) | Analog CVBS ut, analog RSSI, 25-bit SPI (kanaltabell) | −85 till −90 dBm (standard), upp till −98 dBm med extern LNA/filter | **+** Industristandard i 10+ år, beprövad, noll mjukvarulatens.<br>**−** Begränsad känslighet utan skärmad LNA, global komponentbrist periodvis. | **Referens / Baslinje** (Modul RX5808) |
| **RichWave RTC6716S** | FM-mottagare för 1,2 / 6,5 GHz (QFN-48) | 1,2 GHz & 6,5 GHz | Analog CVBS, RSSI, SPI | Obelagd vid 5,8 GHz | Alternativ för framtida bandexpansion, men saknar officiellt 5,8 GHz-stöd. | Forskningsspår |
| **Skyzone RX5G-modul** | Skärmad dubbelmottagarmodul | 5,3–5,9 GHz | Analog CVBS, I2C/SPI | −98 dBm ±1 dB | **+** Utmärkt känslighet och selektivitet.<br>**−** Proprietär modul, sluten leveranskedja. | Referensprodukt |

### 2.2 ESP32 som RF-mottagare (Wi-Fi PHY SDR-approach)

| Krets / Modul | Hårdvarukonfiguration | Dataformat ut | Samplingsfrekvens | Känslighet & Prestanda | Styrkor & Svagheter | Lämplighet |
|---|---|---|---|---|---|---|
| **ESP32-C5** (Seeed XIAO) | Wi-Fi 6 PHY (`MODEM_DIAG`), BitScrambler WBFM | 6-bit CVBS på PARLIO TX (D4–D9) + motståndsstege | 40 MS/s IQ in, 20 MS/s CVBS ut | C/N ~8 dB ger synklås, brusgolv ~−93 dBm | **+** Billig (<$5), kräver ingen extern tuner.<br>**−** Endast 15 tillgängliga pinnar på XIAO; 6-bitars upplösning ger stegning; Wi-Fi-AGC kräver anti-hunt (Direct Gain V5). | **Experiment / Bas-C5** |
| **ESP32-C5-WROOM-1U** (Modul med U.FL) | Wi-Fi 6 PHY, 22 tillgängliga GPIO:er | Full 8-bit digital CVBS eller 7+7 bit rå IQ på PARLIO | 40 MS/s eller 80 MS/s | Betydligt högre tak med 8-bit luma eller extern demodulering | **+** Tillräckligt med stift för både databuss, klocka, UART och antennväxel.<br>**−** Kräver eget kretskort. | **Huvudkandidat för Rev B (C5-spår)** |
| **Waveshare ESP32-C5-Zero** | ESP32-C5-HF4, ingen PSRAM, U.FL/IPEX-1 | 7+7 bit rå IQ ut (zerowidth P4USB-layout) | 80 MS/s modembuss | 97 % synklås vid C/N 3–5 dB i extern demodulator | **+** Bevisad av zerowidth att leverera rå IQ till extern processor.<br>**−** Kräver extern FM-demodulator. | **Bästa dev-kort för IQ-forskning** |

### 2.3 RF Front-End Moduler (LNA & SAW-filter)

| Komponent | Funktion | Frekvens | Förstärkning / Brusfaktor (NF) | Gränssnitt / Styrning | Kommentar |
|---|---|---|---|---|---|
| **Skyworks SKY65377-11** | Lågbrusig förstärkare (LNA) | 5,15–5,85 GHz | Förstärkning: 16 dB, NF: 1,3 dB | Bypass-läge via 1 GPIO | Perfekt frontend framför RTC6715 eller ESP32-C5 för att lyfta svagsignalkänsligheten med 4–6 dB. |
| **Qorvo QPF4528** | Wi-Fi 6 FEM (LNA + PA + Switch) | 5,15–5,925 GHz | LNA Gain: 14 dB, NF: 1,8 dB | 3,3 V logikstyrning | Mycket kompakt, integrerade switchar för antenndiversity. |
| **Tai-Saw TA1248A** | SAW Bandpassfilter | 5,725–5,875 GHz | Insättningsdämpning: ~2,5 dB | 50 Ω impedans, SMD | Dämpar 2,4 GHz (RC-länk / ELRS) med >40 dB och 5,2 GHz Wi-Fi med >30 dB. Minskar intermodulation drastiskt. |

### 2.4 Reella SDR-Kretsar (Software Defined Radio Transceivers)

| Komponent | Arkitektur | Frekvensomfång | Bandbredd | RF-kanaler | Gränssnitt | Kommentar |
|---|---|---|---|---|---|---|
| **ADI AD9361** | Bredbandig RF Agile Transceiver | 70 MHz – 6,0 GHz | 200 kHz – 56 MHz | 2x RX, 2x TX | Dual LVDS eller 12-bit CMOS | **Guldstandarden för äkta RF-diversity.** Kan sampla båda 5,8 GHz-antennerna fas-koherent. Dyr ($150+), drar 1–2 W, kräver stor FPGA. |
| **ADI AD9364** | Bredbandig RF Agile Transceiver | 70 MHz – 6,0 GHz | 200 kHz – 56 MHz | 1x RX, 1x TX | 12-bit LVDS/CMOS | Enkanalsversion av AD9361. Något lägre effekt, samma RF-prestanda. |
| **ADI ADL5380** | Bredbandig I/Q-demodulator | 400 MHz – 6,0 GHz | Basband upp till 390 MHz | 1x RX (I/Q) | Differentiell analog I/Q ut | Kräver extern lokaloscillator (t.ex. ADF4351) och snabba ADC:er. Byggblock för egen diskret mottagare. |

---

## 3. Kategori 2: Video-Avkodare (CVBS till Digital BT.656 / MIPI)

När mottagaren levererar analog kompositvideo (CVBS) krävs en avkodare för att digitalisera linjerna till komponentvideo (YCbCr).

| Komponent | ADC-upplösning | Utgångsformat | Klocka | Effektförbrukning | Synkegenskaper | Status & Kommentar |
|---|---|---|---|---|---|---|
| **TI TVP5150AM1** | 9-bit ADC | 8-bit BT.656 (YCbCr 4:2:2) | 27 MHz | **115 mW** (ultralåg) | Godkänd synk vid måttligt brus; tappar färglås och fas vid djup snö | **Nuvarande baslinje i OpenVRX Rev A.** Beprövad och fungerar i simulering. |
| **ADI ADV7180** | 10-bit ADC | 8-bit BT.656 | 27 MHz | ~200 mW | Adaptivt 4H-kamfilter, godkänd låsning vid brus | Finns i fordon och industri. Ersättare till TVP5150 med bättre färgåtergivning. |
| **ADI ADV7280 / ADV7282-M** | 10-bit ADC | **ADV7280:** 8-bit BT.656<br>**ADV7282-M:** MIPI-CSI-2 (1 lane) | 27 MHz / MIPI D-PHY | ~180 mW | **"Fast Lock"-läge:** låser på under 1 fält efter signalbortfall | **Mycket intressant för P4:** ADV7282-M kan mata CVBS direkt in i ESP32-P4:s MIPI-CSI-port utan FPGA! |
| **Techpoint TP2825** | 10-bit ADC | 8/16-bit BT.656 / Digital RGB | 27 / 54 MHz | ~350 mW | Extremt aggressiv synkföljning vid dålig RF | **Används i HDZero BoxPro och Goggle 2** för analog ingång. Bevisad i FPV-sammanhang. |
| **Renesas / Intersil TW9912** | 10-bit ADC | 8-bit BT.656 | 27 MHz | ~250 mW | Automotive grade, konstruerad för att aldrig krascha vid brutna synkpulser | Utmärkt alternativ till TVP5150 för tuffa RF-miljöer. |

---

## 4. Kategori 3: FPGAs & Logikkretsar (Realtids DSP, Mixning & HDMI)

| Komponent / Kort | Logikelement | Block-RAM / SDRAM | Högsta serialiserarhastighet | Verktygskedja | Typisk kostnad | Kommentar |
|---|---|---|---|---|---|---|
| **Gowin GW2AR-18** (Tang Nano 20K) | 20 736 LUT4 | 828 kbit B-RAM + **64 Mbit internt SDRAM** (32-bit buss) | 1 200 Mbit/s (LVDS/OSER10) | Öppen (Apicula, nextpnr) & Gowin EDA | ~$20 (devkit) | **Nuvarande plattform för M0–M6.** Genererar 720p60 native HDMI utan externa chip. Saknar bandbredd för 1080p60 TMDS. |
| **Gowin GW5A-25** (Tang Primer 25K) | 25 000 LUT4 | 1 000 kbit B-RAM, extern DDR3/SDR | **2 000 Mbit/s** (OSER10) | Apicula (experimentell) & Gowin EDA | ~$25–35 (modul) | **Klarar native 1080p60 TMDS (1 485 Mbit/s)!** Den renaste vägen till direkt XR-glasögondrivning utan extern HDMI-sändarkrets. |
| **Efinix Trion T20 / Ti35** | 20K–35K LE | 1–2 Mbit B-RAM, hårdvaru-MIPI | Upp till 1 500 Mbit/s per lane | Efinity | ~$15–30 | Extremt strömsnål. Har dedikerade hårda MIPI CSI/DSI-block. Idealisk för inbyggnad i små goggle-sidecars. |
| **Lattice ECP5** (LFE5U-25F / 45F) | 24K–44K LUT | 1–2 Mbit B-RAM, extern SDRAM/DDR | **3 200 Mbit/s (SerDes)** | Helt öppen (Yosys + Project Trellis) | ~$30–45 | Guldstandarden för open-source FPGA. SerDes-blocken hanterar 1080p60 HDMI, DisplayPort och MIPI utan minsta ansträngning. |

---

## 5. Kategori 4: Processorer, Mikrokontrollers & SoCs

| Processor | Kärnor & Klocka | Displaygränssnitt ut | Videoingångar in | Hårdvaruacceleration | Latens (estimerad) | Roll i projektet |
|---|---|---|---|---|---|---|
| **Espressif ESP32-P4** | Dual-core RISC-V @ 400 MHz | **MIPI-DSI (2 lanes, 1,5 Gbps)**, stöder extern HDMI-brygga | MIPI-CSI (2 lanes), PARLIO RX (16-bit), DVP Camera | H.264 Encoder/Decoder, 2D Pixel Accelerator (PPA), DMA | 1–2 bildrutor (16–33 ms) | **Huvudkandidat för ren MCU-väg.** Kan ta emot digital video från C5 via PARLIO och driva HDMI via LT8912B. |
| **Raspberry Pi RP2350** | Dual Cortex-M33 / Hazard3 @ 150+ MHz | **HSTX (High-Speed Serial Transmit)** för direkt DVI/HDMI (upp till 720p) | PIO (Programmerbar I/O) | Inga fasta videoenheter, men extremt flexibla PIO-state machines | 1 bildruta (16 ms) | Intressant som lågkostnadskontroller med direkt DVI-utgång, men saknar minnesbandbredd för dubbla videoströmmar. |
| **Allwinner T113-S3** | Dual Cortex-A7 @ 1,2 GHz + HiFi4 DSP | Parallell RGB, LVDS, MIPI-DSI, CVBS ut | **Integrerad CVBS-videoingång (TVD)** direkt på chippet! | H.264/JPEG dekoder, 64 MB internt DDR3 | 40–80 ms (under Linux V4L2) | Kan ta analog CVBS direkt utan TVP5150 och spotta ut HDMI via RGB-brygga. Tyvärr hög mjukvarulatens. |
| **Allwinner V853** | Cortex-A7 @ 1 GHz + 1 TOPS NPU + RISC-V E907 | MIPI-DSI, RGB | MIPI-CSI (4 lanes), DVP | H.264/H.265 enc/dec, internt DDR3 | 30–60 ms | IP-kamera-SoC. Kraftfull för digital videolänk, men överdrivet komplex för ren analog mottagning. |

---

## 6. Kategori 5: HDMI-Sändare, Bryggor & Skalarkretsar

| Komponent | Ingångsformat | Utgångsformat | Max upplösning | Kontrollgränssnitt | Kommentar |
|---|---|---|---|---|---|
| **Lontium LT8912B** | MIPI-DSI (1–4 lanes) | HDMI 1.4 / DVI | 1080p@30Hz, **720p@60Hz** | I2C | Standardbryggan på ESP32-P4-kort (t.ex. Olimex P4-PC). Kräver 3,3 V och 1,8 V. |
| **Lontium LT8618SX / SXB** | 16-bit BT.1120 eller 24-bit RGB | HDMI 1.4 | **1080p@60Hz** (148,5 MHz) | I2C (enkel registerkarta) | **Perfekt följeslagare till Tang Nano 20K:** Låter FPGA:n skicka 1080p60 parallellt i 148,5 MHz medan LT8618 sköter TMDS-serialiseringen! Mycket strömsnål (~150 mW). |
| **Analog Devices ADV7513** | 16-bit YCbCr 4:2:2 (BT.1120) eller 24-bit RGB | HDMI 1.4b med fulla Infoframes | **1080p@60Hz**, 165 MHz | I2C, fullt dokumenterad | Högkvalitativ sändare. Fullt stöd för AVI Infoframes (RGB/YCbCr, Full/Limited range) vilket löser alla färgomfångsproblem i skärmar och glasögon. |
| **Texas Instruments TFP410** | 24-bit RGB eller 12-bit DDR RGB | DVI 1.0 (TMDS) | 1080p@60Hz (165 MHz) | Hårdvarukonfigurerad (inga register krävs!) | Mycket enkel att starta upp (noll I2C-kod behövs). Nackdel: Skickar ren DVI utan HDMI-paket, vilket kan få vissa TV-apparater att gissa fel färgomfång. |
| **Parade PS176 / Realtek RTD2172** | HDMI 2.0 / DP 1.2 | **USB-C DisplayPort Alternate Mode** | 4K@60Hz / 1080p@120Hz | Autonom | Gör att pucken kan ha en direkt USB-C-port med DP Alt Mode och 5 V-matning direkt till XR-glasögon utan externa adapterdosor! |
| **Macrosilicon MS1858 / MS1824** | Analog CVBS | HDMI 1080p (inbyggd skalare) | 1080p60 | I2C (eller intern ROM) | Finns i billiga AV2HDMI-dosor. **Rekommenderas ej:** Hög latens (60–120 ms) och blåskärmar vid minsta RF-brus. |

---

## 7. Kategori 6: Strömförsörjning, USB-C PD & Lågbrusreglering

Mottagare och ADC:er är extremt känsliga för switchrippel från DC/DC-omvandlare (vilket syns som diagonala ränder i videobilden).

| Komponent | Funktion | Inspänning | Utspänning / Ström | Brustal / PSRR | Kommentar |
|---|---|---|---|---|---|
| **WCH CH224K** | USB-C PD Sink Controller | 4–22 V (USB-C) | Begär 9 V, 12 V, 15 V eller 20 V hårdvarumässigt via motstånd | — | Extremt liten (ESSOP-10), noll mjukvara krävs. Låter pucken matas från valfri USB-C PD powerbank. |
| **Analog Devices LT3045** | Ultralågbrusig LDO | 1,8–20 V | Ställbar (t.ex. 3,3 V @ 500 mA) | **0,8 µVRMS brus**, 76 dB PSRR vid 1 MHz | **Bästa LDO:n för RF & Video-ADC:** Eliminerar allt switchbrus från batteriomvandlare. |
| **TI TPS62840** | Högeffektiv Step-Down (Buck) | 1,8–6,5 V | 3,3 V / 1,8 V @ 750 mA | Mycket låg rippel vid lätt last, ultralåg IQ (60 nA) | Utmärkt som primärregulator från 1S/2S Li-ion batteri före LDO:er. |

---

## 8. Djupdykning: De fyra arkitekturvägarna framåt

### Arkitektur A: "Pure ESP32 Route" (Ingen FPGA)
```
[Antenn] ──► [ESP32-C5] (RF + BitScrambler WBFM)
                   │  (7+7 bit IQ eller 8-bit digital CVBS via PARLIO @ 40/80 MHz)
                   ▼
             [ESP32-P4] (Dual 400 MHz RISC-V, Synk/Line Buffer i PSRAM, LVGL OSD)
                   │  (MIPI-DSI, 2 lanes)
                   ▼
             [LT8912B] (MIPI till HDMI-brygga)
                   │
                   ▼
             [HDMI-port] (720p60 / 1080p30)
```
* **Fördelar:**
  - Helt och hållet inom Espressifs ekosystem (ESP-IDF, ren C/C++, inga FPGA-verktyg behövs).
  - ESP32-P4 har enorm CPU-kraft och 2D-accelerator för snygga menyer, kanalscanning och Wi-Fi/Bluetooth-telemetri.
* **Kritiska flaskhalsar & Risker:**
  - **Latens:** Att buffra frames i PSRAM och driva MIPI-DSI via DMA ger oundvikligen 1–2 bildrutors latens (minst 16–33 ms).
  - **Diversity:** Att köra två ESP32-C5:or in i en ESP32-P4 och göra linje-för-linje-mixning i mjukvara på mikrosekundnivå pressar DMA-bussen till dess absoluta gräns.
  - **XR-glasögon:** P4 + LT8912B är bevisad för 720p60 och 1080p30. Att nå stabil 1080p60 med konstant CEA-861-radantal för kräsna XR-glasögon är inte garanterat.

---

### Arkitektur B: "Direct Digital C5 till FPGA" (Det hybrida genombrottet)
```
[Antenn A] ──► [ESP32-C5-WROOM-1U #A] (RF) ──(8-bit CVBS + 40 MHz CLK)──┐
                                                                         ├──► [Tang Nano 20K] (Mixer + TBC + SDRAM)
[Antenn B] ──► [ESP32-C5-WROOM-1U #B] (RF) ──(8-bit CVBS + 40 MHz CLK)──┘         │ (TMDS native)
                                                                                   ▼
                                                                             [HDMI-port] (720p60)
```
* **Fördelar:**
  - **Skippar både motstånds-DAC och analog TVP5150:** Inga analoga kvalitetsförluster eller felmatchade impedanser.
  - Använder C5:ans interna BitScrambler-demodulering, men skickar rena digitala sampel direkt till FPGA:n.
  - FPGA:n gör det den är bäst på: digital synkseparation, snömätning, mikrosekund-linjemixning och bergfast HDMI-generering med **<1 ms latens**.
* **Kritiska flaskhalsar & Risker:**
  - FPGA-gatewaren måste själv göra synkextraktion och färgdemodulering (PAL/NTSC subcarrier-lås) ur de digitala samplen (det arbete som startades i `DIGITAL_INGANG.md`).

---

### Arkitektur C: "Classic OpenVRX" (Tang Nano 20K + TVP5150 + RX5808 / C5)
```
[Antenn A] ──► [RX5808 / C5 Analog] ──► [TVP5150AM1 #A] (BT.656) ──┐
                                                                     ├──► [Tang Nano 20K] (Mixer + SDRAM)
[Antenn B] ──► [RX5808 / C5 Analog] ──► [TVP5150AM1 #B] (BT.656) ──┘         │ (TMDS native)
                                                                               ▼
                                                                         [HDMI-port] (720p60)
```
* **Fördelar:**
  - **M0-testbilden fungerar redan fysiskt på bänken (bekräftat 2026-10-20).**
  - 790+ godkända simuleringstester i repot. TVP5150 levererar färdigavkodad YCbCr 4:2:2 så FPGA:n slipper färgdemodulering.
  - Lägst utvecklingsrisk på kort sikt.
* **Kritiska flaskhalsar & Risker:**
  - Kräver analoga mottagarmoduler (RX5808) som har osäker framtida tillgång, eller C5 med motstånds-DAC.
  - TVP5150-avkodaren kan tappa färglåset vid djup snö.

---

### Arkitektur D: "Next-Gen 1080p XR-Native" (Gowin GW5A / Tang Primer 25K)
```
2x Digital RF In (C5 eller SDR) ──► [Gowin GW5A-25] ──(2.0 Gbps OSER10)──► [HDMI / Type-C DP Alt Mode]
                                    (Linjemix, 1080p skalare, TBC)         (Strikt 1080p60 CEA-861)
                                                                                   │
                                                                                   ▼
                                                                         [XR-glasögon: XREAL / Viture]
```
* **Fördelar:**
  - **Fulländad XR-kompatibilitet:** GW5A-25 har 2,0 Gbps serialiserare och driver äkta 1080p60 TMDS (148,5 MHz pixelklocka) direkt utan externa sändarkretsar.
  - Kan skala 480i/576i direkt till 1080p60 med linjär interpolation och konstant 1125-raders timing.
* **Kritiska flaskhalsar & Risker:**
  - Kräver extern DDR3-krets (GW5A-25 har inte 64 Mbit internt SDRAM som GW2AR-18).
  - Något dyrare FPGA-kort.

---

## 9. Rekommenderade komponentval för inköp & framtida layout

1. **För direkt digital C5-bänkprovning (Arkitektur B):**
   - **Waveshare ESP32-C5-Zero** (eller DevKitC-1) med U.FL-kontakt, för att testa 8-bitars PARLIO-utgång och rå IQ utan XIAO:ns stiftbegränsningar.
2. **För ren MCU-forskning (Arkitektur A):**
   - **Olimex ESP32-P4-PC** (ESP32-P4 med integrerad LT8912B HDMI-utgång och Ethernet/USB).
3. **För stabil RF-förstärkning:**
   - **Skyworks SKY65377 LNA-modul** eller diskret RF-frontend med 5,8 GHz SAW-filter.
4. **För 1080p-utgång till XR-glasögon på Tang Nano 20K:**
   - Utvärderingsmodul med **Analog Devices ADV7513** eller **Lontium LT8618SX** (parallell BT.1120 in $\rightarrow$ 1080p60 HDMI ut).
5. **För strömmatning:**
   - **WCH CH224K** USB-C PD Sink-kort (begär 9 V / 12 V direkt från powerbank).
   - **Analog Devices LT3045** ultralågbrusig LDO för 3,3 V-matning till RF-delarna.

---

## 10. Referenser & Källor

- **C5VRX Uppströms:** [github.com/Twotoz/C5VRX](https://github.com/Twotoz/C5VRX) (GPL-3.0)
- **zerowidth P4USB PR #3:** [github.com/zerowidth/C5VRX/pull/3](https://github.com/zerowidth/C5VRX/pull/3) (7+7 bit IQ på 80 MS/s från C5 till P4)
- **Espressif ESP32-C5 Datablad:** [documentation.espressif.com](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)
- **Espressif ESP32-P4 Datablad & EVB:** [docs.espressif.com](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32p4/)
- **Lontium LT8912B & LT8618SX:** [lontiumsemi.com](https://www.lontiumsemi.com)
- **OpenVRX Interna underlag:**
  - [`docs/design/2026-10-24/DIGITAL_INGANG.md`](../docs/design/2026-10-24/DIGITAL_INGANG.md)
  - [`research/C5VRX_EKOSYSTEM_2026-10-24.md`](C5VRX_EKOSYSTEM_2026-10-24.md)
  - [`research/C5VRX_8BIT_HARDVARA_2026-10-24.md`](C5VRX_8BIT_HARDVARA_2026-10-24.md)
  - [`research/UTGANG_1080P_2026-10.md`](UTGANG_1080P_2026-10.md)
  - [`research/XR_GLASOGON_KOMPATIBILITET.md`](XR_GLASOGON_KOMPATIBILITET.md)
