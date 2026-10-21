# Råd 2026-10-21: efter de första dagarna på kortet

Två granskare (Opus 5.5) med varsin brief, sammanställt av Fable som ordförande. Rapporterna: [LOGIKGRANSKNING.md](LOGIKGRANSKNING.md) (15 fynd i kedjan, kodläsning plus ett Icarus-prov) och [MOTTAGARE_ALTERNATIV.md](MOTTAGARE_ALTERNATIV.md) (mottagarvägar nu och för produkten; daterade priser i `research/MOTTAGARE_ALTERNATIV_2026-10-21.md`). Rådet beslutar inget; det föreslår, ägaren väljer.

## Vad kortet har lärt oss hittills

M0-bild, M2a godkänd (läspunkt 5 ren med marginal när I/O-cellregistren är av), S1/S2, UART-vägen, och en TVP-modul som ger klocka, I2C (adress 5D) och NTSC-timing. Två klasser av fel som simuleringen inte fångade: en räknare som slår runt efter 778 bildrutor (ingen simulering körde så länge) och register med CE/SET/RESET i I/O-cellerna som inte beter sig med vår verktygskedja. Ingen videosignal har nått dekodern än.

## Rådets slutsatser

1. **Första bilden tas i LOW**, inte BUF. Logikgranskningens F1: SDRAM-läsningens fönster följer bygget så länge DQ-registret har klockenable och ingen I/O-timing är begränsad; M2a:s godkända läspunkt gäller alltså M2a-bygget, inte M4/M6. LOW rör inte SDRAM:en. M4 saknar byggval för LOW; det är en rad i `build.sh` (uppgift 53). M6 har `LAT LOW` i menyn.
2. **Gör M2a:s resultat giltigt för alla toppar** (uppgift 49): DQ-infångning som ren vippa varje klocka, kvalificering i nästa steg, bygg med enbart `--vopt ireg_in_iob` och `iob_regs.py --strict` som grind; samma för dekodrarnas YOUT-ingångar (F5). Det är beslut 2:s syfte utan verktygskedjans fälla. Verifieras med M2a-svepet på kortet igen och ett SDRAM-självtest i `fb_backend` som varje bygge visar.
3. **Adressen 5D kan vara FPGA:ns verk** (F3): utan RESETB-tråd tar dekodern adressen medan FPGA:n ännu konfigureras. Mät YOUT7 på modulen med Tang-kortet strömlöst, koppla RESETB-tråden, och låt `tvp_ctrl` prova båda adresserna själv (uppgift 50) innan M4 körs med två moduler.
4. **Okänd dekoderstatus får inte räknas som lås** (F4): med dagens regel kan en frilöpande dekoder vinna radvalet med en platt bild i just det ögonblick diversity ska hjälpa. Åtgärden är liten (uppgift 51) men ska mätas först: M6:s mätarsida med en öppen videoingång säger hur platt frilöpningen är.
5. **Mottagardelen:** XIAO/C5VRX är dagens snabbaste väg till bild och samtidigt planens C5VRX-jämförelse; kör den med webbterminalen öppen (livstecknet är en `STATUS`-rad varannan sekund; lysdioden säger inget) och låt första kalibreringen gå klart med sändaren av. Beställ RX5808 från ett andra håll parallellt (uppgift 32): de är referensen och produktens rev A-mottagare. Kontrollera om RC832HD från blad 15 har kommit: AV-ut ger en ström direkt. Premiummoduler lämnar en redan mixad ström och duger bara som referens. AD9361-vägen väntar.
6. **Mindre fynd** (F2, F6–F15) samlas i uppgift 52; bänkkriteriet för M4 med en modul ändras i bänkplanen nu: "bild på HDMI och lysdiod 1", inte "lysdiod 0 till 1 Hz".

## Frågor till ägaren

- I/O-cellregistren: ägaren tar ingen ställning (2026-10-21); de förblir av tills uppgift 49 är gjord.
- Moneagle får öppnas för en CVBS-tapp som reserv (ägaren 2026-10-21).
- Vem tar uppgift 49–52: nattpasset för Opus finns i [NATTPASS_2026-10-21.md](../../NATTPASS_2026-10-21.md); Fable tar 53 och bänken.
