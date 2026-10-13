# Mätprotokoll per milstolpe

Ett blad per mätning i tabellen "Mätningar när kortet finns" i [ARBETSPLAN_2026-10-05.md](ARBETSPLAN_2026-10-05.md), plus de mätpunkter som tillkommit sedan ([ARBETSPLAN_2026-10-12.md](ARBETSPLAN_2026-10-12.md), "Kräver kortet"): TV mot VCR, låsflaggan, genlockens klipp, jämförelse mot en färdig mottagare och glasögon. Material: [MATERIAL_UPPSTART.md](MATERIAL_UPPSTART.md). Koppling och felsökning: Core `gateware/BRINGUP.md`.

Skrivet 2026-10-12 ur Core `main` 3d4ed8f; blad 17–19 tillagda 2026-10-13 ur Core `main` bf05ac0. Inget här är mätt än; bladen fylls i på bänken och resultatet läggs i `docs/bench/` med datum.

## Gemensamt för alla blad

**Före varje mätning:** bygg bitströmmen och kontrollera manifestet, så att resultatet går att knyta till en källa.

```bash
gateware/build.sh <topp>
.venv/bin/python gateware/tools/build_manifest.py verify gateware/build/<topp>.build.json --root .
```

**Anteckna alltid:** datum, Tang-kortets revision (3923 krävs), toppmodul, Core-commit och manifestets SHA-256, seed, kamera och sändare (NTSC/PAL, kanal), skärm (modell, firmware), avstånd och antenner.

**Mätloggen (M6)** läses med `tools/snowlog.py`, en etikett per villkor. CSV-kolumner: `time, label, snow_a, snow_b, noise_a, noise_b, use_a, use_b, use_mix, channel, mhz, mode, filter, dropped, lost_a, lost_b, rssi_a, rssi_b, rssi_pct_a, rssi_pct_b, rssi_state_a, rssi_state_b` (RSSI sedan 2026-10-13; äldre CSV-filer får inga nya rader, skriv till en ny fil). `--summary` ger medianen per etikett. Ändra en sak i taget och jämför bara körningar med samma kamerabild: snövärdet beror också på bildinnehållet.

```bash
python gateware/tools/snowlog.py /dev/ttyUSB1 --label <villkor> --seconds 30 --out <fil>.csv
python gateware/tools/snowlog.py --summary <fil>.csv
```

**Latens** mäts med Core `tests/latency/`: en lysdiod som blinkar slumpvis mitt i kamerabilden, filmad med 240 bilder/s tillsammans med skärmen, minst 30 blinkningar per villkor, `python tests/latency/analyze_latency.py klipp.mp4 --capture-fps 240 --led x,y,w,h --screen namn=x,y,w,h`. Upplösning ±2 ms; median och standardavvikelse rapporteras.

---

## 1. M0: bild på tre skärmar

| | |
|---|---|
| Uppställning | Tang Nano 20K, USB-C, HDMI-kabel; tre olika skärmar eller TV, en i taget |
| Bitström | `m0_testpattern` |
| Logga | per skärm: bild ja/nej, tid till bild, vad skärmen rapporterar (upplösning, Hz), färgstaplarnas färger, om 4:3-ramen och den studsande kvadraten syns hela |
| Godkänt | bild på minst två av tre skärmar, 720p60 rapporterad |
| Underkänt | ingen bild någonstans: HDMI-nivåer eller tidtagning; kontrollera att `tools/tmds_fuses.py` ger "same" för bygget |
| Stänger | HDMI-nivåerna (arbetsplanen, M0) |

## 2. M2a: minnestestet, fas 180°, 225°, 270°

