# Bänken från datorn

Hur utvecklingsslingan körs från en Windows-dator med WSL: flasha, läsa loggen, styra M6, läsa C5VRX-konsolen, fånga bilden och mäta den. En människa eller en agent gör allt härifrån; händer behövs bara vid kabelbyten och strömbrytning. Verktygen ligger i navets `tools/bench.ps1` (Windows) och `tools/bench/` (WSL). Det som är mätt på hårdvara står med datum; resten är skrivet och testat utan kort.

## Från delarna till första bilden

För den som bygger efter. Allmänna beteckningar; tillverkarnas artikelnummer där det spelar roll.

1. **Delar.** [MATERIAL_UPPSTART.md](MATERIAL_UPPSTART.md): FPGA-kortet Tang Nano 20K i revision 3923 (revisionen står på undersidan; 3921 fungerar inte med stiftplanen), en eller två TVP5150AM1-moduler, en videokälla och kablar. Videokällan är en RX5808-mottagare med SPI-moden gjord, eller en XIAO ESP32-C5 med firmwaren C5VRX och en motstånds-DAC (kopplingen i [BANK_2026-10-22.md](BANK_2026-10-22.md)). Avsnittet "Bänkrigg" där har det som gör bänken styrbar från datorn.
2. **Koppling.** Core `gateware/BRINGUP.md` avsnitt 0 (kortrevision, knapparna vid start, mät modulens IO_DVDD) och avsnitt 1 (stiftplanen på J5 och J6, I2C med egen SDA per dekoder, RESETB).
3. **Datorn.** Avsnittet nedan: WSL, verktygskedjan, usbipd, `tools\bench.ps1 up`.
4. **Bitströmmen.** Bygg själv i Core (`gateware/build.sh <topp>`, manifest med käll- och artefakthashar) eller ta en från bitströmsgrenen (`bench/bitstreams-2026-10-20`, katalog per commit, med manifest). `bench.py flash` vägrar en fil som inte stämmer med sitt manifest. Samma källor och samma verktygsversioner ger samma bitström: M6 byggd 2026-10-23 ur Core `e71a268` är bit för bit lika med bygget ur `cd90e6e` från natten till 2026-10-22 på bitströmsgrenen (SHA-256 `130d2234…1673`, samma källhashar i manifesten). Ett utkast till GitHub Actions som kör sviten och byggena och sparar manifest och bitströmmar ligger på Core-grenen `ci/github-actions-draft` (startas bara för hand; påslaget är ägarens beslut B5).
5. **Ordningen** (BRINGUP 2), med riggen:

| Steg | Bitström | Klart när | Läses med |
|---|---|---|---|
| M0 | `m0_testpattern` | testbilden syns | ögat, eller grabbern: `quality.py calibrate` |
| M2a | `m2a_memtest` | `rs=5 err=00000000` varv efter varv | serieloggen (BRINGUP 2.1) |
| M3 | `m3_probe` | `sclk` cirka 27 000 000, `i2c 5C`/`5D`, `len 1716-1716`, med video `st ..0E` | `bench.py log m3`, `bench.py status` |
| M4 | `m4_dual_mix` | kamerabilden på HDMI, lysdiod 1 | ögat, grabbern |
| M6 | `m6_puck_proto`, på bänken med `DEVCMD=1` | loggraden med självtest `2`, kommandona syns i raden | `bench.py log m6`, `m6ctl.py`, `fielddump.py` |

Första bilden här kom 2026-10-22 med C5VRX-källan i M4 (BANK_2026-10-22.md). Den med två RX5808 och mixern är inte gjord.

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
| `bench.py cmd <tecken>` | WSL | M6 med `DEVCMD=1`: kommandon genom Core `m6ctl.py`, var och en väntar på loggraden som visar den; `cmd '?'` ger statusraden |
| `bench.py dump D\|F` | WSL | fältdumpen genom Core `fielddump.py` till PNG och JSON under `bench-logs` (`D` dekoder A, `F` mixerns utström) |

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

