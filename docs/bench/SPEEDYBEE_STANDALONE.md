# SpeedyBee 5.8GHz Goggles Receiver utanför goggles

Status 2026-10-01: sammanställt från källor, **inte provat på en fysisk modul**. Källor i `research/raw/exp1/`.

## Vad modulen behöver

| | Värde | Källa |
|---|---|---|
| Matning | 5 V, 450 mA | SpeedyBee-manualen (EN, 2023-09-04) |
| Kontakt | 9 stift, 2,54 mm delning (Fat Shark-modulfack) | TBS Fusion-manualen anger samma fack som "2,5mm pin header, 9 Pins"; SpeedyBee anger Fat Shark Dominator-kompatibilitet |
| Styrning | Egen OLED 128×64 + 5-vägsknapp på modulen | SpeedyBee-manualen |
| Antenner | 2× SMA-hona (yttergänga, hål); combon har RHCP patch + RHCP lollipop | Manualen, n-Factory |
| Firmware | USB-kontakt på modulen | Manualen |

Modulen behöver alltså **ingen** styrning från goggles: kanal, band, skanning, RSSI-OSD, ljud och kalibrering sköts med knappen. En användare på intofpv körde den i Skyzone-goggles via AV-ingången med separat matning (Y-kabel), vilket stöder fristående drift.

## Pinout (att verifiera)

Oscar Liangs bild för Fat Shark-modulfacket, som han kallar universell (`research/raw/exp1/fatshark_module_pinout_oscarliang.jpg`):

| Stift | Funktion |
|---:|---|
| 1 | +5 V in |
| 2 | RSSI (NC i hans bygge) |
| 3 | GND |
| 4 | Ljud |
| 5 | Ljud |
| 6 | **Video (CVBS)** |
| 7 | Kanalval 3 (NC) |
| 8 | Kanalval 2 (NC) |
| 9 | Kanalval 1 (NC) |

Bilden visar en annan modul än SpeedyBee, och en Reddit-tråd klagar på motstridiga pinouts. Därför:

### Mätning innan första ström (5 minuter, multimeter)

1. Utan ström: sök det stift som har **kontakt med SMA-kontakternas ytterhölje** → GND. Enligt bilden stift 3.
2. Sök stiftet bredvid som **inte** är kortslutet mot GND men ligger på en kraftig ledare/kondensator → 5 V-kandidat (stift 1).
3. Video-stiftet har normalt en låg resistans mot GND via utgångssteget/75 Ω, men inte kortslutning. Mät och anteckna alla 9 stift mot GND.
4. Om något inte stämmer med tabellen: stoppa och fotografera kortet; vi jämför med SpeedyBees bilder innan ström.
5. Första ström via labbagg eller USB med strömbegränsning ~0,6 A om möjligt. OLED ska tändas.

## Koppling i experiment 1

```
PD-powerbank ──USB-A 5 V──► stift 1 (+5 V), stift 3 (GND)        SpeedyBee
                                                   stift 6 (video) ──► RCA-hane ──► Moneagle AV-in   (steg 1)
                                                                              └──► CVBS→HDMI-modul (steg 2)
```

- Videon är 75 Ω CVBS. Korta ledare, skärmad kabel om den blir längre än ~20 cm. Gemensam jord mellan modul och mottagande enhet.
- Ljud behövs inte i experimentet; lämna stift 4/5 oanslutna.
- 3D-printa en hållare med 1×9 stifthylsa (projektägarens skrivare) så modulen inte bär på kablarna.

## Saker att observera

- **Vad visas vid svag signal?** Oscar Liang lade en DVR mellan mottagare och monitor för att få "snowy screen" i stället för "blue screen". Moneagle och konverterarna kan blåskärma; anteckna beteende och återhämtningstid.
- **Kalibrering:** manualen beskriver tvåstegs-kalibrering (utan antenner/VTX på A1, sedan VTX 25 mW på 1 m). Görs bara om bilden är dålig.
- **Antenner:** intofpv-användare påpekar att mixning fungerar bäst med likadana antenner på båda ingångarna; combon har patch + lollipop. Prova båda kombinationerna om det finns tid.
