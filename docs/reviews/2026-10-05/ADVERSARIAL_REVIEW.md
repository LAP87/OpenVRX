# OpenVRX: adversarial review, 2026-10-05

Granskat: `OpenVRX` 4fd0f11, `OpenVRX-Core` dec88d6, `OpenVRX-Puck` bdee8e4 (Core som submodul på samma commit).

## Slutsats

Byggstenarna håller. Er testsvit går igenom på en ren klon (52 av 52), M0, M4 och M6 bygger med uppfylld timing, och jag hittade inga fel i BT.656-mottagaren, FIFO:n, TMDS-kodaren, färgomvandlingen, 720p-tidsbasen, RX5808-ramen, kanaltabellen eller rev A-schemats stiftning. Inget av fynden kan skada hårdvara.

Det som inte håller är radmixern utanför det enda läge som testas: två låsta dekodrar i takt, med fält på 10 rader. På riktiga fält är RTL:en inte bitexakt mot modellen. När en mottagare tappar signalen, alltså fallet diversity finns till för, visar mixern i simuleringen snö från den döda mottagaren i ungefär halva bilden och kastar den friska mottagarens rader (M-2). Rättar man bara tidsgränsen som orsakar det fastnar mixern i stället helt på en olåst kanal (M-3). Med en icke-sammanflätad kamera startar radnumreringen aldrig om (M-5).

Tre saker till bör lösas före första kortet: M4 och M6 packar HDMI-klockparet annorlunda än M0 eftersom RESETB ligger på stift 25 (P-1, samma fälla som ert CVBS2HDMI-underlag varnar för), SDRAM-läsningen är inte den hårdvaruprovade konfigurationen (R-1), och M4 ställer aldrig in mottagarna (U-1).

Två av mina egna misstankar höll inte när jag simulerade dem. De står under "Det som höll" och V-3.

## Vad jag gjorde

| | |
|---|---|
| Läst | All RTL, alla testbänkar och modeller, cst-filerna, rev A-skriptet med utdata och alla dokument i de tre repona |
| Kört orört | Testsviten: 52 av 52 gröna på 5 min 6 s (WSL Ubuntu 24.04, Icarus Verilog 12.0, paketen i `requirements.txt`). `build.sh` för M0, M4 och M6: alla klockor klarar kravet 75 MHz efter routning. M4 7 034 LUT4 och M6 10 330 LUT4 (README: 7 026 och 10 341) |
| Egna simuleringar | E1–E7 nedan, mot oförändrad RTL. Skript och rådata ligger i `repro/` |
| Datablad och scheman | Tre separata genomgångar av underagenter: rev A-schemat mot TI SLES209E, Tang Nano 20K mot Sipeeds scheman och Gowins datablad, RX5808/SSD1306/I2C mot RTC6715- och SSD1306-databladen och UM10204. Det jag själv har kontrollerat i källan är märkt "egen kontroll" |
| Inte gjort | Ingen hårdvara. Rev A-skriptet är inte kört (kräver SKiDL och KiCad-bibliotek) |

Belägg: **[S]** simulerat mot oförändrad RTL, **[K]** läst ur koden, **[D]** datablad eller schema, **[H]** hypotes som måste mätas på hårdvara.

## Fynd i korthet

