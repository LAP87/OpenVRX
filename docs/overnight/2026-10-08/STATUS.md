# Kvällspass 2026-10-08

Uppdraget är [NATTPASS_2026-10-08.md](../../NATTPASS_2026-10-08.md). Användaren valde uttryckligen uppgiftsgrenar och merge till `main` efter verifiering. C1 → C3 → C2 är ordningen. Codex/root granskar, kör grindarna och integrerar; Luna hjälper med avgränsade filer (nu high, äldre max-körningar är historik). Den befintliga Vibe-sessionen äger M1–M3 och startas eller styrs inte av Codex.

## Aktuellt läge 2026-10-12 efter C2-acceptans

Detta avsnitt är aktuell brief; de daterade körjournalerna längre ned bevarar statusen vid respektive tidpunkt. Användaren har lämnat datorn med ”Datorn är din” och begärt fortsatt arbete inom ordinarie kvot, en uppgift åt gången. Ett tungt jobb åt gången hålls under `/home/lenny/openvrx-review/build.lock`.

- Core main **`a1247ab`** innehåller C2-grenen **`509fc95`**, verifierad från källan **`c3fda21`**. Den frysta sviten gav **604 pass i 39 filer** på **5411,439 s**, 157 oförändrade källhashar, alla 570 tidigare testnoder, 19 cocotb-rapportidentiteter samt 7 formella bevis och 14 verkliga negativa motexempel. Root återvaliderade råresultat och både fryst källa och slutlig main. [Svitacceptans](evidence/C2_SUITE_ACCEPTANCE.json) · [Slutgranskning](evidence/C2_SUITE_ROOT_REVIEW.json).
- Färska M0 seed 0, M4 seed 0 och M6 seed 2-byggen passerar 75 MHz på samtliga rapporterade klockor. M4:s lägsta maxfrekvens är 101,69 MHz, M6:s 104,85 MHz; alla fem M4/M6-domäner kontrollerades. Alla fyra TMDS-par matchar M0 i båda topparna. Root granskade manifest, råtiming och samtliga 24 arkiverade artefakter. [Bygggrind](evidence/C2_BUILD_GATE.json) · [Bygggranskning](evidence/C2_BUILD_ROOT_REVIEW.json).
- Puck main **`f2e7d53`** pekar på Core `a1247ab` efter egen uppgiftsgren och verifierad merge. De två stift-/schemakontrakttesterna passerade på **2,08 s**, med sina negativa kontroller. [Integrationskvitto](evidence/C2_INTEGRATION.json).
- M6:s filterfält begär TV/VCR för båda dekodrarna. Ett pågående I²C-skrivvärde och SDA-linje hålls fast; en äldre kvittens lämnar ett nyare val väntande. NACK ger omförsök efter parad pollning. OLED/OSD och den nya 62-byte-loggen visar begärt menyval, inte en återläsning av 02h. Äldre loggformer behålls. [56 riktade pass/två subtester och nio meningsfulla gamla-vakt-negativer](evidence/C2_FOCUSED_ACCEPTANCE.json) är separat verifierade. Den första riktade körningens 53 pass/3 fail och timestampfel bevaras i [första granskningen](evidence/C2_FOCUSED_FAILURE_REVIEW.json).
- Mixerns väntande output-F-gräns över helt utelämnade fält ligger kvar; dekoderns F-bit är separat. B:s tidigare 570-pass- och byggresultat är historik, med sina ursprungliga kvitton.
- C3:s kampanj slutade vid 200/260 frön: **199 PASS, 1 FAIL**, 60 ej körda. Seed **1345** gav 72 kontrollerade rader mot minst 144; triagen fann bara en komplett kvalificerad aktiv bild före sista källbyten. Längre stimulus kräver nytt käll-/parameterkontrakt och ny evidenskatalog. Råfelet och tröskeln bevaras. Ingen ny kampanj har körts och inget RTL-fel är fastställt.

