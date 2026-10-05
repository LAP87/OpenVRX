# Återskapa granskningens körningar

Allt körs mot en orörd utcheckning av OpenVRX-Core (dec88d6) med dess `.venv` och Icarus Verilog 12.
Skripten ändrar ingen RTL. De lägger tillfälliga testfiler i `gateware/sim/` och tar bort dem igen;
utdata hamnar i `gateware/sim/build/` (ignoreras av git).

```bash
OPENVRX_CORE=/sökväg/till/OpenVRX-Core ./run_all.sh
```

Ett jobb i taget, cirka 45 minuter. Mina rådata finns i `results.txt`.

| Körning | Fil | Fynd | Vad den gör |
|---|---|---|---|
| VBI = 20 | `run_all.sh` (en `sed`-rad på ert `sim/test_mixer.py`) | M-1 | Ert mixertest med 20 släckrader i stället för 2 |
| E1 | `review_mixer.py e1` | M-1 | RTL mot `line_mixer_ref.py` med 24 + 20 rader per fält |
| E2, E3 | `review_mixer.py e2 e3` | M-2 | En mottagare utan signal, standard-`TIMEOUT` |
| E2b, E3b | `review_mixer.py e2b e3b` | M-2 | Samma med `TIMEOUT` 262 144 |
| E3c | `review_mixer.py e3c`, `review_tail_lines.py` | M-3, V-1 | Olåst kanal är aktuell, `TIMEOUT` 262 144 |
| E4, E4d | `review_mixer.py e4 e4d` | M-4 | Olåst kanal 2, 5 och 12 rader efter den friska |
| E5, E5b | `review_mixer.py e5 e5b` | M-5 | F-biten fast på 1 |
| E6 | `test_review_ll.py` | (höll) | Låglatensläget med 12 och 11 rader omväxlande |
| E7, E7b | `test_review_tb3.py slow fast` | V-3 | Trippelbuffertens invariant, publicering kring en bildstart |
| Bank 5 | `review_lvds_bank.py`, `review_tmds_fuses.py` | P-1 | IOB-fuses för TMDS-paren med och utan utgång på stift 25 |

`tb_review_mixer.v` är `sim/tb_mixer.v` med en `EXT_A`-parameter, logg av `cur`/`alive` och valfri
ordlogg. `review_mixer.py` återanvänder `model/bt656.py`, `model/line_mixer_ref.py` och
stimulushjälparna i `sim/test_mixer.py`.

Två saker att känna till:
- `tb_mixer.v` kör kanal B 0,19 % långsammare än A (37,00 mot 37,07 ns). I korta test är det bra.
  Över tusen rader blir det 2,7 raders glidning, vilket två dekodrar låsta till samma kamera inte har.
  E5 och E5b kör därför B på 37,001 ns.
- Fönstren i E2–E4 räknar bara tiden då båda strömmarna går.
