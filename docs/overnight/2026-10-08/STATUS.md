# Kvällspass 2026-10-08

Uppdraget är [NATTPASS_2026-10-08.md](../../NATTPASS_2026-10-08.md). Användaren valde uttryckligen uppgiftsgrenar och merge till `main` efter verifiering. C1 → C3 → C2 är ordningen. Codex/root granskar, kör grindarna och integrerar; Luna hjälper med avgränsade filer (nu high, äldre max-körningar är historik). Den befintliga Vibe-sessionen äger M1–M3 och startas eller styrs inte av Codex.

## Aktuell rootacceptans 2026-10-13: Core `0503dac`

Fryst Core `0503dac` är rootgranskad i simulation och färska byggen: **695 pass / 43 filer / 439 processer / 187 Git-indata**, 19 cocotb-rapporter, sju formella bevis och fjorton verkliga negativa motexempel. Helsviten kördes en gång på **7328,015 s**. Den avsiktliga STRICT-negativen gav rätt tRCD-stopp och en SimFailure; de övriga 18 XML-filerna är rena. Alla käll-/runtimebytes och barnloggar är bundna. [Acceptans och artefakter](evidence/core-0503-gate.json).

Den nya fältlagringsregeln avvisar den anslutna delraden 4 som börjar vid ord 101; den gamla regeln markerar och läser den. BUF-marginalerna innehåller 10 F- och 325 R-kontroller, LOW 11 W-kontroller. Alla giltiga marginaler överstiger en pixelklocka; de tre riktiga sena F/W/R-felvarianterna avvisas. Root prövade 25 resultat-/XML-/byggmetadata-negativer och 24 skadade ägda artefaktkopior. Alla 24 byggartefakter inklusive manifest har hash och storlek.

Färska **M0 seed 0 / M4 seed 0 / M6 seed 2**, IOREG **0/1/1**, klarar 75 MHz på samtliga berörda klockor. M4:s lägsta maxfrekvens är **107,70 MHz**, M6:s **108,18 MHz**. Fyra TMDS-par i vardera M4/M6 är identiska med det färska M0-bygget. SDRAM:s stifttiming, fas på kortet och HDMI-kompatibilitet är fortfarande omätta.

Ett privat skript stannade före diagnossimuleringen eftersom en addendumfil saknades. Första felresultatet, skriptet och loggen är bevarade. Ett nytt fortsättningskontrakt band 507 befintliga artefakter och körde endast de ännu inte startade diagnos-/byggstegen; helsviten kördes inte om. Inga RTL-, modell-, checker-, seed- eller tröskeländringar gjordes för detta paket.

Fjärr-Core har därefter gått till `46a1e4f` med VINTERP, HDMI/AVI och varierande vsync-rad. De ändringarna och externa 728-test-/byggpåståenden omfattas inte av denna acceptans. Puck-fjärrmain `1404485` pinnar fortfarande Core `f32407f`; lokal Puck `a2ad438` är orörd. Separat källgranskning/integration återstår. Den blandade 257+3-kampanjrapporten är inte rootaccepterad som 260 frön. Gamla FAIL och äldre källbundna acceptanser nedan bevaras.

## Historisk brief 2026-10-12 efter opt-in recovery

Detta avsnitt bevarar läget efter opt-in recovery; aktuell rootacceptans står ovan. Användaren har lämnat datorn med ”Datorn är din” och begärt fortsatt arbete inom ordinarie kvot, en uppgift åt gången. Ett tungt jobb åt gången hålls under `/home/lenny/openvrx-review/build.lock`.

- Core main **`2dca245`** har explicit `--recovery-fields` (standard 0) i kampanjköraren. Schema 2 binder fortsättningen i manifestet; 75 fokuserade tester och två native-prover med 360/6 480 rader är rootgranskade. RTL, checkerpredikat och trösklar är oförändrade; alla 160 aktuella indata matchar mergad main. [Acceptans](evidence/recovery-campaign-acceptance.json). C2:s tidigare main **`a1247ab`** innehåller C2-grenen **`509fc95`**, verifierad från källan **`c3fda21`**. Den frysta sviten gav **604 pass i 39 filer** på **5411,439 s**, 157 oförändrade källhashar, alla 570 tidigare testnoder, 19 cocotb-rapportidentiteter samt 7 formella bevis och 14 verkliga negativa motexempel. Root återvaliderade råresultat och både fryst källa och slutlig main. [Svitacceptans](evidence/C2_SUITE_ACCEPTANCE.json) · [Slutgranskning](evidence/C2_SUITE_ROOT_REVIEW.json).
- Färska M0 seed 0, M4 seed 0 och M6 seed 2-byggen passerar 75 MHz på samtliga rapporterade klockor. M4:s lägsta maxfrekvens är 101,69 MHz, M6:s 104,85 MHz; alla fem M4/M6-domäner kontrollerades. Alla fyra TMDS-par matchar M0 i båda topparna. Root granskade manifest, råtiming och samtliga 24 arkiverade artefakter. [Bygggrind](evidence/C2_BUILD_GATE.json) · [Bygggranskning](evidence/C2_BUILD_ROOT_REVIEW.json).
- Puck main **`a2ad438`** pekar på Core `2dca245` efter egen uppgiftsgren och verifierad merge. De två stift-/schemakontrakttesterna passerade på **1,91 s**. Tidigare C2-gitlänk `f2e7d53`/`a1247ab` behåller sitt [kvitto](evidence/C2_INTEGRATION.json); den nya [integrationen](evidence/recovery-campaign-acceptance.json) gäller stimulusverktyget och dess opt-in-anrop.
- M6:s filterfält begär TV/VCR för båda dekodrarna. Ett pågående I²C-skrivvärde och SDA-linje hålls fast; en äldre kvittens lämnar ett nyare val väntande. NACK ger omförsök efter parad pollning. OLED/OSD och den nya 62-byte-loggen visar begärt menyval, inte en återläsning av 02h. Äldre loggformer behålls. [56 riktade pass/två subtester och nio meningsfulla gamla-vakt-negativer](evidence/C2_FOCUSED_ACCEPTANCE.json) är separat verifierade. Den första riktade körningens 53 pass/3 fail och timestampfel bevaras i [första granskningen](evidence/C2_FOCUSED_FAILURE_REVIEW.json).
- Mixerns väntande output-F-gräns över helt utelämnade fält ligger kvar; dekoderns F-bit är separat. B:s tidigare 570-pass- och byggresultat är historik, med sina ursprungliga kvitton.
- C3:s kampanj slutade vid 200/260 frön: **199 PASS, 1 FAIL**, 60 ej körda. Seed **1345** gav 72 kontrollerade rader mot minst 144; triagen fann bara en komplett kvalificerad aktiv bild före sista källbyten. Längre stimulus kräver nytt käll-/parameterkontrakt och ny evidenskatalog. Råfelet och tröskeln bevaras. Ingen ny kampanj har körts och inget RTL-fel är fastställt.

C2 är accepterat i simulation och byggen. Ingen FPGA-hårdvara eller TV/VCR-bildskillnad är mätt; kamera/VTX → Moneagle vid 4,2 V är en separat bänkobservation. Seed1345-kontrollen är nu slutgranskad: oförändrad baslinje FAIL 72<144, separat prov med fyra tillagda kamerafält PASS 360. Prefixbevarande fortsättning har nu separata native-prover för 1345/1400/full-PAL1601 och en explicit modell-API i Core. Opt-in-anrop och parameterkontrakt är nu verifierade separat. En ny kampanj behöver en egen fryst källa, strikt råevidens och resultatgranskning; ingen sådan slutkampanj har startats.

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


### Privat recovery-suffix: byte- och modellgrind, 2026-10-12

