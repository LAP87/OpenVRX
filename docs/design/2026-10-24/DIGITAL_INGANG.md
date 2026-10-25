# Digital videoingång från C5VRX: sex datatrådar och en klocka i stället för DAC och TVP

**Körschema för måndag 26 oktober:** [fryst firmware, kontrollerade filer och koppling](../../bench/MANDAG_2026-10-26.md). Det provet använder fortfarande `388d2d1` + privat GPIO2-patch. Texten nedan är underlaget från 24 oktober; dess krav på M6:s B-logg/fältdump och ett omedelbart godkänt A/B-diversityprov gäller inte den byggda M4-toppen. Hälsogrinden och mätuttaget behöver separat arbete (arbetsplan uppgift 69).

Underlag 2026-10-24 (Fable) för uppgift 63–66. Ägarens fråga: kan C5VRX med små ändringar ge en perfekt bild hos oss? Svaret avgörs av två saker som går att skilja åt: vad mottagaren själv levererar (dess tak) och vad vår väg från den gör med det (vår förlust). I dag går vägen genom en 6-bitars motstånds-DAC på kopplingsplatta och en TVP5150 som tappar färglåset. Den här noten beskriver vägen där FPGA:n tar samplen direkt.

## Vad källkoden säger (C5VRX-5, commit `388d2d1`, läst 2026-10-24; GPL-3.0, inget kopierat)

| Sak | Fakta | Var |
|---|---|---|
| Videoutgång | PARLIO TX, utklocka 40 MHz, databredd 8, stift `{23, 24, 11, 12, 8, 9, -1, -1}` = XIAO D4–D9, LSB först, data skiftas på negativ flank, klockutgång avstängd (`clk_out_gpio_num = -1`) | `main/transport.c`, `prepare_tx()` |
| Innehåll | FM-demodulerad komposit (synk, burst, luma med färgbärvågen), 6 bitar använda av 8 lanes | `main/transport.c`, demodulatorprogrammen `u85q*.bsasm` |
| Mottagarens upplösning | 4 bitar I och 4 bitar Q ("ultrafine Q4/I4") från Wi-Fi-kretsens diagnostikbuss, 40 MS/s in i PARLIO RX; pads GPIO 1, 0, 25, 7, 10 (= D0, D1, D2, D3, D10) och 5, 3, 4 (JTAG-pads på baksidan) | `main/rf.c`, `main/transport.c` |
| Ledig pad | GPIO2 (MTMS, baksidan). Synkhjulets utgångsprob speglar DATA4 dit och vägrar om paden är upptagen ("mirror_occupied") | `main/sync_output_probe.c` |
| Nivåer | OUTPUT 0–9; 9 = "low swing: halverar brus och klippning, kräver känslig synk" | `main/control.c`, `main/menu.c` |
| Egenstörning | DAC:en och PARLIO-klockan intill antenningången höjer brusgolvet; mäts med konsoltangent N | `main/calibration.c` |
| Konsol | ESP-IDF:s standardkonsol på USB-JTAG-porten, ingen DTR/RTS-hantering, ingen UART | `sdkconfig.defaults`, `main/` |
| Blackbox | per sekund: C/N, nivå i dBm, andel fönster med synk, avbrottskategori, förstärkning, DC-servo, AFC, H/V-lås i procent, längsta H-avbrott; CSV från webbsidan | `main/flightlog_format.h`, `web/flight-log.js` |

Stiftkartan är Seeeds ([XIAO ESP32-C5 getting started](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/)): D0 = GPIO1, D1 = GPIO0, D2 = GPIO25, D3 = GPIO7, D4 = GPIO23, D5 = GPIO24, D6 = GPIO11, D7 = GPIO12, D8 = GPIO8, D9 = GPIO9, D10 = GPIO10; MTMS/MTDI/MTCK/MTDO är pads på baksidan. Alla elva kantstift är alltså upptagna av C5VRX; klockan får MTMS.

## Firmwareändringen (privat bygge, utanför våra repon)

En rad i `prepare_tx()`: `.clk_out_gpio_num = 2` bakom en kompileringsflagga (`C5VRX_CLK_OUT_GPIO`), annars oförändrat. Synkhjulets prob ser paden upptagen och avstår av egen kraft; bygget körs därför med synkhjulet av (konsol `U`, sparas), vilket också är vad vi vill: FPGA:n gör sin egen synkbehandling på den råa demodulerade signalen. Bygget görs med ESP-IDF 6.0.2 i WSL; `FIRMWARE`-raden märker trädet som ändrat. Flashas med webbflasharens "Local File" (appen på 0x10000 enligt `partitions.csv`) eller esptool. Det är allt som behövs på XIAO-sidan för att prova. En statusrad på UART (ägarens punkt 1) är en separat, senare ändring och i första hand en önskan uppströms.

## Kopplingen

| XIAO | Signal | Tang Nano 20K (dekoder B:s plats, `BRINGUP.md`) |
|---|---|---|
| MTMS-pad (GPIO2), tunn tråd lödd på baksidan | sampelklocka 40 MHz | J5-4 (PIN80, GCLKT: klockingång) |
| D4 | bit 0 | J5-3 (PIN76) |
| D5 | bit 1 | J5-5 (PIN42) |
| D6 | bit 2 | J5-6 (PIN41) |
| D7 | bit 3 | J5-10 (PIN48) |
| D8 | bit 4 | J5-12 (PIN49) |
| D9 | bit 5 | J5-13 (PIN86) |
| GND | jord | GND |

3,3 V-logik på båda sidor, korta trådar (40 MHz). DAC-motstånden kan sitta kvar parallellt under övergången; TVP-modulen och RCA:n behövs inte för den här vägen. Dekoder A (TVP, RX5808 när de kommer) är orörd: det ger första riktiga diversity-provet, analog A mot digital B från samma kamera.

