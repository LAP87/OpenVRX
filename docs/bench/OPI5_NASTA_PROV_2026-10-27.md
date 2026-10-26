# Orange Pi: nästa prov tisdag 27 oktober

Förberett 26 oktober från Claudes sparade bänkloggar och en läsning av den frysta Realtek-källan. **Första målet är en identifierad, komplett råfångst. HDMI-bild kommer senare.** Detta fortsätter [uppgift 70](OPI5_RTL8852BE_2026-10-26.md); inget nytt hårdvaruprov eller drivrutinsbygge är gjort för denna not.

## Utgångsläget

Claudes `bench-logs/2026-10-26-digital-b/NOTES.md` och `opi5-*.txt` på jobblaptopen visar följande:

- Orange Pi startade med Armbian 26.8.1, kernel `6.1.115-vendor-rk35xx`. Den befintliga reservationen för det skadade RAM-området var aktiv. Det är inte ett nytt friskintyg för minnet.
- RTL8852BE, PCI-ID `10ec:b852`, hittades med kärnans `rtw89`. Den separata vendor-drivrutinen byggdes och laddades; LA-/PSD-hjälptexterna gick att läsa.
- PSD-proven gav `PSD_SET_FAIL`. Den observerade kanalen blev kvar på 36 trots kanalönskemålen.
- Vid nästa modulbyte rapporterade `insmod` **Device or resource busy**. Därefter slutade SSH svara. Ingen kraschdump som fastställer orsaken är läst.
- Codex kontroll på kvällen nådde Gaminglaptop, men Pi:ns senaste adress gav timeout under SSH-bannerutbytet. Inga återställningar eller modulbyten gjordes.

Det finns ännu ingen godkänd OPi-råfångst, FM-demodulering eller levande HDMI-video. Den tidigare kamerabilden genom C5/DAC/TVP/Tang är en annan signalväg. Tangens kanaltext bevisar inte vilken frekvens C5 eller Realtek faktiskt tar emot.

## Källfynd som ändrar provordningen

All Realtek-läsning gäller `lwfinger/rtw8852be` **52f1fa3aa5171301c8b009756a1cf7a53a9d91d0**. Egna Makefile-patchar och den faktiskt laddade modulen måste jämföras med detta efter omstart. GPL-källan stannar utanför OpenVRX-repona.

