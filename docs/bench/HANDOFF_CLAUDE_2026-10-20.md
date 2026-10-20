# Till Claude: börja här efter hemmabänken

**Uppföljning samma kväll:** dina `m2u_uart27` och `m2u_uart64` gav båda 39/39 exakta rader vid 115200 8N1. [Resultat och råloggar](UART_KLOCKPROV_2026-10-20.md). Båda är IOREG=0; det oläsbara M2a-provet var IOREG=1. Det är fortfarande inget SDRAM-pass. `fix/m0-bounce` finns nu på Core `a169638`; ägaren uppger att Claude kör hela sviten före merge. Starta ingen parallell integrationskörning.

Ägaren bad Codex att synka resultaten till GitHub den 20 oktober. **M0 fungerar nu på det fysiska kortet, inklusive fortsatt studs efter omstart från flash. M2a är inte godkänt: UART-loggen är oläsbar.** Core-main är fortfarande `8dff8d1`; den rättade M0-versionen på kortet är en separat bänkversion, inte en mergad Core-ändring.

## 1. För in M0-rättningen i Core — uppgift 46

Originalets 11-bitars x-räknare slår runt vid vänsterkanten: `1 - 3` blir 2046. Efter bildruta 778 växlar den mellan 1 och 2046 medan y fortsätter. Samma rörelseblock finns i `8dff8d1`. Lösningen begränsar positionen till kanten innan riktningen vänds; inga pinnar, klockor eller videoval ändrades.

Underlaget ligger nu i repot:

- [Patchen](2026-10-20/m0-motion/candidate.patch), [originalet](2026-10-20/m0-motion/original_m0.v) och [den rättade bänkkällan](2026-10-20/m0-motion/candidate_m0.v).
- [Den faktiskt använda testbänken](2026-10-20/m0-motion/tb_motion.v), [originalspåret](2026-10-20/m0-motion/original.trace.gz), [kandidatspåret](2026-10-20/m0-motion/candidate.trace.gz) och [den exporterade modellkontrollen](2026-10-20/m0-motion/check_trace.py).
- [Byggmanifestet](2026-10-20/m0-motion/build.json), [utvalda originalkvitton och SHA256](2026-10-20/EVIDENCE.json), samt [bänkrapporten](M0_RORELSEFEL_2026-10-20.md).

Läs befintliga spår utan att köra om simuleringen, från navets rot:

```sh
python3 docs/bench/2026-10-20/m0-motion/check_trace.py original docs/bench/2026-10-20/m0-motion/original.trace.gz
python3 docs/bench/2026-10-20/m0-motion/check_trace.py candidate docs/bench/2026-10-20/m0-motion/candidate.trace.gz
```

Originalkontrollen ska bekräfta det **förväntade felet**, inte frisk rörelse. Kandidaten matchar den oberoende modellen över 5 000 bildrutor och 5 000 hållkontroller, med minst sex besök vid vardera sidokanten. Den ursprungliga läshjälparen missade Icarus extra `$finish`-rad och stannade efter originalkörningen. Originalspåret bevarades och lästes i en separat fortsättning; originalets native-returkod sparades inte separat. Kandidatens kompilering och körning har sparade rc0. Ingen originalkörning gjordes om.

Porta bara rörelseändringen till en ny Core-gren från färsk `origin/main`, lägg in ett varaktigt regressionstest och följ Core-reglerna för commit/sammanslagning. Den exporterade testbänken isolerar rörelsen med stubbar och är exakt den som användes mot `bf05ac0`. **Vid portning till ny main behöver DVI-stubben även porten `rgb_full`**, som tillkommit efter baskällan; stubben verifierar varken HDMI eller PLL. Bygg- och fullsvitskraven för en Core-merge är inte uppfyllda av det privata bänkprovet.

Bitströmmen som finns på kortet är `bf05ac0` plus den medföljande patchen: SHA256 `dea73706130d512345e01d3ddc7b6d41d3e80b34144d3c568b33c26bcfc25fd3`, 842 822 byte. Ägaren bekräftade både fortsatt rörelse efter SRAM-laddning och start med fortsatt studs efter ur- och inkopplad USB-ström. Byggkravet 75 MHz klarades av båda klockorna. Binären ligger kvar privat; ingen ny generell Core-main- eller receiveracceptans följer av detta.

## 2. Red ut M2a-loggen innan SDRAM godkänns — uppgift 47

M2a byggdes en gång ur oförändrad `8dff8d1`, seed 0, IOREG 1, standardfas 10/16, HDMI/VINTERP 0. Bygget och SRAM-laddningen lyckades. Vid 115200 8N1 togs 6 232 byte emot på 20 sekunder, men **ingen komplett giltig M2a-rad**. Åtta andra mottagarinställningar på samma körande design gav inte heller giltiga rader. Ingen ny FPGA-laddning gjordes mellan dessa avläsningar.

- [Alla nio råcapturer, storlekar och hashvärden](2026-10-20/EVIDENCE.json) finns i `2026-10-20/uart/`, inklusive [första 115200-capturen](2026-10-20/uart/baseline.raw).
- [Första läshjälparen](2026-10-20/uart/read_uart_original.py) och de två [baud-](2026-10-20/uart/baud_diagnostic_original.py)/[klockhypotesdiagnoserna](2026-10-20/uart/clock_baud_diagnostic_original.py) är exporterade för inspektion. De är historiska hjälpare, inte en instruktion att köra om avläsningarna.
- [M2a-byggmanifest](2026-10-20/uart/m2a-build.json) och [rapport](MINNE_OCH_FLASH_HEMMA_2026-10-20.md).

Börja med `memtest_core.v`, `uart_tx.v`, `clocks_sdram.v` och den faktiska serieavläsningens inställningar. Skilj vad RTL ska sända från vad USB faktiskt levererar. Källan väljer `rs=4/5/6`; inget belagt `rs=5 err=0` finns. S2-felinjektionen provades inte när loggen inte gick att tolka. Det finns varken ett godkänt eller underkänt fysiskt minnesresultat och ingen fastställd felorsak.

Ingen BL616-firmware, klockgenerator eller drivrutin ändrades. Upprepa inte baudserien eller bygg med andra SDRAM-faser för att få grönt utan en ny konkret hypotes. En oberoende serieadapter eller ett känt UART-mönster kan skilja transport från testlogik, men behöver planeras som ett separat prov. S1/S2 ska inte hållas inne när kortet får ström.

## Kortet och övriga beslut

Tang Nano 20K rev 3923 och HDMI-skärm finns hemma. TVP-modulen och övrig utrustning finns på jobbet; RX5808 har ännu inte mottagits. Kortet startar nu med den rättade M0-bänkbilden. Nästa inkopplingssteg finns i [BANK_2026-10-21.md](../BANK_2026-10-21.md), med UART-/minnesluckan ovan kvar.

M0-resultatet bevisar inte TVP, RF, SDRAM, dubbla videovägar eller den nya menyn. Flygvygrenen `ui/flight-view` är fortfarande ett separat ägarbeslut; ingen menygren mergades eller laddades under bänkprovet. Automationen återupptogs inte. Primära och historiska checkouter bevarades; inga paket installerades.
