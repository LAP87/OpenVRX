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
