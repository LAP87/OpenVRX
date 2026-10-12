# Alternativa vägar — så att vi inte låser oss (2026-10-02)

projektägaren bad om en bred koll innan rev A-schemat ritas. Varje rad nedan är en hel väg från mottagare till ögon, eller ett utbytbart block. Källor längst ned; priser är sökträffar 2026-10-02 och ska kontrolleras vid köp.

## 1. Hela vägar från 5,8 GHz till ögonen

| Väg | Kedja | Mixning | Kostnad (ungefär) | Vad vi lär oss / risk |
|---|---|---|---|---|
| **A. Bara köpt** | mottagare med AV-ut → CVBS→HDMI-box (1080p60) → HDMI→USB-C → XR | bara om mottagaren gör det | ≈ steg 2 i `bom/EXPERIMENT1_INKOPSLISTA.md` | Snabbast till bild i glasögonen; boxens latens okänd (mät med riggen). Inget eget. |
| **B. Köpt mixning + egen bildväg** | SteadyView X (AV-ut via "ground station"-kit, ≈ 180–240 USD) → vår FPGA (en TVP, M2/M5) → XR | Skyzones | 180–240 USD + FPGA | Mixningen är löst och beprövad; vi gör ren skalning, OSD, låg latens. Dyr modul, men kan återanvändas i vanliga goggles. |
| **C. Egen mixning (nuvarande spår)** | 2 mottagare → 2 TVP5150AM1 → FPGA-mixer → HDMI | vår (M4, simulerad) | se block nedan | Mest att lära, mest risk; mixern måste bevisas mot riktig signal. |
| **D. Utan XR-glasögon** | (A/B/C) → HDMI → mikro-OLED + drivkort, eller CVBS direkt till drivkort | valfri | ECX335 1080p 238 USD + HDMI-drivkort 95 USD **per öga** (+ optik); ECX334 1024×768 med **CVBS-drivkort** 99,59 USD + panel | Egen optik/mekanik (skrivaren!). Drivkortens godkända format (720p? 50 Hz?) är inte publicerade — om de tar 720p räcker Tang Nano 20K:s egen HDMI. Dyrt för två ögon. |
| **E. Kortdator/SoC + USB-fångare** | mottagare → USB-UVC → telefon/SBC → skärm | nej | billigt | Bekvämt men typiskt 1–3 bilders extra latens; avvisat som huvudspår (latensmålet ≈ 50 ms). |

Väg A och B är inte konkurrenter till C — de är **jämförelsepunkter**: samma latensrigg och samma flygning ger svar på om vår mixning är värd mödan.

## 2. Utbytbara block inne i väg C

### HDMI-utgång (1080p60, som glasögonen kräver)

| Alternativ | Dokumentation | Pris / tillgång | Kommentar |
|---|---|---|---|
| **LT8618SXB** (nuvarande rev A-koncept) | inget datablad hos oss; init härledd ur M5Stack-kod (`research/LT8618SX_INIT.md`) | ≈ 5 USD | Billig men gissningar om adress/reset/klockflank. Ingen breakout hittad. |
| **ADV7513** (ADI) | **fullständig** programmeringsguide + hårdvaruguide; "Recommended for new designs" | LCSC C408901, 26,71 USD (1 st), LQFP-64 (lättlödd) | Samma sändare som Terasic DE10-Nano (MiSTer) — beprövad mot FPGA i tusentals exemplar. Tar YCbCr 4:2:2 med inbäddad synk (ITU-656-stil), 165 MHz. |
| **IT66121FN** (ITE) | Linux-drivrutin (`ite-it66121.c`) + läckta datablad | ≈ 1–4 USD, QFN64 | Billigast; drivrutinen hanterar bara RGB-ingång → 24 stift. |
| **Ingen sändare: FPGA:n gör TMDS själv** | Gowin DS1103 | — | Kräver FPGA med snabba serialiserare: **GW5A-25: 10:1-serialiserare upp till 2 000 Mbit/s** (DS1103 tabell 3-33) mot 1 485 som 1080p60 kräver. GW2AR-18 (Tang Nano 20K, nuvarande) klarar bara 1 200. |

### FPGA

