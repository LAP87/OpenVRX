# AVG16 tar upp fält i modellen, men bilden är ännu inte godkänd

Uppgift 83 prövar exakt ett redan källdefinierat alternativ: Capture(avg=16) i fryst Core `031bba053943ee04ce303ae75b5e701746169c97`. Samma sparade seed2/CN12/7bit PLL-koder som uppgift81–82, COMB1/WHITE_X8=20/bootkontroll på. Ingen ny IQ, parametersökning, producentändring eller defaultändring. AVG8-baslinjen återanvändes från dess sparade resultat och kördes inte om.

## Fältupptagning och pixelkvalitet är olika resultat

| Kontroll | Sparad AVG8-baslinje | Första AVG16-fallet |
|---|---:|---:|
| Utmatade slutna rader | 0 | 723 |
| Strukturellt giltiga rader | 0 | 723 |
| Observerade V-armar | 0 | 3 |
| Utmatade F-faser | inga | båda, 480 respektive 243 rader |
| Giltiga rader med ursprunglig pixel-RMSE<16 | 0 | 0 |

AVG16 gav tillräcklig fältupptagning för den förbestämda grinden, minst 400 strukturellt giltiga rader, båda F-faser och minst en V-arm. Den grinden är inte bildacceptans. Längre slicermedelvärde påverkar synkdetekteringen; lumaordens pixelkrav har inte flyttats, och inget RMS-fel har korrigerats med offset/gain eller tidsanpassning.

Tidsmappningen mot den syntetiska källans radstarter visar dessutom förskjutna radetiketter:

| Utdataradnummer minus källans aktiva radindex | Rader |
|---:|---:|
| −4 | 20 |
| −3 | 70 |
| −2 | 108 |
| −1 | 179 |
| 0 | 346 |

377 av 723 slutna rader har alltså förskjutet radnummer i denna tidsmappning. Det nya filtervalet löser inte detta eller pixelkvaliteten. Känd startupfråga #34 är inte stängd, och F-fasgrupperna är diagnostik mot källtiden, inte en ny policy för mixerns F-bit.

## Verklig modellnegativ: ta bort V men behåll aktiv video

Efter positivfasen skapades en ägd indatakopia där endast de 76 geometriska vertikalintervallen ersattes av vanliga H-rader: 188 sampel med kod 13, resten 22. Alla aktiva källbyten är exakt oförändrade. Den faktiska kopian och hashvärdet bands före en separat första modellfas med samma AVG16.

Resultatet blev **noll V-armar och noll utmatade ord**. Modellen fabricerade alltså ingen bild från denna H-signal utan V. Det stöder att den positiva fältupptagningen beror på vertikalsynken. Detta är en faktisk indatamutation som matats genom modellen, inte en metadataassertion eller ett RTL-test.

## Timing

Första H-låset kom vid sampel 25435 med AVG16 mot 30516 i den sparade AVG8-baslinjen: 5081 sampel tidigare i just detta fall, cirka 127,025 µs vid 40 MS/s. Detta är uppstarts-/låsbeteende i den adaptiva modellen, inte en generell latensvinst.

Ett registrerat 16-sampels rektangulärt medelvärde har analytiskt fyra sampel mer gruppfördröjning än motsvarande åttasampelsmedel, 0,1 µs vid 40 MS/s. Det bestämmer inte den adaptiva slicerns faktiska flank- eller låstid. AVG16:s första ord emitteras 368–377 sampel efter respektive syntetisk H-start. AVG8 har inga ord att jämföra mot; extra faktisk bild-/HDMI-latens är därför inte uppmätt.

## Verifiering och gränser

Första positiva fasen 3,474 s, enda negativa fasen 2,778 s, båda rc0. Root återläste ord/markörer, exakt gamla pixelmått, tidsstämplar, källradsmappning och den faktiska V-masken utan import av DUT eller primärläsare. Sex ytterligare ägda källa-/options-/nod-/falsk kvalitets-/native-/hårdvaruskador avvisades; samma kopior lästes i final. Inga fel, signaler, timeout eller omkörningar.

264 Git-/arkiv-/källfiler är oförändrade. Modellen och RTL-källan har redan AVG-parametern; dess statiska förekomst är inte ett bevis på en fungerande FPGA-konfiguration med 16. Ingen HDL, place-and-route eller hårdvara kördes och ingen Core-commit gjordes. Produktionsdefault är fortsatt 8; det stoppade rådet har inte återstartats.

[Maskinläsbart resultat](IQ_AVG16_EXPERIMENT_2026-11-07.json) och [exakta experimenthjälpare](../research/experiments/iq_avg16_2026-11-07/) finns sparade. Resultatet motiverar en separat första RTL-kontroll av det existerande parameteralternativet och kvarstående radetiketter, innan någon produktionsändring övervägs. Det är inte ett skäl att prova fler medelvärden tills ett mått blir grönt.
