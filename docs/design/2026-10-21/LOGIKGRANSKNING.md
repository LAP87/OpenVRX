# Logikgranskning av video- och styrkedjan, 2026-10-21

En av två granskare i rådet. Granskat: Core `7354865` (grenen `ui/flight-view` med `main` `f626a6f` inmergad), navet `bc29e58`. Läst: hela kedjan i `gateware/rtl/` (bt656_rx → chan_capture → async_fifo → mix_chan → line_mixer → fb_backend/fb_sdram/fb_display/genlock_timing → tmds_link), `tvp_ctrl`, `i2c_master`, `rx5808_*`, `puck_ui`, `ssd1306_text`, `flash_store`, `rssi_adc`, `chan_scan`, topparna M3, M4 och M6, deras `.cst` och `build.sh`, samt bänknoterna [HANDOFF_CLAUDE_2026-10-20](../../bench/HANDOFF_CLAUDE_2026-10-20.md), [IOREG_ANALYS_2026-10-21](../../bench/IOREG_ANALYS_2026-10-21.md) och [BANK_2026-10-21](../../BANK_2026-10-21.md).

Allt nedan är kodläsning, utom F7 som är kört i Icarus 12 (WSL). Inget är byggt, committat eller provat på kortet.

Allvar: **A** blockerar första bild (eller dess bänkkriterium), **B** blockerar flygbruk, **C** senare.

| # | Fynd | Allvar | Var |
|---|---|---|---|
| F1 | SDRAM-läsningens fönster följer bygget; M2a:s godkända läspunkt gäller inte automatiskt M4/M6 | A (BUF), kringgås med LOW | `sdram_burst.v:180` |
| F2 | Bänkkriteriet "lysdiod 0 till 1 Hz" i M4 kan inte nås med en dekoder | A (kriteriet) | `m4_dual_mix.v:69-70`, `m6_puck_proto.v:166-167` |
| F3 | Adressen 5D kan bero på FPGA:ns pull-up under konfigurationen, inte på modulen | A | `tvp_ctrl.v:146,203,220` |
| F4 | Okänd eller för gammal dekoderstatus räknas som "låst"; frilöpande rader avgörs då på HF | B | `m4_dual_mix.v:89-90`, `m6_puck_proto.v:176-177` |
| F5 | YOUT fångas på SCLK:s stigande flank genom obegränsad routning; M3:s rena resultat följer inte med till M4/M6 | A om marginalen är liten (okänt) | `mixer2.v:49-50` |
| F6 | `LEN_TOL = 2` förutsätter radlängd 1716/1728 ± 2 från dekodern även med riktig källa | B | `mix_chan.v:93-95,114` |
| F7 | `xy_bad_cnt`/`xy_corr_cnt` är 8 bitar och slår runt (kört: 256 dåliga koder ger 0) | C | `bt656_rx.v:140,155,161,176` |
| F8 | M3:s `fld` räknar F-bitens växlingar: 0 för en progressiv källa | C (läs dagens M3-rader med det i minnet) | `bt656_probe.v:70` |
| F9 | `flash_store` väntar utan tidsgräns på flashens busy-bit och håller då WP# hög | C | `flash_store.v:220-231` |
| F10 | M6:s logg tystnar när mixern inte får rader | C (bänkhjälp) | `puck_ui.v:553` |
| F11 | DVI-standardbygget skickar full-range-RGB i en CE-timing utan InfoFrame | C | `m4_dual_mix.v:112`, `tmds_link.v:52-55` |
| F12 | Dekoderstift utan pull: en saknad modul ger en flytande klockingång | C | `m4_dual_mix.cst:15,36` m.fl. |
| F13 | OSD-spegelns räknare i M6 saknar reset: Icarus ser X, OSD i M6-toppen är otestad | C | `m6_puck_proto.v:193-201` |
| F14 | `nolock` är kombinatorik av flera register före synkroniseraren | C | `mix_chan.v:98` |
| F15 | I2C: ingen bussåterställning; OLED:n går i 397 kHz utan kontroll av SDA:s stigtid | C | `i2c_master.v:113-118`, `ssd1306_text.v:23` |

---

## F1. SDRAM-läsningen är byggberoende (A för BUF)

