# Plocklista för smådelar till bänken, och hur man känner igen dem

Det som behövs utöver modulerna i `MATERIAL_UPPSTART.md` när M3–M6 kopplas på kopplingsdäck och sladdar: motstånd, kondensatorer, spolar, tråd. Allt är vanliga lagervaror som brukar finnas i en komponentlåda på en arbetsplats. Antalen är för två dekodrar och två mottagare; ta några extra av varje. Inga butiker eller priser. Mät alltid lånade delar med multimetern innan de kopplas in (avsnitt 3).

## 1. Plocklista

| Del | Värde | Antal | Vad den gör | Steg | Källa |
|---|---|---:|---|---|---|
| Motstånd, I2C-pull-up | 4,7 kΩ (2,2–4,7 kΩ går) | 3 (+2 extra) | SCL, SDA_A och SDA_B till 3,3 V, om modulerna inte har egna (titta efter två små motstånd intill SCL/SDA på TVP-modulen; mät mellan SCL och 3,3 V utan ström: cirka 4,7 kΩ betyder att de finns) | M3 | BRINGUP 1 "Gemensamt" |
| Motstånd, serieterminering på dekoderdata | 33 Ω (22–47 Ω går) | 18 (9 per dekoder: D0–D7 och SCLK) | På kopplingsdäck med 10–20 cm sladd ringer 27 MHz-signalerna; ett motstånd vid TVP-modulens stift tar ned det. Rev A-kortet har dem fast (R9–R16, R19). Går att hoppa över för ett första prov, men sätt dem om proben visar `tog`-värden som hoppar eller bild med fel pixlar | M3 | Rev A-schemat; TI SLEA081 |
| Motstånd, knapp-pull-up | 10 kΩ | 2 (+2) | Egna OK/NEXT-knappar mot jord behöver pull-up till 3,3 V, om inte FPGA:ns interna pull-up slås på i stiftfilen (då 0 st) | M6 | Core `gateware/boards/` (PULL_MODE) |
| Motstånd, RSSI-pull-down | 100 kΩ | 2 | Om RSSI ska mätas med multimeter på bänken innan rev A finns: 0 V utan mottagare | M4 (frivilligt) | Puck README "RSSI" |
| Kondensator, keramisk | 100 nF | 10 | Avkoppling vid varje moduls matningsstift (TVP ×2, RX5808 ×2, OLED, DC-DC-utgångar) | M3 | Allmän praxis; rev A-schemat |
| Kondensator, elektrolyt eller tantal | 10 µF, minst 10 V | 4 | Intill varje mottagare och dekoder på 5 V respektive 3,3 V, för att sladdarnas induktans inte ska ge spänningsdippar när RX5808 växlar kanal | M3 | Rev A-schemat (C17/C32 är 10 µF) |
| Kondensator, elektrolyt | 100–220 µF, minst 10 V | 2 | LC-filter efter DC-DC-modulen till mottagarna | M4 (när snö och brus mäts) | `MATERIAL_UPPSTART.md` "Finns hemma" |
| Spole eller ferritpärla | 10–22 µH, minst 1 A (eller ferritpärla 600 Ω vid 100 MHz om bara HF ska bort) | 2 | Samma LC-filter: spole i serie från DC-DC-modulen, 100 µF och 100 nF efter spolen, en filter per mottagare | M4 | RF-underlaget (linjär eller filtrerad 5 V per mottagare) |
| Kopplingstråd hona–hona och hona–hane, 10–20 cm | — | 40 | 9 dataledare + jord per dekoder, SCL, SDA ×2, RESETB, 3 SPI-ledare till RX5808, matning. Korta sladdar: 27 MHz tål inte 30 cm | M3 | BRINGUP 1 (tabellerna för J5 och J6) |
| Stiftlist 2,54 mm, hane, rak | 2 × 20 (+ några bitar) | 2 | Till Tang Nano 20K:s J5/J6 om de inte är lödda; bitar för modulerna | M0 | — |
| Krympslang eller eltejp | — | — | Pigtailarnas lödställe på RX5808 och resettråden | M3 | `MATERIAL_UPPSTART.md` "Finns hemma" |
| Tenn, flussmedel, pincett, lupp | — | — | Resettråd på TVP-modulen (stift 8 är 0,8 mm delning), SPI-moden på RX5808 | M3 | BRINGUP 0 "Reset" |

