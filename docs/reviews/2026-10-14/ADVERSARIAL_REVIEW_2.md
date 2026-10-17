# OpenVRX: adversarial granskning 2, 2026-10-14

Granskat: `OpenVRX-Core` 072dbde (för blocken nedan samma källa som `bf05ac0`), navet 23e0657. Blocken skrevs och testades av samma agent 12–13 oktober: `rssi_adc.v` och regeln för svag mottagare i mixern (`ext_weak`, `mix_chan.v`, `line_mixer.v`), `chan_scan.v`, `flash_store.v`, HDMI-paketen i `tmds_link.v`, `vblend.v` med `VINTERP` i `fb_display.v`, och `WAIT_BEFORE_VSYNC` i `genlock_timing.v`.

## Slutsats

Två fel borde inte nå kortet. Båda är rättade på egna grenar med regressionstest och negativ kontroll:

- **RS-1.** Regeln som gör att en svag mottagare (RSSI-varning) förlorar sin hälsa gör också att den aldrig kan ta över. Är den andra mottagarens dekoder olåst och går de två ur takt, stannar mixern på den trasiga för gott: 69 av dess 72 dåliga rader visas och ingen av den svaga mottagarens 72 felfria.
- **FL-1.** Ett strömavbrott mitt i raderingen av en full sektor kan få startläsningen att ladda en post som aldrig skrevs. Nästa sparande raderar då sektorn med den riktiga posten. I en enkel bitmodell händer det i 2–24 % av de avbrutna raderingarna.

Fyra punkter är öppna och har issues: RS-2 (RSSI-varningen saknar marginal), SC-1 (skanningen avgör lika rena kanaler på tabellordning), HD-1 (HDMI-läget säger fullt omfång utan att veta om skärmen tar det) och VI-1 (det formella radbuffertbeviset täcker inte `VINTERP`). De tre första har strikta xfail-test.

HDMI-paketen, skyddsbanden, föramblerna och VIC stämmer i alla tre lägena enligt en avkodare skriven fristående från Core:s. `VINTERP` ger rätt rader och vikter också vid fältets första och sista rad, i full geometri. Skanningen fastnar inte. I `WAIT_BEFORE_VSYNC` hittade jag inget utöver den dokumenterade gränsen för ringen.

Planens frågor:

| Fråga | Svar |
|---|---|
| Kan RSSI-varningen svälta en kanal för gott när båda är svaga? | Två mottagare som båda är låga varnar inte. Men gränsen saknar marginal: 19 % mot 21 % varnar alltid, och mixern tar då den andra i varje par (RS-2). Värre var att varningen höll mixern kvar på en trasig mottagare (RS-1, rättat) |
| Kan skanningen fastna på en kanal med lås men brus? | Nej. Varje kanal avgörs senast 200 ms efter insvängningen, och en brusig låst kanal förlorar mot en ren. Bland rena kanaler vinner den som står först i tabellen (SC-1) |
| Kan flashlagret skriva fel sektor vid strömavbrott mitt i en radering? | Ja, före rättningen: en halvraderad post kunde laddas, och nästa sparande raderade sektorn med den riktiga posten (FL-1, rättat) |
| Stämmer HDMI-paketens ECC och skyddsband mot CEA-861 och HDMI 1.4 i varje läge? | Ja, i 720p60, 720p50 och DVI. Omfångsflaggan följer inte CTA-861:s regel för skärmar utan QS (HD-1) |
| Ger `VINTERP` rätt vikt vid fältets första och sista rad? | Ja, för 240–288 källrader och båda fälten. Andra läsporten är inte formellt bevisad (VI-1) |

## Vad jag gjorde