**Var.** `sdram_burst.v:179-182`: `rdata <= SDRAM_DQ` i ett register med klockenable (`cycle >= rs && cycle < rs + 8`). Med `IOREG=0` (standard sedan 2026-10-21) sitter registret i logiken, och vägen pad → vippa routas fritt. Inga in- eller utgångsfördröjningar är begränsade (ingen `.sdc` finns; alla klockor har bara `--freq 75`). Samma gäller kommando- och adressvipporna (`:113`, `:144`) och `dq_out` (`:164`).

**Vad.** M2a gav `rs=5 err=0` vid fas 9-11 i *sitt* bygge. M4 och M6 placeras och routas annorlunda, så fördröjningen för de 32 DQ-bitarna och kommandobitarna är andra. Fönstret per ord är enligt filhuvudet en period minus 3,5 ns, och hur mycket av det M2a-bygget använde är inte känt.

**Varför på kortet.** Är någon DQ-bit i M4/M6 utanför fönstret blir BUF-bilden fel (flyttade ord, felfärg) eller grå, utan att något säger varför.

**Prov.** (1) Självtest i `fb_backend` efter `init_done`: skriv två 8-ordsskurar med gående ettor och adressmönster till en rad som fält aldrig når (buffert 3, rad 1023 → bank 3, rad 2046), läs tillbaka med `rd_sample` 4, 5 och 6, och visa resultatet (M6: ett tecken i loggen; M4: lysdiod 1/2 de första sekunderna). Negativ kontroll: i `sim/test_sdram.py` med kortfördröjningen utanför gränsen ska självtestet fälla; på kortet ett bygge med `SDRAM_PHASE=2`. (2) Samma commit byggd som M2a och M4: om M2a-svepet visar samma läspunkt men M4:s självtest fäller är det placeringen.

**Åtgärd.** Gör DQ-infångningen till en ren vippa varje klocka (`dq_in <= SDRAM_DQ`, ingen CE, ingen reset) och kvalificera i nästa steg (läspunkten flyttas en klocka; `RD_SAMPLE` justeras). Bygg sedan med bara `--vopt ireg_in_iob` och `iob_regs.py --strict` som grind, så hamnar exakt de 32 rena vipporna i I/O-cellerna och fönstret blir detsamma i alla toppar. Det är IOREG-analysens förslag, nu med motiveringen att det också gör M2a-resultatet giltigt för M4/M6. Till dess: första bilden kan tas i LOW, som inte rör SDRAM:en (M6:s `LAT LOW`; M4 saknar byggval för `LOW_LATENCY=1`, ett `LOW=1` i `build.sh` vore en rad).

## F2. Lysdiod 0 visar bara "båda låsta" (A för bänkkriteriet)

**Var.** `m4_dual_mix.v:69-70` och `m6_puck_proto.v:166-167`: `locked_ok` kräver `st_valid == 2'b11` och lås i båda dekodrarna.

**Vad.** BANK_2026-10-21 steg 5 har "lysdiod 0 går från 4 Hz till 1 Hz (lås)" som klarkriterium för M4 med *en* TVP-modul. Med en modul svarar dekoder B aldrig, och lysdioden blinkar 4 Hz även med perfekt bild.

**Prov.** `sim/test_top_pins.py` med dekoder A låst och B utan slav: lysdiod 0 ska vara 4 Hz (bekräftar beteendet). Ändras regeln: samma fall ger 1 Hz, och fallet "ingen låst" fortsatt 4 Hz (negativ kontroll).

**Åtgärd.** Enklast i bänkplanen: kriteriet blir "bild på HDMI och lysdiod 1 (rader från A)". Alternativt i RTL: 1 Hz när minst en är låst, 2 Hz när båda är det.

## F3. Dekoderns adress kan komma från FPGA:ns konfigurationsläge (A)

**Var.** `tvp_ctrl.v:146,203,220` (fast `DEV0`/`DEV1`), byggvalet `TVP_ADDR` i M3/M4/M6. YOUT7 (stift 74 för A, 72 för B) har `PULL_MODE=NONE` efter konfigurationen.