| | |
|---|---|
| Uppställning | bara Tang-kortet och USB-C |
| Bitström | `SDRAM_PHASE=8`, `10` (standard) och `12 gateware/build.sh m2a_memtest` |
| Logga | UART-raderna per läspunkt (`rs=0..7`, `err=`), varv för varv, minst en minut per fas; `err=00000001` medan S2 hålls intryckt (kontrollen att felräkningen fungerar) |
| Godkänt | en fas där `rs=5` är ren och läspunkten ett steg (0,96 ns) åt vardera hållet också är ren |
| Underkänt | ingen fas ger en ren `rs=5`: välj den fas och läspunkt som är renast och notera det; resultatet gäller då bara det bygget |
| Stänger | SDRAM-fas och läspunkt (arbetsplanen, M2a). Vald fas förs in som `PSDA_SEL` i `rtl/clocks_sdram.v`. Med I/O-register i I/O-cellerna (standard sedan 2026-10-12) ska resultatet gälla även bildbyggena; kontrollera det i blad 5 |

## 3. M3: proben med båda dekodrarna

| | |
|---|---|
| Uppställning | båda TVP-modulerna kopplade enligt BRINGUP 1, mottagarna på F4, kameran på |
| Bitström | `m3_probe`; vid tveksamma bitar även `PULL=UP` och `PULL=DOWN` |
| Logga | en rad per dekoder och sekund under minst en minut: `sclk`, `tog`, `hi`, `len`, `ln`, `xe`, `i2c`, `st`, `ri`, `fld` |
| Godkänt | båda dekodrarna: SCLK cirka 27 MHz, alla åtta bitar i `tog`, `len 1716-1716` (PAL `1728-1728`), `i2c OK`, låsbitarna satta i `st`, `ri` står still |
| Underkänt | felbilden slås upp i BRINGUP 4 |
| Stänger | kablaget; `fld` med den egna kameran (sammanflätad eller inte); om 03h läses tillbaka som 0Dh (annars startas dekodern om vid varje pollning och `ri` går till FF) |

## 4. M3: dra ur videon till en dekoder

| | |
|---|---|
| Uppställning | som blad 3; dra ur videokabeln till dekoder B i 10 s, sätt i, upprepa fem gånger |
| Bitström | `m3_probe` |
| Logga | för B under avbrottet: kommer rader (`ln`), med vilken längd (`len`), vad `st` visar; hur ofta 88h bit 4 sätts |
| Godkänt | ingen förväntan; mätningen ska ge beteendet |
| Stänger | om TVP5150 fortsätter leverera rader utan signal och med vilken timing; hur ofta 88h bit 4 sätts (arbetsplanen, M3). Svaret avgör hur mixern ska se en tyst mottagare |

## 5. M2: bild från en dekoder, BUF

| | |
|---|---|
| Uppställning | en dekoder med kamera; HDMI-skärm |
| Bitström | `m2_moneagle_color` (Moneagles dekoder, Core README "M1" och "M2") eller `m4_dual_mix` med en dekoder inkopplad |
| Logga | bild ja/nej, färger, om rader ersätts (syns som upprepade rader vid störning), bildryck vid panorering |
| Godkänt | stillastående, hel bild utan felaktiga rader vid god signal |
| Stänger | fältminnet på riktig SDRAM (arbetsplanen, M2). Bygget ska ha samma `SDRAM_PHASE` som blad 2 gav |

## 6. M4: antenn av, en mottagare i taget

| | |
|---|---|
| Uppställning | båda dekodrarna och mottagarna, samma kamera; ta bort antennen på A i 10 s, sätt tillbaka, sedan B |
| Bitström | `m4_dual_mix` (eller `m6_puck_proto` för loggen) |
| Logga | med M6: `snowlog.py` med etiketterna `ab`, `a_av`, `b_av`; `use_a`, `use_b`, `use_mix`, `dropped`. Med M4: lysdiod 1 och 2 (rader från A och B) och bilden. Filma skärmen för tiden till byte |
| Godkänt | bilden finns kvar hela tiden; bytet sker inom några rader; `!` (kolumnen `dropped`) kommer inte |
| Underkänt | svart bild eller frusen bild efter bytet, eller `!` i loggen |
| Stänger | mixerns byte och tid till byte (arbetsplanen, M4) |

## 7. M4: skriv om samma kanal med bild på

