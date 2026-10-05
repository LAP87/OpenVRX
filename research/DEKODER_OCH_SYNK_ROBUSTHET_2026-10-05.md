# Dekodersteget och synken: robusthet (2026-10-05)

Status: research, inget mätt. Fortsätter på `DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md`, `CVBS2HDMI_2026-10-04.md`, `ALTERNATIVA_VAGAR_2026-10-02.md`, `MOTTAGARE_ALTERNATIV.md` och granskningen 2026-10-05 (M-1 till M-7, V-1, V-2). Det som står där upprepas inte. Livscykelstatus är läst på tillverkarnas sidor 2026-10-05.

Belägg: **[D]** datablad eller tillverkarens produktsida, **[K]** källkod, **[P]** patent, **[T]** tillverkarens egen text utan teknisk redovisning, **[F]** forum eller användarrapport, **[H]** hypotes eller eget resonemang som ska mätas.

## Slutsats

Bedömning: svagheten ligger mindre i dekodervalet än i att FPGA:n litar på dekoderns rad- och fältnumrering. TI skriver själva att TVP5150AM1 ger ofullständiga fält och trasiga dataströmmar vid signalbortfall och brus [F, TI-anställd]. Ingen annan krets har belagt bättre beteende på FPV-signal: den enda FPV-rapport jag hittade gäller ADV7282A och är negativ [F]. En dekoderkrets fördröjer ungefär två rader (0,13 ms) [D, TW99xx], så latensen avgörs av bildbufferten och inte av dekodern.

| # | Åtgärd | Förväntad vinst | Insats |
|---|---|---|---|
| 1 | Svänghjulstidbas i FPGA:n: rader placeras efter ankomsttid, kanalens fasavvikelse blir kvalitetsmått, genlock triggas av tidbasen (avsnitt 5) | Stor. Tar bort felklassen bakom M-2 till M-5 och V-2 och ger ett mått på rivning, som HF-energin inte ser (M-7) | Medel: modell, RTL och slumptest. Ingen ny hårdvara |
| 2 | Dekoderinställningar över I2C: lås videostandard och TV/VCR-läge, läs den klibbiga "lost lock"-biten och radantalet (avsnitt 2) | Liten till medel [H] | Timmar: bara registertabell |
| 3 | Döljning av dåliga rader: föregående rad i LOW, giltig-bit per rad och ersättning vid utläsning i BUF (avsnitt 4) | Medel: enstaka trasiga rader syns inte | Medel |
| 4 | H-lås och V-lås på stift till FPGA:n (TVP5150AM1 stift 24 och 23) | Liten till medel. Reaktionstiden är inte dokumenterad | 1–2 stift per dekoder. Rev A har dem på testpunkter |
| 5 | Rå CVBS genom en ADC som tids- och brusreferens och för inspelning (avsnitt 3) | Medel. Ger riktiga data till REVIEW punkt 1 | Eget kort, 9 stift per kanal |
| 6 | TW9990 (Renesas, Active) som alternativ dekoder | Okänd: bättre insyn och fler inställningar är belagt, bättre lås är det inte | Utvärderingskort, ny registertabell |
| 7 | ISL79988 (Renesas, Active): båda kanalerna i en krets, låsstatus i varje rad | Okänd | Stor: ny mottagare i FPGA:n, 1,2 V-matning |
| 8 | Egen avkodning i FPGA:n i stället för dekodrar | Ingen latensvinst värd namnet | Mycket stor. Ryms inte i GW2AR-18 med två kanaler |

## 1. Kommersiella mottagare

Ingen tillverkare redovisar sin signalbehandling. Jag hittade inga isärtagningar med kretsbeteckningar och inga patent från ImmersionRC, TBS, Skyzone eller Iftron.