C2 är accepterat i simulation och byggen. Ingen FPGA-hårdvara eller TV/VCR-bildskillnad är mätt; kamera/VTX → Moneagle vid 4,2 V är en separat bänkobservation. Seed1345-kontrollen är nu slutgranskad: oförändrad baslinje FAIL 72<144, separat prov med fyra tillagda kamerafält PASS 360. Nästa uppgift är ett generellt, prefixbevarande stimuluskontrakt med egna kontroller före någon ny slutkampanj.

## C1 — integrerat 2026-10-09

- Gren `fix/genlock-cut-vsync`, Core `3aed0b7`, pushad. En bild som klipps efter tre tidiga triggers behåller nu hela vsync-pulsen. Bara den direkt följande bilden får kortare släcklucka för upphämtning. Båda behåller hela sista släckraden, där displayens skalning och radindex återställs.
- Modellen och de nya mikrosimuleringarna: 9 gröna på liten och 750-raders vertikal geometri. Gammalt hopp till sista raden fäller pulsregeln; avstängd upphämtning fäller samma tvåbilders fasgräns. Riktade fixturetester fäller för kort upphämtning, en tredje kort bild, för kort `HOLD` och saknad synkpuls.
- Fullsviten på fryst `3aed0b7` är klar: **447 passed**, inga xfail, skips eller processfel, på 1:29:36. Formalgrinden gav 7 bevis och 14 verkliga motexempel för de avsiktliga felvarianterna.
- Råköraren avslutade med `FAIL_SOURCE_CHANGED` (returstatus 1), eftersom 19 genererade cocotb-XML hamnade i dess källinventering. Inga indata ändrades eller togs bort. Ett separat, granskat kvitto verifierar alla 172 filer mot ursprungsarkivet, samtliga pytest-utfall och exakt de insamlade XML-rapporterna. SDRAM-testet som avsiktligt stoppar simulatorn har sin förväntade felrapport; andra XML-fel avvisas. Fem negativa kontroller av kvittogrinden passerade. Råloggar och råstatus är bevarade i `private/notes/evening_2026-10-08/c1`; inget testundantag lades till i RTL eller modell.
- **M4 seed 0 och M6 seed 3 är byggda och manifestverifierade** på fryst `3aed0b7`; alla fem klockor klarar 75 MHz. M0-referensen och samtliga fyra HDMI-par har godkända manifest/fuse-kontroller. M6 seed 2 misslyckades i klockroutningen (`Can't route the clocks.clk_27 net`), innan slutlig timing. Diagnostiken bevaras; standardseed 2, stift, BUFG, IOB och SDC är oförändrade. C2:s krav på seed 2 återstår.
- Båda README är uppdaterade efter granskning. Endast dessa dokument skiljer den accepterade källan från grenens sista commit. `fix/genlock-cut-vsync` är mergad med `--no-ff` och pushad till Core `main` **`629806f`**. Puck-gitlänken är uppdaterad via egen gren och merge till `main` **`e655d14`**; dess aktuella test gav **1 passed** på 1,42 s. Inga schema- eller BOM-filer ändrades.
- Kompakt verifieringsjournal: [C1.json](evidence/C1.json).

## C3 och C2

C3:s privata körplan, adapter och sekventiella körjournal är förberedda; den nya 260-frökampanjen har inte startat. Seed 126 är omspelat med byte-identiskt stimulus på Fables `e113cf6`-RTL med separat strikt checker, och separat på fryst C1 `629806f`. **Båda rapporterar ett SDRAM-läschecksummefel och X/Z på utgången**. Terminalens första grupp är inte hela fyndlistan.

