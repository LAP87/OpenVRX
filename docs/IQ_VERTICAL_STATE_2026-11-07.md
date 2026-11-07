# H-låst PLL-video utan bild: ingen bredpuls blir godkänd radpuls

Uppgift 82 följer de exakta sparade PLL-koderna från seed2/CN12/7+7bit i uppgift81. En ny passiv tillståndsobservation utvärderade oförändrad Capture en gång. Ingen IQ eller kodström genererades om. Det är ytterligare observationstäckning på samma indata, inte en andra variant för ett bättre bildutfall. Core `031bba053943ee04ce303ae75b5e701746169c97`, COMB1/AVG8/WHITE_X8=20/ursprunglig bootkontroll.

## Verifierad kedja i just detta modellfall

1. Slicern ger 3332 avslutade låg-pulser efter originalets tre-låg/tre-hög-avstudsning. Bara två når 600 sampel; längst 827.
2. Ingen av dessa två pulser matchar pulsstarten som H-följningen har accepterat för aktuell eller väntande rad.
3. Därför kvalificeras ingen bredpuls för den nuvarande radens `_line_class_update`. Ingen V-arm sker.
4. Aktivnedräkningen förblir −1 genom 1050 ACT_CHECK-utvärderingar. `numbered` och `cur_active` förblir falska, och ingen bildrad matas ut.

Detta förklarar den tomma utmatningen trots 98,86 % H-låst tid i uppgift81. Det fastställer varken ett hårdvarufel eller att varje mottagare med brus beter sig så.

| När bredden når 600 | Rå pulsstart | Accepterad aktuell radpuls | Väntande radpuls | Skillnad mellan starter |
|---:|---:|---:|---|---:|
| sampel 678108 | 677509 | 676243 | ingen | +1266 sampel |
| sampel 679771 | 679172 | 678735 | ingen | +437 sampel |

Den första skillnaden ligger nära en halv rad. En tillräckligt lång rå puls räcker alltså inte: [step](https://github.com/LAP87/OpenVRX-Core/blob/031bba053943ee04ce303ae75b5e701746169c97/gateware/model/cvbs_capture_ref.py) kopplar klassningen till `cur_edge` eller `pend_edge`, och en väntande klassning armar inte V. I de två faktiska händelserna är båda kopplingarna falska. `seen_normal` är sant, så den senare återarmeringsgrinden är inte vad som stoppar just dessa pulser.

Den sparade syntetiska källans IRE-array innehåller 24 bredpulsfönster. I 22 av dem når ingen överlappande detekterad puls600. Denna uppdelning avser originalets adaptiva slicer och tidslägen, inte en hypotetisk fast tröskel. Spåret visar hur pulserna klassas och varför V-grinden aldrig öppnar; det isolerar inte demodulatorns, filtrets och den adaptiva nivåföljningens samtliga bidrag till fragmenteringen.

## Oberoende återläsning

Observatören ersätter inga metoder och skriver inga producenttillstånd. Den loggar 29 tillståndsfält vid 9300 händelser: pulsstart/slut, tröskelpassager, radstart, nivåändringar och aktivkontroller. Både tomma entry-bytes och låshändelsen `[30516,true]` är identiska med uppgift81.

Root återskapar slicerns registrerade åttasampelsumma från kodbyten och de loggade nivåändringarna. En separat tre-låg/tre-hög-parser återger samtliga 3332 pulsstart-, slut- och breddvärden. Vertikalvillkoren kontrolleras från de loggade tillståndsövergångarna och den frysta källans regler. Ingen Capture eller IQ-modell körs i återläsningen.

Åtta ägda skador avvisades: fel pulsbredd, fabricerad V-arm, ändrad nedräkning, falsk utmatningsekvivalens, flyttad låshändelse, falsk generell orsak samt native-/hårdvarupåståenden. Samma kopior återlästes i final. Dessa är rådata-/metadatakontroller, inte nya RTL-motexempel.

## Bevarade hjälparfel

Modellobservationens wrapper avslutades rc1 efter att alla data sparats. Dess sista kontroll jämförde modellens lista av tupler med JSON:s lista av listor. Den rapporterade därför felaktigt att låsspåren skilde sig, trots identiska händelsevärden. Originalhjälpare, kontrakt, logg och falsk flagga är orörda. En separat bunden rootfortsättning läser endast befintliga JSON-/råfiler och verifierar exakt tidsindex och booleskt låsvärde; en avsiktligt flyttad låshändelse avvisas. Modellen kördes inte om för detta.

Ett separat förberedande runtimeuppslag antog att `array` hade `__file__`. Modulen är inbyggd i aktuell Python. Felet och den trunkerade verktygsdiagnosens begränsning sparades före första rootjobbet; inget rootjobb behövde köras om.

Den enda modellobservationen tog 6,228 s, inga signaler eller timeout. Root 1,893 s/final 0,494 s, rc0. 264 Git-/arkiv-/källfiler och 471 befintliga bindningar oförändrade. Råinventering 31 filer/39 070 187 byte med hash och storlek. Python 3.12.12, faktisk venv-prefix, enbart stdlib; ingen installation.

[Maskinläsbart tillståndsresultat](IQ_VERTICAL_STATE_2026-11-07.json) och [exakta observer-/rootkällor](../research/experiments/iq_vertical_state_2026-11-07/) är sparade. Fyndet gäller detta oförändrade modellfall. Ingen producentfix, oberoende RTL-reproduktion, bättre bild, fysisk känslighet eller hårdvara godkänns. Det stoppade designrådet återstartades inte.

Ett möjligt nästa separat experiment är att pröva modellens befintliga längre slicermedelvärde på samma sparade koder. Det måste vara en fördefinierad första parameterkontroll, behålla pixelkraven och redovisa både utebliven förbättring och eventuell extra fördröjning; ingen automatisk parametersökning eller defaultändring.