| Produkt | Det som finns belagt | Belägg |
|---|---|---|
| ImmersionRC rapidFIRE | Produkttext: bilderna från två mottagare slås ihop, modulen "rebuilds analog signals to avoid tearing, rolling, and dropped DVR frames, all with zero added latency". Lägen: rapidFIRE #1, #2 och Legacy (växlar på signalstyrka). Ändringslogg: #2 kom i 1.0.9 "to support cameras and other hardware that violates PAL/NTSC specs"; senare "Wider tolerance for cameras with unstable quartz oscillators"; 1.2.7 "Add ability to change sync-lock time"; 1.3.2 "Removed Sync Lock setting, defaults to short, eliminating rolling even with marginal systems" | T, produkttexten läst hos återförsäljare; ändringsloggen citerad i forum (F). Tillverkarens sida låg nere 2026-10-05 |
| TBS Fusion | Manualen: bildbehandlingen är BrainFPV:s. FUSION-läget rekommenderas "unless you experience issues with your video", då finns rent diversityläge. Antennerna behöver inte vara lika. Inget om metoden | T |
| Skyzone SteadyView/RapidMix | Två kort: mottagarkort och "fusion board". MIX2 "improves synchronization stability, especially under weak signal"; MIX3 "enhances the synchronization signal" och sänker ljusstyrkan; DIV väljer kanalen med högst RSSI. Mörk och rullande bild i tidiga versioner rättades med ny hårdvara (V3.3) | T, återgivet av Oscar Liang; F |
| Iftron ClearView | "stabilize the picture while reducing video noise in real time", utan latens. Inget patent hittat | T |
| SpeedyBee, Foxeer Wildfire | Inget tekniskt hittat | — |
| HDZero-glasögonens analoga ingång | En Techpoint TP2825 till FPGA:n. Lås läses över I2C (register 01h) med avstudsning: låst efter 10 läsningar i följd, tappat efter 5. Klampinställningen byts efter låstillstånd. Ingen mixning | K |
| Drone Racing League, US 9 813 659 och US 10 499 003 | Varje mottagare går genom en frame synchronizer (synkseparator, ADC, FIFO, DAC) som släpper bilden i takt med en gemensam synkreferens. Sedan blandas signalerna analogt med vikter ur RSSI. Motiv: växling mellan signaler ger avbrott i bilden och tvingar skärmen att låsa om | P |

Vad det säger:
- Alla som beskriver något stabiliserar eller ersätter synken före eller i samband med sammanslagningen. Det stöder en egen tidbas (avsnitt 5).
- Kompatibilitetslägen finns för att kameror bryter mot PAL/NTSC. En tidbas får inte anta nominell radfrekvens eller nominellt radantal.
- Belägg för sammanslagning per bildpunkt saknas. DRL blandar hela signalen efter RSSI. "Ingen extra latens" utesluter fältminne, alltså också döljning ur föregående fält [H].
- Att MIX3 sänker ljusstyrkan tyder på analog synkförstärkning, inte ny avkodning [H].

## 2. Dekoderkretsar

| Krets | Status hos tillverkaren | Utgång | ADC, kamfilter | Matning, kapsel |
|---|---|---|---|---|
| TVP5150AM1 (TI) | ACTIVE, med texten "No design support from TI available" | 8 bit BT.656 med inbäddad synk, radlåst 27 MHz | 9 bit; 4 rader | 1,8 V + 3,3 V; TQFP-32, BGA-48; kristall 14,31818 MHz |
| TVP5151 (TI) | ACTIVE, samma text | som ovan | som ovan | som ovan; kristall 27 MHz |
| ADV7180, ADV7182(A), ADV7280(A), ADV7282(A), ADV7283, MAX9526 (ADI) | Alla NOT RECOMMENDED FOR NEW DESIGNS | 8 bit BT.656, radlåst klocka | ADV: 10 bit, 4× översampling; 5 rader | ADV: 1,8 V + 3,3 V; LFCSP-32 med flera |
| TW9900 (Renesas) | Active | 8 bit BT.656, radlåst | 10 bit; 4 rader | 1,8 V + 3,3 V; QFN-32 4×4 mm; kristall 27 MHz |
| TW9990 (Renesas) | Active; datablad rev 6.01 från 2023 | som TW9900 | 2 × 10 bit; 4 rader | 1,8 V + 3,3 V; WFQFN-32 5×5 mm; AEC-Q100; −40 till +105 °C |
| TW9910, TW9912 (Renesas) | Active | TW9912: även progressiv utgång | TW9912: 3 × 10 bit; 4 rader | TW9912: QFN-48 7×7 mm |
| ISL79987, ISL79988 (Renesas) | Active; datablad rev 1.02 från 2024 | ISL79988: två kanaler radvis flätade på en 8-bitarsbuss vid 54 MHz, fyra vid 108 MHz | 10 bit per kanal; 4 rader | 1,2 V + 3,3 V; QFN-48 7×7 mm |
| GM7150BC (CorPro) | Inte verifierad | Liknar TVP5150: 14,31818 MHz, lås på FID- och PALI-stiften | 9 bit | QFN-32 |
| TP2825 (Techpoint) | Inget offentligt datablad hittat | — | — | — |

