# Utgång och latens efter mixern (2026-10-05)

Omfattning: buffring, deinterlacing/skalning och bildutgång till XR-glasögon, goggles och TV. Bygger på granskningen 2026-10-05 (V-1 till V-3), `XR_GLASOGON_KOMPATIBILITET.md`, `ALTERNATIVA_VAGAR_2026-10-02.md` och Core `gateware/README.md` ("Låglatensläge") och upprepar dem inte. Kod läst i Core 92a2025. Inget är provat på hårdvara.

Belägg: **[D]** primärkälla som jag har öppnat (datablad, manual, källkod, tillverkarens sida), **[S]** simulerat mot oförändrad RTL, **[K]** läst ur vår kod, **[R]** räknat, **[F]** forum- eller användarrapport, **[I]** läst via sökmotorns utdrag eftersom sidan inte gick att öppna, **[H]** hypotes.

## Slutsats

- **LOW ger inte 750/751 rader med en sammanflätad källa.** Triggern kommer på rad 1 i varje fält, och fältens första bildrader ligger omväxlande 263 och 262 källrader isär (313/312 i PAL). `genlock_timing.v` ger då bilder om 752, 750, 752, 749 rader (NTSC) och 751, 749 (PAL) [S]. Fördröjs vartannat fälts trigger en halv källrad blir det 751, 751, 751, 750 respektive konstant 750 [S].
- **BUF kan bli ungefär ett fält snabbare utan att tidsbasen ändras**, genom att visa fältet som håller på att skrivas när skrivaren har försprång (avsnitt 5). Det är principen i tv-teknikens frame synchronizer, och RetroTINK-5X uppger 0,25–1,25 bilder i sitt buffrade läge.
- **XR-glasögon kräver en 1080p-utgång.** XREAL Airs EDID har 1920×1080 i 60, 90 och 120 Hz och inget annat i det jag kunde läsa [I]. Inget jag hittat visar stöd för 720p, 50 Hz eller VRR. Hur HDMI→USB-C-adaptrar och glasögon tar ett radantal som ändras är inte dokumenterat; det måste provas.
- **1080p60 direkt ur GW5A-25 ligger inom databladet** (10:1-serialiserare 2 000 Mbit/s [D]) men är inte visat med öppen verktygskedja. ADV7513 och TFP410 är dokumenterade reserver.

| # | Åtgärd | Vinst | Insats |
|---|---|---|---|
| 1 | BUF: visa fältet som skrivs när skrivaren har försprång (avsnitt 5) | Latens överst i bilden: NTSC 16,6–33 ms → 0,1–17 ms, PAL till 60 Hz 20–40 ms → 2,6–23 ms [R]. Standardtiming, alla mottagare | Liten till medel: buffertvalet flyttas till SDRAM-domänen (löser också V-3), tröskel, modell och test. Kräver att mixern lämnar rader i ordning (granskningens punkt 1) |
| 2 | LOW: jämn bildperiod och rätt fältläge (avsnitt 2 och 4) | Radantalet svänger 1 rad i stället för 3 (NTSC) och 0 i stället för 2 (PAL). Samma ändring rättar bobbens halvradsfel | Liten: triggerfördröjning per fält, en fältbit till `fb_display` |
| 3 | Testbitström: M0 + `genlock_timing` med syntetisk trigger och valbara radföljder | Svar på V-2 för TV, fångstkort och HDZero-goggles innan mer arbete läggs på LOW | Timmar, när kortet finns. Glasögonen kräver 1080p och kan inte provas så |
| 4 | Bob med interpolation i höjdled, linjär interpolation i sidled vid 720p (avsnitt 4) | Jämna radhöjder vid PAL och 1080p, inga dubblade pixlar | Liten. +1 källrad (64 µs) i LOW |
| 5 | 1080p60: prova direkt TMDS på Tang Primer 25K. Reserv ADV7513, därefter TFP410. Släpp LT8618SXB (avsnitt 3) | Förutsättning för XR-glasögon | Medel till stor: portning, nytt kort |
| 6 | LOW som svänghjul: nominell 59,94/50 Hz-klocka, trigger bara i ett fönster, högst ±1 rad per bild, BUF-vägen som reserv när ingången störs (avsnitt 2) | Mottagaren ser standardtiming och aldrig en kort bild | Medel |
| 7 | Vänta med rörelseadaptiv deinterlacing, DisplayPort direkt ur FPGA och VRR | Liten eller obelagd nytta | — |