**Vad.** TVP5150AM1 läser adressen ur YOUT7 vid reset. Den röda modulen saknar RESETB-stift (BRINGUP: "löd en tråd till TVP stift 8"). Utan tråden tar dekodern adressen vid sin egen strömpåslagning, medan FPGA:n ännu konfigureras. Gowin-I/O har, såvitt jag vet, svag pull-up under konfigurationen (obekräftat här; kontrollera i GW2AR-databladet). Har modulen inget starkt strappmotstånd blir svaret då 5D. Läggs RESETB-tråden till pulsar `tvp_ctrl` den 20 ms efter konfigurationen, när stift 74 är utan pull, och adressen bestäms av modulen ensam: 5C, 5D eller slump.

**Varför på kortet.** Samma modul kan byta adress när RESETB kopplas in, och dagens `_tvp5d`-bitström ger då `i2c NA` igen.

**Prov.** Mät YOUT7 mot jord och 3,3 V på modulen med Tang-kortet strömlöst (modulen matad för sig): fast nivå = strap på modulen, flytande = FPGA:ns pull avgör. Kör sedan M3 både med och utan RESETB-tråden; ändrat svar bekräftar hypotesen.

**Åtgärd.** Uppgift 48 steg 2 (automatisk sökning) bör gå före M4 med två moduler: vid NACK på första init-skrivningen provar `tvp_ctrl` `DEV ^ 1` och låser den adress som svarar, per dekoder. Test mot `i2c_slave_model.v` på 5D med `DEV0 = 5C`; negativ kontroll med sökningen avslagen ska ge `dev_err`. Koppla RESETB-tråden, så att adressen tas i ett känt läge.

## F4. Okänd status räknas som låst (B)

**Var.** `m4_dual_mix.v:89-90`, `m6_puck_proto.v:176-177`: `nolock = st_valid && !(H && V)`. `status_valid` nollas vid varje NACK (`tvp_ctrl.v:177-178`) och efter en återinitiering (`:185-190`). Status uppdateras en gång per runda, ungefär 22,4 ms (20 ms paus plus sex läsningar à cirka 0,4 ms vid 99 kHz, `:200-215`).

**Vad.** En frilöpande dekoder levererar giltiga koder och rader på 1716 byte; `mix_chan.v:114` ser inget fel i dem. Det enda som gör dem dåliga är `ext_bad`. När status saknas (NACK, nyss återinitierad) eller ännu inte hunnit visa låsförlusten (upp till cirka 24 ms, 1,4 fält) räknas de frilöpande raderna som bra. I ett par väljer `line_mixer.v:121-145` raden med minst HF. Är den frilöpande utsignalen platt (svart eller enfärgad, HF nära 0) vinner den mot riktig bild med `to_b`/`to_a`, och `cur` flyttas dit.

**Varför på kortet.** Just när en mottagare tappar signalen är de två dekodrarna fortfarande i takt (den frilöpande tidbasen startar där låset släppte), så raderna paras. Varje bortfall på en mottagare kan då ge ett platt band eller fält i bilden i stället för den andra mottagarens bild, plus åtta rader innan `cur` går tillbaka. Det är precis det diversity ska förhindra. Hur platt TVP5150AM1:s frilöpande utsignal är vet vi inte; bänken 2026-10-21 visade bara att koderna växlar (`tog FF`).

**Prov.** Bänk: M6, mätarsidan, med dekoder B:s videoingång öppen. Ett snövärde för B nära 0 betyder platt frilöpning och att F4 gäller fullt ut; brusnivå betyder att raderna förlorar på HF ändå. Simulering: `tb_top_pins`/`tb_chain` med A som riktig bild och B som platt BT.656 i takt, B:s slavmodell först låst, sedan olåst med en NACK-runda emellan. Förväntat: inget ord från B efter låsförlusten plus en runda. Negativ kontroll: dagens mappning skickar B-rader i fönstret.

**Åtgärd.** (a) `nolock = !(st_valid && H && V)`: okänt räknas som dåligt. Ensam dekoder visas ändå (dåliga rader i följd visas), och en dekoder utan I2C har inga utgångar påslagna. (b) Kortare latens: läs bara 88h, varannan dekoder, varannan millisekund, och 89h/03h glesare; eller I2C i 400 kHz. (c) Efter bänkmätningen: en rad med HF under ett golv (t.ex. < 16 per rad) räknas som misstänkt. En riktig kamera har sensorbrus och hamnar över; en genererad yta gör det inte.

