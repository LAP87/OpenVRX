# SDR-väg för 5,8 GHz analog video: vad som finns att experimentera med

Ägarens fråga 2026-10-19: finns Analog Devices mottagarkretsar (AD9361/AD9364, ur rådets lista utan RichWave) att få tag på för experiment? Svar: ja, på färdiga kort; inget eget RF-kort behövs för ett första prov. Det här är underlag, inget köpbeslut. Priser är daterade enligt inköpsregeln (beslut 4).

## Vad experimentet skulle visa

Analog VTX → SDR-kort med AD9361 → FM-demodulering och PAL/NTSC-avkodning på datorn → bild på skärmen. Det avgör om mottagningen med en bred, kalibrerad radio är intressant innan någon försöker göra den bärbar. Det ersätter inte bänkjämförelsen av RX5808 (rådets P4): bildvinst avgörs med samma sändare, samma RF-nivå och samma bildkriterium, inte med blad.

Det SDR-kortet lämnar är digitala IQ-sampel, inte CVBS. För att nå OpenVRX:s kedja behövs antingen CVBS tillbaka ut (gräns A i Pucks `design/MOTTAGARGRANS.md`) eller BT.656 direkt in i FPGA:n (gräns B). Inget av det finns; först bilden på datorn.

## Signalen

En analog FPV-kanal är FM-modulerad video med ljudunderbärvågor; en mottagare behöver tiotals MHz bandbredd kring bärvågen. RTL-SDR:s notis om HackRF-mottagning av 5,7 GHz-drönarvideo säger att en bredbandig mottagare ger färg medan en smal (RTL-SDR, ~2 MHz) bara ger gråskala. AD9361/AD9364 har 56 MHz kanalbandbredd och täcker 70 MHz–6 GHz; AD9363 slutar vid 3,8 GHz och 20 MHz och passar inte 5,8 GHz (tillverkarens blad, lästa av rådet 2026-10-19).

FM-demodulering av IQ är en rad kod (`np.angle(x[1:] * np.conj(x[:-1]))`, PySDR kapitel 25, som också visar radfrekvensens övertoner vid 15,734 kHz / 15,625 kHz som kontroll av NTSC/PAL). Synkseparation och bildbygge därefter finns i färdiga program (nedan).

## Plattformar

| Kort | Radio | Täckning | Gränssnitt | För oss |
|---|---|---|---|---|
| MicroPhase AntSDR E200, 9361-varianten | AD9361, två mottagarkanaler | 70 MHz–6 GHz, 56 MHz | Zynq XC7Z020, Gigabit Ethernet, 2 × SMA + 2 × U.FL | Första kandidat: två mottagarkanaler i samma kort (två antenner), FPGA på kortet för en senare egen demodulering. Crowd Supply 2026-10-19: 689 USD utan kåpa, 729 USD med, "In stock", 18 USD frakt utanför USA; svensk moms och tull tillkommer. 9363-varianten (449/489 USD) når inte 5,8 GHz |
| Ettus USRP B210 | AD9361, 2 × 2 | 70 MHz–6 GHz, 56 MHz | USB 3.0 | Samma radio, datorn gör allt; dyrare (pris inte kontrollerat) |
| Ettus USRP B205mini-i | AD9364, en mottagarkanal | 70 MHz–6 GHz, 56 MHz | USB 3.0 | En kanal räcker för "bild på datorn"; ingen diversity. Codex nämnde B206mini-i (samma radio, annan klocka); inte kontrollerat |
| ADALM-PLUTO | AD9363 | 325 MHz–3,8 GHz enligt bladet | USB 2.0 | Passar inte: 5,8 GHz ligger utanför specifikationen; den kända firmwareutökningen är ingen garanti för ingångsnätet vid 5,8 GHz |
| HackRF One | eget, 8 bitar | 1 MHz–6 GHz, 20 MS/s | USB 2.0 | Billigast; 20 MHz bandbredd och 8 bitar räcker för att se bild (RTL-SDR:s notis), inte för att bedöma känslighet. Bra "fungerar kedjan alls"-steg |
| AD-FMCOMMS3/4 | AD9361/AD9364 | som ovan | FMC mot ett FPGA-värdkort | Omständligare start; bara om ett FMC-kort redan finns |
| LimeSDR / LimeSDR Mini | LMS7002M | upp till 3,5–3,8 GHz | USB 3.0 | Passar inte 5,8 GHz |

Specifikationerna ovan är tillverkarnas; inget är mätt av oss.

## Programvara som redan gör videodelen

- PySDR kapitel 25 "Analog FPV Video Signals": Python, FM-demodulering och radtiming, steg för steg.
- SigDigger: användes i RTL-SDR:s notis om 5,7 GHz NTSC-drönarvideo med HackRF (DragonOS).
- TVSharp (plugin till SDR#) för PAL/NTSC, och uAVD (Windows) för FM-FPV-länkar, båda enligt RTL-SDR.
- GNU Radio: FM-demodulering och filter finns som block, men ingen färdig flödesgraf för 5,8 GHz FPV hittades vid en vanlig sökning 2026-10-19.

Ingen av dessa importeras i våra repon (licenser ej granskade; vi behöver dem bara som verktyg på datorn).

## Vad som inte är bestämt

- Om något kort köps, och vilket. Billigaste provet av kedjan är HackRF; det som svarar på frågan om mottagning med en bättre radio är ett AD9361-kort.
- Hur IQ-vägen i så fall skulle nå OpenVRX (gräns A eller B).

Källor: [PySDR kapitel 25](https://pysdr.org/content/fpv_video.html); [RTL-SDR: 5,7 GHz NTSC med HackRF och SigDigger](https://rtl-sdr.com/page/104); [AntSDR E200 på Crowd Supply](https://www.crowdsupply.com/microphase/antsdr-e200) (pris och lager 2026-10-19); [AD9361](https://www.analog.com/en/products/ad9361.html), [AD9364](https://www.analog.com/en/products/ad9364.html); rådets rapport `docs/design/2026-10-19/COUNCIL.md`.