Ett generellt privat prototypverktyg lägger fyra rena kamerafält efter det redan genererade störda prefixet. Det behåller A/B-prefix, styrbyten, starttider, byteklockor och klassmetadata; originalobjektet lämnas orört. Fortsättningen synkroniserar kanalernas ankomstfas efter blankning och följer originalets interlaced/progressiva kamerakonvention. Ursprunglig B-offset bärs därför inte vidare in i den nya recovery-fasen, medan dess byteklocka och eventuell drift behålls. Detta är ett nytt stimuluskontrakt.

Nio rena fall passerade på **18,56 s**: representanter för de sex gruppkonfigurationerna samt explicit PAL i skalad/full geometri och progressiv PAL. Båda modellmottagarna avkodar fyra kompletta fortsättningsfält med rätt radlängd, aktiv bytekvantitet, linjenummer och F-bit, utan felaktiga/korrigerade timingkoder eller luma utanför intervallet. Åtta ogiltiga fältantal/geometri/standard/klockvärden avvisas; alla 157 källhashar och helperhashar är verifierade. [Rootgranskning](evidence/generic-suffix-pure-review.json).

För 1345 är det generella verktygets A/B/CTL-bytes exakt samma som det tidigare accepterade native-provet med 360 kontrollerade rader. Övriga fall har bara byte-/modellacceptans; ingen ny native-simulering kördes i detta paket. Prototypen är privat och har inte integrerats i Core. Nästa uppgift är utvalda native-prober med ett nytt komplett käll-/helper-/parameterkontrakt, före en eventuell 260-frökampanj. Produktions-RTL/checker och gamla FAIL-kvitton ändras inte; hårdvara är fortfarande omätt.


### Generell fortsättning: native frö 1400, 2026-10-12

Den generella privata tilläggsfunktionen är nu också provad i native-simulering med frö 1400: skalad NTSC, density 1,0, tio originalfält, tvingad `b_edge` och fyra rena recovery-fält. Det är ett eget kontrakt; gamla kampanjens ej körda grupper får inget nytt utfall genom detta prov.

Kompilering, vvp och drain avslutade utan fel. **864 rader passerade på 223,77 s**, utan findings, known, edges eller notes. Root återläste hela modellen/invarianten mot råspåren, verifierade 157 källhashar, helperhashar, 12 råfiler och genererade originalindata. Originalprefix och CTL-bytes är kvar. Samma nya råspår med originalets källsluttid räknar 576 rader; detta är en jämförelse inom det nya provet, ingen separat native-körning av originalet.

Fel bildord och fel källrad i första tillkomna bilden vid pixelklocka 1435542 ger `display/word` och `display/map`, vardera med 792 godkända rader kvar. Första efterkontrollen pekade av misstag på den 1345-specifika fixture-loggen och stoppade innan replay; den är bevarad. Den rättade efterkontrollen binder den verkliga generella pure-granskningens hash. Ingen simulering kördes om. [Rootacceptans](evidence/recovery-native-1400.json).

Core a1247ab och Puck f2e7d53 är oförändrade. Funktionen är fortfarande privat. Full geometri och PAL behöver egna native-prober innan någon ny 260-frökampanj eller produktionsintegration; gamla FAIL och 144/720-gränser står kvar. Ingen FPGA-hårdvara är mätt.


### Generell fortsättning: full PAL frö 1601, 2026-10-12

Ett separat native-prov använder full geometri, PAL, density 1,0 och åtta originalfält med tvingade `pal`/`mode_switch`, följt av fyra rena recovery-fält. Alla originalbytes, styrtider och byteklockor behålls. Fortsättningen följer originalets interlaced-kamerakonvention och synkroniserar kanalernas ankomstfas efter blankning.

**6 480 rader passerade på 2 000,922 s**, med minst 720 som oförändrat krav. Kompilering, vvp och drain avslutade utan fel; inga findings, known, edges eller notes. Root återläste modeller och invarianter, verifierade 157 källhashar, helperhashar, 12 råfiler, genererade originalindata samt fullgeometrins och alla fyra RT-parametrarnas verkliga kompilatorargument.

Samma råspår med originalets källsluttid räknar 2 880 rader; det är ingen separat native-baslinjekörning. Fel bildord och källrad i den första tillkomna kontrollerbara bilden vid pixelklocka 11137542 ger `display/word` respektive `display/map`/`display/not_read`; vardera lämnar 5 760 godkända rader. Den bilden kör BUF, vilket styr ordkontrollens förväntade feltyp. [Rootacceptans](evidence/recovery-native-1601.json).

Detta accepterar endast det nya full-PAL-scenariot. Core a1247ab och Puck f2e7d53 är oförändrade; prototypverktyget är fortfarande privat. Gamla kampanjen med 199 PASS/1 FAIL/60 ej körda är fortsatt inte accepterad. Ingen FPGA-hårdvara är verifierad.


### Recovery-modellverktyg integrerat, 2026-10-12

`fuzz_recovery.append_camera_fields(scenario, fields=4)` finns nu i Core. Dess algoritm är identisk med den privata prövade versionen; den binder generator- och mottagarmodellerna genom lokala importnamn. Generatorn, kampanjköraren, checker och RTL ändras inte. **68 fokuserade tester passerade på 23,65 s**, varav 25 nya för nio geometri/standard/kamerafall, ogiltiga metadata och två verkliga strömskador. A/B-bytes matchar golden-hasharna från de tre accepterade native-proven.

Root verifierade de tidigare 157 oförändrade indata och de två tillagda modellfilerna. Den verkliga kampanjmanifestfunktionen tar med dem; ett manifest från den frysta gamla källan avvisas utan att ändra manifest eller starta något frö. Första privata snapshot-granskningen hade kvar fel HERE-sökväg när den läste gamla källan; den stoppade före resume-evidence och är bevarad. Den rättade granskningen ändrar inga produktionsfunktioner eller fokuserade tester. Core/Puck är mergade och pushade, Pucks två stiftkontrakttester passerade på 2,08 s. [Integrationsacceptans](evidence/core-recovery-helper.json).

Detta paket har ingen ny helsvit eller FPGA-routning. C2:s frysta 604-pass-resultat och byggen behåller sin ursprungliga källa. Verktyget är explicit opt-in på modellnivå; kampanj-CLI använder det ännu inte. Ingen ny 260-frökampanj eller hårdvaruacceptans påstås.


### Opt-in recovery i kampanjvägen accepterat, 2026-10-12

`--recovery-fields N` gäller `run` och `narrow`, med 0 som standard. Schema 2 binder antalet och typen av fortsättning; ändringar avvisas före workerstart och lämnar tidigare evidens orörd. Valet går vidare genom worker till `run_seed`; budgeten räknar med tillagda fält och PASS-råfiler bevaras för recovery. Originalets störningar, bytes och styrtider behålls. 75 fokuserade tester passerade på 43,43 s.

De två nya native-proven på fryst `7754112` gick seriellt: skalat frö 1345 (densitet 2,5, tio originalfält och fyra recovery-fält) gav **360 rader på 215,8 s**; frö 1601 med full PAL-geometri (densitet 1, åtta originalfält och fyra recovery-fält, tvingad `pal`/`mode_switch`) gav **6 480 rader på 1 954,0 s**. Kompilering, vvp och drain passerade utan fynd, known, edges eller notes. Alla sex kamera-/CTL-/mixer-/minnes-/bildfiler i vardera provet är byte-identiska med motsvarande tidigare accepterade native-prov.

Root verifierade 160 källhashar och 24 råfiler, återläste modeller/invarianter och avvisade fel bildord/källrad i båda tillkomna bildfönstren. De fyra negativa återläsningarna lämnar 288/288 respektive 5 760/5 760 godkända rader. Samma spår med originalsluttid ger 72 respektive 2 880 rader. Elva simulator-/modell-/checkerfunktioner är AST-identiska med a1247ab; kraven på 144/720 rader och 3000 s timeout behålls. Core och Puck är mergade och pushade, och Pucks två tester passerar på 1,91 s. [Integrationsacceptans](evidence/recovery-campaign-acceptance.json).