## F5. YOUT-infångningen (A om marginalen är liten, okänt)

**Var.** `mixer2.v:49-50` (`a_in <= a_d` på `a_clk`), samma i `bt656_probe.v` (`din`). Klockan går via GCLKT-stiftet till det globala nätet; datat via fri routning. Ingen begränsning finns.

**Vad.** Om TVP5150AM1 byter YOUT kort efter SCLK:s stigande flank (SLES209E, figuren "Clocks, video data and sync timing"; inte kontrollerat här) samplar FPGA:n nära övergången, och var den hamnar beror på varje bits routning i varje bygge. M3 visade `len 1716-1716` och rätt koder i *sitt* bygge. M4 och M6 har annan routning och ingen räknare för synkfel.

**Prov.** (1) Läs fördröjningen ur databladet. (2) M3 byggt med seed 0-3: `xe` och `len` lika i alla → marginalen är troligen god. (3) Ett byggval som samplar på fallande flank: ger båda flankerna `xe 0000` är ögat brett; ger bara den ena det ska den väljas.

**Åtgärd.** `a_in`/`b_in` är redan rena vippor utan CE och reset, alltså just den sort som är säker i I/O-cellen. Med enbart `ireg_in_iob` (se F1) får de samma fördröjning i alla byggen. Lägg dessutom ett synkfelstal per kanal i M6-loggen, så att varje bygge visar sin egen infångning.

## F6. Radlängdstoleransen ±2 byte (B)

**Var.** `mix_chan.v:93-95,114`, `mixer2.v:6` (`LEN_TOL = 2`).

**Vad.** En rad är dålig om avståndet EAV-EAV inte är 1716 eller 1728 inom 2 byte. Frilöpande gav TVP:n exakt 1716 (bänken). Vad den ger med en riktig men ostabil källa (svag RF, kamera med avvikande radfrekvens, en mjukvarugenererad CVBS som C5VRX:s DAC) är inte mätt. Om längderna sprider mer blir alla rader dåliga, och mixern väljer inte längre på kvalitet, bara på "aktuell kanal".

**Prov.** M3 med XIAO/C5VRX-källan och sedan RX5808 på svag signal: `len min-max` per sekund. Spridning ≤ 4 byte: inget att göra. Större: mät fördelningen innan toleransen ändras.

**Åtgärd.** Efter mätningen: bredare tolerans, eller längden som ett eget "misstänkt"-mått som bara väger i par, inte som "dålig".

## F7. 8-bitars felräknare slår runt (C)

**Var.** `bt656_rx.v:140` (`xy_bad_cnt + 8'd1`), `:155`, `:161`, `:176` (`xy_corr_cnt`). Modellen `model/bt656.py` har ingen gräns. `bt656_probe.v:52` (M3:s `xe`) summerar det omslagna värdet.

**Vad och kört prov.** En testbänk matade en hel rad, N okorrigerbara tidkoder (`FF 00 00 01`) och sedan en hel rad till `bt656_rx.v`. Icarus 12: N = 255 ger `xy_bad 255`, N = 256 ger `0`, N = 257 ger `1`. Raden efter en lång följd trasiga koder kan alltså räknas som felfri, och M3:s `xe` underskattar vid hela-fält-fel, som vid marginell infångning (F5). Samma klass som M0-räknaren: inget test har så många fel mellan två rader.

**Åtgärd.** Mätta båda räknarna vid FFh. Testet ovan blir permanent, med dagens RTL som negativ kontroll (den ger 0 vid 256).

## F8. M3:s fältantal bygger på F-biten (C)

**Var.** `bt656_probe.v:70`: `fields` ökar när `rec_field` byter värde.

**Vad.** Projektets egen regel (AGENTS.md) är att TVP5150AM1 håller F = 1 för icke-sammanflätade källor. En progressiv 240p-källa, vanlig för mjukvarugenererad CVBS och möjlig för C5VRX, ger då `fld 000` med fullt fungerande fält. `bt656_rx` räknar redan fält på vertikal släckning.

