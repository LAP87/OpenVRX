# Bänken från datorn

Hur utvecklingsslingan körs från en Windows-dator med WSL: flasha, läsa loggen, styra M6, läsa C5VRX-konsolen, fånga bilden och mäta den. En människa eller en agent gör allt härifrån; händer behövs bara vid kabelbyten och strömbrytning. Verktygen ligger i navets `tools/bench.ps1` (Windows) och `tools/bench/` (WSL). Det som är mätt på hårdvara står med datum; resten är skrivet och testat utan kort.

## Från nystartad dator till "M6 kör och loggen rullar"

En gång per dator (ägaren, med administratör där det står):

1. WSL med Ubuntu 24.04 och verktygskedjan som i Core `README.md`: venv med `requirements.txt`, Icarus Verilog 12, `openfpgaloader` (apt, med udev-reglerna). Core-checkouten för byggen i WSL ligger i dag under `/root/openvrx-review/OpenVRX-Core` med venv:en `.venv`; `bench.ps1` anropar den pythonen.
2. `usbipd-win` 5.x på Windows.
3. Tang Nano 20K i USB, sedan som administratör: `usbipd list` (busid för `0403:6010`) och `usbipd bind --busid <id> --force`. `--force` gör att Windows inte längre tar kortet (inga drivrutinsdialoger); kortet är WSL:s tills `usbipd unbind`.

Varje gång, i en PowerShell i navet:

```powershell
tools\bench.ps1 up
```

Startar WSL-vakten om den saknas (`wsl.exe -d Ubuntu -- sleep 36000`, dold; WSL stannar annars när inget kör och tappar korten), kopplar in Tang med `usbipd attach --wsl --hardware-id 0403:6010 --auto-attach` som en dold process som överlever skriptet och kopplar in kortet igen efter en omkoppling, och visar vad WSL ser:

```
tang  0403:6010 bus 001 dev 002  Future Technology Devices International, Ltd FT2232C/D/H Dual UART/FIFO IC
      if00 /dev/ttyUSB0  /dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if00-port0
      if01 /dev/ttyUSB1  /dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if01-port0
Tang log port: /dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if01-port0
```

Sedan:

```powershell
tools\bench.ps1 flash /root/openvrx-wt/n55/gateware/build/m6_puck_proto.fs
tools\bench.ps1 log m6 --seconds 20
tools\bench.ps1 status --json
```

`flash` vägrar en bitström som inte stämmer med sitt manifest. `log` skriver en JSONL-fil under `bench-logs\` (bredvid navet, inte i git) och en sammanfattning. `status` läser tills det har två tolkade rader (M3: en per dekoder), högst 25 s, och skriver den sista tolkad.

## Kommandona

| Kommando | Var | Gör |
|---|---|---|
| `bench.ps1 up` | Windows | vakt, Tang inkopplad med auto-attach, `devices` |
| `bench.ps1 attach [-Xiao]` | Windows | vakt och auto-attach; XIAO:n bara med `-Xiao` |
| `bench.ps1 state` | Windows | vad `usbipd state` ser: bunden, inkopplad, busid |
| `bench.ps1 <övrigt>` | Windows | skickas till `bench.py` i WSL med `wsl.exe -e` (inget skal emellan, så `$` i argument överlever) |
| `bench.py devices [--json] [--detect]` | WSL | korten på VID:PID (`lsusb`), deras tty-noder ur sysfs, Tangs loggport; `--detect` kör `openFPGALoader --detect` |
| `bench.py flash <topp eller fil> [--build-dir D] [--flash] [--root]` | WSL | manifestkontroll, sedan `openFPGALoader -b tangnano20k` (SRAM; `--flash` skriver SPI-flashen); skriver `bench-logs/state.json` |
| `bench.py log m3\|m6 [--seconds N] [--out fil] [--json]` | WSL | raderna med tidsstämpel och tolkning till JSONL, sammanfattning på slutet |
| `bench.py status [--json]` | WSL | sista tolkade raden, självtest, adresser, låsflaggor, vilken bitström som laddades |

**Manifestkontrollen.** Bitströmmens SHA-256 jämförs alltid med `<prefix>.build.json` bredvid den. Ligger alla byggets artefakter bredvid (byggkatalogen) körs också Core `build_manifest.py verify`; en bitström från bitströmsgrenen har bara `.fs` och manifest, och då står det `verified: bitstream`. `--root` jämför dessutom manifestets källhashar med Core-checkouten (`OPENVRX_CORE`). Utan manifest vägras filen (`--no-verify` finns för undantag).

**Loggen.** En rad per objekt: `{"t": ankomsttid UTC, "raw": raden, "rec": tolkningen eller null}`. M6-raderna tolkas med Core `gateware/tools/snowlog.py` (alla radlängder från 43 till 89 byte), M3-proben med `tools/bench/m3probe.py` (`sclk`, `tog`, `hi`, `len`, `ln`, `fld`, `xe`, `i2c`, `st` avkodat till H-, V- och färglås, svag signal och 50 Hz, `ri`). En rad som skadats på vägen ger `null` och räknas som `damaged`. Vilken tolk och vilken baudrate som gäller tas ur `state.json` (det som senast flashades), annars `m3`/`m6` och `--baud`.

**Tidsstämplarna** är datorns ankomsttid. Över usbipd kommer serieloggen i skurar, ibland en halv minut sent (BANK_2026-10-21): de ordnar raderna, de mäter inte kortet. Läs minst 20 s innan något sägs om en logg.

**Sökvägar.** `OPENVRX_CORE` (Core-checkouten för `snowlog.py` och `build_manifest.py`; standard `../OpenVRX-Core` bredvid navet), `OPENVRX_BUILD` (extra katalog att söka `<topp>.fs` i före `<core>/gateware/build`), `OPENVRX_BENCH_LOGS` (standard `../bench-logs`).

**Test utan kort:** `python -m unittest discover -s tools/bench -p 'test_*.py'` i WSL (Core-venv:ens python). M3-tolken har en negativ kontroll: varje förlorad byte och varje ändrad byte i en probrad ger `null`.

## Mätt på hårdvara

| Datum | Vad | Resultat |
|---|---|---|
| 2026-10-23 kväll | `bench.ps1 devices --detect` i Windows PowerShell 5.1 och PowerShell 7 | Tang hittad på `0403:6010`, `if01` = loggporten, FPGA GW2A(R)-18(C) över JTAG |
| 2026-10-23 kväll | `bench.ps1 attach` | auto-attach-processen startad, kortet inkopplat; en omkoppling är inte provad (inga händer vid bänken) |