Detta är acceptans av de två opt-in-proven och parameter-/resume-vägen. Ingen ny 260-frökampanj, helsvit eller FPGA-routning är körd. Gamla 199 PASS/1 FAIL/60 ej körda och C2:s frysta 604-pass-källa/byggen bevaras; ingen FPGA-hårdvara är verifierad.


### Skalad PAL-recovery: frö 1600, 2026-10-12

Ett separat native-prov genom accepterad kampanjworker använder skalad PAL, densitet 1, tio interlaced originalfält, tvingad `pal` och fyra rena recovery-fält. **1 008 rader passerade på 280,1 s**, med minst 144 som oförändrat krav. Kompilering, vvp och drain avslutade utan fynd, known, edges eller notes. Genererade A/B/CTL-förväntningar matchar verkliga kompletta indata; originalprefix, styrtider och byteklockor är kvar. Detta har ingen äldre native-baslinje att jämföra pixelspåren mot.

Root verifierade 160 källhashar, runtime-/kampanjmanifestet, helperhashar och 12 råfiler och återläste modeller/invarianter. Fel bildord och källrad i det tillkomna kontrollerbara bildfönstret vid pixelklocka 1722642 ger `display/word` respektive `display/map`/`display/not_read`, vardera med 936 godkända rader kvar. Bilden använder BUF. Samma nya råspår med originalets källsluttid räknar 648 rader; det är ingen separat native-körning av originalet. [Rootacceptans](evidence/recovery-scaled-pal-1600.json).

Första förkontrollen stoppade före kompilering: förberedelsen använde Python 3.14.7, projektets körmiljö 3.12.12. Endast Python-identiteten skilde; felkontrakt och logg bevaras. Ett separat kontrakt och en ny outputkatalog förbereddes med faktisk körmiljö. Alla sex original-/extended-inputfiler är byte-identiska över versionerna; versionskontrollen behölls. En enda faktisk native-körning gjordes, med oförändrade källor, seed, 144-raderskrav och 3000 s timeout.

Core 2dca245 och Puck a2ad438 är oförändrade. Skalad PAL har nu native-acceptans för detta scenario; full NTSC återstår som separat prov i matrisen. Ingen ny 260-frökampanj, helsvit, routning eller FPGA-hårdvarumätning påstås.


### Full NTSC-recovery: frö 1500, 2026-10-12

Ett separat native-prov genom accepterad kampanjworker använder full NTSC, densitet 1, åtta interlaced originalfält, tvingad `mode_switch` och fyra rena recovery-fält. **5 760 rader passerade på 1 659,2 s**, med minst 720 som oförändrat krav. Kompilering, vvp och drain avslutade utan fynd, known, edges eller notes. De kompletta A/B/CTL-indata matchar genererade förväntningar; originalprefix, styrtider och byteklockor är kvar. Detta har ingen tidigare native-pixelbaslinje att jämföra mot.

Root verifierade 160 källhashar, runtime-/kampanjmanifestet, helperhashar och 12 råfiler och återläste modeller/invarianter. Fel bildord och källrad i det tillkomna kontrollerbara BUF-bildfönstret vid pixelklocka 9913242 ger `display/word` respektive `display/map`/`display/not_read`, vardera med 5 040 godkända rader kvar. Samma nya råspår med originalets källsluttid räknar 2 880 rader; det är ingen separat native-körning av originalet. Förberedelse och execution använder projektets Python 3.12.12, med oförändrade versionskontroller och 3000 s timeout. [Rootacceptans](evidence/recovery-full-ntsc-1500.json).

De fyra geometri-/standardkombinationerna har nu utvalda accepterade native-prover:

| Geometri | Standard | Frö | Kontrollerade rader | Acceptans |
|---|---|---:|---:|---|
| Skalad | NTSC | 1345 | 360 | [Nya API-vägen](evidence/recovery-campaign-acceptance.json) |
| Skalad | PAL | 1600 | 1 008 | [Separat prov](evidence/recovery-scaled-pal-1600.json) |
| Full | NTSC | 1500 | 5 760 | [Separat prov](evidence/recovery-full-ntsc-1500.json) |
| Full | PAL | 1601 | 6 480 | [Nya API-vägen](evidence/recovery-campaign-acceptance.json) |

Varje prov har två faktiska negativa kontroller i ett tillkommet bildfönster. Det är representanter för ett nytt recovery-kontrakt, ingen acceptans av alla kampanjfrön, tätheter eller bildlägeskombinationer. Core 2dca245 och Puck a2ad438 är oförändrade. Ingen ny 260-frökampanj, helsvit, routning eller FPGA-hårdvarumätning är körd. En större runda kräver ett separat kontrakt med strikt råevidens, återupptagning och granskning.


### Strikt recovery-runda: adapter och pilot, 2026-10-12

Den privata kvitto-/resume-adaptern binder nu recovery-antalet i parameterkontraktet, sparar kompilatorns och vvp:s stdout/stderr och kräver en worker åt gången. **73 aktuella fixturetester passerade** (58 befintliga och 15 nya). Oförändrade hjälpare validerar hash, storlek, sökvägar, råkvitton och ägd processgrupp. Den historiska räkningsuppgiften 59 korrigerades mot de verkliga testfilerna; en saknad relativ pixel-fixture återställdes byte-identiskt. Ursprungliga felloggar är kvar.

Ett pilotfrö, 1200 med skalad NTSC, densitet 1, tio originalfält och fyra recovery-fält, kördes på fryst Core 2dca245: **864 rader på 220,1 s**, med oförändrat minimikrav 144 och inga fynd, known, edges eller notes. Root verifierade 160 källhashar, runtime, adapterhashar och 15 rå-/diagnostikfiler samt återläste modeller och invarianter. Fel bildord och källrad i första tillkomna BUF-bilden vid pixelklocka 1435542 avvisas; båda lämnar 792 godkända rader. Samma spår med originalets sluttid räknar 576 rader.

Identisk resume körde noll nya frön och behöll resultatrad, råfiler och kvitto byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart utan evidensändring. Skadad råfil i en ägd kopia avvisades. Första efterkontrollskriptet använde en funktion för platta råkataloger på hela resultatkatalogen och stoppade efter lyckad resume; felet är bevarat. Rättad efterkontroll återanvände den avslutade resume-körningen. Ingen simulering kördes om. [Rootacceptans](evidence/recovery-round-adapter.json).

Core 2dca245 och Puck a2ad438 är oförändrade. Adaptern är privat och har bara en accepterad pilot; större rundor kräver ett separat kontrakt och egen granskning. Gamla 199 PASS/1 FAIL/60 ej körda behålls. Ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda med tre frön, 2026-10-12

Den granskade privata adaptern körde exakt frö 1201–1203 seriellt på fryst Core 2dca245: skalad NTSC, densitet 1, tio originalfält och fyra recovery-fält, ingen tvingad störning. Alla tre passerade med **576 / 864 / 864 rader** på 225,6 / 225,2 / 239,5 s. Minimikravet 144 rader och 3000 s timeout är oförändrade. Kompilering, vvp och drain passerade utan findings, known, edges eller notes.

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt tre resultatrader/kvitton och 45 rå-/diagnostikfiler. Kompletta kameraindata, originalprefix och CTL matchar genererade förväntningar. Modell- och invariantåterläsningen passerar. Fel bildord och källrad i varje tillkommet bildfönster upptäcks: sex negativa kontroller lämnar 504/504, 792/792 och 792/792 godkända rader. Samma spår med originalets sluttid ger 288 / 576 / 576 rader.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart. En skadad råfil i en ägd kopia avvisades; verkliga rådata behölls. [Rootacceptans](evidence/recovery-round-1201-1203.json).

