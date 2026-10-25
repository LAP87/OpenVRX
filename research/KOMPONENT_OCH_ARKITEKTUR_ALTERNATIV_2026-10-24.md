# Komponent- och arkitekturalternativ för OpenVRX

Ursprungligt AI-underlag 2026-10-24, faktagranskat och omarbetat 2026-10-25. Originalet finns i Git, navcommit `fee21c0`. **Det var en kandidatlista, inte ett verifierat konstruktions- eller inköpsunderlag.** Flera avgörande specifikationer var fel. Tabellen nedan skiljer tillverkaruppgifter från projektets simuleringar och sådant som fortfarande saknar stöd.

Måndagens praktiska arbete: [fryst C5-bygge, kopplingsschema och körordning](../docs/bench/MANDAG_2026-10-26.md). Utgångsvalet behandlas mer utförligt i [extern skalare mot Primer 25K](HDMI_SKALNING_PRIMER_25K_2026-10-25.md).

## 1. Rättelser som påverkar våra beslut

| Ursprungligt antagande | Granskat läge / konsekvens |
|---|---|
| SKY65377-11 är en 5,8 GHz-LNA | **Fel frekvensband.** Skyworks beskriver den som en **450 MHz T/R-FEM**. Den tas bort ur 5,8 GHz-spåret. [Tillverkarens produktblad](https://www.skyworksinc.com/-/media/F08B6516C8B74C59A2F1D107028739C1.pdf). |
| ADF4351 kan vara LO till ADL5380 på 5,8 GHz | **Inte direkt:** ADF4351 slutar vid 4,4 GHz. ADF4356 täcker till 6,8 GHz och är en möjlig LO-kandidat, med ny kontroll av fasbrus, drivnivå och filtrering. [ADF4351](https://www.analog.com/en/products/ADF4351.html), [ADF4356](https://www.analog.com/en/products/adf4356.html). |
| ESP32-C5-WROOM ger redan full 8-bitars CVBS | Fler stift är en möjlighet, inte en färdig demodulator. Upstream säger **sex verkliga utgångsbitar**; utökad precision kräver nya LUT-/demodulatorprogram. [Utvecklarens svar](https://github.com/Twotoz/C5VRX/issues/256#issuecomment-6390572931). |
| LT8912B är begränsad till 1080p30 | **Fel för själva kretsen:** tillverkaren anger 1080p60, upp till fyra DSI-lanes à 1,5 Gbit/s, kontinuerlig klocka. En viss P4-kombination måste ändå provas med sitt laneantal och RGB-format. [LT8912B produktblad](https://www.lontiumsemi.com/UploadFiles/2022-03/LT8912B_Brief_R1.3.pdf). |
| ADV7513/LT8618 är färdiga uppskalare till Nano | De är HDMI-sändare för en redan skapad videoström. FPGA:n måste skapa 1080p-bilden och klara pixel-/minnestiming. [ADV7513](https://www.analog.com/en/products/adv7513.html). |
| PS176 ger HDMI→USB-C DP Alt Mode | **Fel riktning:** PS176 tar DisplayPort in och ger HDMI ut. En sådan adapter kan inte bara vändas. [Parade PS176](https://www.paradetech.com/products/ps176/). |
| Primer 25K har 25 000 LUT och måste ha DDR3 | Kortet har **23 040 LUT4** och externt minne som tillval. Sipeed erbjuder **SDR-SDRAM**. HDMI ansluts med separat PMOD_DVI, inte en inbyggd port. [Sipeed kort](https://en.wiki.sipeed.com/hardware/en/tang/tang-primer-25k/primer-25k.html), [moduler](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD). |
| LFE5U-25/45 har 3,2 Gbit/s SERDES | **Fel variant:** LFE5U har inga sådana SERDES-kanaler; de finns i LFE5UM/UM5G. Ett snabbt SERDES-tal räcker dessutom inte som verifiering av TMDS, DP eller D-PHY. [Lattices familjetabell](https://www.latticesemi.com/Products/FPGAandCPLD/ECP5). |
| P4 har H.264-kodare/avkodare och egen Wi-Fi/BT | Tillverkaren anger **H.264-kodare**, JPEG-codec och PPA. P4 har ingen egen Wi-Fi-radio; sådan uppkoppling kräver en separat krets. [P4-datablad](https://documentation.espressif.com/esp32-p4_datasheet_en.html), [Olimex kortbeskrivning](https://www.olimex.com/Products/IoT/ESP32-P4/ESP32-P4-PC/open-source-hardware). |
| P4 får oundvikligen minst 1–2 bildrutor | Inte ett hårdvarukrav som kan slås fast från databladet. Latensen följer DMA-/bufferdesignen, synkreglerna och programmet. Någon mätning av vår P4-mixer finns inte. |
| TPS62840 kan matas direkt från 2S Li-ion | **Fel:** högsta inspänning är 6,5 V; full 2S Li-ion är 8,4 V. [TI TPS62840](https://www.ti.com/product/TPS62840). |
| LT3045 eliminerar allt switchbrus | Ingen regulator gör det. ADI anger brus och PSRR vid bestämda villkor; layout, dropout, last och värme återstår. [ADI LT3045](https://www.analog.com/en/products/lt3045.html). |
| Alla XR kräver full bildbuffert och alla skalare lägger till en bildruta | För kategoriska slutsatser. Konstant korrekt utgångstiming behöver säkras, men line buffers/genlock kan vara möjliga. Format och latens verifieras per glasögon, brygga och skalarläge. Se [latensnoten](HDMI_SKALNING_PRIMER_25K_2026-10-25.md). |

Siffror som ”−98 dBm”, ”4–6 dB bättre” eller ”aldrig blåskärm” tas inte vidare utan källa, modulation, bandbredd, bildkriterium och mätvillkor. Video-SNR, RF C/N och dBm-känslighet är olika mått.

## 2. Mottagarvägarna, rangordnade för vårt nästa steg

| Spår | Vad vi har | Vad som återstår | Roll |
|---|---|---|---|
| **C5, digital komposit → Nano** | M4 `DIGIN=1`, sex bitar, modell och sparad byggd bitström. Privat C5-klockbygge från `388d2d1`. | Måndagens klock-/gråskaleprov, verkliga sampel och färgavkodning. | Första praktiska spåret; hoppar över DAC och TVP för denna kanal. |
| **C5, rå IQ → FPGA** | Core `iq_demod_ref.py`, syntetisk FM-/brusmodell. | RF-gränssnitt, fasföljning/begränsning, verkliga sampel, RTL, resurser och ny bänk. | Nästa kvalitetsundersökning, ingen färdig mottagare ännu. |
| **C5/RX5808 → TVP5150 → Nano** | En C5/DAC/TVP-kamerabild har visats på HDMI enligt bänknoten 22 oktober. | RX5808 och tvåkanalsdiversity på hårdvara. | Referens och återgångsväg; behöver inte byggas bort nu. |
| **ADL5380 + LO + dual ADC → FPGA** | Dokumenterade byggblock, nedan. | En hel RF-/analog-/digitaldesign och mätning. | Långsiktig RichWave-fri egen mottagare, inte en billig drop-in-modul. |
| **AD9361/AD9364 → FPGA/SoC** | Integrerade SDR-kretsar med ADC och frekvenssyntes. | Kort, RF-ingång, klockor, styrprogram, FM-demod och kostnadsbudget. | Referensarkitektur; inget skäl att köpa en dyr SDR-plattform för måndagsprovet. |

C5-spåret är ett användande av Wi-Fi-kretsens diagnostikfunktioner; det ska inte beskrivas som ett av tillverkaren garanterat analog-FPV-gränssnitt. [C5VRX](https://github.com/Twotoz/C5VRX) är extern GPL-firmware. Ingen kod därifrån kopieras in i OpenVRX:s CERN-OHL-källor.

## 3. AD-spåret: vad som faktiskt måste tillkomma

```text
antenn → bandfilter/LNA → RF-balun → ADL5380 → I/Q-filter + ADC-drivning
                                         ↑             ↓
                             5,8 GHz-LO/PLL     två synkrona ADC-kanaler
                                                       ↓
                                           FPGA: FM → komposit → färg/mixer
```

- **ADL5380**, RF och LO 400 MHz–6 GHz, differentiell analog I/Q ut, 5 V-matning. Produktion / rekommenderad för nya konstruktioner på ADI:s sida 25 oktober. Den är en quadrature downconverter, **inte en komplett FM-videomottagare**. Många framhävda NF-/linjäritetstal gäller 900/1900 MHz och får inte märkas om till 5,8 GHz. [Produkt och datablad](https://www.analog.com/en/products/adl5380.html).
- **ADF4356**, syntes till 6,8 GHz, rekommenderad för nya konstruktioner enligt ADI. Möjlig LO-kandidat där ADF4351 inte räcker. Kräver referens, loopfilter, matning och rätt LO-nivå. Ingen färdig komponentkombination är godkänd här. [Produkt](https://www.analog.com/en/products/adf4356.html).
- **Nytt fynd: AD9231**, dual 12-bitars ADC med varianter 20/40/65/80 MS/s, differentiella ingångar och testmönster. ADI anger Production. Kandidat för synkron I/Q-infångning; analog drivning, common-mode, anti-aliasfilter, databusspinnar och klockjitter måste dimensioneras. En dual ADC räcker till I och Q för **en** RF-mottagare, inte två diversitetsmottagare. [Produkt](https://www.analog.com/en/products/ad9231.html).
- **AD9361** integrerar 2×RX/2×TX, 12-bitars dataväg, RX 70 MHz–6 GHz och programmerbar bandbredd till 56 MHz. Antennfas, kalibrering och koherent kombination blir inte lösta automatiskt bara för att två kanaler finns. [Produkt](https://www.analog.com/en/products/ad9361.html).

JLC-monterade komponenter kan minska monteringsarbetet, men ADL5380:s styckpris är inte en kostnad för en komplett mottagare. Vi behöver räkna PLL, referens, två ADC-kanaler, RF-/basbandsfilter, drivsteg, matningar, kontakter och kortets RF-layout innan ”under 1 000 kr” går att bedöma. Ingen aktuell inköpskorg är kontrollerad i denna granskning.

### RF-filter och förstärkare

**QPF4528** är en riktig 4,9–5,925 GHz FEM med PA, switch och bypassbar LNA; Qorvo anger Production, cirka 15 dB RX-gain och 2 dB NF. Den tidigare katalogens 14 dB/1,8 dB ersätts av tillverkaruppgiften. Det är inte bara en LNA och PA-delen behövs inte för vår mottagare. Styrtillstånd, maximal insignal och filtrering måste granskas. [Qorvo](https://www.qorvo.com/products/p/QPF4528).

En extern LNA kan hjälpa när systemets brusfaktor begränsar, men kan också överstyra C5 eller förstärka störningar. En angiven förbättring i dB kräver kaskadberäkning och mätning. **SKY65377-11 används inte i 5,8 GHz-designen.** Tai-Saw TA1248A:s tidigare påstådda 5,8 GHz-band och rejectiontal har inte verifierats mot ett tillverkarblad; de är borttagna som konstruktionsvärden.

## 4. Avkodare och processorer

| Kandidat | Bedömning nu |
|---|---|
| TVP5150AM1 | Befintlig analog referens. Digital C5-komposit kan ersätta just denna omvandlingsväg, men FPGA:n måste då göra synk och färgavkodning. |
| ADV7180 / ADV728x | Möjliga alternativa CVBS-avkodare. Exakt suffix avgör parallell respektive MIPI-utgång. Ingen bevisad kvalitetsvinst över vår TVP på snöig FPV finns här. |
| ADV7280-M / ADV7282-M + P4 | Intressant MIPI-väg, men kompatibelt kontaktnamn räcker inte. ADI varnar för varierande fältlängder och buffer overflow i sökläge. I2P är linjeinterpolation, inte automatiskt en helbildsbuffert. [ADI AN-1337](https://ez.analog.com/cfs-file/__key/communityserver-discussions-components-files/331/AN_2D00_1337.pdf), [ADI:s applikationssvar](https://ez.analog.com/video/f/q-a/9323/adv7280-deinterlacing-question). |
| ESP32-P4 | Har MIPI CSI/DSI, PPA, JPEG och H.264-kodare. Olimex P4-PC har HDMI-brygga på kortet och kan vara ett sidospår för UI, inspelning eller en receiver utan FPGA. Ingen garanti för dubbla C5-bussar, linjemixning eller viss latens utan en faktisk implementation. |
| RP2350 | HSTX/PIO är användbart, men inget verifierat byte för dagens tvåkanalsmixer. 720p via överklockade exempel är inte ett garanterat standardläge för all last. [Raspberry Pi](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html). |
| Allwinner T113/V853 | Möjliga SoC-spår men inte tillräckligt granskade för en bestämd latens, TVD-/displaykonfiguration eller kortrekommendation. Tidigare 30–80 ms-tal saknar en definierad pipeline och tas bort. |
| TP2825, TW9912 och ”Skyzone RX5G” | Tidigare exakta egenskaper, användning i namngivna goggles och påstådda snöfördelar saknar tillräckligt primärstöd i underlaget. Inga inköp eller BOM-val baseras på dem. |

## 5. FPGA och videoutgång

| Plattform / krets | Verifierbar möjlighet | Begränsning för oss |
|---|---|---|
| Nano 20K / GW2AR-18 | Befintlig 720p-kedja och SDRAM i kapseln. | Direkt 1080p60 kräver 1,485 Gbit/s per TMDS-par, över det tidigare dokumenterade 1,2 Gbit/s-taket för denna krets. |
| Primer 25K / GW5A-25 | 23 040 LUT, 1 008 kbit BSRAM, PMOD_DVI och separat SDRAM-modul. Databladets OSER10-tak 2 Gbit/s passar 1080p60. | Ingen färdig OpenVRX-port eller uppmätt 1080p/XR-acceptans. Minneskontroller, Fmax och stiftbudget kräver arbete. |
| ECP5 | Bra öppen verktygskedja; rätt UM/UM5G-variant har snabba SERDES. | U-varianten har inte dessa. TMDS, DP och MIPI har olika elektriska/protokollkrav och är inga automatiska följder av bitraten. |
| Efinix Trion | T20 och andra utvalda kapslar har hårda MIPI-block enligt [Efinix](https://www.efinixinc.com/products-trion.html). | ”Trion T20 / Ti35” blandade familjer; verifiera exakt produkt/kapsel. Inget portningsarbete är gjort. |
| ADV7513 | Dokumenterad 165 MHz HDMI-sändare med AVI-infoframes. | Ingen skalare. ADI anger också att köp kräver HDMI-adopterstatus; det måste utredas före produkt-BOM. |
| TFP410 | TI anger Active och 165 MHz DVI-sändare, 24-bitars SDR eller 12-bitars DDR ingång. [TI](https://www.ti.com/product/TFP410). | Ingen skalare eller HDMI-infoframes. Kräver ändå snabb parallell video från FPGA:n. |
| LT8912B | Tillverkarbladet anger 1080p60 HDMI. | DSI-brygga, inte en parallell videoutgång som kan kopplas rakt till nuvarande Nano-stiftplan. |
| LT8618SX/SXB | Parallell-video-till-HDMI är ett möjligt arkitekturspår. | Startsekvensens ursprung/licens är fortfarande ett projekthinder. Den tidigare utelämnade M5c-koden blir inte godkänd av denna not. |
| HDMI→USB-C | Behövs om glasögonen kräver DP Alt Mode. | Rätt riktning, matning och exakt glasögonmodell måste kontrolleras. PS176 är fel riktning för detta. |

## 6. Displaykrav utan generella garantier

1080p60 med standardtiming är ett rimligt gemensamt testmål för de aktuella XR-spåren, men är inte här en garanti för alla XREAL-, VITURE- eller Rokid-modeller. EDID, adapter, firmware, matning och fullt/begränsat RGB måste provas tillsammans.

Den gamla listan blandade goggles med olika eller inga HDMI-ingångar. Vi använder därför ingen sådan generell produktmatris. Varje verklig skärm får en rad i mätprotokollet: exakt modell, ingång, EDID/timing, signal vid bortfall, tid till återlåsning och uppmätt latens. ”Behöver stabil timing” betyder inte att en viss produkt ovillkorligen måste ha en helbildsbuffert.

## 7. Beslutsordning

1. **Nu:** fryst C5 + Nano, sex bitar och klocka, gråskala. Inga nya komponenter för att besvara om direktvägen ger bild.
2. **Efter bänken:** verkliga sampel i modellen, rätt digital hälsostatus och färgavkodning. Testa en mottagare innan tvåkanals-BOM bestäms.
3. **När 1080p behövs:** välj mellan belagt snabb extern skalare och ett komplett Primer-kit enligt [latens-/portningsnoten](HDMI_SKALNING_PRIMER_25K_2026-10-25.md).
4. **Parallellt framtidsspår:** rå IQ ur C5. Separat RF-kort med ADL5380 utreds först när totalbudget och mätmöjlighet är kända.

Inga livscykelkontroller här ersätter en full BOM-granskning före layout eller beställning. Kandidatstatus är inte schemaacceptans, och simulering är inte uppmätt RF- eller flygprestanda.
