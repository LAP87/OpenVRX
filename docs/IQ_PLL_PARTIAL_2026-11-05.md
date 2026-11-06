# IQ-PLL: första modellförsöket, 2026-11-05

Uppgift 74 / Core #28 är delvis genomförd och inte godkänd. Den nya privata heltalsmodellen jämfördes med ursprunglig fasdifferens på samma hashbundna IQ-indata. Core-bas `a6e3c2bb473ef18442ac32a06e81c9bbb615029c`. Ingen RTL ändrades.

FS 40 MHz, 60 rader, seed 1, deviation 2,8 MHz/V, kanal 12 MHz, video-LP 4,2 MHz. PLL: kp 3/8, ki 1/32, effekt-IIR 1/256, amplitudvikt högst 2. Fasdetektorns atan2-LUT är idealiserad; loopens steg använder heltal. Ingen efterhandsjustering av tidsläge. Ursprungliga SNR- och synkmått behölls.

| IQ-bitar/axel | C/N dB | SNR fasdifferens | SNR viktad PLL | Synkträffar fasdifferens | Synkträffar PLL |
|---|---|---|---|---|---|
| 4 | 4 | 5.62 | 9.33 | 0.000 | 0.000 |
| 4 | 8 | 10.59 | 12.93 | 0.034 | 0.017 |
| 4 | 12 | 14.78 | 16.31 | 0.186 | 0.085 |
| 7 | 4 | 5.15 | 9.92 | 0.000 | 0.000 |
| 7 | 8 | 11.34 | 13.68 | 0.068 | 0.034 |
| 7 | 12 | 15.65 | 17.44 | 0.305 | 0.068 |

Matrisen avslutades rc0 på 3,462 s med oförändrade bundna indata. Bättre luma-SNR är inte tillräckligt: kravet på minst lika bra synkträffar missades vid 8 och 12 dB för båda bitdjupen. Vid 4 dB var båda metoderna utan synkträffar. Det visar ingen mottagarkänslighet eller fungerande RF-kedja.

Riktad verifiering: 8 PASS och 2 FAIL på 1,37 s pytest (1,742 s driver). De sex ursprungliga IQ-testerna och två nya egenskaper passerade. Båda riktningarna i det nya fasramptestet missade gränsen TURN/10000: medelabsolutfel cirka 814 302 mot gränsen 429 497 i fasinkrementets heltalsenheter. Testet av fel looptecken nåddes därför inte; någon godkänd semantisk negativ kontroll påstås inte.

Originalkod, kontrakt, XML och loggar är bevarade privat i `private/notes/dev_2026-11-05/iq-results/`. Oberoende återläsning kontrollerade de båda jobbens hashbindningar och exakt tio XML-utfall. Inga signaler eller omkörningar. Ingen quick/fullsvit, Core-commit, Core-mainmerge eller hårdvaruacceptans.

Nästa motiverade steg är att granska fasrampens kvantiseringsfel och loopens tidsläge, innan ett separat experiment övervägs. Koefficienter och felgränser har inte ändrats efter utfallen. Detta är en sparad begränsning, inte en färdig PLL-leverans.

## Fortsättning 2026-11-06

Fasrampens medelfrekvensfel är 0 i båda riktningarna över det fasta slutliga 512-sampelfönstret. En separat oinlindad flyttalsrekursion av samma ekvationer avviker högst 1,414 heltalsfasenheter från heltalsloopen. Axlar avrundade till heltal på cirkelradie 100 tillåter redan ett fasfel asin(sqrt(0,5)/100), cirka 4 833 577 fasenheter. Det var inte motiverat att kräva momentant inkrementfel under 429 497. Den gamla felande testfilen och resultaten bevaras; inga loopkoefficienter eller videopredikat har ändrats.

De nya testerna skiljer medelfrekvens från rippel. En härledd absolut impulssumma för LUT-avrundning samt frekvens- och proportionalavrundning ger en felbudget 6,8444, konservativt mindre än 7 fasenheter mot flyttalsekvationerna. **12 riktade tester passerar på 1,53 s**, inklusive de sex ursprungliga IQ-testerna. Det är modellverifiering, inte uppfyllt synkmål.

Synkdiagnostiken behåller originalets ±3 sampel: en ren flank hittas vid+1 med båda metoderna. I brusfallet 4 bitar/CN 12 har PLL:n 20 av 59 sökfönster låga redan vid−40 sampel. Det visar tidiga passager, inte en fast extra latens eller en etablerad fysisk felorsak. Fel looptecken försämrar faktiskt bildmåtten:16,313 till 4,836 dB SNR och 5/59 till 0/59 synkträffar. Ett senare diagnostikutkast misslyckades vid JSON-export av ett komplext egenvärde, sparade inget resultat och används inte som bevis; det kördes inte om.

Snabbsviten avbröts när Baldur's Gate 3 startade. SIGTERM gick enbart till den egna sviten efter kontroll av PID, processgrupp, startticks och kommando; svitens städning avslutade arbetarna. Alla sparade egna processidentiteter var sedan borta och bygglåset ledigt. **43 begärda tester PASS;677 tester i 415 processer återstår**, rc 3. 4 792 käll-/runtime-/hjälparbindningar var oförändrade. Ingen Core-commit eller PR har publicerats: snabbsviten är ännu inte klar.

Nästa start måste invänta att gamingpausen upphör och använda färsk kvotkontroll. Fortsätt endast svitens sparade pending-lista med originalets fingerprintgrind; kör inte om de 43 klara testerna. Ett framtida separat modellspår kan jämföra samma IQ-strömmar genom den befintliga pulsbredds- och periodföljande kompositdekodern. Det får inte ersätta eller skriva över det missade slicermålet i #28.

## Publicerad modellgren 2026-11-06

[Core draft PR #32](https://github.com/LAP87/OpenVRX-Core/pull/32), commit `81a448c4a464de7c7c90a2b035ee4e226925911a`, innehåller modellen, testerna och rapporten `docs/IQ_PLL_2026-11-06.*`. Synkmålet är fortfarande inte uppfyllt; #28 hålls öppet och fasdifferens är kvar som standard.

Den förberedda återupptagningen slutfördes efter att spelet avslutats: **720 begärda PASS i 458 testenheter**. De 43 tidigare kvittona återanvändes exakt, endast 415 återstående enheter kördes i en ny identisk källkopia. Driver 89,841 s, rc 0; alla 5 191 bundna käll-/runtime-/hjälpar-/rådatafiler oförändrade. Originalets avbrutna byggfiler, loggar och spår är orörda. De 12 riktade testen passerar separat; de räknas inte som extra utfall i snabbsvitens 720.

Slutgranskningen kontrollerade exakt utfallsidentitet, oförändrade ursprungliga IQ-definitioner och testfil, negativ orsak samt faktisk Gitblob/arkiv/källidentitet för commitens 259 filer. Fullsvit, Core-mainmerge, FPGA och hårdvara ingår inte. Ett experiment är avslutat och redovisat; önskad synkförbättring är ännu inte löst.