| | |
|---|---|
| Uppställning | som blad 6, bild på; i M6 tryck NEXT så att samma kanal väljs igen (band- eller kanalbyte fram och tillbaka) |
| Bitström | `m6_puck_proto` |
| Logga | filma skärmen; `snowlog.py` med etiketten `omskrivning` |
| Godkänt | ingen synlig störning när kanalen skrivs om |
| Stänger | om omskrivning av RX5808 stör bilden (arbetsplanen, M4). I dag skrivs kanalen inte om så länge en dekoder är låst; resultatet avgör om den regeln kan lättas |

## 8. M4: stillbild med vågräta kanter, sammanflätad kamera

| | |
|---|---|
| Uppställning | kameran riktad mot ett stilla motiv med vågräta kanter (till exempel ett rutat papper), sammanflätad kamera (M3:s `fld` visar det) |
| Bitström | `m4_dual_mix` |
| Logga | filma skärmen nära; kanterna ska stå still |
| Godkänt | kanterna står still |
| Underkänt | kanterna hoppar en halv rad upp och ned i bildtakt: fältfasen är fel håll |
| Stänger | att det nedre fältet hamnar lägre (arbetsplanen, M4; `field_phase.v`) |

## 9. M6: BUF mot HDMI-skärm

| | |
|---|---|
| Uppställning | full uppställning, HDMI-skärm, `BUF` i menyn |
| Bitström | `m6_puck_proto` |
| Logga | rivning vid panorering (filma), latens enligt "Gemensamt" med `BUF` och sedan med ett bygge där toppmodulen sätter `RT_EN = 0` (bara färdiga fält) |
| Godkänt | ingen rivning; latensen med följsam buffring lägre än med `RT_EN = 0` |
| Stänger | att följsam buffring inte ger rivning; upplevd latens mot `RT_EN = 0` (arbetsplanen, M6) |

## 10. M6: LOW mot skärm, goggles, brygga

| | |
|---|---|
| Uppställning | full uppställning, `LOW` i menyn; samma kamera mot HDMI-skärm, goggles med HDMI-ingång och, om den finns, en HDMI-brygga |
| Bitström | `m6_puck_proto` |
| Logga | per enhet: bild ja/nej, om den tar 750/751 rader (NTSC) eller 720p50 (PAL), vad den gör vid omlåsning (byt kanal, starta om kameran), tid till bild, latens enligt "Gemensamt" |
| Godkänt | bild utan avbrott under stabil signal; en omlåsning ger högst en kort bild |
| Stänger | om mottagaren tar 750/751 rader, och vad den gör vid omlåsning (arbetsplanen, M6). Fler enheter: blad 16 |

## 11. M6: snöloggen med dekoderkort och HDMI av/på, vid svag signal

| | |
|---|---|
| Uppställning | full uppställning; sändaren på avstånd eller med dämpning så att snö syns |
| Bitström | `m6_puck_proto` |
| Logga | `snowlog.py` med etiketterna `hdmi_pa` och `hdmi_av` (HDMI-kabeln i och ur), sedan dekoderkortet nära och långt från mottagarna; 30 s per villkor, upprepa varje villkor tre gånger |
| Godkänt | ingen skillnad i `snow_*` och `noise_*` mellan villkoren utöver spridningen mellan upprepningarna |
| Stänger | egenstörning, även i mellanfrekvensbandet (arbetsplanen, M6; Puck-konceptets EMI-tabell) |

## 12. TV mot VCR (`FILT`)

| | |
|---|---|
| Uppställning | samma kamera, kanal och avstånd; först god signal, sedan svag signal som i blad 11 |
| Bitström | `m6_puck_proto` |
| Logga | `snowlog.py`, etiketterna `tv_god`, `vcr_god`, `tv_svag`, `vcr_svag`; kolumnen `filter` ska visa `T` respektive `V`; `lost_a`, `lost_b`; filma skärmen för bildjämförelse (färgkanter, rörelse) |
| Godkänt | ingen förväntan; mätningen ska välja läge |
| Stänger | vilket fast TV/VCR-läge som håller låset och bilden bäst (ägarens fråga; Core README "02h"). Filtret i loggen är det begärda läget, inte en återläsning; vänta några sekunder efter ett byte |

