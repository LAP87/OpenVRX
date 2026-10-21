# Mottagardelen: vägar nu och för produkten (2026-10-21)

Ägarens fråga 2026-10-21: vilka realistiska vägar finns för den analoga mottagardelen, nu och för produkten, och vad görs först? Läget: Tang Nano 20K och en TVP5150_CP803A-modul fungerar (klocka, I2C på 5D, frilöpande NTSC-timing, [BANK_2026-10-21.md](../../bench/BANK_2026-10-21.md)); kamera med sändare på A1 5865 MHz; Moneagles AV-jack är en ingång; XIAO ESP32-C5 med C5VRX men utan motstånds-DAC; två RX5808 beställda men inte skickade. Underlaget är läst 2026-10-21; inget här är mätt av oss. Priser och tillgång står i [research/MOTTAGARE_ALTERNATIV_2026-10-21.md](../../../research/MOTTAGARE_ALTERNATIV_2026-10-21.md).

Märkning som i researchnoterna: **[T]** tillverkarens uppgift, **[K]** projektets kod eller egna dokument, **[A]** användarrapport, **[R]** vårt resonemang, **ej verifierat** där inget belägg finns.

## Rekommendation

1. **I dag: XIAO:n först, men felsök "dör efter en stund" innan DAC:n löds.** Flasha senaste C5VRX-5 (`c5vrx5-v5.0.363`, 2026-10-21) som *Full firmware*, låt första kalibreringen gå klart med sändaren av (högst åtta minuter) och håll webbterminalen öppen: firmwaren skickar en `STATUS`-rad varannan sekund. Lysdioden säger ingenting. Bygg sedan DAC:n (motstånden står redan i bänkplanens lista) och gå BANK steg 4–5.
2. **Samtidigt: beställ RX5808 med SPI från ett andra håll** (tre styck, uppgift 32). De behövs för två oberoende strömmar (blad 6–8) och som referens. Ett färdigt RX5808-diversitykort är en alternativ källa till två moduler.
3. **Reserv om XIAO:n inte ger bild på en dag:** tappa CVBS inuti Moneagle (en tråd från dess mottagarmodul till vår TVP-modul). Det öppnar den enda referensskärmen, så det är ägarens beslut.
4. **Produkten:** RX5808/RTC6715 står kvar som referens och rev A-mottagare. C5VRX är kandidaten mot gräns A, men behöver två kort och en styrväg från kärnan. AD9361-vägen väntar (rådets P5). Premiummoduler är referenser, inte mixerkällor: de lämnar en redan mixad ström.

## 1. Video in i TVP:n nu (dagar)

Rangordnat efter tid till första bild på HDMI genom vår egen TVP-modul. "Strömmar" är antalet oberoende CVBS-strömmar för radmixern (gräns A i Puck `design/MOTTAGARGRANS.md`).

