# RF-sidan: mottagare, diversity, kvalitetssignal per rad och egenstörning (2026-10-05)

Radiodelens svar på frågan om robust analog bild. Bygger på `MOTTAGARE_ALTERNATIV.md`, `C5VRX_OCH_OPENDRONE_2026-10-03.md`, `BANDPASSFILTER_DIVIMATH.md`, `OpenVRX-Puck: design/PUCK_2027_KONCEPT.md` (antenner, EMI) och granskningen 2026-10-05 (D-5, M-7), utan att upprepa dem. Inget här är mätt på hårdvara.

Märkning: *datablad*, *källkod*, *forum* (användarrapport), *räknat* (egen räkning ur den formel som anges), *ej verifierat*. Livscykelstatus är läst hos tillverkaren 2026-10-05.

## Slutsats

- Ingen annan mottagarkrets för analog 5,8 GHz-video hittades än RichWaves RTC6715 och den nyare RTC6716S, som saknar öppet datablad. RichWave listar RTC6715 fortfarande (utan statusmärkning), och den sitter i HDZero Goggle 2. Behåll 2× RX5808 i prototypen.
- De största vinsterna ligger utanför mottagarkretsen: antennernas höjd, egenstörning i mellanfrekvensbandet 470–490 MHz (dit dekodrarnas klockövertoner och TMDS-energin når), och en kvalitetssignal per rad som inte beror på bildinnehållet.
- Val per rad ger det mesta av diversityvinsten: 10,2 dB av högst 11,7 dB vid 1 % avbrott med två lika grenar (räknat). Patch + lollipop ger täckning åt flera håll men mindre skydd mot fädning än två lika antenner.
- RSSI är den svagaste ensamma signalen. Brus över videobandet och FM-klick varnar tidigast. Synkfel kommer sist men är det enda som visar rullning.

| # | Åtgärd | Väntad nytta för bildstabiliteten | Insats |
|---|---|---|---|
| 1 | Antennerna upp från marken: stativgänga eller ben, ca 1,5 m. Hängande: på bröstet med patchen framåt | Upp till 23,5 dB vid låg flyghöjd bortom brytavståndet (räknat, avsnitt 5). Kroppsskugga på mer än 10 dB undviks | Mekanik |
| 2 | Mät egenstörningen även i mellanfrekvensbandet, kabelbundet vid tröskeln (avsnitt 4). Sedan skärmburk, filtrerade mottagarledningar, HDMI-kontaktens skal mot skärmen | Okänd tills den är mätt. I jämförbara mätta fall höjdes brusgolvet 20–25 dB och skärmning tog tillbaka 10–12 dB | Låg till medel |
| 3 | Egen 5 V per mottagare efter en linjär regulator, koax för CVBS | Tar bort mönster som kommer via matningen. Storleken är ej verifierad | Låg |
| 4 | Kvalitetssignal per rad som inte beror på bilden (avsnitt 3): räkna luma utanför 16–235 i gatewaren, synkseparator per mottagare, brusdetektor över videobandet | Täcker radmixerns blinda fläckar (M-7) och varnar före synkfel | Från ingen hårdvara till en analog kedja per mottagare |
| 5 | Viktad blandning i radmixern, vikt ∝ 1/brusvarians | Upp till 3 dB lägre brus när raderna är lika bra, aldrig sämre än den bästa raden (räknat, avsnitt 2) | Gateware. Kräver 4 |
| 6 | Bandpassfilter och LNA före varje RX5808 | Modulens brusfaktor minus ca 2,5 dB, alltså 2,5–7,5 dB om brusfaktorn är 5–10 dB (ej verifierad). Skydd mot 2,4 GHz-sändaren | Medel: 5,8 GHz-layout |
| 7 | RSSI per rad via ADC | Liten som ensam signal. Behövs för visning och som villkor för de andra måtten | En krets, fyra stift |
| 8 | Prova två likadana antenner mot patch + lollipop med snö-loggen | Fädningsvinst vid 1 % avbrott: 10 dB med lika grenar, 5 dB om de skiljer 10 dB (räknat) | Bara mätning |
| 9 | Eget RF-kort med 2× RTC6715: gemensam 8 MHz-referens, känt MF-filter, uttag på BBOUT2 och RSSI | Ger det modulen döljer. Motiveras först av mätningarna i 2 och 4 | Hög |
| 10 | Summering före detektorn (I/Q in i FPGA:n) | Teoretiskt 1,5 dB över val vid 1 % avbrott och 3 dB lägre FM-tröskel med lika grenar | Forskningsprojekt |

## 1. RTC6715 och RX5808: data, status, alternativ

