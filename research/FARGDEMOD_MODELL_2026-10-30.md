# Färgdemoduleringsmodell i Core (uppgift 65, simuleringsdelen)

Datum: 2026-10-30. Core-grenen `vibe/colour-demod-ref-bc782a`, draft-PR LAP87/OpenVRX-Core #26.
Modell: `gateware/model/colour_demod_ref.py`, tester: `gateware/sim/test_colour_demod.py` (7 test, alla gröna).

## Vad modellen gör

Samma 6-bitars sampelström vid 40 MS/s som `cvbs_capture_ref.py` får på luma-vägen (C5VRX-bussen).
Kedja, helt i heltal (referens för framtida RTL):

- **Burstlåsning per rad**: NCO på 3,579545 MHz (32-bitars ackumulator, 8-bitars cos/sin-tabeller),
  fasen nollställs aldrig vid radstart. Burstfönstret är 202..313 sampel efter radstarten (111 sampel
  = 9,93 subbärarcykler — medvetet nära 10 hela cykler så att capture-modellens ±5 sampels
  start-jitter inte spelar roll). Burstvektorn låses mot NCO:n, `est = burst_i*256/mag`, IIR
  (skift 4), `inc = FSC_INC - err*LOOP_GAIN >> 8`. Tecknet är verifierat med fasesvep: `burst_i > 0`
  när NCO:n leder, så inkrementet måste minska (fel tecken = positiv återkoppling, svänger ±60°).
  Multiplikatorerna avrundar (`+64 >> 7`): golvtrunkering gav −20 i burstvektorn över fönstret och
  ~15° låsningsfel. En magnitudgräns (BURST_MIN=60) hoppar över vertikalintervallrader (där finns
  ingen burst; en riktig burst mäter ~210).
- **1H-kam**: `csub = s - prev[p]` (kroma dubbleras, luma tar ut varandra), luma `c7 = s + prev[p]`.
  På 40 MS/s är en rad 2542 sampel = 227,48 cykler, inte 227,5 — kammen inverterar alltså med
  172,83°, och det exakta invers-mappningen för Cb/Cr blir
  `Cb = 128 − (i·ROT_C8 + q·ROT_S8)·K >> 14`, `Cr = 128 − (i·ROT_S8 − q·ROT_C8)·K >> 14`
  med `ROT_C8/S8 = 127·cos/sin(86,42°)` (verifierat till <0,3 koder på alla åtta färgstaplar).
  Samma 172,83° lämnar 2·cos(86,42°) = 12,5 % av subbäraren i kammad luma — ärligt på
  40 MS/s-nätet, finns på bänken också.
- **Kromademod**: `i = (csub·cos+64)>>7`, `q = (csub·sin+64)>>7`, 32-tapps boxcar (körande summor),
  ett Cb/Cr-par per andra lumasampel (27/80-NCO, 13,5 MS/s → 6,75 MHz kroma, 4:2:2).
  `K = 111·16384/(127·0,35·(vitt−blank)·|sin(86,42°)|)` kalibrerar fullskalig kroma till ±111.
- **Syntes** (`synth_colour`): subbärare per sampel (absolut index, kontinuerlig över rader —
  per-x ZOH fryst fas i ~3 sampel och gav fel fas), 9-cyklisk burst på 180° i bakre porchen,
  valfritt gaussiskt brus och per-rad burstfas-ramp.

## Mätt (40 rader, `run_frame`)

| brus σ | ramp °/rad | luma SNR dB | hue RMS ° | kroma RMS | sync |
|---|---|---|---|---|---|
| 0 | 0 | 22,8 | 1,6 | 33 | 1,000 |
| 0 | 2 | 22,9 | 5,5 | 87 | 1,000 |
| 0 | 8 | 23,0 | 18,6 | 115 | 1,000 |
| 1 | 0 | 22,6 | 4,3 | 35 | 1,000 |
| 3 | 0 | 21,3 | 30,9 | 76 | 1,000 |

Ramp och brus försämrar måtten monotont. Kroma-RMS 33 på rent signaler domineras av
kantövergångar mellan staplarna och 12,5 %-läckan i luman, inte av demoduleringen (mitt i en
stapel är felet ~5 koder).

## Negativa kontroller (i testsviten)

- Kam av: luma SNR 22,8 → 12,4 dB, kroma RMS 33 → 45.
- Ingen burst + öppnad magnitudgräns: NCO-fasen vandrar (spridning 77° mot 40° med burst;
  med gränsen stängd låses den aldrig alls, `burst_lines == 0`).
- `pack_words`: {Y1, Cr, Y0, Cb}-layout som `fb_display.v` läser.

## Nästa steg (ej gjort)

RTL:n själv (NCO + kam + boxcar + Cb/Cr i Verilog) med sim mot denna modell ord-för-ord;
sedan jämförelse mot TVP-vägen med `bench quality` och fältdumpen på riktig C5VRX-signal
(där mäts också om C5VRX:s burst verkligen är fasstabil — rampkolumnen ovan är just det).
