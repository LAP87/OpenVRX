# Arbetsplan efter granskningen 2026-10-05

Underlag: [reviews/2026-10-05/ADVERSARIAL_REVIEW.md](reviews/2026-10-05/ADVERSARIAL_REVIEW.md). Fynden ligger som issues; index i LAP87/OpenVRX#3. Den här planen säger i vilken ordning de åtgärdas, hur varje åtgärd ska vara konstruerad och hur den räknas som klar.

## Status

| Fas | Innehåll | Issues | Läge |
|---|---|---|---|
| 0 | Issues och plan | hub #3 | klar |
| 1 | Radnumrering från V-biten | Core #4 | se "Utfört" |
| 2 | Mixern: parning, hälsa, radordning, test | Core #1 #2 #3 #5 | se "Utfört" |
| 3 | Uppstart och stift | Core #6 #8 #9 #12, Puck #1 | se "Utfört" |
| 4 | SDRAM | Core #7 | se "Utfört" |
| 5 | Utgångsvägen | Core #10 #11 #15 #16 | se "Utfört" |
| 6 | Smått | Core #13 #14, hub #2, Puck #2–#4 | se "Utfört" |
| 7 | Alternativa vägar (forskning) | hub #1 | se "Utfört" |
| 8 | Mätningar när kortet finns | alla | väntar på hårdvara |

Avsnittet "Utfört" sist i dokumentet fylls i efter varje arbetspass, med commit och testläge.

## Arbetssätt

- Grenar: Core `fix/review-2026-10-05` (delspåren `fix/sdram-capture` och `fix/bringup-pins` slås ihop dit), navet och Puck `review-2026-10-05`. En commit per åtgärd.
- Varje RTL-ändring får en simulering mot modell och en negativ kontroll (AGENTS.md). Test som visar felet skrivs först och ska fallera på koden före ändringen.
- Ett tungt jobb i taget (place-and-route). Simuleringar får gå parallellt.
- Siffror märks "simulerat", "byggt" eller "mätt på hårdvara". Inget i den här planen är mätt på hårdvara.

## Fas 1. Radnumrering från V-biten (Core #4)

Rad 0 är första radstart efter vertikalsläckning: minst två giltiga synkord i följd med V = 1 sedan förra radstarten. F-biten används inte för numreringen. Register 15h lämnas orört, så att fast F betyder två lika fält.

Klart när: `bt656_rx.v` är bitexakt mot `model/bt656.py` på alla vektorer, inklusive en ny med fast F; mixern parar en sådan källa även när dekodrarna startat på olika rader.

## Fas 2. Mixern (Core #1, #2, #3, #5)

### Krav

1. En rad från en kanal som är `bad` visas inte om den andra kanalen levererar en bra rad för samma läge.
2. Radnumren i utströmmen stiger strikt inom ett fält. Fältgränser går att se på F-bit eller radnummer.
3. Är en kanal död, olåst eller ur takt är utströmmen den andra kanalens rader, alla, i ordning.
4. Är båda friska och i takt gäller dagens regel per rad (blanda, byt med hysteres), bitexakt mot modellen.
5. Inget beslut beror på hur lång vertikalsläckningen är.

### Konstruktion

- **Parning.** Två rader paras om de har samma radnummer och kom inom `T_PAIR` (1 024 cykler, 15,8 µs) från varandra. F-biten ingår inte i parningen. En rad vars partner inte kommit inom `T_PAIR` avgörs ensam. Äldst rad först.
- **I takt.** `in_step` sätts av varje parad rad och släcks efter `N_STEP` (8) ensamma rader i följd.
- **Ensam rad från aktuell kanal** visas om den ligger i ordning.
- **Ensam rad från den andra kanalen** visas bara som lucktätning: kanalerna är i takt, raden är bra, den aktuella kanalen har ingen rad som kom före radens tidsgräns, och raden ligger i ordning.
- **Byte av aktuell kanal utan parning.** (a) Hälsa: den aktuella kanalens åtta senaste rader är alla dåliga och den andras åtta senaste alla bra. (b) Tystnad: den aktuella kanalen har inte levererat något på `N_STEP` av den andras rader om kanalerna var i takt när den tystnade, annars `N_DEAD` (40, längre än en släckning). Tvingat läge från menyn går samma väg, eftersom det gör den andra kanalens rader dåliga.
- **Radordning.** Mixern håller reda på senast utsläppta rad och på vilket fält varje kanal är i (en fälträknare per kanal, som stegas när kanalens radnummer börjar om). En rad släpps ut om den börjar ett nytt fält eller har högre nummer än den senaste. Utströmmens F-bit låses vid fältets första rad.
- **Väntetid.** Är den andra kanalen tyst sedan `N_DEAD` rader avgörs rader utan att vänta på `T_PAIR`.
- **Ringbufferten.** En rad som delvis tappats för att ringen var full sparas inte. `overflow` förs ut i loggen.
- `alive` finns kvar som lysdiodssignal men styr inget.

