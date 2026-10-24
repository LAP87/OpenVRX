# C5VRX-ekosystemet 2026-10-24: vad andra redan gjort, och vad det betyder för oss

Läst 2026-10-24 efter att vårt ärende Twotoz/C5VRX#256 (sampelklocka ut på GPIO2) postats och ägaren
hittat tre repon till. Allt är GPL-3.0 (eller olicensierat) och läses som underlag; inget kopieras in.

## Projekten

| Projekt | Vad | Hur | Siffror och läge |
|---|---|---|---|
| [zerowidth/C5VRX PR #3 "P4USB"](https://github.com/zerowidth/C5VRX/pull/3) | ESP32-C5 bara som radio och IQ-källa, ESP32-P4 demodulerar, avkodar och streamar USB-webbkamera | **7 + 7 bitar IQ** ut ur C5:an på PARLIO-lanes (modembussen går i 80 MS/s, "the top 7 bits of I and Q"; oanvända LSB-lanes dras höga), självtest av trådarna vid start, P4:an driver C5:ans EN/BOOT och vidarebefordrar UART; demodulering med en 16 kB fastabell, analys i 13,33 och 40 MS/s; kort: Waveshare ESP32-C5-Zero (GPIO26 väljer antenn) | "as clear an image as I'm seeing on a standalone sologood receiver+display" vid 25 mW och 15 m genom två väggar med RHCP-antenn; synklås 10 % → 97 % av raderna vid C/N 3–5 dB; brusgolv cirka −93 dBm i 19 MHz, brusfaktor runt 8 dB; Wi-Fi-skurar klippte 1–4 % av samplen och höll förstärkningen 20 dB för lågt; 802.11p-läge smalnar filtret 19 → 12 MHz; extern RHCP 4,5–8 dB bättre än kortantennen. Öppen PR, 180 commits, inte sammanslagen |
| [Twotoz/C5VRX #47](https://github.com/Twotoz/C5VRX/issues/47) | ESP32-P4+C5-moduler som väg | Upphovsmannen positiv ("a beast"); zerowidth: de färdiga P4C5-modulerna lägger inte ut nog många C5-linjer för rå IQ (bara SDIO), därav den diskreta lösningen ovan | öppen sedan 2026-09-21 |
| [Iamethan1755/vrx-bridge](https://github.com/Iamethan1755/vrx-bridge) | Wi-Fi/USB-brygga: en XIAO ESP32-S3 läser C5:ans videobuss och streamar MJPEG | **Samma tap som vår uppgift 64, i programvara:** S3:an samplar D5–D9 (5 bitar; D4 används för knappar) med 20 MHz utan klocka, synkslicing, rad-PLL och vertikaldetektering i kod, gråskala 320×240/288 upp till 30 fps, latens "on the order of 100 ms"; C5VRX-5 v5.0.109 med tre små ändringar (UART-knappläsare, direkt kanalval, knapplinje på D4) | "the C5's output used 22 of the 64 levels, 16 remain"; ingen färg (nästa experiment); GPL-3.0 |
| [Twotoz/C5VRX-OpenPocket](https://github.com/Twotoz/C5VRX-OpenPocket) | Upphovsmannens handhållna koncept: Waveshare ESP32-S3-LCD-kort med RGB-LCD plus en C5 som mottagare, RivetTX för sändning | C5:an sägs ge "8-bit unsigned CVBS samples"; blockeraren är "continuous C5 RF sampling", märkt oprövad | experimentellt, "not yet a working FPV receiver"; ingen licens angiven |
| [ardchain/esp32-fpv-receiver](https://github.com/ardchain/esp32-fpv-receiver) | Byggföljeslagare: kopplingsguide och webbkonsol för C5VRX på XIAO | Firmwaren som oförändrad undermodul; 6-bitars DAC som i README | inget nytt tekniskt; inte bänkprovad enligt sidan |
| [Twotoz/C5VRX #201](https://github.com/Twotoz/C5VRX/issues/201), #222 | Upphovsmannens egen utredning av bildraset utomhus och dold räckviddsförlust | Misstänkta led i ordning: radiolänk och utbredning, C5:ans frontend och **4-bitars IQ-kvantisering**, U85Q:s fasföljning och Kp/LP-växling, CVBS-nivåer och glasögonens tröskel | inga hårdvarumätningar i ärendet; simulerade vinster 0,4–3 dB; "No measured RF range gain or physical picture-cliff cure is claimed" |

## Vad det betyder för OpenVRX

1. **Den starkaste vägen ligger ett steg före vår uppgift 64.** zerowidth visar att C5:an kan lämna ut
   7 + 7 bitar IQ på PARLIO-lanes och att en demodulator utanför kretsen slår den inbyggda 4-bitarsvägen
   med bred marginal (synklås 97 % vid C/N 3–5 dB, bild som en färdig mottagare). För oss är det
   mottagargräns C: 14 datatrådar plus klocka in i FPGA:n, FM-demodulering och kompositavkodning i
   Verilog. Det är DSP-arbete av det slag vi redan gör, och det tar bort 6-bitars-utgången helt. XIAO:n
   har inte stiften; ESP32-C5-Zero eller en WROOM-1U-modul har.
2. **Uppgift 64 står kvar** som måndagens snabba väg och som reserv: synkseparering, radnumrering,
   kamfilter och färgdemodulering återanvänds efter en egen FM-demodulator.
3. **Modellens nivåer är syntetiska.** vrx-bridge såg bara 22 av 64 koder använda; det stämmer med att
   OUTPUT 1,0× ger liten svängning. Måndag: läs riktiga sampel med fältdumpen och kalibrera
   `cvbs_capture_ref.py`:s fönsterkonstanter mot dem. Gain-tabellen hanterar nivåerna i sig.
4. **UART på ett GPIO har prejudikat:** vrx-bridge lade en UART-knappläsare på D4 med tre commits. En
   statusrad åt andra hållet är samma storlek.
5. **OpenPocket säger 8-bitars sampel internt.** Det stöder fråga 1 i #256: lane 6 och 7 bär sannolikt
   riktig information när de får stift.
6. **Bänkkort för IQ-vägen:** Waveshare ESP32-C5-Zero (ESP32-C5-HF4 med 4 MB flash, ingen PSRAM så
   GPIO15 är fri, antennväxlingskrets med IPEX-1-kontakt, GPIO26 väljer antenn enligt zerowidth;
   stiftantalet läses ur [Waveshares wiki](https://docs.waveshare.com/ESP32-C5-Zero) och schemat).
   Upphovsmannens egna räckviddsärenden pekar på samma 4-bitars-IQ som taket, så IQ-vägen angriper
   rätt led.

## Förslag till planen

- Uppgift 67 (ny): mottagargräns C i simulering: Python-modell av FM-demodulering ur 7 + 7-bitars IQ i
  40 MS/s på syntetisk FM-video (NTSC-komposit → FM-deviation som FPV-sändare → brus), mått på synklås
  och luma-SNR mot C/N, jämfört med 6-bitars kompositvägen; sedan Verilog med negativ kontroll. Ingen
  hårdvara förrän kortfrågan är löst.
- Ordning: måndag 64 på kortet, därefter 67 i simulering före 65 (färgen), eftersom 67 avgör vilken väg
  färgen ska byggas för.