Pixelobservationen av det gamla LOW→BUF-fönstret på `e113cf6` visar däremot 72 blanka prov med stängd videogrind, varav 45 före publicering. Rå probe-FAIL använde det äldre gråvärdet; separat källbundet kvitto jämför med faktiska `202020`. Se [LOW_BUF_FINDING.md](../2026-10-07/LOW_BUF_FINDING.md). Lunas käll- och eventspårning pekar på två avgränsade orsaker: checksummefacit tas vid radval före avslutad skrivburst, och den skalade bilden får reservstorlek 240 när 24 behövs. [Triagen](evidence/seed126-triage.json) bevarar båda underkända råkörningarna. Rättningen är pushad på `fix/c3-scaled-fallback-readstart` som `7e5fe09`: geometriskt reservvärde, faktisk accepterad lässtart och strikta läskontroller. Tolv riktade testfall passerade, inklusive modell och negativa kontroller. Den identiska omspelningen av seed 126 är fortfarande **FAIL**: checksummeavvikelsen är borta, men rad 28 läser oskriven ringplats 9 (`display/ll_empty`) och X/Z finns kvar på utgången (`pc919091`). Grenen är inte integrerad; fullsvit och byggen väntar på det kvarvarande fyndet. Den efterföljande ringrättningen är pushad som **`39c7dc9`** på samma gren: bara aldrig komplett skrivna platser ger svart, med giltighet som behålls över BUF/LOW och nollställs globalt. Oberoende adressmodell, BUF-proveniens, klockpassage och adress/data-koppling verifieras. Root granskade och kompletterade kontrollerna: **46 riktade gröna**, sex verkliga RTL-felvarianter samt kontroller som avvisar saknad skrivlogg och alltid svart. Den identiska seed 126-körningen är nu **PASS** med **216 kontrollerade rader**, inga fynd/known/edge/notes; A/B/styrstimulus är byte-identiskt med förra körningen. Rå RAM-X på ringplats 9 blir det väntade svarta ordet på displayens indata. [Kvitto](evidence/seed126-39c7dc9.json).

Den frysta 486-testsviten på `39c7dc9` avslutades med **323 passed och 1 failed**; senare testfiler startades inte. Felet är `test_chain_checks_catch_faults[ring]`: en avsiktlig skrivning till fel ringplats upptäcktes inte. Det separata rena motexemplet visar varför: modellen godtog den faktiska skrivadressen som facit, så svart från den rätta men oskrivna platsen kunde godtas. Seed 126:s råa PASS är bevarat men räcker inte för acceptans. Inga C3-byggen startade. [Fynd och råstatus](evidence/checker-ring-binding.json).

Checker-rättningen **`8d7b0e9`** är pushad på samma uppgiftsgren. LOW-skrivningens adress, ordindex och data jämförs nu med den oberoende kontrollerade mixerströmmen, även när displayen visar svart. Fyra rena felvarianter avvisas; **43 riktade tester passerade**. Den verkliga felvarianten med fel ringplats avvisas nu med `display/ll_word`. Seed 126 är åter **PASS med 216 kontrollerade rader**, utan fynd/known/edge/notes. Alla sex stimulus- och råloggfiler är byte-identiska med `39c7dc9`. Den privata efterkontrollen fick fel evidenssökväg efter avslutade simuleringar; rå FAIL är bevarat, och ett separat granskat kvitto kontrollerar de faktiska filerna. [Kvitto och råresultat](evidence/seed126-8d7b0e9.json). Den frysta **490-testsviten är accepterad**: 490 godkända, inga andra utfall, på 4 861,264 s (1:21:01,264). Alla 39 filer kördes och samtliga 157 källhashar är oförändrade; formaltestet gav 7 bevis och 14 verkliga negativa motexempel. M4 seed 0 och M6 seed 3 klarade 75 MHz på alla fem klockor. Manifest, M0-referens och fyra HDMI-par är verifierade, loggarna saknar `ERROR`, och 24 byggartefakter är arkiverade. Root granskade råutfall och acceptanskvittot före merge. Endast README ändrades efter den verifierade källan `8d7b0e9`: docscommit `96df311`, `--no-ff`-merge till Core **`edb85d0`**, pushad. Puck-länken är uppdaterad via egen gren och merge till **`5146688`**, pushad; dess kontraktstest gav 1 pass på 2,34 s, med negativa kontroller för reset/stift/saknad validator. [Samlad evidens](evidence/C3_fix.json).

