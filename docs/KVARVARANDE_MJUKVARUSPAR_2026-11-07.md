# Kvarvarande mjukvaruspår

Kontrollerat 2026-11-07 mot faktiska fjärrhuvuden: Core `a6e3c2bb473ef18442ac32a06e81c9bbb615029c`, navet `592283f6623f79c4e55a2bccb12cd348542c4258`, Puck `0d09424741ff518a3769935ea79a6bb73b007f72`. Core har fyra öppna frågor, #27–29 och #34, samt modellförslagen PR #30–33. Detta är ett urval från dessa källor och sparade experiment, inte en global inventering av varje möjlig funktion. Inga nya tester eller simuleringar kördes för denna genomgång.

## Prioritering

1. **Korrekt uppstart i kompositdekodern.** [Core #34](https://github.com/LAP87/OpenVRX-Core/issues/34) har ett faktiskt RTL-motexempel: första fältets 243 radstarter får en för låg etikett. Modell och RTL gör samma fel. Nästa steg är att granska det konkreta korrigeringsförslaget, därefter separat implementation med rätt källrad som oberoende facit. Läs [native-resultatet](CAPTURE_STARTUP_NATIVE_2026-11-07.md). Att bara köra om sviten ger ingen ny täckning.

2. **Spåra varje pixels ursprung genom bildkedjan.** Uppgift 75 använder samma gråstaplar på alla rader och ramar; dess pixelmått kan därför missa en gammal eller felplacerad rad. Uppgift 76–77 lade till tidsbaserad radidentifiering, men verifierar inte varje pixels ursprung genom exempelvis 1H-kammen. Ett nytt syntetiskt mönster som varierar med rad och fält kan skilja legitim kamfiltrering från fel rad, dubbling eller en bild som hängt kvar. Facit måste härledas från källmönster och avsedd filterfunktion. Negativer: fel radfördröjning, dubblerad rad och gammalt fält. Detta är ett nytt testkontrakt, inte en omkörning av gråstaplarna.

3. **Förklara varför den brusiga IQ-kedjan inte återvinner bilden.** I [PR #33](https://github.com/LAP87/OpenVRX-Core/pull/33) klarade ingen rad både struktur och fryst pixelbudget vid C/N 4, 8 eller 12 dB. [PLL-försöket](IQ_PLL_PARTIAL_2026-11-05.md) förbättrade luma-SNR men försämrade synkmåttet. Nästa nyttiga arbete är en avgränsad orsakskontroll av befintliga rådata: var tappar nivåval, pulskvalificering och radposition kontakten med källan? Ändra inte koefficienter eller gränser för att få grönt. Ny simulering först om analysen ger en prövbar hypotes.

4. **Avgör vad sexbitars färg faktiskt kan återge.** [Core #27](https://github.com/LAP87/OpenVRX-Core/issues/27) och [PR #31](https://github.com/LAP87/OpenVRX-Core/pull/31) lämnar kvalitetsfrågan öppen vid de uppmätta C5-nivåerna. Ett distinkt modellförsök kan separera klippning, kvantisering och avkodarfel med känd färgsanning, samma analoga syntessignal före kvantiseringen och oförändrade felmått. Målet är ett ärligt kvalitetsgolv och en konkret felorsak; en syntetisk nivåjustering är inte bevis för att C5-firmware eller radion kan leverera den skalan.

5. **Återlåsning och formatbyten efter stabil bild.** Den nya IQ/Capture-kedjan har kontrollerats med två NTSC-ramar, inte med avbruten signal, byte av nivåskala eller PAL/NTSC-övergångar i samma ström. En framtida kontroll ska mäta sista korrekta rad, svart/gammalt innehåll under avbrottet och första korrekt identifierade återvunna bild. Fastställ först vad oförändrad Capture faktiskt stöder; PAL-färg är en separat funktion och får inte antas ingå. Gör detta efter startupkontraktet, så att samma fel inte utreds två gånger.

## Rådet för uppgift 78 stoppade före första rösten

Det första externa anropet till den förvalda DeepSeek-granskaren misslyckades. Den lokala budgetklientens ledgerpost 3048 klassificerar felet som `quota_exhausted`; arbetaren sparade `A0Error`, ingen ballot. Driver rc 1 på 0,971 s, inga signaler. Vid återläsningen var samtliga 4 812 bundna käll-, runtime- och hjälparfiler oförändrade.

Den förbestämda stoppregeln gäller: Mercury startades inte, ingen retry eller annan modell/provider användes. Root avstod från ballot efter driftstoppet. **0/3 YES; designen är inte godkänd.** Detta är ett driftstopp, inte ett sakligt nej till förslaget. Ingen modell-/RTL-/produktionsfix har gjorts. Ett nytt råd får inte startas automatiskt för att kringgå stoppet.

## Vad som behöver bänken

Verklig mottagarkänslighet, färgkvalitet från kameran, breadboardens signalintegritet, fysisk HDMI-latens och två mottagares verkliga diversityvinst kräver mätningar. Ovanstående modeller kan ge bättre hypoteser och fånga logikfel; de fastställer inte dessa egenskaper.
