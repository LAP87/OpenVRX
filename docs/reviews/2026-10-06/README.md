# Granskning och fortsättning 2026-10-06

Fables granskade bas är nu utgångspunkten på `main` i Core, Puck och navet. Codex fortsätter därifrån med byggverktyg och testinfrastruktur. Opus tre nattgrenar är fortsatt separata. Inget har körts på hårdvara.

Tre reproducerade funktionsfel behöver rättas före tillit till bildens innehåll: en ofullständig aktiv rad släpps igenom, en misslyckad statusläsning döljs och en saknad första rad saknar giltig reservkälla. De beskrivs nedan med kontroller och accepteringsvillkor. Ingen av dessa RTL-rättningar görs i detta pass.

## Vilka versioner granskades

| Repo / spår | Commit | Roll i granskningen |
|---|---|---|
| Core `fix/review-2026-10-05` | `e5585bab98343fa2289d7a8165752b1e7206b54a` | Fables bas; hela sviten och felreproduktionerna |
| Puck `review-2026-10-05` | `17cdbea713c32d0b44e4fb410eb9900eb82760ac` | 114-delars schema; pekade vid start på Core `f02a98e5d3ebd75ae69dee32170db89d806b5cad` |
| Nav `review-2026-10-05` | `1c57184372ad869073b15911c69896bd4a64afd9` | Arbetsplan och nattuppdrag |
| Core `feat/noise-metric` | `a6640b003fc950e9cb89eed8d06dd72712a6da38` | Riktade brus-, UI- och loggtester |
| Core `feat/i2c-multibyte` | `013300aba631d7d85da1c3af2d8d12d87f2fa05c` | Riktade master- och dekoderstyrtester |
| Core `formal/fb-backend-cdc` | `53e5ab2da0002ee19d4b8160f46590e6628b1c3f` | Formellt test och oberoende reproduktion av dokumenterad hålltid |
| Core `exp/ioreg-in-iob` | `215ee5ecb43beb6559156d6c5125121d9e88ea1b` | Läst experiment; äldre bas, ingen ny verifiering av dess byggen |
| Core `main` efter detta pass | `6a61a17647fe47d483c7bac53a6437e869ed589d` | Fables bas plus två avgränsade infrastrukturcommits |

Fables urval bevaras: dagens gren är ingen återimport av hela morgonens Codex-gren. De lokala `main`-grenarna kunde flyttas fram utan mergekonflikt; deras tidigare lägen finns kvar i Git-historiken. Opus funktioner är inte inlagda i denna Core-version.

Puck pekade fem Core-commits före Fables bas. Detta pass uppdaterar gitlänken till `6a61a17`, så en rekursiv klon får både den senare BUF/LOW-rättningen och de nya byggverktygen. Kortets schema, stiftplan och genererade konstruktionsfiler ändras inte av Codex.

## Vad dagens arbete faktiskt gav

Fables bas innehåller bland annat fyrbuffrat fältminne, ändrad radkö/mixer, en minsta bildperiod i genlock, återinitiering av dekodern och SDRAM-minnestest. Genlock-rättningen har en oberoende positiv kontroll: efter reset blir bildperioderna 168, 168, 168 och 266 cykler i den skalade testbänken, aldrig under den låsta minimigränsen 154. Det tidigare korta bildintervallet reproduceras inte i denna bas.

Nattuppdraget i [NATTPASS_2026-10-06.md](../../NATTPASS_2026-10-06.md) äger brusmåttet, flerbytes-I²C och CDC-bevisen. Codex valde därför byggartefakter och långa testsökvägar:

- `e6bf0a9`: testbänkarna för probe och top-stift använder SystemVerilog-strängar för vektorsökvägar och avbryter vid oläsbar fil. Python-testerna använder alltid sökvägar över 128 byte som regression.
- `6a61a17`: byggskriptet kompilerar en fryst kopia av RTL, headers, top och stiftfil. Manifestet anger commit, smutsig arbetskopia, verktygsversioner, alternativ, SHA-256 för indata och artefakter samt slutlig timing per klocka.
- Varje byggförsök får en egen stagingmapp. Tidigare publicerade artefakter flyttas undan innan verktygen körs. Nextpnr-`ERROR`, missad timing, tomma utdata och ändrade indata stoppar publicering. Bitströmmen publiceras sist; ett misslyckat försök lämnar ingen bitström på den kanoniska flash-sökvägen. Diagnostik och eventuella delutdata kan finnas kvar i stagingmappen.
- Variantnamnet används konsekvent för bitström, loggar och manifest. Ett `flock` serialiserar verktygskörningarna för samma byggmapp.

