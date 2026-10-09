# Arbetsplan efter granskningen 2026-10-05

Underlag: [reviews/2026-10-05/ADVERSARIAL_REVIEW.md](reviews/2026-10-05/ADVERSARIAL_REVIEW.md). Fynden ligger som issues; index i LAP87/OpenVRX#3. Första passet är gjort samma dag. Det här dokumentet säger vad som är gjort, var det avviker från planen, vad som återstår och i vilken ordning.

**Inget är mätt på hårdvara.** "Simulerat" betyder mot modell i testsviten, "byggt" betyder syntes och place-and-route med öppen verktygskedja.

## Läge

| Fas | Innehåll | Issues | Läge |
|---|---|---|---|
| 0 | Issues och plan | hub #3 | klar |
| 1 | Radnumrering från vertikalsläckningen | Core #4 | klar, simulerat |
| 2 | Mixern | Core #1 #2 #3 #5 | klar, simulerat och byggt |
| 3 | Uppstart och stift | Core #6 #8 #9 #12, Puck #1 | klar i Core, simulerat och byggt. Rev A har RESETB på J6-18 (Puck 4a45f6a) |
| 4 | SDRAM | Core #7 | klar, simulerat och byggt. Fas och läspunkt avgörs av minnestestet på kortet |
| 5 | Utgångsvägen | Core #10 #11 #15 #16 | klar, simulerat och byggt |
| 6 | Smått | Core #13 #14, hub #2, Puck #4 | klart utom det som är ägarens beslut. Puck #2 och #3 väntar på nästa schemavarv |
| 7 | Alternativa vägar | hub #1 | tre underlag skrivna; förslagen står under "Nästa steg" |
| 8 | Mätningar när kortet finns | alla | väntar på hårdvara |

Grenar, pushade 2026-10-06: Core `fix/review-2026-10-05` (delspåren `fix/bringup-pins` och `fix/sdram-capture` är sammanslagna dit), navet och Puck `review-2026-10-05`. Codex-grenarna från 2026-10-06 är inarbetade: latensparningen och klocktabellen i `build.sh` (Core 74e0bfa), stiftkontraktet `tools/board_contract.py` (Core f02a98e), överlämningen i navet (6dcca08) och RESETB-flytten i Puck (4a45f6a). Puck-submodulen pekar på Core-grenen (e605ef3).

Issues 2026-10-06: Core #1–#16, Puck #1 och #4 är stängda med en kommentar om vad som gjordes och vad som återstår att mäta. Öppna: navet #1–#3 (ägarens beslut, index), Puck #2–#3 (nästa schemavarv).

Testsviten i Core: 284 test (52 före passet). Byggt ur grenens topp: M1, M2, M2s, M2a, M3, M4, M6; alla klockor klarar sina krav, och HDMI-paren i M4 och M6 packas som i M0. Siffrorna står i Core `gateware/README.md`.

## Utfört

### Fas 1. Radnumrering (Core 92a2025)

Rad 0 är första radstart efter minst två synkord i följd med V = 1. F-biten ingår inte. En källa med fast F (som TVP5150AM1 ger för icke sammanflätat) numreras nu som alla andra. Negativ kontroll: mottagaren före ändringen faller på den nya vektorn `f_stuck_fields`.

### Fas 2. Mixern (Core 57cd08d)

Reglerna står i Core `gateware/README.md` (M4) och i sin helhet i `model/line_mixer_ref.py`: parning på radnummer inom 15,8 µs, ensamma rader bara från aktuell kanal eller som lucktätning i takt, kanalbyte på hälsa (åtta rader) eller tystnad (8 respektive 40 rader), stigande radordning, ingen tidsgräns i klocktid.

- `sim/test_mixer.py`: 14 scenarier på fält med riktig släcklucka, varje beslut och varje ord mot modellen. `model/test_line_mixer_ref.py`: fem egenskaper på 25 slumpade radföljder var.
- Negativa kontroller: ändrad `N_STEP` eller `N_DEAD` fäller motsvarande test, och mixern före ändringen fäller 7 av 12 scenariokontroller (körd en gång för hand).

Avvikelser från planen:
- "Avgör utan att vänta när den andra kanalen är tyst" är inte infört. Varje ensam rad väntar 15,8 µs. Det håller RTL och modell lika oberoende av hur upptagen mixern är.
- Lucktätningen kräver att den andra kanalen inte levererade *någon* rad inom 15,8 µs, vilket avgörs per rad vid ankomsten (inte när raden behandlas).
- `overflow` syns nu i M6:s logg (Core 4964da3): raden slutar med `!` när mixern har tappat en rad.