| Krets | Instabil eller saknad synk | Icke-sammanflätad källa | Fördröjning | Lås utan I2C-pollning |
|---|---|---|---|---|
| TVP5150AM1 | Ofullständiga fält och trasiga strömmar vid bortfall och brus [F, TI]. Svart bild utan källa [F, TI]. I automatläge går kretsen till VCR-läge vid instabil synk: kamfiltret av, färgfälla på [D]. Radlängden avviker vid störning (rrk1) [F] | 15h bit 5:4: F tvingas till 1 (standardvärdet), växlar eller pulsar. Uppmätt radantal i 84h/85h [D] | Inte angiven. Kamfiltret spänner över 4 rader (3 radfördröjningar) [D] | Stift 24 H-lås, stift 23 V-lås (03h bit 4, 0Fh bit 6 och 4). INTREQ på stift 27 vid låsändring (C0h, C1h) [D]. Reaktionstid inte angiven |
| ADV7180 (datablad), ADV728x (FAQ och forum) | Synkbehandling byggd för bandspelare och brus: radlängden mäts och predikteras och bilden samplas om till 720 punkter per rad [D]. Frigång med stabil klocka, synk och färgad bild; med frigången avstängd: "If the decoder is unlocked, it outputs noise" [D]. FPV-användare 2026: ADV7282A ger instabila EAV/SAV vid svag signal, olöst i tråden [F] | Statusbitarna INTERLACED och STD FLD LEN [D]. F-bitens beteende inte läst | 20–100 pixelklockor enligt ADI (tidigare underlag) | INTRQ med SD_LOCK och SD_UNLOCK [D]. Låsfiltret CIL/COL går att ställa från 1 till 100 000 rader [D] |
| TW9900/TW9990 | Digital H-PLL. HPM (infångningstid), VLCKI/VLCKO (in- och urlåsningstid vertikalt), MISSCNT (hur snabbt bortfall flaggas), FRM (frigång auto, 60 eller 50 Hz). Blå eller svart bild vid bortfall kan väljas. Svagsignalflaggor WKAIR och WKAIR1 [D]. Inga tider i sekunder angivna. Inga FPV-rapporter hittade | Statusbit NINTL; AFLD (automatisk fältgenerering) [D] | 2 rader [D] | MPOUT ger bortfall, H-lås, V-lås eller FIELD i realtid. INTREQ vid ändring [D] |
| ISL79988 | Samma inställningar som TW99xx: MISSCNT, HPM, VLCKI/VLCKO, FRM [D] | NINTL [D] | Inte angiven; FIFO per kanal | Valfri rubrik på 8 byte i varje rad: radnummer, fält, VDLOSS, HLOCK, VLOCK, V_STABLE. IRQ-stift [D] |

**TVP5150AM1: det som går utan att byta krets** [D, SLES209E]
- 28h: tvinga NTSC (0010) eller PAL (0100) i stället för autoswitch, som är standardvärdet. Två dekodrar i brus kan annars välja olika (granskningen U-3).
- 02h bit 5:4: samma fasta läge på båda. I automatläge kan den ena gå till VCR-läge och filtrera annorlunda än den andra; HF-måttet jämför då två olika filter [H]. Vilket läge som håller låset bäst ska provas.
- 88h bit 4 är klibbig: "Lost lock since status register #1 was last read". Läst vid varje pollning visar den bortfall kortare än 20 ms. Pollningen kan göras tätare, men hur ofta kretsen själv uppdaterar 88h står inte i databladet.
- 84h/85h: uppmätt radantal per bild. Avslöjar 240p/288p och andra radantal.
- Låsstiften: rev A drar stift 23–26 till testpunkter och stift 27 bara till ett motstånd (`Puck: design/rev_a/dekoderkort.py:318-326`). Exakt väljarlogik står i figur 3-12. Linux-drivrutinen använder INTREQ för låsändring [K].
- Tidsprocessorn är delvis program i en intern mikroprocessor (avsnitt 3.7). Databladet: "Use of the latest patch release is highly recommended" (3.21.44). Om TI fortfarande lämnar ut patchen är inte verifierat.

