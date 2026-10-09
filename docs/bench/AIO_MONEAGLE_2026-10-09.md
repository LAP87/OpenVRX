# Första bild: analog AIO-kamera → Moneagle

Rapporterat av projektägaren 2026-10-09. Resultatet är observerat på
bänken; Codex har inte själv utfört eller mätt testet.

## Uppställning och resultat

- Analog AIO-kamera med VTX, förpackning märkt **S2-OSD**.
- Kameran/VTX:n matades med **4,2 V från ett bänkaggregat**.
- **Eachine Moneagle** startades och visade kamerabilden direkt.
- Ingen manuell kanalsökning eller kanaländring behövdes.
- Byte mellan **PAL och NTSC provades inte**.

Detta bekräftar en fungerande bildkedja från kameran via dess sändare
till Moneagles mottagning och skärm i den provade uppställningen.
Det visar inte om monitorn använde en redan vald kanal eller automatisk
sökning. Aktivt band, kanal, frekvens och videostandard antecknades inte.

## Återstående kontroller

Nästa korta bänktest är att anteckna band/kanal och aktiv videostandard,
prova PAL respektive NTSC och kontrollera att bilden återkommer efter
omstart. Strömförbrukning, räckvidd, sändareffekt och latens är inte mätta.
Manualens uppgift om 25 mW är en specifikation, inte ett mätresultat.

Ingen Tang Nano, separat RX5808 eller TVP5150-modul ingick i detta test.
Resultatet verifierar därför inte OpenVRX-Core eller FPGA-bildkedjan.
