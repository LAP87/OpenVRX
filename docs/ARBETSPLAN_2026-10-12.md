# Arbetsplan från 2026-10-12: det som återstår före kortet

Utgångspunkt: Core `main` 2dca245 plus testrättningen från 2026-10-12, 651 test gröna (parallellt, en process per simtest). Puck `main` pekar på Core. Vad som gjordes fram till nu står i [ARBETSPLAN_2026-10-05.md](ARBETSPLAN_2026-10-05.md); det här dokumentet är listan framåt, i den ordning den ska göras. Ingenting här kräver hårdvara. Det som kräver kortet står sist, och det som är ägarens beslut står i ett eget avsnitt i den gamla planen ("Beslut som är ägarens") med en förklaring från 2026-10-12 i navets commit-logg.

Regler för den som arbetar: `AGENTS.md`, plus de tre reglerna som inte rörs utan att commit-meddelandena till Core e873f4b, e113cf6 och 6c12099 lästs (LOW-videogrinden, mixerns F-gräns, släppta fält). En uppgift i taget, egen gren från `main`, sammanslagning med `--no-ff` bara med hela sviten grön (parallellt är fint, men varje test i egen byggkatalog) och uppgiftens byggen gjorda. Pusha efter varje commit. Efter varje uppgift: en rad under "Sjunde passet" i den gamla planen eller en ny rubrik här, och bocka av i tabellen nedan.

## Ordning

| # | Uppgift | Varför först | Klart när | Status |
|---|---|---|---|---|
| 1 | Parallellkörare i repot och byggkatalogsrevision | Tre gånger på en vecka har parametriserade test krockat i delade byggkataloger när de körs parallellt; sviten tar 18 min parallellt mot över 90 min i följd, så alla kör parallellt | `gateware/tools/run_suite.py` (en process per simtest, N åt gången, samlad rapport, returkod); en revision som visar att varje test har egen byggkatalog (skript som listar `build/`-namn per test och fäller dubbletter); README beskriver köraren | klar, Core `main` 5314ed1, 2026-10-12 |
| 2 | M6:s seed-beroende | `build.sh m6_puck_proto` kan falla i klockroutning beroende på seed och källa; orsaken är inte utredd sedan 2026-10-05 | Orsaken beskriven (vilket nät, vilken resurs nextpnr saknar) och en åtgärd som gör att M6 routar med seed 0–3 på nuvarande `main` (klockrestriktion, PLL-placering eller buffer), byggt och bokfört i README | |
| 3 | Störningskampanjen färdig | C3 stannade vid 200 av 260 frön; frö 1345 fäller på för kort stimulus och behöver ett längre källkontrakt | De 60 återstående fröna körda; frö 1345 med längre stimulus grönt eller ett RTL-fel med regressionstest; loggen i `gateware/sim/FUZZ_2026-10-07.md` avslutad med totalsiffror | |
| 4 | Simuleringskontroller för det formella bevisets öppna punkter | `gateware/formal/README.md` punkt 4 och 5 (att `frame_low`/`ll_low` hinner fram före rad 0, och att radbufferten är skriven innan den läses) är inte bevisade, bara antagna | Assertions i `tb_fb.v`/`tb_chain.v` som fäller om marginalen går under en klocka respektive om en rad läses före sitt sista ord; negativ kontroll med fördröjd skrivare | |
| 5 | Arbetsplan och README i fas | Allt från 10 till 12 oktober står bara i Codex journal; Core README:s statusrad anger 604 test | Den gamla planen har "Sjunde passet" (finns sedan 2026-10-12, kompletteras), README:s statusrad säger aktuellt antal och vad som byggts ur vilken commit, `BRINGUP.md` nämner FILT-fältet och loggraden på 62 byte | |
| 6 | Materiallista för uppstarten | Begärd 2026-10-08, inte gjord | `docs/MATERIAL_UPPSTART.md` enligt NATTPASS_2026-10-08 M1: rad per sak, antal, vilket steg, varifrån uppgiften kommer; inga butiker, priser eller länkar | |
| 7 | Mätprotokoll per milstolpe | Begärd 2026-10-08, inte gjord | `docs/MATPROTOKOLL.md` enligt M2: ett blad per mätning i "Mätningar när kortet finns", plus jämförelse mot en färdig mottagare med HDMI och ett blad TV mot VCR | |
| 8 | Konsekvenskoll av dokumenten | Begärd 2026-10-08, inte gjord | Lista över meningar i Core README, BRINGUP, navets AGENTS och REVIEW som inte stämmer med reglerna från 8–12 oktober, och rättade i samma commit | |
| 9 | Interpolation i höjdled som parameter, standard av | Bildkvalitet som kan göras utan kort: två källrader per utrad i stället för närmaste rad (`fb_display.v`, BOB); utgångsunderlaget avsnitt 4 | Parameter `VINTERP`, modell i `fb_ref.py`, test mot modellen och negativ kontroll, M4/M6 byggda med och utan, README-rad om kostnad i LUT och Fmax. Standard av tills kortet säger annat | |

Uppgift 9 är störst och görs sist. Uppgift 3 kräver många timmar maskintid men lite tanke; den kan köras medan 4–8 görs, under bygglåset bara när den bygger.

## Kräver kortet

Oförändrat från den gamla planens tabell "Mätningar när kortet finns": M0 bild, M3 prob, M2a SDRAM-fas, M2 bild via fältminne, M4 två mottagare, M6 meny och logg. Nya mätpunkter sedan dess: TV mot VCR (FILT i menyn), låsflaggan i loggen, genlockens klipp mot en riktig HDMI-skärm (klippet behåller vsync sedan C1), och en jämförelse mot en färdig mottagare med HDMI-utgång.

## Inte i listan, med skäl

- TI:s firmware-patch till TVP5150AM1: kräver patchdata som inte får ligga i repot; flerbyteskrivning finns.
- RSSI: Tang Nano 20K saknar ADC.
- Ett bildläge i stället för två, IOB-register, licens, ESD-klamp, 1080p för XR-glasögon: ägarens beslut.
- Rev A-kortet: beställs först när M4 går på moduler.