**Prov.** `sim/test_probe.py` med en ström där F hålls 1: dagens RTL ger 0, rättad ger 60.

**Åtgärd.** Räkna rader med `rec_line == 0`.

## F9. Flashen: busy-väntan utan tidsgräns (C)

**Var.** `flash_store.v:220-231`. `flash_wp_drive` sätts i `S_CRC` och släpps först när busy-biten är 0 inför `S_VERIFY`.

**Vad.** Svarar flashen inte (MISO hålls hög av `PULL_MODE=UP`: bygge utan `--mspi_as_gpio`, flash i djup viloläge, trasig koppling) läser `S_POLL` FFh för alltid. `flash_store` hänger, flygvyn står på `UNSAVED`, och WP# drivs hög hela tiden, det som enligt filhuvudet störde USB-programmeringen i en annan konstruktion.

**Prov.** `tb_flash_store` med MISO bunden till 1: förväntat `err` och WP# släppt inom 1 s. Negativ kontroll: dagens RTL fastnar.

**Åtgärd.** Tidsgräns i `S_POLL` (radering högst några hundra ms; 1 s räcker), sedan `err`, WP# släppt och `S_IDLE`. Skicka gärna ABh (väck ur djupt viloläge) före avsökningen; om Gowins konfiguration lämnar flashen så är inte kontrollerat.

## F10. M6-loggen tystnar utan rader (C, bänkhjälp)

**Var.** `puck_ui.v:553`: en loggrad skickas bara när `use_toggle` vänder, alltså efter 1 024 mixerbeslut.

**Vad.** Utan rader från någon dekoder (fel adress, utgångar av, ingen modul) kommer ingen rad alls, just när loggen behövs. Status och lås ligger ändå i registren.

**Åtgärd.** Skicka också en rad om inget fönster kommit på 250 ms (snötalen visas då som `------`, som `stale` redan gör). Test: inga rader in → en loggrad per ≤ 250 ms.

## F11. DVI med full-range-RGB i 720p (C)

**Var.** `m4_dual_mix.v:112` (`rgb_full(1'b1)`), DVI-grenen `tmds_link.v:52-55`, `ycbcr2rgb.v` ger 0-255.

**Vad.** 720p är ett CE-format. En mottagare utan AVI InfoFrame antar enligt CEA-861 begränsat omfång för CE-format; många TV-apparater och HDMI-inspelare gör det. Svart och mörka nyanser kläms då ihop och högdagrar klipps. Bildskärmar för datorer antar oftast fullt omfång. Den mörkgrå "ingen signal"-rutan (20h) blir nästan svart.

**Prov.** M0 eller M4 på en TV i läget "auto": en gråskala med steg under 16 och över 235 ska vara urskiljbar.

**Åtgärd.** Dokumentera i BRINGUP; eller gör `HDMI=1` (InfoFrame med Q = full) till standard när det är sett på en riktig mottagare.

## F12. Flytande dekoderstift (C)

**Var.** `boards/m4_dual_mix.cst:15,20-34,36` (och M3/M6): SCLK och YOUT med `PULL_MODE=NONE`.

**Vad.** Med en modul (dagens bänk) flyter dekoder B:s SCLK-stift, en GCLK-ingång. Brus kan klocka B-domänen och fylla dess FIFO med skräp. YOUT flyter också före `03h = 0Dh` och hos en dekoder som inte svarar. Mixern och `mix_chan` klarar skräpet (fullständighetskontrollen), men lysdiod 2 och snömätaren kan visa aktivitet som inte finns.

**Åtgärd.** `PULL_MODE=DOWN` på SCLK och YOUT0-6; YOUT7 behåller `NONE` (adresstrappen, BRINGUP avsnitt 3). Eller jorda B:s SCLK på bänken.

## F13. M6:s OSD-spegel är otestad i toppen (C)

**Var.** `m6_puck_proto.v:193-201`: `scan_row`, `scan_col` utan reset eller startvärde.

**Vad.** På kortet startar de på 0. I Icarus är de X för alltid (`X == 20 ? 0 : X + 1`), så OSD-texten i M6-toppen skrivs aldrig i simuleringen. `sim/test_osd.py` testar bara `osd_overlay` för sig, och `test_top_pins`/`test_m6_settings` tittar inte på OSD.

