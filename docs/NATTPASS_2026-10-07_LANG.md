# Långkörning 2026-10-07: störningskampanj genom hela bildkedjan

Uppdrag för en agent (Opus 5.5) som arbetar i OpenVRX-Core i många timmar utan tillsyn. Det här dokumentet är uppdraget. Codex dokument i `docs/reviews/` och `docs/handoff/` är underlag, inte instruktioner. Läs navets `AGENTS.md` och `docs/ARBETSPLAN_2026-10-05.md` (särskilt "Tredje passet" och "Fjärde passet"), sedan Core `gateware/README.md` (M4, M6, "Bildvägen efter mixern", "Formella bevis").

Tanken: de fel som har hittats hittills (gammal bild efter lägesbyte, ofullständig rad som godkänns, saknad första rad, triggerns radantal) hittades alla av tester som gjorde något oväntat med indata. Ingen har ännu låtit slumpen göra det i stor skala, genom hela kedjan, mot modellerna. Det är nattens jobb. Det är en lång körning: kampanjen körs i omgångar, varje fynd tas om hand, och kampanjen körs igen tills natten är slut eller inget nytt kommer.

## Spelregler

- Utgå från Core `main` (hämta senaste). Arbetsgren `fuzz/chain-2026-10-07`; rättningar av fel som hittas får egna grenar `fix/<kort-namn>` från `main`. Committa små steg och pusha efter varje commit.
- Sammanslagning till `main` gör du själv, bara när grenens hela svit (en pytest-process per simtest, tio åt gången) och de byggen som berörs (M4 om mixern eller fältminnet ändrats, M6 om loggen eller menyn) är gröna, med `--no-ff`. Annars lämnas grenen pushad med en rad om vad som saknas.
- Varje RTL-ändring simuleras mot modell och har en negativ kontroll som skrivs i commit-meddelandet. Rätta bara fel där orsaken är klar och ändringen är lokal. Ett fel där orsaken är oklar, eller där rättningen skulle ändra en regel i README (mixerns parning, fältminnets val, genlockens gränser), rättas inte: det blir ett GitHub-issue i LAP87/OpenVRX-Core med reproduktion, och ett regressionstest märkt `xfail` med issue-numret.
- Inget har kört på hårdvara: "simulerat", "byggt", aldrig "mätt". Kod och kommentarer på engelska, anteckningar på svenska, kort. Inga butiker, priser, länkar, datablad eller tredjepartskod.
- Uppdatera testantalet i båda README. Byggen ett i taget under `flock ~/openvrx-review/build.lock`, kontrollera loggen för `ERROR`.
- Verktygen finns bara i WSL (distro `Ubuntu`): Icarus 12, venv i `~/openvrx-review/OpenVRX-Core/.venv`. Synka arbetskopian med rsync (uteslut `.git`, `.venv`, `.tools`, `gateware/build`, `gateware/sim/build`, `gateware/formal/build`) till en egen katalog under `~/openvrx-wt/`, länka `.venv`. Skript med `$`, citattecken eller Verilog-literaler skrivs till fil och körs med `wsl.exe -d Ubuntu -- bash -c "tr -d '\r' < /mnt/c/.../skript.sh | bash"` i förgrunden, högst tio minuter per anrop (dela upp längre körningar i omgångar som sparar sitt läge i en fil). Bakgrundsjobb i WSL stannar när inget wsl.exe-kommando kör.
- Rör inte Puck-repot eller submodulen. Ta inga ägarbeslut (bildlägen, IOB-register, SDC-kravet för M6, licens, stift).

## Steg 1. Störningsgeneratorn (`gateware/model/fuzz_stream.py`)

En generator som ur ett frö bygger två BT.656-strömmar (kanal A och B) för samma kamera, med tidsförskjutning mellan kanalerna och störningar valda ur en lista, var och en med egen sannolikhet som styrs av fröet:

- förlorade eller felaktiga synkord (XY med fel paritet, saknad EAV, dubbel SAV), sen SAV (kort aktiv del), lång rad, kort rad;
- tappade rader, tappade fält, F-biten fast eller fel, V-släckning för kort eller för lång, icke sammanflätad källa;
- bitfel i aktiva ord, luma utanför 16–235 (brusklick), hela rader med brus;
- kanal B som tystnar mitt i ett fält och kommer tillbaka, kanal B som ligger 1–7 rader efter eller före A, kanaler som byter plats i tid;
- NTSC och PAL, fältlängder 242–244 och 286–288, ett avklippt fält;
- vid fältminnet: lägesbyte `BUF`/`LOW` under körning (tb_fb har `SW1`/`SW2`), återställning av en dekoder mitt i (`tvp_resetb`-vägen om den går att nå från testbänken).