**Mest lovande alternativ: TW9990.** Skälen är belagda i databladet, inte i mätningar: realtidsstift för lås, flaggor för svag signal och icke-sammanflätad källa, inställbara låstider, dokumenterad fördröjning, ingen firmwarepatch, datablad uppdaterat 2023. XTI tar en extern 27 MHz-klocka, så en oscillator bör kunna mata båda dekodrarna [H]. Det som saknas är belägg för att den håller låset bättre än TVP5150AM1 på FPV-signal. Den ska provas på utvärderingskort mot samma svaga signal innan den ritas in.

ADV7842 (ADI, Recommended for New Designs) kan enligt en användare frigå med avkodad bild [F], men är en HDMI-mottagare som bara säljs till HDMI-adopters [D]. Inte aktuell.

**Ändringar i FPGA:n vid byte**

| Byte till | I2C | BT.656-mottagaren | Övrigt |
|---|---|---|---|
| TVP5151 | Samma Linux-drivrutin som TVP5150AM1 [K] | Oförändrad | 27 MHz-kristall |
| TW9900/TW9990 | Ny registertabell; status i 01h och 31h | Oförändrad i princip: 8 bit BT.656, radlåst klocka | MPOUT på ett stift |
| ISL79988 | Ny registertabell | Ny: 54 MHz, kanal-ID i EAV/SAV, rubrik per rad | En klockdomän och en FIFO mindre; 9 stift i stället för 18. Raderna lämnar kretsen hela och i den ordning de blir klara, så ankomsttiden blir grövre [H] |
| ADV-familjen | Ny registertabell | Oförändrad i princip | Avrådes: NRND |

## 3. Direkt digitalisering

CVBS2HDMI (MIT) är den enda fullständiga öppna färgavkodaren i HDL jag hittade. Övrigt öppet är programvara: `ld-decode` och `vhs-decode` (TBC, bortfallsrättning, PAL-kamfilter).

Vad robusthet kräver, ur CVBS2HDMI:s labbdagbok [K] och ADV7180-databladet [D]:
- **Synkseparator:** lågpass som tar bort färgbärvågen före tröskeln; pulsbredden avgör om det är H eller V. "Detection and position want different thresholds — and you cannot have both": hög tröskel hittar synken men ger fel läge, låg tröskel ger rätt läge men missar pulser. ADV7180 gör det i två steg: "a coarse detection based on a threshold crossing, followed by a more detailed detection using an adaptive interpolation algorithm".
- **DC-återställning:** digitalt från svartnivån. Analog klampning störde synken (tidigare underlag).
- **Horisontellt svänghjul:** inlärd radperiod; tvingade radstarter bara i låst läge. Deras regler: "Never learn the period from a counter that forced starts also reset" och "Do not run the flywheel during acquisition". Falskt lås förekommer: "a picture edge that dips below the threshold at the same point on every line is a self-consistent false lock".
- **Vertikalt:** en låg nivå längre än en rad kan bara vara vertikalsynk. Renesas-kärnan använder ett fönster: "the actual sync determination is controlled by a detection window" [D].
- **Frigång:** med `FREE_RUN` visades 60 av 60 brusbilder mot 1 av 60 utan. Lås efter 104–105 rader.
- **Färg:** NCO på färgbärvågens frekvens; burstens fas mäts på varje rad med CORDIC. Bara NTSC.

Resurser: labbdagboken anger 58 % av LUT:arna i GW2A-18 för konstruktionen byggd utan DSP och ALU, och 76 % av LUT4 och 44 av 46 BSRAM i avsnittet om zoomringen [K]. M6 använder redan 10 330 av 20 736 LUT4 (granskningen). Två egna avkodare ryms inte bredvid mixern utan omkonstruktion.

Latens: en dekoderkrets fördröjer cirka två rader. Egen avkodning kan som mest spara det, 0,13 ms. CVBS2HDMI:s låga fördröjning kommer av att bildbufferten saknas, och det gör redan LOW-läget.

Det som blir sämre: PAL saknas. Y/C-separationen är ett medelvärde över 7 sampel med nollställe vid 3,6 MHz; luman är då nere 3 dB vid ungefär 1,6 MHz (min räkning: 0,443 × 25,2 MHz / 7), medan ett kamfilter behåller luma förbi färgbärvågen. 8 bitar mot dekodrarnas 9–10, och ingen förstärkningsreglering före ADC:n (kortet har bara terminering och AC-koppling, tidigare underlag). ADC:ns läsögonblick måste kalibreras [K].

