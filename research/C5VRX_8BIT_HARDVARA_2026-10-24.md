# ESP32-C5-hårdvara för en digital C5VRX-väg med 8 bitar (2026-10-24)

Fråga från ägaren 2026-10-24: RX5808 är svår att få tag på, så en OpenVRX byggd på C5VRX som
mottagare är det realistiska spåret. Upphovsmannen nämner själv att en 8-bitars utgång skulle ge
bättre upplösning. XIAO ESP32-C5 har inga stift kvar: vilken hårdvara har det, och vad kostar det i
firmware? Inga butiker eller priser här (beslut 4).

## Vad som behövs i stift

C5VRX-5 på XIAO:n använder i dag 14 av kortets 15 åtkomliga GPIO:er: åtta pads för IQ-slingan
(Wi-Fi-kretsens diagnostikbuss ut på pads och tillbaka in i PARLIO RX; GPIO 1, 0, 25, 7, 10, 5, 3, 4)
och sex för videobussen (PARLIO TX, GPIO 23, 24, 11, 12, 8, 9 = D4–D9). PARLIO TX är konfigurerad med
åtta lanes; lane 6 och 7 saknar stift. Den sista paden, MTMS/GPIO2, tar vår sampelklocka.

| Behov | Stift | Varför |
|---|---|---|
| IQ-slinga som i dag (4 + 4 bitar) | 8 | fast i dagens demodulator |
| IQ-slinga bredare (5 + 5 eller 6 + 6) | 10–12 | upphovsmannens egen framtidspunkt (hans `AGENTS.md`: "Wider I5/Q5 or I6/Q6"); höjer brusgolvet i demodulatorn, det riktiga taket i dag |
| Videobuss 8 bitar | 8 | upplösning i luma och i färgbärvågen |
| Sampelklocka ut | 1 | den digitala vägen (uppgift 63–64) |
| Statusrad på UART | 1 | önskvärd, inte nödvändig |

Summa 18 med dagens IQ, 20–22 med bredare IQ.

## Vad ESP32-C5 har

Enligt Espressifs datablad för modulerna ESP32-C5-WROOM-1 och -1U (v1.3, 2026-09-03;
[datablad](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)):

- 22 GPIO:er ute på modulen: GPIO0–15 och 23–28. GPIO13/14 är USB (konsol och flashning), GPIO15 är
  PSRAM-chipselect på varianter med PSRAM. Kvar: 19 fria med PSRAM-variant, 20 utan.
- Strappstift: 26, 27, 28 (startläge), 25 och 3 (SDIO-flanker), 7 (JTAG-källa), 2 (MTMS). De går att
  använda som utgångar efter start om nivån vid reset respekteras; C5VRX gör redan så med 25, 7, 3, 4 och 5.
  På vår sida är de ingångar i FPGA:n, som inte driver något under ESP32:ans reset.
- WROOM-1U har antennkontakt (kompatibel med U.FL, I-PEX MHF I och Amphenol AMC) och ANT1 aktiv;
  WROOM-1 har PCB-antenn för 2,4 och 5 GHz, vars prestanda vid 5,8 GHz vi inte känner.
- Radion är densamma som i XIAO:n (samma krets, ingen extern LNA någonstans): mottagningen blir inte
  bättre av bytet, bara stiftbudgeten.

Stiftbudgeten räcker alltså: 8 IQ + 8 video + 1 klocka + 1 UART = 18 av 19. Bredare IQ (10) och 8 bitar
video med klocka ger 19, utan UART. Allt ryms bara på ett kort som lägger ut modulens alla stift.

## Kandidater

| Kort | GPIO:er åtkomliga | Antenn | Kommentar |
|---|---|---|---|
| Seeed XIAO ESP32-C5 (dagens) | 11 på kanten + 4 JTAG-pads på baksidan | U.FL | fullt utnyttjat; 6 bitar och klockan på MTMS är slutet ([stiftkarta](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/)) |
| ESP32-C5-WROOM-1U-modul på eget kort | 22 (GPIO15 bara utan PSRAM) | kontakt, U.FL-kompatibel | rev B-spåret: modulen löds på vårt kort, två stycken för diversity, bussarna rakt in i FPGA:n; firmwaren behöver en stifttabell för kortet |
| ESP32-C5-WROOM-1 på eget kort | 22 | PCB-antenn | samma som ovan men utan extern antenn; 5,8 GHz-prestanda okänd, inte för FPV |
| ESP32-C5-DevKitC-1 | alla utom flashbussen, på stiftlister ([bruksanvisning](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html)) | modulens; kortet säljs med WROOM-1 (PCB-antenn), 1U-variant inte bekräftad | bänkkort för att prova stifttabellen och 8 bitar före rev B; J1/J3 ändrades från tillverkningsnummer PW-2025-04-0446, läs etiketten |
| ESP32-C5-MINI-serien | finns i Espressifs sortiment | 1U-variant med kontakt | stiftlistan inte kontrollerad här |

## Firmwaresidan

- C5VRX-5 har stiften hårdkodade (`main/transport.c` `s_dac_gpio`, `main/rf.c` `s_iq_pins`). Den äldre
  generationen C5VRX-3 (`legacy/c5vrx3/main/board_config.h`) hade stifttabeller i Kconfig och en väg för
  `CONFIG_C5VRX_DAC_BITS == 8`. En kortkonfiguration är alltså en måttlig ändring med förebild i hans eget
  träd, inte ett nytt grepp.
- Det avgörande är om demodulatorns utgångstabell bär åtta betydande bitar i dag, så att lane 6 och 7
  får riktig information när de får stift. Frågan ligger i GitHub-ärendet.
- IQ-breddningen är hans utvecklingsspår; vår del är bara att inte låsa stiften.

## Vad det betyder för OpenVRX

Rev B som "två ESP32-C5-WROOM-1U-moduler + FPGA + HDMI": ingen RX5808, ingen TVP5150, varje modul ger
8 bitar plus klocka rakt in i FPGA:n (18 ingångar för två kanaler, samma antal som två TVP:er tar i dag).
TVP-vägen kan finnas kvar som option för analoga moduler, men behöver inte bygga kortet. Mottagningens
kvalitet är då C5VRX:s och upphovsmannens arbete; vår del är sync, färg, mixning och utgång, mätt med
riggen. Modulerna drar strömtoppar på Wi-Fi-radion; 3,3 V-matningen dimensioneras för det.

## Att avgöra

- Ägaren: rev B-riktningen (uppgift 66) mot moduler, och om ett DevKitC-1 ska in på bänken för att prova
  stifttabellen innan kortet ritas.
- Upphovsmannen: 8-bitars utgångstabell, kortkonfiguration i C5VRX-5, intresse för en modulvariant.