| # | Fynd | Allvar | Belägg |
|---|---|---|---|
| M-1 | `alive`-tidsgränsen (1,01 ms) är kortare än släckningen mellan fält (1,27 ms NTSC). `cur` nollställs varje fält, RTL ≠ modell | Hög (rotorsak) | S |
| M-2 | En mottagare utan signal: 51 % av den friskas rader kastas, snö visas i stället | Hög | S |
| M-3 | Oparade rader frågar aldrig efter `bad`: med M-1 rättad fastnar mixern på en olåst kanal | Hög | S |
| M-4 | En kanal 2–7 rader efter tar över bilden oavsett `cur` och `bad`; rader i fel ordning ger falska fältgränser | Hög | S |
| M-5 | Radnumren startar om på F-biten. TVP5150AM1 tvingar F = 1 för icke-sammanflätad video | Hög med sådan källa | S, D |
| M-6 | Mixertestet kör 10 + 2 rader per fält och modellen saknar `alive`; `overflow` visas ingenstans | Medel | K |
| M-7 | Måttets gränser: platt bild vinner, rivning syns inte | Medel | H |
| P-1 | RESETB på stift 25: TMDS-klockparet får andra IOB-fuses i M4/M6 än i M0. Stiftet sitter också på HDMI-CEC | Medel–hög | S, D, H |
| R-1 | SDRAM: 180° och 8-ordsburstar är inte den provade konfigurationen (225°, enstaka ord). Modellen ger data en klocka för sent | Medel | D, K |
| U-1 | M4 ställer aldrig in RX5808 och driver deras SEL/DATA från statuslysdioderna | Medel | K, D |
| V-1 | Låglatens: en ensam kanals två sista rader per fält kommer 1,33 ms för sent | Låg–medel | S |
| V-2 | Genlock saknar undre gräns för bildlängden. XR-glasögonen tar enligt ert eget underlag inte 720p | Medel | K, H |
| V-3 | Trippelbufferten håller för 59,94 och 50 Hz in, men inte för en källa som är snabbare än utgången | Låg | S |
| P-2 | Rev 3921: stift 75 (SCL) är BL616:s BOOT-strapp. Pull-up på SCL stoppar kortets USB-del | Hög på 3921 | D |
| P-3 | S1/S2 är FPGA:ns MODE0/MODE1. Intryckt knapp vid start hindrar laddning från flash | Låg | D |
| U-2 | RX5808-kanalen skrivs en gång, 0,3 µs efter konfigurering, utan omskrivning | Låg–medel | K |
| U-3 | `tvp_ctrl` initierar aldrig om en dekoder; `dev_err` är klibbig | Låg–medel | K |
| U-4 | Statusbit 5 är 50 Hz, inte 60 Hz. Exemplet `st 402E` i BRINGUP är PAL med svag signal | Låg | D |
| B-1 | Rev A: PTC 0,5 A för 0,45 A last löser ut i varm låda | Medel | D |
| D-1…7 | Dokument: regeln "No sourcing" bryts, licensstycket, EMI-tabellen saknar mellanfrekvensen m.m. | Låg | K, H |

---

## 1. Radmixern

### M-1. `alive` faller i varje vertikalsläckning [S]

Var: `Core: gateware/rtl/mix_chan.v:14,76-78`, `mixer2.v:7`, `line_mixer.v:105-106`.

`TIMEOUT` är 65 536 cykler, vid 64,8 MHz 1,011 ms. Mellan sista radmarkören i ett fält och första i nästa går 20 radtider i NTSC (1,271 ms; BT.656 har 19 släckrader, `model/bt656.py:27`) och 25–26 i PAL (1,60–1,66 ms). Båda kanalerna räknas alltså som döda i slutet av varje släckning. Den kanal vars första rad kommer först blir `cur`.

Följder:
- Hysteresen "även mellan fält" (`Hub: docs/GATEWARE_PLAN.md:118`) finns inte. Vilken kanal varje fält börjar på avgörs av några mikrosekunders skillnad i ankomst.
- RTL:en är inte bitexakt mot `model/line_mixer_ref.py` (`Hub: AGENTS.md:36`). Modellen antar enligt sin docstring att båda kanaler lever (`line_mixer_ref.py:9`).

Belägg:
- **E1.** Fält om 24 + 20 rader. I fält 2–4 har B 20 % mer HF-energi än A på varje rad, alltså inom hysteresbandet. Modellen stannar på B, RTL:en använder A. 71 av 119 beslut skiljer. Händelseloggen visar `alive_a`/`alive_b` → 0 och `cur`-byten vid varje fältgräns.
- **Ert eget `sim/test_mixer.py` med en konstant ändrad** (`VBI` 2 → 20): `test_dead_channel_switches` fallerar med "0 lines dropped". De två andra går igenom, eftersom slumpsnön i scenariot aldrig hamnar i hysteresbandet vid en fältstart.

Varför testerna inte såg det: `sim/test_mixer.py:27` kör `LINES, VBI, FIELDS = 10, 2, 5`. Två släckrader är 0,13 ms.

### M-2. En mottagare utan signal förstör bilden från den friska [S]

Scenario: A frisk, låst och ren. B utan signal: dekodern frigår en halv fältperiod ur takt och levererar snö, och `ext_bad_b` är satt hela tiden (statusregistret säger olåst). Fält om 242 + 20 rader, standard-`TIMEOUT`.

Antagande [H]: en TVP5150 utan användbar insignal fortsätter leverera rader med egen timing. Databladet säger det inte uttryckligen. Underagenten hittade det i en TI-forumtråd, och er konstruktion utgår från det: det är därför låsbitarna förs in som `ext_bad`. Tystnar dekodern i stället helt tar `alive`-vägen över, och M-2 och M-3 gäller då bara svag signal.

| Körning | Rader visade från den friska | Snörader visade från den döda | Friska rader kastade | `cur`-byten | Fältstarter som `fb_sdram` ser |
|---|---:|---:|---:|---:|---:|
| E2: B död | 458 | 432 | 484 (51 %) | 8 | 8 på 3,9 fält |
| E3: A död | 468 | 422 | 472 (50 %) | 8 | 8 på 3,9 fält |
| E2b/E3b: samma, `TIMEOUT` 262 144 | 942 / 940 | 0 | 0 | 0 | 4 |