Efter användarens återupptagning 2026-10-09 fungerar avgränsade Luna-paket; det äldre kreditfelet är historiskt och inga credits köptes. Kampanjläsaren följer RAW/X-formatet; root körde 17 rena kontroller, och RAW kan inte ersätta visad X-täckning. Den nya 260-frökampanjen startade **20:16 UTC 2026-10-09** på fryst Core-main `edb85d0`: 250 skalade frön (varav 50 tvingad `b_edge`) och 10 fullgeometriska, 130 vardera vid täthet 1,0 och 2,5. En koordinator håller bygglåset genom sex sekventiella grupper; alla råfiler bevaras och fullgeometri kräver en komplett 720-raders LOW-bild efter lägesbyte. Kampanjen avbröts för spel på utvecklingsdatorn innan något fröresultat blev färdigt. Alla partiella råfiler är bevarade. Efter användarens uttryckliga klartecken återstartades den i en ny evidenskatalog med **identiskt manifest, källa och parametrar**. Den är nu **AVBRUTEN FÖR TESTBÄNKSTRIAGE, inte accepterad**. Root avslutade exakt de egna körprocesserna efter att fynden ringats in; bygglåset är fritt. Den avbrutna omgången är orörd; [källbundet körkontrakt](evidence/C3_campaign.json). C2:s controller- och UI/loggpaket är förberedda privat, men C2-koden har inte påbörjats. En separat T/V-loggtoken kräver 62 byte inklusive CRLF; M3/M4 får inaktiva request-ingångar. C2:s M6 seed 2-krav återstår; C3 seed 3 ersätter det inte. FPGA-kedjan är inte provad på hårdvara. Kameran/VTX:n och Moneagle har däremot gett bild vid 4,2 V från bänkaggregat; [bänkobservation](../../bench/AIO_MONEAGLE_2026-10-09.md).


## Avgränsningar

Dagens inlästa bas var navet `87a5717`, Core `e113cf6` och Puck `08aa8f4` med ren Core-gitlänk. Fable rapporterade 433 gröna; de angivna testsökvägarna samlade 434 innan C1:s 13 nya testfall. Tidigare nattens 432 gröna och två xfail hör till den frysta äldre revisionen `aece6eb`.

Ingen FPGA-hårdvara är verifierad. F-bit-regeln, LOW-videogrinden, släpp av det fält skrivaren gick med i, stift, IOB, SDC, licens och BOM ändras inte här. TV/VCR jämförs genom C2:s meny senare, utan att ett fast filterval tas åt ägaren. Inga krediter eller delar köps. Automationens gamla körning till morgonen 8 oktober är avslutad; detta är det nya passet.

## Första kampanjfynd efter återstarten

De första 20 färdiga fröna gav 14 PASS och 6 FAIL. Frön 1200, 1208 och 1213 slutar med en accepterad SDRAM-läsning utan avslutande läsmarkör; frön 1201, 1216 och 1218 fäller kontrollen av första bilden efter BUF→LOW. Råresultaten är orörda. Root och Luna jämför slutvillkoret i testbänken och den senare kontrollen mot ägarens regel om triggerstartade LOW-bilder. Ingen orsak är fastställd och inga undantag införda. [Frön och källbundet råresultat](evidence/C3_initial_findings.json).

Triagen visar att frön 1200/1208 slutar efter 264/352 av 360 läsord, när testbänkens fasta svans stänger loggen. Den kan därför inte fastställa att läsningen skulle ha slutförts. För frö 1201 saknas direkt loggning av triggerstatus; RTL-regeln tillåter video på en triggerstartad första bild, medan checkern kräver en blank bild oavsett trigger. Root har tilldelat Luna endast `tb_chain.v` och `test_fuzz_chain.py` på `fix/c3-bench-drain-trigger-oracle`: tidsbegränsad avslutning och direkt observerbar triggerregel med negativa kontroller. RTL och ägarbeslut ändras inte. De 23 färdiga råresultaten (17 PASS, 6 FAIL) och alla partiella råfiler bevaras; ingen ny simulering har startats.

## Kreditstopp i Luna

