# M0: rutan fastnade vid vänsterkanten

Ägaren såg att testbildens ruta efter en stund fastnade till vänster och bara fortsatte uppåt och nedåt. Felet reproducerades i originalets RTL. En separat rättad bänkbitström är nu skriven till kortets flash, återläst av programmeraren och bekräftad av ägaren efter en strömcykel: ”Ja, den startar och fortsätter studsa”.

## Orsak

Originalets 11-bitars x-position uppdaterades innan den nya riktningen fick effekt. När positionen var 1 och rutan gick åt vänster blev `1 - 3` lika med 2046 efter heltalsomslag. Därefter växlade både position och riktning mellan `(1, vänster)` och `(2046, höger)`. Höjdrörelsen fortsatte. Första omslaget inträffar på bildruta 778 från startvärdet 100, ungefär 13 sekunder vid nominella 60 bilder/s; tiden är beräknad, inte uppmätt på skärmen.

Detta gäller den laddade M0-källan från Core `bf05ac0`. Samma rörelseblock finns i granskad Core-main `8dff8d1`. Testbildens ursprungliga hårdvaruobservation styrkte bild och rörelse vid observationstillfället, men fångade inte felet efter längre körning. Start- och bildresultaten står kvar; obegränsad korrekt studs var inte verifierad då.

## Privat rättning och verifiering

Rättningen begränsar positionen till bildkanten innan riktningen vänds. X hålls inom 0–1216 och Y inom 0–656, så hela rutan på 64×64 pixlar ryms. Bara rörelseblocket i `gateware/top/m0_testpattern.v` ändrades. Pinnarna, klockorna, DVI-sändaren och övrig Core-kod är oförändrade.

- Riktad Icarus-simulering av den faktiska M0-toppen med stubbar för klockor, videotiming och sändare: 5 000 bildrutor och 5 000 kontroller av stillastående position mellan bildpulser. Detta isolerar rörelsen; det är ingen simulering av HDMI eller PLL.
- Originalet reproducerade omslaget och låg kvar i x=1/2046. Det fungerade som den negativa kontrollen. Kandidaten matchade en oberoende heltalsmodell för samtliga bildrutor: sex besök vid vardera sidokanten, sju vid överkanten och åtta vid underkanten, utan position utanför bildytan.
- Första privata läshjälparen stannade efter originalsimuleringen eftersom den inte väntade sig Icarus egen rad efter `$finish`. Hjälparen och originalspåret är bevarade. En separat fortsättning läste samma originalspår och körde den ännu inte startade kandidaten. Originalets native-returkod sparades inte separat före läsfelet och anges därför inte som ett separat kvitterat rc0. Kandidatens kompilering och körning har sparade rc0. Ingen originalsimulering kördes om.
- Ett nytt M0-bygge från fryst `bf05ac0` plus den enda patchen tog 46,503 s, rc0, utan signaler eller omförsök. Seed 0, IOREG 0, HDMI 0 och VINTERP 0. Sista routade klockorna: pixel 150,13 MHz och 27-MHz-domänen 310,27 MHz, båda godkända mot byggkravet 75 MHz.
- Samtliga 207 källfiler kontrollerades mot baskällans Gitblobbar: exakt toppens rörelseblock skiljer. Byggmanifestets 50 inputs och sju artifacthashar kontrollerades. Genererade pinnconstraints är identiska med den tidigare M0-versionens.
- SRAM-laddning rc0, därefter ägarens bekräftelse: ”Ja, den studsar tillbaka och fortsätter”. Den rättade versionen skrevs sedan med openFPGALoader `-f --verify`, rc0, följt av bekräftad start och fortsatt studs efter ur- och inkopplad USB-ström.

**Bitström i flash:** SHA256 `dea73706130d512345e01d3ddc7b6d41d3e80b34144d3c568b33c26bcfc25fd3`, 842 822 byte. Baskälla `bf05ac0feed58c3295949a6f3b4ee55c886cd1e2`, tree `49923a6dda3c8f3466eff76ddaa7d835f1785c1d`, plus rörelsepatch SHA256 `0f37bb90f9066afceb66d54d37f9b95f59329d14b8f56c96376d10581866a18d`.

Det är en **privat bänkversion**, inte en ny Core-main-revision. Ingen Core-commit eller sammanslagning gjordes; patchen och det riktade regressionstestet behöver föras in i en separat Core-uppgift med dess vanliga granskningskrav. Ingen helsvit kördes om för detta bänkprov. Inga tidigare källor, byggen eller råspår ändrades.

Original, patch, testbänk, spår, byggmanifest, programmeringsloggar och ägarens svar finns privat i `private/notes/bench_home_2026-10-20/m0-motion/`. SDRAM-provet är fortfarande ej avgjort på grund av oläsbar UART-logg; TVP, RF och mottagarkedjan är inte provade genom denna rättning.
