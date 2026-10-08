# Slutrapport för OpenVRX, 7–8 oktober 2026

Sparad 2026-10-08 07:43 Europe/Stockholm. Core och Puck är granskade och pushade
till `main`. Inget har körts på hårdvara. Navets slutrapport och evidence
pushas i detta avslut; därefter stoppas nattens automation.

## Resultat och källversioner

| Kontroll | Resultat | Källversion och evidence |
|---|---|---|
| Fryst Core-baslinje | 395 passed, 1 xfailed; 1:25:56 | `7cc4eda`, [rålogg](evidence/baseline-core-7cc4eda.log) |
| Fryst slutlig Core-svit | **432 passed, 2 xfailed; 1:26:02; returstatus 0** | `aece6eb`, alla 171 källhashar oförändrade, [metadata](evidence/final-suite.json), [rålogg](evidence/final-suite.log) |
| M4/M6 | Båda byggda, alla klockkrav uppfyllda; 25 BSRAM vardera | Byggindata matchar `7cc4eda` och slutlig kod; [M4](evidence/m4_dual_mix.build.json), [M6](evidence/m6_puck_proto.build.json) |
| Mixer och displayens negativa kontroll | 29 passed, 1 xfailed (#18) | Varje beslut/ord mot modell, både A/B-återkomst och gamla RTL-regeln, [rålogg](evidence/targeted-mixer-display.log) |
| Full PAL/LOW | Fyra hela LOW-bilder, 2 880 rader; bara känt #17 | Frö 49, åtta fält, 1160,8 s, [kontrakt/resultat](evidence/r06-pal-low-full.json) |
| Riktig kampanjåterupptagning | ran 0, 0 left | Identiskt käll-/parameterkontrakt; [rålogg](evidence/r06-pal-resume.log) |
| Puck | 1 passed på 1,35 s, med negativa kontraktskontroller | Gitlänk `fb6896a`, [metadata](evidence/final-puck.json), [rålogg](evidence/final-puck.log) |

Core är pushad som **`fb6896a`**, Puck som **`8917d27`**. Core-integrationen
bevarar Opus nattarbete till `059aadd` och Codex granskade ändringar.
Slutcommitens tre Markdown-ändringar påverkar inte den testade koden:
övriga 168 filer är byte-identiska med frysta `aece6eb`.
[Integration och hashjämförelse](evidence/final-integration.json).

## Vad Codex färdigställde

Fuzzrundor får nu ett strikt kontrakt för inställningar, källor, verktyg
och seeddefinitioner. Ändrade eller gamla okontrakterade rundor avvisas
före simulering och filändring. 28 små kontroller passerar; riktig resume
har också verifierats. Äldre loggar finns kvar.

Mixeråterkomsten täcks för både A och B mot modellen, med den gamla
regeln som negativ kontroll. #18:s xfail avgränsas till den observerade
omarkerade fältstarten, efter RTL/modell-agreement.

Tre försvagningar av fuzzkontrollerna återställdes: korrupt läsning ska
fällas även utan senare bildbeslut; kameraförsprång får inte undanta
fältminnets egen ålder; för liten bildtäckning får inte passera vid
lägesbyte. Små negativa kontroller visar att upstream missade dessa fall.
[Evidence](evidence/upstream-oracle-negative-controls.json).

Ingen RTL-regel, bildlägespolicy, F-bit, stift, IOB, SDC, licens eller BOM
ändrades av Codex i detta pass. Vibes överlämnade dokument granskades och
checkades in med en daterad rättelse; dess session har inte startats eller
styrts igen. Luna/max sparade planen före kreditfelet; inga omförsök,
credits eller andra providers användes efter felet.

## Öppna fynd och nästa utvecklingspaket

| Fynd | Kvarvarande problem | Nästa steg |
|---|---|---|
| Core #17 | BUF→LOW kan visa video innan genlock/ring är redo, och läsa oskrivna ringplatser. | Bestäm när första LOW-bilden får visa video; därefter modell, fassvep, negativ kontroll och M4/M6-bygg. |
| Core #18 | Ett nytt mixerutfält med samma F och stigande radnummer blir osynligt för fältminnet. | Bestäm fältmarkeringens kontrakt innan F-regeln ändras. |
| **OVN-F1** | LOW→BUF kan behålla LOW:s videoflagga och visa RGB innan publicering, med en halvskriven SDRAM-läsning. | Följ [det avgränsade rättningspaketet](LOW_BUF_FINDING.md); börja med kontraktet för bilden som redan pågår vid bytet. |

OVN-F1 är belagt med byte-identiska stimuli och 72 aktiva RGB-prov,
varav 45 i BUF med video före publicering. Opus har bekräftat fyndet och
rättat sin logg. **En godkänd regressionssvit betyder inte att detta fel är
rättat**: frö 126 ingår inte bland svitens fasta frön. Den strikta kontrollen
hittar fortfarande `store/read` i den riktade uppspelningen.

Opus rapporterade 1 772 förstakörda frön. Dessa totalsiffror hör till hans
då gällande kontrollversioner; omgångarna har inte körts om med de
återställda strikta kontrollerna. R05:s breda fuzz är avsiktligt uppskjuten
för att undvika dubbletter. R07 är diagnostiserat men kräver ägarbeslut;
övriga verifierbara nattpaket är accepterade.

Återupptagning av utvecklingen utgår från [WORKPLAN.md](WORKPLAN.md),
[tasks.json](tasks.json), [STATUS.md](STATUS.md) och
[COORDINATION.md](COORDINATION.md). Hårdvarubringup följer Cores
`gateware/BRINGUP.md`; simulator- och byggresultaten är inga mätningar på kort.