Detta accepterar endast den avgränsade trefrörundan. Core och Puck är oförändrade. Gamla kampanjens 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny 260-frökampanj, helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda med fem frön, 2026-10-12

Frö 1204–1208 kördes seriellt genom den granskade privata adaptern på fryst Core 2dca245, med skalad geometri, densitet 1, tio originalfält och fyra recovery-fält. Alla passerade kompilering, vvp, drain och modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Ingen störning eller standard tvingades; generatorn valde PAL för 1204 och NTSC för övriga. Den ursprungliga taskens beteckning skalad NTSC var för snäv och har ett separat rättelsekvitto; körkontrakt och indata är oförändrade.

| Frö | Standard | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---:|---:|---:|
| 1204 | PAL | 1 008 | 271,4 | 648 |
| 1205 | NTSC | 648 | 237,7 | 360 |
| 1206 | NTSC | 360 | 217,5 | 216 |
| 1207 | NTSC | 864 | 227,1 | 576 |
| 1208 | NTSC | 864 | 224,1 | 576 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt fem resultatrader/kvitton och 75 rå-/diagnostikfiler. Kameraindata, originalprefix och CTL matchar genererade förväntningar. Två verkliga fel per frö, bildord och källrad i en tillkommen BUF-bild, ger de väntade kontrollfynden: tio negativa återläsningar lämnar 936/936, 576/576, 288/288, 792/792 respektive 792/792 godkända rader.

Identisk resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1204-1208.json).

Core och Puck är oförändrade. Detta accepterar fem nya scenarier, ingen fullständig kampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda med tio frön, 2026-10-12

Frö 1209–1218 kördes seriellt med den granskade privata adaptern på fryst Core 2dca245: skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla tio passerade kompilering, vvp, drain och modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Generatorn valde PAL för 1210 och NTSC för övriga; 1213 och 1218 har den genererade progressive-störningen.

| Frö | Standard | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---:|---:|---:|
| 1209 | NTSC | 864 | 226,5 | 576 |
| 1210 | PAL | 1008 | 266,9 | 648 |
| 1211 | NTSC | 864 | 228,5 | 576 |
| 1212 | NTSC | 792 | 234,8 | 504 |
| 1213 | NTSC | 864 | 225,6 | 576 |
| 1214 | NTSC | 576 | 228,3 | 288 |
| 1215 | NTSC | 792 | 228,9 | 504 |
| 1216 | NTSC | 720 | 220,7 | 432 |
| 1217 | NTSC | 864 | 239,9 | 576 |
| 1218 | NTSC | 504 | 221,3 | 216 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt tio resultatrader/kvitton och 150 rå-/diagnostikfiler. Alla original-/extended-kameraindata, prefix och CTL matchar genererade förväntningar. Två verkliga fel per frö i en tillkommen bild, fel bildord respektive källrad, ger de väntade kontrollfynden: 20 negativa återläsningar upptäcker felen och minskar antalet godkända rader. Bildfönstren för 1214, 1216 och 1218 använder LOW; övriga använder BUF. Kvittodata anger rätt läge; formuleringen som kallade alla dessa fönster BUF rättades vid gruppkontrollen. Positiva återläsningar kontrollerar sammanlagt **7 848 rader**.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1209-1218.json).

Core och Puck är oförändrade. Detta accepterar endast den avgränsade rundan, ingen fullständig kampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda med tjugo frön, 2026-10-12

Frö 1219–1238 kördes seriellt på fryst Core 2dca245 med skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla tjugo passerade kompilering, vvp, drain samt modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Totalt kontrollerades **16 776 bildrader**.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---|---:|---:|---:|
| 1219 | NTSC | Interlaced | 864 | 239,5 | 576 |
| 1220 | NTSC | Interlaced | 648 | 224,6 | 360 |
| 1221 | PAL | Interlaced | 1008 | 277,4 | 720 |
| 1222 | NTSC | Interlaced | 864 | 235,0 | 576 |
| 1223 | NTSC | Progressiv | 792 | 226,0 | 504 |
| 1224 | NTSC | Interlaced | 504 | 229,2 | 216 |
| 1225 | NTSC | Interlaced | 864 | 236,4 | 576 |
| 1226 | NTSC | Interlaced | 792 | 226,6 | 504 |
| 1227 | PAL | Interlaced | 1008 | 281,7 | 648 |
| 1228 | NTSC | Progressiv | 864 | 226,8 | 576 |
| 1229 | NTSC | Interlaced | 576 | 227,8 | 288 |
| 1230 | NTSC | Progressiv | 864 | 227,1 | 576 |
| 1231 | NTSC | Interlaced | 864 | 221,6 | 504 |
| 1232 | PAL | Interlaced | 1008 | 273,1 | 648 |
| 1233 | NTSC | Interlaced | 864 | 237,6 | 576 |
| 1234 | NTSC | Progressiv | 864 | 222,5 | 576 |
| 1235 | NTSC | Interlaced | 864 | 224,7 | 576 |
| 1236 | NTSC | Interlaced | 864 | 223,7 | 576 |
| 1237 | PAL | Interlaced | 1080 | 283,3 | 720 |
| 1238 | NTSC | Interlaced | 720 | 219,6 | 432 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt tjugo resultatrader/kvitton och 300 rå-/diagnostikfiler. Alla kameraindata, originalprefix och CTL matchar genererade förväntningar. En separat återgenerering binder faktisk standard och kamerakonvention per frö till samma native-indata; den kör ingen ny simulering.

Två verkliga fel per frö i en tillkommen bild, fel bildord respektive källrad, avvisas: 40 negativa återläsningar ger de väntade fynden och färre godkända rader. Bildfönstren för 1220, 1229 och 1238 använder LOW; övriga använder BUF. Ordfelet kontrolleras därför med rätt LOW-/BUF-predikat.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1219-1238.json).

Core och Puck är oförändrade. Detta accepterar den avgränsade rundan, ingen fullständig kampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda 1239–1258, 2026-10-12

Tjugo frön kördes seriellt på fryst Core 2dca245 med skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla passerade kompilering, vvp, drain samt modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Totalt kontrollerades **16 344 bildrader**.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---|---:|---:|---:|
| 1239 | NTSC | Interlaced | 864 | 232,7 | 504 |
| 1240 | NTSC | Interlaced | 864 | 227,4 | 576 |
| 1241 | NTSC | Interlaced | 864 | 224,1 | 576 |
| 1242 | NTSC | Interlaced | 864 | 216,1 | 576 |
| 1243 | PAL | Interlaced | 1080 | 266,4 | 720 |
| 1244 | NTSC | Interlaced | 864 | 234,9 | 576 |
| 1245 | NTSC | Interlaced | 792 | 224,9 | 504 |
| 1246 | PAL | Interlaced | 1080 | 285,6 | 720 |
| 1247 | NTSC | Progressiv | 864 | 263,1 | 576 |
| 1248 | PAL | Interlaced | 1080 | 282,1 | 720 |
| 1249 | NTSC | Interlaced | 432 | 237,4 | 144 |
| 1250 | NTSC | Interlaced | 576 | 220,5 | 288 |
| 1251 | NTSC | Interlaced | 864 | 219,8 | 576 |
| 1252 | PAL | Interlaced | 1008 | 279,4 | 648 |
| 1253 | NTSC | Interlaced | 864 | 242,2 | 576 |
| 1254 | NTSC | Progressiv | 576 | 220,0 | 288 |
| 1255 | NTSC | Interlaced | 648 | 211,0 | 360 |
| 1256 | NTSC | Interlaced | 864 | 225,7 | 576 |
| 1257 | NTSC | Interlaced | 432 | 227,2 | 144 |
| 1258 | NTSC | Interlaced | 864 | 236,2 | 576 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt tjugo resultatrader/kvitton och 300 rå-/diagnostikfiler. Alla original-/extended-kameraindata, prefix och CTL matchar genererade förväntningar. Återgenereringen binder faktisk standard, interlacing och kamerafält till samma native-indata; metadata och ursprungliga kamerafält ska behållas i fortsättningen.

