# Analoga mottagare med mixning — alla alternativ (2026-10-01)

Råfiler: `research/raw/rxmods/`, `research/raw/` (gårdagens butikssidor). Priser/lager kontrollerade 2026-09-30–10-01; "mixning" = tillverkaren påstår att två antennsignaler kombineras (inte bara växlas). Prestandaomdömen är användarrapporter.

## Översikt

| Modul | Kombinerar? | Pris | Lager (kontrollerat) | Fristående/utveckling | Omdöme (användare) |
|---|---|---:|---|---|---|
| **Skyzone SteadyView X (ground station)** | Ja: Mix1–3 + diversity | 193 USD | I lager hos Skyzone | **Enklast:** egen färgskärm + ratt, 3,5 mm AV-ut, USB-C eller 2–6S | Låser stabilt (V3.3 rekommenderas); flera rapporter om rullning i multipath med äldre SteadyView |
| Skyzone SteadyView X (Fat Shark-modul, "STVX") | Ja | 183 USD | I lager hos Skyzone | Skärm + ratt; video ut 1,0 Vpp/75 Ω; matning 6,5–26 V | som ovan |
| **SpeedyBee 5.8GHz Goggles Receiver** | Ja ("fusion") | 131,25 € inkl. svensk moms, fri frakt (combo) | n-Factory i lager; övriga slut/discontinued | OLED + 5-vägsknapp; Fat Shark-stift → kräver lödning/hylsa för fristående drift | Bra rapporter (höll bild där RapidFire rullade); verkar vara på väg ut |
| TBS Fusion | Ja (BrainFPV-fusion) | 168,99 USD (GetFPV), 129,99–134,95 USD andra | GetFPV i lager; TBS/ProgressiveRC slut | OSD i bilden; Fat Shark-fack, 5 V; extern matningssats ingår | J. Bardwell: "Fusion and Rapidfire have equal performance" |
| ImmersionRC RapidFire | Ja | ~187–196 USD (USA) | Delvis | Fat Shark-fack; knappar på modulen | "Holy grail"; ingen firmware sedan 2020; rullar ibland vid svag signal |
| **ClearView Goggle Receiver (Iftron)** | Ja — "not a diversity receiver"; låser och stabiliserar bilden | 219,95 USD | 25 st hos tillverkaren | Kanalbyte via Fat Shark-gogglarnas knappar → besvärlig fristående | Påstår ingen rullning/tearing efter lås (5–30 s) |
| Skyzone SteadyView V3.3 OEM | Ja | 157 USD | I lager | Styrs från Skyzone-goggles UI → nej | |
| Foxeer Wildfire | Oklart (dual receiver) | 199 USD | Slut | 5-vägsknapp, 400 mA | |
| Eachine Pro58 m.fl. (< 80 USD) | Nej, vanlig diversity | | | | Billigt, ingen mixning |

## Goggles där analogt redan är löst (som jämförelse)

| | Pris | Det som är intressant för oss |
|---|---:|---|
| HDZero Goggle 2 | 699,99 USD | Inbyggd analog mottagare (en antenn delad med HDZero), deinterlacer "utan fördröjning", analog <2 ms (tillverkaren), **HDMI in <1 ms**, AV in, modulfack för analoga moduler, 1080p OLED 46°. Gör mycket av det vi vill bygga — men kostar. |
| Fat Shark Dominator HD-serien (begagnad) | ~2 000 kr (projektägarens erbjudande, HD2 + modul) | 800×600, ca 50° diagonalt (Dominator HD enligt säljartext), **HDMI-ingång**, DVR, modulfack för alla moduler ovan. |

## Vad en mixande modul ger oss

1. **Flyga analogt med bra bild nu**, oberoende av utvecklingen.
2. **Referens att slå:** spela in samma flygning med modulen och med vår egen mixer — utan ett facit vet vi inte om vår mixer är bra.
3. **CVBS-källa** till konverterare/XR-kedjan och till FPGA-utvecklingen.

Den behövs **inte** för att utveckla vår egen mixer: det kräver två *separata* mottagare (modulens utgång är redan mixad). Det täcks av utvecklingssatsen (`bom/GATEWARE_DEVKIT.md`).

## Rekommendation "enklast för utveckling"

- **Mest plug-and-play:** SteadyView X ground station (193 USD): skärm, ratt, AV-ut, USB-C-matning — rakt in i Moneagle eller konverteraren, ingen lödning.
- **Om HD2-erbjudandet tas:** sätt en mixande modul i dess fack (SpeedyBee eller Fusion) — då har vi en komplett referensgoggle *och* en skärm med HDMI-ingång för att titta på FPGA-utgången.
