# LOW → BUF: video före publicerat fält

Codex/root, 2026-10-08. **Simulerat, inte hårdvarumätt.** Fynd OVN-F1.
Ingen RTL-rättning eller ändring av lägesregler görs i detta paket.

## Vad som är belagt

Frö 126, skalad geometri, density 2,5 och 10 kamerafält, kördes med Core
`7cc4eda`-RTL. LOW aktiveras efter cirka 9,14 ms och BUF efter 15,79 ms.
BUF-bytet kommer på pixelklocka 1178661, efter visningens provtagning på
den sista släckraden (1178141), före nästa aktiva bild (1179791).
`have_video` behåller då LOW-värdet trots att `have_pub` är noll i BUF.

Den strikta fältminneskontrollen rapporterar en läsning av buffert 0,
rad 5: checksumma `db82d583`, medan SDRAM-facitet vid lässtart är
`6a4f29aa`. Läshändelsen ligger mellan 16,487 och 16,551 ms och före
den första BUF-bildens fältminnesbeslut. Bristen på ett sådant beslut
innebär alltså inte att bildens RGB är blank.

En separat bänkkopia lade enbart till observation av `ll_p`,
`have_video`, `have_pub` och RGB vid x=300 på varje aktiv rad. Kamera-
och kontrollfilerna är byte-identiska med den första uppspelningen.
Alla 72 provtagna aktiva rader har RGB skild från blankvärdet `404040`.
I bildens början är läget BUF, video på och inget fält publicerat.
Senare blir `have_pub` ett; samma bild innehåller därför båda tillstånden.
Råvärden, källhashar och kontrolltider finns i
[transition-probe-126.json](evidence/transition-probe-126.json).

## Granskningsbeslut

Grenändringen `3ad2c2b` kopplade checksumfel till ett efterföljande
bildbeslut och gjorde en oanknuten läsning till en anteckning.
På dessa råloggar försvinner felet då. Antagandet att bilden saknar
video är motbevisat av observationskörningen. Kontroll av varje SDRAM-
läsning behålls, även när inget bildbeslut hunnit komma. Ett litet
negativt test matar en felaktig checksumma före första bildbeslutet och
kräver `store/read`.

Opus sammanfogade nattgrenen till fjärrens `main` `0e0bf49` medan den
lokala PAL-verifieringen körde. Codex granskar därför integrationen mot
den revisionen och återinför den strikta läskontrollen som en avgränsad
korrigering. Senare kampanjresultat från Opus har andra orakelversioner;
de utgör inte verifiering med denna kontroll.

## Avgränsat nästa rättningspaket

Ägare utses före arbete. Första läsytor är `rtl/fb_display.v` och
`rtl/fb_backend.v`; eventuell lagringsändring avgränsas separat till
`rtl/fb_sdram.v` och `model/fb_ref.py`. Tester/bänk ägs av samma paket:
`sim/test_fb.py`, `sim/tb_fb.v` och den riktade kedjereproduktionen.

1. Beskriv befintligt kontrakt för LOW → BUF: video saknas fram till ett
   helt, efter bytet publicerat BUF-fält. Ta ställning till bild som redan
   pågår vid själva bytet utan att ändra andra lägesregler.
2. Bygg ett litet deterministiskt scenario som placerar bytet mellan sista
   släckradens provtagning och första aktiva raden. Jämför grindstatus,
   RGB, fältval och läsningar med modellen; bevara frö 126 som integration.
3. Rätta bara den verifierade fasluckan. Svep bytesögonblick på båda
   sidor om släckrad/aktiv bild samt synkfördröjningarnas gränser.
4. Negativ kontroll ska återinföra gammal grindlogik och falla på synlig
   bild före publicering. Varken checksumkontroll, täckningsgräns eller
   bytesfönster får försvagas för att passera.
5. Kör berörda framebuffer-/kedjetester, modellkontroller och färska
   M4/M6-byggen under det gemensamma låset. Granska manifest och stift-
   kontroll. Först därefter commit/push med käll- och körproveniens.