| | RTC6715 (kretsen) | RX5808 (modulen) |
|---|---|---|
| Källa | [RTC6715-DST-001][rtc] rev V0.2, sept 2007, märkt Preliminary | [Product Specification V1.0][rx], 2010-09-02 |
| Frekvens | 5725–5865 MHz (s. 5) | 5705–5945 MHz |
| Känslighet | −85 dBm typ, mätt med 15 kHz ton, ±2,5 MHz deviation, 20 kHz lågpass, SNR 43 dB. Inget videomått | −90 dBm typ, −88 min. Mätvillkor anges inte |
| Mellanfrekvens (MF) | 479–480 MHz (s. 5). LO = RF − 479 MHz i steg om 2 MHz (s. 7), så MF blir 480 MHz på jämna kanalfrekvenser och 479 på udda (räknat) | anges inte |
| MF-filter | Utanför kretsen: IFOUT (stift 43) → filter → IFIN (stift 20), 50 Ω vid 480 MHz. Bandbredd anges inte | anges inte |
| Demodulator | Egen 480 MHz-VCO (stift 41, register 04h) | — |
| RSSI | 0,5–1,1 V för −91…+5 dBm, stift 18. Svarstid anges inte | Stift 9, inga data |
| Video ut | 1 Vpp i 75 Ω efter klampning | 0,9–1,1 Vpp, 75 Ω, bandbredd 0–8,0 MHz |
| Ljudbärvågor | 6,0 och 6,5 MHz | 6,5 MHz |
| Matning | 3,1–3,5 V, 146 mA | 3,5–5,5 V, 170 mA typ |
| Temperatur | −40…+85 °C | −10…+85 °C |
| Kanal efter spänningspåslag | 5865 MHz (s. 7). Bekräftar U-1 i granskningen | — |

Inget av dokumenten anger brusfaktor, spegeldämpning, högsta insignal eller RSSI:s svarstid.

**MF-filtret** sitter på modulen. Forum: RC832-mottagare har ett 480 MHz SAW-filter märkt NDF4010, och en omgång RX5808 märkta MM208R V1.3 hade i stället HDF429 (429 MHz), alltså fel filter ([fpv-community.de, 2018][sawforum]). Datablad för NDF4010 hittades inte. Som jämförelse har TaiSAW TA0421A (480 MHz, 50 Ω) en 2 dB-bandbredd på minst 20 MHz, typiskt 24,3 MHz, och minst 40 dB dämpning först 45 MHz från mitten ([datablad][ta0421]; exempel på filterklassen, ingen vald del). Läs märkningen på filtret i de moduler som köps.

**RSSI.** 0,6 V över 96 dB ger 6,25 mV/dB om kurvan är rak (räknat; databladet ger bara ändpunkterna). Nedre änden, −91 dBm, ligger 6 dB under databladets känslighet. Exemplar skiljer sig åt: rx5808-pro-diversity sparar min- och maxvärde per mottagare ([källkod][rxpd-recv]) och TBS Fusion har en kalibreringsrutin ([manual][tbs]).

**Livscykel.** RichWave listar RTC6715 som mottagare för 5,8 GHz i 48L QFN 7×7, utan statusmärkning och med databladet bakom inloggning ([produktsida][rw]). Det enda öppna databladet är utgåvan från 2007. Kretsen används i HDZero Goggle 2 och BoxPro ([källkod][hdz]) och i en tvåkanalig mottagarmodul som visades 2026 ([LongLink LLAMRX58DA][ll]). Status hos tillverkaren är alltså ej verifierad: fråga RichWave eller en distributör före ett eget RF-kort. För RX5808-modulen finns ingen tillverkare som publicerar livscykeldata.

**Kända ändringar**
- SPI-läge: SPI_SE (stift 7) har intern pull-up, och på moduler utan SPI-läge tas ett motstånd bort ([datablad s. 3–4 och 7][rtc], [rx5808-pro-diversity][spimod]).
- Ljuddemodulatorerna av: register 0Ah = 10DF3h i stället för standardvärdet 10C13h. Samma värde används i rx5808-pro-diversity (`DISABLE_AUDIO`) och i HDZero ([källkod][rxpd-recv], [källkod][hdz]). Två oscillatorer (6,0 och 6,5 MHz) stängs av. Nyttan för bilden är ej verifierad.

**Alternativ**