Tolken läser varje känd rad strikt (`CONTROL`, `RX_LEVEL`, `HB`, `OUTPUT`, `FIRMWARE`, `FILTER`, `FILTER_CAL`, `FIELD_DIAG_EVENT`): ett fält som saknas eller har fel form ger fel i stället för ett gissat värde. Testat mot de tre sparade loggarna i `tools/bench/fixtures/` med negativ kontroll (sju förvanskade rader, var och en ger fel), och demonen mot en låtsas-C5VRX på en pty (`status`, `channel`, `level`, korta och långa loggen). Privata byggen säger `version=5.0.0-dev` och `commit=<sha>-dirty`; tolken tar det sedan 2026-10-27.

Mot kortet 2026-10-27: demonen öppnar porten och tar emot kommandon, men socketen kan inte ligga under `/mnt/c` (DrvFs ger "Operation not supported" för AF_UNIX), så den läggs under `/tmp` när loggmappen ligger på Windows-disken. Samma dag tog kortet inte emot ett enda byte via usbipd (esptool "Write timeout" både med och utan reset, demonens `T` utan svar, resetpuls utan verkan), medan Chromes webbterminal fungerade direkt efteråt; orsaken är inte utredd. Webbterminalen (`web/app.js`, `receiver-console.js` i C5VRX-källan) nekar själv tangenterna `U`, `m`, `K`, `k`, `j`, `P`, `O` och `H` ("[Web terminal] Unsupported key"), oavsett firmware, och `b`/`c` först när den sett raden `C5VRX5 version=`.

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

## Bildvägen: grabber och kvalitetsmått

En UVC-grabber på HDMI-utgången (B3) gör bilden till PNG på Windows, `quality.py` räknar i WSL:

```powershell
tools\bench.ps1 cameras                                   # DirectShow-namnen
tools\bench.ps1 capture -Device "<namn>" -Frames 10 -Interval 1
tools\bench.ps1 quality -Device "<namn>" -Frames 30 -Interval 0.5   # fånga, sedan report.json och sheet.png
```

`capture` kallar `ffmpeg.exe` (1280×720 ur DirectShow, en bild per `-Interval` sekund, 0 = bild för bild) och lägger bilderna i `bench-logs\capture-<tid>\`. Jobbdatorn har ffmpeg 9.0.1 via Chocolatey (funnet 2026-10-23); valet av verktyg är ägarens (B2). `cameras` är provat; `capture` är provat fram till att ffmpeg söker enheten, mer går inte utan grabber.

`tools/bench/quality.py measure <bilder eller katalog> [--color-window x,y,w,h] --out report.json --sheet sheet.png` mäter i 4:3-fönstret där M4 och M6 lägger bilden (x 160–1119):

| Mått | Definition |
|---|---|
| `y_mean`, `y_std` | luma, BT.601 studionivå 16–235, ur RGB med fullt omfång (DVI-utgången) |
| `snow` | medel över källrader av summan \|Y[n] − Y[n−1]\| över 720 lumasampel: mixerns HF-energi per rad (Core `model/bt656.py`, som `line_mixer_ref.py` beslutar på; testet jämför med modellen). Fönstret läses tillbaka till 720 sampel, och rader som är lika räknas som en källrad. Samma definition som loggens snövärde, men inte samma tal: grabberns komprimering och färgomvandlingen ligger emellan |
| `black` | `y_mean` < 20 och `y_std` < 3 |
| `repeated_lines` | källrader som visas två gånger i rad (en följd lika rader minst dubbelt så lång som den vanliga): fältminnets ersättningsrad i BUF; 0 med `VINTERP=1` |
| `cb`, `cr`, `hue`, `sat` | medelkroma i färgfönstret; nyans i grader |
| serien | andel svarta bilder, snö (medel, spridning), nyansens spridning (cirkulär) och Cb/Cr-spridning över bilderna som inte är svarta, upprepade rader totalt |

Kontaktarket har bilderna i kvarts storlek, fyra per rad, så att en agent kan se dem. `quality.py calibrate <png>` jämför M0:s åtta färgstaplar (Core `top/m0_testpattern.v`: 0 eller C0h per kanal) med en tolerans (standard 12): det är kalibreringen av vägen genom grabbern. Testat på syntetiska bilder (`tools/bench/test_quality.py`: brusnivåer, färgdrift, svart bild, upprepad rad, M0-staplar, alla fem PNG-filter) med negativa kontroller (mörk bild med textur är inte svart, konstant nyans ger ingen spridning, ren bild har ingen upprepad rad, staplar 20 steg fel fäller kalibreringen, trasig PNG vägras). Ren Python: ungefär en sekund per bild.

## Mätningar (uppgift 60, från 2026-10-26)

Körscheman för veckans mätningar med verktygen ovan. Bitströmmen är M6 med `DEVCMD=1` (kommandon, statusrad, fältdump); `m6ctl.py`, `fielddump.py` och `snowlog.py` ligger i Core `gateware/tools/`. Ändra en sak i taget, och jämför bara körningar med samma kamerabild: snövärdet beror också på bildinnehållet. Varje körning får en etikett och sparas under `bench-logs/` med datum; sammanfattningen och små utdrag committas under `docs/bench/`. Inget av detta är kört.

**(a) TV mot VCR i TVP:n.** Samma kamera, kanal och avstånd. Växla filter med kommandon i stället för menyn, tre gånger åt varje håll, så att drift i källan inte tas för filtrets verkan:

```bash
for f in T V T V T V; do
  python gateware/tools/m6ctl.py $f
  python gateware/tools/snowlog.py /dev/ttyUSB1 --label filt_$f --seconds 60 --out filt.csv
  python gateware/tools/m6ctl.py '?'        # 88h: färglås (bit 3), låsförlust (bit 4)
