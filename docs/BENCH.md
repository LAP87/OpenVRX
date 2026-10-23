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

## C5VRX-konsolen

`tools/bench/c5.py` (WSL, bara standardbiblioteket) håller XIAO ESP32-C5:ans serieport öppen som en demon, loggar allt och tar kommandon på en Unix-socket. Förutsättning (B7, ägaren): XIAO:n bunden till usbipd en gång som administratör (`usbipd bind --busid <id>`) och strömmen bruten efter fredagens försök. Sedan:

```powershell
tools\bench.ps1 attach -Xiao
```

```bash
python tools/bench/c5.py daemon &          # i WSL; loggar i ../bench-logs/c5vrx/
python tools/bench/c5.py status            # skickar T, skriver tolkad status som JSON
python tools/bench/c5.py channel A2        # b och c tills CONTROL säger A2
python tools/bench/c5.py level 1.5         # g tills OUTPUT säger 1.5x
python tools/bench/c5.py calibrate         # frågar om sändaren är av, skickar F, väntar på startup=0 busy=0
```

| Del | Gör |
|---|---|
| `daemon` | öppnar porten en gång (`/dev/serial/by-id/usb-Espressif*`), rör inte DTR/RTS efter öppningen, återöppnar när enheten kommer tillbaka; `full.log` får allt, `short.log` allt utom `FIELD_TRACE`/`FIELD_DIAG` (`FIELD_DIAG_EVENT` är kvar), båda med ankomsttid |
| `status` | `T` genom demonen; svaret räknas som klart efter 0,8 s utan ny svarsrad (flödesraderna och hjärtslaget räknas inte); JSON med `fw`, `channel`, `freq`, `afc_locked`, `detected`, `cn_db`, `carrier_dbm`, `stage`, `startup`, `busy`, `output_level`, filtret, de senaste `FILTER_CAL`-raderna och senaste `FIELD_DIAG_EVENT` |
| `parse <logg>` | samma tolkning av en sparad logg (webbterminalens `.log`-filer) |
| `send`, `tail` | råa tangenter genom demonen, de senaste korta raderna |
| `reboot --i-know`, `download --i-know` | sätter DTR/RTS med avsikt (demonen stoppad), efter en varning |

Tolken läser varje känd rad strikt (`CONTROL`, `RX_LEVEL`, `HB`, `OUTPUT`, `FIRMWARE`, `FILTER`, `FILTER_CAL`, `FIELD_DIAG_EVENT`): ett fält som saknas eller har fel form ger fel i stället för ett gissat värde. Testat mot de tre sparade loggarna i `tools/bench/fixtures/` med negativ kontroll (sju förvanskade rader, var och en ger fel), och demonen mot en låtsas-C5VRX på en pty (`status`, `channel`, `level`, korta och långa loggen). Inte provat mot kortet.

**DTR/RTS på ESP32-C5:ans USB-serial-JTAG-port.**

| | Vad |
|---|---|
| Observerat (BANK_2026-10-23) | Chromes webbterminal på Windows fungerar varje gång; sidan gör bara `port.open({ baudRate })`, skickar `hT` och sedan `T` med jämna mellanrum |
| Observerat | .NET-klassen `System.IO.Ports` växlar linjerna en i taget vid öppning och stängning; efter en sådan öppning tystnade kretsen tills strömmen bröts |
| Observerat | `tools/c5port.ps1` (Win32, båda linjerna i ett anrop) gav rader en gång, direkt efter att Chrome kopplat ner, men inte vid andra öppningar, oavsett läge på linjerna. USB-enhetens ankomsttid ändrades inte, men porten överlever en kretsreset, så det säger inget |
| Antaget | Porten tolkar linjerna som den klassiska auto-reset-kretsen: RTS ensam håller kretsen i reset, DTR ensam drar boot-strappen, lika linjer gör inget (Espressifs beskrivning av USB-serial-JTAG; för just C5 inte kontrollerat) |
| Antaget | Linux `cdc_acm` sätter DTR och RTS i samma begäran när porten öppnas och släpper båda i samma begäran när den stängs (HUPCL); inte mätt med protokollanalysator |
| Okänt | Vad Chrome på Windows gör med linjerna vid öppning, och varför kretsen svarade Chromes handtag men inte skriptets; troligast stod kretsen redan i nedladdningsläget efter `System.IO.Ports` |

`reboot` och `download` använder sekvenserna ur den antagna tolkningen (reset-puls med strappen släppt; strapp, reset, släpp). De är inte provade och ska bara köras med någon vid bänken som kan dra ur kortet.

## När loggen tystnar

Över usbipd har loggen kommit i skurar (BANK_2026-10-21). Kvällen 2026-10-23 stannade den helt:

1. Första `log m6` efter `flash` gav 93 rader inom en tiondels sekund, alla från tiden före öppningen (8 KB, troligen BL616:s buffert från bitströmmen som kört sedan kvällen), sedan ingenting.
2. Därefter 0 byte i varje läsning, sammanlagt mer än sju minuter: med M6 ur `e71a268` och `cd90e6e`, med M3 ur `cd90e6e`, med porten öppen medan bitströmmen laddades, efter `usbipd detach` (auto-attach kopplade in kortet igen, ny enhetsadress), efter `usbreset 0403:6010` i WSL, efter FTDI-protokollets återställning och tömning av port B (styröverföring via usbfs), med latenstimern 16 ms (BL616 rapporterade 0 på port B, 5 på A) och efter ett byte av baudrate fram och tillbaka. JTAG fungerade hela tiden (`flash`, `--detect`).
3. Slutsats: BL616:s UART-brygga levererar inget från FPGA:ns stift 69 förrän kortet får strömmen bruten. Orsaken är inte känd; att bryggan låser sig när dess buffert fylls utan läsare är en gissning. En sökning efter kända fel i BL616-firmwaren gav inget om just det här kortet.

Gör så här tills orsaken är känd: läs loggen löpande (en `log` i bakgrunden) i stället för att låta den ligga oläst i timmar, och bryt strömmen (dra ur USB) när `log` ger 0 rader på 30 s med en bitström som ska skriva.

## Mätt på hårdvara

| Datum | Vad | Resultat |
|---|---|---|
| 2026-10-23 kväll | `bench.ps1 devices --detect` i Windows PowerShell 5.1 och PowerShell 7 | Tang hittad på `0403:6010`, `if01` = loggporten, FPGA GW2A(R)-18(C) över JTAG |
| 2026-10-23 kväll | `bench.ps1 attach`, sedan `usbipd detach --hardware-id 0403:6010` | auto-attach-processen kopplade in kortet igen inom 6 s (ny enhetsadress, samma by-id-länkar); en fysisk omkoppling är inte provad |
| 2026-10-23 kväll | `bench.ps1 flash .../n55/.../m6_puck_proto.fs --root /root/openvrx-wt/n55` (M6 ur `e71a268`, byggt i natt) | `verified: full+sources`, SRAM laddat; mot Windows-checkouten på en annan gren vägrades samma fil (`current sources do not match`), som det ska |
| 2026-10-23 kväll | `bench.ps1 log m6 --seconds 25` | 93 rader, 92 tolkade, 1 skadad (den första, avklippt): `S 000000 ------ ... F4 5800 MIX T F - L? ... 2`, självtest `2`; alla inom 0,1 s och troligen från bitströmmen före laddningen, se "När loggen tystnar". Löpande logg är inte mätt i natt |