24 nya avgränsade tester använder verktygsdubblar för misslyckad syntes/routing/packning, fel som trots allt ger exit 0, gamla eller tomma artefakter, variantnamn och källändringar. En kontroll ändrar och återställer en källfil under bygget: det kompilerade innehållet måste ändå vara den frysta kopian. En avsiktligt felaktig variant som kompilerar från arbetskopian fälls av samma kontroll.

En extern A0-granskning av byggändringen föreslog detta sista fall; observationen kontrollerades lokalt innan rättningen accepterades. En separat A0-läsning av fältminnet tog slut i svarslängd och används inte som bevis för någon punkt nedan.

## Ny verifiering i detta pass

Alla tunga jobb kördes ett i taget. [evidence/](evidence/) innehåller små loggar, versionsögonblicksbild och byggmanifest.

| Kontroll | Nytt resultat | Praktisk gräns |
|---|---|---|
| Hela Core-sviten vid `e5585ba` | 280 gröna, 4 fel; 32 min 56 s | Samtliga fyra fel kom från trunkerad vektorsökväg i probe/top-testbänkarna |
| Probe/top efter sökvägsrättningen | 5 gröna; 2 min 17 s | Inkluderar de fyra tidigare fallen, med lång sökväg |
| Byggartefakter + befintlig pull-kontroll | 25 gröna; 3,62 s | 24 nya tester och den tidigare kontrollen |
| Testinsamling på Core `main` | 308 insamlade | Ingen ny sammanhängande körning av alla 308 påstås |
| Brusgrenen | 9 gröna | `test_noise_stats.py`, `test_puck_ui.py`, `test_snowlog.py`; inte hela grenens svit |
| Flerbytes-I²C-grenen | 12 gröna | `test_i2c_master.py`, `test_tvp_ctrl.py`; inte hela grenens svit |
| Formal-grenen | 1 grönt | `test_formal.py` kör bevis och negativa kontroller; integrationsvillkoren återstår |
| Puck mot uppdaterad Core-gitlänk | 1 grönt, inklusive negativa kontraktskontroller | Stift- och signalrollskontrakt, inga fysiska prov |
| Ny isolerad Puck-export | 114 delar, 83 nät, ERC 0 fel/0 varningar | Designkontroller gröna; saknade footprintbibliotek och netlistans rottagg ger separata generatorvarningar |

De första fyra Core-felen var testinfrastruktur, inte ett belagt RTL-fel: den isolerade vektorsökvägen var 141 byte, men testbänkarna hade 128 byte stora register. Icarus försökte läsa en fil med de första 13 byte bortskurna. Rättningen ändrar inga produktionsmoduler eller deras förväntade stiftbeteende.

Två riktiga byggen vid ren Core `6a61a17` passerade syntes, routing, slutlig timing, packning och manifestverifiering:

| Byggvariant | Slutlig Fmax / krav | Bitströmmens SHA-256 |
|---|---|---|
| `m0_testpattern` | pixel 146,41 / 75 MHz; 27-MHz-domän 350,75 / 75 MHz | `63ff3c7ee2f7e4114eaba826a728e0b412c16826c696cc93d773621cd2635c44` |
| `m2a_memtest_phase12` | SDRAM 82,93 / 75 MHz | `6dff3616c7c120abdcbd9908dcc48dbed488ececf29c6a1570f921c2b6a04711` |

Verktyg: Apicula 0.32, yowasp-nextpnr-himbaechel-gowin 0.11.1.0.post826 och yowasp-yosys 0.69.0.0.post1233. Fas 12 verifierar också variantens filnamn; lämplig SDRAM-fas för det verkliga kortet väljs med minnestest på bänken. De andra milstolparnas publicerade P&R-tal är Fables tidigare resultat, inte nya byggen från detta pass.

## F1: ofullständig aktiv rad godkänns och gammal svans visas

Källa: Core `gateware/rtl/chan_capture.v:18–36` och `mix_chan.v:67–69,115–149` vid `e5585ba`. `chan_capture` har `rec_active`, men skickar det inte i markören. `mix_chan` godkänner radens EAV-längd/status utan att kräva 360 sammanhängande payloadord.

