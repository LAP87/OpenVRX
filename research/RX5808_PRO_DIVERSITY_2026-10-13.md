# rx5808-pro-diversity och FENIX: vad vi tar med oss (2026-10-13)

Två öppna Arduino-/ESP32-projekt för RX5808-diversity, båda MIT. Inget lyfts in som kod (C++ mot Arduino och ESP32); lärdomarna nedan styr uppgift 13–15 i `docs/ARBETSPLAN_2026-10-12.md`.

- **sheaivey/rx5808-pro-diversity** (754 stjärnor, senast rört 2024-02): två RX5808, RSSI via Arduinons ADC, analog switch (4066) som byter kompositvideon, OLED-meny med auto scan, band scanner, RSSI-graf, kalibrering av RSSI min/max per modul och sparad senaste kanal. Dokumentet om SPI-modden av RX5808 (`docs/rx5808-spi-mod.md` i repot) är den bästa beskrivningen vi hittat och kan länkas från BRINGUP.
- **JyeSmith/FENIX-rx5808-pro-diversity** (110 stjärnor, senast rört 2021-03): samma kod på ESP32 i ett gogglemodulkort med pekplatta. Byter antenn i radtakt (15 kHz) med en SPDT-switch (TS5A3159) på RSSI samplad varje rad; spektrum över 72 kanaler; sveper i 1 MHz-steg över toppen och låser på sändarens verkliga centrum; 100 kΩ pulldown på RSSI; kalibrering vid första start mot en sändare på 25 mW intill. Noterar att RX5808-varianten med två extra lödflikar har större RSSI-omfång och lägre minimum.

Slutsatser för OpenVRX:
1. Byte i radtakt före avkodningen fungerar i praktiken (dekodern tål det), vilket stöder vår parning rad för rad efter avkodningen; vår väg slipper switchens ryck och kravet på lika fördröjning i mottagarna.
2. RSSI i fälttakt (50–60 Hz) räcker för tidig varning till mixern, scanning och logg: en I2C-ADC på rev A. Radtakt kräver minst 15–30 kSPS, alltså SPI-ADC eller FPGA med inbyggd ADC: rev B.
3. RSSI måste kalibreras per mottagare och sparas; utan det är värdet meningslöst.
4. Auto scan går att göra redan utan RSSI, på dekoderns lås och brusräkningen per kanal.