| # | Väg | Tid till bild | Vad som saknas | Strömmar | Relevans för produkten | Risk, okänt |
|---|---|---|---|---|---|---|
| 1 | **XIAO ESP32-C5 + C5VRX** | timmar | sju motstånd, 5,8 GHz-antenn (Moneagle-antennen enligt BANK), att XIAO:n håller sig vid liv | 1 per kort | medel: den kandidat mot gräns A som finns på bordet; samtidigt första punkten i planens C5VRX-jämförelse | "dör" efter en stund (avsnitt 2); bildkvalitet och räckvidd ej visade av oss |
| 2 | **CVBS ur Moneagles mottagarmodul** → vår TVP-modul | timmar | öppna Moneagle, en tråd och jord vid kopplingskondensatorn före dess TVP ([MONEAGLE_TEARDOWN.md](../../../research/MONEAGLE_TEARDOWN.md), punkt 3) | 1 (Moneagles diversityval) | låg: bara bänkkälla | teardownen gäller ett annat exemplar (2020); Moneagles egen bild kan påverkas; skärmen är vår enda referens |
| 3 | **M1/M2: lyssna på Moneagles egen TVP** (BT.656 direkt in i Tang) | timmar till en dag | tio tunna trådar på TQFP-32, IO_DVDD mätt till 3,3 V (Core `gateware/README.md`, "M1 — koppla in Moneagle") | 1 | låg: hoppar över vår TVP-modul, som redan fungerar | Moneagles SoC äger I2C (FPGA:n får bara lyssna); synkläget kan kräva M1s; finpitchlödning |
| 4 | **RX5808 med SPI från en annan källa** | dagar till veckor beroende på varifrån (ej verifierat) | SPI-modden om modulen inte redan har den ([beskrivning][spimod]), 5 V, antenn | 1 per modul, 2 med två | hög: rev A:s mottagare och referensen | varianter skiljer (SPI-revision, två extra flikar, SAW-filter, [RF-underlaget][rfdiv] avsnitt 1); listningar ej kontrollerade mot modulen |
| 5 | **Färdigt RX5808-diversitykort** (rx5808-pro-diversity-typ med OLED) | dagar till veckor | inget för en ström; för två: tappa varje moduls video före kortets analoga switch | 1 ur AV-utgången, 2 vid modulernas videostift [R] | hög som källa till två RX5808 | kortlayouten okänd tills det är öppnat; skiftlägesbrus från switchen ([projektet][rxpd], 4066-switch) |
| 6 | **Färdig mottagare med AV-ut** (RC832-typ; RC832-HD har också HDMI) | dagar | 6–24 V-matning, AV-kabel | 1 | referens för blad 15, inte mixerkälla | blad 15 säger att en RC832HD var "på väg" 2026-10-12: om den har kommit är den snabbast av alla; video 1 Vpp/75 Ω enligt återförsäljarens specifikation (ej verifierat) |
| 7 | **Monitor med en AV-utgång per mottagare** (FlySight Black Pearl: RX1, RX2 och DIV AV OUT) | dagar, om den går att få | 7–28 V | **2** enligt återförsäljarens specifikation (ej verifierat) | referens med två strömmar; gammal produkt | inga tillverkardokument hittade; de flesta billiga diversitymonitorer (t.ex. LCD5802D) har bara en AV-utgång |
| 8 | **SDR på datorn** (HackRF One med fpv-sdr eller fpvdec) | dagar + programvara | kort, dator, verktyg ([SDR-noten][sdr]) | 0 (IQ, ingen CVBS) | låg för TVP:n; svarar på P5:s fråga om en bredare radio | 20 MS/s är gränsen för en FPV-kanal; ingen tröskelmätning publicerad ([3G3/5G8-noten][rx3358] avsnitt 1.2) |

Rangordning efter relevans för produkten: 4, 5, 1, 7, 6, 8, 2, 3.

## 2. XIAO ESP32-C5 med C5VRX: det README säger

Läst ur [README vid `59dcfce`][c5readme] (2026-10-21) och projektets ärenden. C5VRX är GPL-3.0-only och körs som separat firmware på ägarens kort; ingen kod kommer in i våra repon (beslut 3).

| Fråga | Svar | Källa |
|---|---|---|
| Första start | Strömsätt "best with the VTX off, for a few minutes (at most eight)"; skärmen visar CALIBRATING med förlopp. Med sändaren på kalibreras filtret på en tyst kanal. Resultatet sparas; senare starter hoppar över det som redan är mätt. En ny kalibreringsgeneration i ny firmware kalibrerar om helt en gång. Kalibrering körs bara vid start eller via CALIBRATE | [K] README "First boot" |
| Under kalibreringen | Menytangenter vägras med `COMMAND <key> refused=busy` medan statusskärmen äger bilden | [K] README "Web flasher" |
| Startkanal | A1 5865 MHz utan sparad kanal, alltså ägarens sändarkanal | [K] |
| Konsol (USB, 115200, en byte utan Enter) | `T` status, `D` räckvidd/hälsa, `R` FIELD_DIAG per sekund, `I` IQ-ögonblick, `o` meny, `c`/`b` nästa kanal/band, `n`/`x` meny nästa/välj, `s` skanna, `F` kalibrera om, `v` AUTO/NTSC/PAL, `g` OUTPUT 0,5–5,0×, `G` GAIN, `U` FLYWHEEL, `Z` DAC-självtest, `` ` `` USB-nedladdningsläge, `h` hjälp. Inget kommando för en given frekvens | [K] README "Serial console" |
| Livstecken | Firmwaren skickar en kort `STATUS`-rad varannan sekund, som webbterminalen läser | [K] README "Web flasher" |
| Lysdiod | README nämner ingen lysdiod, och C5VRX-5 styr den inte enligt en kodsökning (bara äldre generationer). Seeeds wiki anger en röd laddningslysdiod och en gul användarlysdiod (GPIO27) men inte laddningslysdiodens beteende utan batteri ([Seeed][seeed]) | [K], [T]; beteendet ej verifierat |
| Nivå mot vår modul | DAC-nätets källimpedans är ca 122 Ω; med 200 Ω-lasten blir full skala ca 2,0 V öppen, ca 1,0 V när modulens 75 Ω-terminering ligger parallellt. Börja med OUTPUT 1,0× och 200 Ω kvar | [R] ur motståndsvärdena; mät på plats |

**Varför XIAO:n kan verka "dö" efter en stund.** Ingen av orsakerna är bekräftad för ägarens kort; de är de som projektet självt har dokumenterat, i ordning efter hur lätta de är att utesluta.

| Trolig orsak | Belägg | Hur den utesluts |
|---|---|---|
| Den lever, men USB-konsolen tystnar efter flashvägen (`` ` `` → ROM → flash → watchdogreset); efter omkoppling startade kortet två gånger i ROM-laddaren | [K] [FINDINGS][c5find], avsnittet om #221: "the USB serial console sometimes stays silent while the receiver keeps a picture … a RESET tap recovers it. Cause open." | tryck RESET efter flashning; se om `STATUS` kommer |
| Uppgiftsvakten (`task_wdt: IDLE (CPU 0)`) "roughly every few minutes" i byggen före #221 | [K] [PR 221][c5pr221], sammanslagen 2026-10-18 | flasha en release efter 2026-10-18; läs konsolen när den tystnar |
| Första kalibreringen pågår upp till åtta minuter och vägrar tangenter | [K] README | vänta ut den; `refused=busy` betyder att den lever |
| Misslyckad omstart av videovägen "latches live OFF"; USB lever vidare | [K] README | `T` visar läget |
| Matningen från laptopens port, energisparläge för USB i Windows eller att porten flyttats till WSL med `usbipd` | [R]; inget belägg i projektet | annan port eller laddare med data; `usbipd list` |
| Värme | inget hittat i README eller ärenden | ej verifierat |