| | Vad | Status | Kommentar |
|---|---|---|---|
| RichWave RTC6716S | FM-mottagare 1,2/6,5 GHz, 48L QFN 7×7 | Listad hos [RichWave][rw] utan status, datablad bakom inloggning | Samma kapselstorlek som RTC6715. Stiftkompatibilitet och prestanda ej verifierade |
| RichWave RTC67133 | FM-mottagare 1,2/3,3 GHz | som ovan | Fel band |
| Annan tillverkares krets | — | — | Ingen hittad i sökningen |
| ESP32-C5 med [C5VRX][c5] | Wifi-radions I/Q, 40 MS/s med 4 bitar per I och Q, 6 bitars DAC (8 bitar på prov sedan 2026-10-04) | Kretsen i volymproduktion sedan [2025-04-30][esp]. Firmware v3.0.0, senaste ändring 2026-10-04 | Ingen uppmätt känslighet eller räckvidd. README anger att räckviddsgräns, överstyrning nära VTX och långa pass återstår att prova. Bygger på ett odokumenterat diagnosläge |
| HDZero Goggle 2, BoxPro | En RTC6715, RSSI via ADC 10 gånger per sekund | — | [Källkod][hdz]. Ingen diversity |
| Skyzone SteadyView | Syntesregistret skrivs med RTC6715:s ram och formel i ExpressLRS Backpack | se `MOTTAGARE_ALTERNATIV.md` | [Källkod][elrs]. Kretsmärkningen är ej verifierad |
| ImmersionRC RapidFire | Två mottagarmoduler mellan två kort ([recension][oscar]); forum: MM238R med RTC6715 ([intofpv, 2019][intofpv]) | som ovan | Stängd |
| TBS Fusion | Utbytbara mottagarkort. Tillverkaren anger −96 dBm utan mätvillkor. Kort från 2025 har fler band och saknar ljud ([manual 2025-11-13][tbs]) | som ovan | Kretsen ej verifierad (forum: RTC6715) |

## 2. Diversity för bredbandig FM-video

### Val, lika förstärkning eller maximal kvot

Två grenar, oberoende Rayleigh-fädning, lika medeleffekt ([Adve, Univ. of Toronto][adve], ekv. 14, 16, 27, 32, 46):

| Metod | Medel-SNR | Vinst vid 1 % avbrott | Vinst vid 10 % avbrott | Kräver |
|---|---|---|---|---|
| Val (selection) | +1,8 dB | 10,2 dB | 5,6 dB | Ett kvalitetsmått per gren |
| Lika förstärkning (EGC) | +2,5 dB | mellan de två; ca 0,6 dB under MRC vid bitfel 1 % (avsnitt 6) | | Samma fas på bärvågorna |
| Maximal kvot (MRC) | +3,0 dB | 11,7 dB | 7,0 dB | Fas och amplitudvikter |

Avbrott = SNR under en given tröskel. Vinsterna vid 1 % och 10 % är räknade ur ekv. 14 och 32. Korrelation under 0,5 mellan grenarna ändrar nästan ingenting (avsnitt 8).

### Varför produkterna väljer eller blandar efter detektorn

- Summering före detektorn kräver fasinformation ([Adve][adve], avsnitt 6). Två RX5808 har var sin kristall och syntes, så fasläget glider. Det går bara med gemensam referens, fasvridare och reglerloop, på MF-nivå (RTC6715 har MF:en utdragen mellan IFOUT och IFIN) eller på I/Q.
- Efter detektorn är båda signalerna samma video och kan väljas eller blandas utan fasreglering.
- Priset: val efter detektorn sänker inte FM-tröskeln. Under ca 10 dB bärvåg/brus ger demodulatorn klick utöver det jämna bruset ([NASA CR-120492][nasa], s. 2-5). Två lika grenar summerade före detektorn ger 3 dB högre bärvåg/brus (räknat ur ekv. 27) och flyttar tröskeln lika mycket.
- Drone Racing Leagues patent gör samma avvägning: A/D, synkronisering i FIFO, D/A och analog blandning med en kvot räknad ur RSSI, eftersom ren växling ger avbrott medan bilden synkas om ([US 9,813,659][drl]).

### Patch + lollipop

Val mellan två grenar där den ena har lägre medeleffekt (räknat ur ekv. 12 i [Adve][adve], vinst över den starka grenen ensam):

| Den svagare grenen ligger | 0 dB | 3 dB | 6 dB | 10 dB | 20 dB under |
|---|---|---|---|---|---|
| Vinst vid 1 % avbrott | 10,2 | 8,7 | 7,3 | 5,4 | 1,3 dB |
| Vinst vid 10 % avbrott | 5,6 | 4,1 | 2,8 | 1,3 | 0,0 dB |

