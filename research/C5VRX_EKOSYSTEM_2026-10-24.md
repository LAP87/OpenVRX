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

## Resultat ur modellen (uppgift 67, 2026-10-24 kväll)

Core `gateware/model/iq_demod_ref.py` (numpy): syntetisk NTSC-komposit → FM med 2,8 MHz/V → 12 MHz kanal →
brus vid givet C/N → AGC och kvantisering till 4 eller 7 bitar per axel → fasderivata som demodulator →
videofilter. Luma-SNR mot den rena videon och andelen rader där synkflanken hittas inom ±3 sampel med en
fast slicer. 60–90 rader gråstaplar. Siffrorna gäller denna syntetiska kedja; de är ingen undre gräns för verklig hårdvara.

| C/N (dB) | 4-bitars IQ | 7-bitars IQ | 4-bitars IQ, 6-bitars utgång |
|---|---|---|---|
| 8 | 10,7 dB, synk 7 % | 11,4 dB, 6 % | 10,7 dB, 7 % |
| 12 | 14,8 dB, 19 % | 15,7 dB, 38 % | 14,8 dB, 22 % |
| 20 | 20,1 dB, 63 % | 23,7 dB, 99 % | 20,1 dB, 63 % |
| 30 | 22,4 dB, 87 % | 33,0 dB, 100 % | 22,3 dB, 87 % |

Samma bild med deviation 2,0 och 4,0 MHz/V och med 16 MHz kanal: 4 bitar stannar på 20–29 dB hur stark
signalen än är, 7 bitar når 30–36 dB och hittar synken i alla rader från 20 dB C/N; 6-bitars utgången
kostar under 1 dB. I modellen begränsar 4-bitarskvantiseringen mer än den modellerade 6-bitarsutgången; 7 bitar ger cirka 10 dB högre SNR vid stark signal. Det fastställer inte vilket led som begränsar den fysiska C5VRX/DAC/TVP-kedjan. Under
10 dB C/N är båda dåliga i den här enkla modellen; där ligger vinsten i demodulatorn (begränsare,
fasföljning), som zerowidths 97 % synklås vid 3–5 dB visar. Testet `gateware/sim/test_iq_demod.py` låser
egenskaperna (SNR stiger med C/N, 7 bitar minst 8 dB över 4, utgången under 1 dB, negativa kontroller med
2 bitar och fel deviation).

### Egen PLL-jämförelse, uppgift 74, 2026-11-05/06

Fryst 40 MS/s, 60 rader, seed 1, deviation 2,8 MHz/V, kanal 12 MHz, video-LP 4,2 MHz. Samma hashbundna IQ per fall. PLL med kp 3/8, ki 1/32, amplitudvikt högst 2 och effekt-IIR 1/256. Siffrorna är simulering med originalets tidsaxel och synktolerans ±3. Ingen parameterjustering eller tidsförskjutning efter utfallet.

| Bitar/axel | C/N | SNR fasdifferens/PLL | Synkträffar fasdifferens/PLL |
|---|---|---|---|
| 4 | 4 dB | 5.62/9.33 dB | 0.000/0.000 |
| 4 | 8 dB | 10.59/12.93 dB | 0.034/0.017 |
| 4 | 12 dB | 14.78/16.31 dB | 0.186/0.085 |
| 7 | 4 dB | 5.15/9.92 dB | 0.000/0.000 |
| 7 | 8 dB | 11.34/13.68 dB | 0.068/0.034 |
| 7 | 12 dB | 15.65/17.44 dB | 0.305/0.068 |

SNR förbättras men synkmålet i Core #28 missas vid 8/12 dB. Tolv riktade modelltester passerar; en separat felteckenkontroll tappar både SNR och synk. Snabbsviten är gamingavbruten, 43 PASS/677 pending, och modellen är ännu inte publicerad i Core. [Full begränsning och testhistorik](../docs/IQ_PLL_PARTIAL_2026-11-05.md). Ingen FPGA-, RF-, provtagnings- eller räckviddsgaranti.

## Förslag till planen

- Uppgift 67 (ny): mottagargräns C i simulering: Python-modell av FM-demodulering ur 7 + 7-bitars IQ i
  40 MS/s på syntetisk FM-video (NTSC-komposit → FM-deviation som FPV-sändare → brus), mått på synklås
  och luma-SNR mot C/N, jämfört med 6-bitars kompositvägen; sedan Verilog med negativ kontroll. Ingen
  hårdvara förrän kortfrågan är löst.
- Ordning: måndag 64 på kortet, därefter 67 i simulering före 65 (färgen), eftersom 67 avgör vilken väg
  färgen ska byggas för.
