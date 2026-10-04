# Videodekodrar för eget FPGA-kort — kunskapsunderlag 2026-09-30

Status: research inför rev A. Inget beställt. Rådata i `research/raw/decoders/`. Påståenden från forum är användarrapporter, inte mätningar, om inget annat anges.

## Viktigaste fynd: det finns ett FPV-förebild

**rrk1/FPGA-FPV-scaler** (GitHub, GPL-3.0, senast uppdaterat 2017; README läst). Konstruktion: TI **TVP5150AM1** → Xilinx **Artix-7 (XC7A35T devkort)** → 720p HDMI/DVI. Byggd för analog FPV till Avegant Glyph.

Hur den fungerar (enligt README + författarens inlägg i [rcgroups-tråden](https://www.rcgroups.com/forums/showthread.php?t=2993411), läst i webbläsaren):
- FIFO mellan 27 MHz-domänen och en egen HDMI-klocka; HDMI-sidan låses långsamt mot analog VSYNC ("flywheel timebase corrector") så att störningar på analogsidan inte ger HDMI-glitchar.
- Bob-deinterlacing + närmaste-granne-skalning, radbuffert, ingen bildbuffert.
- Författaren anger latens "<<2ms" — **egen uppgift, inte oberoende mätt**.
- Bara ca 1/4 av FPGA:n användes; författaren nämner diversity, stereo och egen panelstyrning som möjliga tillägg.

Kända problem som författaren själv listar (verbatim i README):
- "Locking onto input video takes about 20 seconds."
- Vid stört mottagande: "FIFO buffer gets overflown/underflown and video output gets garbled."
- TVP5150AM1:s BT.656-radlängd är inte alltid 720 pixlar när signalen är störd.
- Ingen automatisk PAL/NTSC-detektering; manuell omkopplare.
- Vissa HDMI-mottagare kräver +5 V på HDMI-kabeln; han använde ca 200 Ω seriemotstånd.
- TVP5150-modulen saknade reset-anslutning; han fick dra en extra tråd.

Filträdet innehåller bara `scaler.zip` (källkod/bitström), inget PCB — hans bygge var devkort + modul.

Andra FPV-relaterade projekt (README/filträd lästa):
- **kllsd/rx5808_x2_otg** (GPL-3.0, 2024): två RX5808 + MS2107 USB-capture + CH32X035-MCU → USB/UVC till telefon/dator. Ingen mixing nämnd. Varnar för USB-kablar över 30 cm.
- **ChisBread/RX5808-Div** (GPL-3.0, 2022): två RX5808 + ESP32 med LCD/OSD. Ingen mixing nämnd.
- **marqs85/de2-vd** (OSSC-författaren, GPL-3.0, 2017): videodigitizer för DE2-115. Anger "very low latency (less than 2 input scanlines)". Varnar att dess 720p-läge inte matchar standard-720p och kanske inte fungerar på alla skärmar — relevant för XR-glasögon.

Inget hittat öppet projekt gör riktig bildmixning mellan två mottagare. Det är därför fortfarande den egna, nya delen.

## TVP5150/TVP5150AM1 — fallgropar ur TI E2E och StackExchange

(Extraherat av DeepSeek V4 Pro via A0; alla citat kontrollerade mot källfilerna med skript.)
- **Lås-status:** Status Register #1 (0x88). *Rättat 2026-10-01 mot TI-databladet SLES209E:* bit 0 = TV/VCR, bit 1 = H-lås, bit 2 = V-lås, bit 3 = färgbärvågslås, bit 4 = "lost lock" sedan senaste läsning, bit 5 = 50/60 Hz. Status Register #2 (0x89) bit 6 = **"Weak signal"**. Båda användbara som kvalitetsingång för mixern. (StackExchange-citatet blandade ihop bitarna.)
- **Ingångsnivå:** TI rekommenderar en divide-by-2-dämpare ("R75 (75 ohms) could be replaced with two 37.4 ohm resistor") och 0,1 µF kopplingskondensator i stället för 0,47 µF. TI-svar: insignal utanför område kan ge falska färger.
- **Kristall:** rätt lastkondensatorer, ≤50 ppm, samt 100 kΩ parallellt med kristallen (TI-rekommendation).
- **Anti-alias-filter** externt rekommenderas.
- **Brus/fel färger** kan bero på sampling på fel klockflank eller Cb/Cr-förväxling.
- En StackExchange-tråd med utdata "0x80/0x10" och noll lås-bitar förblev olöst.

## ADV7180 — fallgropar ur ADI EngineerZone och Toradex

- **Clamp/ingångsområde** (ADI-svar, EngineerZone 2011): ADC-området är 1,0 V; en insignal som ofta ligger utanför gör clampen instabil, och starka ljuskällor kan få bilden att tappa. (Användarens misstanke om svagare clampströmmar än ADV7181B bekräftades inte av ADI.)
- **Synk-utgångar:** ADV7180 ger bara HS, VS och Field, ingen DE. Liten logik i FPGA/CPLD behövs för att ta fram aktiv bild. HS kan bara flyttas begränsat.
- **Toradex-tråd:** blå bild + opålitlig I2C; misstänkt orsak var jord/kopplingsstörningar mellan analog och digital del. Råd: korta kablar och seriemotstånd på parallellbussen. Orsaken bekräftades inte slutligt.

## Tillgänglighet hos LCSC (läst 2026-09-30 i webbläsaren)

Alla träffar låg under **"Other Suppliers"**, inte LCSC:s eget lager. Hur JLCPCB-bestyckning hanterar sådana delar (global sourcing/leveransbeställning) är **inte kontrollerat**.
- TVP5150AM1PBS (C3824301): 3,74 USD vid 30+ (5–7 dagar) eller 19,32 USD vid 5+ (3–5 dagar).
- TVP5150AM1PBSR (C10013): 2 477 st, 10,82 USD vid 5+ (3–5 dagar).
- ADV7180BCPZ (C11164): 65 st, 1,69 USD (3–5 dagar). Övriga ADV7180-varianter 41–43 dagars ledtid.
- ADV7280BCPZ (C579437): 41–43 dagar, ca 16,7 USD vid 100+.
- TW9912: inga träffar.

## Vad detta betyder för rev A (min bedömning, inte beslutad)

1. **TVP5150AM1 som förstaval**, ADV7180 som reserv: det finns ett FPV-bevis för kedjan, TI-rekommendationer för ingången, och delar hos LCSC-leverantörer.
2. **Ingångssteg med alternativ:** 75 Ω-terminering eller 2×37,4 Ω dämpare, 0,1 µF, ESD, testpunkt på CVBS. Nollohmsbyglar så vi kan byta utan nytt kort.
3. **Reset, I2C-pullups och 14,31818 MHz-kristall enligt TI**, med testpunkter. *(Rättat 2026-10-01 efter Astras granskning: tidigare stod 27 MHz. TVP5150AM1 tar 14,31818 MHz som referens och genererar själv 27 MHz-klockan på SCLK.)*
4. **FPGA-logik måste tåla trasiga rader** (inte anta 720 px/rad) och läsa lås-status per dekoder. Snabbare låsning än rrk1:s 20 s är ett uttalat mål.
5. **Två dekodrar redan i rev A** så att mixning kan provas senare utan nytt kort.
6. **HDMI:** +5 V med strömbegränsning, standardtiming (inte "nästan 720p"), eftersom XR-glasögon kan vara kinkiga.

## Öppna källor som inte kunde läsas automatiskt

- Raspberry Pi-forumet (bot-verifiering): [ADV7282-M latens](https://forums.raspberrypi.com/viewtopic.php?t=357215).
- ADI EngineerZone: [ADV7282M output delay/latency](https://ez.analog.com/video/f/q-a/573972/adv7282m-output-delay-latency) — ej hämtad ännu.
- intofpv (bot-skydd) från tidigare runda.
- OpenCLI kunde inte användas: Chromium-tillägget "Browser Bridge" var inte anslutet.

## Workerlogg och kostnad

A0-ledger, anrop 84–97 i dag: summa **0,0725 Diem-ekvivalent**.
- GLM 5.3 Flash misslyckades 6 av 6 på riktiga extraktionsjobb: alla 2 048 output-tokens gick till resonerande, tomt svar. Varken `disable_thinking` eller `reasoning_effort: "none"` hjälpte (mikroprob med "svara OK" lyckades, receipt 90). `thinking`-parametern gav HTTP 400 (receipt 91). Kostnad för misslyckade GLM-anrop ca 0,013.
- DeepSeek V4 Pro (`deepseek-v4-pro`, 1,65/3,30 USD per miljon in/ut enligt Venice publika prislista) klarade 3 av 3 med 0 resonemangstokens; ca 0,056 totalt. Den är nu tillagd i `scripts/a0_budget_client.py` (pris) och `scripts/a0_run.py` (val); 21 tester passerar.
- Promptar: `job_d1_tvp5150_pitfalls.md`, `job_d2_adv7180_pitfalls.md`, `job_d3_precedent_projects.md`.

## Tillägg 2026-09-30 (kväll): blockerade källor lästa via användarens Chromium (OpenCLI)

Hämtat: rcgroups-tråden sida 1–6, RPi-forumets ADV7282-M-latenstråd (2 sidor), tre intofpv-trådar, Reddit-inlägget om en vidareutveckling. Fem snäva DeepSeek V4 Pro-jobb (receipts 98–102, ca 0,19) extraherade; 139 citatsegment kontrollerades med skript och samtliga återfanns i källorna (fem krävde manuell kontroll pga smileys/kodblock/citatstart).

**rcgroups (rrk1 m fl):**
- rrk1: "27M output from 5150 in proven to have huge jitter, especially when input signal is fading on the Rx." → Klocka inte hela bildkedjan från dekoderns 27 MHz utan eget skydd.
- rrk1: "Any dropouts on radio cause HDMI monitor to blank for a few seconds." (om kommersiell box/HDMI-sidan) och en föreslagen markör för signalfading: plötslig h-sync-förskjutning.
- rrk1 om mixning: "syncing multiple receiver channels don't seems to be a big problem. They all run from the same crystal-controlled source" (dvs. samma VTX). Användare spekulerar att ClearView/RapidFire jämför rad för rad. Ingen i tråden byggde mixning.
- Senare användare lade till automatisk PAL/NTSC via TVP5150:s field-rate-register, och uppskattade skalningens extra latens till ~0,15 ms (två radbuffertar).
- Kompatibilitet: fungerade med Avegant Glyph och Fat Shark HD2; Topsky F7X och en kinesisk HDMI-inspelare vägrade 720p50/720p60 från skalaren.
- En användare föreslog TVP5156 i stället för TVP5150 för egen PCB (ej motiverat närmare).
- **pthalin/video_scaler** (GPL-3.0, 2018): omskriven, uppstädad version med uppackad VHDL (`src/*.vhd`) och Artix-7-constraints. Bättre startpunkt än rrk1:s zip.

**Raspberry Pi + ADV7282-M (CSI):** ca 130 ms med `gst-launch-1.0 v4l2src ! glimagesink` (ingen mätmetod angiven). Orsaker enligt Pi-utvecklare: textur/kompositering i GL, kmssink låst till utgångens vsync, CPU-konvertering. ADV7282 har max 3 raders buffert själv. Ingen lägre siffra rapporterades efter optimering. → Pi-spåret är inte låglatens utan mycket eget arbete; stödjer FPGA-vägen.

**intofpv, mätningar av skärm-/goggle-latens (240 fps mobilkamera, samma användare):**
- Skyzone Cobra X V2 HDMI-ingång: 37 ± 4 ms. Analog helkedja: Skyzone 23 ± 6 ms (första ljusa pixel) / 35 ± 6 ms (första ljusa fält); Fat Shark Scout 40 ± 5 / 55 ± 6 ms. Walksnail VRX via HDMI i Cobra X: 71 / 83 ms. Desview P5II-monitor: "i storleksordningen 60 ms" (ej färdigräknat).
- Skyzone uppges förklara HDMI-latensen med att FPGA:n roterar bilden 90° för stående mobilpaneler. → Välj panel/skärm som skannar i landskapsläge, eller acceptera halvbildsfördröjning.

**intofpv "fpv glasses POC" (VITURE):** källan var digital HD, inte analog. 1080p60 gav "avg latency of 60ms" (ej formellt mätt). 720p fungerade inte: glasögonen annonserar inte 720p i EDID. HDMI→USB-C via VITURE Pro mobile dock; strömförsörjning (USB-C PD) var en begränsning. → Vår CVBS→HDMI-kedja måste leverera 1080p60 till sådana glasögon, eller verifiera EDID först.

**intofpv, mottagarjämförelse (användarrapporter, ej mätningar):**
- mstc: i direkt jämförelse började RapidFire rulla medan SpeedyBee höll bilden.
- SeismicCWave (metallstaket, multipath): SpeedyBee och RapidFire fungerade bra; inbyggd Skyzone SteadyView i 04O Pro/04X Pro gav rullning/tearing — "The Skyzone Steadyview simply did not work." Version/mix-läge ej angivet.
- SpeedyBee fick köras via AV-ingång med separat matning (Y-kabel) i Skyzone → modulen kan användas utanför original-bay.
- RapidFire: senaste officiella firmware 1.3.2 från 2020 enligt en användare.

## Tillägg 2 (2026-09-30): material från projektägaren (inklistrat/skärmdumpar) + livscykelkontroll

**Reddit r/electronics al2sj1** (vidareutveckling av rrk1:s kod av u/alessandroau, full tråd inklistrad av projektägaren):
- Bilinjär uppskalning buffrar 2 rader. Författaren skrev först "1.5ms ish"; en annan användare rättade till ca 0,15 ms och författaren höll med.
- HDMI-klockan justeras så att 60 Hz-fältfrekvensen från videon ligger i fas med HDMI-bilden (samma princip som rrk1:s flywheel/DPLL).
- Flögs på en MultiGP-tävling; "I don't detect any latency" — subjektivt, ingen mätning.
- PAL-skalning i y-led var ofullständig: 576/720 ger ingen heltalskvot (NTSC 240→720 = ×3).
- En ESP32 med OLED styrde RX5808:ans kanal ("easier in arduino than on the FPGA").
- Kommentar (GearBent): radbuffrande skalare kan ge icke-standard HDMI-timing och kompatibilitetsproblem med vissa skärmar. Stämmer med rrk1:s Topsky-problem och marqs85:s varning.
- Källkoden släpptes inte enligt tråden (fråga om sources obesvarad).

**EDAboard "Video decoder selection guide" (2018):** trådstartaren påstår att MAX9526, TVP5150 och ADV7181 är "Not recommended for new design" och nämner TW9912 och ADV7182A som nyare alternativ. Kontroll mot TI:s produktsidor 2026-09-30:
- TVP5150 (ursprunglig): **NRND** ("not recommended for new designs").
- **TVP5150AM1: ACTIVE.** TVP5151: ACTIVE. → Påståendet gäller den gamla TVP5150, inte AM1.
- ADI:s statussidor gick inte att läsa med skript (JS); ADV7180/ADV7182A-status ej verifierad.

**LCSC ADV7182A** (webbläsare 2026-09-30, "Other Suppliers"): ADV7182AWBCPZ-RL (C662245) 6 707 st, 5,61 USD vid 10+, 3–5 dagar; övriga varianter 29–53 dagar.

**Konsekvens för rev A:** välj uttryckligen **TVP5150AM1** (eller TVP5151), aldrig ursprungliga TVP5150. ADV7182A är ett rimligt ADI-alternativ med nyare status än ADV7180; ingen FPV-förebild hittad för den.

## Designprioritet ändrad 2026-09-30: inte racing, latens sekundär

projektägaren bygger inte för racing. Arbetsmål ca ≤ 50 ms glas-till-glas. Motivering (ej krav): uppmätt analog Skyzone-kedja 23 ± 6 ms och Walksnail via HDMI 71/83 ms (intofpv, 240 fps-kamera); VITURE-användaren flög med ca 60 ms utan att beskriva det som ett hinder. 50 ms ligger mellan och lämnar plats för en bildbuffert. Justeras efter egen provflygning.

Konsekvenser (bedömning):
- **En bildbuffert är tillåten** (+1 bild ≈ 17–20 ms). Det ger fri utgångsklocka med standardtiming (inga låstider på ~20 s, ingen HDMI-blankning vid bortfall; visa senaste bild eller brus), riktig deinterlacing, godtycklig skalning (PAL fungerar) och enklare OSD. Kompatibilitetsproblemen med radbuffrande skalare försvinner i stort sett.
- **Minne behövs.** En FPGA med minne i kapseln slipper extern DDR-routning på eget kort. Kandidat att verifiera: Gowin GW2AR-18 (Tang Nano 20K) som uppges ha inbyggt SDRAM och HDMI-kontakt på devkortet. En PAL-bild 720×576 YUV 4:2:2 är ca 0,8 MB.
- **Mixningen bör fortfarande göras rad för rad före bufferten**, eftersom två mottagare av samma VTX redan är synkrona.
- **Spår 2 (billig AV→HDMI-box + XR-glasögon) blir betydligt mer intressant.** 30–50 ms per box (orverifierat) kan vara acceptabelt. Måste mätas, och utgången måste vara 1080p60 för VITURE-liknande glasögon.
- **Raspberry Pi + ADV7282-M (~130 ms rapporterat)** ligger fortfarande över arbetsmålet.

## Tillägg 3 (2026-09-30): ADI EngineerZone-trådar inklistrade av projektägaren + ADI-status

**Livscykel (ADI:s egna sidor/sidhuvuden):** ADV7180, ADV7280, ADV7282 och ADV7182A är alla **Not Recommended for New Designs**. TI TVP5150AM1 och TVP5151 är ACTIVE (se Tillägg 2). → **Dekoderval för rev A: TVP5150AM1 (alt. TVP5151). Inga ADI-dekodrar.**

**[ADV7282M output delay/latency](https://ez.analog.com/video/f/q-a/573972/adv7282m-output-delay-latency) (2023):**
- ADI: själva dekodern fördröjer "20–100 Pixel clocks" beroende på aktiverade funktioner. Frågeställaren bekräftade att ~130 ms på Pi 4 "is greatly caused by gstreamer and pi, not the chip itself" (Pi-kameran IMX477 gav 70–100 ms i samma kedja). → Dekodern är inte flaskhalsen; det är SBC-/mjukvarukedjan.
- ADI: flera dekodrar låser på insignalen vid olika tidpunkter; att synkronisera analog video beskrivs som mycket svårt. (Gäller oberoende kameror. För oss är källan en och samma VTX, men varje dekoder låser och fasar ändå individuellt → mixern behöver radräknare/FIFO-justering per kanal.)
- Dekodern kan inte ändra timing (720 aktiva pixlar), och ADV7282-M ger bara YCrCb, inte RGB.

**[ADV7282-M Raspberry Pi Vertical Jitter](https://ez.analog.com/video/f/q-a/553218/adv7282-m-raspberry-pi-vertical-jitter) (2021–22):**
- ADV728x:s inbyggda I2P är radfördubbling ("line doubling"); gav vertikalt jitter där text blev nästan oläslig. ADI:s råd: stäng av I2P och gör deinterlacing i efterföljande processor genom att lagra fält i minne — "This will add significant latency". → Med vår nya latensprioritet är fältbaserad deinterlacing med bildbuffert rätt val; ren bob ger hoppande OSD-text.
- ADI: dekodern kan ge fält som är för långa/korta; en "line counter algorithm" behövs så att bufferten inte svämmar över. Samma problem som rrk1 såg med TVP5150AM1.
- ADI om stabilitet: PLL-matningen (PVDD 1,8 V) är mycket viktig — ferritpärla-isolerad från andra matningar, kontrollera brus även runt linjefrekvensen, C0G/NP0-kondensatorer i PLL-filtret, följ datablads power-up-sekvens för reset/powerdown. Rådet gäller ADI-kretsen men är relevant layoutpraxis även för TVP5150AM1:s PLL-matning.
- 2D-kamfilter ger Y/C-artefakter; 3D-kam kräver extern SDRAM och fler bilders fördröjning. (Inte aktuellt för oss.)

## SBC-spår (2026-09-30): finns det värdiga kort?

Kriterium: inbyggd analog videoingång eller bevisat kort väg till skärm, eftersom USB/CSI-capture + Linux-videokedja gav ~130 ms i tidigare rapport. Råfiler i `research/raw/sbc/`.

**Allwinner T113-S3 — enda kandidaten värd ett experiment.** Enligt datablad v1.9: "2-channel CVBS input and 1-channel CVBS decoder", 3D-kamfilter, 10-bit ADC, detektering av signallås och 625 linjer; dessutom parallellt kamerainterface för BT.656 (upp till 2×1080p30 tidsmultiplexat) och egen displaymotor. Kort: t.ex. MangoPi MQ-Dual.
- Två ingångar men **en** avkodare → kan växla mellan två mottagare, inte avkoda båda samtidigt. Ingen riktig mixning med bara den inbyggda delen.
- **Mjukvarurisk:** i Allwinners forum ([t113 CVBS IN/OUT on Tina and Mainline 6.10](https://bbs.aw-ol.com/topic/5473), 2024) fick en MangoPi Dual-användare inte CVBS in/ut att fungera; analog kamera verkar bara stödjas i leverantörens Tina Linux (kärna 5.4), inte i mainline 6.x. Frågan är obesvarad. Äldre öppen TVD-drivrutin finns bara för A20 (ihuguet/sunxi-tv-decoder, 2018).
- **Ingen latensdata hittad.**

**Uteslutna efter kontroll:**
- Allwinner T507/T507-H: MYIR:s kort listar bara CVBS-*utgång* och MIPI-CSI/DVP-kamera. Sökträffens påstående om fyra CVBS-ingångar kunde inte bekräftas (T5-databladet gav serverfel).
- Rockchip RK3588 HDMI-in (Orange Pi 5 Plus): enda hittade rapporten mätte omkodning till fil (2 s), inte visning — inget belägg åt något håll, och HDMI-in hjälper inte en analog källa utan extra konverterare.
- hobisatelit/fpv-sdr (MIT, 2026): tar emot analog 5,8 GHz FPV med SDR (HackRF, BladeRF, USRP, Pluto) på vanlig dator. Labb-/analysverktyg, inte goggles — men intressant för att studera mixning i mjukvara på riktiga RF-signaler.

**Slutsats:** inget SBC är bevisat för låglatens analog→skärm. T113-S3 är ett billigt sidoexperiment (inbyggd dekoder med 3D-kam, direkt LCD-utgång) med tydlig mjukvarurisk. Huvudspåren förblir mottagare + konverterare/XR respektive eget FPGA-kort.
