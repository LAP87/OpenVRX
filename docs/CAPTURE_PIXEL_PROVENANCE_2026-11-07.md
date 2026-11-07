# Vilka sampel bidrar till Capture-pixlarna?

Uppgift 79, fryst Core `031bba053943ee04ce303ae75b5e701746169c97`, tree `83734acc12ba3c4708a002fef3fd85abd9279fc5`. En första modellobservation med rad-/fältberoende innehåll. **Numerisk återläsning och åtta skadekontroller passerade; en tillagd timinggrind i rootgranskaren föll. Paketet är stoppgranskat, inte ett godkänt timing- eller RTL-resultat.** Ingen producent ändrades och modellen kördes inte om.

## Ny täckning

De tidigare gråstaplarna är identiska mellan rader och ramar. Här har två NTSC-ramar 974 olika åttadelade kodmönster, ett per aktiv källrad. Varje mönster beror på global rad och horisontell del. Insignalen är rektangulär sexbitarsvideo med sync/blank/vit = 4/20/60, inte filtrerad IQ eller verkliga C5-nivåer. H = 2542,2222 sampel, 40 MS/s, COMB=1, AVG=8, WHITE_X8=20, ursprunglig bootkontroll.

Två listomslag behåller modellens ursprungliga minnesvärden och registrerar endast vilket insignalsampel som skrev varje position. Därmed sparas aktuellt sampel och faktisk föregående-radspartner för varje utmatad pixel. Originalets step, nivåföljning, linjebeslut och pixelfunktion är orörda. Det är observerade modellberoenden, inte en oberoende implementation av kontrolltimingen.

| Kontroll | Resultat |
|---|---|
| Olika källradsmönster | 974 av 974 |
| Utmatade ord/rader | 350 640 ord, 974 radstarter |
| Alla utmatade pixlar | 701 280, samtliga numeriskt kontrollerade |
| Slutna rader | 973 / 700 560 pixlar |
| Sista raden | 360 ord / 720 pixlar utan slutmarkör; inte räknad som sluten rad |
| Pixlar med föregående-radspartner | 698 400 |
| Där aktuell kod och partnerkod skiljer sig | 676 729 / 96,90 % av partnerpixlarna |
| Källramar, utmatade radstarter | 487 + 487 |
| Oberoende aritmetik | 16 ± trunc(abs(c_now+c_prev−40)×701/256), klippt 1..254 |

Primärvalidatorn och rootgranskarens separata pixelåterläsning kontrollerade ordvärden, källrad, F-/radetikett och partnerns rad/position mot de sparade insignalsbyten. Root härledde källans aktiva kodvärden från rad-/delformeln utan import av DUT eller primärorakel. Detta rena nivåfall har korrekta radetiketter; [#34:s motexempel](CAPTURE_STARTUP_NATIVE_2026-11-07.md) vid andra nivåer är fortfarande olöst.

Åtta faktiska skador avvisades: pixelbit, partner ur samma rad, fel F, kopierade pixlar från annan rad, saknad kamfilterpartner, fel COMB-val, falskt hårdvarupåstående och falskt nativepåstående. Ursprungspaketet validerades före och efter skadorna. Rootfortsättningen läste samma sparade åtta kopior; inga nya kontroller skapades.

## Varför rootgranskningen stoppade

Rootgranskaren lade efter modellkörningen till kravet att första pixelns aktuella insignalsampel inte fick ligga före aktivstart 362. Den gränsen var inte motiverad i det ursprungliga uppgiftskontraktet. Den får inte användas ensam för att utropa ett produktionsfel, och den ändrades inte för ett grönt utfall.

| Första pixelns position från fysisk källradstart | Antal rader |
|---|---|
| 360 | 25 |
| 361 | 276 |
| 362 | 667 |
| 363 | 4 |
| 364 | 2 |

301 rader börjar alltså med ett aktuellt sampel ur källans sista 1–2 backporch-sampel, medan kamfilterpartnern kan ligga inne i föregående rads aktiva innehåll. De observerade värdena stämmer med den kombinationen. Exakt önskad horisontell fas/croppning är inte fastställd av detta experiment. Innan en fix eller en starkare timingacceptans görs behövs ett förankrat resamplingskontrakt som skiljer tillåten NCO-/PLL-fas från felplacerat bildinnehåll. Ingen alignment söktes för bättre siffror.

Originalets felande roothelper, logg, kontrakt och rådata är bevarade. En separat bunden fortsättning slutförde endast återstående kontroller av befintliga skadekopior, källarkiv, hashbindningar och avslutade processer. Den ursprungliga fulla pixelloopen, modellen och rootjobbet kördes inte om.

## Körningar och gränser

Modell 4,824 s rc0; primäråterläsning/skador 2,130 s rc0; första root 1,638 s rc1; stoppfortsättning 0,491 s rc0; final 0,280 s rc0. Inga signaler eller timeout. 264 Git-/arkiv-/källfiler oförändrade; 480 unika befintliga bindningar kontrollerade i final. Råinventeringen omfattar 25 fas-/kontrollfiler, 18 472 353 byte, med hash och storlek.

Python 3.12.12 och enbart stdlib. Modellargv använde den upplösta Pythonbinären och därmed basinstallationens sys.prefix; förberedelsens venv-probe var inte fasens prefix. Den skillnaden är uttryckligen sparad i återläsningen. Inga paket installerades eller byttes.

[Exakt observatör och primärvalidator](../research/experiments/capture_pixel_provenance_2026-11-07/) och [maskinläsbar sammanfattning](CAPTURE_PIXEL_PROVENANCE_2026-11-07.json) är publicerade. Hela produktionskedjan, oberoende kontrolltiming, RTL, IQ/brus/färg, PAL, återlåsning, verkliga C5-skalor, FPGA och hårdvara ingår inte. Det stoppade rådet för #34 har inte återstartats.