Luna avslutade återstartsgranskningen och triagen, men implementeringspaketet avbröts med `Your workspace is out of credits`. En ofärdig ändring i `tb_chain.v` finns endast på arbetsgrenen `fix/c3-bench-drain-trigger-oracle`; checkern är ännu inte uppdaterad och inga nya native-simuleringar eller byggen har körts. De 31 gröna kontrollerna gäller den privata kampanjläsaren, inte acceptans av den ofärdiga testbänksrättningen. Root tar över de sparade filerna utan automatiska Luna-omförsök, kreditköp eller providerbyte. C3:s nya kampanj och C2 är inte klara. Inga tunga processer kör vid denna checkpoint.

## Återupptaget 2026-10-10

Användaren återupptog arbetet uttryckligen. En Luna fortsätter det sparade tvåfilspaketet på arbetsgrenen; root granskar före native-simuleringar och commit. Ingen kod är accepterad ännu. Den separat versionerade kampanjläsarens 36 snabba kontroller passerar: nio fält i bildposten med live/triggerstatus, fyra i lägesbytesposten med direkt blankprov, full 720-raderstäckning och negativa kontroller för saknade/felaktiga metadata. [Paketstatus](evidence/C3_bench_packet.json). Den avbrutna kampanjens råfynd behålls.

Luna överlämnade tvåfilspaketet med 56 snabba gröna kontroller. Root skärpte avslutskontrollerna och begränsade blankundantaget till det faktiska en-klockasfönstret vid lägesbyte. Åtta riktade native-körningar har startat under bygglåset: frön 1200/1208/1201/126, tre RTL-felvarianter och en accepterad läsning vars data medvetet hålls tillbaka. Alla åtta har kompilerats och kör nu i vvp; utfall, fullsvit och merge är ännu inte godkända.

Första riktade körningen är avslutad och bevarad. Alla fyra positiva frön passerade: 1200/1208 med 576 kontrollerade rader, 1201/126 med 288. Stimulus för 1200/1208/1201 är byte-identiskt med kampanjens tidigare underkända körningar; 126 är ett extra prov med density 2.5. Lägesbytesfelvarianten upptäcks. De två grindfelvarianterna aktiverar däremot inte sina avsedda villkor, och det fastlåsta läsprovet når gränsen vid 4096 klockor men avslöjar ett saknat formatfält i felkvittot. Paketet är därför underkänt tills dessa kontroller är rättade. Root/Luna kompletterar även slutkvittot med masken för en kvarvarande delvis fylld skrivgrupp; RTL ändras inte.

Tvåfilspaketet är pushat på `fix/c3-bench-drain-trigger-oracle` som **`0dcff5d`**. 81 snabba kontroller och samtliga tio riktade native-jobb passerar. Samma grindstimulus ger blank bild i oförändrad RTL och video i båda felvarianterna, som upptäcks vid exakt samma bildprov; lässtoppet ger komplett felkvitto vid 4096 klockor. Hela Core-grinden har startat på en ren, fryst kopia: **543 tester i 39 filer**, en pytest-process per fil, högst tio samtidigt under bygglåset. Inga tester får hoppas över eller räknas som godkända known/edge. M4:s 46 och M6:s 47 byggindata samt deras arkiverade artefakter är identiska med de accepterade byggena; ingen ny byggkörning påstås. Merge till main och den nya 260-frökampanjen väntar på fullsviten.

### Kampanjköraren granskad, 2026-10-10

Luna rättade tre luckor i den privata C3-köraren: checker-anteckningar kunde döljas bakom PASS, råfiler saknade verifierade kvitton vid återupptagning, och ett signalavbrott kunde lämna barnjobb efter att låset släppts. Root hittade dessutom ett fel i avbrottstestets väntan och en städningslucka vid loggfel. Den första testkörningens 36 PASS/1 FAIL är bevarad; efter rättning passerade 59 rena fil-/processkontroller på 3,85 s. Integrationstestet kör den verkliga adapterkoden mot en fejkad simulator och verifierar två frökvitton före resultatraderna. SIGINT/SIGTERM/SIGHUP, eskalering, låsordning och loggfel är provade med korta barnprocesser och ett tillfälligt lås.