## 1. Mottagare: glasögon, goggles och adaptrar

| Mottagare | Tar emot | Egen latens |
|---|---|---|
| XREAL Air | EDID: tre format, 1920×1080 i 60, 90 och 120 Hz (148,5 / 222,75 / 297 MHz), alla med CEA-släckningen för 1080p60 (2200×1125). Inga "established timings" [I]. Om ett tilläggsblock listar fler format gick inte att se | ingen uppgift |
| XREAL One, One Pro | 1920×1080, högst 120 Hz [D] | 3 ms rörelse-till-bild [D]. Det gäller glasögonens egen skärmförankring, inte ingång till bild |
| VITURE | Tillverkarens USB-C-adapter lämnar 1920×1200, 1920×1080 och 3840×1080, alla i 60 Hz [D] | ingen uppgift |
| Rokid | inget verifierat | — |
| HDZero Goggle | HDMI in: aktiv bild exakt 1920×1080 eller 1280×720. Bildfrekvensen mäts och sorteras: 720p under 57 Hz räknas som 50, 57–80 som 60, över 80 som 100; 1080p 45–57 som 50, 57–70 som 60 [D] | Goggle 2: HDMI in under 1 ms, analog kamera till skärm under 2 ms enligt tillverkaren [D] |
| Walksnail Goggles X | HDMI in finns, formaten anges inte [D] | — |
| Fat Shark, Skyzone, DJI | inget verifierat. DJI:s specifikation för Goggles RE listar inga HDMI-format [D] | — |

- **720p och 50 Hz till glasögon:** saknas i EDID-utdraget, och navets tre användarrapporter säger att 720p inte ger bild. PAL i LOW (720p50/1080p50) är alltså inte ett glasögonläge.
- **HDZero-gogglen passar dagens 720p-utgång.** Firmwaren använder det totala radantalet bara för att räkna bildfrekvens, så ±3 rader ändrar inte klassningen; byter klassen startas skärmen om (`it66021.c`, `hardware-goggle.c`) [D]. Om gogglens egen FPGA tål ett radantal som varierar framgår inte [H].
- **Adaptrarna:** en isärtagen HDMI→USB-C-adapter för AR-glasögon bygger på Lontium LT6711A [F]. Kretsen är en HDMI 2.0-mottagare och DP 1.2-sändare (1,62 / 2,7 / 5,4 Gbit/s, upp till fyra banor) med USB-C-logik och en mikroprocessor med firmware i flash [I]. Firmwaren ligger under sekretessavtal enligt konstruktören av melonHD-modulen [F].
- **Vad adaptern gör med avvikande timing:** funktionslistan nämner inget bildminne, så kretsen kan varken omtajma eller byta bildfrekvens; det som kommer in går ut [H]. DisplayPort skickar timingen som attribut en gång per bild (MSA, bland annat totalt radantal). En mottagare får bortse från dem bara om den anger `DP_MSA_TIMING_PAR_IGNORED` i DPCD 007h, vilket är samma sak som stöd för Adaptive-Sync [D]. En källa vars radantal växlar säger alltså emot sina egna attribut. Vad LT6711A:s firmware och glasögonens DP-mottagare gör då finns inte dokumenterat [H].
- **Släckningen:** i XREAL:s forum beskrivs adaptrar som byter ut glasögonens EDID mot en egen och då ger en förskjuten bild [I, F]. Det tyder på att glasögonen placerar bilden efter synken. `genlock_timing.v` lägger de varierande raderna sist i bakre svartskuldran, alltså mellan VSYNC och första bildrad [K]. Håll avståndet VSYNC–bild fast och lägg variationen före VSYNC.
- **59,94 Hz med fast radantal** är vad en NTSC-låst utgång bör ge. DP-länken bär pixelklockan som ett förhållande och bryr sig inte om 0,1 % [H]. Om glasögonen tar det är inte verifierat.