Mekanism: under den friska kanalens släckning är den "död" och den andra "levande", så `cur` går till den döda (`line_mixer.v:105-106`). Därefter visas dess rader via de oparade grenarna, som inte tittar på `bad` (M-3), fram till dess egen släckning. Andelen beror på fasläget; en frigående dekoder driver igenom alla lägen.

Det här är grundfallet för diversity och klarkriteriet för M4 ("byte mellan mottagarna när en antenn tas bort", `Core: gateware/BRINGUP.md:61`).

### M-3. Oparade rader frågar aldrig efter `bad` [S]

Var: `line_mixer.v:108-113`. Grenarna för rader utan partner väljer efter `cur` och radavstånd. `bada`/`badb` (synkfel, fel radlängd, olåst dekoder, tvingat läge från menyn) används bara i `S_DEC`, alltså bara när fält och radnummer är lika i båda kanalerna.

**E3c.** `TIMEOUT` höjd till 4 ms, så att M-1 är ur vägen. A är olåst och aktuell (levererar rader först, som efter start), B är frisk men en halv fältperiod bort. Resultat: 831 snörader visas, 0 rader från B, 811 friska rader kastas och `cur` ändras aldrig. Mixern kommer ur läget först om kanalerna råkar hamna i takt eller A slutar leverera rader helt.

Av samma skäl tvingar MODE A/B i menyn (`puck_ui.v:127`) ingenting när kanalerna inte paras.

Rättar man bara M-1 byter man alltså M-2 mot M-3.

### M-4. En kanal 2–7 rader efter tar över, oavsett `cur` och `bad` [S]

Var: `line_mixer.v:109-110`. Den äldre raden visas om den hör till `cur` eller om avståndet är under `NEAR` (8), med tanken att den andra kanalen hoppade över raden. Men ligger B stadigt några rader efter A har A redan visat raden.

**E4.** A frisk och aktuell, B olåst med snö, `TIMEOUT` 4 ms. Samma resultat med standardvärdet (E4d).

| B efter A | Rader från B som visas | Fältstarter som `fb_sdram` ser (verkliga: 2,9) |
|---|---|---:|
| 2 rader | 166 av 172. Varje rad skickas två gånger, B:s version sist | 3 |
| 5 rader | 166 av 172 | 160 |
| 12 rader | 21: de sju sista raderna i varje fält | 6 |

Vid 5 raders eftersläpning kommer raderna dessutom i fel ordning. `fb_sdram.v:83` och låglatensskrivaren (`fb_backend.v:125`) tolkar ett radnummer som går bakåt som nytt fält. I BUF publiceras då 160 "fält" på 2,9. I LOW blir vart och ett en genlock-trigger (V-2).

En frigående dekoder passerar de här lägena under sin drift. Om en låst TVP5150 kan bli liggande några rader fel i sitt V-lås vet jag inte [H].

### M-5. Radnumreringen startar om på F-biten, inte på släckningen [S, D]

Var: `bt656_rx.v:154,175-176`. Rad 0 är första radstart efter att F har ändrats.

TVP5150AM1 med standardvärdet 15h = 01h tvingar F till 1 för signaler med "nonstandard even" radantal (SLES209E avsnitt 3.21.20, egen kontroll). Det gäller icke-sammanflätad video (240p/288p), som en del kameror, OSD-kretsar utan kamera och testbildskällor ger. Det är min tolkning av tabellen: två lika fält ger alltid ett jämnt radantal per bildpar. `tvp_ctrl.v` skriver inte 15h.

**E5, E5b.** F fast på 1, två rena och låsta kanaler, 12 fält.
- Radnumren går 0…1023 och slår runt. Noll omstarter på 12 fält. `fb_sdram` och låglatenstriggern ser 1 fältstart.
- Slogs dekoder B:s utgång på 30 rader efter A:s, så att dess första rad är rad 10 i fältet (`tvp_ctrl` initierar dekodrarna i tur och ordning), paras 0 av 2 386 beslut och B används aldrig. Startar de på samma rad paras allt, men det är tur.

M3-proben visar fallet som `fld 000`. Felsökningstabellen i `BRINGUP.md` tar inte upp det.

Åtgärd: numrera från V-bitens övergång från släckning till aktiv bild, och skriv 15h bit 4 = 1 så att F växlar även för sådana källor.

### M-6. Vad testerna och modellen inte täcker [K]