En patch har typiskt 6–8 dB mer antennvinst än en lollipop i sin lob och 10–20 dB mindre bakåt (katalogvärden, ej verifierat för valda antenner). Enligt tabellen ger paret då 6–7 dB fädningsvinst vid 1 % avbrott i patchens lob och 1–5 dB utanför den. Resten av nyttan är täckning åt flera håll. TBS skriver att Fusion inte behöver två likadana antenner ([manual s. 7][tbs]). En användarrapport säger att blandning fungerar bäst med likadana (`docs/bench/SPEEDYBEE_STANDALONE.md`). Publicerade mätningar av diversityvinst för analog FPV hittades inte.

### Vilken signal varnar först

| Signal | Ser | Ser inte | Underlag |
|---|---|---|---|
| RSSI | Effekten i MF-bandet: bärvåg, störning och brus tillsammans | Flervägsdistorsion. Störning höjer RSSI medan bilden blir sämre. Bottnar vid −91 dBm | [Datablad][rtc]. Används av [rx5808-pro-diversity][rxpd-set] och i [DRL-patentet][drl] |
| Brus över videobandet i basbandet | Demodulatorns brus (stiger med frekvensen), klick, distorsion och svävningstoner, oberoende av bilden | Kräver ett band utan ljudbärvåg | Philips [TEA6101][tea] (1992) väljer antenn på högfrekventa komponenter plus nivå. Sanyos patent [US 4,977,615][sanyo] högpassfiltrerar FM-detektorns utgång och låter fältstyrkan välja tröskel |
| FM-klick | Själva tröskelpassagen. En klick är ett fashopp på en period; efter 8 MHz lågpass blir toppen ca 16 MHz, mer än videons deviation på några MHz (räknat) | Inget över tröskeln | [NASA CR-120492][nasa], kapitel II |
| Synk | Rivning och rullning | Brus, tills synken skadas. Synken är lågfrekvent och stor, och FM-bruset är lägst vid låga frekvenser | M-7 |
| Snö (Σ\|ΔY\|) | Brus plus bilddetaljer | Platta rader, skillnad i innehåll | M-7 |

RTC6715 har en intern brusspärr (register 09h, [datablad s. 1 och 10][rtc]) men ingen brusutgång.

### Öppna projekt

- [rx5808-pro-diversity][rxpd-set]: RSSI via ADC. Växlar när den andra mottagaren är 2 procentenheter starkare i 5 ms. Växlingen styrs bara av RSSI och en timer ([receiver.cpp][rxpd-recv]).
- [HDZero][hdz]: en mottagare, RSSI läses var 100:e ms.
- C5VRX: en mottagare. Dess fusion väljer förstärkning (se C5VRX-anteckningen).
- RapidFire, Fusion och SteadyView är stängda. Tillverkarna uppger brusdetektering respektive bildbehandling utan detaljer ([recension][oscar], [manual][tbs]).

Val per rad (64 µs) är ca 80 gånger snabbare än den öppna förebilden.

### Följd för radmixern (räknat)

Två rader med samma bild och oberoende brus, σ₁² ≤ σ₂²:
- Medelvärdet får bruset (σ₁² + σ₂²)/4. Det är bättre än den bästa raden så länge σ₂² < 3·σ₁² (4,8 dB).
- Vikterna w₁ = σ₂²/(σ₁² + σ₂²) och w₂ = σ₁²/(σ₁² + σ₂²) ger σ₁²σ₂²/(σ₁² + σ₂²), alltid lägre än den bästa.

Dagens regel blandar bara när HF-energierna skiljer mindre än 15 %. Marginalen går att använda först när måttet mäter brus och inte bild. M-7:s invändning om sidledes jitter mellan dekodrarna gäller oavsett vikter.

## 3. Bättre kvalitetssignal per rad

En rad är 63,6 µs (NTSC) eller 64 µs (PAL). Tang Nano 20K har inga lediga vanliga stift (`OpenVRX-Core: gateware/BRINGUP.md` avsnitt 5), så allt utom väg 0 tar stift från lysdioderna eller väntar på en större FPGA.