## 2. Bildlåsning i andra videoprocessorer

| Produkt | Låst läge | Fritt läge | Vad de säger om skärmar |
|---|---|---|---|
| OSSC Pro [D] | Ren radmultiplikator: högst 2 rader. Adaptiv radmultiplikator: högst 60 rader, antalet släckrader anpassas så att utgången får en standardupplösning. Skalare med framelock: cirka 1 bild | Skalare utan framelock: 1–2 bilder, i källans frekvens från egen klocka eller fast 50/60/100/120 Hz | Egen gradering: ren multiplikator "varierande", adaptiv och låst skalare "mycket hög", fri skalare "full". Med framelock kan ett avbrott på ingången bryta synken på utgången |
| RetroTINK-5X och 4K | Frame Lock: cirka 0,25 bild (5X) [D]. Gen Lock: följer ingångens bildfrekvens med en återskapad klocka som är stabilare än Frame Lock [D] | Triple Buffer: 0,25–1,25 bilder (5X) [D] | Triple Buffer finns för att utgången inte ska falla bort när ingången byter läge [D] |
| GBS-Control | FrameTime Lock ställer frekvensen på en extern klockgenerator (Si5351) [D] | av | Wikin ber användaren stänga av om skärmen blir instabil eller svart [D]. I forumet: lås genom ändrad utgångstiming gav svarta bilder på en del skärmar, klockgeneratorn gick bättre [I, F] |
| MiSTer (ascal) | `vsync_adjust=2`: en enda buffert; skalaren har en utgång för finjustering av utgångens PLL [D] | `vsync_adjust=0`: trippelbuffert. `=1`: utfrekvensen anpassas till källan | `vrr_mode` kan skicka FreeSync- eller VESA-VRR-signalering [D] |
| HDZero Goggle, analog in | Skärmen ställs på 720p50 för PAL och 720p60 för NTSC [D] | — | egen skärm |
| PixelFX Morph | inget verifierat | | |

Det som går att föra över:

1. **Ett fritt läge som användaren väljer** finns i alla. BUF/LOW i menyn motsvarar det.
2. **De låser genom att ställa utgångens klocka** (RetroTINK Gen Lock, GBS-C med klockgenerator, MiSTer) eller genom att fylla ut till standardens radantal (OSSC Pro adaptiv). Läget där utgången följer ingången rakt av är det som OSSC Pro graderar lägst.
3. **Löst kopplat lås tål störningar, hårt lås skickar dem vidare.** Analog FPV tappar synk ofta. I LOW blir varje sådant tillfälle en kort eller lång bild på HDMI (V-2), och en skärm som tappar låsningen är svart i 1–2 s (Core-README).

**Vårt LOW idag** [S]: Icarus Verilog 12.0, `genlock_timing.v` oförändrad, `lock = 1`, en triggerpuls omväxlande 263 × 4 719 och 262 × 4 719 pixelklockor isär (PAL: 313/312 × 4 752, `h_alt = 1`). Radantal = pixelklockor mellan `frame_start` delat med radlängden. Testbänken ligger inte i repot.

| Trigger | NTSC, 74,25 MHz | PAL, 720p50 |
|---|---|---|
| Som koden: rad 1 i varje fält | 752, 750, 752, 749 | 751, 749 |
| Vartannat fälts trigger fördröjd en halv källrad | 751, 751, 751, 750 | 750 |
| Dito med pixelklocka 74,25/1,001 MHz [R, egen radmodell] | 750; vid ±50 ppm en bild om 749 eller 751 rader ungefär var 27:e | — |

