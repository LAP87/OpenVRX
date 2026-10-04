# Köra en analog AIO-kamera/sändare utan drönare eller FC

En AIO ("all-in-one") som S2-kameran i `bom/MONEAGLE_SPRINT_INKOP.md` är kamera + 5,8 GHz-sändare på samma lilla kort. Den behöver **ingen flygkontroller**: så fort den får ström sänder den kamerabilden. FC:n i en drönare gör bara två saker man inte behöver på bänken — matar ström och lägger ibland på OSD/byter kanal via SmartAudio.

## Steg för steg (S2-kameran enligt säljarens spec)

1. **Antennen på först.** Skruva/kläm fast antennen innan ström kopplas in. En sändare utan antenn kan skadas av sin egen effekt (energin reflekteras tillbaka). S2 har en fast trefoil-antenn — kontrollera att den sitter.
2. **Ström: 3,6–5,5 V, ca 0,4 A.** Enklast: offra en USB-kabel, klipp den, hitta + och − med multimeter (oftast röd = +5 V, svart = GND; datatrådarna isoleras), löd eller kläm till AIO:ns röda/svarta matningstrådar. Kontrollera polariteten med multimeter innan anslutning — fel polaritet kan förstöra kortet. Mata från en vanlig USB-laddare eller powerbank.
3. **Välj kanal med knappen:** kort tryck = kanal 1–8, långt tryck (> 1,5 s) = band A/B/E/F/R, mycket långt tryck (> 3 s) = NTSC/PAL. **Blå lysdiod tänd = NTSC** (det vi vill ha, se nedan).
4. **Moneagle:** starta, kör "Search"/auto-sök (eller välj samma band/kanal manuellt). Bilden ska komma direkt.
5. **Avstånd ≥ 1 m** mellan sändare och mottagare på bänken, annars kan mottagaren överstyras och bilden bli sämre trots stark signal.

## Lagligt i Sverige

PTS föreskrifter **PTSFS 2025:1, 3 kap. 204 §**: 5,725–5,875 GHz får användas utan tillstånd för "ospecificerat tillämpningsområde" med **högst 25 mW e.i.r.p.** (e.i.r.p. räknar in antennens förstärkning).
- S2 sänder fast 25 mW — det lägsta som finns på billiga AIO:er.
- **Välj kanaler inne i bandet med marginal**: 5 740–5 860 MHz. Bra val: **F4 = 5 800 MHz** eller **R4 = 5 769 MHz**.
- Undvik R1/R2 (5 658/5 695 MHz), R7/R8 och F8 (5 880 MHz och uppåt) — de ligger utanför bandet.

## Värme

Utan fartvind blir AIO:er varma (S2: ca 380 mA × 3,7 V ≈ 1,4 W på ett frimärke). Låt den ligga fritt (inte inbäddad), gärna en liten fläkt eller kylfläns vid långa bänkpass, och dra ur strömmen mellan testerna. Blir den för varm att hålla i — stäng av.

## NTSC eller PAL?

Ställ på **NTSC** (blå lysdiod). Moneagle och FPGA:n klarar båda, men XR-glasögon vill ha 60 Hz, och NTSC (59,94 Hz) slipper bildfrekvenskonvertering. M1-gatewaren visar 240 rader; NTSC har 243–244 aktiva rader per fält (PAL 288, beskärs).

## Användning i projektet

- **M1 (Moneagle → HDMI):** AIO:n på bordet riktad mot något med rörelse, Moneagle tar emot, FPGA:n lyssnar på Moneagles TVP5150 → HDMI till TV.
- **Latensriggen:** AIO:n riktad mot den slumpblinkande LED:en (`tests/latency/`), filma LED + skärm.
- **Mixer-inspelning senare:** samma AIO, två mottagare.