| Väg | Delar (status) | Stift | Ger | Begränsning |
|---|---|---|---|---|
| 0. Räkna lumasampel utanför 16–235 per rad | Inga | 0 | Klickmått som inte beror på bilddetaljer | Ej verifierat att TVP5150AM1 släpper igenom klicken (0Dh = 47h bör ge utökat kodområde; inte kontrollerat mot SLES209E här). Kamerans vitnivå och OSD kan ligga över 235 |
| A. RSSI, komparator A mot B | [TLV3201][tlv] (TI, Active) | 1 | Vilken mottagare som är starkast | Ingen absolutnivå. Trimning mot exemplarspridning. RSSI:s svagheter enligt avsnitt 2 |
| B. RSSI via ADC | [ADC124S021][adc] (TI, Active): 4 kanaler, 12 bitar, 50–200 ksps, SPI | 4 | RSSI per mottagare och rad, två kanaler över till C | RSSI:s svarstid är okänd: mät med pulsad signal |
| C. Brus över videobandet | Buffert [OPA356][opa] (TI, Active) → bandpass ca 7–8 MHz → logaritmisk detektor [AD8307][ad8307] (ADI, Production) → ADC enligt B | 0 utöver B | Brusmått per rad utan bildinnehåll. Ser även klick och flervägsdistorsion | Uttaget ska vara högohmigt och sitta före delaren 2 × 37,4 Ω. Mät först modulens utgång med oscilloskop-FFT: finns brus kvar vid 7–8 MHz, och var ligger ljudbärvågen? Övertonerna i avsnitt 4 ger svävning vid 6–7,8 MHz som detektorn också ser |
| D. Klickräknare | Två TLV3201 per mottagare som fönster runt bildens område | 1–2 per mottagare | Antal klick per rad | Trösklarna måste följa synkbotten. Förslag, ej provat |
| E. Synkseparator | [LMH1980][lmh] (TI, Active) | 1–2 per mottagare | Radsynk direkt från mottagaren: jitter och uteblivna pulser per rad, utan att vänta på TVP:ns låsbitar (pollas var 20:e ms) | Ser inte brus förrän synken skadas |
| F. Basbands-ADC parallellt med dekodern | [AD9280][ad9280] (ADI, Production): 8 bitar, 32 MSPS | 9 per mottagare | Allt ovan i gateware: brus mätt på synkbotten (4,7 µs utan bildinnehåll i varje rad), klick, synk | Ryms inte på Tang Nano 20K. Mest gatewarearbete |

Bruset vid 7–8 MHz är inte litet: med brustäthet som stiger med f² har det bandet 1,3 dB mer effekt än hela 0–5 MHz (räknat; förutsätter att modulen inte filtrerar bort det, och specen säger 0–8 MHz).

GW5A-25:s inbyggda ADC räcker inte för RSSI på varje rad: den är av ΔΣ-typ med 0–1 V ingång, mäter en ingång i taget, och kortaste omvandling är (128 + 20) klockcykler vid 2,5 MHz = 59 µs ([UG299-1.0.8E][ug299], tabell 2-2, 3-5 och 3-6). Det ger som bäst varannan rad per mottagare, och RSSI (0,5–1,1 V) måste delas ned. Stöd i den öppna verktygskedjan är ej verifierat. En I2C-ADC på 400 kHz behöver ca 73 µs per avläsning (räknat: ca 29 bitar) och hinner alltså inte båda mottagarna på varje rad.

Ordning: 0 är gratis och visar om klick syns i BT.656. E är billigast i hårdvara och tar det HF-energin inte ser. C ger mest ny information. F ersätter C, D och E om FPGA:n har stift nog.

## 4. Egenstörning

### Mellanfrekvensbandet (svar på D-5)

MF är 479 eller 480 MHz (avsnitt 1). Filtrets bredd står inte i något dokument för modulen. Signalen är ca 18 MHz bred (Carsons regel med ±2,5 MHz deviation och ljudbärvåg på 6,5 MHz, räknat) och filterklassen i avsnitt 1 har 20–24 MHz. Då ligger dessa övertoner i passbandet:

| Överton | Frekvens | Avstånd från MF |
|---|---|---|
| 18 × 27 MHz (TVP SCLK, Tang-kortets oscillator) = 36 × 13,5 MHz (BT.656-data) | 486,0 MHz | +6 till +7 MHz |
| 34 × 14,31818 MHz (TVP-kristallen) | 486,8 MHz | +6,8 till +7,8 MHz |
| 33 × 14,31818 MHz = 35 × 13,5 MHz | 472,5 MHz | −6,5 till −7,5 MHz |
| SDRAM 64,8 MHz, pixel 74,25 MHz | inga inom ±20 MHz | |

472,5 MHz står inte i granskningen. Alla tre gäller på varje kanal.