Detta verifierar köraren, inte störningskampanjen. Äldre kampanjer och hjälpfiler är oförändrade. 543-testgrinden på fryst `0dcff5d` pågår fortfarande; ny kampanj startas först efter accepterad Core-merge och Puck-kontroll.

### Bänkpaket accepterat och ny kampanj, 2026-10-10

Den frysta grinden på `0dcff5d` passerade **543 tester i 39 filer**, inga andra utfall, på **4 993,121 s (1:23:13)**. Alla 157 källhashar är oförändrade; 19 cocotb-rapporter är bundna till sina test och formalgrinden gav 7 bevis/14 verkliga motexempel. Kvittots SHA-256 är `81eb8e3813a5f0099e06e450257e274df77edd2fdd87a4f880b9a830e8493d7b`. M4:s 46 och M6:s 47 byggindata matchar de tidigare accepterade byggena; samtliga 24 arkiverade artefakter är oförändrade. Ingen ny routning påstås.

Båda README är uppdaterade i `a3d44e0`; verifierat arbete är mergat med `--no-ff` och pushat till Core main **`606659f`**. Puck main **`f8d9de1`** pekar dit efter **1 pass på 1,53 s**, inklusive reset-, stift- och validatorfel som negativa kontroller. Den nya störningskampanjen startade 10:08:59 UTC på en ren, fryst kopia av slutlig main vars 157 indata matchar den testade källan. Den omfattar 260 frön i sex grupper, med nya råkvitton och oförändrade äldre resultat. [Kampanjstatus](evidence/C3_campaign_606659f.json). Kampanjen är pågående och ännu inte accepterad.

C2:s läsbara förberedelse är klar: tvådekoder-trace behövs för pollordningen, och UART-formatet är fastlagt till 62 byte inklusive CRLF. C2-kod och dess nya M6 seed-2-grind återstår. Ingen FPGA-hårdvara är verifierad.

### Kampanj stoppad för täckningsanalys, 2026-10-10

Frö **1249** gav `bench/few_lines`: **72 kontrollerade bildrader mot minst 144**. Kampanjen stoppades därför innan fler grupper: **50 färdiga rader, 49 PASS och 1 FAIL**, inga known/edge/crash; tio påbörjade frön bevaras. Den verifierade koordinatorn fick SIGTERM, stoppade sin egen barngrupp innan bygglåset släpptes och avslutade med 143. Inga egna barnprocesser är kvar och låset kunde återtas. Samtliga 628 evidensfiler har sparade hashvärden.

Råfelet och minimitäckningen behålls. En Luna läser stimulus, bildprover och slutkvitto för att avgöra om stimulus/avslut gav för liten visningstäckning eller om någon bildregel bröts. Inget RTL-fel eller hårdvarufel är fastställt. Den accepterade 543-testgrinden för bänkpaketet står kvar, men den nya 260-frökampanjen är **inte accepterad**. [Aktuellt kvitto](evidence/C3_campaign_606659f.json).


### Aktiv bild före lägesbyte, 2026-10-10

Frö 1249 hade en komplett triggerstartad LOW-bild vars aktiva yta var färdig före lägesbytet i vertikal blankning. Checkern räknade bort den med sitt gamla helbildsfönster. Den snäva rättningen på `fix/c3-active-display-window`, **`79b1406`**, använder bildens observerade ALT: 1650 klockor per NTSC-rad, 1980 per PAL-rad. Alla tidigare invarianter, X/Z-fönstret efter byte, ringmodellen och miniminivån 144 ligger kvar. Okänd ALT i en komplett videobild blir ett uttryckligt fel. RTL ändras inte.

104 snabba kontroller passerar. Återläsning av samtliga 50 sparade råresultat passerar utan fynd, known/edge eller anteckningar; 1249 räknar 144 rader. En ny native-körning av 1249 avslutade med kod 0 och byte-identiska A/B/CTL-, mixer-, minnes- och bildspår. Avsiktligt fel bildord och fel källrad upptäcks i den nytillagda bilden. Första återkörningens kvittosparare missade processdiagnostiken; försöket är underkänt och bevarat. De 628 filerna från den stoppade kampanjen är oförändrade.