Reproduktionen använder den riktiga kedjan BT.656 → capture → radkö. Fyra hela rader fyller och återanvänder ringens platser. På femte raden kommer SAV fyra byte sent; EAV-avståndet är fortfarande 1716 och XY är felfritt. Den aktiva delen blir 1436 byte, alltså 359 ord. Resultat:

```text
MARKER n=4 words=359 length=1716 xy_bad=0 active=1436
ROW n=4 count=1 bad=0 overflow=0 tail=20802080
```

Den femte raden blir tillgänglig som frisk och dess sista ord kommer från första raden. Ingen FIFO-overflow behövs för detta fall. Morgonens `1a1e5c7` avvisar samma ofullständiga rad (`count=0`); de fyra hela positiva kontrollerna godkänns i båda versionerna. Detta är en syntetiskt störd videosignal, inte ett uppmätt kamera- eller RF-fel.

Åtgärd: ge radpublicering ett fullständighetsvillkor, exempelvis sammanhängande ordindex plus aktiv längd. Acceptera först när hela rader passerar, sena SAV/förkortad aktiv del och saknat/dubbelt ord inte kan publicera gammal data, och den negativa kontrollen med borttagen fullständighetskontroll fälls. Återför inte en hel äldre mixer bara för denna rättning.

## F2: ett status-NACK döljs av nästa lyckade transaktion

Källa: Core `gateware/rtl/tvp_ctrl.v:115–129`. `dev_err[di]` skrivs om efter varje transaktion. Ett NACK vid 88h lämnar gammal status; ACK vid 89h sätter `status_valid`, och nästa lyckade läsning kan åter nolla `dev_err`.

Testet kör den riktiga styr-FSM:en med en deterministisk completion-stub för I²C. Först görs en hel lyckad poll. Nästa poll får NACK på 88h och ACK på 89h/03h:

```text
POSITIVE status_valid=1 dev_err=0 status=000e
AFTER_NACK88 status_valid=1 dev_err=0 status=000e
```

Toppen kan därför fortsätta tolka äldre låsstatus som giltig efter en ofullständig poll. Stubben prövar styrlogikens hantering av avslutade transaktioner; den simulerar inte ett elektriskt I²C-fel.

Åtgärd: samla hela pollens status och fel innan resultat publiceras. Testa NACK på 88h, 89h och 03h var för sig, återhämtning vid nästa hela poll samt återinitiering. Ett senare ACK får inte göra den misslyckade pollen giltig. Flerbytesgrenen ändrar inte denna styrlogik.

## F3: saknad första rad kan läsas från oskrivet minne

Källa: Core `gateware/rtl/fb_sdram.v:251–261`. När raden saknar markering, ingen tidigare giltig bild finns och ingen tidigare hämtad rad finns (`rep_v=0`), väljer sista `else` ändå `show_buf` och den saknade raden.

Reproduktionen använder `fb_backend` och repots beteendemodell för SDRAM, fem skalade 12-radersfält och bara `(fält 1, rad 0)` borttagen. En senare bild har `have_video=1`, men de första line-buffer-orden är X. Det händer både med `RT_EN=0` och standardvärdet `RT_EN=1`. Alla SDRAM-protokollkontroller är gröna. Samma följd med alla rader närvarande ger noll sådana bilder.

Referensmodellen delar reservpolicyn; den vanliga replay-kontrollen hoppar över innehållskontrollen när `stored is None`. Att RTL och modell överensstämmer täcker därför inte detta fall. Observationen gäller okända bildord i line-buffer med aktiv video, inte en mätning av HDMI-pixlar på en skärm.

Åtgärd: välj en definierad giltig reservrad/svart rad, eller håll video avstängd tills en användbar rad finns. Lägg till oberoende kontroll av innehållets giltighet utöver modelljämförelsen. Prova borttagen rad 0 i första och senare publicerade fält, bägge realtidslägena, och en negativ kontroll som åter tillåter läsningen.

## Två kända öppna integrationspunkter