- **Orsak:** `fb_backend.v` triggar när rad 1 i ett fält är klar. Enligt BT.656-tabellen i `model/bt656.py` börjar bildraderna på rad 20 och 283 (525 rader) och 23 och 336 (625 rader) [K]. TVP5150AM1 byter F och V på EAV, alltså på radgränser (SLES209E avsnitt 3.14) [D], och 525 och 625 är udda tal: avstånden kan inte bli lika. En TI-ingenjör beskriver samma sak: den som läser fältbiten vid radstart ser ett fält som är en rad längre än det andra [F].
- **Varför testet inte såg det:** `sim/test_m2.py` matar fält som alla är 14 rader långa [K].
- **Åtgärd:** mät de två triggeravstånden och fördröj triggern efter det kortare med halva skillnaden (858 dekoderklockor i NTSC, 864 i PAL). Det kräver inget antagande om vilken fältbit som är vilken. Fältet som inte fördröjs ska visas en halv källrad lägre (avsnitt 4); då har båda fälten samma marginal mellan skrivning och läsning [R].
- **Klocka för fast radantal i NTSC:** 74,25/1,001 MHz = 27 MHz × 250/91. GW2AR-18:s PLL har delare 1–64, fasdetektorfrekvens minst 3 MHz och VCO 500–1 250 MHz (DS226, PLL-avsnittet) [D], så förhållandet ryms inte i en PLL. Två i kaskad, × 25/7 och × 10/13, ger det exakt inom de gränserna [R], men kretsen har två PLL:er och båda används. Jitter efter två PLL:er är inte bedömt [H]. GW5A-25 har sex PLL:er [D]. Alternativet är en programmerbar klockgenerator som GBS-C:s Si5351 (aktiv enligt distributörsuppgifter, inte kontrollerat hos Skyworks [I]).
- **Svänghjul:** tidsbasen går på sin egen period, tar bara emot triggrar i ett fönster kring väntad bildstart och rättar fasen med högst en rad per bild. Perioden är då känd i förväg, så den ändrade raden kan läggas före VSYNC. Ligger fasen utanför ringens 16 rader läses bilden ur SDRAM enligt avsnitt 5. LOW och BUF blir då samma bildväg med olika styrning av tidsbasen: fri på 60,00 Hz eller styrd mot ingången.
- **Dekoderns radlåsta 27 MHz som referens** ger i PAL exakt en 720p50-bild per fält med × 11/4, men klockan har stort jitter vid fading (`REV_A_KONCEPT.md`, risk 4) och det finns två dekodrar. Avrådes.

## 3. 1080p60 från en liten FPGA

### HDMI-sändare

| Krets | Livscykel | Ingång | Dokumentation | Kapsel |
|---|---|---|---|---|
| ADV7513 (ADI) | "Recommended for New Designs" enligt navets anteckning 2026-10-02. ADI:s sida svarade inte 2026-10-05 | RGB eller YCbCr 4:4:4/4:2:2, 8/10/12 bitar per komponent, klocka 1×, 2× eller DDR, inbäddad synk valbar [D, Linux-bindningen] | ADI:s programmerings- och hårdvaruguide (navets länkar), Linux `adv7511` med `adi,adv7513` [D] | LQFP-64 |
| TFP410 (TI) | ACTIVE [D, ti.com 2026-10-05] | RGB 24 bitar på en flank eller 12 bitar på båda flankerna, DE/HSYNC/VSYNC, upp till 165 MHz. Setup/hold 1,3/1,3 ns (en flank), 0,9/1,0 ns (två flanker) [D] | Fullständigt datablad SLDS145D. Behöver ingen I2C: med ISEL låg ställs kretsen med stiften BSEL, DSEL och EDGE [D] | HTQFP-64, 0–70 °C. Ren DVI: inget ljud, inga InfoFrames |
| IT66121FN (ITE) | inte verifierad | Linux-drivrutinen kan bara RGB: 24 bitar upp till 148,5 MHz, 12 bitar DDR upp till 74,25 MHz [D] | Linux `ite-it66121.c` (även IT6610, IT66122) [D]. Databladet i omlopp är en förhandsutgåva [I] | QFN-64 |
| LT8618SXB (Lontium) | inte verifierad | RGB, BT.656/BT.1120, 148,5 MHz DDR (`REV_A_KONCEPT.md`) | Inget fullständigt datablad och ingen registerkarta offentligt. Ingen drivrutin i Linux hittad vid sökning 2026-10-05 | QFN-64 |
| SiI9022A (Lattice) | aktiv enligt distributörsuppgifter, inte kontrollerat hos Lattice [I] | inte undersökt | — | — |
| TDA19988 (NXP) | utgången, avvecklingsbesked 2021 [I] | — | — | — |
| CH7035 (Chrontel) | inte undersökt | | | |