Root har bundit 121 evidensfiler och provat 13 negativa kvittokontroller. Uppgiftsgrenen är pushad, men ännu inte mergad. Hela Core-grinden kör på en ren fryst kopia: **566 tester i 39 filer**, 157 källhashar och samma obligatoriska 19 cocotb-rapportidentiteter som föregående acceptans. Fullsvit, README, main-merge, Puck-kontroll och en ny 260-frökampanj återstår före C2. [Aktuellt kvitto](evidence/C3_active_display_window.json). Ingen FPGA-hårdvara är verifierad.


### Displaypaket accepterat och ny kampanj startad, 2026-10-10

Den frysta sviten avslutades med **566 pass i 39 filer** på **4893,875 s**; alla 157 källhashar är oförändrade. Root verifierade samtliga 19 cocotb-rapportidentiteter, 7 positiva formella bevis, 14 motexempel från reset och alla 24 arkiverade byggartefakter. Den ursprungliga efterkontrollen gav exit 1 efter gröna tester: ett rent Python-parameternamn med `/` behandlades som ett cocotb-filnamn. Separat eftervalidering tar bort endast kandidater utan cocotb-modul och behåller kontrollerna för verkliga XML-filer. Tre negativa kontroller passerar. Testerna kördes inte om och råfelet bevaras.

Uppgiftsgrenen är mergad och pushad: Core **`db0035f`**, README **`26d05b5`**. Alla testade indata matchar även den mergade källan. Pucks Core-länk är mergad/pushad som **`5ff06be`**, med 1 pass på 1,55 s och negativa kontroller för RESETB, fel stift och saknad validator. M4 seed 0/M6 seed 3 återanvänds; ingen ny routning hävdas.

Den nya 260-frökampanjen kör nu under bygglåset från en ren fryst kopia av `db0035f`, med högst tio arbetare i en grupp åt gången. Tidigare 49 PASS/1 FAIL och partiella råfiler bevaras separat. Kampanjen är **inte accepterad** och C2:s implementation, fullsvit och M4 seed 0/M6 seed 2 återstår. [Källbundet kvitto](evidence/C3_active_display_window.json). Ingen FPGA-kedja är verifierad på hårdvara.


### C2:s uppgiftsgren förberedd

Root har släppt den accepterade C3-main-källan `db0035f` för separat C2-kodarbete på **`feat/tvvcr-menu`**. Kampanjen fortsätter på sin oföränderliga kopia; native-simuleringar, fullgrind, byggen och merge är inte släppta. En Luna på max äger controller/UI, deras bänkar/tester, M6-kopplingen, nya indata bundna till noll i M3/M4 samt snowlog/parsertester. README-resultat och main-integration ägs av root.

Den privata I2C-pinavkodaren har 10 gröna syntetiska fixture-tester, granskade av root. Två upptäckta informationsförluster är rättade: spåret måste börja på känd vilande buss och en START på den andra SDA-linjen under överföring avvisas. Ingen verklig HDL-pintrace eller C2-beteendeverifiering har ännu körts. C2 måste visa rätt ordning på båda dekodrarna, stale-ACK/NACK-fairness och TV/VCR-värden innan acceptans.


### Tungt arbete pausat för spel

Användaren vill spela Baldur’s Gate 3. Inga egna simulerings- eller byggprocesser kör och det gemensamma bygglåset är verifierat ledigt. Inga nya tunga jobb startas före användarens återupptagning.

C3-kampanjen avslutade 200 frön: **199 PASS och 1 FAIL**, inga known/edge/crash. Frö 1345 gav `bench/few_lines`, 72 kontrollerade bildrader mot minst 144; koordinatorn avslutade med kod 2 innan de sista 60 fröna. Råfilerna behålls och orsaken är ännu inte triagerad. Detta är ingen kampanjacceptans och inget fastställt RTL-/hårdvarufel.