| Fynd | Följd för nästa prov | Källa |
|---|---|---|
| PSD väntar på att debugvärdet uppfyller `(värde & 0x80000f00) == 0`. Loggarnas `0xeaeaeaea` ger `0x80000a00`, alltså inte vila. | Det förklarar varför just detta värde inte passerar villkoret, inte varför värdet uppstår eller varför maskinen hängde. Hoppa inte över kontrollen. | [`halbb_stop_ic_trx`, 492–539](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_api.c#L492-L539) |
| LA:s `halbb_la_main` startar MAC-fångsten utan att anropa PSD:s `halbb_stop_ic_trx`. | En lyckad PSD-mätning är inte ett visat krav för att prova LA. Testa fångstvägen separat när grundsystem och kanal är verifierade. Att LA fungerar är fortfarande oprövat. | [`halbb_la_main`](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_la_mode.c#L722-L811) |
| Bufferhämtningen och utskriften använder båda dumpmarkörer, men det är `halbb_la_buffer_print` som skriver alla 64-bitarsvärden. | `Dump_Start`/`Dump_End` ensamma räcker inte. Efter lyckad hämtning: explicit full utskrift och kontroll av antal poster mot `smp_number`. | [`hämtning`](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_la_mode.c#L98-L164), [`utskrift`](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_la_mode.c#L1335-L1422) |
| I den partiella utskriftsgrenen läses både övre och undre 32 bitar från `idx + 1`. Fullutskriften använder två olika ord. | Använd `bb lamode print 0` och tolka bitar utanför drivrutinen. Undvik `print 1` som facit för I/Q; exempelvis skulle två olika ord kunna presenteras som dubblerat övre ord. Ingen patch behövs för detta första prov. | Samma utskriftsfunktion, särskilt 1399–1403 |
| `cfg80211_rtw_set_monitor_channel` skickar ett kanaljobb men returnerar sedan 0 utan att här pröva dess returvärde. | Ett lyckat `iw`-kommando måste följas av faktisk kanalavläsning och logg. Monitorstöd är en kandidat för kanalstyrning, inte bevis för rå-I/Q. | [`kanalvägen`](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/os_dep/linux/ioctl_cfg80211.c#L6520-L6562) |

Ytterligare källobservation: PSD sätter `psd_in_progress=1` före vilokontrollen, men felreturen vid denna kontroll återställer inte flaggan till 0. Normalavslutet gör det. Det är ett separat granskningsfynd i [`halbb_psd`](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_psd.c#L227-L365), **inte en fastställd förklaring till hänget**. Ändra inte det och modulbytet samtidigt.

## Vad bufferten räcker till

64 KiB ger högst **8 192 poster à 64 bitar**. Tabellen antar en post per vald LA-klocka och full buffer. Antal komplexa I/Q-sampel per post och den verkliga signalens takt är ännu inte fastställda.

| LA-klocka | Tid i 8 192 poster | Nominella NTSC-radperioder |
|---|---:|---:|
| 160 MHz | 51,2 µs | 0,81 |
| 80 MHz | 102,4 µs | 1,61 |
| 40 MHz | 204,8 µs | 3,22 |
| 20 MHz | 409,6 µs | 6,44 |
| 10 MHz | 819,2 µs | 12,89 |
| 5 MHz | 1 638,4 µs | 25,78 |

Beräkning: `tid = poster / klockfrekvens`; nominell NTSC-rad här är 63,5556 µs (525 rader, 30000/1001 hela bilder/s). Klockvalen och formatnamnen kommer från [LA-headern](https://github.com/lwfinger/rtw8852be/blob/52f1fa3aa5171301c8b009756a1cf7a53a9d91d0/phl/hal_g6/phy/bb/halbb_la_mode.h#L107-L140). Bekräfta chip-cut och faktiskt allokerad storlek; anta inte 128 KiB från andra kort.

**Sänk inte bara klockan för att få fler rader.** Det kan ge aliasering eller tappa delar av FM-signalen. Först behöver vi signalpunkt, format och bandbredd. En 40 MHz-fångst skulle villkorligt ge drygt tre radperioder: användbart för en första synkfråga, långt från en hel bild. Vid varje nytt klockval måste samma frekvens användas i analysen.

VTX på F4 är nominellt 5 800 MHz; Wi-Fi-kanal 161 är 5 805 MHz. Om mottagningsfiltret verkligen vore centrerat på 5 805 MHz med 20 MHz total passbandbredd ligger VTX-centret 5 MHz från den nedre kanten. En bred FM-signal kan därför beskäras. Det är en hypotes att kontrollera med faktisk centerfrekvens, filter/tappunkt och signalbredd, inte ett skäl att ändra region eller sända på nya frekvenser.

## Morgondagens ordning

### 1. Återfå ett känt grundläge

Fotografera eventuella fel på TV:n före strömbrytning. Starta sedan om lokalt och anslut via jobblaptopens befintliga WSL-alias `opi5`. Om adress eller värdnyckel ändrats: identifiera kortet igen.

Spara följande till **nya** filer innan något gammalt skrivs över:

```bash
date -Is
uptime
uname -a
lsmod
lspci -nnk
ip -br addr
iw dev
journalctl --list-boots
ls -la /sys/fs/pstore /var/lib/systemd/pstore
journalctl -k -b -1 --no-pager
dmesg --color=never
```

Saknad pstore eller föregående journal betyder saknat bevis, inte att ingen krasch skedde. Kontrollera också att RAM-reservationen finns kvar och om den aktuella starten har minnes-, PCIe- eller lagringsfel. Sådana fel går före RF-arbetet.

### 2. Ett separat modulbyte

Läs först källrevision, patchar, bygglogg, modulhash, `modinfo`/vermagic och aktuellt drivrutinsägarskap för PCI-enheten. Kontrollera att Wi-Fi inte används för SSH; Ethernet ska bära anslutningen.

Strömma kernel-loggen till jobblaptopen före ändringen. Gör högst ett motiverat byte med kontroll mellan varje kommando. **Om borttagning ger fel eller modulen finns kvar: stoppa före `insmod`, monitorläge, kanalval och PSD.** Ingen forcerad avlastning, inget fortsatt skript efter ett misslyckat steg. En timeout hos SSH bevisar inte att kerneljobbet avbrutits.

Ingen ny rebuild behövs enbart för att upprepa dagens bygge: kontrollera först den redan byggda monitorvarianten. Ett lyckat bygge visar inte att den variant som för tillfället körs är den nya.

### 3. Kanal och första LA-fångst

1. Visa faktisk drivrutin, gränssnitt, monitorstöd och kanal. Prova en motiverad kanalinställning och läs tillbaka. Stanna om kanalen fortfarande är fel. Ändra inte radioinställningar parallellt med en pågående fångst.
2. Läs `bb lamode show` och hjälp för den faktiskt laddade modulen. Spara bufferstorlek, alla `cmn`-/DMA-/triggerinställningar och klockans **enumvärde**. Källans visningsformel `80 >> enum` visar inte 160 MHz rätt för enum 7; textfältet ensamt räcker inte som tidsbas.
3. Identifiera vilken `src_sel`/path och vilket DMA-format som ger signalen före paketavkodningen. Om det inte går: märk filen **okänd LA-data**, inte I/Q. `2s_12b` bevisar varken två tidssampel, två oberoende mottagare eller ADC-upplösning.
4. Första fångsten har VTX av och en uttryckligen dokumenterad trigger som inte kräver ett giltigt Wi-Fi-paket. Källans hjälpetikett ”Fake Trig” ändrar `not_stop_trig`; den betyder inte i sig syntetiska I/Q-värden. Fastställ inställningen innan körning.
5. En manuell fångst, antal satt till ett. Spara rapport, faktisk `smp_number`, status/offset/wrap och eventuell dataförlust. Efter lyckad hämtning: `bb lamode print 0` medan kernel-loggen tas emot. Räkna poster; markörer utan data eller tappade loggrader är inte en komplett fångst.
6. Om detta fungerar: samma inställningar, människan slår VTX på, notera klockslag och verifiera den faktiska VTX-kanalen. Ta en separat fångst. Kalibrering eller kanaländring mellan av/på skulle göra jämförelsen tvetydig.

PSD lämnas utanför det första LA-provet. Om LA också fastnar bevaras detta försök; nästa steg väljs från dess logg, inte från ännu en omladdning av samma kedja.

### 4. Frågan som rådata ska besvara

Först efter identifierad packning: signera I och Q rätt, kontrollera mättning/konstanta ord, spektrum och av/på-skillnaden. FM-diskriminatorn kan använda fasen av `z[n] * conj(z[n-1])`; kontrollera både I/Q-ordning och tidsbas. Ta hänsyn till frekvensoffset före tolkning av videon.

En topp nära nominell radsynk är ett indicium, inte ett bildbevis. Sök återkommande synkpulser med rimliga mellanrum och visa att fyndet följer vår VTX. Brus och interna debugmönster får inte godkännas som video. En mycket kort fångst kan lämna frågan öppen även om formatet är rätt.

**Bra utfall för dagen:** stabil Pi, verifierad kanal, två kompletta och identifierade av/på-fångster samt antingen ett motiverat FM/synkfynd eller ett tydligt kvarvarande hinder. Då har provet fört projektet framåt även utan HDMI-bild. Ingen ny kernel, hårdvaruändring eller större ombyggnad görs för att dölja ett oklart resultat.

## Till jobbagenten

> Fortsätt uppgift 70 med denna not. Börja med kraschbevis och faktiskt grundläge efter lokal omstart. Bevara dagens fel, källor och loggar. Kontrollera den redan byggda modulen innan något nytt bygge. Dela modulbyte, kanal, LA-trigger och full datautskrift i separata kontrollerade steg. Ingen fortsättning efter fel, inget tvångsurplock av modul och ingen PSD som förkrav för LA. Målet är två kompletta, formatidentifierade VTX av/på-fångster, inte en utlovad HDMI-bild. Ändra inte C5/Tang eller andra projekt. Rapportera högsta faktiskt visade nivå och spara rådata/inställningar/hashar. Läs uppgift 70:s övriga gränser; kör inte denna not som ett automatiskt kommandoskript.