## 13. Låsflaggan i loggen

| | |
|---|---|
| Uppställning | som blad 11 och blad 4: god signal, svag signal och en dekoder utan video |
| Bitström | `m6_puck_proto` |
| Logga | `snowlog.py`; `--summary` räknar rader med tappat lås per dekoder (`lost_a`, `lost_b`) |
| Godkänt | ingen förväntan |
| Stänger | om 88h bit 4 säger något på riktig signal som H- och V-låset inte redan säger (Core README M6 "88h bit 4"; arbetsplanen, "Nästa steg" punkt 4). Först därefter kan mixern använda den |

## 14. Genlockens klipp mot en riktig HDMI-skärm

| | |
|---|---|
| Uppställning | `LOW` i menyn, HDMI-skärm; starta om kameran eller byt kanal tio gånger, så att källan hoppar i fas |
| Bitström | `m6_puck_proto` |
| Logga | per omstart: svart avbrott ja/nej och hur länge, om skärmen visar en ny upplösningsruta, tid tills bilden är stilla |
| Godkänt | skärmen behåller synk genom klippet (den klippta bilden har en egen vsync-puls sedan C1) |
| Stänger | om klippet med bevarad vsync tas emot av en riktig skärm (arbetsplanen 2026-10-12, "Kräver kortet") |

## 15. Jämförelse mot en färdig mottagare med HDMI-utgång

| | |
|---|---|
| Uppställning | samma kamera och sändare; den färdiga mottagaren (en RC832HD är på väg) och pucken på samma kanal, var sin skärm av samma modell, eller samma skärm i tur och ordning |
| Bitström | `m6_puck_proto`, `BUF` och `LOW` |
| Logga | latens enligt "Gemensamt", båda skärmarna i samma klipp (två `--screen`-rutor); bild i brus sida vid sida på samma avstånd (filma båda skärmarna), samma villkor som blad 11 |
| Godkänt | ingen förväntan; jämförelsen är målet |
| Stänger | var pucken står mot en produkt i latens och bild i brus. Referensvärde utan pucken: Moneagle direkt, enligt hemmaplanens punkt 4 ([ARBETSPLAN_HEMMA_2026-10-12.md](ARBETSPLAN_HEMMA_2026-10-12.md)) |

## 16. Glasögon och HDMI-skärmar: fem steg

Femstegsplanen i [research/GOGGLES_OCH_XR_2026-10-12.md](../research/GOGGLES_OCH_XR_2026-10-12.md) ("Sju signalregler och en testplan i fem steg"). Ett blad per enhet. Glasögon via USB-C mäts först direkt och sedan via adaptern.

| Steg | Gör | Logga | Stänger |
|---|---|---|---|
| 1. EDID | läs EDID med en PC (`/sys/class/drm/card*-*/edid`, `edid-decode -c -n -p`; i Windows CRU eller Monitor Asset Manager) | rådumpen i `docs/bench/edid/<enhet>.txt` med firmwareversion; nativ och föredragen tidtagning; för glasögon om adaptern visar egen EDID | vad enheten annonserar |
| 2. PC-prov | lägg in proven P1–P7 från PC:n (CRU eller `xrandr --newmode/--addmode`): P1 720p60, P2 sann 59,94, P3 1650×751, P4 1650×757, P5 720p50, P6 1080p60, P7 1080p50 | per prov: bild, OSD-text, skalning, färgfel, tid till bild | enhetens egna gränser, skilda från FPGA:ns |
| 3. FPGA-matris | proven F1–F6 med dagens bygge: BUF med NTSC och PAL, LOW med NTSC och PAL, LOW utan insignal, LOW med fashopp, byten BUF↔LOW och NTSC↔PAL. F7–F9 kräver testbyggen (F8 är arbetsplanens uppgift 11 och kräver en större `LOW`-ring först, se Core README "Den varierande raden"; F9 är uppgift 10) | bild, OSD-text, svarta avbrott per tio minuter, tid till bild efter inkoppling och efter varje byte, lodrätt bildhopp, stabilitet 30 min | vilka av källans tidtagningar enheten tar |
| 4. Bildprov | M0-testbilden; när den finns, gråramp 0–255 med stegen 0, 4, 8, 16, 235, 245, 255 och ett rutnät med 1 pixels linjer | omfångsfel (krossad svärta, klippt vitt), skalning av 720p på 1080p-paneler, 4:3-fönstrets andel av panelen; PAL i BUF: ryck vid panorering | färgomfånget (avgör uppgift 10, AVI-infoframe) |
| 5. Latens | som "Gemensamt", först referens (analog skärm direkt), sedan varje enhet i BUF och LOW; glasögon filmas genom okularet; bryggan isoleras med en HDMI-delare och två `--screen`-rutor | median och standardavvikelse per enhet och läge | om LOW:s vinst överlever enhetens egen buffring |