- Mixertestet kör fält på 10 + 2 rader. Mottagaren testas däremot mot hela 525- och 625-radersbilder (`vectors/`), så verktygen finns.
- `line_mixer_ref.py` har ingen `alive` och `ext_bad` är konstant under hela körningen. Inget test har två levande kanaler ur takt.
- Två invarianter saknas som test: (1) ingen rad från en kanal med `bad`/`ext_bad` visas medan den andra kanalen levererar bra rader, (2) radnumren i utströmmen är strikt stigande inom ett fält. Båda går att slumptesta över fasläge och geometri. E2–E4 är motexempel till dem.
- `overflow` från `mixer2` går inte till lysdiod, OSD eller logg (`top/m4_dual_mix.v:55,67`, `top/m6_puck_proto.v:92,104`). En rad som börjar när ringen är full och slutar när den har fått plats sparas dessutom med gammal vänsterdel (`mix_chan.v:41,61`).

### M-7. Måttets gränser (REVIEW punkt 1) [H]

- HF-jämförelsen betyder bara något när båda raderna har samma innehåll. Ur takt jämförs himmel mot gräs.
- En platt rad har HF-energi 0 och vinner alltid. En mottagare eller dekoder som ger svart eller blå bild utan signal skulle väljas. RX5808 ger snö, men C5VRX-spårets beteende utan signal är okänt.
- Rivning och rullning ändrar inte HF-energin. Där hänger allt på TVP:ns låsbitar, som pollas var 20:e ms (`tvp_ctrl.v:22`) och alltså kan vara drygt ett fält gamla.
- Två dekodrar med var sin H-PLL ger sidledes jitter mot varandra. Medelvärdet av två förskjutna rader är ett lågpassfilter.

---

## 2. Bildbuffert, låglatens och utgång

### V-1. Låglatens: en ensam kanals sista rader kommer för sent [S]

Var: `line_mixer.v:112-113`. En kanal utan partner löses först när den har tre rader i kö. Fältets två sista rader blir därför liggande tills nästa fält har börjat. I E3c-loggen lämnar rad 240 mixern 1 333 µs efter rad 239.

I BUF spelar det ingen roll. I LOW har utgången passerat raderna (den läser dem högst 0,8 ms efter ankomst), så bildens nederkant visar gammalt innehåll så fort bara en mottagare levererar: en dekoder saknas, är död eller ur takt.

### V-2. Genlock och skärmar (REVIEW punkt 6) [K, H]

- Beviset i `formal/` begränsar bildlängden uppåt. Nedåt finns ingen gräns: varje `trig` medan `vc < V_ACTIVE + V_FP` kortar bilden (`genlock_timing.v:48-51,59-60`). De falska fältgränserna i M-4 och M-5 blir därmed synkbortfall på HDMI. En låst generator bör bara acceptera `trig` i ett fönster kring väntad bildstart.
- Enligt ert eget underlag tar XR-glasögonen inte 720p (`Hub: research/XR_GLASOGON_KOMPATIBILITET.md:7`, `Puck: design/REV_A_KONCEPT.md:25`) och bör inte få 50 Hz (rad 8). Allt Core matar ut i dag är 720p, och LOW ger 720p50 för PAL. `Core: gateware/README.md:201` motiverar ändå OSD:n i M6 med XR-glasögonen.
- XR-glasögonen sitter bakom en HDMI→DisplayPort-omvandlare. DisplayPort skickar totala radantalet som ett attribut per bild. Hur omvandlare och glasögon tar att det växlar mellan 750 och 751 är okänt; CVBS2HDMI:s erfarenhet gäller HDMI-skärmar. Prova det tidigt, före mer arbete på LOW.
- Utgången är DVI utan InfoFrame och med fullskalig RGB (`ycbcr2rgb.v`). En TV som antar begränsat omfång för 720p ger för hög kontrast. Kosmetiskt.

### V-3. Trippelbufferten [S]

Skrivaren väljer nästa buffert efter vad den tror visas (`fb_sdram.v:103`), och skärmsidan väljer buffert vid bildstart (`fb_display.v:76`). Beskedet mellan dem tar några klockcykler. Jag lade en publicering på nio lägen kring en bildstart och kontrollerade invarianten "bufferten som skrivs är inte den som visas".

| Körning | Fältperiod mot bildperiod | Resultat |
|---|---|---|
| E7 | längre (som 59,94 eller 50 Hz in mot 60 ut) | Höll i alla lägen, −172 till +136 ns |
| E7b | 0,04 % kortare (källan snabbare än utgången) | Bröts när publiceringen låg 10,6 ns före eller 20,2 ns efter bildstarten: skrivaren skrev i den visade bufferten under en hel bild (65 976 pixelklockor). Höll vid ±51 ns och längre bort |

Med en långsammare ingång hinner varje publicerad buffert visas innan nästa publiceras, och då spelar fördröjningen ingen roll. "Ingen rivning" gäller alltså för NTSC och PAL mot 60 Hz. Det gäller inte en kamera som ligger på 60,00 Hz och råkar gå några ppm fortare än kortets kristall: då passeras fönstret (cirka 70 ns) med jämna mellanrum och en bild blandar två fält. Enklaste rättningen är att låta SDRAM-sidan välja visad buffert när begäran om rad 0 kommer, så att båda valen görs i samma klockdomän.