| Alternativ | Minne | 1080p60 direkt | Kapsel | Öppen verktygskedja |
|---|---|---|---|---|
| **GW2AR-18** (Tang Nano 20K; nuvarande rev A) | 64 Mbit SDRAM **i kapseln** | nej (1 200 Mbit/s) → extern sändare | QFN-88 | ✔ allt vi byggt i natt |
| **GW5A-25** (Tang Primer 25K) | inget inbyggt → externt SDR SDRAM, t.ex. Winbond W9825G6KH (LCSC C62246, ≈ 5 USD, TSOP-54) | **ja, inom spec** | LQ100 / LQ144 (0,5 mm, handlödbar; ≈ 30–34 USD), MG121 BGA (Primer 25K-modulen) | ✔ apicula 0.32 har GW5A-25 inkl. LQFP100/144, PLLA, OSER10 + TLVDS, 640×480-videoexempel för Primer 25K. **Provat i natt: bitström för GW5A-25 LQ144 med OSER10 + LVDS byggdes** (kräver `--vopt sspi_as_gpio` + `gowin_pack --sspi_as_gpio`). Inte provad på kort. |

GW5A-25 har dessutom en **inbyggd ADC** — kan läsa mottagarnas RSSI direkt (GW2AR har ingen).

### Dekoder

TVP5150AM1 står kvar (TI, aktiv, i Moneagle, all vår gateware). Kollade alternativ: Techpoint **TP9950** (aktiv, billig, BT.656 ut, men datablad bara via forumläckor), Renesas **TW2864** (2 kanaler tidsmultiplexade på en 54 MHz-port — sparar stift, men TW286x-familjen är till stor del utgången), ADI ADV718x/728x (NRND).

## 3. Rekommendation

1. **Rev A = ett dekoderkort, inte ett helt goggle-kort.** Två CVBS-ingångar → 2× TVP5150AM1 → stiftlist. Det är den del som är gemensam för *alla* varianter av väg C (och användbar i B med en kanal). Kortet ansluts till devkortet vi väljer — Tang Nano 20K (21 signaler ryms bland 28 lediga) eller Tang Primer 25K. FPGA- och HDMI-valet skjuts upp tills det är provat på riktigt. Hela integrerade kortet blir rev B.
2. **Pröva 1080p60 till glasögonen billigt innan något HDMI-chip väljs:** Tang Primer 25K + Dock (29 USD) + PMOD DVI + SDRAM-modul (10 USD). Ger svaret "tar XREAL vår 1080p60?" utan LT8618SX-breakout. Kräver portning av PLL- och SDRAM-delen (16-bitars externt SDRAM i stället för GW2AR:s inbyggda 32-bitars).
3. Om GW5A + direkt TMDS fungerar → rev B utan HDMI-sändare (färre delar, inga odokumenterade chip). Annars **ADV7513** före LT8618SX.
4. Väg A (köpt CVBS→HDMI-box) är fortfarande det snabbaste sättet att få se glasögonen med FPV-bild och ger en latensreferens.

Inget av detta är köpt eller beställt. Kostnadsbesluten är dina.

## Källor

- ADV7513: LCSC C408901, [ADI produktsida](https://www.analog.com/en/products/adv7513.html), [Programming Guide](https://www.analog.com/media/en/technical-documentation/user-guides/ADV7513_Programming_Guide.pdf), [Hardware User's Guide](https://www.analog.com/media/en/technical-documentation/user-guides/adv7513_hardware_user_guide.pdf)
- IT66121: [Linux-drivrutin (LWN)](https://lwn.net/Articles/852360/)
- GW5A: Gowin DS1103-1.1E (sparad i `raw/alt/gw5a_ds1103e.pdf/.txt`, från cdn.gowinsemi.com.cn), [Sipeed Wiki Tang Primer 25K](https://wiki.sipeed.com/hardware/en/tang/tang-primer-25k/primer-25k.html), [CNX Software (pris)](https://www.cnx-software.com/2024/01/03/sipeed-tang-primer-25k-board-23040-logic-cells-fpga-prototyping-development/), [thisiseth/tang-primer-25k-spi-io (1080p DVI)](https://github.com/thisiseth/tang-primer-25k-spi-io), apicula `examples/gw5a/` (GitHub YosysHQ/apicula), GW5A-LV25MG121N: LCSC C45617374
- SDRAM: W9825G6KH-6, LCSC C62246
- Dekodrar: [TP9950-specifikation (TI E2E-bilaga)](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/138/TP9950Aspec12282018.pdf), [TW2864-datablad](https://www.renesas.com/en/document/dst/tw2864-datasheet), [TW2866 obsolete](https://www.renesas.com/en/products/analog-products/audio-video/video-decodersencoders/tw2866-4-channel-video-decoder-and-audio-codec-plus-video-encoder-security-applications)
- Mikro-OLED: Sony ECX335S (0,71", 1920×1080), HDMI-drivkort för 0,71", CVBS-drivkort för 0,39" (sökträffar på en marknadsplats, länkarna borttagna)
- SteadyView X: [Skyzone](https://www.skyzonefpv.com/products/skyzone-steadyview-x-5-8ghz-ips-screen-receiver-module)