| | |
|---|---|
| Läst | `rssi_adc.v`, `mix_chan.v`, `line_mixer.v`, `mixer2.v`, `chan_scan.v`, `flash_store.v`, `puck_ui.v` (laddning och menyfält), `tmds_link.v`, `tmds_encoder.v`, `vblend.v`, `fb_display.v`, `genlock_timing.v`; modellerna `rssi_ref.py`, `line_mixer_ref.py`, `chan_scan_ref.py`, `flash_store_ref.py`; testerna och testbänkarna för dem; formalharnesken; commit-meddelandena 3bb863b och 440b576 (RSSI-regeln) |
| Egna körningar | Sex skript under `repro/` mot orörd RTL ur 072dbde, rådata i `repro/results.txt` |
| Rättat | RS-1 och FL-1 på egna grenar, var och en med regressionstest och negativ kontroll; sammanslagna efter hela sviten (status i tabellen nedan) |
| Inte gjort | Ingen hårdvara. XTX:s datablad för flashen gick inte att läsa, så modellen för ett avbrott är ett antagande. CTA-861 finns inte i repot; regeln om Q-bitarna är hämtad ur Linux DRM, som citerar den |

Belägg: **[S]** simulerat mot oförändrad RTL eller mot en modell som Core:s test håller lika med RTL, **[K]** läst ur koden, **[D]** standard eller datablad, **[H]** antagande som måste mätas.

## Fynd i korthet

| # | Fynd | Allvar | Belägg | Status |
|---|---|---|---|---|
| RS-1 | En svag mottagare tar aldrig över från en trasig när de går ur takt | Hög | S | Rättat, Core `fix/weak-receiver-takeover` |
| FL-1 | Avbruten radering: en aldrig skriven post laddas, nästa sparande raderar fel sektor | Medel | S, H | Rättat, Core `fix/flash-unidirectional-check` |
| HD-1 | AVI-infoframe säger fullt omfång utan att skärmens QS är känd; `RGB_FULL = 0` ändrar bara flaggan | Medel | D, K, S | Core #23, xfail |
| RS-2 | RSSI-varningen saknar marginal mellan mottagarna | Medel | S | Core #21, xfail |
| SC-1 | Lika rena kanaler avgörs på tabellordning | Låg–medel | S | Core #22, xfail |
| VI-1 | Radbuffertbeviset täcker inte `VINTERP = 1` | Låg | K | Core #24 |

---

## RS-1. En svag mottagare tar aldrig över från en trasig [S]

Var: `mix_chan.v` (`hist_n`, `well_n`), `line_mixer.v` (`s_cur`), samma regel i `model/line_mixer_ref.py` (`_solo`).

En rad som kommer medan mottagarens RSSI varnar räknas som dålig i kanalens hälsa (440b576: "so lone-line decisions leave the receiver too"). Utan par byter mixern kanal på hälsa bara när den aktuella kanalens åtta senaste rader är dåliga och den andras åtta är friska. En svag mottagare är aldrig frisk, så den kan aldrig ta över på det sättet. Tystnadsregeln hjälper inte, eftersom den trasiga mottagaren fortsätter leverera rader.

Scenariot är diversityns grundfall: B har starkare RSSI men dekodern olåst (flervägsutbredning, en lös kabel, en dekoder som tappat), A har svagare RSSI men ren bild. En olåst dekoder frigår och kommer ur takt, så inga rader paras.

Belägg (`repro/review2_mixer_weak.py`, strömmarna ur `sim/test_mixer.py::test_unlocked_current_channel_out_of_step`, A aktuell och olåst, A fem och en tredjedels rad före B):

| Körning | Par | B:s rader visade | A:s dåliga rader visade | B aktuell från beslut |
|---|---:|---:|---:|---:|
| E1: B svag hela tiden | 0 | 0 av 72 | 69 av 72 (3 utelämnade) | aldrig |
| E1c: samma utan varning | 0 | 65 av 72 | 11 | 19 |
| E1p: B svag, i takt | 72 | i alla par | 0 | 0 |

RTL och modell är lika i alla tre körningarna, beslut för beslut och ord för ord. I takt fungerar det, eftersom regeln för dåliga rader kommer före regeln för svaga.