**LOW-payload över klockdomäner.** `fb_backend.v` kan ändra `s_ll_lines` efter triggern men innan pixeldomänen tar emot värdet. Den formella grenen dokumenterar redan buggen och förutsätter att payload hålls minst 16 SDRAM-cykler. I den oberoende skalade reproduktionen skickas hela rader i ett 3-radersfält följt av ett 2-radersfält; nästa fält börjar direkt efter line-1-triggern. Både basen och formal-grenen skickar 3 men tar emot 2. En positiv kontroll med 20 SDRAM-cyklers paus tar emot 3. Detta visar RTL-händelsens felaktiga payload; ingen metastabilitetsmodell används. Villkorade bevis för primitiver gör inte integrationen färdig.

**I²C utan timeout.** Om SCL hålls låg stannar den riktiga `i2c_master` fortfarande med `busy=1` och noll avslut efter 2000 testcykler. Samma start med frigiven SCL slutför en NACK-transaktion. Koden har inget timeout-/avbrottsvillkor för permanent stretching. Det kan stoppa den delade styrvägen tills linjen släpps eller reset ges. Flerbytesfunktionen löser inte återhämtningen.

## Kort, komponenter och hårdvarugränser

Industrivarianten i schemat, TVP5150AM1IPBSR, anges som Active på [TI:s sida för det exakta artikelnumret](https://www.ti.com/quality-reliability-packaging-download/es-mx/report?opn=TVP5150AM1IPBSR). [Databladets beställningstabell](https://www.ti.com/lit/gpn/tvp5150am1) anger TQFP-32 och −40…85 °C. Pucks livscykeldokument är uppdaterat med denna kontroll; småvolymstillgång och övriga BOM-raders status har inte kontrollerats om i detta pass.

Layout, exakta PTC-delar/footprints, ESD-kedja och fysisk signalintegritet återstår. IOREG-experimentet flyttar DQ-ingångsregister till IOB men är baserat före senare BUF/LOW-rättningar; hela grenen ska inte läggas över dagens bas. DQ-utgång/OE/DQM/klockans placering och faktisk SDRAM-marginal måste fortfarande bedömas.

Projektägaren har Eachine Moneagle och har beställt Tang Nano 20K samt analog kamera/VTX-kort. Kortrevision, kamerans/VTX:ens modell och matningskrav är ännu okända. Fortsatt bring-up är M0 → probe → SDRAM-minnestest → en dekoder → två dekodrar. Inga inköp eller kortbeställningar görs utifrån denna granskning.

## Nästa avgränsade pass

| Prioritet | Ägda filer / ansvar | Godkännande innan nästa steg |
|---|---|---|
| 1: radfullständighet | `chan_capture.v`, `mix_chan.v`, motsvarande mixer-/capturetester och modell | F1 avvisas; hela rader och ringomlopp fungerar; borttagen kontroll fälls |
| 2: giltig första rad | `fb_sdram.v`, `fb_ref.py`, `test_fb.py` | F3 ger definierat innehåll eller inaktiv video i båda lägen; modell och oberoende giltighetskontroll passerar |
| 3: atomär statuspoll | `tvp_ctrl.v`, `test_tvp_ctrl.py` | Varje enskild register-NACK avvisar pollen; nästa hela poll återhämtar; återinitiering rensar giltighet |
| 4: nattgrensintegration | Brus, flerbytes-I²C, formal – en gren åt gången | Först samordning med Opus; sedan relevanta modell-/negativtester, gemensam UART-formatkontroll och uppdaterat testantal |
| 5: CDC-hålltid och I²C-återhämtning | Samordnas med nattgrenarnas ansvariga | Faktisk avsändare uppfyller CDC-villkoret; fastlåst SCL lämnar ett definierat fel-/återhämtningsläge |

Tabellen är återstående arbete, inte fler ändringar utförda av Codex. Gör ett RTL-paket i taget, spara testutfall och commit efter varje accepterat paket. Misslyckad acceptans lämnar den tidigare accepterade commiten som återgångspunkt.

## Köra om felreproduktionerna

[repro/README.md](repro/README.md) beskriver körningen. Runnern hämtar källfiler från angiven Git-commit till en separat lokal mapp och ändrar ingen checkout. Exit 0 betyder att de dokumenterade felen och positiva kontrollerna reproducerades; det är inte ett funktionsgodkännande. Ett ändrat resultat efter en rättning kräver nya accepteringskontroller.

De två nya Core-commitsens diff omfattar bara byggverktyg, dokumentation och testinfrastruktur. `gateware/rtl`, `gateware/top` och `gateware/boards` är oförändrade jämfört med Fables `e5585ba`.