- **ADV7513 tar strömmen vi redan har:** `bt1120_tx.v` ger 16 bitar YCbCr 4:2:2 med inbäddad synk vid 148,5 MHz [K], vilket bindningen beskriver som `yuv422`, klocka `1x` och `adi,embedded-sync` [D]. 17 signaler plus I2C. Vilket "Input ID" det motsvarar ska läsas i ADI:s hårdvaruguide före schema.
- **TFP410 är enklast att få igång** (ingen initiering) men kräver RGB och, med 12 bitar, DDR vid 148,5 MHz: 16 signaler och 0,9/1,0 ns setup/hold av en halvperiod på 3,37 ns. Det är ett kretskortsjobb, inte stiftlistetrådar.
- **LT8618SXB** har ingen fördel kvar när initieringens ursprung är oklart och två dokumenterade kretsar finns.

### Direkt ur FPGA

- **GW5A-25:** 10:1-serialiserare högst 2 000 Mbit/s, LVDS ut 2,0 Gbit/s, PLL-VCO 700–1 400 MHz, sex PLL:er (DS1103-1.1E, 2026-09-21, tabell 1-1 och 3-33; tabellnoten säger att värdet är I/O-logikens gräns och beror på IP) [D]. 1080p60 kräver 1 485 Mbit/s och 742,5 MHz serialiserarklocka. Gowin publicerar ingen livscykelstatus; databladet är reviderat 2026-09-21.
- **Visat i praktiken:** projektet `thisiseth/tang-primer-25k-spi-io` uppger 1080p DVI på Tang Primer 25K, byggt med Gowin EDA; bildfrekvensen för 1080p anges inte [D]. Med Apicula/nextpnr har jag inte hittat någon rapport om 1080p60 på GW5A-25. Navet har byggt en bitström (Apicula 0.32) som inte är körd.
- **Apicula** 0.33 (2026-08-25) och 0.34 (2026-10-02) finns [D]. Versionsnoterna för 0.33 nämner GW5A:s klockdelare (CLKDIV, CLKDIV2) och rättade HCLK-fuses, alltså den väg serialiserarklockan går. Kör `tools/test_lvds_bank_inputs.py` vid uppgradering (AGENTS.md).
- **Andra små FPGA:er med öppen kedja:** ECP5 klarar 800 Mbit/s på DDR-utgångarna i snabbaste hastighetsklass, 700 och 624 i de andra (FPGA-DS-02012-3.4) [D]. Det räcker till 720p60 i snabbaste klassen och inte till 1080p60. Artix-7 anges till 1,25 Gbit/s LVDS i AMD:s DS180, som jag inte har öppnat. GW5A-25 är den enda jag hittat med en serialiserare specad över 1 485 Mbit/s.

### DisplayPort direkt

- 1080p60 med 24 bitar är 3,56 Gbit/s nyttolast. Efter 8b/10b bär en bana 1,30 Gbit/s vid 1,62 Gbit/s och 2,16 vid 2,7: fyra banor på lägsta hastigheten eller två på nästa [R]. Därtill AUX-kanal, länkträning och HPD, och för USB-C förhandling av alt mode och 5 V till glasögonen.
- Öppen kärna: `hamsternz/FPGA_DisplayPort` (MIT) går på Artix-7 och Spartan-6 med transceivrar i 2,7 Gbit/s; 1,62 Gbit/s och full hantering av länkträning och hot-plug står som ogjort [D].
- GW5A-25 saknar transceivrar. Dess 2,0 Gbit/s LVDS når bara lägsta hastigheten, och DP:s elektriska krav över LVDS är inte verifierade [H]. Ingen väg för rev B.
- Direkt USB-C från pucken blir därför en bryggkrets med stängd firmware (LT6711A [F]; Analogix ANX7688 behöver också firmware som värden laddar [D]) eller en köpt adapter. Livscykel inte verifierad för någon av dem.

## 4. Deinterlacing och skalning