- Källstyrka: en 27 MHz-fyrkant med 1 ns flanker har sin 18:e överton ca 43 dB starkare än den 215:e vid 5805 MHz (räknat, trapetsmodell, antagen flanktid).
- TMDS: slumpmässiga data på 742,5 Mbit/s (720p) har en spektraltäthet som ligger 7 dB under sitt maximum vid 480 MHz och 33 dB under vid 5,8 GHz. För 1080p (1485 Mbit/s) är det 1,5 dB vid 480 MHz (räknat, sinc² för NRZ; verkliga flanker sänker 5,8 GHz-värdet mer).
- Verkan (FM-teori, ej mätt): en ton på avståndet Δf från bärvågen ger en ton vid Δf i basbandet. Vid 6–8 MHz hamnar den över lumabandet och syns knappt på en stark signal. På en svag signal tävlar störningen med bärvågen och bilden försvinner tidigare, utan mönster. Bredbandigt brus verkar på samma sätt. Felet ser ut som kortare räckvidd och måste mätas vid tröskeln.
- Tänkbara vägar in (inte mätta): modulens tolv stift och kabeln till dekoderkortet, samt springor i modulens burk. Kabeln mellan dekoderkort och FPGA har en jordstift per stiftlist för nio 27 MHz-signaler (B-7) och är en trolig strålare.

### I 5,8 GHz-bandet

Tabellen i `PUCK_2027_KONCEPT.md` stämmer vid omräkning (78 × 74,25 = 5791,5; 79 × 74,25 = 5865,75; 89 och 90 × 64,8 = 5767,2 och 5832,0). Tillägg: 215 × 27 MHz = 5805,0 MHz (A4) och 405 × 14,31818 MHz = 5798,9 MHz, 1,1 MHz från F4.

### Åtgärder och hur mycket de har gett

| Åtgärd | Rapporterad eller räknad verkan |
|---|---|
| Skärmburk | Längsta springan bestämmer: SE ≈ 20·log(λ/2L) ([Brewer och Fenical][slot]). 5 mm ger 14 dB vid 5,8 GHz och 36 dB vid 486 MHz. 2 mm ger 22 dB och 1 mm 28 dB vid 5,8 GHz (räknat). Regeln under ca 5 mm i puckkonceptet ger alltså 36 dB i MF-bandet men bara 14 dB vid 5,8 GHz |
| Skärma störkällan och dess kontakt | Intels mätning på USB 3.0: brusgolvet i 2,4 GHz-bandet steg nära 20 dB med en disk ansluten och ca 25 dB vid kontakten. Helt skärmad disk gav ca 12 dB lägre brus. Kontaktskal bundet mot chassit med bakre skärm gav minst 10 dB ([Intel 2012][intel]) |
| Flytta klockan eller kanalen | Raspberry Pi 4 i 2560×1440 har TMDS-klocka 2,415 GHz och slår ut wifi-kanal 1 ([mätning 2019][rpi]). Hos oss är bara SDRAM-klockan fri. 27 och 14,318 MHz bestäms av TVP5150AM1 och pixelklockan av bildformatet, så MF-övertonerna går inte att flytta |
| Spread spectrum | Minskar inte den totala utstrålade energin, bara toppen i smal mätbandbredd ([Wikipedia][ssc]). Mot en mottagare med ca 20 MHz bandbredd hjälper det därför lite, och en fast ton blir en svepande (resonemang, ej mätt) |
| Matningsfilter per mottagare | Ingen siffra hittad. Se avsnitt 5 |

Rapporter om HDMI-störning mot just analoga 5,8 GHz-mottagare hittades inte.

### Tillägg till mätplanen i puckkonceptet

1. Kabelbunden signal: VTX i skärmad låda → dämpare → delare → båda mottagarna, inställd strax över tröskeln. Då försvinner flervägsutbredningen ur mätningen.
2. Snö-loggen med: dekoderkortet av och på (D-5), HDMI-kabeln i och ur, mottagare B av och på (LO-läckage mellan två mottagare på samma kanal; hypotes, inga rapporter hittade), 2,4 GHz-sändaren 30 cm bort av och på, wifi eller backpack av och på.
3. RSSI-spänningen med 50 Ω på antenningången, digitaldelen av och på. 6,25 mV/dB; visar bara störning över ca −91 dBm.
4. Närfältsprob och en enkel SDR vid 470–490 MHz runt modulens burk och kablar.

## 5. Det som ofta förbises i RF-kedjan

