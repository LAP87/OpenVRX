# Kvällspass 2026-10-08

Uppdraget är [NATTPASS_2026-10-08.md](../../NATTPASS_2026-10-08.md). Användaren valde uttryckligen uppgiftsgrenar och merge till `main` efter verifiering. C1 → C3 → C2 är ordningen. Codex/root granskar, kör grindarna och integrerar; en Luna på max hjälper med avgränsade filer. Den befintliga Vibe-sessionen äger M1–M3 och startas eller styrs inte av Codex.

## C1 — integrerat 2026-10-09

- Gren `fix/genlock-cut-vsync`, Core `3aed0b7`, pushad. En bild som klipps efter tre tidiga triggers behåller nu hela vsync-pulsen. Bara den direkt följande bilden får kortare släcklucka för upphämtning. Båda behåller hela sista släckraden, där displayens skalning och radindex återställs.
- Modellen och de nya mikrosimuleringarna: 9 gröna på liten och 750-raders vertikal geometri. Gammalt hopp till sista raden fäller pulsregeln; avstängd upphämtning fäller samma tvåbilders fasgräns. Riktade fixturetester fäller för kort upphämtning, en tredje kort bild, för kort `HOLD` och saknad synkpuls.
- Fullsviten på fryst `3aed0b7` är klar: **447 passed**, inga xfail, skips eller processfel, på 1:29:36. Formalgrinden gav 7 bevis och 14 verkliga motexempel för de avsiktliga felvarianterna.
- Råköraren avslutade med `FAIL_SOURCE_CHANGED` (returstatus 1), eftersom 19 genererade cocotb-XML hamnade i dess källinventering. Inga indata ändrades eller togs bort. Ett separat, granskat kvitto verifierar alla 172 filer mot ursprungsarkivet, samtliga pytest-utfall och exakt de insamlade XML-rapporterna. SDRAM-testet som avsiktligt stoppar simulatorn har sin förväntade felrapport; andra XML-fel avvisas. Fem negativa kontroller av kvittogrinden passerade. Råloggar och råstatus är bevarade i `private/notes/evening_2026-10-08/c1`; inget testundantag lades till i RTL eller modell.
- **M4 seed 0 och M6 seed 3 är byggda och manifestverifierade** på fryst `3aed0b7`; alla fem klockor klarar 75 MHz. M0-referensen och samtliga fyra HDMI-par har godkända manifest/fuse-kontroller. M6 seed 2 misslyckades i klockroutningen (`Can't route the clocks.clk_27 net`), innan slutlig timing. Diagnostiken bevaras; standardseed 2, stift, BUFG, IOB och SDC är oförändrade. C2:s krav på seed 2 återstår.
- Båda README är uppdaterade efter granskning. Endast dessa dokument skiljer den accepterade källan från grenens sista commit. `fix/genlock-cut-vsync` är mergad med `--no-ff` och pushad till Core `main` **`629806f`**. Puck-gitlänken är uppdaterad via egen gren och merge till `main` **`e655d14`**; dess aktuella test gav **1 passed** på 1,42 s. Inga schema- eller BOM-filer ändrades.
- Kompakt verifieringsjournal: [C1.json](evidence/C1.json).

## C3 och C2

C3:s privata körplan, adapter och sekventiella körjournal är förberedda; den nya 260-frökampanjen har inte startat. Seed 126 är omspelat med byte-identiskt stimulus på Fables `e113cf6`-RTL med separat strikt checker, och separat på fryst C1 `629806f`. **Båda rapporterar ett SDRAM-läschecksummefel och X/Z på utgången**. Terminalens första grupp är inte hela fyndlistan.

Pixelobservationen av det gamla LOW→BUF-fönstret på `e113cf6` visar däremot 72 blanka prov med stängd videogrind, varav 45 före publicering. Rå probe-FAIL använde det äldre gråvärdet; separat källbundet kvitto jämför med faktiska `202020`. Se [LOW_BUF_FINDING.md](../2026-10-07/LOW_BUF_FINDING.md). Luna triagerar de kvarstående läs-/X/Z-fynden från sparade råloggar innan större kampanj. C2-koden har inte påbörjats.

## Avgränsningar

Dagens inlästa bas var navet `87a5717`, Core `e113cf6` och Puck `08aa8f4` med ren Core-gitlänk. Fable rapporterade 433 gröna; de angivna testsökvägarna samlade 434 innan C1:s 13 nya testfall. Tidigare nattens 432 gröna och två xfail hör till den frysta äldre revisionen `aece6eb`.

Ingen hårdvara är verifierad. F-bit-regeln, LOW-videogrinden, släpp av det fält skrivaren gick med i, stift, IOB, SDC, licens och BOM ändras inte här. TV/VCR jämförs genom C2:s meny senare, utan att ett fast filterval tas åt ägaren. Inga krediter eller delar köps. Automationens gamla körning till morgonen 8 oktober är avslutad; detta är det nya passet.
