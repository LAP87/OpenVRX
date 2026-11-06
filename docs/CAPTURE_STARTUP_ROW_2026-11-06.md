# Första fältets radnummer förskjuts i den rena referenskedjan

Uppgift 76, oförändrad Core `031bba0`. Tidsobservation på exakt samma rena bypass-kodström som uppgift 75 ger ett avgränsat fynd: **första fältets 243 radstarter får radnummer ett lägre än det aktiva källradindexet**. Senare fält stämmer i detta körfall. Det är ett referensmodellresultat; RTL och hårdvara har inte provats för denna ström.

## Radbokföring

Indata innehåller 974 aktiva källrader. Observatören ser 973 utmatade ordradsstarter och 972 slutmarkörer:

| Källram / halva | Utmatat F | Radstarter | Utmatat radnummer minus aktivt källradindex |
|---|---|---|---|
| 0 / första | 1 | 243 | −1 |
| 0 / andra | 0 | 243 | 0 |
| 1 / första | 1 | 244 | 0 |
| 1 / andra | 0 | 243 | 0 |

Den första aktiva källraden, global rad 20, saknar en tilldelad utmatad radstart. Första utmatade rad 0 hör tidsmässigt till källrad 21, vars aktiva index är 1. Sista globala källraden 1050 har skickat 360 ord men ingen slutmarkör innan indatan tar slut. Det förklarar 974 = 1 utan radstart + 972 stängda rader + 1 ej stängd slutrad. Inga extra eller dubblerade radstarter hittades.

Associationen använder Capture-radens observerade last_start och närmaste kända H-start i indatan; alla ligger inom 64 sampel. Råa ord och taggar har inte flyttats eller korrigerats. F är modellens egen fälträknare, inte ett påstående om en fysisk TVP F-signal.

## Observerad uppstartssekvens

Originalmodellen börjar med sync=4 och blank=20, alltså boot_slice=12. Svepet når 13 vid sampel 5083 och 14 vid 10167. Första bredpulsens platå på källrad 4 innehåller 936 sammanhängande kodvärden 13. Originalets slicer jämför föregående åtta sampels summa med en strikt mindre-än-jämförelse:

`8 × 13 < 8 × 13` är falskt när slicern står på 13.

Därför kvalificerar denna platå inte som en sammanhängande bredpuls under det aktuella svepsteget. Efter steget till 14 accepteras bredpulsen på källrad 5: den observerade V-armen sker vid sampel 10776, med pulsbredd 600 och countdown=16. Den fasta nedräkningen ger första aktiva utdata på källrad 21, etiketterad 0. De senare V-armarna sker på källrad 267, därefter 4 och 267, och når rätt aktiva starter 283, 20 och 283.

Källställen i den frysta modellen: [initialnivåer och svep](https://github.com/LAP87/OpenVRX-Core/blob/031bba053943ee04ce303ae75b5e701746169c97/gateware/model/cvbs_capture_ref.py#L68), [strikt slicer](https://github.com/LAP87/OpenVRX-Core/blob/031bba053943ee04ce303ae75b5e701746169c97/gateware/model/cvbs_capture_ref.py#L284), [V-arm](https://github.com/LAP87/OpenVRX-Core/blob/031bba053943ee04ce303ae75b5e701746169c97/gateware/model/cvbs_capture_ref.py#L269) och [nedräkning/radstart](https://github.com/LAP87/OpenVRX-Core/blob/031bba053943ee04ce303ae75b5e701746169c97/gateware/model/cvbs_capture_ref.py#L371). Ingen av dem har ändrats.

## Vad som verifierats

En första privat observatörskörning tog 5,580 s driver, rc0, utan signal eller timeout. Den sparade kodbytes, rad-/markörtider och tillståndsväxlingar utan att mutera producenten. Både indatakodernas och utdataentryernas SHA256 är exakt samma som i uppgift 75. Alla 4 805 bundna käll-/runtime-/hjälpar-/beroendefiler var oförändrade. En separat stdlib-granskare, utan producentimporter, kontrollerade varje rad-/markörhändelse mot de binära entryerna och räknade om associationen till källgeometrin. Ingen ny C/N-svepning, pytest, HDL, proof eller FPGA-körning.

[JSON-kvitto](CAPTURE_STARTUP_ROW_2026-11-06.json) innehåller mappning, V-händelser och råfilernas hash/storlek. [Observatörens exakta körda kod](../research/experiments/observe_capture_timing.py) kan användas med Core på `031bba0`, dess publicerade `docs/IQ_CAPTURE_2026-11-06.json` som föregående kvitto och en ny outputkatalog. Befintlig katalog vägras. Ordinarie kvot-, gaming- och bygglåsgater gäller även reproduktion; gamla körningar ska inte startas om.

## Begränsning och nästa grind

Detta bevisar en tidsmässig radetikettförskjutning i det angivna rena modellfallet. Gråstaplarna och 1H-kammen bevisar inte varje pixels ursprung: sampel från källrad 20 kan till exempel bidra genom kammen trots att raden saknar egen utmatad radstart. Hot-relock, andra nivåer, verkliga C5-sampel och RTL-beteendet är inte verifierade.

Ingen producentfix har gjorts. Nästa motiverade kontroll är en separat native-reproducer med samma kodbytes och oberoende tidsstämplar, innan en startup-/V-policy ändras. Ett eventuellt första fält som saknar säker radidentitet behöver ett uttryckligt kontrakt; att skriva om taggarna eller sänka gränser för ett grönt test vore inte en lösning. Produktionsändring kräver tillämplig council-/modell-/negativ-/bygggrind.
