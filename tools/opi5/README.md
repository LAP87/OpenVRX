# Orange Pi 5 + RTL8852BE som mätprobe för 5,8 GHz

Verktygen från uppgift 70 ([resultatet](../../docs/bench/OPI5_RTL8852BE_RESULTAT_2026-10-27.md)). Ett Wi-Fi-kort i monitorläge ger 64 KiB råa I/Q-sampel per fångst ur drivrutinens logikanalysator (LA); skripten tar fångsterna över SSH och tolkar dem på datorn: spektrum, bärare, FM-demodulering och radtakt. Det är en **probe**, inte en mottagare: 410 µs per fångst, som tätast var 0,4 s (fas D). Mätt på hårdvara 2026-10-27; proven som verifierade varje steg står i resultatdokumentet och i bänkloggen den dagen.

## Vad som krävs på Pi:n

- Orange Pi 5 med Armbian (kärna 6.1.115-vendor-rk35xx provad), kärnheaders, `make`, `git`, `flex`, `bison`, `libssl-dev`, `python3`, `iw`. SSH med nyckel som `root`; aliaset `opi5` i `~/.ssh/config` (hostnamnet ändras när DHCP-adressen byts: `find.sh`).
- RTL8852BE på PCIe (M.2 A/E→M-adapter), antenn på väg B. Kärnans `rtw89` laddas vid start och lastas ur av `swap.sh unload`.
- Vendordrivrutinen `lwfinger/rtw8852be` vid `52f1fa3aa5171301c8b009756a1cf7a53a9d91d0`, klonad till `/root/openvrx-rtl8852be/src/rtw8852be` (GPL, utanför våra repon), byggd med tre ändringar i dess `Makefile`: `CONFIG_PROC_DEBUG = y`, `EXTRA_CFLAGS += -DDBG_LA_MODE`, `CONFIG_WIFI_MONITOR = y`. Laddas med `insmod 8852be.ko rtw_la_mode_en=1`.
- **Modulen lastas aldrig ur.** `rmmod` hängde kärnan 2026-10-26 (RCU-stall, strömbrytning). Byte av bygge görs med `swap.sh reboot` och en laddning per start. Om Pi:n hänger och ett tangentbord sitter i: Alt+SysRq+B bevarar kraschloggen i ramoops; en strömbrytning raderar den.

## Arbetsgång

```bash
export OPI5_HOST=opi5 OPI5_LOGD=/path/to/bench-logs/opi5      # var fångsterna hamnar på datorn
tools/opi5/find.sh 192.168.1          # efter omstart: vilken adress svarar "orangepi5"
tools/opi5/swap.sh prep               # läge, och dmesg -w till fil på Pi:n (krävs för fångsterna)
tools/opi5/swap.sh unload             # rtw89 ur
tools/opi5/swap.sh load               # vendormodulen in, en gång per start
tools/opi5/swap.sh monitor            # monitorläge, upp, 5 805 MHz, läs tillbaka kanalen
tools/opi5/cal.sh 2 5805              # en fångst på kanal 161 med 20 MHz sampling, hämtad till OPI5_LOGD
python3 tools/opi5/la_fm.py OPI5_LOGD/la-ch5805-<tid>.txt OPI5_LOGD/la-ch5805-<tid> 20e6 auto auto 5805
```

`la_fm.py` skriver `<prefix>_fm.png`: spektrum med bäraren markerad, demodulerad momentanfrekvens över hela fångsten och de första 70 µs (en NTSC-rad är 63,6 µs). Sista argumentet är kanalmitten i MHz; då dras mottagarens kända smala toppar bort innan demoduleringen (listan `KNOWN_TONES_MHZ` i skriptet, uppmätt på ägarens kort). `la_lines.py` mäter synkbredd, radavstånd och burstfrekvens i sampel, oberoende av antagen samplingsklocka. `la_decode.py` visar ordstrukturen och skriver tid- och spektrumbilder. `la_join.py` kontrollerar att ringbuffertens skarv är hel.

Fler kommandon: `la.sh chan 5745 80 5775` (40- och 80 MHz-block; deras nollpunkt är inte utredd, använd 20 MHz-kanaler för frekvenser), `la.sh sweep` (effekt per block 5 490 till 5 835 MHz), `cadence.sh 20 2 cca 404` (kadensmätning med MAC-trigg på CCA), `la.sh dbg 2002` (en fångst med en annan debugport).

## Fångsten

- Kommandon till `/proc/net/rtl8852be/<iface>/odm/phl_cmd`: `bb lamode reset`, `buf 0` (64 KiB = 8 192 ord, det enda på 8852B cut B eller senare), `cmn <trigtid µs> 0 <dbgport hex> 0 <klockindex>`, sedan antingen `tmac 1 0` (MAC-timeout 1 s, ingen trigg) eller `tmac 0 0` plus `mac 0 1 0 0` (trigg på CCA; trigtiden 404 µs fyller bufferten efter triggen), `trig`, vid timeout `get <finish_ofst> <round_up>` från pollraden med `rpt=((0x3))`, och `print 0` som skriver 8 192 rader `[BB]<16 hex>` till dmesg. `set 1 1` är inte fejktrigg utan "not stop trig".
- Ordet: bit 47 till 0 är fyra 12-bitars signerade fält, (f0, f1) = I/Q väg A och (f2, f3) = I/Q väg B; bit 63 till 48 är debugportens bitar 31 till 16 (noll med 0x10205).
- Klockindex: 0 = 80 MHz (102 µs per fångst), 2 = 20 MHz (410 µs, 6,4 NTSC-rader). Lägre index decimerar utan filter, så signalen ska ligga inom kanalen (±10 MHz från LO på en 20 MHz-kanal). Index 1 gav motsägande tider och används inte.
- Radion ger 5 500 till 5 825 MHz i 20 MHz-steg (kanal 100 till 165); 5 725 avvisas tyst. Läs alltid tillbaka `cur_ch` i `rf_info`.
- Mottagarens egna toppar utan sändare: 5 796,1, 5 800, 5 801,5, 5 805 (DC), 5 811,2 och 5 830,5/5 831,5 MHz.
- Kadens (fas D): timeout-metoden 1,4 till 1,5 s mellan fångster; CCA-triggen 0,40 till 0,62 s över 20 fångster i följd, golv cirka 0,2 s i drivrutinen. Inga luckor under 0,4 s går att få med den här vägen.

## `sd/`

Två Windows-skript från förberedelsen: `sd_image.py` läser ett SD-kort rått och skrivskyddat från `\\.\PhysicalDriveN` in i en gles avbild i WSL (med 4 KiB-återförsök och nollor för dåliga sektorer, loggade), `sd_patch.py` skriver tillbaka bara utpekade 4 MiB-block efter att ha kontrollerat att kortet fortfarande har originalinnehållet, och läser tillbaka. Båda kördes upphöjt med `py -3` 2026-10-26 (kopia 0 läsfel, 7 block skrivna och verifierade) när `wsl --mount` inte tog den flyttbara läsaren.