### Fas 3. Uppstart och stift (Core dc36058, sju commits)

RESETB på stift 18, tre lysdioder, M4 styr RX5808, kanalen skrivs om medan ingen dekoder är låst, `tvp_ctrl` läser tillbaka 03h och startar om en återställd dekoder, SECAM maskas (04h = FCh), statusexempel och BRINGUP rättade, vakttest för utgångar i HDMI-bankerna. Detaljer i commit-meddelandena och `gateware/BRINGUP.md`.

Avvikelser: kanalen skrivs alltid 0,5 s efter start, även om en dekoder redan är låst. Rev 3921 av Tang-kortet är kontrollerad mot schemat (BOOT-bygeln); rev 3850 är det inte.

### Fas 4. SDRAM (Core db5ba3b, sex commits)

Simuleringsmodell med en riktig krets tider (tAC, tOH, protokollkontroller, negativa kontroller per regel), klockfas 225° och tiderna 2/2/6, läspunkt valbar under drift, minnestestet `m2a_memtest`.

Det som kom fram:
- De gamla tiderna 1/1 gav 15,4 ns för tRCD och tRP där databladet kräver 18 ns.
- Läsning i burst är inte provad på hårdvara någonstans uppströms. Läspunkten måste träffa ett fönster på 11,9 ns, och var det ligger beror på kortets fördröjning. Med de antagna fördröjningarna (3 + 3 ns) är läsningen ren; med noll fördröjning är ingen läspunkt ren vid 225°.
- Minnestestet mäter sitt eget bygge: I/O-registren placeras fritt. Delspåret provade nextpnr:s `--vopt ireg_in_iob --vopt oreg_in_iob --vopt ioreg_in_iob`, som lägger registren i I/O-cellerna och gör resultatet oberoende av placeringen. Det är inte infört, eftersom det ändrar alla byggen. Se "Nästa steg".

### Fas 5. Utgångsvägen (Core dba75d9, 9404d7d, 5436a8f)

- **Fältminne med fyra buffertar.** Vilken buffert en bild visar bestäms i SDRAM-domänen. Skrivaren får aldrig bufferten som visas, dess reserv eller den nyss publicerade (V-3).
- **Lagrade rader.** En bit per rad och buffert. En rad som saknas ersätts av raden ovanför (högst två i följd), sedan av förra fältets rad. Visningen kan inte få en halvskriven rad.
- **Följsam buffring.** En bild visar fältet som skrivs när skrivaren ligger 4 rader före (44 för PAL in i 60 Hz). Översta raden blir 0,3–17 ms gammal i stället för 17–33 ms (NTSC, räknat ur radtiderna; simulerat i nedskalad bild).
- **Ett radantal.** Skalan följer det mindre av de två senaste fältens radantal när de skiljer högst 2. Ett avklippt fält sträcks inte ut.
- **Fältfas ur ankomsttid.** `field_phase.v` avgör vilket fält som är det nedre på att fälten kommer omväxlande en radtid längre och kortare isär. Det nedre fältet ritas en halv källrad lägre.
- **LOW.** Bildstarten för det tidiga fältet fördröjs med halva skillnaden, så att utbilderna blir lika långa (annars växlar de med tre rader, vilket underlaget om utgången visade). En enstaka tidig trigger kortar inte längre bilden; tre i följd ger en kort bild och sedan ingen på 32 bilder. Formellt bevisat: undre och övre gräns för bildlängden, avstånd mellan korta bilder.

Avvikelser från planen:
- Fältförskjutningens riktning är ingen parameter. Den följer av ankomsttiden: fältet som kommer sent ligger lägre. Det behöver bekräftas på hårdvara men inte ställas in.
- Buffertvalet flyttades till SDRAM-domänen i stället för att undanta tre buffertar på skrivarsidan. Fyra buffertar behövs ändå, för reservfältet.

### Fas 6. Smått

