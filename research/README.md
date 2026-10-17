# Underlag i `research/`

En rad per fil: datum, ämne, om den gäller, och vilket beslut eller vilken uppgift den matar. Anteckningarna själva ändras inte; när något i dem har ersatts står det här. Besluten finns i [`docs/BESLUT_2026-10-12.md`](../docs/BESLUT_2026-10-12.md) (numrerade), uppgifterna i arbetsplanerna under `docs/`. Registret gäller 2026-10-17.

"Rensad 2026-10-12" betyder att butiker, butikslänkar och odaterade priser togs bort enligt inköpsregeln (uppgift 8b), inget annat. Status: **gällande**, **delvis ersatt** (vad), **ersatt av** (vad), **historisk** (sparad som underlag, inget att göra).

## Anteckningar

| Fil | Datum | Ämne | Status | Matar |
|---|---|---|---|---|
| [DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md](DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md) | 2026-09-30, rensad 2026-10-12 | Dekoderval för rev A, FPV-förebilder, latensmål 50 ms | delvis ersatt: GPL-projekten som kodkälla (beslut 3, 2026-10-12: aldrig GPL-kod) | dekoder och ingångssteg på rev A; latensmålet |
| [BANDPASSFILTER_DIVIMATH.md](BANDPASSFILTER_DIVIMATH.md) | 2026-10-01, rensad 2026-10-12 | SMA-bandpassfilter 5–6 GHz: data, vad det dämpar | historisk (försöket det var tänkt för finns inte i någon plan; filterfrågan förs vidare i RF-underlaget, åtgärd 6) | RF_DIVERSITY, avsnitt 5 |
| [MONEAGLE_TEARDOWN.md](MONEAGLE_TEARDOWN.md) | 2026-10-01 | Moneagles insida enligt en isärtagning från 2020, avtappning av BT.656 | delvis ersatt: avtappningen, av egna dekodermoduler (`docs/handoff/2026-10-06/AUDIT.md`, avsnitt 7 punkt 5) | M1/M2 med Moneagle; MATPROTOKOLL blad 5 |
| [MOTTAGARE_ALTERNATIV.md](MOTTAGARE_ALTERNATIV.md) | 2026-10-01, rensad 2026-10-12 | Analoga mottagare som mixar, goggles med HDMI-ingång, med daterade priser | historisk (köpunderlag från oktobers första dagar) | DEKODER_OCH_SYNK avsnitt 1; MATPROTOKOLL blad 15 |
| [XR_GLASOGON_KOMPATIBILITET.md](XR_GLASOGON_KOMPATIBILITET.md) | 2026-10-01, rensad 2026-10-12 | XR-glasögon och analog FPV: 720p, 50 Hz, latensrapporter | ersatt av [GOGGLES_OCH_XR_2026-10-12.md](GOGGLES_OCH_XR_2026-10-12.md) och [UTGANG_1080P_2026-10.md](UTGANG_1080P_2026-10.md) | beslut 6; granskningen 2026-10-05 |
| [ALTERNATIVA_VAGAR_2026-10-02.md](ALTERNATIVA_VAGAR_2026-10-02.md) | 2026-10-02, rensad 2026-10-12 | Hela vägar från mottagare till ögonen, utbytbara block | delvis ersatt: HDMI-blocket och 1080p-provet, av UTGANG_1080P och beslut 6 (1080p senare, M0 i 720p60 först) | rev A som dekoderkort; uppgift 12 |
| [C5VRX_OCH_OPENDRONE_2026-10-03.md](C5VRX_OCH_OPENDRONE_2026-10-03.md) | 2026-10-03 | ESP32-C5 som analog mottagare (C5VRX); OpenDrone-hw | delvis ersatt: licensstycket (beslut 3) | beslut 3; regeln om 5,8 GHz-antenn i AGENTS.md |
| [CVBS2HDMI_2026-10-04.md](CVBS2HDMI_2026-10-04.md) | 2026-10-04 | otanl/CVBS2HDMI på Tang Nano 20K; vår kod kontrollerad mot dess fällor | historisk (åtgärderna gjordes 2026-10-04) | reglerna om `signed` och LVDS-banken i AGENTS.md |
| [DEKODER_OCH_SYNK_ROBUSTHET_2026-10-05.md](DEKODER_OCH_SYNK_ROBUSTHET_2026-10-05.md) | 2026-10-05, rensad 2026-10-12 | Dekoder vid svag signal, döljning av dåliga rader, svänghjulstidbas | gällande (svänghjulet är öppet) | Fas 7 och Nästa steg 3, 4 och 6 i ARBETSPLAN_2026-10-05; MATPROTOKOLL blad 13 |
| [RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md](RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md) | 2026-10-05, tillägg 2026-10-17 | RX5808, diversity per rad, kvalitetssignal per rad, egenstörning, antennhöjd; tillägget: Bardwells klipp om RX5808-modulens brist och ESP32-C5 som mottagare | delvis ersatt: RSSI per rad via SPI-ADC, av beslut 7 (I2C-ADC i fälttakt på rev A, radtakt först på rev B); kretsarna i de dyra mottagarna (avsnitt 1, "Alternativ") av MOTTAGARKRETSAR_2026-10 | brusmåttet; Nästa steg 5 och 9; MATPROTOKOLL blad 11; livscykelrisken i Pucks `design/rev_a/LIFECYCLE.md` |
| [UTGANG_OCH_LATENS_2026-10-05.md](UTGANG_OCH_LATENS_2026-10-05.md) | 2026-10-05 | Buffring, `LOW`-timing, deinterlacing och skalning, sändare för 1080p | delvis ersatt: avsnitt 3 av UTGANG_1080P; den varierande raden avgjord i uppgift 11 (efter vsync som standard); 1080p-provet av beslut 6 | Fas 5; uppgift 9, 11 och 12 |
| [GOGGLES_OCH_XR_2026-10-12.md](GOGGLES_OCH_XR_2026-10-12.md) | 2026-10-12 | Skärmar och glasögon med HDMI-ingång: signalregler, testplan i fem steg | delvis ersatt: "utgången bara DVI" och "radens plats olöst" (uppgift 10 och 11, Core 9164d12 och 46a1e4f); köpförslaget obesvarat | uppgift 7, 10, 11, 12; MATPROTOKOLL blad 16; hemmaplanen punkt 3 och 5–9 |
| [RX5808_PRO_DIVERSITY_2026-10-13.md](RX5808_PRO_DIVERSITY_2026-10-13.md) | 2026-10-13 | rx5808-pro-diversity och FENIX: RSSI-kalibrering, skanning, byte i radtakt | gällande | beslut 7; uppgift 13–15 |
| [UTGANG_1080P_2026-10.md](UTGANG_1080P_2026-10.md) | 2026-10-13 | Tre vägar till 1080p60 och vad som måste mätas för var och en | gällande | beslut 6; uppgift 12 |
| [MOTTAGARKRETSAR_2026-10.md](MOTTAGARKRETSAR_2026-10.md) | 2026-10-17 | Mottagarkretsen i HDZero, SteadyView, rapidFIRE, Fusion och Fat Shark Scout, belagd med FCC, tillverkarens dokument, källkod och foton; RichWaves mottagarlista | gällande | uppgift 30; valet av mottagare för rev B |

