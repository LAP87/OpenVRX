# Scripts som användes för underlaget

Dessa fem scripts sparas oförändrade för att visa hur gransknings- och
acceptansresultaten togs fram. De är arbetsverktyg från originalmaskinen,
inte installerade produktkommandon. Absoluta sökvägar och antaganden om
`private/` i dem gäller den historiska arbetskatalogen och måste anpassas
om de ska köras någon annanstans. `check_puck_export.py` regenererar
Pucks exportfiler; använd en separat checkout och en ny utmatningsmapp.

`reproduce.py`, `check_schematic.py` och `probe_edges.py` användes mot
övertagandeläget. Assertions i dem kan avsiktligt falla mot rättad Core.
`record_build.py` och `check_puck_export.py` användes för utvecklingspaketets
acceptans. Aktuella regressionskommandon finns i [RESULTAT.md](../../RESULTAT.md).