## 3. Produktens RF-del (månader)

Avgörande fråga för radmixern: ger vägen **två oberoende videoströmmar från två antenner** (Puck `design/MOTTAGARGRANS.md`, "Vad kärnan antar om bilden")?

| Väg | Två oberoende strömmar? | Gräns | Styrning från kärnan | Livscykel, källa | Det som saknas |
|---|---|---|---|---|---|
| **2× RX5808 / RTC6715** (dagens rev A) | ja | A | finns: SPI, gemensam kanal (`rx5808_tune.v`) | RichWave listar RTC6715 utan statusmärke 2026-10-21, liksom alla sina kretsar ([RichWave][rw]); datablad bakom formulär; ingen tillverkare publicerar livscykel för RX5808-modulen ([RF-underlaget][rfdiv]) | status hos RichWave (fråga före eget RF-kort); modulvarianterna mätta mot varandra |
| **Eget RF-kort med 2× RTC6715** | ja | A | samma SPI-ram | som ovan | motiveras först av blad 11-mätningen ([RF-underlaget][rfdiv], åtgärd 9) |
| **2× ESP32-C5 med C5VRX** | ja, ett kort per antenn [R] | A | bara USB-konsol och knapp, inget kommando för en given frekvens; kärnan behöver en UART-väg per kort eller en överenskommen styrning | ESP32-C5 i volymproduktion sedan 2025-04-30 ([RF-underlaget][rfdiv]); C5VRX ändras flera gånger per dag (release 5.0.363 2026-10-21) [K]; GPL-3.0 kräver ett licensbeslut om den levereras med produkten (rådet 2026-10-19) | jämförelse mot RX5808 (avsnitt 4). Projektet anger att kedjan når ca −93 dBm med brusfaktor ca 6 dB, mätt mot Wi-Fi-radions egen RSSI och inte mot en extern källa ([FINDINGS][c5find], PR #226), och beskriver samtidigt kort räckvidd utomhus ([ärende 201][c5i201]); samexistens mellan två C5-radioer nära varandra (ej undersökt); C5VRX:s egen jämförelse mot RX5808 är "the open measurement" ([FINDINGS][c5find]) |
| **AD9361 (två mottagarkanaler) eller AD9364 (en)** | ja med AD9361; dessutom RF-faser före detektorn [R] | B (BT.656) eller ny: IQ in i FPGA:n | ny styrning | aktiva enligt ADI:s sidor lästa av rådet 2026-10-19; inte omläst i dag | FM-demodulering och videoavkodning i FPGA eller dator, effekt-, latens- och resursbudget; en ny arkitektur, inte ett modulbyte ([COUNCIL.md](../2026-10-19/COUNCIL.md), [SDR-noten][sdr]) |
| **Premiummodul som den är** (Fusion, rapidFIRE, SteadyView X) | **nej**: en redan mixad utgång | A, en kanal | Fusion har ett publicerat seriellt protokoll; övriga egna ([3G3/5G8-noten][rx3358]) | se 3G3/5G8-noten | duger som referens i blad 15, inte som mixerkälla |
| **Premiummodul uppöppnad**, tappa varje intern mottagare före dess fusion | möjligen: rapidFIRE och Fusion har två mottagarmoduler/-kort internt ([MOTTAGARKRETSAR][mk]) | A | modulens egen processor | inga scheman; kretsarna obelagda | ingen produktväg: odokumenterat, okänd nivå och last [R] |
| **FT VRX 5.8, FLYTO MM238RW** (moduler med I2C/SPI) | ja, två moduler | A | I2C respektive SPI; ny styrmodul i gatewaren | se [3G3/5G8-noten][rx3358] (MM238RW-datablad saknas, FT:s 5,8 GHz-manual ej läst) | datablad, krets, RSSI |

Slutsats för produkten: bara vägar med två separata mottagare framför kärnan ger radmixern något att välja mellan. Det gäller RX5808/RTC6715, två C5-kort, FT/FLYTO-moduler och AD9361. En färdig diversitymottagare ger det inte.

## 4. Mätningen som avgör "bättre bild än RX5808"

Bara det som [MATPROTOKOLL.md](../../MATPROTOKOLL.md) redan definierar:

- **Blad 11** (snöloggen vid svag signal, "på avstånd eller med dämpning"): `snowlog.py`, 30 s per villkor, tre upprepningar, `snow_*` och `noise_*`. Kör M6 (byggt med `TVP_ADDR=5D` för CP803A-modulerna) med RX5808 på kanal A och kandidaten (till exempel C5VRX) på kanal B, samma sändare, likadana antenner sida vid sida. Båda dekodrarna ser samma kamerabild i samma ögonblick, så bildinnehållet tar ut sig. Byt A och B och upprepa, så att dekoderskillnad inte räknas som mottagarskillnad [R].
- **Blad 13** (låsflaggan): `lost_a`/`lost_b` per villkor i samma körning.
- **Blad 15** (jämförelse mot en färdig mottagare): latens och bild i brus sida vid sida, samma villkor som blad 11. För en mottagare som inte kan matas in i pucken.
- **Blad 6** (en antenn av i taget) visar att mixern faktiskt använder kandidaten (`use_a`/`use_b`).

Kandidaten är bättre om den har lägre `snow`/`noise` och färre `lost` än RX5808 på samma avstånd, i båda A/B-placeringarna, utöver spridningen mellan upprepningarna. Begränsningar: M6 ställer bara RX5808 över SPI, så kandidaten ställs för hand på samma kanal; bladen anger avstånd eller dämpning men ingen RF-nivå i dBm, och ingen kalibrerad dämparsats finns i materiallistan. Det är en lucka i bladen, inte något denna not fyller.

## Ej verifierat

- Om ägarens XIAO faktiskt dör eller bara tystnar på USB; vilken C5VRX-version som är flashad.
- RC832HD: inte beställd (ägaren 2026-10-21); väg 6 kräver alltså en beställning.
- FlySight Black Pearls separata RX1/RX2-utgångar och RC832-HD:s videonivå (bara återförsäljares specifikation).
- Var videostiften sitter på ett färdigt RX5808-diversitykort och om de går att tappa före switchen.
- RTC6715:s livscykel hos RichWave (tabellen saknar statusmärken för alla rader), AD9361/AD9364:s status i dag.
- Moneagle-exemplarets kort och TVP-konfiguration.

[spimod]: https://github.com/sheaivey/rx5808-pro-diversity/blob/master/docs/rx5808-spi-mod.md
[rxpd]: https://github.com/sheaivey/rx5808-pro-diversity
[rfdiv]: ../../../research/RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md
[rx3358]: ../../../research/MOTTAGARE_3G3_5G8_2026-10-18.md
[mk]: ../../../research/MOTTAGARKRETSAR_2026-10.md
[sdr]: ../../../research/SDR_5G8_MOTTAGNING_2026-10-19.md
[c5readme]: https://github.com/Twotoz/C5VRX/blob/59dcfceb59e230a94fda369f84a8e29edef74447/README.md
[c5find]: https://github.com/Twotoz/C5VRX/blob/59dcfceb59e230a94fda369f84a8e29edef74447/docs/FINDINGS.md
[c5pr221]: https://github.com/Twotoz/C5VRX/pull/221
[c5i201]: https://github.com/Twotoz/C5VRX/issues/201
[seeed]: https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/
[rw]: https://www.richwave.com.tw/en/page_prd_new.aspx?Id=8