- **Höjden över marken.** Två-strålemodellen: bortom brytavståndet d = 4π·h₁·h₂/λ faller effekten med d⁴ och är proportionell mot antennhöjden i kvadrat ([formel][tworay]). λ = 51,7 mm. Puck på marken (0,1 m) och flyghöjd 1 m ger brytavstånd 24 m; flyghöjd 5 m ger 122 m. Med pucken på 1,5 m blir det 365 m och 1,8 km. Bortom brytavståndet skiljer 0,1 m och 1,5 m 23,5 dB (räknat; plan mark, förenklad modell).
- **Kroppen.** Kroppen mellan antenn och sändare kostar mer än 10 dB för de flesta bärplatser vid 5,8 GHz inomhus ([Yoo m.fl., IEEE TWC 2016][body], tabell II). Utomhus finns färre reflexer som fyller i (ej verifierat).
- **Spegelfrekvensen.** LO ligger under signalen ([datablad s. 7][rtc]), så spegeln är RF − 2 × MF ≈ RF − 958 MHz: 4767–4917 MHz för 5725–5875 MHz. Andra övertonen av 2,4 GHz-bandet är 4800–4967 MHz och täcker spegeln för kanalerna 5758–5875 MHz (räknat). Radiosändaren i handen och varje 2,4 GHz-sändare i lådan (wifi, backpack) kan alltså störa via spegeln. Det är en hypotes: mottagarens spegeldämpning och sändarnas övertonsnivå är okända. Spegeln ligger bara 80–230 MHz under passbandet på filtret i `BANDPASSFILTER_DIVIMATH.md`, och dess dämpning där är inte uppgiven. Grundtonen är ett eget problem: 1 W på 0,3 m ger ca 0 dBm vid antennen (räknat, isotrop).
- **Filter och LNA.** Kandidater: Qorvo [QPL9503][qpl] (Production): 0,6–6 GHz, 21,6 dB förstärkning och 0,9 dB brusfaktor vid 5,5 GHz, avstängningsstift. ADI [HMC717A][hmc] (Recommended for New Designs): 4,8–6,0 GHz, 14,5 dB, 1,1 dB. Med 1,5 dB filterförlust före LNA:n blir systemets brusfaktor ca 2,5 dB (QPL9503) eller 2,9–3,6 dB (HMC717A) för en modul på 5–10 dB (räknat, Friis). Nackdel: 15–22 dB mindre marginal mot överstyrning. 25 mW på 1 m ger ca −24 dBm i en 8 dBi-patch (räknat: 14 dBm + 2 dBi + 8 dBi − 47,7 dB). Filtret ska dämpa 2,4–2,5 GHz och spegelbandet. Ingen filterdel är vald.
- **Förlust före första förstärkaren** (pigtail, kontakter, filter) kostar känslighet dB för dB.
- **Matningen.** Kretsen går på 3,1–3,5 V och modulen tar 3,5–5,5 V, så modulen har en egen regulator (slutsats ur de två dokumenten; inget schema sett). Dess dämpning av switchrippel är okänd. Rev A matar mottagarna från samma 5 V som FPGA-kortet via en PTC. Lägg en linjär regulator per mottagare, till exempel ADI [LT3045][lt] (Recommended for New Designs): 500 mA, 76 dB dämpning vid 1 MHz.
- **Videoutgångens last.** 75 Ω-källa mot 2 × 37,4 Ω ger 0,45–0,55 Vpp vid TVP:n, under gränsen 0,75 Vpp. Varje extra uttag (detektor, CVBS ut, DVR) måste vara högohmigt, annars halveras nivån.
- **Temperatur.** RX5808 är specad från −10 °C, kretsen från −40 °C.

## Ej verifierat

- RX5808: brusfaktor, spegeldämpning, högsta insignal, RSSI:s svarstid, vilket SAW-filter som sitter i köpta moduler och dess bandbredd.
- Om modulens videoutgång har brus kvar vid 7–8 MHz, och om ljudbärvågen syns där.
- Livscykelstatus för RTC6715 och RTC6716S hos RichWave.
- Vilken krets RapidFire och Fusion använder (forum: RTC6715).
- C5VRX: känslighet, räckvidd, beteende nära VTX.
- Att FM-klick syns som luma utanför 16–235 efter TVP5150AM1.
- Störning via spegelfrekvensen och LO-läckage mellan mottagarna (hypoteser).
- Diversityvinst för analog FPV: inga publicerade mätningar hittade.

## Källor

