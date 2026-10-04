# C5VRX och OpenDrone (tips, 2026-10-03)

## C5VRX — ESP32-C5 som analog 5,8 GHz-mottagare

[github.com/Twotoz/C5VRX](https://github.com/Twotoz/C5VRX) (GPL-3.0-only, 169 stjärnor, aktiv 2026-10-03; README, fusion-, bildkvalitets-, räckvidds- och licensdokument sparade i `raw/c5vrx/`).

**Vad det är:** en Seeed Studio XIAO ESP32-C5 (5 GHz wifi-krets med RISC-V) läser radions rå-I/Q i 40 MS/s via ett diagnosläge (MODEM_DIAG). Den demodulerar FM-videon i kretsens BitScrambler-hårdvara och skriver ut 6-bitars CVBS (20 MS/s) via PARLIO TX och en motståndsstege (8,2 k … 240 Ω, 470 pF filter). Inget CPU-arbete per pixel. 48 kanaler, PAL/NTSC-detektering, egen förstärkningsreglering ("Direct Gain V5"), kanalscanning, web-flashare. Bänkstatus: ren bild statiskt och i rörelse. Räckviddsgräns, överstyrning nära VTX och långa pass "behöver tester" (deras egna ord).

**Varför det är intressant för pucken:**

1. **Billig modern mottagare** i stället för RX5808 (RTC6715 från ~2014): en XIAO ESP32-C5 per kanal, med mätdata RX5808 inte har (I/Q-amplitud, fas-koherens, klippning, förstärkning) över seriellt gränssnitt. Det är bättre underlag för mixern än vår snö-mätare ensam.
2. **Digital väg utan TVP5150 (forskningsspår):** ESP32-C5 har redan videon som 6-bitars digitala sampel innan motståndsstegen. Skickas de parallellt till FPGA:n kan dekodern hoppa över DAC → kabel → TVP5150 → ADC. FPGA:n måste då själv göra CVBS-avkodningen (synkseparering, färgdemodulering). Stort jobb, och 6 bitar ger sämre bild än TVP:ns 9 bitar.
3. **Äkta "fusion" före demodulering:** C5VRX:s fusionsdokument säger uttryckligen att CPU:n inte kan slå ihop flera 40 MS/s-demodulatorer i realtid. Deras fusion är i dag en övervakare som väljer förstärkning. Med I/Q från två ESP32-C5 in i en FPGA vore kombination på I/Q-nivå möjlig (som diversity-mottagare gör). Det är ett tydligt större steg än vår radmixer och ett eget forskningsprojekt.

**Förbehåll:** ung, snabbrörlig firmware (versioner flera gånger per dag), ett odokumenterat diagnosläge i ESP32-C5 (kan försvinna eller ändras med ESP-IDF), 6-bitars DAC, bara bänktestad. Räckvidd mot RX5808/RTC6715 är inte jämförd. Ett prisvärt *experiment*: en XIAO ESP32-C5 och en handfull motstånd.

**Förslag:** köp en XIAO ESP32-C5, flasha C5VRX, koppla CVBS-utgången till ett av puckens video-in. Snö-mätaren och mixern jämför den direkt med en RX5808 på samma kanal. Det är det billigaste sättet att få ett svar.

## OpenDrone (Discord-skärmbild)

Öppen drönarhårdvara med egna kanaler för fc, aio, esc, **rx**, **vtx**, **digital-vtx**, gps, frame, **kicad-library**, samt mjukvarukanaler (betaflight, AM32, ExpressLRS). Licensbyte till **CERN-OHL-S v2** (starkt reciprok öppen hårdvarulicens) syns i PR:erna för OpenFC-Lite/-Mini. En utvecklare skriver att den som vill bygga ett bättre flygkontrollkort får stöd.

**För oss:** ett naturligt ställe att visa pucken/dekoderkortet och få granskning av KiCad-designen, om projektägaren vill. projektägaren har bestämt att licens inte spelar någon roll för privat bruk. Bygger vi vidare på *deras* KiCad-filer gäller CERN-OHL-S för de delarna, om det någon gång delas eller blir produkt. Detsamma gäller GPL-3.0 för C5VRX-kod.