## Komponentregistret och råunderlag

| Fil | Datum | Ämne | Status | Matar |
|---|---|---|---|---|
| [komponentregister/README.md](komponentregister/README.md) | 2026-10-06, uppdaterad 2026-10-08 | Läsvy över 313 poster (komponenter, projekt, gränssnitt) och rev A-BOM:ens positioner | delvis ersatt: BOM-delen gäller 114 positioner; rev A har 126 delar efter beslut 5 och 7 | — |
| [komponentregister/components.csv](komponentregister/components.csv) | 2026-10-06, uppdaterad 2026-10-08 | Registret: MPN, livscykel, källa, nästa kontroll | delvis ersatt: som README.md (ADS1115 och den andra ESD-klampen saknas) | — |
| [komponentregister/sources.csv](komponentregister/sources.csv) | 2026-10-06, uppdaterad 2026-10-08 | 28 källor med version, läsdatum och SHA-256 | gällande (varje rad gäller sin version) | — |
| [komponentregister/render.py](komponentregister/render.py) | 2026-10-06, uppdaterad 2026-10-08 | Skriver README.md ur CSV-filerna; `--check` kontrollerar | gällande | — |
| [raw/goggles_2026-10-12/](raw/goggles_2026-10-12/) (fyra filer, engelska) | 2026-10-12 | Råunderlag till GOGGLES_OCH_XR: bryggor och signalregler, goggles med HDMI-ingång, recensioner med priser från datumet, XR-glasögonens specifikationer | historisk (råunderlag) | GOGGLES_OCH_XR, regel 1–6 och rangordningen |

## Rader som ett senare beslut har ändrat

Anteckningarna är orörda; här är meningarna som inte längre gäller.

- DEKODRAR, rad 90, och C5VRX, rad 23: GPL-kod som startpunkt. Beslut 3: CERN-OHL-S-2.0, aldrig GPL-kod.
- DEKODRAR, rad 63: "standardtiming". Beslut 1 behåller `LOW` med 750/751 rader.
- ALTERNATIVA_VAGAR, rad 44, och UTGANG_OCH_LATENS, rad 18 och 20: 1080p till glasögonen först. Beslut 6: senare, M0 i 720p60 först.
- UTGANG_OCH_LATENS, rad 40: den varierande raden före vsync. Uppgift 11 gjorde placeringen valbar med raden efter vsync som standard.
- GOGGLES, rad 70: radens plats "olöst". Uppgift 11 gjorde den valbar (`WAIT_BEFORE_VSYNC`), så testbygget F8 går att göra.
- GOGGLES, regel 4 (rad 74) och testbygget F9: utgången utan AVI-infoframe. Uppgift 10 lade till `HDMI=1`.
- RF_DIVERSITY, rad 22 och 138: RSSI per rad via SPI-ADC. Beslut 7.
- CVBS2HDMI, rad 35: 1080p med bildbuffert. Core ger 720p (beslut 6).
- komponentregister/README.md, rad 5 och 25: 114 positioner och Tang Nano 20K "beställd". Rev A har 126 delar, och kortet finns hemma.

Hänvisningar i anteckningarna till `bom/`, `research/LT8618SX_INIT.md` och andra underkataloger i `research/raw/` än `goggles_2026-10-12` pekar på filer som inte finns i repot.