Godkänt per enhet: P1 och F1 ger bild; övrigt är kartläggning. XR-glasögon väntas inte ta 720p (rapportens regel 6); ett nej där är ett resultat, inte ett fel i pucken.

## 17. RSSI: ADS1115 på rev A-kortet, kalibrering och varning

| | |
|---|---|
| Uppställning | rev A-kortet med ADS1115 (Puck `design/rev_a`), båda mottagarna med RSSI-stift på kontaktens stift 4, en sändare på fast kanal; först utan, sedan med sändaren |
| Bitström | `m6_puck_proto` |
| Före | mät varje mottagares RSSI-spänning med multimeter på testpunkten, sändaren av och sändaren intill: ligger den inom 0–3,3 V? Annars ska ADC:ns mätområde eller kopplingen ändras innan kortet används |
| Logga | RSSI-sidan och `snowlog.py` (`rssi_a`, `rssi_b`): rå kod mot multimeterns spänning på tre nivåer (kod × 125 µV); kalibrering via `CAL` med sändaren nära och långt bort; sedan en mottagare skärmad eller med antennen av: `rssi_state` ska bli `W` för den och mixern ska visa den andra (`use_a`/`use_b`) |
| Godkänt | koden följer spänningen inom någon procent; båda mottagarna får `OK` efter kalibrering; varningen kommer innan bilden från den svaga mottagaren blir snöig |
| Stänger | om RSSI-tröskeln (20 %, 3 avläsningar) och spannet (400 koder) passar riktiga mottagare, och om varningen hjälper mixern (arbetsplanen 2026-10-12, uppgift 13–14) |

## 18. SCAN: kanalskanning utan RSSI

| | |
|---|---|
| Uppställning | en sändare på en kanal som inte är F4, en andra sändare på en annan kanal om det finns, mottagarna på bänken |
| Bitström | `m6_puck_proto` |
| Logga | starta `SCAN` (huvudsidan, sjunde fältet); tid till klar, vald kanal; upprepa tre gånger; avbryt en skanning halvvägs med OK och kontrollera att startkanalen står kvar |
| Godkänt | skanningen hittar sändarens kanal, på 5–8 s; med två sändare den med minst brus; utan sändare `NONE` och startkanalen kvar |
| Stänger | om två brusfönster per kanal räcker, eller om grannkanaler (5 MHz isär hos en del band) lurar den (arbetsplanen 2026-10-12, uppgift 15) |

## 19. Sparade inställningar i kortets flash

| | |
|---|---|
| Uppställning | Tang Nano 20K med `m6_puck_proto` i flash |
| Bitström | `m6_puck_proto` (byggd med `--mspi_as_gpio`, se manifestets `mspi`) |
| Logga | ändra band, kanal, mixläge, latensläge och filter, vänta 5 s, bryt strömmen, slå på: står allt kvar? Gör om efter en RSSI-kalibrering. Programmera sedan om flashen över USB med samma bitström och kontrollera om inställningarna finns kvar |
| Godkänt | inställningarna finns kvar efter strömavbrott; USB-programmeringen fungerar som förut (en konstruktion som höll WP# högt hela tiden störde den) |
| Stänger | om skrivning till flashen fungerar på kortet och om programmering över USB raderar inställningarna (README under M6, "Sparade inställningar") |
