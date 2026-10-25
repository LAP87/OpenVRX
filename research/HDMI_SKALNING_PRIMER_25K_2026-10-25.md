# Extern HDMI-skalare eller Tang Primer 25K?

Granskning 2026-10-25. Inga nya kort eller skalare är köpta eller provade. **En extern skalare behöver inte lägga till en hel bildruta. Primer-modulen ger å andra sidan inte automatiskt en snabb 1080p-mottagare.** Skalalgoritmen, buffringsregeln och skärmens egen behandling bestämmer resultatet.

Måndagens C5-prov görs på befintlig Nano 20K och vanlig HDMI-skärm. Se [körschemat och kopplingen](../docs/bench/MANDAG_2026-10-26.md).

## 1. Fyra saker som ofta blandas ihop

| Del | Gör | Behöver bildminne? |
|---|---|---|
| Kontakt-/DVI-modul | Ansluter FPGA:ns TMDS-signaler till kabeln | Inte ett extra bildminne för skalning. Ingen sådan skalare anges för Sipeeds PMOD_DVI. |
| HDMI-sändare, exempel ADV7513 / LT8618 | Kodar och serialiserar redan färdig video till TMDS | Är inte i sig en 720p→1080p-skalare. FPGA:n måste leverera rätt bild och timing. |
| Skalare | Beräknar nya pixelpositioner, exempelvis 1280×720→1920×1080 | Kan arbeta med några rader om in-/utmatning följer varandra, eller använda hela bilder. |
| Bildtaktsomvandlare / frame synchronizer | Gör fri 60 Hz ut från annan eller varierande ingångstakt | Kräver buffring och ibland upprepade/tappade bilder; latensen beror på läge och implementation. |

720p60→1080p60 är skala 1,5 i båda riktningar, inte en ren heltalsdubbling. Linjeföljande skalning är möjlig, men en produkt som kallas linjedubblare är inte därför lämplig för just detta formatpar.

## 2. Vad latenssiffrorna faktiskt säger

Vid 60 Hz är en bildperiod 16,67 ms. Vid 59,94 Hz är den 16,68 ms. Detta är omräkning, inte en mätning av vår kedja.

| Väg / läge | Underbyggd uppgift | Vad den inte bevisar |
|---|---|---|
| Nano direkt till en skärm som tar 720p | Ingen extern skalarbox i kedjan | Skärmen kan själv skala och buffra. Vår mottagares totallatens är fortfarande separat. |
| Extern strömmande skalare, exempel Marseille mClassic | Tillverkarens egen kampanj uppger cirka **0,2 ms genomsnittlig bearbetningslatens** | Inte en oberoende mätning av vår firmware, LOW, färgomfång eller XR-kedja. Produkten väljer även format efter mottagaren; 1080p60 måste verifieras. |
| OSSC Pro, scaler med frame lock | Projektets manual anger cirka **1 bildruta**, alltså ungefär **16,7 ms vid 60 Hz** | Inte ett generellt värde för alla skalare eller alla lägen. |
| OSSC Pro, scaler utan frame lock | Manualen anger **1–2 bildrutor**, alltså ungefär **16,7–33,3 ms vid 60 Hz** | Inte en mätning av en billig HDMI-box. |
| OSSC Pro, line multiplier | Manualen anger max 2 rader i Pure LM och max 60 i Adaptive LM | Man måste först kontrollera stöd för exakt 720p→1080p och vald timing. Siffrorna får inte flyttas till scaler-läget. |
| Ospecificerad HDMI 720p→1080p-box | **Okänt** tills modell, manual och mätning finns | Namnet ”upscaler”, ”4K” eller ”zero lag” räcker inte för ett latensvärde. |
| Primer 25K + PMOD_DVI + egen 1080p-pipeline | Kontaktmodulen tillför inget extra bildbuffringssteg för skalning | Ingen färdig OpenVRX-port eller uppmätt totallatens finns. BUF, deinterlace och skalning kan fortfarande lägga till väntan. |