Inte med på listan, med skäl: 75 Ω-terminering på video (TVP-modulen har sitt eget ingångsnät), motstånd i serie med RX5808:s SPI-ledare (FPGA:n och modulen är båda 3,3 V), pull-down på RESETB (borttagen i rev A, se Puck #1), ESD-dioder (bara på kortet).

## 2. Känna igen motstånd

**Fyra ringar** (vanligast i komponentlådor, tolerans 5 %): första två ringarna är siffror, tredje är antalet nollor, fjärde (guld) är toleransen. Läs med guldringen till höger.

| Färg | Siffra | Som tredje ring: multiplikator |
|---|---:|---|
| svart | 0 | ×1 |
| brun | 1 | ×10 |
| röd | 2 | ×100 |
| orange | 3 | ×1 000 |
| gul | 4 | ×10 000 |
| grön | 5 | ×100 000 |
| blå | 6 | ×1 000 000 |
| violett | 7 | ×10 000 000 |
| grå | 8 | — |
| vit | 9 | — |
| guld | — | ×0,1 (tolerans 5 % som sista ring) |
| silver | — | ×0,01 (tolerans 10 % som sista ring) |

**Fem ringar** (tolerans 1 %, ofta blå kropp): tre siffror, sedan multiplikator, sedan tolerans (brun = 1 %). Läs med toleransringen (ofta lite bredare, eller med större avstånd) till höger.

Värdena på plocklistan:

| Värde | Fyra ringar | Fem ringar |
|---|---|---|
| 33 Ω | orange, orange, svart, guld | orange, orange, svart, guld, brun |
| 1 kΩ | brun, svart, röd, guld | brun, svart, svart, brun, brun |
| 4,7 kΩ | gul, violett, röd, guld | gul, violett, svart, brun, brun |
| 10 kΩ | brun, svart, orange, guld | brun, svart, svart, röd, brun |
| 100 kΩ | brun, svart, gul, guld | brun, svart, svart, orange, brun |

Lätt att blanda ihop: brun och röd, orange och gul, violett och blå, särskilt på små eller gamla motstånd. Mät.

**SMD-motstånd** har siffror i stället: tre siffror är två siffror plus antalet nollor (`330` = 33 Ω, `472` = 4,7 kΩ, `103` = 10 kΩ, `104` = 100 kΩ), fyra siffror är tre siffror plus nollor (`4701` = 4,7 kΩ, `1002` = 10 kΩ). `R` är kommatecken (`4R7` = 4,7 Ω, `0R` eller `000` = 0 Ω bygel). Små storlekar (0402) saknar text; de går bara att mäta.

## 3. Känna igen kondensatorer och spolar

- **Keramiska skivor och SMD-kondensatorer med text:** tre siffror i pikofarad, två siffror plus antalet nollor: `104` = 100 000 pF = 100 nF, `106` = 10 µF, `102` = 1 nF, `221` = 220 pF. Bokstav efter är toleransen (K = 10 %, J = 5 %, M = 20 %). De flesta SMD-kondensatorer saknar text helt.
- **Elektrolyter:** värdet och spänningen står i klartext (`10µF 25V`). Polariserade: minusbenet är kortare och markerat med en ljus rand på burken; fel vänd kan den gå sönder. Tantal: markeringen (streck eller plus) är pluspolen, tvärtom mot elektrolyter.
- **Spolar:** tre siffror i mikrohenry på samma sätt som motstånd (`100` = 10 µH, `220` = 22 µH). Omärkta smådelar som ser ut som motstånd men är gröna eller har en spole-symbol är ofta spolar; mät: en spole har nära 0 Ω, en ferritpärla också. Mät inte en spole mot en ferrit med multimetern, de ser lika ut; det är bara strömtåligheten och induktansen som skiljer, och det står på påsen eller inte alls.
- **Ferritpärlor** (för matningsfilter) är omärkta små cylindrar eller SMD-block; 0 Ω för multimetern.

## 4. Mät innan du kopplar

- Motstånd: multimetern på Ω, delen lös (inte i en krets). Avvikelse under 5 % från färgkoden är normalt.
- Kondensator: en multimeter med kapacitansläge visar värdet; utan det går det bara att se att den inte är kortsluten (Ω-läge: stiger mot oändligt). Elektrolyter som legat länge kan ha tappat kapacitet.
- Spole eller pärla: nära 0 Ω. Går den inte att skilja från en tråd är det en.
- Lånade motstånd av okänd effekt: alla värden här är under 10 mW, så 1/8 W eller 1/4 W räcker; storleken spelar ingen roll.