**Åtgärd.** Startvärde eller reset, och en pixelkontroll av OSD i M6-toppen.

## F14. Kombinatorik före synkroniseraren (C)

**Var.** `nolock_*` (F4) och `nolock | force_bad` i M6 går kombinatoriskt till `ext_s` (`mix_chan.v:98`) i en annan klockdomän.

**Vad.** När `status0` och `status_valid` byter värde i samma klocka kan uttrycket glitcha, och `ext_s` kan fånga glitchen. Effekten är högst en felbedömd rad per runda. Registrera uttrycket i 27 MHz-domänen innan det korsar.

## F15. I2C-bussens robusthet (C)

**Var.** `i2c_master.v:113-118` (START utan kontroll av att SDA är hög), `ssd1306_text.v:23` (`I2C_DIV = 17`, 397 kHz).

**Vad.** (a) Ingen bussåterställning: håller en slav SDA låg (FPGA:n laddades om mitt i en läsning) blir varje transaktion NACK tills slavens byte råkar klockas ut. TVP:erna återställs av RESETB vid start, men OLED:n och ADS1115 inte. (b) SCL:s stigtid hanteras av sträckningslogiken; SDA:s gör det inte. Vid 397 kHz har SDA två kvartsbitar (1,26 µs) på sig. Med bara FPGA:ns interna pull-up räcker det inte, och OLED-trafiken blir NACK eller skräp.

**Åtgärd.** Nio SCL-pulser och STOP när SDA är låg i vila. OLED:n i 100 kHz om pull-up ≤ 2,2 kΩ inte är uppmätt på bussen.

---

## Svar: en dekoder som finns, klockar och är initierad men saknar lås

Bänken 2026-10-21: 1716 byte per rad, 60 fält/s, `st 0000`. Så hanterar RTL:en det:

1. `bt656_rx` ser giltiga koder, `mix_chan` rätt längd och 360 ord i följd. Inget i själva strömmen säger att låset saknas; bara `ext_bad` gör det (`mix_chan.v:114`).
2. M4/M6: status giltig, H/V-lås 0 → `nolock = 1` → varje rad dålig, efter högst cirka 24 ms.
3. **En dekoder (dagens bänk):** mixern visar den aktuella kanalens dåliga rader i följd. Första raden i varje utfält lämnas ute och ersätts i `fb_sdram` av raden ovanför, förra fältets rad eller svart. Fälten publiceras var 16,7 ms, `have_video` blir 1, och HDMI visar dekoderns frilöpande utsignal i 4:3-fönstret, inte den mörkgrå "ingen signal"-rutan. OLED:n säger `NOSIG`, lysdiod 0 blinkar 4 Hz (som den gör även med lås, F2), och RX5808 skrivs om varannan sekund. I LOW låser genlocken till de frilöpande fälten; samma bild.
4. **Två dekodrar, den ena låst:** den olåsta förlorar i varje par. Dess ensamma rader visas inte (den är inte aktuell, och `gap_ok` kräver en bra rad), och övertagandereglerna kräver bra rader. Rätt beteende, med förbehållet i F4: allt hänger på att I2C-statusen är färsk och giltig.
5. Fältminnet tittar aldrig på lås, med avsikt; det visar vad mixern ger.

## Granskat och funnet sunt