Två verkliga fel per frö i en tillkommen bild, fel bildord respektive källrad, avvisas: 40 negativa återläsningar ger de väntade fynden och färre godkända rader. Bildfönstren för 1250 och 1255 använder LOW; övriga använder BUF. Ordfelet kontrolleras med rätt LOW-/BUF-predikat.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1239-1258.json).

Core och Puck är oförändrade. Detta accepterar endast rundan, ingen fullständig kampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda 1259–1278, 2026-10-12

Tjugo frön kördes seriellt på fryst Core 2dca245 med skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla passerade kompilering, vvp, drain och modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Totalt kontrollerades **17 712 bildrader**.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---|---:|---:|---:|
| 1259 | PAL | Interlaced | 936 | 266,9 | 576 |
| 1260 | PAL | Interlaced | 1152 | 285,7 | 792 |
| 1261 | PAL | Interlaced | 1152 | 271,3 | 792 |
| 1262 | NTSC | Interlaced | 792 | 222,2 | 504 |
| 1263 | NTSC | Interlaced | 576 | 231,4 | 288 |
| 1264 | PAL | Progressiv | 936 | 267,1 | 576 |
| 1265 | NTSC | Interlaced | 864 | 223,9 | 576 |
| 1266 | NTSC | Interlaced | 864 | 219,4 | 576 |
| 1267 | NTSC | Interlaced | 504 | 218,0 | 216 |
| 1268 | NTSC | Interlaced | 864 | 236,0 | 576 |
| 1269 | PAL | Interlaced | 1008 | 269,9 | 648 |
| 1270 | NTSC | Interlaced | 864 | 236,8 | 576 |
| 1271 | PAL | Progressiv | 1008 | 267,7 | 648 |
| 1272 | PAL | Interlaced | 1008 | 272,4 | 648 |
| 1273 | PAL | Progressiv | 1080 | 263,2 | 720 |
| 1274 | NTSC | Interlaced | 864 | 217,1 | 576 |
| 1275 | NTSC | Progressiv | 864 | 228,2 | 576 |
| 1276 | NTSC | Interlaced | 504 | 223,3 | 288 |
| 1277 | PAL | Progressiv | 1008 | 272,4 | 648 |
| 1278 | NTSC | Progressiv | 864 | 244,2 | 576 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt tjugo resultatrader/kvitton och 300 rå-/diagnostikfiler. Alla original-/extended-kameraindata, prefix och CTL matchar genererade förväntningar. Faktisk standard, interlacing och kamerafält sparas från den bytebundna återgenereringen.

Två verkliga fel per frö i en tillkommen bild, fel bildord respektive källrad, avvisas: 40 negativa återläsningar ger väntade fynd och färre godkända rader. Bildfönstret för 1276 använder LOW; övriga använder BUF. Ordfelet kontrolleras med rätt LOW-/BUF-predikat.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1259-1278.json).

Core och Puck är oförändrade. Detta accepterar endast rundan, ingen fullständig kampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda 1279–1299, 2026-10-12

De sista 21 fröna i gruppen 1200–1299 kördes seriellt på fryst Core 2dca245 med skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla passerade kompilering, vvp, drain och modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Totalt kontrollerades **17 856 bildrader**.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---|---:|---:|---:|
| 1279 | NTSC | Progressiv | 864 | 239,8 | 576 |
| 1280 | NTSC | Interlaced | 936 | 232,6 | 648 |
| 1281 | PAL | Interlaced | 1080 | 278,3 | 720 |
| 1282 | NTSC | Progressiv | 648 | 226,9 | 360 |
| 1283 | PAL | Progressiv | 1008 | 276,5 | 720 |
| 1284 | NTSC | Interlaced | 864 | 231,2 | 576 |
| 1285 | NTSC | Interlaced | 1008 | 235,2 | 720 |
| 1286 | PAL | Interlaced | 1008 | 276,0 | 720 |
| 1287 | NTSC | Interlaced | 432 | 226,5 | 144 |
| 1288 | NTSC | Interlaced | 864 | 234,8 | 576 |
| 1289 | NTSC | Interlaced | 864 | 235,9 | 576 |
| 1290 | PAL | Interlaced | 1080 | 273,9 | 720 |
| 1291 | NTSC | Interlaced | 648 | 215,8 | 360 |
| 1292 | NTSC | Interlaced | 720 | 224,3 | 432 |
| 1293 | NTSC | Interlaced | 576 | 215,1 | 288 |
| 1294 | NTSC | Interlaced | 792 | 218,9 | 504 |
| 1295 | NTSC | Interlaced | 864 | 219,5 | 576 |
| 1296 | PAL | Interlaced | 1080 | 264,5 | 720 |
| 1297 | NTSC | Interlaced | 792 | 218,9 | 504 |
| 1298 | NTSC | Interlaced | 864 | 235,7 | 576 |
| 1299 | NTSC | Interlaced | 864 | 222,6 | 576 |

Root verifierade 160 källhashar, runtime, sex privata moduler, exakt 21 resultatrader/kvitton och 315 rå-/diagnostikfiler. Alla original-/extended-kameraindata, prefix och CTL matchar genererade förväntningar. Faktisk standard, interlacing och kamerafält sparas från den bytebundna återgenereringen.

Två verkliga fel per frö i en tillkommen bild, fel bildord respektive källrad, avvisas: 42 negativa återläsningar ger väntade fynd och färre godkända rader. Bildfönstren för 1291 och 1293 använder LOW; övriga använder BUF. Ordfelet kontrolleras med rätt LOW-/BUF-predikat.

Exakt resume körde noll nya frön och behöll råfiler, resultatrader och kvitton byte-identiskt. Ändrat recovery-antal, checkerhash och förväntad revision avvisades före workerstart; skadad råfil i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-round-1279-1299.json).

Core och Puck är oförändrade. Detta accepterar endast rundan. Alla hundra frön har individuella paketkvitton; gruppacceptans kräver en separat kontroll av fullständighet, dubbletter och identiska käll-/parameterkontrakt. Ingen fullständig 260-frökampanj är accepterad. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Hundrafrögruppen 1200–1299 accepterad, 2026-10-12

Gruppkontrollen binder exakt **100 unika frön** till åtta publicerade paket, samma frysta Core 2dca245, runtime, 160 källhashar och sex privata adaptermoduler. Alla använder skalad geometri, densitet 1, tio originalfält och fyra recovery-fält, utan tvingade störningar. De deklarerade rundornas seedset, taggar, output och budget skiljer sig; käll- och videoparametrarna är identiska. Inga frön saknas eller är dubblerade.

**83 448 bildrader** har passerat de tidigare modell-/invariantåterläsningarna. Gruppkontrollen verifierade åter alla 1 500 rå-/diagnostikfiler, kompilator-/vvp-kvitton, publicerade Git-artefakter och deras ancestry samt återgenererade alla original-/extended-kameraindata, prefix och CTL. Den körde ingen ny HDL- eller modellkampanj. Varje frö har två hashbundna verkliga fel i en tillkommen bild: totalt 200 negativa återläsningar. Elva negativa bildfönster använder LOW, 89 BUF.

| Kameradata i gruppen | Antal frön |
|---|---:|
| NTSC | 76 |
| PAL | 24 |
| Interlaced | 83 |
| Progressiv | 17 |

Tio semantiska kontroller av gruppvalideringen avvisar bortfall, dubbletter, oväntat frö, fel parameter/källa/helper, FAIL-rad, för få kontrollerade rader och saknad eller felaktig bildnegativ. En elfte kontroll avvisar faktisk bytekorruption i en ägd råkopia; samma kopia passerade före ändringen och originalet passerade efteråt. Alla åtta rundors verifierade resume kör noll nya frön och behåller raw/row/receipt byte-identiskt. [Gruppacceptans och fröledger](evidence/recovery-group-1200-1299.json).