Vad andra uppger:
- HDZero: en "2D"-deinterlacer (inom ett fält) som inte lägger till fördröjning på analog ingång [D].
- OSSC Pro: bob visar fälten efter varandra med det ena förskjutet en halv källrad. Radmultiplikatorlägena har bara bob; rörelseadaptiv finns bara i skalaren med bildminne [D].
- RetroTINK-5X: rörelseadaptiv utan extra fördröjning enligt tillverkaren [D].
- Intels videosvit: bob lägger till några klockcykler, weave ett fält, rörelseadaptiv två rader (den använder sparade tidigare fält) [I].

Vår kod: `fb_display.v` mappar utrad till källrad med samma Bresenham-räknare för båda fälten och har ingen fältingång [K]. Enligt BT.656-tabellerna ligger rad n i F=1-fältet en halv källrad under rad n i F=0-fältet [R]. Fälten ritas alltså en halv källrad fel mot varandra (1,25–1,5 utrader vid 720p), och vågräta kanter hoppar i 25–30 Hz.

1. **Rätt läge:** källradens position för utrad j är u = (j + 0,5) · L/V − 0,25 i det övre fältet och − 0,75 i det undre (L fältrader, V utrader). Utan interpolation, avrundat till närmaste rad, flyttas det undre fältet två utrader vid 240 → 720. Felet går från 1,5 till 0,5 utrader utan kostnad.
2. **Interpolation i höjdled med två rader:** vid 240 → 720 återkommer faserna var tredje utrad (i tolftedelar 11, 3, 7 i det övre fältet och 1, 5, 9 i det undre), så det räcker med fasta vikter. Raden finns redan i ringen eller radbufferten. I LOW måste läsaren ligga en källrad till efter skrivaren (64 µs).
3. **Skalfaktorer:** 240 → 720 är × 3, det enda heltalet. 288 → 720 är × 2,5, 240 → 1080 × 4,5 och 288 → 1080 × 3,75. Med närmaste rad får raderna där omväxlande höjd (2/3, 4/5, 3/4 utrader); interpolationen tar bort det.
4. **I sidled:** 720p-fönstret tar källpixel x · 3/4 utan interpolation [K], så var tredje källpixel visas dubbelt. Linjär interpolation med faserna 0, 3/4, 2/4, 1/4 är skift och addition. Vid 1080p är × 2 exakt.
5. **Bildbredd:** PAL:s aktiva rad är 52 µs, alltså 702 av de 720 samplen vid 13,5 MHz [R]. Fyller alla 720 fönstret blir bilden upp till 2,5 % för smal. Kan lämnas.
6. **Rörelseadaptiv:** måste jämföra fält med samma paritet för att skilja rörelse från detalj i höjdled, alltså två sparade fält, och finns därför bara i BUF. Under flygning rör sig nästan hela bilden och metoden faller tillbaka på bob; snö ser ut som rörelse [H]. Nyttan är stillbilder. Vänta.

## 5. Buffrat läge som visar fältet som skrivs

**Idag:** `fb_sdram.v` publicerar ett fält först när nästa fälts första ord kommer (rad 97–107), och `fb_display.v` byter buffert vid bildstart [K]. Bilden visar därför alltid fältet före det som skrivs, och latensen överst i bilden är en till två fältperioder: 16,6–33 ms (NTSC), 20–40 ms (PAL till 60 Hz) [R].

**Förslaget:** vid bildstart väljs fältet som skrivs om skrivaren har hunnit N rader, annars senaste hela fältet.
- NTSC till 60,00 Hz: utgången läser en källrad på 66,7 µs, ingången skriver den på 63,6 µs. Läsaren hinner aldrig ifatt. N är pipelinens djup (FIFO, 8-ordsburst, och `fb_display` hämtar en utrad i förväg [K]).
- PAL till 60 Hz: läsaren tar 55,6 µs per källrad mot 64 µs och tar in 2,43 ms på ett fält, alltså 38 rader, plus pipelinen.
- Egen tidsmodell (inte RTL, ligger inte i repot): 400 000 utbilder, källan 37 ppm från nominell så att alla faslägen passeras, en utrad förhämtning och en källrad pipeline. Läsaren kommer aldrig före skrivaren med N = 3 (NTSC) och N = 41 (PAL) [R].