Luna har överlämnat C2-utkastet på `feat/tvvcr-menu`, med rapporterade 14 rena parser-/pin-fixture-pass och 2 subtester. Root-granskning, native-controller/UI-simuleringar och M4/M6-byggen återstår. Utkastet är inte incheckat, pushat eller mergat.


### Seed 1345 med kontinuerlig källa, 2026-10-12

Återspelning på accepterad Core `a1247ab` gav åter FAIL: 72 kontrollerade rader mot 144. A/B/CTL och mixer-, minnes- och bildspår är byte-identiska med den gamla kampanjen. Simulatorn avslutade utan fel; kampanjadapterns exit 0 betyder att alla begärda jobb blev klara, inte att deras checkerresultat är PASS. [Baslinjegranskning](evidence/seed1345-baseline-review.json).

Ett nytt separat scenario behåller alla tio ursprungliga störda kamerafält och styrbyten. Efter blankning läggs fyra rena progressiva NTSC-fält till, med 6 VBI-rader och 24 aktiva rader per fält i den skalade geometrin; suffixen på de två dekodrarna börjar 12,641 ns från varandra. Samtliga originalbytes, starttider, byteklockor och CTL-bytes är kvar. Produktions-RTL, modeller, checker,144-tröskeln samt switch-/X/Z-fönster ändras inte. [Nytt kontrakt](evidence/seed1345-extended-contract.json).

Det nya provet passerade med **360 kontrollerade rader på 220,521 s**, utan fynd, known, edge eller notes. Root återläste råspåren och kontrollerade 157 källhashar, 12 råfiler och helperhashar. Samma nya råspår men den gamla källsluttiden ger 72 rader. Ett fel bildord respektive fel källrad i den första nytillkomna bilden vid pixelklocka 1364592 avvisas av `display/word` respektive `display/map`; vardera sänker den godkända täckningen till 288. Åtta rena förkontroller verifierar också suffixens BT.656-geometri och att en bild efter källslut fortfarande räknas bort. [Rootacceptans](evidence/seed1345-extended-acceptance.json) · [Förkontroller och granskning](evidence/seed1345-suffix-review.json).

Detta accepterar bara det nya seed1345-scenariot. Den gamla kampanjen står kvar på 199 PASS / 1 FAIL / 60 ej körda. Fyra rena slutfält är ännu inte ett generellt kontrakt för PAL, full geometri eller alla störningsklasser; ingen 260-frökampanj har startats och ingen hårdvara är mätt.


### Fler genererade fält ändrar originalkontraktet, 2026-10-12

En modellkontroll jämförde ursprungligt fältantal med fyra extra genererade fält för en representant från var och en av kampanjens sex parametergrupper. Minst ett ursprungligt byteprefix ändrades i samtliga sex fall. Styrbytenas tider ändrades i fyra fall; byteklockor och starttider behölls i alla sex. Baslinje 1345 matchar de tidigare sparade native-indata. Körningen tog 18,96 s och alla 157 källhashar var oförändrade. [Rootgranskat mätkvitto](evidence/field-growth-audit.json).

| Grupp | Frö | A-prefix kvar | B-prefix kvar | CTL-bytes/tider kvar |
|---|---:|---|---|---|
| scaled-d1 | 1200 | Ja | Nej | Ja |
| scaled-d2p5 | 1345 | Nej | Nej | Nej |
| scaled-bedge-d1 | 1400 | Ja | Nej | Ja |
| scaled-bedge-d2p5 | 1425 | Nej | Nej | Nej |
| full-d1 | 1500 | Nej | Nej | Nej |
| full-d2p5 | 1505 | Nej | Nej | Nej |

Att bara höja `n_fields` är därför inte ett prefixbevarande kontrakt för dessa prov. Nästa generella tillägg ska behålla redan genererade kamerabytes och styrtider och bygga en separat fortsättning. Detta var sex modellfall, ingen native-simulering eller acceptans av hela 260-frökampanjen.