Återupptagning: läs denna fil, `STATUS.md`, `COORDINATION.md` och evidence;
kontrollera andra arbetare innan filer tas. Återanvänd inte en gammal
fuzz-round med ändrade källor. Råloggarna finns på denna värd under
`OpenVRX-Core/gateware/sim/build/fuzz/overnight-transition-probe-126-20261008`
och R03:s sparade workkatalog. Ingen hårdvara har verifierat fyndet.

## Omspelning på Fables bas, 2026-10-09

`e113cf6`-RTL/modell med C1:s strikta checker (`8a9b3fcc…`) kördes som
separat hybriddiagnostik: seed 126, scaled, density 2,5, 10 fält. Kamera-
och kontrollfiler är byte-identiska med det historiska scenariot. Källor
är oförändrade före/efter körningen.

Den fulla uppspelningen rapporterar fortfarande `store/read`: rad (0, 5),
checksumma `db82d583` mot `6a4f29aa` vid lässtart. Den rapporterar också
`output/xz` på pixelklocka 882791. Uppspelningen är alltså underkänd;
fynden får inte döljas genom undantag för läsning utan bildbeslut.

Den separata pixelobservationen i det gamla LOW→BUF-fönstret ger ett annat
utfall än `7cc4eda`: alla 72 prov har `have_video=0` och RGB `202020`.
De första 45 ligger före BUF-publicering. Detta överensstämmer med den
frysta källans gråvärde och visar att just denna synliga faslucka inte
återkommer i `e113cf6`-scenariot. Det är ingen garanti för alla bytesfaser
eller en ren kedjekörning.

Observationsskriptet använde först äldre gråvärdet `404040` och gav råstatus
FAIL. Den råa rapporten bevaras. Ett separat källbundet analyskvitto jämför
med `fb_display.v`:s faktiska blankgren `202020`; negativa kontroller för
öppen videogrind, avvikande RGB och saknat prov avvisas. Det ändrar inga
RTL-, checksumme- eller täckningsregler.

C1-källan `629806f` får en egen strikt seed-126-diagnostik före den nya
kampanjen. Resultaten hör till olika kontrakt. Råloggar på denna värd:
`private/notes/evening_2026-10-08/c3/ovn-f1-e113-seed126` och
`ovn-f1-e113-seed126-probe`. Kompakt journal:
[ovn-f1-e113-replay.json](../2026-10-08/evidence/ovn-f1-e113-replay.json).


## Verifierad rättning 2026-10-09

Ren C1-main `629806f` gav samma store/read-checksummefel och X/Z som det separata strikta e113-RTL-kontraktet. Den första rättningen `7e5fe09` tog bort checksummefelet, men seed 126 läste fortfarande en aldrig komplett skriven ringplats. `39c7dc9` visade den platsen svart och passerade fröet, men dess fullsvit avslöjade en missad negativ kontroll: fel ringadress kunde godtas som svart. Rå FAIL (323 pass, 1 fel) är bevarad.

På `8d7b0e9` binds LOW-skrivningens adress, ordindex och data till den oberoende mixerströmmen. Den verkliga felvarianten avvisas med `display/ll_word`; identiskt seed 126 ger PASS med 216 kontrollerade rader, utan fynd, known, edges eller notes. Alla sex stimulus-/råloggfiler är byte-identiska med `39c7dc9`. Giltighetsmasken visar svart för aldrig initialiserade ringplatser och behåller äldre data i redan initialiserade platser. Triggergrind, F-bit och publiceringsregel är oförändrade.

Hela den frysta 490-testsviten är grön. M4 seed 0 och M6 seed 3 klarar 75 MHz på alla fem klockor; manifest och fyra HDMI-par är verifierade. Källan är accepterad och mergad till Core `edb85d0`. Den nya 260-frökampanjen återstår: det testade fröet stänger inte alla möjliga LOW→BUF-faser, och inget hårdvaruförlopp är verifierat. Se [C3_fix.json](../2026-10-08/evidence/C3_fix.json) för det källbundna acceptanskvittot och arkivhasharna.