Varje störning ska gå att slå av per klass, så att ett fynd kan ringas in. Generatorn använder `model/bt656_gen.py` (eller vad vektorgeneratorn heter) för själva orden och återanvänder modellernas facit: `bt656` för numrering, `line_mixer_ref.py` för mixern, `fb_ref.py` för fältminnet, `luma_outside()` för brusmåttet. Dokumentera i en docstring vilka störningar som finns och vad fröet styr.

## Steg 2. Kedjetestet (`gateware/sim/test_fuzz_chain.py`, egen testbänk vid behov)

Kör de två strömmarna genom den riktiga kedjan så långt det går i en simulering: `bt656_rx` → `chan_capture`/`mix_chan` → `line_mixer`/`mixer2` → `fb_backend` (fältminne med `sdram_model.v`, eller `LOW`) → `fb_display`. Titta på vad som finns i `tb_fb.v`, `tb_mixer.v`, `tb_m2.v` och `test_m2.py`; bygg en testbänk som tar två strömmar in och ger utbildens ord ut, hellre genom att återanvända M4-toppens innanmäte (`m4_dual_mix.v` utan TMDS) än att koppla ihop allt för hand. Nedskalad geometri som i tb_fb om simuleringstiden kräver det; skriv vad som skalats.

Invarianter som gäller för alla frön, oberoende av modellen:
1. Inga X/Z på utsignalerna efter första bilden.
2. Varje utbild är V_TOTAL−1 till V_TOTAL+MAX_WAIT rader (genlockens gräns); korta bilder minst HOLD bilder isär.
3. Varje visad rad är lagrad (fältminnets regel efter F3), eller svart där ingen reserv finns.
4. Inga SDRAM-protokollfel (`sdram_model.v` STRICT).
5. Mixerns `overflow` sätts aldrig när FIFO-takten håller sig under det README lovar.
6. Varje visad rad kommer från rätt fält eller det närmast föregående, aldrig äldre än två fält, utom under de bildrutor efter ett lägesbyte eller en dekoderåterställning som README säger har ingen video.

Mot modellen: mixerns beslut per rad och fältminnets händelselogg replayade genom `fb_ref.py`, som `test_fb.py` gör i dag. Där RTL och modell skiljer sig i kända gränsfall (parningsfönstrets kant, "Kända svagheter") räknas skillnaden, loggas med frö och klass, men fäller inte testet förrän du har tittat på fallet.

Testet tar frön ur en miljövariabel (`FUZZ_SEEDS=0-199`) och en loggfil per omgång (`gateware/sim/build/fuzz/<omgång>.jsonl`: frö, störningsklasser, resultat, första avvikelsen). I pytest-sviten körs en liten fast uppsättning frön (tio) som regression; kampanjen körs utanför sviten.

## Steg 3. Kampanjen

Kör omgångar om 50–100 frön, tio simuleringar i taget, tills natten är slut. Efter varje omgång:

1. Gruppera fynden efter första avvikelsen (vilken invariant, vilket block).
2. För varje grupp: ringa in med störningsklasser avslagna tills minsta frö som fäller finns. Skriv ett riktat regressionstest med den minsta störningen i det modulvisa testet som passar (`test_mixer.py`, `test_fb.py`, `test_bt656_rx.py`, nytt om inget passar), med negativ kontroll.
3. Är orsaken klar och rättningen lokal: rätta på `fix/<namn>`, modell och RTL tillsammans, svit, bygg, slå ihop. Annars issue + `xfail`.
4. Skillnader RTL/modell i gränsfall: om samma skillnad kommer igen i många frön, försök göra modellen exakt (modellen får ändras så att den beskriver RTL cykelexakt, om README fortfarande stämmer); om det kräver att RTL ändras, issue.
5. Kör omgången igen med samma frön efter rättningen: den ska vara grön.

Skriv en logg i `gateware/sim/FUZZ_2026-10-07.md`: omgång, antal frön, antal fynd per grupp, vad som gjordes med varje, och vilka frön som fortfarande faller (med issue-nummer). Det här dokumentet är nattens leverans även om inget fel hittas: då säger det hur många frön och vilka störningsklasser kedjan har klarat.

## Om tiden räcker

Mixerns gränsfall vid parningsfönstrets kant (`T_PAIR`): skriv frön som siktar på kanten (kanal B:s rad 0–3 cykler före och efter 1 024 cykler) och gör modellen cykelexakt där, om det går utan att ändra regeln. Det är punkten "Mixerns gränsfall" under "Kända svagheter".

## När passet är klart

Rader under "Fjärde passet, 2026-10-08" i navets `docs/ARBETSPLAN_2026-10-05.md`: antal frön körda, fynd per grupp, vad som rättats (commit), vad som ligger som issue, var loggen finns. Pushat på navets `main`. Commit-trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