Regeln för parade rader (`decide_pair`) ändras inte, så jämförelsen mot flyttalsprototypen i `mixer/` gäller fortfarande.

### Test

- `model/line_mixer_ref.py` får tid som indata och modellerar allt ovan.
- `sim/test_mixer.py` kör fält med minst 20 släckrader. Scenarier: frisk och i takt; tappad rad; trasigt synkord; kanal som tystnar; olåst kanal i takt; olåst kanal ur takt (halvt fält, 2, 5 och 12 rader); olåst kanal som är aktuell vid start; F-bit som skiljer mellan kanalerna; fast F.
- Invarianterna 1–3 som slumptest över fasläge mellan kanalerna, på RTL:ens utström.
- Negativ kontroll: de nya testen körs mot mixern före ändringen och ska fallera.

Klart när: alla test ovan går igenom, RTL och modell ger samma beslut och ord i de scenarier som inte ligger på en tidsgräns, och körningarna E1–E5 i granskningen ger noll rader från den olåsta kanalen.

## Fas 3. Uppstart och stift (Core #6, #8, #9, #12; Puck #1)

Beslut:
- RESETB flyttas från stift 25 till stift 18 (J6-18, bank 6). M3/M4/M6 får tre lysdioder (15–17). Inga vanliga utgångar i bank 4 och 5 i byggen med TMDS.
- Lysdioder: M3 hjärtslag, SCLK A, SCLK B. M4/M6 hjärtslag (1 Hz låst, 4 Hz olåst), rader A, rader B.
- M4 får samma RX5808-styrning som M3.
- Kanalen skrivs 0,5 s efter reset och sedan varannan sekund så länge ingen dekoder är låst, aldrig när någon är låst. SPI-DATA vilar hög.
- `tvp_ctrl` läser tillbaka 03h vid pollningen och gör om init om värdet är fel. `dev_err` släcks vid nästa kvitterade transaktion. 15h skrivs inte.
- SECAM maskas ur autoswitchen om databladet stöder det.
- Statusexempel, modellvärden och BRINGUP rättas efter databladets tabeller.
- Pull-testet lämnar `d[7]` orörd.
- Vakttest: inga utgångar på stift 25–42 i TMDS-byggen, och en fuse-jämförelse med stift 25 som negativ kontroll.

Klart när: M3, M4 och M6 bygger, TMDS-klockparets IOB-fuses i M4 och M6 är lika med M0:s, och testsviten går igenom.