| Latens överst i bilden [R] | Idag | Förslaget |
|---|---|---|
| NTSC till 60,00 Hz | 16,6–33,3 ms, medel 25 | 0,1–16,8 ms, medel 8,5 |
| PAL till 60 Hz | 19,9–39,9 ms, medel 30 | 2,6–22,6 ms, medel 12,6 |

**Belägg för:**
- Tv-teknikens frame synchronizer: Lynx Technik beskriver att beslutet tas exakt vid bildstart och har en parameter som flyttar beslutspunkten 12 µs, så att en ingång strax efter referensen inte kostar en extra bild [D]. Det är samma beslut och samma tröskel. Att fördröjningen där går från noll till en bild beroende på fasen mellan ingång och referens har jag bara läst i utdrag ur patentskrifter [I].
- RetroTINK-5X: cirka 0,25 bild i Frame Lock och 0,25–1,25 bilder i Triple Buffering [D]. Ett läge som väntar in hela bilder kan inte komma under en bild, och lägsta värdet är detsamma som i låst läge. Min tolkning är att den läser bilden som skrivs; genomförandet är inte publicerat [H].

**Belägg emot, eller annan praxis:**
- OSSC Pro: skalare utan framelock 1–2 bilder, med framelock cirka 1 bild [D]. Hela bilder.
- MiSTer ascal: trippelbufferten byter till senast färdiga buffert vid utgångens vsync; läget med en enda buffert används bara låst [D].
- Intels Frame Buffer II: en bild [I].
- Inget hobbyprojekt hittat som beskriver metoden under något namn.

**Fallgropar:**
1. **Latensen varierar.** NTSC mot 60,00 Hz: en sågtand från 16,7 till 0,1 ms på 16,7 s, sedan ett språng på ett fält där ett fält visas två gånger [R]. BUF har samma språng idag, ett fält högre upp.
2. **Källa nära utgångens frekvens:** fasen kan bli liggande vid tröskeln, och valet växlar då mellan fältet som skrivs och det förra, med ett fälts latensskillnad. Kräver hysteres (olika tröskel in och ut). NTSC och PAL ligger långt ifrån och driver igenom.
3. **Rader som kommer sent eller i fel ordning** (M-4, V-1) läses innan de är skrivna, och bufferten visar då innehåll som är flera fält gammalt. Tröskeln ska räknas i rader som är skrivna till SDRAM, och fältet som skrivs ska bara väljas när källan levererar i ordning.
4. **Buffertregeln ändras.** Skrivaren skriver med avsikt i den visade bufferten. Invarianten blir "läsaren läser bara rader som skrivaren redan har skrivit i samma fält". Den behöver ett modelltest med negativ kontroll, och buffertvalet måste göras i SDRAM-domänen med skrivarens aktuella radräknare.
5. **Avbrutet fält:** tystnar källan mitt i fältet visar nederdelen buffertens gamla innehåll. Byt till senaste hela fältet när raderna slutar komma.

## Inte verifierat

- XREAL Airs EDID: läst i sökmotorns utdrag, ärendet kräver botkontroll. VITURE och Rokid: ingen EDID hittad.
- Hur LT6711A, andra bryggkretsar och glasögonen reagerar på växlande radantal, 59,94 Hz eller ändrad släckning.
- Vilka HDMI-format Fat Shark, Skyzone, DJI och Walksnail tar emot.
- ADV7513:s status och ingångstabell hos ADI (sidan svarade inte); IT66121, LT8618SXB, LT6711A, ANX7688 och Si5351A hos respektive tillverkare.
- 1080p60 på GW5A-25 med Apicula/nextpnr.
- Jitter och låsning hos två kaskadkopplade PLL:er för 74,25/1,001 MHz.
- Vilken fältbit TVP5150AM1 ger det övre fältet; åtgärderna i avsnitt 2 och 4 är skrivna så att det mäts.

## Källor