**Hybriden: en ADC bredvid dekodrarna.** Rimlig, först som mätverktyg:
- FPGA:n ser synken före dekodern. Tidbasen blir oberoende av dekoderns lås och firmware.
- Brus kan mätas där signalen är känd: i synkbotten och på svartnivån. Måttet beror inte på bildinnehållet och täcker luckorna i M-7 (platt rad vinner, jämförelse ur takt). ADV7180 har ett brusmått i register (ST_NOISE) [D]. Nyttan för mixern är inte mätt [H].
- Rå CVBS kan spelas in och spelas upp i simulering, som CVBS2HDMI gör. Det ger riktiga testvektorer till mixern (REVIEW punkt 1).
- AD9280 (ADI, Production) behöver 8 datastift och klocka per kanal. De finns inte på Tang Nano 20K bredvid två dekodrar: M6 använder alla stift (granskningen). CVBS2HDMI:s ADC-kort kan användas fristående för inspelning av en kanal.
- Bara tidsreferens går med ett stift per kanal: en synkseparator som LMH1981 (TI, ACTIVE, 50 % tröskel). Den ger inget brusmått, och hur den beter sig i FPV-brus är inte belagt.

## 4. Tidbaskorrigering och döljning

| Praxis | Vad den gör | Motsvarighet här |
|---|---|---|
| Rad-TBC | Buffrar signalen i ingångens ojämna takt och läser ut i jämn takt | Dekoderns radlåsta klocka plus FIFO till systemklockan. ADI kallar sin variant "mini-TBC" [D] |
| Bild-TBC, frame synchronizer | Minst en bild i minnet, skrivs med ingångens synk och läses med egen referens. Vid bortfall hålls senaste hela bild: "freeze the last good frame" (Evertz) [D] | BUF: SDRAM-trippelbuffert och fri utgångsklocka |
| Bortfallskompensator i videobandspelare | Detekterar bortfall på FM-bärvågens amplitud och byter till signalen en rad tidigare (1H-fördröjning) [P] | Radmixer plus döljning. RSSI är samma slags detektor; RX5808:ans RSSI-bandbredd är inte mätt [H] |
| `ld-dropout-correct` | Ersätter bortfall ur det andra fältet som standard, inom fältet som val (`--intra`) [K] | — |

Döljning av en dålig rad:

| Metod | Kräver | Artefakt |
|---|---|---|
| Föregående rad i samma fält | En rad i minne; ingen extra latens | Trappsteg på sneda kanter. Flera rader i följd blir ett utdraget band |
| Medel av raden över och under | En rads väntan (64 µs) och två bra grannar | Mjukare än upprepning; lokal oskärpa |
| Samma rad i föregående fält | Fältminne | Motsatt paritet ger en halv rads höjdfel. Innehållet är 17–20 ms gammalt: vid rörelse dubbelkontur eller ett förskjutet band |
| Samma rad två fält tillbaka | Två fält i minne | Inget höjdfel; 33–40 ms gammalt |
| Median av över, under och föregående fält | Fältminne och en rads väntan | Standard i deinterlacers (de Haan och Bellers 1998, inte öppnad i dag). Blir tidslig ersättning när grannraderna också är dåliga |

Artefakterna följer av fältgeometrin [H]; ingen är mätt här. FPV-bilden rör sig nästan alltid, så en rad ur föregående fält visar förskjutet innehåll. Enstaka rader döljs därför bäst inom fältet. Föregående fält passar långa bortfall, där upprepning ger ett platt band.

Med ett fält i minne:
- **BUF:** en giltig-bit per rad och buffert (3 × 288 bitar). Skrivaren hoppar över dåliga rader och nollar biten. Utläsningen ersätter raden med raden ovanför eller med samma rad i den buffert som visades senast. Hoppar man bara över skrivningen ligger två till tre fält gammalt innehåll kvar, ibland med fel paritet.
- **LOW:** inget fältminne (ring på 16 rader). Bara föregående rad, eller medelvärde mot en rads extra latens.

## 5. Svänghjulsförslaget: för och emot

Förslaget: rad- och fälträknare i FPGA:n som låses långsamt till den friskare dekoderns tider. Varje rad placeras efter ankomsttid. Dåliga eller saknade rader döljs.