Puck: rev A-skriptet, netlistan, BOM:en och stiftkontrollen ändras tillsammans med nästa bump av Core-submodulen (Puck #1). Kräver SKiDL och görs inte i det här passet.

## Fas 4. SDRAM (Core #7)

- Klockfas 225° och NESTangs tider (2/2/6) om inte en hämtningsgräns bryts.
- Modellen får riktig lästiming (tAC, tOH) och uttalade antaganden för de två kortfördröjningarna, med negativa kontroller för varje regel.
- Läspunkten blir valbar under drift.
- Ny toppmodul `m2a_memtest`: skriver och läser hela minnet, räknar fel per DQ-bit och per plats i bursten för varje läspunkt, skriver en rad per pass över UART.

Klart när: minnestestet i simulering hittar rätt läspunkt både med antagna fördröjningar och med noll fördröjning, och M2 och M2a bygger.

## Fas 5. Utgångsvägen (Core #10, #11, #15, #16)

I den här ordningen, eftersom varje steg bygger på det förra:

1. **Fjärde bufferten (#11).** Skrivaren undantar senast publicerad, näst senast publicerad och den som den tror visas. Klart när invarianten "bufferten som skrivs visas inte" håller i E7b.
2. **Ett radantal för båda fälten (#15).** Det minsta av de två senaste fältens radantal används för alla bilder.
3. **Fältförskjutning (#15).** Det nedre fältet (F = 1 med BT.656:s V-lägen) läggs en halv källrad lägre. Ingen förskjutning när F inte växlar. Polariteten är en parameter tills den är mätt på hårdvara.
4. **Följsam buffring (#16).** BUF visar fältet som skrivs när skrivaren ligger tillräckligt före vid bildstart (2 rader för NTSC, 40 för PAL in i 60 Hz), annars senaste hela fält. Standardtiming ut. Väntad latens 0,1–17 ms i stället för 17–34 ms.
5. **Genlock-fönster (#10).** Låst generator tar bara `trig` i ett fönster kring väntad bildstart, och låser om först efter flera triggrar i följd på ny fas. Formellt bevis för undre gräns på bildlängden, med negativ kontroll.

## Fas 6. Smått

- `snowlog.py` på Windows (Core #13).
- README-hänvisningar och två formuleringar (Core #14).
- AGENTS.md: uppstartsordning och "bit-exact" (hub #2). Inköpsregeln och licensstycket kräver ägarens beslut.
- EMI-tabellen: mellanfrekvensens övertoner (Puck #4).
- Rev A: PTC, temperaturklass, PLL-filter, ESD, jordstift (Puck #2, #3). Görs med nästa schemavarv.

## Fas 7. Alternativa vägar

Tre underlag skrivs i `research/` (2026-10-05):
- dekoder och synk: hur kommersiella mottagare håller bilden stilla, andra dekoderkretsar, direkt digitalisering, tidbaskorrektion;
- utgång och latens: vad XR-glasögon och bryggor tar emot, 1080p-vägar, deinterlacing;
- RF: mottagarkretsar, diversity, kvalitetsmått, egenstörning.

Förslag som kommit ur granskningen och ska prövas mot underlagen:
- **Svänghjul.** En intern rad- och fälträknare i FPGA:n som låser långsamt till den friskare dekodern. Varje rad placeras efter ankomsttid mot svänghjulet i stället för efter dekoderns eget radnummer. Då kan en dekoder med fel radnummer men rätt radtiming fortfarande bidra, och bilden hoppar inte när en dekoder tappar V-låset.
- **Döljning.** En rad som är dålig i båda kanalerna skrivs inte, så att förra fältets rad står kvar.
- **Snabbare låsbesked.** Låsbitarna pollas var 20:e ms. En avbrottssignal från dekodern eller tätare pollning kortar tiden en olåst kanal kan visas.
- **Fältmedel av HF-energin** som mått när raderna inte går att para.

## Fas 8. När kortet finns

I den här ordningen. Varje rad är en mätning som simuleringen inte kan ersätta.

| Steg | Mätning | Avgör |
|---|---|---|
| M0 | Bild på tre skärmar | HDMI-nivåer, klockparets tålighet |
| M2a | Minnestest, alla läspunkter | SDRAM-fas och läspunkt (Core #7) |
| M3 | Proben med båda dekodrarna | Kablage, `fld` med den egna kameran (sammanflätad eller inte) |
| M3 | Dra ur videon till en dekoder | Om TVP5150 fortsätter leverera rader utan signal, och med vilken timing (antagande i Core #2) |
| M4 | Antenn av, en mottagare i taget | Mixerns byte, tid till byte |
| M4 | Skriv om samma kanal med bild på | Om omskrivning stör bilden (Core #8) |
| M4 | Stillbild med vågräta kanter | Fältförskjutningens polaritet (Core #15) |
| M6 | LOW mot HDMI-skärm, brygga och XR-glasögon | 750/751 rader (hub #1) |
| M6 | Snö-mätaren med dekoderkort och HDMI av/på | Egenstörning, även mellanfrekvensen (Puck #4) |

## Beslut som är ägarens

- Ska grenarna pushas och bli pull requests?
- Inköpsregeln i AGENTS.md mot priser och butikslänkar i Puck och `research/` (hub #2).
- Licensstycket i `docs/GATEWARE_PLAN.md` (hub #2).
- Rev A: RESETB på J6-18 och övriga schemaändringar (Puck #1–#3).

## Utfört

Fylls i efter varje pass.