## FPGA-sidan, i steg

1. **`cvbs_capture` (uppgift 64): samplen in, luma ut.** Klockdomän 40 MHz från PIN80 (ren vippa i I/O-cellen, inget CE: lärdomen från uppgift 49). Synkseparering på samplen: synktoppens nivå och bakporschens nivå mäts löpande (min- och medelföljare), H-pulsens framflank ger radstart, serrations- och utjämningspulserna ger fältstart; radnummer räknas som i dag (omstart vid vertikal släckning, F ur ankomsttiden via `field_phase.v`). Omsampling 40 → 13,5 MS/s (80:27) med linjär interpolation, nivåskalning till Y 16–235 ur de mätta nivåerna, Cb = Cr = 128. Utmatning i samma ordformat som `chan_capture` ger (360 ord per rad), så att `mix_chan`, mixern och fältminnet inte ändras. Modell `cvbs_capture_ref.py`: syntetisk komposit ur en testbild (NTSC-timing, 40 MS/s, 6 bitar, valbart brus och nivåfel), testbänk jämför ord för ord; negativa kontroller: fel synknivå, saknad serration, för kort rad. Byggt i en M4-variant (`DIGIN=1`) med A = TVP, B = digital.
2. **Färg (uppgift 65).** 40 MS/s är 11,2 sampel per färgbärvågsperiod. Burstfasen mäts per rad (korrelation mot sinus/cosinus med NCO på 3,579545 MHz), kromat separeras med 1H-kamfilter eller notch, demoduleras till Cb/Cr, lågpassas och dec imeras till 4:2:2. Modellen utökas med färgstaplar; testet mäter färgfel per stapel och fasbrus. Här syns också om C5VRX:s burst är fasstabil mot dess synk: en fast fas ger stabil färg, en vandrande fas ger siffror på hur mycket.
3. **Jämförelse (uppgift 60 b och c med den här vägen).** Samma kamerabild genom TVP-vägen och den digitala vägen, mätt med `bench quality` och fältdumpen: snö, färgstabilitet, avbrott. Det är svaret på ägarens fråga.
4. **Rev B (uppgift 66).** Om den digitala vägen håller: XIAO-moduler direkt på kortet via den här bussen, TVP och kristall bara för RX5808-kanaler eller inte alls. Underlag, inget bygge.

## Taket och riskerna

- **Taket:** 4-bitars IQ i demodulatorn. Grynet i en ren länk sätts av det, inte av oss. Goggle-användarnas omdöme säger att det räcker för flygning; mätningen i steg 3 säger vad det är i siffror.
- **Klockan på MTMS:** om PARLIO:s klockutgång visar sig vara grindad mellan DMA-överföringar (IDF:s `clk_gate_en` är av, strömmen är kontinuerlig) klarar vi korta luckor med en FIFO; annars är reservvägen klockåtervinning ur datan i FPGA:n, mer arbete.
- **40 MHz in på Tang:** PIN80 är klockingång; databussen samplas i den domänen och korsar till 27/SDRAM-domänen genom FIFO som i dag. Marginalerna kontrolleras i bygget.
- **Synkhjulet av:** den råa signalen har inga reparerade synkpulser; vår synkseparering måste tåla luckor. Det är samma krav som för RX5808-vägen och mäts i modellen med brus.
- **Egenstörningen:** oförändrad; den sitter på XIAO:n.

## Ägarens beslut

| # | Fråga | Förslag |
|---|---|---|
| C1 | Digitalingången som nästa Core-spår före rev A schemavarv 2 | ja; 64 först, 65 när 64 ger bild |
| C2 | Dekoder B:s stift till digitalingången i prototypen | ja; RX5808 får A tills vidare |
| C3 | Firmwarebygget privat, utanför repona, tills licensfrågan tas | ja; byggbeskrivning och patch som text i den här noten, inte kod i repona |
| C4 | Tråd på MTMS-paden på XIAO:n | ägaren löder (tunn tråd, baksidan) |

## Status 2026-10-24

- **Firmware (63):** byggd med ESP-IDF 6.0.2 ur `388d2d1` plus klockraden; filer och flashanvisning i `bench-logs/c5vrx-clkout-2026-10-24/`. Inte flashad.
- **FPGA-sidan (64), steg 1:** `cvbs_capture.v` på Core-grenen `digin/cvbs-capture` (`6b845e8`), bit för bit mot modellen i tre fall (ren bildruta, brus med saknad synk och kort rad, utan kamfilter som negativ kontroll). M4 med `DIGIN=1` byggt: 6 822 LUT4, 31 BSRAM, 40 MHz-domänen klarar 84,5 MHz efter att luma-vägen pipelinats i tre steg. Bitströmmen `6b845e8/m4_dual_mix_digin.fs` på bänkgrenen. Snabbsviten 720 gröna; hela sviten kör inför sammanslagningen.
- **Vad modellen säger om vägen:** med syntetiska staplar blir radlängden 1715–1717 byte (mixerns tolerans ±2), alla rader 360 ord, numreringen 0–243 och 0–242 per fält, en saknad synk ger en rad märkt dålig och numreringen går vidare, ett fashopp på 300 sampel låser om på fyra rader. Nivåföljaren hamnar inom tre koder från de syntetiska nivåerna.
- **Måndag:** strömbrytning av XIAO:n, flash, synkhjulet av, tråden på MTMS, sex datatrådar och klockan till J5 enligt tabellen, `m4_dual_mix_digin.fs`: lysdiod 2 ska lysa (rader från B) och bilden från B ska synas när A saknas. Därefter `bench quality` och fältdumpen på B mot A.
