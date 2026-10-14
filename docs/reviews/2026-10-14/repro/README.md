# Återskapa granskningens körningar

Allt körs mot en orörd utcheckning av OpenVRX-Core med dess `.venv` och Icarus Verilog 12. `results.txt` är från Core 072dbde. Skripten ändrar ingen RTL; testbänkar och loggar hamnar i `gateware/sim/build/review2_*` (ignoreras av git).

```bash
OPENVRX_CORE=/sökväg/till/OpenVRX-Core ./run_all.sh | tee results.txt
```

Cirka två minuter. Efter rättningarna (RS-1 och FL-1 sammanslagna i Core) säger de två första skripten att fyndet inte återskapas; det är meningen.

| Fil | Fynd | Vad den gör |
|---|---|---|
| `review2_mixer_weak.py` | RS-1 | Mixern (RTL och modell) med A olåst och ur takt, B svag: E1. Utan varningen: E1c. I takt: E1p. Återanvänder strömmarna och `check()` ur Core:s `sim/test_mixer.py` |
| `review2_rssi_margin.py` | RS-2 | `model/rssi_ref.py` med A fast och B med brus kring tröskeln, 20 000 avläsningar per rad |
| `review2_flash_interrupted.py` | FL-1 | Avbruten radering och programmering mot `model/flash_store_ref.py` (numpy för räkningen, varje fel bekräftat med `scan()`), sedan RTL:en på den första felande avbilden via `sim/test_flash_store.py` |
| `review2_scan_ties.py` | SC-1 | `model/chan_scan_ref.py` med två rena kanaler, en brusig och en ren, och bara en brusig |
| `review2_hdmi_independent.py` | HD-1 | `sim/tb_hdmi.v` i HDMI (`RGB_FULL` 1 och 0) och DVI, avkodad av en avkodare skriven för granskningen |
| `review2_vinterp_full.py` | VI-1 | `fb_display.v` med `VINTERP = 1` och `genlock_timing.v` i full 720-radsgeometri; källrader och vikt för varje utrad mot avbildningen |

Två saker att känna till:
- Modellen för en avbruten radering (varje nollbit satt med sannolikheten p, oberoende) är ett antagande. XTX beskriver inte vad ett avbrott lämnar, och databladet gick inte att läsa.
- RS-2, SC-1 och FL-1:s räkning körs på modellerna. Core:s egna test håller dem lika med RTL (`sim/test_rssi_adc.py`, `sim/test_chan_scan.py`, `sim/test_flash_store.py`); RS-1, FL-1:s första avbild, HD-1 och VI-1 körs på RTL:en.