- RTC6715: [RTC6715-DST-001 rev V0.2 (kopia)][rtc], [RichWave produktsida][rw]. RX5808: [Product Specification V1.0][rx] (läst via en annan kopia av samma dokument).
- SAW-filter: [fpv-community.de][sawforum] (forum), [TaiSAW TA0421A][ta0421].
- Användning och källkod: [hdzero-goggle rtc6715.c][hdz], [ExpressLRS Backpack steadyview.cpp][elrs], [rx5808-pro-diversity receiver.cpp][rxpd-recv], [settings.h][rxpd-set], [SPI-mod][spimod], [LongLink LLAMRX58DA][ll], [C5VRX][c5], [Espressif om ESP32-C5][esp].
- Produkter: [TBS Fusion manual 2025-11-13][tbs], [Oscar Liang om RapidFire][oscar], [intofpv][intofpv] (forum).
- Diversity och FM: [R. S. Adve, Receive Diversity][adve], [US 9,813,659][drl], [Philips TEA6101][tea], [US 4,977,615][sanyo], [NASA CR-120492][nasa].
- Delar: [TLV3201][tlv], [ADC124S021][adc], [OPA356][opa], [LMH1980][lmh], [AD8307][ad8307], [AD9280][ad9280], [HMC717A][hmc], [LT3045][lt], [QPL9503][qpl], [Gowin UG299][ug299].
- Störning och utbredning: [Intel, USB 3.0 RFI (2012)][intel], [Raspberry Pi 4 och 1440p][rpi], [Brewer och Fenical, Shielding: The Hole Problem][slot], [Spread spectrum][ssc], [Two-ray ground-reflection model][tworay], [Yoo m.fl. 2016][body].

[rtc]: https://opendevices.ru/wp-content/uploads/2015/02/7058r.pdf
[rw]: https://www.richwave.com.tw/en/page_prd_new.aspx?Id=8
[rx]: https://mikrocontroller.net/attachment/172723/RX5808-Spec-V1.pdf
[sawforum]: https://fpv-community.de/threads/rx5808-mit-merkw%C3%BCrdigen-saw-filern.83641/
[ta0421]: https://www.taisaw.com/assets/PDF/TA0421A%20_Rev.2.0_.pdf
[hdz]: https://github.com/hd-zero/hdzero-goggle/blob/main/src/driver/rtc6715.c
[elrs]: https://github.com/ExpressLRS/Backpack/blob/master/src/steadyview.cpp
[rxpd-recv]: https://github.com/sheaivey/rx5808-pro-diversity/blob/develop/src/rx5808-pro-diversity/receiver.cpp
[rxpd-set]: https://github.com/sheaivey/rx5808-pro-diversity/blob/develop/src/rx5808-pro-diversity/settings.h
[spimod]: https://github.com/sheaivey/rx5808-pro-diversity/blob/master/docs/rx5808-spi-mod.md
[ll]: https://www.b2match.com/e/een-matchmaking-taiwan-expo-europe/opportunities/UGFydGljaXBhdGlvbk9wcG9ydHVuaXR5OjI0MTA1NA==
[c5]: https://github.com/Twotoz/C5VRX
[esp]: https://www.espressif.com/en/news/ESP32-C5_Mass_Production
[tbs]: https://www.team-blacksheep.com/media/files/tbs-fusion-manual.pdf
[oscar]: https://oscarliang.com/immersionrc-rapidfire-module/
[intofpv]: https://intofpv.com/t-video-rssi
[adve]: https://www.comm.utoronto.ca/~rsadve/Notes/DiversityReceive.pdf
[drl]: https://patents.google.com/patent/US9813659B1/en
[tea]: https://www.cieri.net/Documenti/Data%20Sheets/Radio%20and%20Video%20ICs/TEA6101,%20TEA6101T%20(Philips).pdf
[sanyo]: https://patents.google.com/patent/US4977615A/en
[nasa]: https://ntrs.nasa.gov/api/citations/19750004126/downloads/19750004126.pdf
[tlv]: https://www.ti.com/product/TLV3201
[adc]: https://www.ti.com/product/ADC124S021
[opa]: https://www.ti.com/product/OPA356
[lmh]: https://www.ti.com/product/LMH1980
[ad8307]: https://www.analog.com/en/products/ad8307.html
[ad9280]: https://www.analog.com/en/products/ad9280.html
[hmc]: https://www.analog.com/en/products/hmc717a.html
[lt]: https://www.analog.com/en/products/lt3045.html
[qpl]: https://www.qorvo.com/products/p/QPL9503
[ug299]: https://cdn.gowinsemi.com.cn/UG299E.pdf
[intel]: https://www.intel.com/content/www/us/en/content-details/841692/usb-3-0-radio-frequency-interference-impact-on-2-4-ghz-wireless-devices-white-paper.html
[rpi]: https://www.rtl-sdr.com/using-a-hackrf-to-investigate-why-wifi-on-the-raspberry-pi-4-doesnt-work-when-running-hdmi-at-1440p/
[slot]: https://www.electronicdesign.com/home/article/21200214/shielding-the-hole-problem
[ssc]: https://en.wikipedia.org/wiki/Spread_spectrum
[tworay]: https://en.wikipedia.org/wiki/Two-ray_ground-reflection_model
[body]: https://eprints.whiterose.ac.uk/101075/19/07456328.pdf
