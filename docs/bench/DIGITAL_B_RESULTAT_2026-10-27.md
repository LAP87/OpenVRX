# Digital B på bänken 2026-10-27: första bilden från C5VRX:s sampelbuss

Protokoll för uppgift 68 och 69 ([guiden](GUIDE_DIGITAL_B_2026-10-26.md), [planen](../ARBETSPLAN.md)). Allt nedan är mätt på hårdvara den dagen om inget annat sägs; loggar, fångster och bilder ligger i `bench-logs/2026-10-26-digital-b/` (utanför repona), tidsordningen i `NOTES.md` där.

## Uppställning

Kamera med VTX på F4 (5 800 MHz), XIAO ESP32-C5 med det frysta klockbygget av C5VRX (`388d2d1` + klockpatch, `bench-logs/c5vrx-clkout-2026-10-24/`, rapporterar `version=5.0.0-dev`), kopplad till Tang Nano 20K J5 enligt guidens tabell (klocka på J5-4, D4–D9 på J5-3/5/6/10/12/13, jord), TVP-modulen helt urkopplad. Tang i WSL via usbipd; XIAO:n flashad av ägaren via c5vrx.com i Chrome (esptool över usbipd tog inga byte, orsak inte utredd).

## Resultat i ordning

| Tid | Bitström | Vad som syntes | Förklaring |
|---|---|---|---|
| 13:12 | `6b845e8` (uppgift 64, den frysta) | grå ruta med svarta kanter, lysdiod 2 släckt | mottagaren stod på A2, sändaren på F4: C5VRX:s egen utsignal utan mottagning |
| 13:35 | samma, kanalen rättad, mottagning C/N 20 dB | fortfarande grå, lysdiod 2 släckt | inga rader ur `cvbs_capture`: dess nivåskiljare startade på 12 och väntade synk vid kod 4, men C5VRX lägger synken på 23 |
| 13:52 | bänkbygge med startnivåerna 23/31 | svartvit bild, hjärtslag 1 Hz (B låser) | nivåerna var enda spärren för rader |
| 14:22 | `digin/levels` `bf50d5e` (svepande skiljare) | samma bild, lysdiod 2 fast; hackar och hoppar, extremt grynig | hacket mätt 15:24 (nedan); grynet är källans C/N plus vår förstärkning |
| 15:55 | `digin/levels` (medelvärdesskiljare, sha `58cc180e…`) | laddad efter att ägaren gått; inte sedd | nästa bänkpass |

## Mätt på bussen

M3-proben (`m3_probe.fs`) visade klockan (räknarens tak, över 33,5 MHz) och alla sex databitar växlande (`tog 3F`). Den nya M7-proben (Core `top/m7_digin_probe.v`, navets `tools/bench/uart_raw.py`, `digin_decode.py`, `digin_model.py`; [BENCH.md](../BENCH.md) "Den digitala bussen") gav samplen själva:

| Storhet | Värde | Fångst |
|---|---|---|
| Bussklocka | 40,0 MHz (0x262 × 65 536 Hz, upplösning 65 kHz) | alla |
| Radperiod | 2 530–2 544 sampel (63,6 µs); utjämningspulser var 1 272:e i vertikalintervallet | `134336`, `134701` |
| Synkpuls | 182–190 sampel (4,7 µs) | `150820` |
| Nivåer (`OUTPUT 1.0x`) | synktopp 22–24, släckning 30–32, video 40–56, vitt 62; synktoppen brusar ±8 koder | `134336`, `150820` |
| Övrigt | samplen kommer parvis (varje värde två klockor); enstaka sampel med kod 0 (0,1–0,5 %, 2,3 % under C5VRX:s startkalibrering) | |
| Under C5VRX:s DC-kalibrering vid start (sändaren på: kanalhopp) | skräp: dubbelnollor, synktopp 0–45; 844 låsväxlingar på 13,6 s | `150629` |

Probens levande `cvbs_capture` på bussen, ren signal, per 13,6 s-fönster (15:24, bygget `bf50d5e` + ingångsvippa): 180 000 radmarkörer (13 300 rader/s), 16–24 dåliga, 18–24 låsväxlingar, 65 miljoner ord, men radlängder 1 643–1 728 ticks mot mixerns krav 1 716 ± 2.