- XREAL Air EDID: [freedesktop drm/misc ärende 53](https://gitlab.freedesktop.org/drm/misc/kernel/-/issues/53) [I]. XREAL One: [specifikation](https://tutorials.xreal.com/docs/glasses/one-series/spec). XREAL-forum om adaptrar: [tråd 1666](https://community.xreal.com/t/nreal-air-display-misaligned-with-hdmi-to-usb-c/1666) [I]
- VITURE: [USB-C XR Charging Adapter](https://www.viture.com/academy/adapters/usb-c-xr-charging-adapter)
- HDZero: [it66021.c](https://github.com/hd-zero/hdzero-goggle/blob/main/src/driver/it66021.c), [hardware-goggle.c](https://github.com/hd-zero/hdzero-goggle/blob/main/src/driver/hardware-goggle.c), Goggle 2: tillverkarens produktsida (hd-zero.com, läst 2026-10-05)
- Walksnail Goggles X: tillverkarens produktsida (caddxfpv.com, läst 2026-10-05). DJI: [Goggles RE](https://www.dji.com/dji-goggles-re/specs)
- LT6711A: [isärtagen adapter](https://everydaything.substack.com/p/an-hdmi-to-usbc-display-port-converter), [melonHD-tråden](https://bitbuilt.net/forums/threads/melonhd.6782/); Lontiums datablad läst i utdrag [I]. ANX7688: [xnux.eu](https://www.xnux.eu/devices/feature/anx7688.html)
- DisplayPort MSA: [Linux-commit 24cfbec99647](https://github.com/torvalds/linux/commit/24cfbec99647d241c3c31a72d247ee81f9061b5b)
- OSSC Pro: [wiki](https://junkerhq.net/xrgb/index.php?title=OSSC_Pro)
- RetroTINK: 5X Pro: tillverkarens produktsida (retrotink.com, läst 2026-10-05), [4K](https://www.retrotink.com/blog/introducing-the-retrotink-4k), [firmware 2.73 med Gen Lock (RetroRGB)](https://retrorgb.com/?p=35121)
- GBS-Control: [klockgenerator och FrameTime Lock](https://ramapcsx2.github.io/gbs-control/Wiki/Si5351-Clock-Generator-install-notes.html); forumtråden "GBS 8200/8220 CFW Project", [inlägg 1455880](https://shmups.system11.org/viewtopic.php?p=1455880) med grannar [I]
- MiSTer: [MiSTer.ini](https://github.com/MiSTer-devel/Main_MiSTer/blob/master/MiSTer.ini), [ascal.vhd](https://github.com/MiSTer-devel/Template_MiSTer/blob/master/sys/ascal.vhd)
- TVP5150AM1 och halvraden: [SLES209E](https://www.ti.com/lit/ds/symlink/tvp5150am1.pdf) avsnitt 3.14, [TI E2E](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/535193/tvp5150am1-output-problem). GW2AR-18:s PLL: Gowin DS226
- ADV7513: [ADI](https://www.analog.com/en/products/adv7513.html) (svarade inte), [Linux-bindningen](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/display/bridge/adi,adv7511.yaml)
- TFP410: [TI](https://www.ti.com/product/TFP410), [datablad SLDS145D](https://www.ti.com/lit/ds/symlink/tfp410.pdf)
- IT66121: [Linux-drivrutinen](https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/bridge/ite-it66121.c). TDA19988: [NXP community](https://community.nxp.com/t5/NXP-Designs/TDA19988-Input-format/td-p/1063841) [I]
- GW5A: [DS1103-1.1E](https://cdn.gowinsemi.com.cn/DS1103E.pdf). Tang Primer 25K: [thisiseth/tang-primer-25k-spi-io](https://github.com/thisiseth/tang-primer-25k-spi-io). Apicula: [PyPI](https://pypi.org/project/Apycula/), [versionsnoter](https://github.com/YosysHQ/apicula/releases)
- ECP5: [FPGA-DS-02012-3.4](https://www.latticesemi.com/view_document?document_id=50461). Artix-7: [DS180](https://docs.amd.com/v/u/en-US/ds180_7Series_Overview) (inte öppnad)
- DisplayPort-kärna: [hamsternz/FPGA_DisplayPort](https://github.com/hamsternz/FPGA_DisplayPort)
- Intels videosvit, latenstabell: [683416](https://www.intel.com/content/www/us/en/docs/programmable/683416/19-4/latency.html) [I]
- Frame synchronizer: [Lynx Technik](https://support.lynx-technik.com/support/solutions/articles/1000333368-frame-synchronizer-decision-point-and-delay-optimization)
