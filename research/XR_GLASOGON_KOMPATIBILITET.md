# XR-glasögon för analog FPV — kompatibilitet (2026-10-01)

Råfiler: `research/raw/xr/` (Reddit via OpenCLI, XREAL-dokumentation). Användarrapporter är inte mätningar om inget annat anges.

## Slutsats

1. **Mata glasögonen med 1080p60.** Tre oberoende rapporter om att 720p inte fungerar: VITURE Pro XR ("rainbow screen" vid 720p), XREAL XBX ("no signal" vid 720p), VITURE i intofpv-tråden (720p saknas i EDID).
2. **Undvik 50 Hz.** XREAL:s egen tabell listar bara 60/72/90/120 Hz för alla modeller (gäller utvecklarläget; extern 50 Hz-ingång är inte bekräftad åt något håll). Analog kamera i NTSC, eller konverterare som ger 1080p60 oavsett källa.
3. **Latens med HDMI→USB-C-kedja:** en användare uppger **45–55 ms vid 1080p60** (VITURE Pro XR + Caddx Ascent VRX + samma typ av HDMI-adapter). intofpv-användaren: ca 60 ms (VITURE, digital HD-källa). En kommentar återger "20–50+ ms extra" från en YouTuber. Ingen av dem beskriver mätmetod. → Ligger nära vårt arbetsmål (≈ 50 ms); mät själv.
4. **Analog fungerar i praktiken:** en användare kör Skyzone M5-monitorns videoutgång → AV→HDMI-konverterare för ca 5 € (användarens uppgift, läst 2026-10-01) → XR-glasögon och upplevde ingen märkbar latens. Han behövde Skyzones mix-läge eftersom switch-läget tappade bilden vid start — stöd för att mixning spelar roll även här.

## XREAL-modeller (tillverkarens tabell)

| Modell | Vikt | Upplösning/öga | FOV | Bildfrekvenser |
|---|---:|---|---:|---|
| Air | ~77 g | 1920×1080 | 46° | 60, 72 Hz |
| Air 2 | ~72 g | 1920×1080 | 46° | 60, 72, 90, 120 Hz |
| **Air 2 Pro** | ~75 g | 1920×1080 | 46° | 60, 72, 90, 120 Hz |
| Air 2 Ultra | ~80 g | 1920×1080 | 52° | 60, 72, 90, 120 Hz |
| One | 82 g | 1920×1080 | 50° | 60, 72, 90, 120 Hz |
| One Pro | 87 g | 1920×1080 | 57° | 60, 72, 90, 120 Hz |
| 1S | 82 g | 1920×1200 | 52° | 60, 72, 90, 120 Hz |

Källa: [docs.xreal.com/XREALDevices/XREAL Glasses](https://docs.xreal.com/XREALDevices/XREAL%20Glasses). XREAL One-serien: "Devices with an HDMI port can be connected … via an HDMI-to-USB-C adapter", kräver DP + 5 V/1 A, inget inbyggt batteri.

## Ström

Glasögonen har inget batteri och matas via USB-C. Adaptern (Guermok i inköpslistan) har en separat 5 V-port (1–1,5 A) som måste vara inkopplad. En användare noterade att USB-C PD-matningen var begränsande med en liten powerbank (intofpv).

## Ergonomi och optik (användarrapporter)

- Lätta, ljusa, bra färger; ljusläckage hanteras med glasögonens svarta skydd.
- Fokus: när drönaren är nära och syns i nedre synfältet måste man koncentrera sig för att inte fokusera förbi bilden (intofpv).
- 46° FOV (Air 2 Pro) är smalare än typiska FPV-goggles; One Pro har 57°.

## Rekommendation för experiment 1

- **XREAL Air 2 Pro begagnad (2 800 kr, 2026-10-01)**: 60 Hz-stöd bekräftat av tillverkaren, lättast, billigast.
- Ställ konverteraren på **1080p60**. Testa NTSC-läge på kameran först.
- Uppgradering senare: One Pro (57° FOV) om 46° känns trångt.

## Öppet (mäts i experimentet)

- Faktisk latens i vår kedja (SpeedyBee → CVBS→HDMI-modul → adapter → Air 2 Pro).
- Vad glasögonen visar när konverteraren tappar synk (svart, blått, frys).
- Om Air 2 Pro accepterar 1080p50 (PAL-läge).