done
python gateware/tools/snowlog.py --summary filt.csv
```

Med grabbern per läge `tools\bench.ps1 quality -Device "<namn>" -Frames 30 -Interval 0.5`, och `quality.py measure --color-window` över ett färgat föremål. Mått: nyansens spridning (`hue_std`), andelen loggrader med `L` per dekoder, färglåsbiten i statusraden. Avgör blad 12.

**(b) Färgvägen.** Först M0 genom grabbern: `quality.py calibrate` ska ge alla åtta staplar inom toleransen; det kalibrerar grabbern och färgomvandlingen. Sedan en känd CVBS-källa (testbildsgivaren i `MATERIAL_UPPSTART.md`, "Bänkrigg") genom TVP:n till M6 och HDMI: `fielddump.py D` ger dekoderns Cb och Cr per sampel; i en blå stapel ska Cb vara högt och Cr lågt, i en röd tvärtom. Samma stapel i `fielddump.py F` (efter mixern) och i grabberbilden ska ha samma ordning. Byter Cb och Cr plats någonstans syns det som fel nyans i just den bilden.

**(c) Avbrott.** Källan tappar: sändaren av i 5 s med kameran stilla, en gång i LOW och en gång i BUF (`m6ctl.py L`, `m6ctl.py B`). Logga under tiden (`bench.py log m6 --seconds 40`) och fånga bild för bild (`-Interval 0`). Tider ur loggen räknas i rader (cirka 15 per sekund med video, en per sekund utan), inte ur ankomsttiderna, som kommer i skurar över usbipd. Väntat enligt simuleringen: LOW svart medan genlocken saknas, BUF fryser sista fältet; mät hur länge det tar tillbaka. Frågan till ägaren (B6), om LOW ska hålla sista fältet i stället för svart, avgörs med bilderna från den här körningen.

**(d) Mixertrösklarna** (blanda när \|d\|·256 < 38·max, byt när > 64·max; AGENTS.md) mot uppmätt snö, när två mottagare finns: båda RX5808 på samma kanal, den ena antennen nära, den andra längre bort eller avskärmd i steg. Per steg 60 s logg (`snow_a`, `snow_b`, `use_a`, `use_b`, `use_mix`); kvoten \|snö A − snö B\| / max mot andelen blandade beslut, och grabberns snövärde för samma steg, visar om 38 och 64 ligger där bilden faktiskt blir bättre. `m6ctl.py a` och `b` ger varje mottagare för sig som referens.

**(e) Parningsfönstret 15,8 µs mot C5VRX:s fördröjning.** C5VRX bygger om radtakten med sitt synkhjul, så en RX5808 och en XIAO som tar emot samma sändare kan lämna samma radnummer mer än en rad isär; då parar mixern aldrig deras rader. Kroken finns inte än: fältdumpen har inga tidsstämplar, och loggen räknar inte parade rader. Förslag till designunderlag: mixern räknar per mätfönster rader som parades, rader som kom utan partner inom fönstret och avståndet i klockor mellan A:s och B:s rad med samma nummer (medel och största), och skriver det i statusraden. Med det mäts (e) direkt: RX5808 på dekoder A, XIAO på dekoder B, samma sändare. Ingen RTL-ändring är gjord för det i natt.

## När loggen tystnar

Över usbipd har loggen kommit i skurar (BANK_2026-10-21). Kvällen 2026-10-23 stannade den helt:

1. Första `log m6` efter `flash` gav 93 rader inom en tiondels sekund, alla från tiden före öppningen (8 KB, troligen BL616:s buffert från bitströmmen som kört sedan kvällen), sedan ingenting.
2. Därefter 0 byte i varje läsning, sammanlagt mer än sju minuter: med M6 ur `e71a268` och `cd90e6e`, med M3 ur `cd90e6e`, med porten öppen medan bitströmmen laddades, efter `usbipd detach` (auto-attach kopplade in kortet igen, ny enhetsadress), efter `usbreset 0403:6010` i WSL, efter FTDI-protokollets återställning och tömning av port B (styröverföring via usbfs), med latenstimern 16 ms (BL616 rapporterade 0 på port B, 5 på A) och efter ett byte av baudrate fram och tillbaka. JTAG fungerade hela tiden (`flash`, `--detect`).
3. Slutsats: BL616:s UART-brygga levererar inget från FPGA:ns stift 69 förrän kortet får strömmen bruten. Orsaken är inte känd; att bryggan låser sig när dess buffert fylls utan läsare är en gissning. En sökning efter kända fel i BL616-firmwaren gav inget om just det här kortet.

Gör så här tills orsaken är känd: läs loggen löpande (en `log` i bakgrunden) i stället för att låta den ligga oläst i timmar, och bryt strömmen (dra ur USB) när `log` ger 0 rader på 30 s med en bitström som ska skriva.

2026-10-27: bryggan tystnade tre gånger. Efter 7,7 kB i 921 600 baud (M7-probens dump); efter ett enda USB-paket när proben hade sänt en sekund innan läsaren öppnades; och mitt i en dump med läsaren öppen, efter att 7,8 kB legat oläst i bryggan från den förra laddningen. Det gemensamma är oläst data i bryggan. Regel: öppna läsaren före laddningen, lämna aldrig en pratande bitström utan läsare, ladda en tyst bitström efter mätningen, håll 115 200 baud. En strömbrytning av Tang ensam hjälpte inte: med XIAO:n kopplad till J5 matas kortet svagt genom I/O-cellernas skyddsdioder från klock- och datatrådarna (alla lysdioder släckta först när båda korten är ur), så BL616 startar inte om förrän båda korten är strömlösa samtidigt. `wsl --shutdown` och ny attach ändrade inget.

## Orange Pi-proben (uppgift 70)

En Orange Pi 5 med ett RTL8852BE-kort i monitorläge ger 64 KiB råa I/Q-sampel per fångst ur drivrutinens logikanalysator, 410 µs vid 20 MHz sampling. Skripten i `tools/opi5/` tar fångsterna över SSH och tolkar dem på datorn: spektrum, bärare, FM-demodulering med radsynk och burst, kanal och deviation för en sändare på några sekunder. Det är en mätprobe, inte en mottagare: som tätast 0,4 s mellan fångster. Krav på Pi:n, arbetsgång och gränser står i [tools/opi5/README.md](../tools/opi5/README.md); mätningarna i [bench/OPI5_RTL8852BE_RESULTAT_2026-10-27.md](bench/OPI5_RTL8852BE_RESULTAT_2026-10-27.md).

## Den digitala bussen: M7-proben (uppgift 68/69)

När kanal B tar C5VRX:s sampelbuss (`DIGIN=1`) finns ingen TVP-status att läsa, och M4 har ingen UART. Core `top/m7_digin_probe.v` (`gateware/build.sh m7_digin_probe`, bygget tar sekunder) fångar 65 536 sampel (1,6 ms, 26 NTSC-rader) på bussklockan från J5, från första breda pulsen (vertikalintervallet och raderna efter hamnar i dumpen), och skickar dem som hex över USB-UART:en i 115 200 baud, en fångst per 12 s, med en rad `CAP …` emellan från en levande `cvbs_capture` på bussen (med en ingångsvippa före, som `mixer2`): fönstrets längd, lås nu, låsväxlingar, radmarkörer, dåliga, kortaste och längsta rad, ord, och `x=` rader med längd utanför mixerns 1 716 ± 2. Huvudraden `DIGIN <n> CLK <t>` ger bussklockan (`t` × 65 536 Hz).

**Läsaren först.** Bryggan låser sig när data ligger oläst i den (tre gånger 2026-10-27, se "När loggen tystnar"), och proben börjar skicka en sekund efter laddningen. Öppna läsaren, ladda sedan, och ladda en tyst bitström (M4) direkt efter mätningen:

```bash
python tools/bench/uart_raw.py /dev/ttyUSB1 60 ../bench-logs/<dag>/digin-probe.txt &   # rått, öppnas först
sleep 1; python tools/bench/bench.py flash m7_digin_probe --build-dir <Core>/gateware/build
wait; python tools/bench/bench.py flash m4_dual_mix_digin --build-dir <Core>/gateware/build   # tyst igen
python tools/bench/digin_decode.py ../bench-logs/<dag>/digin-probe.txt                   # nivåer, pulser, bild
python tools/bench/digin_model.py <Core> ../bench-logs/<dag>/digin-probe.txt [synk släckning]   # samplen genom modellen
```

Mätt 2026-10-27 (bänkloggen `2026-10-26-digital-b/digin-probe-1027-*`): bussklockan 40,0 MHz, rader om 2 530–2 544 sampel, synkpuls 182 sampel, och C5VRX:s nivåer synktopp 22–24, släckning 30–32, video 40–56, vitt 62 med `OUTPUT 1.0x`; synktoppen brusar ±8 koder, samplen kommer parvis. Det var därför `6b845e8` inte gav rader: skiljaren startade på 12 och väntade synk vid 4. Sedan grenen `digin/levels` sveper `cvbs_capture` skiljaren tills en rad hittas. M3-proben (`m3_probe.fs`) duger för kabelkontrollen: B:s `sclk` visar räknarens tak (över 33,5 MHz) och `tog 3F` säger att alla sex bitar växlar.

## Mätt på hårdvara

| Datum | Vad | Resultat |
|---|---|---|
| 2026-10-23 kväll | `bench.ps1 devices --detect` i Windows PowerShell 5.1 och PowerShell 7 | Tang hittad på `0403:6010`, `if01` = loggporten, FPGA GW2A(R)-18(C) över JTAG |
| 2026-10-23 kväll | `bench.ps1 attach`, sedan `usbipd detach --hardware-id 0403:6010` | auto-attach-processen kopplade in kortet igen inom 6 s (ny enhetsadress, samma by-id-länkar); en fysisk omkoppling är inte provad |
| 2026-10-23 kväll | `bench.ps1 flash .../n55/.../m6_puck_proto.fs --root /root/openvrx-wt/n55` (M6 ur `e71a268`, byggt i natt) | `verified: full+sources`, SRAM laddat; mot Windows-checkouten på en annan gren vägrades samma fil (`current sources do not match`), som det ska |
| 2026-10-23 kväll | `bench.ps1 log m6 --seconds 25` | 93 rader, 92 tolkade, 1 skadad (den första, avklippt): `S 000000 ------ ... F4 5800 MIX T F - L? ... 2`, självtest `2`; alla inom 0,1 s och troligen från bitströmmen före laddningen, se "När loggen tystnar". Löpande logg är inte mätt i natt |
