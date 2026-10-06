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
- **27 MHz-domänen i M6** når 64–69 MHz och har ett eget krav på 54 MHz. Den kritiska vägen är menyns frekvensräkning i `puck_ui.v`.
- **Testsviten tar längre tid:** 16 minuter i följd (5 minuter förut, med 52 test). Simuleringarna är oberoende av varandra; med tio åt gången tar sviten 5 minuter.
- **Mixerns gränsfall.** Rader som kommer inom några klockcykler från parningsfönstrets kant kan avgöras olika i RTL och modell. Testen håller sig borta från kanten.
- **Klockdomänsövergångarna i `fb_backend.v`** är fortfarande inte formellt bevisade.

## Andra passet, 2026-10-06

- **Lägesbyte `BUF`/`LOW` under drift är simulerat** (Core a6d23fd, test skrivet av en Sonnet-agent). Bildlängder, X/Z och SDRAM-protokoll är rena över båda bytena. Testet hittade ett fel: första bilden efter `LOW` → `BUF` visade ett sju fält gammalt fält. Två orsaker, båda rättade (Core 62a69be): `fb_display.v` behöll "har ett publicerat fält" från före `LOW`, och `fb_sdram.v` publicerade det halva fält skrivaren gick med i, vars saknade rader lästes rått ur bufferten. Nu släpps det fältet utan publicering (gäller även vid start) och publicerade fält glöms medan `LOW` är aktivt. Modell, händelselogg och M2-testet följer. Negativa kontroller: utan vardera delen faller testet.
- **I/O-register i I/O-cellerna** (Core-gren `exp/ioreg-in-iob`, Sonnet-agent): `IOREG=1` i `build.sh`, alla nio toppar byggda med och utan. Inga timingfel, LUT4 oförändrat, DFF 1–2 % färre, HDMI-paren packas som M0. I M2a hamnar alla 32 DQ-ingångsregister i I/O-cellerna, men DQ-utdata, utgångsaktiveringen, DQM och SDRAM-klockan ligger kvar i logiken; orsaken är inte utredd (gissning: ett register driver alla 32 stift). Rekommendation: inför för M2a, övriga SDRAM-toppar efter att minnestestet har körts på kortet med och utan. Ägarens beslut.
- **Rev A** (Puck 828976c–bdb99d1, 17cdbea): PTC 0,75 A hållström (#2 stängt), I-klassad dekoder (livscykeln inte kontrollerad), 4,7 µF efter PLL_AVDD-ferriterna, probjord vid 27 MHz-headrarna, 47/27 ohm beskrivet. Kvar i #3: ESD-klamp efter delaren, firmware-patch (kräver flerbyteskrivning i `i2c_master.v`).
- **README-tabellen** i Core hade siffror från placeringen; `build.sh` skriver nu tabellen efter routning (Codex) och tabellen byggs om med den.
- Issues uppdaterade, se "Läge".

## Återstår ur granskningen

- **Rev A-kortet** (Puck #2–#3): PTC, temperaturklass, PLL-filter, ESD-klamp efter delaren, jordstift, 47/27 ohm på ingången. RESETB-flytten är gjord (Puck #1). SKiDL finns i Core-miljön i WSL; Puck-testet går där.
- **Ägarens beslut**, se sist.

## Nästa steg

Ordnade efter nytta mot insats. De tre första går att göra utan hårdvara.

1. **I/O-register i I/O-cellerna.** Experimentet är gjort (se "Andra passet"); kvar är beslutet, och att ta reda på varför DQ-utgångarna inte hamnar i cellerna.
2. **Ett bildläge i stället för två.** Fältminnet visar redan fältet som skrivs. Med genlockad tidsbas och bildstart några rader efter fältstart ger samma väg ungefär `LOW`:s latens (uppskattat 0,2 ms överst, 0,9 ms nederst), med täckning av saknade rader och utan ringbuffertens 16-radersgräns. Då försvinner en specialväg, och omlåsning kan ske utan skräp i bilden eftersom fältminnet faller tillbaka på senaste hela fält. Nackdel: `LOW` blir beroende av SDRAM. Ägarens val.
3. **Svänghjulstidbas** (dekoderunderlaget, avsnitt 5). Rader placeras efter ankomsttid mot en egen rad- och fälträknare. Fältfasen ur ankomsttid och genlockens fönster är första stegen dit. Fortsättningen behöver mätvärden först: hur mycket dekoderns radtider skakar vid svag signal, och vad den gör när den tappar H-låset.
4. **Dekoderinställningar.** Lås videostandarden (28h) och TV/VCR-läget (02h) lika på båda. Använd den klibbiga biten "lost lock" (88h bit 4) som underlag för mixern först när den har loggats på riktig signal; i simulering går det inte att veta om den hjälper eller stjälper.
5. **Kvalitetsmått som inte beror på bilden.** Räkna lumasampel utanför 16–235 per rad (kräver ingen hårdvara) och logga det bredvid snövärdet. Om klick syns där kan måttet ta över från HF-energin, och blandningen kan viktas efter brus (RF-underlaget, avsnitt 2 och 3).
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

- Ska grenarna bli pull requests mot `main`? De är pushade men inte sammanslagna.
- Ett bildläge i stället för två (punkt 2 ovan).
- I/O-register i I/O-cellerna: för M2a nu, övriga efter mätning (gren `exp/ioreg-in-iob`).
- Inköpsregeln i AGENTS.md mot priser och butikslänkar i Puck och i äldre anteckningar i `research/` (hub #2).
- Licensstycket i `docs/GATEWARE_PLAN.md`, och upphovsnotisen i `sdram_burst.v` (hub #2).
- Rev A: övriga schemaändringar (Puck #2–#3).
