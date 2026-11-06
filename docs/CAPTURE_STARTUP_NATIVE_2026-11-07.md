# RTL-motexempel: första fältets radetiketter

Uppgift 77 bekräftar [modellfyndet från 76](CAPTURE_STARTUP_ROW_2026-11-06.md) i en faktisk Icarus-körning av oförändrad `cvbs_capture.v`. **243 radstarter i första fältet har en etikett ett lägre än källans aktiva radindex.** Felet spåras i [Core #34](https://github.com/LAP87/OpenVRX-Core/issues/34). Ingen producentfix har gjorts.

## Två separata kontroller

| Kontroll | Faktiskt utfall |
|---|---|
| Kompilering / VVP | Båda rc0; 0,012 / 30,014 s |
| Native mot sparad modell | Alla 351 252 entries bitidentiska |
| Oberoende källradskrav | **FAIL på 243 av 973 radstarter** |
| Wrapper | rc1, exakt `AssertionError: source_row_identity` |
| Timeout / signal / omkörning | Inga |

Detta är ett semantiskt motexempel, inte ett godkänt DUT. Modellöverensstämmelse ensam hade godkänt samma felaktiga radetiketter. En krasch eller ett kompileringsfel används inte som negativ kontroll.

Första utmatade F=1/rad=0 kommer vid testbänkens tillämpade sampelräknare 51220, under källrad 21 som har aktivt index 1. Den första källradens index 0 på rad 20 saknar en egen utmatad radstart. Följande 242 starter i samma fält är också ett index för låga. Därefter stämmer etiketterna:

| Källram / halva | Utmatat F | Radstarter | Etikett minus källans aktiva index |
|---|---|---|---|
| 0 / första | 1 | 243 | −1 |
| 0 / andra | 0 | 243 | 0 |
| 1 / första | 1 | 244 | 0 |
| 1 / andra | 0 | 243 | 0 |

Körningen ger 972 slutmarkörer. Sista källraden 1050 har skickat sina ord men hinner inte få slutmarkör. Det är inte samma sak som den uteblivna radstarten på rad 20. Ingen extra tidsförskjutning anpassades för ett bättre utfall; den första ordhändelsen måste ligga inom ACT_START±64 i sin källrad. Native-radstarternas loggade räknare ligger 4 eller 5 sampel efter modellens ordhändelser (429 respektive 544 rader). Det omfattar bänkens räknarkonvention och RTL-pipelinen, inte en uppmätt fysisk systemlatens.

## Exakt körfall

Fryst Core `031bba053943ee04ce303ae75b5e701746169c97`, tree `83734acc12ba3c4708a002fef3fd85abd9279fc5`. DUT och båda gain-tabellernas byte är också identiska med fjärrläst Core-main `a6e3c2b`. Det är källparitet, ingen färsk main-/top-/byggacceptans.

2 669 333 sparade 6-bitarskoder från 75/76 användes direkt, utan IQ-generering eller modellomkörning. SHA256:

`9b5f8fd7b7592e240c20fad0b794b267406fcee1327e03ad4ccdd58320b38412`

Kompilerade parametrar återlästes ur VVP: COMB=1, AVG=8, WHITE_X8=20, ACT_START=362, V_LINES=16 och BOOT_INIT=12. Originalets 40 MHz-klocka, fyra resetkanter, åtta tömningskanter och minne för 4 194 304 sampel behölls. Enda testbänksändringen är fdisplay av befintlig räknare `i` intill entryn. Inga port-, clock-, F-, gain- eller RTL-ändringar.

Icarus och VVP 12.0, Python 3.12.12. Två separat namngivna versionsprober följdes av exakt en kompilering och en simulering. Driver 31,727 s, alla 4 811 bindningar oförändrade. VVP:s readmemh-varning om oanvända delar av 4M-minnet är bevarad; det explicita antalet n=2669333 lästes klart och RESULT-raden rapporterar 351252 entries. Alla egna processidentiteter är avslutade.

## Oberoende återläsning och reproduktion

Rootgranskaren importerade ingen producentkod. Den verifierade varje hexsampel mot sparade kodbytes, parsade alla 53-bitarsutdata mot modellens binära entries, kontrollerade faktiskt kompilerade parametrar och räknade källradsetiketterna från råa tidsstämplar och H-geometri. 18 rå-/logg-/jobbmetadatafiler omfattar 24 583 630 byte; [JSON-kvittot](CAPTURE_STARTUP_NATIVE_2026-11-07.json) binder hash/storlek, mappning och runtime.

[Exakt körda hjälpare och tidsbänk](../research/experiments/capture_startup_native_2026-11-07/) är sparade. För en separat, godkänd reproduktion: kopiera experimentmappen till ny scratchkatalog, checka ut 031bba0 isolerat och återskapa kodpaketet med [76-observatören](../research/experiments/observe_capture_timing.py) och den publicerade 75-rapportens JSON. Kör runtime_probe med källkatalogen och scratch/RUNTIME.json. Kör sedan native_witness med källkatalog, observationspaket och ny output under ordinarie kvot-/gaming-/bygglåsgrind. Befintliga outputkataloger vägras. Kör inte om historiska jobb eller skriv över deras rådata.

Witness-hjälparen innehåller medvetet två olika krav: identitet mot den frysta, felande modellen och korrekt källradsetikett. Den är ett historiskt motexempel, inte ett färdigt acceptanstest efter en framtida modell-/RTL-fix.

## Nästa grind

Modellspåret visar varför detta händer: startslicern 12→13→14 missar den första 13-kodiga bredplatån, varpå V-armen hamnar på källrad 5 i stället för 4. Nedräkningen 16 ger då aktiv radstart 21. RTL-körningen bekräftar etikettförskjutningen; den är ingen fysisk mottagarmätning eller verifiering av andra nivåer, hot-relock, WHITE_X8=31 eller en integrerad M4/M6-top.

Före fix behövs ett uttryckligt startupkontrakt och tillämplig council-/ägargrind. En lösning får inte skriva om sparade etiketter, ändra F-policy i smyg eller bara dölja all video. Den måste ge korrekt identifierad användbar återhämtning och behålla tidigare beteenden enligt riktade tester, modell, faktiskt motexempel och färskt berört FPGA-bygge. Ingen fullsvit, route, Puck- eller hårdvaruacceptans ingår här.