---

## 3. SDRAM (REVIEW punkt 4)

### R-1. Inte den hårdvaruprovade konfigurationen [D, K]

`rtl/sdram_burst.v:4-8` och `README.md:113` säger att init, timing och läspunkt är nand2marios, provade på hårdvara vid 64,8 MHz. Egen kontroll mot källorna:

| | OpenVRX | nand2mario `sdram-tang-nano-20k` | NESTang (64,8 MHz) |
|---|---|---|---|
| Klockfrekvens i exemplet | 64,8 MHz | 27 MHz (`gowin_rpll.v`: FBDIV 1, IDIV 1) | 64,8 MHz |
| SDRAM-klockans fas | 180° (`clocks_sdram.v:19`, PSDA_SEL 1000) | 225° (PSDA_SEL 1010) | 225° (PSDA_SEL 1010) |
| Burstlängd | 8 | 1 | 1 |
| T_RCD / T_RP / T_RC | 1 / 1 / 4 | 1 / 1 / 4 | 2 / 2 / 6 |

Det som skiljer i sak:
- Med enstaka ord släpper minnet bussen efter ordet, och bussen håller värdet. Läspunkten har då marginal bakåt. I en burst ersätts ordet av nästa strax efter nästa SDRAM-klockflank. 180° i stället för 225° tar bort ytterligare 1,9 ns av den marginalen.
- `sim/sdram_model.v:47-50,79` lägger ut ord 0 efter flank n + 2, alltså en hel klocka senare än en riktig CL = 2-krets, som har data giltiga vid flank n + 2. Modellen har inga fördröjningar. Den passar `RD_SAMPLE = 4` med en halv period åt båda håll och säger därför inget om läspunkten.
- I/O-fördröjningarna är obegränsade: ingen SDC, inga IOB-register. Underagentens uppskattning är 3–8 ns, olika per DQ-bit och per placering. Symptomet blir då bitvis och ändras mellan byggen.

README pekar redan ut `RD_SAMPLE` som ratt. Fasen är den andra ratten, och troligen den viktigare.

Åtgärd: börja på 225° som NESTang. Bygg en minnestestare som eget steg före M2: skriv mönster, läs tillbaka, räkna fel per DQ-bit, skriv ut över UART, och svep fas och `RD_SAMPLE`. Det tar bort gissandet ur "bilden är förskjuten 2 pixlar".

---

## 4. Tang Nano 20K: stift och bankar (REVIEW punkt 7 och 8)

### P-1. RESETB på stift 25 [S, D, H]

Tre oberoende problem med samma stift:

**Bank 5 delas med TMDS-klockparet (33/34).** Apicula 0.32 sätter `BANK_VCCIO` för alla IOB i en bank efter bankens första vanliga utgång, och 1,2 om det inte finns någon (`apycula/gowin_pack.py:3907-3927,3962`, egen kontroll). M0–M2 har bara ingångar i bank 5. M4 och M6 har RESETB där som LVCMOS33-utgång.

Mätt i era egna bitströmmar (`repro/review_tmds_fuses.py`, samma metod som `tools/test_lvds_bank_inputs.py`): klockparet har 18 IOB-fuses satta i M0 och 16 i M4 och M6. Fuse (24,5) och (27,48) i ruta (54,23) saknas. De tre dataparen, som ligger i bank 4, är identiska i alla tre. Ett minimalt par av testkonstruktioner ger samma skillnad med en utgång på stift 25 och ingen skillnad med samma utgång på stift 72 (`repro/review_lvds_bank.py`).

Er egen anteckning (`Hub: research/CVBS2HDMI_2026-10-04.md:84`) säger om LVDS25: "sätt aldrig `DRIVE=` eller `BANK_VCCIO=` (länken byggs men ingen skärm låser)". Cst-filerna sätter det inte, men packaren gör det åt er via RESETB. `tools/test_lvds_bank_inputs.py` ser det inte: testet har bara ingångar i bank 5. Om en skärm låser eller inte är [H]. Det säkra påståendet är att en fungerande M0 inte bevisar HDMI-utgången i M4/M6.

**Stiftet sitter på HDMI-CEC.** Sipeeds 3921-schema, DISPLAY-bladet (egen kontroll): PIN25 → R51 100 Ω → CEC, med R40 27 kΩ pull-up. FPGA:n driver alltså en buss med öppen kollektor hårt hög.