Rättning: `mix_chan.v` för en andra historik med bara dåliga rader (`dead`, `self_ok`, `peer_dead`), och `line_mixer.v` byter också när den aktuella kanalen är död och den andra har inga dåliga rader. Utan svaga rader är de nya signalerna lika med `sick` och `self_well`, så M4 och alla äldre test är oförändrade. Två svaga mottagare tar inte bilden från varandra, eftersom ingen av dem är död. Modellen har samma regel. Regressionstest `sim/test_mixer.py::test_weak_receiver_takes_over_from_a_broken_one` (B tar över vid sin åttonde rad, bara B därefter), negativ kontroll `::test_weak_rescue_rule_is_checked` (utan termen i `line_mixer.v` skiljer sig RTL från modellen).

## FL-1. Avbruten radering laddar en post som aldrig skrevs [S, H]

Var: `flash_store.v` (`S_SCAN`), `model/flash_store_ref.py` (`scan`).

Startläsningen godtog varje post med `A5` och rätt CRC-8. Sektorn som raderas är alltid den som inte har den nyaste posten, så själva raderingen tar aldrig bort den nyaste [K]. Men en sektor som lämnas halvraderad har kvar 256 gamla poster med enstaka bitar satta. CRC-8 fångar fel med få bitar; med många ändrade bitar släpper den igenom ungefär en post på 256. Löpnumrets höga byte får bitar satta, så en sådan post blir ofta "nyare" än den riktiga.

Belägg (`repro/review2_flash_interrupted.py`). Antagen modell [H]: en avbruten radering har satt varje nollbit med sannolikheten p, oberoende av varandra. Avbilden är den före det 513:e sparandet: sektor 0 har löpnummer 1–256, sektor 1 har 257–512, och sparandet raderar sektor 0. 4 000 avbilder per p:

| p | Fel post laddas | Varav band 6 eller 7 |
|---:|---:|---:|
| 0,02 | 2,45 % | 0,10 % |
| 0,05 | 14,27 % | 0,47 % |
| 0,10 | 23,62 % | 1,98 % |
| 0,20 | 22,68 % | 3,43 % |
| 0,30 | 13,45 % | 2,85 % |
| 0,50 | 3,25 % | 1,57 % |
| 0,90 | 0 % | 0 % |

I alla 3 198 fall med fel post raderar nästa sparande sektor 1, alltså sektorn med den riktiga nyaste posten, och den halvraderade sektorn lämnas kvar. RTL laddar samma skräppost som modellen på den första avbilden (band 5, löpnummer 1198, kalibreringen skräp). Band 6 och 7 kontrollerades inte vid laddning: RX5808 får då kanaltabellens tomma post, syntesordet 0, och menyn visar 0 MHz [K]. En avbruten programmering av en post gav högst 0,15 % fel.

Hur ofta det händer på kortet: raderingen sker en gång per 256 sparanden, 3 s efter en ändring, och tar cirka 65 ms. Hur en XT25F64F lämnar en avbruten radering är inte känt [H].

Rättning: byte 13 i posten (förut `FF`) bär Z, antalet nollbitar i byte 0–12. En radering sätter bara bitar och en avbruten programmering lämnar bara bitar satta, så datans nollbitar blir färre medan Z bara kan växa: varje fel åt ett håll upptäcks. En post godtas dessutom bara med band 0–5 och läge 0–2, det menyn kan ställa. Formatet ändras, så poster från äldre bitströmmar laddas inte (`BRINGUP.md`). Regressionstest `sim/test_flash_store.py::test_interrupted_erase_loads_only_written_records` (150 halvraderade avbilder: modellen laddar alltid löpnummer 512 och nästa sparande raderar den halvraderade sektorn igen; RTL laddar 512 på två avbilder där bara `A5` och CRC lurades) och `::test_record_outside_the_menu_is_not_loaded`. Negativa kontroller: `no_zero_count` (den gamla kontrollen laddar posten), `no_range` (band 7 laddas).

## HD-1. Omfångsflaggan utan skärmens QS [D, K, S]

Var: `tmds_link.v` (`pb3`), `ycbcr2rgb.v`.