Core 57cd08d numrerar rader från vertikalsläckningen och parar rader som har samma nummer och kommer inom `T_PAIR` = 1 024 cykler (15,8 µs) från varandra. Det är en jämförelse mellan kanalerna. Svänghjulet lägger till en referens som finns kvar när en kanal saknas eller har fel fältfas.

**För**
- Båda mottagarna får samma tidbas från samma sändare (rrk1, tidigare underlag).
- Dekoderns numrering håller inte vid störning. TI: "the TVP will output partial fields/frames when a video signal is attached/disconnected" och "you will absolutely receive corrupt data streams due to signal loss, plug/unplug events, noise" [F, TI-anställd]. Granskningens E2–E5 visar följderna.
- Tidigare känt: synkåterskapning med fönster och räknare som frihjular vid bortfall (BBC, US 5 495 294) [P]; gemensam synkreferens före mixning (DRL) [P]; frame synchronizers; rrk1:s svänghjul på HDMI-sidan. Dekodrarna gör samma sak internt: ADV7180 har ett "line-length measurement and prediction block" [D].
- CVBS2HDMI:s mätning: frigång gav 60 av 60 brusbilder på skärmen mot 1 av 60 [K].
- rapidFIRE hade en inställning för "sync-lock time" och slutade på kort tid [F].
- Fasavvikelsen mot tidbasen mäter rivning direkt. En dekoder vars H-PLL ligger fel ger rader vid fel tid och bild som är förskjuten lika mycket. HF-energin ser inte det (M-7) [H].
- Utgången skyddas: genlock får sin trigger ur tidbasen i stället för ur varje fältstart (V-2) [H].

**Emot och felsätt**
- Ankomsttiden betyder något bara så länge dekoderns H-PLL är låst. Radtiderna kommer ur PLL:en, inte direkt ur ingångens synk. Efter tappat lås frigår kretsen: "Even when lock is lost the TVP will generate free running syncs" (TI E2E, bara läst som sökutdrag). ADV7180 ger i frigång stabil klocka, HS och VS utan samband med ingången [D]. En frigående kanal driver genom fönstret och hamnar tidvis rätt av en slump. Det krävs flera rader i följd inom fönstret, inte en.
- PLL:en skakar vid svag signal: "27M output from 5150 in proven to have huge jitter, especially when input signal is fading on the Rx" (rrk1) [F]. Fönstret måste vara bredare än skakningen och skiljer då sämre. Storleken är inte mätt.
- Strömmen kan sakna rader eller ha extra. ADV7282A på FPV-signal gav instabila EAV/SAV [F]. Räknaren måste tåla båda. CVBS2HDMI hittade tre av fem fel genom att kräva att funna och tvingade radstarter summerar till radtakten [K].
- Långsam låsning ger långsam återhämtning när tidbasen verkligen hoppar (kameran startar om, en OSD-krets tar över, kanalbyte). ClearView anger 5–30 s och rrk1 20 s (tidigare underlag).
- Falskt lås: tidbasen kan låsa till en dekoder som själv ligger fel och stanna där. Samma mekanism finns beskriven i CVBS2HDMI [K].
- Kameror utanför standard (rapidFIRE:s ändringslogg) [F]: radperiod och fältlängd måste läras in.
- Döljning ur föregående fält ger rörelsefel och finns bara i BUF (avsnitt 4).
- Om de två dekodrarna har olika rörfördröjning, till exempel i TV- respektive VCR-läge, blir fasmåttet fel. Inte dokumenterat [H].
- Mer logik att verifiera. RTL och modell har redan gått isär en gång (M-1).

**Vad dekodern gör med radtiderna**

| Tillstånd | Radtider | Numrering | Belägg |
|---|---|---|---|
| H och V låsta | Följer ingången, med PLL:ens skakning | Rätt | D |
| H låst, V olåst eller fel fältfas | Följer ingången | Fel | H: inte dokumenterat |
| H olåst | Frigång i kristallens takt; fasen driver | Fel; ofullständiga fält i övergångarna | F (TI), D (ADI) |
| Ingen källa | TVP5150AM1: svart bild med synk | — | F (TI) |