**Jittret** (`edge_jitter.py` på `150820`): den råa radstarten (tre låga sampel i rad) vandrar upp till ±32 sampel rad till rad av synktoppens brus; 9 av 23 radperioder utanför 2 542 ± 3. Med åtta sampels glidande medelvärde före skiljaren: alla 25 inom ±3. Mixern förkastar rader med fel längd (hacket), och radstarten flyttar bilden (hoppen).

## Rättningar (Core-grenen `digin/levels`)

- Olåst sveper skiljaren från 12 ett steg per två radperioder (8–40 och runt) tills en rad med riktig synk mätts; nivåerna tas då rakt ur den raden; ett tappat lås släpper dem (den gamla IIR-följaren strandade efter kalibreringsskräpet och hittade aldrig tillbaka: 15:08). Lås kräver att pulsen som startade raden nått `T_EQ`.
- Skiljaren jämför summan av de åtta samplen före det aktuella med åtta gånger nivån (parameter `AVG`; registrerad summa, annars föll `mix.b_clk` till 70,4 MHz mot kravet 75).
- Ett gammalt RTL-fel: `period` lästes ett sampel för kort, så `hp` lade sig ett under sann period medan svänghjulet steg `hp + 1`; kvittade sig tills medelvärdet fick modellens `hp` att röra sig. Rättat till modellens definition.
- Test (`sim/test_cvbs_capture.py`, 9 av 9): C5VRX:s nivåer låser via svepet och ger fälten bitexakt; svart bild med synk under `T_EQ` låser aldrig; brus σ 3 på C5VRX-nivåer ger högst 5 % rader utanför ±2 ticks (3,4 % i modellen) utan tappat lås, och utan medelvärdet hittas inte ens vertikalsynken. Snabbsviten 720 gröna.

Simulerat och byggt, inte sett på skärmen: bitströmmen med medelvärdet laddades 15:55 efter att ägaren gått.

## Vad som är kvar

1. **Titta på bilden** med medelvärdesbygget (i Tang sedan 15:55, sha `58cc180e…`; sammanslaget i Core `main` som `518abfb`, hela sviten 892 gröna): mindre hack och hopp väntas, inte noll (modellen: 3,4 % rader utanför toleransen). Steget efter är redan simulerat på Core-grenen `digin/line-start` (`228aa04`): låst startar raden vid svänghjulets förutsägelse och kanten nudgar bara nästa förutsägelse med en sextondel, periodskattningen går kant till kant utan dödzon och sås med låsperioden. Modellen ger då noll rader utanför toleransen på brusströmmen, och kanter som flyttas ±8 sampel ger alla längder inom toleransen (negativ kontroll ±72: lås tappas). Bitströmmen är byggd (`gateware/build/digin-line-start/`, sha `194a45b9…`, `mix.b_clk` 105 MHz), inte laddad: nästa bänkpass laddar den och jämför. Bredare medelvärde är fel väg (modellen: 16 sampel ger 84 fel, 32 ger 223 av ~720).
2. **Förstärkningen:** `cvbs_capture` antar vitt − släckning = 2,5 × (släckning − synk); C5VRX ger 31/8 = 3,9. Allt över kod 51 klipps till vitt och bruset förstoras 1,55×. En parameter för den digitala källan.
3. **Mätning med proben** kräver att bryggan inte låser sig: läsaren öppen före laddningen, aldrig en pratande bitström utan läsare, tyst bitström efteråt; efter en låsning hjälper bara ström till båda korten (XIAO:n matar Tang via skyddsdioderna när bara Tang dras ur).
4. Guidens steg 7 (avbrott) och 8 (PR #257-paketet), sedan utkastet till Twotoz.
5. `c5.py` mot kortet över usbipd: inga byte togs emot, Chrome fungerade. Oförklarat.

## Filer

`bench-logs/2026-10-26-digital-b/`: `c5vrx-2026-10-27T12-*.log`, `c5vrx-session-17*.csv` (ägarens konsol- och sessionsloggar), `m3probe-1027-133848.jsonl`, `digin-probe-1027-*.txt` och `_digin.png`, `xiao-esptool-*.txt`, `NOTES.md`. Byggen: Core-arbetskopian `digin-fix` i WSL (`m4_dual_mix_digin.fs` sha `58cc180e…`) och kopian i Windows `OpenVRX-Core/gateware/build/digin-levels/`.