HDMI-läget sänder RGB i fullt omfång och säger det i varje AVI-infoframe (Q1:Q0 = 10). För 720p är standardomfånget för RGB begränsat. CTA-861 tillåter ett annat Q-värde än formatets standard bara när skärmen anger QS i sitt Video Capabilities Data Block. Linux DRM (`drm_hdmi_avi_infoframe_quant_range`) följer regeln och citerar den. Ingenting här läser skärmens EDID (DDC ligger på stift 52/53, som är konfigurationsstift och inte används). En skärm utan QS kan därför strunta i flaggan och visa bilden som begränsat omfång, alltså den krossade svärta HDMI-läget skulle undvika [D]. Det är en fråga för bänken, inte ett fel som syns i simulering.

Dessutom ändrar `RGB_FULL = 0` bara flaggan (Q = 01, begränsat), inte bildpunkterna [K]. En infoframe byggd med det beskriver bilden fel.

Belägg (`repro/review2_hdmi_independent.py`, `sim/tb_hdmi.v` avkodad av en avkodare skriven för granskningen, med tabellerna ur HDMI 1.4 och paritetsregistret ur hdl-util/hdmi): 40 aktiva rader med 8 klockors förambel och 2 klockors skyddsband, 4 dataöar utan fel i förambel, skyddsband, TERC4, bit 3 på kanal 0 eller BCH-paritet, huvudet `82 02 0D`, kontrollsumman 0, RGB, 16:9, VIC 4 eller 19 efter `hz50`. Q är 2 med `RGB_FULL = 1` och 1 med `RGB_FULL = 0`. DVI har bara styrkoder i släckningen och inga skyddsband.

Planerad rättning (ägarens, efter bänken): mät rampen med DVI och HDMI på de skärmar som spelar roll (`docs/MATPROTOKOLL.md` blad 16) och läs deras EDID med en dator. Spelar en skärm utan QS roll: sänd begränsat omfång med Q = 0, vilket varje skärm läser rätt, och låt `RGB_FULL` välja det. Core #23; xfail `sim/test_review_2026_10_14.py::test_hdmi_limited_flag_means_limited_pixels` (med `RGB_FULL = 0` ligger i dag 487 av 1 600 avkodade bildpunkter utanför 16–235).

## RS-2. RSSI-varningen saknar marginal [S]

Var: `rssi_adc.v` (`warn`), `model/rssi_ref.py`.

En mottagare varnar efter tre avläsningar under 20 % om den andra är kalibrerad, har en avläsning och inte är låg. Mellan de två finns ingen marginal. Medan A varnar tar mixern B i varje par utan blandning, oavsett HF-energin.

Belägg (`repro/review2_rssi_margin.py`, modellen som `sim/test_rssi_adc.py` håller lika med RTL, båda kalibrerade över samma omfång, 20 000 avläsningar per rad):

| A | B | A varnar |
|---|---|---:|
| 19 % | 21 % | 100 % |
| 15 % | 20 ± 2 % | 87,7 % |
| 12 % | 22 ± 4 % | 98,3 % |
| 18 % | 19 % | 0 % |

Nära golvet är båda svaga och RSSI brusig, och en skillnad på en eller två procentenheter avgör då bilden så länge den varar. Före varningen avgjorde HF-energin.

Planerad rättning (bänken och ägaren; trösklarna sätts ändå på bänken): varna bara när den andra ligger minst M enheter högre, eller en andra tröskel för "inte låg" över 20 %. Core #21; xfail `::test_rssi_warning_needs_a_margin`.

## SC-1. Lika rena kanaler avgörs på tabellordning [S]

Var: `chan_scan.v` (`best`), `model/chan_scan_ref.py`.

Skanningen behåller kanalen där en dekoder låser med lägst brusräkning, vid lika den tidigare. Brusräkningen är antalet lumasampel utanför 16–235 på 1 024 rader; en dekoder håller en ren bild inom det intervallet, så varje ren kanal får 0 eller nära 0 oavsett signalstyrka. En sändare utan kamera (platt bild) får också 0.

