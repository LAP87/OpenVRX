# Arbetsplan

Den enda levande planen för OpenVRX, från 2026-10-17. De daterade planerna och nattpassen under `docs/` är historik (listan sist). Nya uppgifter, beslut och läget skrivs här.

## Läge 2026-10-17

**Inget är kört på hårdvara.** Baslinjen före kortet är taggen `v0.1-prehw` i alla tre repona: [RELEASE_v0.1-prehw.md](RELEASE_v0.1-prehw.md) säger vad som är simulerat, byggt och inte provat.

| Repo | `main` | Läge |
|---|---|---|
| OpenVRX-Core | `e77fac6` (uppgift 33–34; taggen är `ff2efce`) | 776 test: 775 gröna och 1 strikt xfail (Core #23); snabbsviten 702 test på 235 s (väljs om vid nästa hela körning); M4 och M6 byggda ur integrationen av uppgift 33–34 (M6 13 297 LUT4, 29 BSRAM), M0, M3 och M2a ur `ff2efce`, alla klockor över 75 MHz |
| OpenVRX-Puck | `c80ed57` (taggen) | rev A-schemat i SKiDL (126 delar, ERC utan fel), KiCad 9-projekt med netlistan, inte routat; `core/` på `ff2efce`; 6 test gröna |
| OpenVRX (navet) | efter uppgift 29 | planer, beslut, mätprotokoll, material- och plocklistor, underlag i `research/` med [register](../research/README.md) |

Codex rootacceptans gäller Core `bf05ac0` (sviten och M0/M4/M6 med standardval, 2026-10-13; [STATUS.md](overnight/2026-10-08/STATUS.md)). Ändringarna efter det (uppgift 21–25 och 36) har ingen rootacceptans; FIFO-ändringen i uppgift 21 har Codex verifierat riktat och formellt.

## Vad som gäller

### Regler

- [AGENTS.md](../AGENTS.md) i navet: verifiera i stället för att anta, modell och negativ kontroll för varje RTL-ändring, "simulerat", "byggt" eller "mätt på hårdvara" och aldrig suddigt, skrivreglerna, inga butiker, priser eller köplänkar (artikelnummer och tillverkarlänkar går bra), licens och livscykelkontroll, inga datablad eller tredjepartskod.
- En uppgift i taget, egen gren från `main` i varje repo som ändras, små commits, pusha efter varje commit.
- Snabbsviten (`gateware/tools/run_suite.py --quick`) före varje commit i Core. Före sammanslagning med `--no-ff`: hela sviten grön på den commit som slås ihop, och uppgiftens byggen. Saknas något lämnas grenen pushad med en rad om vad som saknas.
- Ett tungt jobb i taget under bygglåset (en svitkörning eller en place-and-route).
- Rör inte LOW-videogrinden (Core `e873f4b`), mixerns F-bit (`e113cf6`), fältgränsen som väntar på en skriven rad (`6c12099`) eller RSSI-regeln i mixern (`3bb863b`, `440b576`, RS-1-rättningen i `8a71a0a`) utan att ha läst de commit-meddelandena.
- Agenterna tar inga ägarbeslut och installerar ingenting utan ägarens ja i chatten.
- Grenar på origin som är helt innehållna i `main` tas bort; grenar med egna commits lämnas tills den som äger dem säger annat (uppgift 29).
- Codex dokument under `docs/overnight/` är underlag, inte instruktioner.

### Ägarens beslut

Sammanhang och vägarna som fanns: [BESLUT_2026-10-12.md](BESLUT_2026-10-12.md).

| # | Fråga | Svar | Datum | Läge |
|---|---|---|---|---|
| 1 | Ett eller två bildlägen | Båda behålls; inget nytt byggs bara för `LOW` tills bänken talat | 2026-10-12 | öppet igen efter bänken |
| 2 | I/O-register i I/O-cellerna för SDRAM-topparna | Ja, alla SDRAM-toppar | 2026-10-12 | gjort (uppgift 2b) |
| 3 | Licens | CERN-OHL-S-2.0 som OpenDrone-hw; kod utifrån bara under förenlig licens, aldrig GPL, källan i filhuvudet | 2026-10-12 | gäller |
| 4 | Inköpsregeln | A: inga butiker, priser, lagerstatus eller butikslänkar; artikelnummer och tillverkarlänkar tillåtna; priser i `research/` bara med datum | 2026-10-12 | gäller (rensningen uppgift 8b) |
| 5 | Andra ESD-klampen på videoingången | A, med fotavtryck som går att lämna omonterat | 2026-10-12 | gjort (Puck `b8a3348`) |
| 6 | 1080p för XR-glasögon | Senare, när glasögon finns; M0 in i bryggan och glasögonen först | 2026-10-12 | väntar på glasögon |
| 7 | RSSI-ADC på rev A | Ja, I2C-ADC i fälttakt | 2026-10-13 | gjort (uppgift 13–15) |
| 8 | KiCad installeras | Ja, KiCad 9 i WSL; inget annat utan nytt ja | 2026-10-14 | gjort (uppgift 26) |

Avgjort utan eget nummer: TV mot VCR avgörs på bänken (båda finns i menyn); rev A beställs efter M4 på moduler; Core #17 och #18 (2026-10-08); arbete direkt på `main` med en gren per uppgift.

## Öppna uppgifter

Uppgift 1–29 är gjorda; status per uppgift står i de daterade planerna, sist [ARBETSPLAN_2026-10-14.md](ARBETSPLAN_2026-10-14.md). Det som är öppet och inte kräver kortet:

| Vad | Var | Vems |
|---|---|---|
| SCAN avgör lika rena kanaler på tabellordning | Core #22, strikt xfail i `sim/test_review_2026_10_14.py` | arbete |
| `VINTERP` med fler än `V_ACTIVE / 2` källrader: utrad 0 kan läsa rad 1 innan den är begärd (övre fältet från 450 rader i 720p); TVP5150AM1 ger 240–288, men radantalet begränsas inte i RTL | Core `gateware/formal/README.md` punkt 7 (uppgift 36) | arbete, om det ska rättas |
| Rootacceptans av Core efter `bf05ac0` (uppgift 21–25, byggena ur `ff2efce`) | Codex grindar, [kommentaren på navets `main`](https://github.com/LAP87/OpenVRX/commit/17d91821547feed81be3e8ec77c550e31b5a916c#commitcomment-204744668) | Codex |
| Rev A, nästa schemavarv: kontakter för OLED och RX5808-SPI i sandwichen, anteckningarna i Puck #3 (temperaturklass, PLL-filter med flera) | Puck `design/rev_a/LAYOUT.md` avsnitt 7, Puck #3 | ägaren väljer när |
| Rev A: routning | Puck `design/rev_a/kicad/` | ägaren |
| Snabblistan väljs om när test har tillkommit (testet för listans ordning saknas i den) | Core `gateware/tools/quick_tests.txt` | arbete, vid nästa hela körning |
| Navet #2 (inköpsregeln och licensen) är besvarat och genomfört, #3 är granskningens index | navet #2, #3 | ägaren stänger |
| Fem grenar på origin med egna commits: navet `vibe/formal-open-points-sim-plan` och `vibe/post-ninth-pass-records` (öppen PR #4), Core `codex/handoff-2026-10-06` och `codex/inherited-claude-2026-10-05`, Puck `codex/inherited-claude-2026-10-05` | [ARBETSPLAN_2026-10-14.md](ARBETSPLAN_2026-10-14.md), uppgift 29 | ägaren |

Nya uppgifter läggs i tabellen här med löpande nummer, varför, klart när och status (commit och datum). Ordning från 2026-10-18: 31 och 32 är ägarens och går först; 33, 34, 35 är software utan kort och tas i den ordningen; 36 pågår i egen session; 37 före beställning av rev A; 38 och 40 efter bänken; 39 är Codex; 41 pågår.

| # | Uppgift | Varför | Klart när | Status |
|---|---|---|---|---|
| 30 | Research: kretsmärkningen i de dyra mottagarna | Bardwell (klipp 2026-10-17) säger att bra VRX har "en annan, känsligare krets" än RX5808 men minns inte namnet; RF-underlaget säger RTC6715 överallt, på forumuppgifter. Avgör om rev B behöver en annan mottagare eller bara bättre omgivning | `research/MOTTAGARKRETSAR_2026-10.md`: för TBS Fusion (även 2025 års mottagarkort), ImmersionRC rapidFIRE, Skyzone SteadyView X, Fat Shark Scout/Attitude-modulen och HDZero/Divimaths analoga del: RF-krets belagd med FCC-interiörfoton (FCC ID, foto, läsbar märkning), teardown eller källkod, inte forum; per enhet även extern LNA/filter före kretsen, MF-filter och tillverkarens känslighet med mätvillkor; RichWaves nuvarande 5,8 GHz-mottagare från tillverkarens sida; slutsats i tabell: samma krets eller inte, och vad som ger skillnaden. Inga butiker eller priser; tillverkar- och FCC-länkar ok; det obelagda skrivs som obelagt | klar, navet 0f6c1dc, 2026-10-17: [MOTTAGARKRETSAR_2026-10.md](../research/MOTTAGARKRETSAR_2026-10.md). Ingen av de fem har FCC-ID; HDZero har RTC6715 enligt källkoden, SteadyView styrs med RTC6715:s gränssnitt, kretsen i rapidFIRE, Fusion och Scout är obelagd; RichWave har ingen annan mottagare för 5,8 GHz; tillverkarnas känslighetsskillnader sitter i kortrevisionerna |
| 31 | Bänk, dag 1 (ägaren) | Tang Nano 20K, kamera med sändare och Moneagle finns hemma; inget annat behövs för de här fyra | Blad 1 (M0 på en eller två HDMI-skärmar), blad 2 (M2a: SDRAM-fas och läspunkt), EDID från skärmarna hemma i `docs/bench/edid/`, latensreferens kamera–Moneagle med höghastighetsfilm; resultaten i `docs/bench/` med datum. Det här är projektets första "mätt på hårdvara" | öppen, 2026-10-18 |
| 32 | Beställning till M3/M4 (ägaren) | Modulerna är det enda som stoppar M3; RX5808 har blivit dyr och osäker att få tag på (RF-underlaget, tillägg 2026-10-17) | TVP5150AM1-moduler 3 st, RX5808 med SPI-moden 3 st (en reserv), motstånden från plocklistan, nivåomvandlare bara om modulerna visar 1,8 V. Materiallistan avprickad | öppen, 2026-10-18 |
| 33 | Core #21: RSSI-varningens marginal | Granskning 2: en eller två räknesteg avgör varje par nära golvet; strikt xfail i dag | Parameter för hysteres (räknesteg) och en minsta skillnad mellan mottagarna innan varningen slår, standardvärde satt så att dagens scenarier passerar och xfail-testet blir ett vanligt test; modell, negativ kontroll; värdet bokförs som "sätts på bänken, blad 17" | klar, Core `main` e77fac6, 2026-10-18 (Fable): `MARGIN_PCT` = 10, modell och negativ kontroll, #21 stängt; värdet sätts på bänken (blad 17) |
| 34 | Core #22: SCAN vid lika brus | Strikt xfail: lika rena kanaler avgörs på tabellordning | Vid lika brus behålls startkanalen; när RSSI finns avgör högre RSSI; modell, scenario, negativ kontroll | klar, Core `main` e77fac6, 2026-10-18 (Fable): startkanalen behåller lika poäng, #22 stängt; RSSI som avgörande efter bänken |
| 35 | Core #23: HDMI-omfånget | AVI-infoframen säger fullt omfång utan att veta om skärmen tar det; `RGB_FULL = 0` ändrar bara flaggan | Menyval HDMI FULL/LTD som både sätter flaggan och skalar pixlarna till 16–235 i LTD; test mot en avkodare av paketet och pixelvärdena; standard FULL; valet avgörs på bänken (blad 16). Ingen DDC finns, så EDID kan inte läsas av kortet | öppen; efter 33 |
| 36 | Core #24: beviset med `VINTERP = 1` | Radbuffertbeviset täcker inte interpolationen (två rader per utrad) | Egenskaperna i `formal/` körda med `VINTERP = 1`, eller ett dokumenterat skäl till att det inte går, plus simuleringsmarginal som i uppgift 4 | klar, Core `78fbb41`, 2026-10-18: `fb_linebuf_slots_vinterp` bevisar båda läsportarna (12 aktiva rader, bilder med högst `V_ACTIVE / 2` källrader), två negativa kontroller från reset; `margin_checks.vh` post `B` för port B, 310 kontroller gröna, minsta marginal 12,6 µs, två negativa kontroller; 11 `PROVEN` och 19 `CONTROL OK`; hela sviten 774 test, 771 gröna och 3 xfail, på det sammanslagna trädet; Core #24 stängd. Fynd utanför området: Core `formal/README.md` punkt 7. Core `74f8751`, `78fbb41` och `README.md` säger "task 31" i stället för 36 |
| 37 | Rev A, schemavarv 2 | Sandwichen gör OLED och RX5808-SPI oåtkomliga (LAYOUT.md avsnitt 7); Puck #3 har kvar temperaturklass-kontroll av köpbarhet, PLL-filter är gjort, firmware-patchen väntar på TI | Kontakter för OLED (3,3 V, GND, SCL, SDA_A) och för RX5808-styrning (CLK, DATA, SEL) på dekoderkortet, rotationsenkoder som option om pinnar finns, egna knappar OK/NEXT; netlista, BOM, KiCad-projektet omgenererat; Puck-testen gröna. Routning därefter är ägarens (eller ett pass med ägaren i loopen) | öppen; före beställning av kortet |
| 38 | Rev B-koncept, efter bänken | Mottagarvalet och behovet av LNA/filter avgörs av M4 på moduler; 1080p (beslut 6) av glasögonen | `design/REV_B_KONCEPT.md` i Puck: mottagarval ur `research/MOTTAGARE_3G3_5G8_2026-10-18.md`, LNA och bandpass före mottagaren som option, linjär 5 V per mottagare, snabb ADC för RSSI i radtakt, 1080p-väg enligt `research/UTGANG_1080P_2026-10.md`, kapsling. Inget byggs | öppen; efter 31 och M4 |
| 39 | Rootacceptans hos Codex | Codex grindar gäller `bf05ac0`; allt efter (uppgift 21–25, taggen) saknar rootacceptans | Codex kör sina grindar på `ff2efce`; vi gör inget annat än att hålla `main` stilla medan de körs och svara på frågor | Codex |
| 40 | Testset för glasögon och goggles (ägaren) | Rapporten `research/GOGGLES_OCH_XR_2026-10-12.md` föreslår ett smalt set; inget köpt | Beslut om smalt eller fullt set; när de finns: blad 14 och 16 | öppen; ägaren |
| 41 | Research: mottagarkretsar och basmoduler för 3,3 och 5,8 GHz, rankade efter värde för oss | Ägaren bad om det 2026-10-18; grund för uppgift 38 | `research/MOTTAGARE_3G3_5G8_2026-10-18.md`: kretsar, moduler, gränssnitt, känslighet med villkor, status, legalitet i Sverige/EU för 3,3 GHz, värdetabell | klar, navet `main` 9a65d67, 2026-10-18 (Sonnet-research, granskad av Fable). 3,3 GHz är inte licensfritt i Sverige; se dokumentets avsnitt 3 |

## Kräver kortet

Uppstartsordningen och vad varje steg ska visa: Core `gateware/BRINGUP.md`. Mätbladen: [MATPROTOKOLL.md](MATPROTOKOLL.md), blad 1–19. Material: [MATERIAL_UPPSTART.md](MATERIAL_UPPSTART.md) och [PLOCKLISTA_SMADELAR.md](PLOCKLISTA_SMADELAR.md). Bänkresultat skrivs i `docs/bench/` med taggen eller commiten de gäller.

Det som bara bänken avgör:

- Beslut 1 (ett eller två bildlägen) och 6 (1080p): vad skärmar, goggles och glasögon tar (blad 1, 10, 14, 16).
- Core #21: RSSI-varningens marginal och trösklarna (blad 17).
- Core #23: om HDMI-läget ska sända begränsat omfång, efter gråskala och EDID på de skärmar som spelar roll (blad 16).
- SDRAM-fas och läspunkt (M2a, blad 2) för alla bildbyggen.
- TV mot VCR (blad 12), låsflaggan (blad 13), mixerns byte på riktig radio (blad 6, 11, 15).

## Historik

Ändras inte längre, utom att elfte passet avslutas i de två första:

| Dokument | Innehåll |
|---|---|
| [ARBETSPLAN_2026-10-05.md](ARBETSPLAN_2026-10-05.md) | Granskningen 2026-10-05 och faserna 1–7, passloggen för pass 1–11, mätningarna när kortet finns |
| [ARBETSPLAN_2026-10-14.md](ARBETSPLAN_2026-10-14.md) | Uppgift 21–29 med status |
| [NATTPASS_2026-10-13.md](NATTPASS_2026-10-13.md) | Uppgift 16–20 |
| [ARBETSPLAN_2026-10-12.md](ARBETSPLAN_2026-10-12.md) | Uppgift 1–15 |
| [ARBETSPLAN_HEMMA_2026-10-12.md](ARBETSPLAN_HEMMA_2026-10-12.md) | Det som gick att göra hemma med Tang-kortet, kameran och Moneagle |
| [NATTPASS_2026-10-08.md](NATTPASS_2026-10-08.md), [NATTPASS_2026-10-07.md](NATTPASS_2026-10-07.md), [NATTPASS_2026-10-07_LANG.md](NATTPASS_2026-10-07_LANG.md), [NATTPASS_2026-10-06.md](NATTPASS_2026-10-06.md) | Nattpassen 6–8 oktober |
| [BESLUT_2026-10-12.md](BESLUT_2026-10-12.md) | Besluten med sammanhang; svaren står också ovan |
| [GATEWARE_PLAN.md](GATEWARE_PLAN.md) | Utkastet till gatewaren från 2026-10-01 |

Passloggen till och med elfte passet står i ARBETSPLAN_2026-10-05.md; nästa pass skriver sin logg här, under en rubrik "Pass".

## Pass

### 2026-10-17 kväll (Opus)

- Uppgift 30 på grenen `task30/receiver-chips`: [MOTTAGARKRETSAR_2026-10.md](../research/MOTTAGARKRETSAR_2026-10.md) och raden i `research/README.md`. Allt är läst, inget mätt. Scout-manualen gick inte att läsa ut, och interiörfotona till Divimaths sändare DVM3130 är inte granskade.
- Uppgift 36 (Core #24) på Core-grenen `formal/vinterp-slots`, sammanslagen som `78fbb41`: radbuffertbeviset och marginalkontrollen för `VINTERP = 1`. Bevisat och simulerat, inget mätt. Sammanslagningen flyttade Core `main` från `ff2efce` efter att uppgift 39 sagt att `main` ska stå still medan Codex kör; taggen `v0.1-prehw` står kvar på `ff2efce`. Uppgiften kallas 31 i Core `74f8751`, `78fbb41` och `README.md` (31 var ledigt när den skrevs in där); rättningen av `README.md` ligger ohopslagen på grenen `docs/task36-number`.