**Rev A:s pull-down håller inte RESETB låg före konfigurering.** 10 kΩ (`Puck: design/rev_a/dekoderkort.py:178`) mot 27 kΩ till ca 3,0 V ger 0,8 V, och mer med FPGA:ns svaga pull-up. TVP:ns V_IL är högst 0,99 V (underagent, SLES209E 4.2). Påståendet "hålls i reset tills FPGA:n släpper" (`Puck: design/rev_a/README.md:19`) stämmer därför inte säkert.

Åtgärd: flytta RESETB till ett stift i en annan bank, till exempel ett lysdiodsstift i bank 6. Det löser alla tre.

### P-2. Rev 3921: SCL ligger på BL616:s BOOT-strapp [D]

Underagentens läsning av Sipeeds 3921-schema: stift 75 går till BL616 GPIO 2 (BOOT) med 10 kΩ till jord. Med pull-up 2,2–4,7 kΩ på SCL (`BRINGUP.md:35`) ligger BOOT högt vid start, BL616 går i ISP-läge, och kortet har varken USB-JTAG eller USB-UART. Egen kontroll: stift 75 heter PIN75_HSPI_DIR på FPGA-bladet. Nätet till BL616 har jag inte följt själv.

`BRINGUP.md:7` säger att BL616 "kan driva samma stift" och att M3-proben avslöjar det. På 3921 kommer proben aldrig i gång. Skriv i stället att stiftplanen inte fungerar på 3921.

På 3923 är stift 75 BL616:s SPI-MISO och 76 dess MOSI. Enligt underagentens läsning av Sipeeds wiki är BL616 slav i länkläget `spi`. Då är det 75 (SCL) som BL616 driver, inte 76, och tabellen i `BRINGUP.md` avsnitt 5 har risken omvänd. Jag har inte kontrollerat det själv.

### P-3. S1 och S2 är MODE0 och MODE1 [D]

Egen kontroll i 3921-schemat: PIN88_MODE0_KEY1 och PIN87_MODE1_KEY2 med 1 kΩ till jord. En knapp som hålls in när FPGA:n konfigureras ändrar konfigureringsläget, och bitströmmen laddas inte från flash. M6 gör båda till menyknappar (`top/m6_puck_proto.v:18-19`). Saknas i `BRINGUP.md` avsnitt 5.

### P-4. Pull-testet [D]

Underagent: `PULL=UP` (`build.sh:22-25`) lägger också pull-up på YOUT7, som är adresstrappen I2CSEL. Mot 10 kΩ på modulen kan nivån bli 1,5 V vid reset, dekodern hamnar på BAh, och proben visar `i2c NA` med alla bitar "följer pull". Stift 26, 79 och 49 har dessutom motstånd på kortet som gör att en odriven bit inte följer pull-testet. Undanta `d[7]` i `sed`-raden.

---

## 5. Uppstartsflödet M3 → M4 → M6

### U-1. M4 ställer aldrig in mottagarna [K, D]

`BRINGUP.md:61` låter M4 köra med samma koppling som M3. Men `top/m4_dual_mix.v` har ingen SPI. En RTC6715 startar på 5865 MHz (A1), enligt underagentens läsning av databladet, så M4 visar bild på F4 bara om M3 har körts sedan mottagarna fick ström.

Dessutom är `led[4]` och `led[5]` i M4 `~have_video` och `~locked_ok` (`top/m4_dual_mix.v:89`). De ligger på stift 19 och 20, som enligt kopplingen är RX5808 DATA och SEL. SEL hålls alltså låg medan båda dekodrarna är låsta, SPI-klockan (stift 71) är odriven, och varje tappat lås ger en stigande SEL-flank, där RTC6715 tar in det som står i skiftregistret.

Åtgärd: lägg F4-skrivningen från M3 i M4 och ta stift 19/20 ur lysdiodsvektorn.

### U-2. Kanalen skrivs en gång [K]

`puck_ui.v:120-122` och `top/m3_probe.v:73-77` skriver kanalen direkt efter reset, cirka 0,3 µs efter konfigurering, och aldrig igen utan knapptryck. Får mottagarna ström efter FPGA:n, eller tappar de den, står de på A1 medan OLED:n visar F4 5800. `BRINGUP.md:108` pekar då på videokabeln. Skriv om kanalen periodiskt, till exempel en gång per sekund.

Lysdiod 4 lyser dessutom hela tiden i M6, eftersom SPI-DATA vilar låg på ett aktivt lågt lysdiodsstift (`rx5808_spi.v:31,46`). `BRINGUP.md:49` säger att den blinkar kort.

### U-3. Dekodrarna initieras aldrig om [K]

`tvp_ctrl.v:84-91`: efter init pollas bara status. En dekoder som återställs (spänningsdipp, störning på RESETB, se P-1) står kvar med utgångarna avstängda tills FPGA:n laddas om. I M6 är S1 inte längre reset. `dev_err` är klibbig (`tvp_ctrl.v:85`): en enda NACK visar dekodern som `----` för gott. `i2c_master.v:107` läser en SDA som är kortsluten låg som ACK.

