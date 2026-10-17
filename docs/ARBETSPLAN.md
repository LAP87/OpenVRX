# Arbetsplan

Den enda levande planen för OpenVRX, från 2026-10-17. De daterade planerna och nattpassen under `docs/` är historik (listan sist). Nya uppgifter, beslut och läget skrivs här.

## Läge 2026-10-17

**Inget är kört på hårdvara.** Baslinjen före kortet är taggen `v0.1-prehw` i alla tre repona: [RELEASE_v0.1-prehw.md](RELEASE_v0.1-prehw.md) säger vad som är simulerat, byggt och inte provat.

| Repo | `main` | Läge |
|---|---|---|
| OpenVRX-Core | `ff2efce` (taggen) | 772 test: 769 gröna och 3 strikta xfail (Core #21–#23); snabbsviten 702 test på 235 s; M0, M3, M2a, M4 och M6 byggda ur `ff2efce`, alla klockor över 75 MHz |
| OpenVRX-Puck | `c80ed57` (taggen) | rev A-schemat i SKiDL (126 delar, ERC utan fel), KiCad 9-projekt med netlistan, inte routat; `core/` på `ff2efce`; 6 test gröna |
| OpenVRX (navet) | efter uppgift 29 | planer, beslut, mätprotokoll, material- och plocklistor, underlag i `research/` med [register](../research/README.md) |

Codex rootacceptans gäller Core `bf05ac0` (sviten och M0/M4/M6 med standardval, 2026-10-13; [STATUS.md](overnight/2026-10-08/STATUS.md)). Ändringarna efter det (uppgift 21–25) har ingen rootacceptans; FIFO-ändringen i uppgift 21 har Codex verifierat riktat och formellt.

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
| Radbuffertbeviset täcker inte `VINTERP = 1` | Core #24 | arbete |
| Rootacceptans av Core efter `bf05ac0` (uppgift 21–25, byggena ur `ff2efce`) | Codex grindar, [kommentaren på navets `main`](https://github.com/LAP87/OpenVRX/commit/17d91821547feed81be3e8ec77c550e31b5a916c#commitcomment-204744668) | Codex |
| Rev A, nästa schemavarv: kontakter för OLED och RX5808-SPI i sandwichen, anteckningarna i Puck #3 (temperaturklass, PLL-filter med flera) | Puck `design/rev_a/LAYOUT.md` avsnitt 7, Puck #3 | ägaren väljer när |
| Rev A: routning | Puck `design/rev_a/kicad/` | ägaren |
| Snabblistan väljs om när test har tillkommit (testet för listans ordning saknas i den) | Core `gateware/tools/quick_tests.txt` | arbete, vid nästa hela körning |
| Navet #2 (inköpsregeln och licensen) är besvarat och genomfört, #3 är granskningens index | navet #2, #3 | ägaren stänger |
| Fem grenar på origin med egna commits: navet `vibe/formal-open-points-sim-plan` och `vibe/post-ninth-pass-records` (öppen PR #4), Core `codex/handoff-2026-10-06` och `codex/inherited-claude-2026-10-05`, Puck `codex/inherited-claude-2026-10-05` | [ARBETSPLAN_2026-10-14.md](ARBETSPLAN_2026-10-14.md), uppgift 29 | ägaren |

Nya uppgifter läggs i en tabell här med nummer från 30, varför, klart när och status (commit och datum).

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
