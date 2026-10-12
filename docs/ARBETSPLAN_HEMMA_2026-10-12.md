# Arbetsplan för hemma, från 2026-10-12

Det som går att göra med det som finns hemma nu (Tang Nano 20K, AIO-kamera S2-OSD med sändare, Eachine Moneagle, en dator, en HDMI-skärm eller TV) utan att vänta på beställningar. Punkterna är oberoende av varandra. Den som inte hinns med ligger kvar; det som inte kräver hårdvara kan Fable eller Opus ta nästa dag (markerat "även utan kort").

## På bänken (kräver dig)

1. **M0 på en HDMI-skärm.** Flasha `m0_testpattern` (bygg med `gateware/build.sh m0_testpattern` i WSL eller använd den arkiverade bitströmmen från senaste bygget) med `openFPGALoader -b tangnano20k`. Testbilden ska synas; prova gärna två skärmar. Det är första beviset på att vår HDMI-utgång tas emot av något alls. Resultat: skärmmodell, om bilden kom direkt, om skärmen rapporterar 720p60. Anteckna i `docs/bench/`.
2. **M2a, minnestestet.** Bara Tang och USB-kabel. Kör `m2a_memtest` med fas 180°, 225° och 270° enligt `gateware/README.md` ("M2a") och `BRINGUP.md`; läs UART-loggen (BL616 visar två serieportar, UART:en är oftast den andra). Det här är mätningen som avgör SDRAM-fas och läspunkt för alla bildbyggen, och den går att göra utan kamera och dekoder. Resultat: vilka faser och läspunkter som är rena.
3. **EDID från skärmarna hemma.** Läs EDID från varje HDMI-skärm, TV och (när de finns) glasögon med en dator: Monitor Asset Manager eller AW EDID Editor på Windows, `edid-decode` på Linux. Spara utskriften i `docs/bench/edid/<skärm>.txt`. Det är grunden för kompatibilitetsarbetet i rapporten `research/GOGGLES_OCH_XR_2026-10-12.md` (avsnittet om signalregler).
4. **Latensreferens med Moneagle.** Kamera → sändare → Moneagle, filmat med telefonens höghastighetsläge enligt `OpenVRX-Core/tests/latency/`. Ger glas-till-glas-tiden för en färdig produkt att jämföra vår kedja mot. Anteckna kameraläge (PAL/NTSC) och kanal den här gången.
5. **Beställningsbeslut.** Rapporten föreslår ett smalt testset (HDZero BoxPro, Walksnail Goggles X, XREAL One plus en HDMI-till-USB-C-adapter med egen matning) och ett fullt. Bestäm vilket, och om rev A-kortets I-klassade dekoder går att köpa i små volymer (agenterna får inte göra inköpskontroller). Materiallistan för uppstarten kommer som uppgift 6 i arbetsplanen 2026-10-12.

## Även utan kort (Fable eller Opus kan ta dem)

6. **HDMI-läge med AVI-infoframe.** Rapporten visar att vår utgång är ren DVI med fullt RGB-omfång, vilket en standardstrikt skärm tolkar som begränsat omfång och krossar svärtan. En AVI-infoframe (VIC 4 för 720p60, VIC 19 för 720p50, RGB, omfångsflagga) i `dvi_tx_gowin.v` tar bort gissningen. Simulering mot en TMDS-avkodare i Python, bygg M0/M4/M6, HDMI-paren som förut. Ägarbeslut behövs inte: DVI-läget blir kvar som parameter.
7. **Var den varierande raden ska ligga.** I `LOW` växlar bilden mellan 750 och 751 rader, och i dag ligger den extra raden i bakre släckningen, så avståndet vsync-till-bild ändras varje bild. Rapporten vill att båda placeringarna (före och efter vsync) kan väljas, för att prova på skärm. En parameter i `genlock_timing.v` med formellt bevis som förut.
8. **1080p-väg för XR-glasögon, underlag.** Alla rapporter om 720p in i XR-glasögon är negativa; de vill ha 1080p60. Tang Nano 20K klarar inte 1080p i sin egen HDMI. Skriv ett underlag med de tre vägarna (extern skalare 720p→1080p60 som produktklass, extern HDMI-sändare på rev B, större FPGA) med vad som behöver mätas för var och en. Inget byggs.
9. **Mätblad för glasögon.** Rapportens femstegsplan (EDID, lägesmatris T1–T8, latens per steg) som ett blad i mätprotokollet (uppgift 7 i arbetsplanen 2026-10-12).

## Bokföring

Allt som görs hamnar i navets `docs/bench/` (bänkresultat) eller i arbetsplanen 2026-10-12 (kod och dokument), pushat på `main`, så att kvällens sammanfattning kan göras ur GitHub.