Åtgärd: läs tillbaka 03h vid pollningen och kör init igen om värdet är fel.

Underagentens läsning av SLES209E: 04h och 28h lämnas på standardvärden, så autoswitchen kan välja SECAM. I brus kan de två dekodrarna då välja olika standard. Lås standarden eller maskera bort de oanvända.

### U-4. Statusregistret är feltolkat i text [D]

Egen kontroll, SLES209E "Status Register #1": bit 5 är fältfrekvens, 0 = 60 Hz och 1 = 50 Hz. `tvp_ctrl.v:10` säger "bit5 60 Hz". Exemplet för frisk NTSC i `BRINGUP.md:80`, `st 402E`, betyder 50 Hz och svag signal (89h bit 6). Frisk NTSC är ungefär `000E`. Samma fel finns i `sim/i2c_slave_model.v:25`. RTL:en använder bara bit 1 och 2, så funktionen påverkas inte, men den som följer BRINGUP letar fel på ett friskt kort.

---

## 6. Rev A-kortet (underagentens genomgång mot datablad)

Inga blockerande fel: alla 32 TVP-stift, matningarna, kristallkretsen, ingångsnätet, strapparna och stiftlisternas mappning mot `m4_dual_mix.cst` stämmer med SLES209E och Sipeeds scheman. Netlista, BOM och kopplingslista stämmer med skriptet.

| # | Fynd | Var |
|---|---|---|
| B-1 | PTC "0,5 A" för 0,45 A last. En 1206-PTC med 0,5 A hållström håller 0,44 A vid 40 °C och 0,35 A vid 60 °C (Bourns MF-NSMF050). BOM:en säger inte om 0,5 A är håll- eller utlösningsström. Välj minst 0,75 A hållström | `dekoderkort.py:262` |
| B-2 | RESETB: se P-1 | `dekoderkort.py:178` |
| B-3 | TVP5150AM1PBSR är 0–70 °C. Vinterflygning ligger utanför. I-varianten (TVP5150AM1IPBSR) är −40–85 °C | `dekoderkort.py:85` |
| B-4 | PLL_AVDD har ferrit och bara 0,1 µF efter den: odämpad LC. Lägg till 4,7–10 µF eller byt ferriten mot 2,2–4,7 Ω | `dekoderkort.py:227-239` |
| B-5 | ESD-dioden klämmer vid 12,5–15 V, AIP tål 2,0 V. Delaren hjälper, men ett andra steg efter den saknas | `dekoderkort.py:268-274` |
| B-6 | TI rekommenderar att ladda sin firmware-patch i TVP5150AM1. `i2c_master` kan bara skriva en byte per transaktion. Effekten i praktiken är okänd | `rtl/i2c_master.v:39-44` |
| B-7 | En jordstift per stiftlist för nio 27 MHz-signaler | — |

---

## 7. Dokument och påståenden

- **D-1.** `Hub: AGENTS.md:85` säger "No sourcing (shops, prices, purchase links) in these repositories". `Puck: design/PUCK_2027_KONCEPT.md` (priser, butikslänkar, Amazon), `Puck: design/REV_A_KONCEPT.md:67` (LCSC-priser och lager) och `Hub: research/` (priser, Blocket) bryter mot den.
- **D-2.** `Hub: docs/GATEWARE_PLAN.md:131` säger att licensen inte spelar någon roll och att ni får bygga på GPL-3.0-kod. Repona är CERN-OHL-S-2.0. Inget filhuvud anger pthalin eller rrk1 som källa, men jag har inte jämfört mot deras kod. Stycket bör bort eller ersättas med ett besked. `rtl/sdram_burst.v` bygger på Apache-2.0-kod (nand2mario, Seyviour): behåll deras upphovsrätts- och licensnotis.
- **D-3.** `Hub: AGENTS.md:98` anger uppstartsordningen M0 → M2 → M4 → M6. Rad 47 och `BRINGUP.md` säger M0 → M3 → M4 → M6.
- **D-4.** `Core: gateware/README.md` hänvisar till filer som inte finns i något av repona (`../bom/GATEWARE_DEVKIT.md`, `../research/LT8618SX_INIT.md`), och statustabellen redovisar ett bygge av `m5c_moneagle_1080p` som inte går att göra om från repot.
- **D-5.** EMI-tabellen i `Puck: design/PUCK_2027_KONCEPT.md:140-152` räknar bara övertoner i 5725–5875 MHz. RTC6715 blandar ned till 479 MHz (`model/vtx_channels.py:7`). 18 × 27 MHz = 486 MHz och 34 × 14,318 MHz = 486,8 MHz ligger 7–8 MHz från mellanfrekvensens mitt, på alla kanaler, och är mycket lägre övertoner än den 215:e. [H]: MF-filtrets bredd på RX5808 har jag inte kontrollerat. Lägg till "dekoderkortet av/på" i mätplanen, inte bara "HDMI av/på". TMDS-data är dessutom bredbandigt mellan bithastighetens multiplar, inte bara spikar.
- **D-6.** `tools/snowlog.py:21` importerar `termios` och går därför inte att köra på Windows.
- **D-7.** Latensen 0,1–0,8 ms i README:erna gäller från att raden är klar i FPGA:n. TVP5150:s egen fördröjning (kamfiltret arbetar över rader) och skärmen tillkommer.