- **Reset:** `mixer2`, `fb_backend`, `m2_core` sätter reset asynkront och släpper den synkront med tre steg per domän; PLL-lås ingår. En klocka som står (dekoder utan SCLK) håller sin domän i reset tills den går. FIFO:ns två sidor återställs var för sig men till samma pekare (0). 27 MHz-domänen har bara strömpåslagsreset; alla dess tillståndsmaskiner har en ände, utom F9.
- **Klockdomänkorsningar:** `async_fifo` (formellt bevisad, även `RD_REG`), `toggle_tx`/`toggle_rx` (bevisade), `sync2` för nivåer med marginalkontroller (`frame_low`, `ll_low`), `linebuf_initialized` (bitar som bara går 0 → 1), snö-, brus- och användningsvärden (växelbit genom tre steg, värdet stilla ett helt fönster), `rgb_full` (två steg, tas vid vsync), `ext_bad`/`ext_weak` (två steg; se F14).
- **Räknare som kan slå runt** (samma klass som M0): `bt656_rx` `pos`, `act_count` mättas; `hf` nollas vid varje SAV och når högst cirka (720 + 138) × 255 < 2^20; `ev_line` slår om vid 1024 och tolkas då som nytt fält (ofarligt); `mix_chan`-åldrar, `idle`, `hcnt` mättas; `line_mixer` `quiet_*`, `since_pair` mättas; `fb_sdram` `n_now = 1023 + 1 = 0` ger `pub_lines = 0` och därmed `DEFAULT_LINES`; `fb_display` `acc`/`step` högst 6 972 < 2^13; `since_pub`, `ll_since`, `field_phase.cnt` mättas; `genlock_timing` räknare formellt avgränsade; `sdram_burst.cycle` mättas vid 31, största behov 17; `i2c_master.st_n`, `rx5808_tune.t`, `chan_scan.t` avgränsade; `flash_store` löpnummer testat förbi FFFFh; `snow_stats`/`noise_stats` summor rymms; `ycbcr2rgb` högst 207 570 < 2^18; M3:s räknare (`sclk/256` på 17 bitar) rymms.
- **SDRAM-styrningen** utöver F1: uppdatering var 7,4 µs med förtur, DQ släpps efter skrivskuren innan läsning, NOP från första klockan. I LOW hålls `fb_sdram` i reset medan `sdram_burst` fortsätter uppdatera.
- **tvp_ctrl:** en NACK gör rundan ogiltig; en återställd dekoder hittas på 03h och initieras om utan RESETB; init-listan stannar vid första NACK; en dekoder som dyker upp senare initieras via 03h-kontrollen. `i2c_master` ger upp efter 10 ms SCL låg, så bussen fastnar inte.
- **Tre mastrar på SDA_A** (M6): hold sätts minst två klockor före start; jag följde fallet där två begär samma klocka (tvp_ctrl startar när OLED:n höjer hold, rssi_adc och OLED:n samtidigt i `S_REQ`). Det blir alltid en i taget, med ordningen rssi_adc > OLED > tvp_ctrl.
- **RX5808 SPI:** 25 bitar LSB först, adress 1, skrivbit, 20 data; DATA och SEL vilar höga (lysdiodsstiften), CLK låg; omskrivning varannan sekund så länge inget är låst.
- **LOW/BUF-byte:** `fb_sdram` i reset i LOW, `have_pub` glöms, resten av bilden släcks vid byte, `s_fetch_req` maskas med `ll_s`. De få klockor `ll_s` och `ll_p` skiljer sig ger högst några pixlar fel rad innan bilden släcks.
- **Genlock utan källa:** bilder om 757 rader (cirka 59,4 Hz), grå. **HDMI/DVI:** TMDS-kodaren är standard och sedd på kortet (M0); InfoFramens omfång tas per bild.
- **puck_ui/flash_store (grenen):** studsfilter, menyns tidsgräns, alla rader exakt 21 tecken (`frow0`, `frow2`, `frow3`), posterna kontrolleras med Z och CRC och ligger inom en 256-bytessida, `set_load` validerar band och läge.

## Övrigt

- M2 initierar inte dekodern (inget I2C; den förutsätter Moneagles SoC). Med CP803A-modulen står YOUT i högimpedans (03h = 01h) och M2 visar ingenting. AGENTS.md nämner M2 i uppstartsordningen; BRINGUP har redan rätt ordning (M3 → M2a → M4).
- `IOREG=1` packar också I2C-, SPI- och UART-vipporna (CE, reset); varje framtida användning behöver `iob_regs.py --strict`, inte bara för SDRAM:en.
- Testbänken för F7 ligger inte i repot (den här granskningen ändrar bara den här filen). Den är 40 rader: `bt656_rx` med en hel rad (EAV 9Dh, 268 släckbyte, SAV 80h, 1 440 aktiva byte, EAV), N × (`FF 00 00 01` + 4 byte), 200 byte, en hel rad till; `rec_xy_bad` för rad 2 skrivs ut.
