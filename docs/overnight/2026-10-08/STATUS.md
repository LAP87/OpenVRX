# Kvällspass 2026-10-08

Uppdraget är [NATTPASS_2026-10-08.md](../../NATTPASS_2026-10-08.md). Användaren valde uttryckligen uppgiftsgrenar och merge till `main` efter verifiering. C1 → C3 → C2 är ordningen. Codex/root granskar, kör grindarna och integrerar; en Luna på max hjälper med avgränsade filer. Den befintliga Vibe-sessionen äger M1–M3 och startas eller styrs inte av Codex.

## C1 — pågår

- Gren `fix/genlock-cut-vsync`, Core `3aed0b7`, pushad. En bild som klipps efter tre tidiga triggers behåller nu hela vsync-pulsen. Bara den direkt följande bilden får kortare släcklucka för upphämtning. Båda behåller hela sista släckraden, där displayens skalning och radindex återställs.
- Modellen och de nya mikrosimuleringarna: 9 gröna på liten och 750-raders vertikal geometri. Gammalt hopp till sista raden fäller pulsregeln; avstängd upphämtning fäller samma tvåbilders fasgräns. Riktade fixturetester fäller för kort upphämtning, en tredje kort bild, för kort `HOLD` och saknad synkpuls.
- Den frysta fullsviten på `3aed0b7` kör från `private/notes/evening_2026-10-08/c1/core-3aed0b7`, under `/home/lenny/openvrx-review/build.lock`. 447 tester samlas. Körningen har en pytest-process per testfil i högst tio samtidiga processer som en sammanhållen grind; inga andra simulator- eller byggpaket körs samtidigt. Varje processretur, rålogg och källhash före/efter sparas i `private/notes/evening_2026-10-08/c1/suite-3aed0b7`.
- Återstår: slutlig fullsvit inklusive utökad formalgrind (7 bevis, 14 negativa kontroller), M4 och M6 ett i taget, byggmanifest och HDMI-fuses, båda README, verifierad merge och Puck-gitlänk.

## C3 och C2

Luna läser kampanjens käll- och parameterkontrakt och förbereder en privat körplan för C3. Ingen ny kampanj har startat. OVN-F1 ska spelas om med samma scenario mot `e113cf6`; den körningen och nya frön mot slutlig C1-bas får egna identiteter. C2-koden har inte påbörjats.

## Avgränsningar

Dagens inlästa bas var navet `87a5717`, Core `e113cf6` och Puck `08aa8f4` med ren Core-gitlänk. Fable rapporterade 433 gröna; de angivna testsökvägarna samlade 434 innan C1:s 13 nya testfall. Tidigare nattens 432 gröna och två xfail hör till den frysta äldre revisionen `aece6eb`.

Ingen hårdvara är verifierad. F-bit-regeln, LOW-videogrinden, släpp av det fält skrivaren gick med i, stift, IOB, SDC, licens och BOM ändras inte här. TV/VCR jämförs genom C2:s meny senare, utan att ett fast filterval tas åt ägaren. Inga krediter eller delar köps. Automationens gamla körning till morgonen 8 oktober är avslutad; detta är det nya passet.