Första auditen stoppade efter de nya fröna: dess filurval läste den gamla kampanjens händelsejournal som fröresultat. Kod, inputkontrakt och fellogg är bevarade. Den rättade auditen binder journalen och de två verkliga resultatfilerna separat, tillsammans med deras manifest; inget record ignoreras för att få rätt totalsumma. Ingen simulering kördes om. Den gamla kampanjen har fortfarande 199 PASS, 1 FAIL (1345, 72 rader), 60 ej körda och oförändrade filhashar.

Acceptansen gäller endast den nya hundrafrögruppen med fyra recovery-fält. Densitet 2,5 och andra kampanjgrupper återstår; ingen fullständig 260-frökampanj är accepterad. Minimikravet 144 och timeout 3000 s är oförändrade. Core/Puck är oförändrade; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda 1300–1304 med densitet 2,5, 2026-10-12

Fem frön kördes seriellt på fryst Core 2dca245 med skalad geometri, densitet 2,5, tio originalfält och fyra recovery-fält, utan tvingade störningar. Alla passerade kompilering, vvp, drain och modell-/invariantåterläsning utan fynd, known, edges eller notes. Minimikravet 144 rader och 3000 s timeout behölls. Totalt kontrollerades **4 392 bildrader**.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Native-tid (s) | Samma spår, originalsluttid |
|---|---|---|---:|---:|---:|
| 1300 | PAL | Progressiv | 1008 | 273,7 | 648 |
| 1301 | NTSC | Progressiv | 720 | 226,9 | 432 |
| 1302 | NTSC | Interlaced | 648 | 218,5 | 288 |
| 1303 | PAL | Progressiv | 1008 | 263,5 | 648 |
| 1304 | PAL | Interlaced | 1008 | 260,9 | 720 |

Root verifierade 160 källhashar, runtime, sex privata moduler, fem unika resultatrader/kvitton och 75 rå-/diagnostikfiler. Återgenererade original-/extended-kameraindata, prefix, CTL och faktisk standard/interlacing/kamerafält matchar råspåren. Tio verkliga fel i tillkomna bilder, fel bildord respektive källrad per frö, avvisas med väntade fynd och färre godkända rader; alla fem negativa bildfönster använder BUF.

Exakt resume körde noll nya frön och behöll raw/row/receipt byte-identiskt. Ändrat recovery-antal, checkerhash och revision vägrades före workerstart; faktisk råkorruption i en ägd kopia avvisades. [Rootacceptans](evidence/recovery-dense-round-1300-1304.json).

Första försöket startade trots att en extra CLI-startkontroll hade anropat parsern fel. Root avbröt endast den verifierade egna processgruppen och bevarade diagnostik och partiella rådata. Rättad sys.argv/parse_args-kontroll verifierade kontraktets samtliga körfält före försök två i ny output/tag/identity; returfel stoppar nu startsekvensen. Det avbrutna försöket accepteras inte. Samma fem frön, källor, parametrar och gränser behölls.

Den tidigare hundrafrögruppen med densitet 1 är separat accepterad. Detta paket accepterar fem nya scenarier med densitet 2,5, ingen fullständig grupp eller 260-frökampanj. Gamla 199 PASS/1 FAIL/60 ej körda bevaras. Core/Puck är oförändrade; ingen ny helsvit, FPGA-routning eller hårdvarumätning är körd.


### Recovery-runda 1305–1314 stoppad i rootgranskning, 2026-10-12

Alla tio native-körningar avslutade med PASS på fryst Core 2dca245, skalad geometri, densitet 2,5, tio originalfält och fyra recovery-fält. **Paketet är inte accepterat:** rootgranskningen stoppade vid frö 1309 när den skulle välja en tillkommen bild för de två negativa kontrollerna. Frön 1305–1308 har positiva modell-/invariantåterläsningar och åtta verkliga bildnegativer; återstående frön har ännu ingen full rootacceptans.

Frö 1309 ger 216 kontrollerade rader både med extended-sluttiden 26,064214 ms och med originalsluttiden 18,252122 ms på samma råspår. Den tillkomna delen ger alltså inga ytterligare kontrollerade bildrader. Fyra kompletta bildfönster före extended-sluttiden har LOW=1, source-alive=1, triggered=0 och video=0, utanför lägesbytesundantagen. Ingen är berättigad till en verklig bildnegativ. Den genererade mode-switch-händelsen finns vid pc473612; faktisk NTSC/interlaced och original-/recovery-metadata är hashbundna. Orsaken till den uteblivna LOW-triggern är ännu inte fastställd. Detta är ett täckningsfel i paketgrinden, inte ett konstaterat RTL-fel.

Rådata, simulator-/kompilatordiagnostik, första StopIteration-felloggen och ett separat källbundet triagekvitto är bevarade. Ingen seed, tröskel, timeout, källa eller checker ändrades och ingen HDL kördes om. Exakt resume och slutlig paketacceptans kördes inte efter felet. [Första avvikelsen och råspår](evidence/recovery-dense-round-1305-1314-failure.json). Fortsatt kampanj väntar på separat utredning av det faktiska LOW-trigger-/bildfönstret.

Core/Puck och tidigare accepterade paket är oförändrade. Gamla 199 PASS/1 FAIL/60 ej körda bevaras; ingen fullständig 260-frökampanj, ny helsvit, FPGA-routning eller hårdvarumätning är accepterad.


### Frö 1309: tidiga recovery-trigger under klippspärren, 2026-10-12

En separat läsning av samma råspår visar att de fyra recovery-triggerna kommer från LOW-skrivaren. De ligger ungefär 27,37, 20,65, 14,24 respektive 7,82 utrader efter bildstart, klart före vertikalsynk vid rad 73 även med åtta pixelklockors tidsmarginal. De är alltså tidiga trigger, inte uteblivna writer-händelser.

Spåret innehåller dessförinnan en klippt niolinjersbild, pc740892–755742. Den frysta `genlock_timing.v` sätter `hold=32` när ett tidigt klipp begärs och tillåter inget nytt tidigt klipp förrän hold är noll; räknaren minskar vid bildslut. Bara åtta senare bildstarter ryms i spåret. Källkod och händelser förklarar därför att återkommande tidiga trigger under spärren lämnar nya bilder utan `triggered`, trots levande källa. **Detta är en källbunden härledning:** själva pixel-domänens hold/early_n/pend/vc är inte loggade. En separat telemetry-probe med oförändrade standardregler kan bekräfta tillståndet direkt. Fyra recovery-fält garanterar inte att genlock hinner återlåsa efter ett tidigare klipp.

Inget RTL-, modell-, checker-, seed- eller tröskelbyte gjordes och ingen native-körning startades. Alla gamla 160 källinputs och fröets råhashar är identiska före/efter läsningen. Paketet 1305–1314 förblir **inte accepterat**. [Tids-/källanalys och upstream-diffar](evidence/seed1309-low-trigger-triage.json).

Fables parallella arbete hade samtidigt uppdaterat fjärr-main: Core 5314ed1 ändrar README, fyra testers byggkataloger och fyra kör-/revisionsverktyg; inga RTL-, modell-, fuzz-chain-, fuzz-campaign- eller tb_chain-filer skiljer mot 2dca245. Puck ecb9b14 ändrar endast gitlänken och pekar på Core f32407f, inte 5314ed1. Lokala Core/Puck-checkouter och fryst kampanjkälla flyttades inte. De externa rapporterna om 651/658 tester är inte lokalt verifierade här och ersätter inte våra tidigare källbundna grindar. Navets nya arbetsplan och ägarbeslutsunderlag har bevarats.