Källor: [Marseilles egen mClassic-kampanj](https://www.indiegogo.com/en/projects/marseilleinc/mclassic-the-first-plug-play-graphics-processor), [OSSC Pro-projektets manual, lägestabell](https://junkerhq.net/xrgb/index.php?title=OSSC_Pro#Basic_setup_.26_usage), [Sipeed PMOD_DVI](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD#pmod_dvi). Uppgifterna lästes 25 oktober; inga tillverkarvärden märks som vår mätning.

**Praktisk slutsats:** mot en skalare som faktiskt behöver en bildruta kan en strömmande Primer-lösning spara ett sådant steg, runt 16,7 ms vid 60 Hz. Mot en väl fungerande strömmande skalare kan vinsten i själva skalsteget ligga under en millisekund. Skillnaden går inte att fastställa från FPGA-kortets namn eller från en Amazon-bild.

Den tidigare noten [UTGANG_1080P_2026-10.md](UTGANG_1080P_2026-10.md) antog nästan säkert en extra helbildsbuffert i en extern skalare. Det är en möjlig arkitektur, **inte ett generellt krav**. Det är inte heller bevisat att extern skalning alltid tar bort hela nyttan med LOW. En strömmande enhet kan behålla mycket av vinsten om den accepterar ingångstimingen.

## 3. Vad Primer 25K-paketet behöver innehålla

Din iakttagelse stämmer med Sipeeds dokumentation: kortfamiljen består av en **SoM och en Dock**. Dock har tre PMOD och en 40-polig expansionskontakt, men ingen fast HDMI-kontakt. Displayen ansluts med **PMOD_DVI**. Videoformatet skapas av FPGA-koden; ”DVI” i modulnamnet begränsar inte i sig bilden till 720p eller ger en egen skalningsfunktion.

För ett fullständigt OpenVRX-försök behövs:

1. **Tang Primer 25K SoM** med GW5A-LV25MG121.
2. **Primer 25K Dock**, med programmerare och rätt kontaktuttag.
3. **Sipeed PMOD_DVI**, för ett PMOD-uttag med rätt differentialpar och rätt constraints.
4. **Tang-kompatibel 40P SDRAM-modul** om vi ska behålla BUF/fältlagringen. Sipeed dokumenterar 32 MB ×2, 16-bit, 143 MHz. Minnet är ett tillval. En godtycklig MiSTer-modul är inte samma stiftplan.
5. HDMI-kabel och USB-datakabel; exakt paket måste ange om modul 3–4 ingår.

Detta är en funktionslista, inte ett beställningsbeslut eller en verifiering av ett visst Amazon-paket. Tillverkarens [kortöversikt](https://en.wiki.sipeed.com/hardware/en/tang/tang-primer-25k/primer-25k.html) och [minnesmodulbeskrivning](https://wiki.sipeed.com/hardware/en/tang/tang-PMOD/FPGA_PMOD#tang_sdram) är underlag. Länk till den exakta annonsen behövs för att avgöra vad säljaren faktiskt levererar.

### Resurser och minne

Primer har enligt Sipeed **23 040 LUT4 och 1 008 kbit BSRAM**, inte bokstavligen 25 000 LUT. Jämfört med Nanos 20 736 LUT4 är logikökningen cirka **11 %**. Det är ingen storleksordnings större FPGA för två fulla IQ-demodulatorer.

Ett enda NTSC-fält 720×240 i 16-bit YCbCr 4:2:2 kräver 345 600 byte. Primers BSRAM är cirka 126 KiB före övriga buffertar och räcker inte ens till det fältet. Fyra sådana fält kräver cirka 1,32 MiB; PAL 720×288 ger cirka 1,58 MiB för fyra. Därför behövs externt minne för dagens BUF-kontrakt. **DDR3 är inte obligatoriskt**: Sipeeds tillval är SDR-SDRAM, med en annan styrning och bredd än Nanos kapselminne.

### 1080p: rimligt mål, ännu inte vårt hårdvaruresultat

Gowins [DS1103, tabell 3-31 för 25K](https://cdn.gowinsemi.com.cn/DS1103E.pdf) anger OSER10 upp till 2 000 Mbit/s. 1080p60 kräver 148,5 MHz pixelklocka och 1 485 Mbit/s per TMDS-datapar, med 742,5 MHz DDR-serialiserarklocka. Kretsens specificerade tak passar därför uppgiften. Det bevisar inte timing closure, PMOD-signalintegritet eller XR-kompatibilitet på vårt kort och med vår verktygskedja.

Sipeeds [HDMI-exempel](https://github.com/sipeed/TangPrimer-25K-example/tree/main/hdmi/svo) visar hur PLL, TMDS och PMOD ansluts. En modes-tabell med 1920×1080 i källan är inte ett hårdvarukvitto för fungerande OpenVRX i 1080p60. Exempelkod granskas för licens innan eventuell återanvändning; inget är kopierat hit.

### Stiftbudgeten kan bli viktigare än LUT-antalet

Tre vanliga PMOD ger sammanlagt 24 signalstift; DVI använder åtta för fyra differentialpar. Då återstår 16 PMOD-signaler. Två C5 med sex bitar plus klocka behöver 14. Det är en första grov budget, inte en färdig pinplan: två lämpliga klockingångar, kontrollsignaler, UART/UI och eventuella delade funktioner måste också få plats. 40P-kontakten är samtidigt upptagen av minnesmodulen.

Två råa 14-bitars IQ-bussar med var sin klocka behöver 30 signaler. Det ryms inte i de 16 återstående PMOD-signalerna. Ett sådant spår kan behöva annan carrier, seriell transport eller annan databredd. **Köp inte Primer-kit under antagandet att ”alla fler framtidsbussar ryms”.**

## 4. Två parallella utvecklingsval, efter digitalprovet

| Val | Fördel | Arbete / beslut före köp |
|---|---|---|
| Behåll Nano, använd en verifierad extern HDMI-skalare när 1080p krävs | Befintlig mottagarpipeline och SDRAM kan behållas | Exakt HDMI-in-modell, formatpar, uppmätt extra latens, 50/60 Hz, LOW-kompatibilitet och matning. En AV→HDMI-box är fel produktklass. |
| Port till Primer för direkt 1080p | Ingen extern scalerbox behövs; utgångsbuffer och skalning kan styras i samma FPGA | M0 i riktig 1080p60 först, sedan SDRAM-port, 148,5 MHz-pipeline eller två pixlar/klocka, radbuffertmarginaler, mottagarbuss och nya constraints. |
| Nano + parallell HDMI-sändare | Behåller FPGA-familjen men flyttar serialisering till separat krets | Kräver fortfarande att FPGA:n skapar 1080p-video; fler stift och snabb parallellbuss. **Ingen fristående uppskalning köps med sändarkretsen.** |

Min rekommendation: genomför måndagsprovet på Nano. För ett portabelt slutbygge med egen 1080p-utgång är Primer intressant, men köp ett komplett och kontrollerat kit som utvecklingsplattform. För ett snabbt XR-prov kan en skalare med belagd låg latens innebära mindre arbete. Vi har ännu inget mätunderlag som motiverar att byta FPGA bara för att spara en antagen bildruta.

## 5. Så mäter vi den tillkommande fördröjningen

Definiera kedjorna före mätning:

```text
A: kamera → RF → samma C5 → samma Nano/BUF → skärm
B: kamera → RF → samma C5 → samma Nano/BUF → skalare → samma skärm
C: kamera → RF → samma C5 → Primer/motsvarande läge → samma skärm
```

För A/B ska allt före HDMI vara oförändrat. För C måste deinterlace, bildtakt, crop och BUF/LOW-kontrakt beskrivas; annars mäts ett annat bildsystem.

- Filma en slumpmässigt blinkande LED och dess bild på skärmen samtidigt. Samma vertikala position på skärmen vid alla avläsningar. Slumpade övergångar fördelar käll-/skärmfasen bättre än en enda periodisk blinkning.
- Spara minst 100 övergångar per fall, både tändning och släckning, samt råfil och analysval. Rapportera min, median, p95 och max. Mät kamerans verkliga bildfrekvens.
- 240 fps ger 4,17 ms mellan kamerabilderna; det räcker för att se ett helt bildsteg men inte för att bevisa 0,2 eller 0,5 ms. För submillisekundfrågan behövs fotodioder och ett känt tidsreferens-/videotestupplägg, eller en lämplig HDMI-latenstestare.
- **Skärmen byter troligen ingångsläge mellan A (720p) och B (1080p).** Då innehåller B−A även skillnaden i skärmens behandling. Kalla detta ”kedjans extra latens”. Isolera skalaren först efter en separat kalibrering av skärmens båda lägen eller direkt videosignalmätning. Grabberns preview och USB-tidsstämplar duger inte som facit för flyglatens.
- Testa först stabil BUF/NTSC. Därefter, som egna fall: LOW, PAL/50 Hz, frånkoppling/återlåsning och HDMI→USB-C-adapter. Rapportera tid till bild efter bortfall separat från latensen när bild redan är låst.

Godkännandegränser bestäms som produktkrav, inte som påstådda mätningar: för flygvägen är ett rimligt första mål högst 2 ms extra från skalsteget; 16–33 ms extra är en annan produktavvägning. XR-brygga och glasögon tillkommer även med Primer. En HDMI-kontakt på Primer är inte en USB-C DP Alt Mode-sändare.
