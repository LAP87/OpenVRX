# Brusfallen: bildstruktur finns kvar i medel, men pixelfelet är stort

Uppgift 80 är en läsning av de 17 sparade modellfallen i uppgift 75, Core `031bba053943ee04ce303ae75b5e701746169c97`. Ingen IQ, kodström eller video genererades om. Inga mottagarmodeller, pytestsviter, RTL- eller hårdvarujobb kördes. Analysen ger ny diagnostik; tidigare resultat står kvar: ingen brusig rad klarade både strukturen och den frysta pixelbudgeten RMSE <16.

## Nytt mått

Var och en av de åtta ursprungliga gråstaplarna är 90 pixlar bred. Vi läser dess mittersta 40 pixlar, position 25–64, utan förskjutningssökning, offsetborttagning eller gainanpassning. Histogram, p10/p50/p90, medel och fel mot stapelvärdet 16+31×stapel sparas för alla slutna rader och separat för strukturellt giltiga slutna rader. Tomma urval redovisas som tomma. De räknas inte som perfekta svarta rader.

Tabellen visar det senare urvalet. Ideala medelvärden är 16, 47, 78, 109, 140, 171, 202, 233.

| Fall | Giltiga rader | Medelvärden i de åtta stapelmitterna |
|---|---:|---|
| Ren fasdifferens, 7 bitar | 972 | 16,0 / 45,0 / 74,3 / 105,4 / 135,4 / 167,4 / 197,3 / 229,3 |
| C/N12 fasdifferens, 7 bitar | 134 | 32,2 / 59,0 / 89,6 / 119,4 / 149,9 / 181,6 / 210,2 / 232,1 |
| C/N12 viktad PLL, 7 bitar | 50 | 28,9 / 58,8 / 91,5 / 124,4 / 157,7 / 190,7 / 220,8 / 241,6 |

Alla sju medelsteg är stigande i dessa tre fall. Det betyder att staplarnas horisontella struktur finns kvar i genomsnitt över de rader som överlevde. Det betyder inte att en viss rad är rätt placerad, skarp eller flygbar. Vid C/N12 är RMSE i de brusiga stapelmitterna fortfarande cirka 33–44 Y-koder för fasdifferens och 21–37 för PLL. Medelkurvan döljer en stor spridning.

## Var ligger spridningen?

Efter första profilläsningen definierades en ytterligare diagnostik före sin första beräkning: exakt uppdelning av medelkvadratfelet i variation inom varje rad, variation mellan radernas medelvärden och kvadrerad global avvikelse mot stapelsanningen. Heltalsmoment och rationella tal verifierar identiteten utan avrundningsrest. Inget av dragen används för att korrigera bilden eller ändra ett godkännandekrav.

| C/N12, 7 bitar | Inom rader | Mellan radmedel | Global medelavvikelse |
|---|---:|---:|---:|
| Fasdifferens, 134 giltiga rader | 62,25 % | 30,89 % | 6,86 % |
| Viktad PLL, 50 giltiga rader | 67,92 % | 9,60 % | 22,48 % |

Andelarna gäller summan av felet i de åtta fasta stapelmitterna. Variation inom en rad är inte automatiskt vitt brus: timing, filtrering eller andra strukturerade fel kan också bidra. Resultatet motiverar att nästa experiment följer enskilda sampel och nivå-/synktillstånd, snarare än att bara ändra en global kontrast.

## Lås och ändkoder räcker inte som bildmått

I uppgift 75:s metadata har C/N12-fasdifferens/7 bitar 82 förekomster av kod 0 eller 63 bland 2 669 333 kodsampel, cirka 30,72 ppm. PLL-fallet har 9, cirka 3,37 ppm. De sparade låsspåren ger låst andel 87,75 respektive 93,24 procent, samtidigt som bara 134 respektive 50 slutna rader är strukturellt giltiga.

Detta är återlästa metadata, inte en ny mätning av kodströmmarna. Kod 0/63 kan också vara naturliga ändvärden; räknarna identifierar inte varje trunkeringshändelse. En låg total andel kan inte utesluta att enstaka händelser stör nivåföljning eller synk. Låsflaggan avser inte ett godkänt helt återvunnet videofält.

De brusiga IQ- och ingångskodbyten sparades inte i de fyra ursprungliga paketen, endast deras hashvärden. Utmatade ord saknar emissionstidsstämplar. Därför kan den här läsningen inte koppla en viss felpixel till en viss ingångskod, låshändelse eller verklig källrad. Överlevande rader är ett selekterat urval, inte ett mått på hela mottagarens känslighet.

## Verifiering och nästa avgränsning

Första analysen tog 0,728 s, root 0,639 s, båda rc0. Samtliga gamla parserantal och fullraders kvadratsummor matchar originalkvittona. En separat läsare, utan import av primärläsare eller DUT, räknade samma profiler och den exakta feluppdelningen. Sex ägda skador avvisades: en rå pixelbyte, ett histogrambin, främmande nod samt falska orsaks-, native- och hårdvarupåståenden. Originalet är giltigt före/efter; final läser samma kopior.

264 Git-/arkiv-/källfiler och 480 befintliga bindningar oförändrade. Råinventeringen omfattar 37 original-/analys-/kontrollfiler, 22 887 944 byte, med hash och storlek. Inga signaler, timeout, fel eller retries. Python 3.12.12 med faktisk venv-prefix, enbart stdlib.

[Maskinläsbara profiler](IQ_NOISY_PIXEL_PROFILES_2026-11-07.json) och [exakt primärläsare](../research/experiments/iq_noisy_profiles_2026-11-07/) finns sparade. Ett eventuellt nytt separat experiment behöver spara faktisk IQ, ingångskoder och tidsatta pixel-/nivåtillstånd från början. Det får inte återskapa de gamla fallen och kalla de nya byten originalbevis. Ingen orsak, producentfix, förbättrad bild, FPGA eller hårdvara godkänns här.