Första diffgranskningen antog felaktigt att Pucks senaste gitlänk redan pekade på Core main; kontrollen avvisade antagandet. Faktisk pin sparas separat i den rättade granskningen; ingen checkout eller gitlänk ändrades för att få likhet.


### Frö 1309: genlock-spärren direkt observerad, 2026-10-12

En separat native-probe med samma frysta Core 2dca245, exakt samma A/B/CTL och samtliga kompilatorparametrar lade endast passiv $fwrite-telemetri i en privat testbänkskopia. Ordinarie A/B/CTL/mix/sd/pix är alla sex byte-identiska med originalkörningen. Kompilator- och vvp-diagnostik är bevarade; inga RTL-, parameter-, checker- eller lägesregler ändrades.

Den interna genlock-spärren är nu observerad direkt: hold=32 vid det tidigare klippet. Vid de fyra recovery-triggerna är hold=27/26/25/24 och vertikalräknaren vc=27/20/14/7, före vertikalsynk vid 73. Alla fyra har lock=1 och jump=0; de tillkomna bildstarterna har triggered=0/video=0 trots alive=1. Detta bekräftar read-only-triagens orsak: fyra recovery-fält är kortare än den kvarvarande spärren efter ett tidigare klipp.

Oförändrad modell-/invariantåterläsning ger 216 kontrollerade rader utan fynd, known, edges eller notes. Ett faktiskt fel hold-värde respektive en felaktig triggerfas i ägda kopior av GT-spåret avvisas av samma telemetrifacit; originalet passerar före och efter. Samtliga 160 originalkällinputs, runtime, privat bänk/driver och originalråhashar är bundna och oförändrade. [Direkt telemetrikvitto](evidence/seed1309-telemetry-probe.json).

Acceptansen gäller enbart orsaksproben. Rundan 1305–1314 förblir ej accepterad och gamla kampanjens FAIL bevaras. Längre återhämtningsstimulus kräver ett nytt uttryckligt käll-/parameterkontrakt och en separat output med originalprefix och styrtider kvar; befintliga bildgränser och HOLD=32 ska inte sänkas. Ingen ny helsvit, routning eller hårdvarumätning är gjord.


### Frö 1309: ren prefix- och tidsbudgetkontroll, 2026-10-12

En modellkontroll prövade 4, 40 och 44 recovery-fält med samma frö 1309, skalad geometri, densitet 2,5 och tio originalfält. Alla behåller originalets A/B-bytes, byteklockor, starttider, kamerafält och styrhändelser. Bytedekodern verifierar samtliga suffixfält: 24 rena aktiva rader per fält och kanal, korrekt NTSC/interlaced-F, radlängd 1716, 1440 aktiva bytes och inga XY-/lumanivåfel. Ingen HDL kördes.

Den konservativa planeringsbudgeten använder hela HOLD=32, tre tidiga trigger och två kontrollerbara bilder, vardera högst (V_TOTAL+MAX_WAIT)*H_TOTAL*T_P. Den kräver 77,71665 ms extra källtid; det är en stimulusbudget, inte bevis på faktisk återlåsning.

| Recovery-fält | Extra källtid (ms) | Klarar budgetvakten |
|---|---:|---|
| 4 | 7,812092 | Nej |
| 40 | 77,526308 | Nej |
| 44 | 85,272332 | Ja |

44 är en deklarerad kandidat för ett separat framtida nativeprov med oförändrade 144-raderskrav, 3000 s timeout, HOLD och lägesregler. De första fyra recovery-fältens payload är identisk; deras tidigare 68-byte terminala blankningstrailer ersätts av nästa fält. Därför är hela gamla fyrfältsindatan inte ett prefix av 44-fältsindatan, medan originalets bytes och hela fyrfälts-payloaden förblir prefix. Nytt recovery-antal binds i ett nytt schema-2-kontrakt; gamla rådata återupptas inte med nytt antal.

Tre verkliga scenarioförvanskningar vägras: ändrat originalprefix, ändrad styrtid och otillräcklig källtidsbudget. Giltig kandidat passerar före/efter; gamla 160 källinputs, runtime och alla baseline-råhashar är oförändrade. [Ren prefix-/budgetacceptans](evidence/seed1309-recovery-window-pure.json). Den gamla rundan 1305–1314 är fortfarande ej accepterad. Ingen ny native-, helsvit-, routing- eller hårdvaruacceptans påstås.


### Frö 1309: separat 44-fältscenario native-accepterat, 2026-10-12

En ny, uttryckligt kontrakterad probe kördes via samma CLI-adapter på fryst Core 2dca245: frö 1309, skalad geometri, densitet 2,5, tio originalfält och 44 recovery-fält, utan tvingade störningar. Schema 2 binder det nya antalet och ny output/tag/identity; den gamla fyrfältsrundan kördes inte om eller ersattes. Native-tid 821,4 s; timeout 3000 s, geometrin, HOLD=32 och minimikravet 144 rader behölls.

Kompilering, vvp, drain och full modell-/invariantåterläsning passerade utan fynd, known, edges eller notes: **3 024 bildrader**, varav **2 808 nya rader i 39 kompletta LOW-video/triggered-bilder** efter gamla fyrfältsfönstrets sluttid 26,064214 ms. Samma nya råspår med originalsluttid eller fyrfälts-sluttid ger 216 kontrollerade rader; dessa jämförelser är inga separata native-körningar. Första nya berättigade LOW-bilden börjar vid pc2130192, cirka 28,544573 ms.

Den tidigare budgeten var konservativ och ingen garanti att hela spärren alltid måste löpa ut: `genlock_timing` tar en trigger i vertikalsynk/släckning även medan hold är positivt. HOLD spärrar ett nytt tidigt klipp. Proben visar den faktiska återhämtningen med längre, oförändrat prefixstimulus; den sänker inte spärren och ändrar inget bildläge.

Root verifierade 160 källhashar, runtime, sex adaptermoduler och 15 rå-/diagnostikfiler. Genererade A/B-bytes matchar den rena 44-fältskandidatens hash exakt, originalprefix/styrtider/klockor/kamerafält bevaras och faktisk NTSC/interlaced är bunden. Två verkliga fel i den första återhämtade bilden, bildord respektive källrad, avvisas med rätt LOW-predikat och 2 952 kvarvarande godkända rader.

Exakt resume körde noll nya frön och behöll raw/row/receipt byte-identiskt. Ändrat recovery-antal, checkerhash eller revision vägrades före workerstart; faktisk råkorruption i en ägd kopia avvisades. [Rootacceptans för det nya scenariot](evidence/seed1309-recovery44-native.json).

Detta accepterar enbart frö 1309 med 44 recovery-fält. Den gamla fyrfältsrundan 1305–1314 förblir ej accepterad och gamla 199 PASS/1 FAIL/60 ej körda bevaras. Ingen fullständig 260-frökampanj, ny helsvit, FPGA-routning eller hårdvarumätning är accepterad. Core/Puck-kod och gitlänkar ändrades inte i proben.


### Befintliga frön 1310–1314 slutgranskade separat, 2026-10-12

Efter frö 1309:s avvikelse återlästes de fem kvarvarande, redan körda fyrfältsråspåren i ett separat kontrakterat rootpaket. Inga nya simuleringar eller resume gjordes och inga resultat skrevs i den gamla native-katalogen. Alias till det ursprungliga native-kontraktet och dess returstatus är byte-identiska; ett separat scope binder exakt frön 1310–1314.

| Frö | Standard | Kamerakonvention | Kontrollerade rader | Negativt bildfönster |
|---|---|---|---:|---|
| 1310 | PAL | Interlaced | 1008 | BUF |
| 1311 | NTSC | Interlaced | 504 | BUF |
| 1312 | NTSC | Progressiv | 576 | LOW |
| 1313 | PAL | Progressiv | 1008 | BUF |
| 1314 | NTSC | Interlaced | 864 | BUF |