---

## 8. Det som höll

- `bt656_rx.v` mot `model/bt656.py` på hela bilder, med felrättning av synkord.
- `async_fifo.v`: Cummings-struktur, Gray-pekare direkt från register. De formella bevisen går igenom här, med negativa kontroller.
- `tmds_encoder.v` rad för rad mot DVI 1.0. `ycbcr2rgb.v`: koefficienter, offset och bitbredder. 720p60 enligt CEA-861.
- `i2c_master.v`: öppen kollektor, START/STOP, klocksträckning. `uart_tx.v`: 115 384 baud, +0,16 %.
- RX5808: ramen (25 bitar, LSB först, adress 1), alla 48 synthord omräknade ur databladets formel, banden A/B/E/F/R mot Betaflight och ExpressLRS.
- SSD1306: adress, init och fönster. Bussdelningen mellan OLED och `tvp_ctrl` kan inte krocka.
- PLL:erna ligger inom DS226:s gränser. Alla 55 SDRAM-pads, alla stiftlistepositioner och klockstiften 77/80 stämmer.
- Trippelbufferten för 59,94 och 50 Hz in (V-3).
- Låglatenslägets radantal. Det tas från ett tidigare fält (`fb_backend.v:132`, `fb_display.v:78`), och BT.656 NTSC har 244 och 243 rader i de två fälten. Jag väntade mig gammalt innehåll i bildens nederkant. **E6** (fält om 12 och 11 rader omväxlande) visade inget sådant: som mest utelämnas sista raden i det längre fältet. Med standardtiming kommer triggern efter att sista raden har börjat, så radantalet tas från fältet två steg bak, som har samma paritet.

Punkterna om RX5808, SSD1306, PLL:er och stift bygger på underagenternas genomgångar mot datablad och scheman. Resten har jag läst eller kört själv.

Om de formella bevisen (REVIEW punkt 5): antagandena stämmer för start från konfigurering. De täcker inte reset under drift. FIFO-pekarna nollställs per domän, men synkroniseringsregistren har ingen reset (`async_fifo.v:44,56`), och `rst` kommer bland annat från PLL-lås (`top/m4_dual_mix.v:35`). En kort resetpuls kan därför lämna läsaren med upp till 2^(AW+1) gamla poster, som läses ut på några mikrosekunder. Det är ett resonemang ur koden, inte simulerat.

## 9. Svar på REVIEW.md punkt för punkt

| REVIEW | Svar |
|---|---|
| 1. Hjälper radmixning? | Går inte att avgöra i simulering. Måttets kända blinda fläckar: M-7 |
| 2. Parning av rader | Här ligger de allvarliga felen: M-1 till M-5 |
| 3. TVP5150-uppstart | Registervärden och resettider stämmer. U-3, U-4 och M-5 (15h) är det som saknas |
| 4. SDRAM | R-1 |
| 5. Klockdomäner | FIFO:n håller. Trippelbufferten: V-3 |
| 6. Låglatens | V-1, V-2 |
| 7. Verktygskedjan | P-1: banken får VCCIO från RESETB |
| 8. Delade stift | P-1 (CEC), P-2, P-3 |
| 9. Egenstörning | D-5 |

## 10. Förslag på ordning

1. Mixern: gör hälsotillstånd per kanal (låst, levererar bra rader) till det som styr `cur`, även utan parning. Visa aldrig en oparad rad från en kanal som inte är aktuell och som är `bad`. Släpp bara ut stigande radnummer inom ett fält. Höj `TIMEOUT` över längsta släckningen. Skriv de två invarianterna i M-6 som slumptest med riktig fältgeometri innan RTL:en ändras, så att de fallerar först.
2. Numrera rader från V-biten och skriv 15h (M-5).
3. Flytta RESETB från stift 25 (P-1).
4. SDRAM: 225° och en minnestestare före M2 (R-1).
5. Uppstart: F4-skrivning i M4, periodisk omskrivning, om-init av dekodrar, rätta `402E` (U-1 till U-4).
6. Prova 750/751-rader mot den skärmkedja som är målet innan mer arbete läggs på LOW (V-2).