- `snowlog.py` går på Windows och hoppar över skadade rader (Core 38d93ed). COM-portsvägen är inte provad mot en riktig port.
- Core-README: läget efter passet, sökvägar, M5C-raden, formuleringen om XR-glasögon, vad latenssiffrorna räknar från (Core 6bcdfc7, #14).
- AGENTS.md: uppstartsordning, mixerns och fältminnets fakta, dekoderns init-lista, stiftregeln (hub #2, de delar som inte är ägarens beslut).
- EMI-tabellen i puckkonceptet: övertonerna i mellanfrekvensbandet och två mätsteg (Puck a9d6976, 152c236).
- M6-bygget (Core 567ca8d): efter sammanslagningarna byggde M6 inte med seed 0, se "Kända svagheter".

### Fas 7. Underlag (navet e2ead95)

`research/DEKODER_OCH_SYNK_ROBUSTHET_2026-10-05.md`, `research/UTGANG_OCH_LATENS_2026-10-05.md`, `research/RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md`. Varje påstående har sitt slag av belägg angivet.

## Kända svagheter efter passet

- **M6-bygget är seed-beroende.** Med seed 0 och 1 kan nextpnr inte lägga kortets klocka på det globala klocknätet; med 2 och 3 går det. Orsaken är inte utredd. `boards/m6_puck_proto.seed` håller seed 2. En ändring i M6 kan kräva ett annat.
- **27 MHz-domänen i M6** har ett eget krav på 54 MHz. Efter routning (Core e5585ba) når den 98,5 MHz; placeringsuppskattningen sade 64–69. Den kritiska vägen är menyns frekvensräkning i `puck_ui.v`. **M2a** har minst marginal av alla: 83 MHz mot kravet 75.
- **Testsviten tar längre tid:** 16 minuter i följd (5 minuter förut, med 52 test). Simuleringarna är oberoende av varandra; med tio åt gången tar sviten 5 minuter.
- **Mixerns gränsfall.** Rader som kommer inom några klockcykler från parningsfönstrets kant kan avgöras olika i RTL och modell, när modellen får tider i ns. Sedan 2026-10-08 räknar `line_mixer_ref.arrival_cycle` den cykel då `mix_chan` tar raden, och på de tiderna är modellen exakt också vid kanten (`test_mixer.py::test_pairing_window_edge`).
- **Klockdomänsövergångarna i `fb_backend.v`** är bevisade sedan 2026-10-07, utom det som står i Core `gateware/formal/README.md` (metastabilitet, SDRAM-latens för radbufferten, lågfördröjningsringen).
- **27 MHz-domänen i M6** nådde 65 MHz mot kravet 54 i bygget av Core f13581c (99 i 62a69be). Samma kritiska väg, menyns kanaltabell till RX5808:s skiftregister; skillnaden är placering. Marginalen mot de verkliga 27 MHz krymper.

## Andra passet, 2026-10-06

Codex fortsatte på `main` enligt projektägarens instruktion. [Granskningen 2026-10-06](reviews/2026-10-06/README.md) innehåller nya verifieringar, felreproduktioner och nästa avgränsade pass. Den skiljer dagens kontroller från de tidigare resultaten nedan.

- **Byggartefakter och testsökvägar** (Core `e6bf0a9`, `6a61a17`): frysta byggindata, hashmanifest, felaktiga/gamla bitströmmar avvisas och variantnamn följer alla artefakter. 25 verktygskontroller, 5 probe/top-tester och två riktiga byggen gröna. Core har 308 insamlade tester; ingen ny sammanhängande 308-körning påstås.
- **Tre öppna funktionsfel**: kort aktiv BT.656-rad godkänns med gammal svans, 88h-NACK döljs av senare ACK, och borttagen första bildrad kan ge okända bildord med aktiv video. Reproducerade i Fables bas, ännu inte rättade. Den dokumenterade LOW-payloadbuggen reproduceras också i formal-grenen.
- **Puck/Core synkade**: gitlänken uppdaterad till Core `6a61a17`; kontraktstest och ny isolerad 114-delars export gröna, ERC 0/0. Industrivarianten TVP5150AM1IPBSR är Active enligt TI:s exakta artikelnummer 2026-10-06; småvolymstillgång är fortfarande okontrollerad.
- **Nattgrenarna** är separata. Ny riktad verifiering: brus 9 gröna, flerbytes-I²C 12 gröna, formellt test grönt. Deras hela sviter och sammanslagen funktion är inte omkörda av Codex.

- **Lägesbyte `BUF`/`LOW` under drift är simulerat** (Core a6d23fd, test skrivet av en Sonnet-agent). Bildlängder, X/Z och SDRAM-protokoll är rena över båda bytena. Testet hittade ett fel: första bilden efter `LOW` → `BUF` visade ett sju fält gammalt fält. Två orsaker, båda rättade (Core 62a69be): `fb_display.v` behöll "har ett publicerat fält" från före `LOW`, och `fb_sdram.v` publicerade det halva fält skrivaren gick med i, vars saknade rader lästes rått ur bufferten. Nu släpps det fältet utan publicering (gäller även vid start) och publicerade fält glöms medan `LOW` är aktivt. Modell, händelselogg och M2-testet följer. Negativa kontroller: utan vardera delen faller testet.
- **I/O-register i I/O-cellerna** (Core-gren `exp/ioreg-in-iob`, Sonnet-agent): `IOREG=1` i `build.sh`, alla nio toppar byggda med och utan. Inga timingfel, LUT4 oförändrat, DFF 1–2 % färre, HDMI-paren packas som M0. I M2a hamnar alla 32 DQ-ingångsregister i I/O-cellerna, men DQ-utdata, utgångsaktiveringen, DQM och SDRAM-klockan ligger kvar i logiken; orsaken är inte utredd (gissning: ett register driver alla 32 stift). Rekommendation: inför för M2a, övriga SDRAM-toppar efter att minnestestet har körts på kortet med och utan. Ägarens beslut.
- **Rev A** (Puck 828976c–bdb99d1, 17cdbea): PTC 0,75 A hållström (#2 stängt), I-klassad dekoder (livscykeln inte kontrollerad), 4,7 µF efter PLL_AVDD-ferriterna, probjord vid 27 MHz-headrarna, 47/27 ohm beskrivet. Kvar i #3: ESD-klamp efter delaren, firmware-patch (kräver flerbyteskrivning i `i2c_master.v`).
- **README-tabellen** i Core hade siffror från placeringen; alla nio toppar är ombyggda ur 62a69be och tabellen visar siffror efter routning (Core e5585ba). Alla klockor klarar sina krav, HDMI-paren i M4 och M6 som M0, verktygstesten 16 gröna. Hela sviten: 284 gröna.
- Issues uppdaterade, se "Läge".
- **Brusmått** (Core `feat/noise-metric`, a6640b0): `noise_stats.v` räknar lumasampel utanför 16–235 per rad och kanal på orden ur kanalernas FIFO, summerat över 1 024 rader; mixern läser det inte. M6-loggen har brus A och B efter snövärdena (57 byte), `snowlog.py` två nya kolumner och läser gamla rader. Simulerat mot `luma_outside()` i modellen på nya vektorn `ntsc_spikes`, varje rad och fönster; intervallet 15–236 och räkning av krominans fäller testet. Sviten 290 gröna; M6 byggd (12 274 LUT, 27 MHz-domänen 90 MHz mot 54). Kvar: om måttet skiljer brus från bildinnehåll på riktig signal.
- **Flerbyteskrivning I2C** (Core `feat/i2c-multibyte`, 013300a): `i2c_master.v` skriver upp till 256 databyte efter registeradressen (`wextra`, `wreq`) och stoppar direkt efter en NACK; en byte fungerar som förut, init-listan är orörd. Simulerat mot `model/i2c_ref.py` (1, 2, 8 och 256 byte, NACK mitt i och på första byten, frånvarande adress, återläsning); en slav utan autoinkrement och en master som inte avbryter fäller testet. Sviten 288 gröna. Kvar: patchdata och laddsteg (Core `gateware/README.md` under M4 säger vad som krävs), prov mot en riktig TVP5150AM1.
- **Klockdomänsövergångarna i `fb_backend.v`** (Core `formal/fb-backend-cdc`, 53e5ab2): synkroniserarna ligger nu i `cdc_sync.v`, simulerat oförändrat. Formellt bevisat för 27–108 MHz mot 74,25 MHz: toggle-handskakningarna tappar eller dubblerar inga händelser och levererar rätt data, `ll_mode` är rätt i båda domänerna från tredje flanken efter ett byte (inte andra: ett första sampel kan bli det gamla värdet), och en radbegäran under en aktiv rad går aldrig till platsen som läses. Sex negativa kontroller, bland dem synkroniseraren borttagen. Sviten 284 gröna. Inte bevisat, med skäl i Core `gateware/formal/README.md`: att två steg räcker mot metastabilitet, SDRAM-latensen för radbufferten, lågfördröjningsringen. Öppet fel: `s_ll_lines` kan ändras en SDRAM-klocka efter triggern när ett fält slutar direkt efter rad 1. Följden är fel radantal i en bild. En rättning är föreslagen men inte införd.

## Tredje passet, 2026-10-07

Opus tog in nattgrenarna och rättade det som [granskningen 2026-10-06](reviews/2026-10-06/README.md) lämnade öppet, ett paket i taget på Core `main`, med hela sviten och byggen efter sista paketet. Core `main` 8b5f0ae: 332 test gröna, M0, M2, M2s, M3, M4 och M6 byggda utan fel med alla klockor inom krav och HDMI-paren som M0. Puck `main` 4c64aae pekar dit; Puck-testet grönt.

- **Nattgrenarna** (brus, flerbytes-I2C, CDC-bevis) är sammanslagna i Core `main` (1672097); README-konflikterna gällde bara testantalet. Sviten 318 gröna vid sammanslagningen.
- **Lågfördröjningstriggerns radantal** (Core 186f98d): `toggle_tx` i `cdc_sync.v` håller radantalet från vändning till vändning och vänder högst var 16:e klocka. Codex fall (tre rader skickade, två mottagna) ger nu tre, `sim/test_ll_payload.py`; en kopia med det ohållna värdet tar emot två igen. Sändarsidan är formellt bevisad mot villkoren i toggle-beviset.
- **I2C som fastnar** (Core 57f8763): `i2c_master.v` ger upp när SCL hålls låg längre än 10 ms, släpper linjerna och avslutar med NACK och `stuck`. Simulerat med kort och fastlåst SCL; en kopia utan tidsgräns hänger.
- **F1, ofullständig rad** (Core 2a69d69): `mix_chan.v` lagrar bara rader vars 360 ord kom i följd. En sådan rad räknas som dålig och som inte levererad, så den andra kanalens rad fyller luckan. RTL och modell lika i ett nytt mixerscenario; en kopia som lagrar raden avviker från modellen.
- **F3, saknad första rad** (Core 9be0d33): utan rad ovanför och utan reservfält skriver fältminnet en svart rad i radbufferten i stället för att läsa oskrivet minne. `test_fb` kräver nu oberoende av modellen att varje läst rad är lagrad, i alla 16 fältminnestest. Den gamla regeln ger okända ord i en bild med video igen.
- **F2, statuspoll** (Core f13581c): en pollrunda gäller bara hel. Ett NACK på 88h, 89h eller 03h gör statusen ogiltig till nästa hela runda, och en återställd dekoder också. Proben visar `st ----` i fönstret där en dekoder återställdes (`BRINGUP.md`). En kopia som lämnar statusen giltig fångas.
- Codex reproduktioner i `reviews/2026-10-06/repro/` gäller basen e5585ba och är inte körda mot Core `main`. Varje fall finns nu som regressionstest i Core med en negativ kontroll som återställer felet.

## Fjärde passet, 2026-10-08

Opus enligt [NATTPASS_2026-10-07.md](NATTPASS_2026-10-07.md), tre grenar ur Core `main`, var och en sammanslagen med `--no-ff` efter hela sviten. Core `main` a71b94f: 368 test gröna. Inget är kört på hårdvara.

- **27 MHz-domänen i M6** (`feat/puck-ui-timing`, sammanslagen i Core 1d5c1c6): kanaltabellens uppslag och MHz-siffrorna (nu en tabell per kanal i stället för division) är register i `puck_ui.v`. Simulerat med oförändrat facit; negativa kontroller med fel syntesord och fel frekvens i en tabellrad. Byggt med seed 0–3: alla fyra routar, 27 MHz-domänen 109, 116, 127 och 115 MHz mot 54. Varför seed 0 och 1 inte routade förut är inte utrett. Kvar: ta bort SDC-raden med 54 MHz-kravet om det önskas.
- **Rader som är dåliga i båda kanalerna** (`feat/mixer-double-bad`, sammanslagen i 8839b0f): mixern skriver inte en sådan rad om raden före i fältet var frisk; i en följd lämnas bara den första ute. Modell, egenskapstest (25 slumpade följder), fyra mixerscenarier och ett fältminnestest; negativa kontroller: RTL som skriver raden ändå, och RTL som lämnar ute varje sådan rad. M4 byggt. Fynd: en utelämnad sista rad gör fältet en rad kortare för fältminnet, så bilden skalas från en rad färre under två fält (vid NTSC 242 i stället för 243). Det går inte att undvika i mixern utan att röra `fb_sdram.v`.
- **Dekoderinställningar** (`feat/decoder-settings`, sammanslagen i a71b94f): init-listan skriver 28h = 00h och 02h = 20h (VCR-läge) före 03h. Videostandarden är kvar på autoswitch, eftersom pucken tar både NTSC- och PAL-kameror och underlaget inte tar upp blandad användning. M6-loggen har en flagga per dekoder för 88h bit 4 (`L`, `-` eller `?`); `snowlog.py` läser den och de äldre raderna. Simulerat mot slavmodellen; negativa kontroller med fel registervärde, fel ordning och fel bit. M6 byggt (27 MHz-domänen 123 MHz). Kvar: vilket fast TV/VCR-läge som håller låset bäst, och om flaggan säger något på riktig signal. Briefen hänvisar till underlagets avsnitt 6, men underlaget har inget sådant; registerlistan står i avsnitt 2.

Långkörningen enligt [NATTPASS_2026-10-07_LANG.md](NATTPASS_2026-10-07_LANG.md) (Opus): störningskampanj genom hela bildkedjan, `bt656_rx` till pixlarna, i simulering. Core `main` 059aadd (koden som i 0e0bf49): 397 test gröna, två av dem xfail (#17, #18). Logg: Core `gateware/sim/FUZZ_2026-10-07.md`.

- **Körda frön:** 1 772 i första körning, 45 av dem i full geometri (243/288 rader in i 720p, fältminnets egna trösklar), resten nedskalade (24/29 rader, 87-radersbild); 194 omkörningar efter rättningarna och med den slutliga kontrollen. 28 störningsklasser, var och en i minst 177 frön. Generator `model/fuzz_stream.py`, kedjetest `sim/test_fuzz_chain.py` (varje block mot sin modell på den indata det fick, sex invarianter), kampanj `sim/fuzz_campaign.py`. Tio frön och fem negativa kontroller ingår i sviten.
- **Fynd per grupp** (första avvikelsen; siffrorna i listan nedan): rx/record 8 frön (rättning 1), store/decision 1 (2), sdram/protocol 1 (3), rx/noise 1 (4), age 2 (5 och #18), display/switch_video 14 (#17). Övriga avvikelser var kontrollens egna fel, rättade i testet och listade i loggen.
- **Rättat**, var och en på en egen `fix/`-gren med riktat test och negativ kontroll, hela sviten och M4 (M6 för brusmätaren), sammanslagen med `--no-ff`:
  1. `bt656_rx.v`: en rad vars EAV tappats löper vidare, och indexet slog runt vid 2 048 byte; mättas nu vid 2 047 (Core a50129d).
  2. `field_phase.v`: tiden från återställning räknades som ett fältintervall, så en progressiv källa kunde ritas en halv rad lägre (dc058dc).
  3. `fb_sdram.v`: hål i en 8-ordsgrupp fylldes från ett oskrivet register, X till SDRAM efter `LOW` → `BUF` mitt i en rad; nu svart (a8c4bac).
  4. `noise_stats.v`: en rad som börjar om utan ett helt ord fick brusräkningen från raden före (2e0926c).
  5. `line_mixer.v` och modellen: ett par avgjordes bara på den aktuella kanalens fälträknare; när en mottagare kom tillbaka efter ett tyst fält medan den andra saknade lås frös utgången (7cc4eda).
- **Issues, inte rättade** (regeländringar, ägarens beslut): Core #17, `LOW` visar video innan utgången har låst efter `BUF` → `LOW`, och README:s påstående om första bilden gäller inte; Core #18, ett utfält som börjar över den senast skickade raden med samma F-bit syns inte för fältminnet, som slår ihop det med fältet före.
- **Mixerns gränsfall** (se "Kända svagheter"): modellen är exakt på de cykler då `mix_chan` tar varje rad (`line_mixer_ref.arrival_cycle`), också vid parningsfönstrets kant; `test_mixer.py::test_pairing_window_edge` med negativ kontroll, och 177 frön med B vid kanten utan avvikelse.
- **Iakttagelser** (inte fel mot README, i loggen): en genlock-kapning före vsync-raderna ger skärmen en lång bild; första `LOW`-bilden efter ett byte skalas från 240 rader (vid PAL saknas de nedersta 48 i den bilden); efter `LOW` → `BUF` har fältminnet kvar gamla lagrad-bitar till första ordet. Rättelse: jag skrev att de bilderna saknar video; Codex visade att första `BUF`-bilden kan ha video (OVN-F1, `docs/overnight/2026-10-07/LOW_BUF_FINDING.md`), och min kontrolländring Core 3ad2c2b, som gjorde läsfelet till en notering, släppte igenom det. Kampanjloggen har rättelsen.

## Femte passet, 2026-10-08 (Fable, dagtid)

- **Nattens arbete granskat:** Opus fyra grenar och långkörningen, Codex nattkoordinering, Mistrals dokumentutkast. Hela sviten på Core `main` 8b5f0ae: 432 gröna, 2 xfail.
- **TV-läge** (Core 8ac74bc): 02h = 30h (bit 5:4 = 11 är TV enligt SLES209E; Opus hade 20h = VCR). Ägaren vill prova båda på bänken innan valet låses, kanske som menyinställning; noterat i README och AGENTS.md.
- **M6 utan eget SDC-krav** (samma commit): 27 MHz-domänen får 75 MHz som alla andra; byggt, 121 MHz.
- **Core #17 och Codex OVN-F1 rättade** (Core e873f4b): en `LOW`-bild har video bara om den startades av en trigger från det här `LOW`-passet (`genlock_timing.v` rapporterar `triggered`), fältet ringskrivaren gick med i triggar inte, triggerräknaren nollställs utanför `LOW`, och ett lägesbyte släcker resten av bilden. Efter första triggerstartade bilden hålls videon så länge triggers kommer (en flyttad källa river i tre bilder i stället för att bli svart). Tre negativa kontroller för hand. Fältminne 16, störningskedja 22, övrigt 249 gröna.
- **#18 rättat** (Core e113cf6, ägarens val): mixerns F-bit växlar vid varje utfält; återgång är en rad i RTL och en i modellen om bilden på kortet säger det. Samma commit gör #17-fixens lägesbytestest helt (det hade inte körts), återgår till den strikta LOW-regeln, och noterar att en avklippt bild saknar egen vsync-puls (hopp till synkraderna provades och förkastades). Hela sviten 433 gröna, ingen xfail kvar.
- **TV/VCR som menyinställning** är nästa steg om bänken visar skillnad: kräver att tvp_ctrl kan skriva om 02h på begäran.
- Kvar: SDRAM-fas och allt annat som kräver kortet.

## Återstår ur granskningen

- **Rev A-kortet** (Puck #2–#3): PTC, temperaturklass, PLL-filter, ESD-klamp efter delaren, jordstift, 47/27 ohm på ingången. RESETB-flytten är gjord (Puck #1). SKiDL finns i Core-miljön i WSL; Puck-testet går där.
- **Ägarens beslut**, se sist.

## Nästa steg

Ordnade efter nytta mot insats. De tre första går att göra utan hårdvara.

1. **I/O-register i I/O-cellerna.** Experimentet är gjort (se "Andra passet"); kvar är beslutet, och att ta reda på varför DQ-utgångarna inte hamnar i cellerna.
2. **Ett bildläge i stället för två.** Fältminnet visar redan fältet som skrivs. Med genlockad tidsbas och bildstart några rader efter fältstart ger samma väg ungefär `LOW`:s latens (uppskattat 0,2 ms överst, 0,9 ms nederst), med täckning av saknade rader och utan ringbuffertens 16-radersgräns. Då försvinner en specialväg, och omlåsning kan ske utan skräp i bilden eftersom fältminnet faller tillbaka på senaste hela fält. Nackdel: `LOW` blir beroende av SDRAM. Ägarens val.
3. **Svänghjulstidbas** (dekoderunderlaget, avsnitt 5). Rader placeras efter ankomsttid mot en egen rad- och fälträknare. Fältfasen ur ankomsttid och genlockens fönster är första stegen dit. Fortsättningen behöver mätvärden först: hur mycket dekoderns radtider skakar vid svag signal, och vad den gör när den tappar H-låset.
4. **Dekoderinställningar.** Lås videostandarden (28h) och TV/VCR-läget (02h) lika på båda. Använd den klibbiga biten "lost lock" (88h bit 4) som underlag för mixern först när den har loggats på riktig signal; i simulering går det inte att veta om den hjälper eller stjälper.
5. **Kvalitetsmått som inte beror på bilden.** Brusmåttet (lumasampel utanför 16–235) räknas och loggas i M6 sedan 2026-10-07. Kvar: logga det på riktig signal. Om klick syns där kan måttet ta över från HF-energin, och blandningen kan viktas efter brus (RF-underlaget, avsnitt 2 och 3).
6. **Döljning av rader som är dåliga i båda kanalerna.** Fältminnet kan redan ersätta en rad. Mixern behöver bara låta bli att skriva enstaka sådana rader. Längre följder ska fortfarande visas: brus är bättre än stillbild.
7. **Interpolation i höjdled med två rader**, och i sidled vid 720p (utgångsunderlaget, avsnitt 4).
8. **1080p för XR-glasögon.** Direkt TMDS ur GW5A-25 är inom databladet men inte visat med öppen verktygskedja; ADV7513 och TFP410 är reserver (utgångsunderlaget, avsnitt 3).
9. **RF.** Antennhöjd, egenstörning i mellanfrekvensbandet, linjär 5 V per mottagare (RF-underlaget). Mekanik och kort, inte gateware.

## Mätningar när kortet finns

I den här ordningen. Varje rad är något simuleringen inte kan ersätta.

| Steg | Mätning | Avgör |
|---|---|---|
| M0 | Bild på tre skärmar | HDMI-nivåer |
| M3 | Proben med båda dekodrarna | Kablage; `fld` med den egna kameran (sammanflätad eller inte); om 03h läses tillbaka som 0Dh (annars startas dekodern om vid varje pollning och `ri` går till FF) |
| M3 | Dra ur videon till en dekoder | Om TVP5150 fortsätter leverera rader utan signal och med vilken timing; hur ofta 88h bit 4 sätts |
| M2a | Minnestestet, fas 180°, 225°, 270° | SDRAM-fas och läspunkt. Resultatet gäller andra byggen bara om läspunkt 5 är ren en fas åt vardera hållet |
| M2 | Bild från en dekoder, `BUF` | Fältminnet på riktig SDRAM; rader som ersätts syns i bilden |
| M4 | Antenn av, en mottagare i taget | Mixerns byte och tid till byte; `!` i loggen ska inte komma |
| M4 | Skriv om samma kanal med bild på | Om omskrivning av RX5808 stör bilden |
| M4 | Stillbild med vågräta kanter, sammanflätad kamera | Att det nedre fältet hamnar lägre (kanterna ska stå still, inte hoppa) |
| M6 | `BUF` mot HDMI-skärm | Att följsam buffring inte ger rivning; upplevd latens mot `RT_EN = 0` |
| M6 | `LOW` mot skärm, goggles, brygga | Om mottagaren tar 750/751 rader, och vad den gör vid omlåsning (en kort bild) |
| M6 | Snö-loggen med dekoderkort och HDMI av/på, vid svag signal | Egenstörning, även i mellanfrekvensbandet |

## Beslut som är ägarens

- Granskningens basgrenar används på `main` enligt projektägarens instruktion 2026-10-06, och nattgrenarna är sammanslagna där 2026-10-07 på ägarens begäran. I/O-experimentet (`exp/ioreg-in-iob`) är fortsatt separat och bygger på en äldre bas.
- Ett bildläge i stället för två (punkt 2 ovan).
- I/O-register i I/O-cellerna: för M2a nu, övriga efter mätning (gren `exp/ioreg-in-iob`).
- Inköpsregeln i AGENTS.md mot priser och butikslänkar i Puck och i äldre anteckningar i `research/` (hub #2).
- Licensstycket i `docs/GATEWARE_PLAN.md`, och upphovsnotisen i `sdram_burst.v` (hub #2).
- Rev A: övriga schemaändringar (Puck #2–#3).

## Sjätte passet, 2026-10-09

| Uppgift | Gjort och simulerat | Byggt | Återstår / Git |
|---|---|---|---|
| C1: klipp med full vsync och upphämtning | 447 pass på fryst `3aed0b7`, inga xfails/skips; 7 formella bevis och 14 negativa kontroller. Separat källkvitto verifierar 172 indata; rå XML-inventeringsavvikelse bevarad. | M4 seed 0 och M6 seed 3, alla fem klockor minst 75 MHz; manifest och HDMI-fuses verifierade. M6 seed 2 misslyckades i klockroutning. | Integrerat/pushat Core `main` `629806f`, Puck `main` `e655d14` med 1 grönt Puck-test. Ingen hårdvara provad. |
| C3: ny störningskampanj och OVN-F1 | `8d7b0e9` på `fix/c3-scaled-fallback-readstart`, pushad. 43 riktade checker-tester gröna. Seed 126 på `39c7dc9` gav rå PASS med 216 rader, men fullsviten upptäckte en lucka: fel ringplats kunde godtas som svart. Rättad bindning avvisar den verkliga RTL-felvarianten; identiskt seed 126 passerar med 216 rader, utan fynd/known/edge/notes. Historisk pixelprobe: 72 blanka prov med stängd grind. | Inga C3-byggen startade. M4 seed 0 och M6 seed 3 efter fullsviten. | `39c7dc9`: 323 passed, 1 failed, senare filer ej startade. RTL-negativ och seed 126 godkända; fryst 490-testsvit kör före byggen och merge. Därefter kampanj med 260 frön. |
| C2: TV/VCR-meny | Privat controllerkontrakt och UI/logg-testpaket; separat T/V-token ger 62-byte logg. | — | Implementation, modell/negativa kontroller, fullsvit och M6 seed 2 vid 75 MHz återstår. |

Detaljer: [kvällspassets status](overnight/2026-10-08/STATUS.md).