Full modell-/invariantåterläsning ger **3 960 bildrader** utan fynd, known, edges eller notes. Tio verkliga fel i tillkomna bilder, bildord respektive källrad per frö, avvisas med rätt BUF-/LOW-predikat och färre godkända rader. Alla 160 källinputs, runtime, sex adaptermoduler, nya scope-helperhashar och de 75 berörda rå-/diagnostikfilerna är granskade. Hela den gamla rundans raw/row/receipt/manifest-katalog behåller samma hash före och efter läsningen. [Separat rootacceptans för fem befintliga spår](evidence/remaining-1310-1314-replay.json).

Tillsammans med tidigare fyra rootgranskade frön är nio av tio fyrfältsfall nu slutgranskade. **Den gamla rundan 1305–1314 förblir ej accepterad på grund av 1309.** Det separat accepterade 44-fältsfallet ersätter inte detta FAIL. Ingen ny native-, helsvit-, routing- eller hårdvaruacceptans påstås.


### Svitköraren på Core 5314ed1: verifierad resume-lucka, 2026-10-12

Root granskade en isolerad Git-snapshot av Core 5314ed1: 185 spårade filer, exakt commit/tree/blob-hashar och oförändrade lokala Core/Puck-checkouter. De sju befintliga byggkatalog-/körar-fixturetesterna passerar direkt och via verklig CLI med `--jobs 1`; CLI-basen ger sju begärda test, sju resultat och returstatus 0. Detta är fixtureverifiering, ingen HDL eller helsvit på 658 test.

**UP-RUN-01:** på en ägd kopia av det giltiga resultatarkivet tömdes ett begärt tests `tests`-fält; källa, fingerprint, övriga sex utfall och alla ursprungliga loggar/tracefiler behölls. Verklig `--resume` accepterar ändå alla sju cacheenheter, startar noll nya enheter och ger returstatus 0. Slutrapporten säger **”7 tests: 6 passed”** och byggkatalogsvakten ser bara sex test. Den saknade begärda testidentiteten avvisas alltså inte.

Orsak: `unit_ok` kräver rc=0 och inga dåliga utfall men `all([])` godkänner ett tomt utfallsfält. Resume återanvänder cache efter unit-id utan att binda den till en komplett uppsättning begärda node-id/utfall; `finish` jämför inte slutresultatet mot varje begärt node-id. Root ska därför inte behandla exit 0 från den revisionens resume som fullständig testacceptans. [Exakt CLI-reproduktion och oförändrad bas](evidence/upstream-suite-runner-audit.json).

Sju fixturepass och katalogkollisionernas befintliga negativa kontroller står kvar. Den nya luckan är ännu inte rättad; council-grinden med minst 70 procent YES krävs före ett nytt fixpaket. Externa 651/658-svitrapporter är inte lokalt verifierade och inga produktionsfiler ändrades. Primära fuzz-checkouten, fryst 2dca245, de gamla kampanjrådata och tidigare accepterade paket är orörda.

## UP-RUN-01 council, 2026-10-12

Fyra av fyra röster godkänner ett avgränsat fel i Core5314ed1:s resume-grind: sju begärda test kan accepteras med endast sex lagrade utfall. Det skadade resultatarkivet är avsiktligt konstruerat; normal förekomst är inte visad. En separat rättning ska kontrollera testidentiteter och fullständighet före återanvändning och före slutlig acceptans. Ingen kodrättning eller ny helsvit ingår i rådet. [Röster, hashkontrakt och avgränsning](evidence/up-run-01-council.json).

## UP-RUN-01 rättat, 2026-10-12

Core main `ff9bfec` innehåller den granskade resume-rättningen efter rådets 4/4 YES. Cacheposter måste täcka exakt begärda testidentiteter; ändrat urval eller saknade/främmande utfall vägras före workerstart och resultatändring. Slutkontrollen kräver kompletta utfall eller uttryckligt väntande test, och en processfelkod fäller även skip/xfail-fall.

32 riktade test passerar på det slutliga kodträdet (25 nya). Verklig sjutest-CLI passerar och exakt resume startar noll nya workers. Tom och felmärkt cache vägras med alla arkivbytes orörda. Samma regression faller på den gamla köraren eftersom den returnerar 0. Inkommande Core `65ecf36` och navets arbetsplan är bevarade; dess byggpåståenden har inte rootverifierats här. Ingen ny helsvit, HDL, routning eller hårdvarumätning ingår. Puck-länken är ännu inte uppdaterad. [Kontroller, källidentitet och revisionskvitto](evidence/up-run-01-fix.json).

## Helsvit på fryst ff9bfec, 2026-10-12

**683 test passerar i 43 filer**, 427 seriella pytest-processer på 6 957,7 s. Root granskade samtliga begärda identiteter/utfall, 186 oförändrade Git-källfiler, runtime, 427 barnloggar och 19 cocotb XML-identiteter. Byggkatalogskontrollen såg 169 kataloger och 19 resultatfiler utan delning. Sju formella bevis och fjorton verkliga negativa motexempel verifierades i råloggarna. Tolv kontroller av skadade resultat-/XML-kopior avvisas av samma acceptansgrind.

Första privata XML-grinden krävde felaktigt att även den avsiktliga SDRAM-negativen skulle vara grön. `test_sdram_model_strict_stops` väntar på SystemExit från `model_strict_violation` med STRICT=1. En enda separat diagnostisk vvp-återläsning av samma kompilerade objekt visade tRCD-felet vid 200739456 ps och modellens STRICT-stopp. Modellen använder `$finish`, så vvp ger rc0 och cocotb rapporterar SimFailure; den första diagnostikscriptets rc1-antagande var också fel. Båda felloggarna är bevarade. Den korrigerade privata grinden kräver just denna källbundna negativa orsak/identitet; en grön negativ, fel orsak/identitet eller extra fel avvisas. De 18 vanliga XML-resultaten kräver fortsatt noll fel. Originalsviten kördes inte om och inga RTL-/checker-/stimulus-/tröskeländringar gjordes.

Detta accepterar **ff9bfec**, inte senare main med IOB-standard, kampanjrapport och nya bänkassertions. Ingen ny FPGA-routning eller hårdvarumätning ingår. [Källbundet slutkvitto och kontrollhashar](evidence/core-ff9bfec-full-suite.json).

## Källrevision av inkommande 0503dac, 2026-10-12

Root granskade fryst Core0503dac: 187 spårade inputs, 16 ändrade filer och en ny `margin_checks.vh` mot accepterad ff9bfec. Alla 683 tidigare testidentiteter är kvar; tolv tillkommer, totalt 695. **104 berörda modell-/byggfixture-/körartester passerar på 9,66 s.** Alla inputs och historiska källor är oförändrade efter granskningen.

Ny RTL/modellregel kräver att ord0 tagits i samma fält innan en rad markeras lagrad; fältraden som BUF-skrivaren ansluter mitt i blir inte lagrad. Bänkarna kontrollerar nu F/W/R-marginaler, med egna icke-vakuösa positiva och tre förseningsnegativer. Kampanjens källmanifest binder den nya include-filen; svitens fingerprint binder även BRINGUP som probtestet läser. Övriga tidigare fuzz-checkerfunktioner och samtliga körarfunktions-AST är oförändrade. Inga stift, SDC, toppar eller övrig RTL har ändrats mot ff9bfec.

Detta är källrevision och fokuserad fixtureverifiering. Den nya RTL-regeln behöver färska native-/hel-/bygggrindar; Fables 695-/kampanj-/byggrapporter är ännu inte rootaccepterade här. Nästa separat avgränsade grind är fryst0503dac, hela695 och färska M0/M4/M6 med IOB-val/TMDS/källmanifest. Puck-länken och historiska kampanjer är kvar. [Revision, nya identiteter och kvarvarande grindar](evidence/upstream-0503-source-audit.json).
