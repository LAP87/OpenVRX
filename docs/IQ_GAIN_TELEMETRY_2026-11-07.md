# Nytt seed2-fall: ingångskoder, gainföljning och utebliven bild

Uppgift 81, Core `031bba053943ee04ce303ae75b5e701746169c97` / tree `83734acc12ba3c4708a002fef3fd85abd9279fc5`. Ett nytt modellfall: seed2, C/N12 dB, 7+7 bitar, två NTSC-ramar/1050 rader. Faktisk IQ, demodulerade arrayer, ingångskoder och pixeltelemetri är nu sparade. Det fyller dataluckan för detta nya fall; gamla seed1-filer har inte återskapats eller ersatts.

## Samma sparade IQ, olika utfall

FS40MHz, deviation2,8MHz/V, kanal12MHz, video-LP4,2MHz. Den befintliga viktade heltals-PLL:n har oförändrade koefficienter och idealiserad fas-LUT. Båda demodulatorerna matades med en rekonstruktion av samma sparade heltals-IQ-par. SHA256 `ca8fc0ca6fe44363d1b464cdd53e60c7c00f2077f02a054aa423983b9f4b7ab1`, skild från gamla seed1. Totalt sparades 146 813 315 byte källarrayer före någon Capture-körning.

Capture är oförändrad: COMB1/AVG8/WHITE_X8=20/bootkontroll på. Nominalskalan är round(22+0,22×IRE), klippt till sex bitar. Källans samtliga arrayer var skrivna och hashbundna före de två separat startade första observationerna.

| Väg | Utmatade pixlar | Slutna rader | Strukturellt giltiga | Giltiga med ursprunglig RMSE<16 | Andel H-låst |
|---|---:|---:|---:|---:|---:|
| Fasdifferens | 119 520 | 166 | 164 | 0 | 92,86 % |
| Viktad PLL | 0 | 0 | 0 | 0 | 98,86 % |

PLL-processen avslutades normalt. Tom utmatning är resultatet, inte ett exekveringsfel. Den kördes inte om med andra inställningar. Ett högt H-lås säger uppenbarligen inte att Capture skickar ett videofält i detta modellfall. Vi har ännu inte fastställt varför PLL-fallet saknar bildrader.

## Direkt mappning jämfört med adaptiva nivåer

Passiva minnestaggar registrerar de faktiska insignalsampel som bidrar till varje utmatad pixel. Blank-, sync- och gainvärden sparas samtidigt. Originalets modellvärden och metoder är oförändrade. Root återläste float-till-kodkonverteringarna och pixelaritmetiken utan import av DUT eller primärorakel.

Vid exakt samma observerade sampeltider definieras två alternativa, fasta mappningar: brusiga koder respektive rena källkoder genom nominal blank22/sync13/gain1246. Gain är härledd ur originalets tabellformel, inte anpassad till resultatet. Båda använder samma ursprungliga tecken-/magnitudtrunkering och klippning.

- A = brusig fast mappning − ren fast mappning.
- B = faktisk adaptiv pixel − brusig fast mappning.
- Faktisk pixel − ren fast mappning = A+B.

Detta är en aritmetisk jämförelse vid observerade tider, inte en ny bildsanning eller en simulering av hur hela dekodern skulle bete sig med frysta nivåer. Kontrollerna, urvalet av rader och sampeltiderna kommer fortfarande från originalets adaptiva modell.

För fasdifferensvägens 52 480 pixlar i giltiga raders fasta stapelmitter:

| Term | Medel per pixel, Y-koder² |
|---|---:|
| A² | 937,484 |
| B² | 445,385 |
| 2AB | 50,546 |
| (A+B)² | 1433,415 |

Medelfelet A är +0,875 Y-koder och B +15,907. Summorna verifieras exakt i heltal: residual² = A²+B²+2AB. Här ökar den adaptiva mappningen residualen mot just denna nominella referens. Det bevisar inte att fast gain skulle återvinna fler rader eller vara rätt för en verklig C5-mottagare. B kan representera både avsedda och felaktiga nivåkorrektioner; korsledet får inte döljas eller göras om till oberoende orsaksandelar.

PLL-vägen har inga utmatade pixlar. Där är dessa pixelmått **inte tillgängliga**, inte perfekta nollfel. Känd startupavvikelse #34, källradidentitet, kontrolltiming, brusfri färg och fysisk RF/ADC/FPGA är inte godkända av denna jämförelse. Det ursprungliga kvalitetsprovet mot Y-staplarna står kvar separat och missas här.

## Körningar och bevarat förberedelsefel

Första nya hjälparen fick ValueError när tre CLI-argument packades upp i två variabler. Det skedde före outputkatalog, källimport eller datagenerering: rc1, 0,838 s, inga signaler. Originalhjälpare, kontrakt och logg bevaras. En separat bunden fortsättningshjälpare ändrar endast args-snittet från [1:] till [1:3] och slutförde det ännu inte startade arbetet; den ursprungliga hjälparen startades aldrig om. Källfasens återstående timeout begränsades till 59 s.

Den enda faktiska källgenereringen tog 4,676 s. Första fasdifferensobservationen tog 5,124 s och första PLL-observationen 4,365 s. Root 6,920 s och final 4,069 s, rc0. Ingen datagenerering eller observation upprepades. Sex ägda sourcebyte-/pixel-/gain-/korsleds-/native-/hårdvaruskador avvisades och samma kopior återlästes i final. Inga signaler eller timeout.

264 Git-/arkiv-/källfiler och 4809 befintliga bindningar oförändrade. Råinventeringen omfattar 44 filer/159 367 593 byte med hash och storlek. Python 3.12.12, faktisk venv-prefix, NumPy 2.5.3; inga installationer. [Maskinläsbar sammanfattning](IQ_GAIN_TELEMETRY_2026-11-07.json) och [exakta körda hjälpare](../research/experiments/iq_gain_telemetry_2026-11-07/) är publicerade.

Nästa konkreta fråga är varför H-låst PLL-video inte ger bildrader. Ett separat första tillståndsspår på de nu sparade koderna kan följa pulsbredd, V-arm och aktivnedräkning, med oförändrade bytes/utdata som grind. Det är ny observationstäckning, inte ett försök att få detta fall grönt. Ingen producentfix eller återstart av det stoppade rådet ingår.