**Villkor för att förslaget ska hålla** [H]
1. Tidbasen lär sig radperiod och fältlängd ur rader i följd från en kanal med H-lås. Inga nominella värden antas. I systemklockan (64,8 MHz) är en NTSC-rad 4 118,4 cykler och en PAL-rad 4 147,2; en cykel är 0,2 bildpunkter.
2. En kanal räknas som i fas först efter N rader i följd inom fönstret. En kanal ur fas är `bad` oavsett HF-energi.
3. Två hastigheter: snabb infångning, långsam följning. Omlåsning direkt när en frisk kanal ligger stadigt fel.
4. Utan frisk kanal frihjular tidbasen. Skärmen visar då brus eller senaste fält, aldrig svart. En FPV-användare formulerar kravet: "static is acceptable, but the monitor should not blank" [F].
5. Modell och slumptest med riktig fältgeometri före RTL (M-6).

**Mät först** (kräver kort)
- TVP5150AM1 mot en signal som dämpas stegvis: SAV-ankomst per rad mot en dekoder på ren signal, låsstiften och 88h. Det ger PLL:ens skakning, fönsterbredden, låsstiftens reaktionstid och vad som händer efter tappat H-lås.
- Rörfördröjningen i TV- och VCR-läge: puls in, BT.656 ut.
- Om rader som dekodern märker som släckning (V = 1) ändå bär bild när V-låset är fel.

## Inte verifierat

- Kretsar och metoder i rapidFIRE, Fusion, SteadyView, ClearView, SpeedyBee och Wildfire. ImmersionRC:s sida låg nere. getfpv:s artikel om ClearView och rcgroups-trådarna ligger bakom botkontroll.
- TI E2E utom en tråd (botkontroll). Uttalandet om frigående synk, tråden om utgångsjitter och tråden om patchfilen är bara lästa som sökutdrag.
- ADV7180-databladet är läst i rev. A (2006) via en spegling; aktuell rev. K och UG-637 gick inte att hämta. Att ADV728x har samma CIL/COL-register är inte kontrollerat. Lås- och avbrottsbitarna är bekräftade i ADI:s FAQ.
- TW9910-databladet är inte läst.
- GM7150BC: livscykeln gick inte att läsa hos CorPro. Databladet är version 1.7 från maj 2018, läst via en distributörs spegling.
- Allt märkt [H].

## Källor