Belägg (`repro/review2_scan_ties.py`): egen sändare på F4 och en annan på A1, båda rena, start från F4: A1 behålls. F4 låst men brusig och R8 ren: R8 (rätt). Bara F4, brusig: F4 (rätt). Varje kanal avgörs senast `MAX_MS` efter insvängningen (`chan_scan.v`, `both_decided`), så skanningen fastnar inte [K].

Planerad rättning (ägarens): behåll startkanalen vid lika, och avgör lika på RSSI, som M6 har sedan 2026-10-13 men skanningen inte använder. Core #22; xfail `::test_scan_keeps_the_starting_channel_on_a_tie`.

## VI-1. Radbuffertbeviset täcker inte `VINTERP` [K]

Var: `formal/linebuf_props.v`, `fb_display.v`.

`fb_linebuf_slots` bevisar att en rad som begärs under en aktiv utrad hamnar på en plats som inte läses under resten av raden. Harnesket instansierar `fb_display` med `VINTERP = 0`, så andra läsporten och förhämtningen en rad längre fram är inte med. Marginalkontrollerna i `sim/margin_checks.vh` gäller också bara första porten.

Simulerat: `repro/review2_vinterp_full.py` loggar källrader och vikt för varje utrad i full 720-radsgeometri, för 240, 242, 243, 244, 287 och 288 källrader och båda fälten. Alla 8 640 rader stämmer med avbildningen i `fb_display.v`. Överst visar utrad 0 (övre fältet) och utrad 0–1 (nedre fältet) källrad 0 oblandad, eftersom positionen ligger ovanför rad 0. Nederst visar de sista en eller två utraderna sista källraden oblandad, eftersom rad s + 1 saknas. Ur koden: andra raden begärs en utrad innan den läses, till plats (s + 2) mod 4, som ingen av portarna läser under den raden.

Planerad rättning: en andra instans i harnesket med `VINTERP = 1` och egenskapen utvidgad till `lb_raddr_b`, och R-posten i `margin_checks.vh` för andra porten. Core #24; inget xfail-test, eftersom inget fallerar.

---

## Det som höll

- **HDMI-paketen** i 720p60, 720p50 och DVI, enligt en avkodare skriven fristående från `sim/test_hdmi.py` (HD-1 ovan). Felkorrigeringen, bitordningen (bit 0 först, paritet efter data) och fördelningen på kanalerna är desamma som i hdl-util/hdmi (`src/packet_assembler.sv`), en annan öppen implementation. `RGB_FULL = 1`: Q = 2. Ön ligger i vertikalsläckningen, efter vsync.
- **`VINTERP`** vid fältets första och sista rad (VI-1 ovan).
- **Kanalskanningen** fastnar inte och väljer en ren låst kanal före en brusig (SC-1 ovan).
- **RSSI-läsaren.** Två låga mottagare varnar inte varandra (18 % mot 19 %: 0 %). Bussdelningen mellan RSSI-läsaren, OLED:n och `tvp_ctrl`: jag hittade ingen väg till dödläge; RSSI höjer sin hold bara när OLED:n inte håller, och OLED:n startar bara när RSSI släppt [K]. En avläsning utan kvittens nollställer räknaren för låg, så varningen faller inom en runda när ADC:n försvinner [K].
- **Flashlagret** raderar aldrig sektorn med den nyaste posten själv, och en avbruten programmering av en post faller nästan alltid på CRC-8 (högst 0,15 % i modellen ovan). WP# drivs från skrivaktiveringen till slutet av radering och programmering.
- **`WAIT_BEFORE_VSYNC`.** Formellt bevisat för båda placeringarna (`formal/run.sh`: bildlängd, en full vsync, hela back porch med 1). Den kända begränsningen står i README: med 1 räcker inte `LOW`-ringen på 16 rader nederst i bilden. Parametern nås inte från `build.sh`.

## Återskapa

`repro/README.md`. Skripten ändrar ingen RTL.