Dekodrar, TI
- [TVP5150AM1 datablad SLES209E](https://www.ti.com/lit/ds/symlink/tvp5150am1.pdf): 3.7, 3.21.3, 3.21.4, 3.21.15 med figur 3-12, 3.21.20, 3.21.32, 3.21.44–46, 3.21.49, 3.21.62–63
- [TVP5150AM1 produktsida](https://www.ti.com/product/TVP5150AM1), [TVP5151 produktsida](https://www.ti.com/product/TVP5151), [TVP5151 datablad SLES241E](https://www.ti.com/lit/ds/symlink/tvp5151.pdf)
- [TI E2E: TVP5150AM1 output problem](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/535193/tvp5150am1-output-problem) (läst; svar av TI-anställd)
- TI E2E, bara sökutdrag: [tvp5150 losing lock](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/137314/tvp5150-losing-lock), [tvp5151 sync issue](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/272424/tvp5151-sync-issue), [video output jitter](https://e2e.ti.com/support/interface-group/interface/f/interface-forum/822636/tvp5150am1-video-output-jitter-of-tvp5150am1), [patchfilen](https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1656982/tvp5150am1-request-for-tvp5150am1-firmware-patch-binary-per-slea093-body)
- [Linux tvp5150.c](https://github.com/torvalds/linux/blob/master/drivers/media/i2c/tvp5150.c)

Dekodrar, ADI
- Produktsidor (status): [ADV7180](https://www.analog.com/en/products/adv7180.html), [ADV7182](https://www.analog.com/en/products/adv7182.html), [ADV7182A](https://www.analog.com/en/products/adv7182a.html), [ADV7280](https://www.analog.com/en/products/adv7280.html), [ADV7280A](https://www.analog.com/en/products/adv7280a.html), [ADV7282](https://www.analog.com/en/products/adv7282.html), [ADV7282A](https://www.analog.com/en/products/adv7282a.html), [ADV7283](https://www.analog.com/en/products/adv7283.html), [MAX9526](https://www.analog.com/en/products/max9526.html), [ADV7842](https://www.analog.com/en/products/adv7842.html), [AD9280](https://www.analog.com/en/products/ad9280.html)
- [ADV7180 datablad](https://www.analog.com/media/en/technical-documentation/data-sheets/ADV7180.pdf): Sync Processing, Lock Related Controls, DEF_VAL_EN, DEF_VAL_AUTO_EN, Status 1–3, registerkartan (läst i rev. A)
- ADI EngineerZone: [låsavbrott på INTRQ](https://ez.analog.com/video/a/documents/do8903/how-to-program-an-interrupt-to-tell-if-the-adv7182-adv728x-has-locked-or-lost-locked), [låsbitarna](https://ez.analog.com/video/a/documents/do8904/how-to-tell-if-the-adv7180-adv7182-adv728x-has-locked-to-a-video-source), [ADV7282A med FPV-mottagare, 2026](https://ez.analog.com/video/f/q-a/604325/video-decoder-adv7282a-outputting-noise-instead-of-blue-screen)
- [Linux adv7180.c](https://github.com/torvalds/linux/blob/master/drivers/media/i2c/adv7180.c)

Dekodrar, Renesas och övriga
- [TW9990](https://www.renesas.com/en/products/tw9990), [datablad FN8406 rev 6.01](https://www.renesas.com/en/document/dst/tw9990-datasheet): Sync Processor, Vertical Timing, register 01h, 19h, 26h, 28h, 2Eh, 2Fh, 31h, 33h, B1h
- [TW9900](https://www.renesas.com/en/products/tw9900), [datablad FN7767 rev 5.00](https://www.renesas.com/en/document/dst/tw9900-datasheet); [TW9910](https://www.renesas.com/en/products/tw9910); [TW9912](https://www.renesas.com/en/products/tw9912), [datablad FN7945 rev 2.00](https://www.renesas.com/en/document/dst/tw9912-datasheet)
- [ISL79988](https://www.renesas.com/en/products/isl79988), [ISL79987](https://www.renesas.com/en/products/isl79987), [datablad FN8907 rev 1.02](https://www.renesas.com/en/document/dst/isl79987-isl79988-datasheet): Sync Processing, BT.656 Line-Interleaved Output, BT.656 Optional Header
- CorPro GM7150BC, datablad version 1.7, maj 2018
- [LMH1981](https://www.ti.com/product/LMH1981)

Kommersiella mottagare och patent
- [US 9 813 659 B1](https://patents.google.com/patent/US9813659B1/en), [US 10 499 003 B2](https://patents.google.com/patent/US10499003B2/en) (Drone Racing League, prioritet 2016-05-11)
- [HDZero: hardware-goggle.c](https://github.com/hd-zero/hdzero-goggle/blob/main/src/driver/hardware-goggle.c), [tp2825-goggle.c](https://github.com/hd-zero/hdzero-goggle/blob/main/src/driver/tp2825-goggle.c)
- [rapidFIRE:s ändringslogg, citerad på intofpv](https://intofpv.com/archive/index.php/thread-11932-2.html); [Oscar Liang om rapidFIRE](https://oscarliang.com/immersionrc-rapidfire-module/)
- [Oscar Liang om SteadyView V3.3](https://oscarliang.com/skyzone-steadyview-module-fusion-v3-3/)
- [TBS Fusion, manual rev 2025-11-13](https://www.team-blacksheep.com/tbs-fusion-manual.pdf)
- ClearView: tillverkarens beskrivning (clearview-direct.com, läst 2026-10-05)

Egen avkodning, TBC och döljning
- [otanl/CVBS2HDMI](https://github.com/otanl/CVBS2HDMI), [labbdagboken CLAUDE.md](https://github.com/otanl/CVBS2HDMI/blob/master/CLAUDE.md)
- [US 5 495 294](https://patents.google.com/patent/US5495294A/en) (BBC, synkåterskapning med fönster)
- [US 4 245 262](https://patents.google.com/patent/US4245262A/en) (Matsushita, bortfallskompensator; beskriver den vanliga lösningen i bakgrunden)
- [Wikipedia: Time base correction](https://en.wikipedia.org/wiki/Time_base_correction); [Evertz 7847FSE](https://evertz.com/products/7847FSE)
- [ld-decode-verktygen, wiki](https://github.com/oyvindln/vhs-decode/wiki/ld-decode-tools)
- G. de Haan och E. B. Bellers, "Deinterlacing: an overview", Proc. IEEE 86(9), 1998, s. 1839–1857, [doi:10.1109/5.705528](https://doi.org/10.1109/5.705528)
