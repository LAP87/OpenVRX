# UART från 27 MHz och SDRAM-PLL: båda läsbara

Claudes två nya fasta UART-kontroller kördes på samma Tang Nano 20K som M0/M2a, med oförändrad mottagare vid 115200 8N1. Båda gav **39 av 39 rader exakt enligt mallen**, utan felaktiga eller ofullständiga rader i respektive capture på tio sekunder.

| Laddad topp | Nominell klocka enligt källa | IOREG | Mottagna byte | Exakta rader | Felaktiga rader |
|---|---|---|---|---|---|
| `m2u_uart27` | 27 MHz, direkt kortklocka | 0 | 3 198 | 39 | 0 |
| `m2u_uart64` | 64,8 MHz, `clocks_sdram` | 0 | 3 198 | 39 | 0 |

Exakt mottagen rad, följd av CRLF:

```text
M rs=5 pass=0012 err=00000000 bits=0123456789ABCDEF0123456789ABCDEF pos=UUUUUUUU
```

De två capturerna är byteidentiska, SHA256 `8a2afca1a35c90212a17becd8a8fcf30153a5d7c3f7e1cec6eb04f56291af213`. Tiderna, råbytes före respektive laddning, programmeringsloggar och läshjälparen finns i [råunderlaget](2026-10-20/uart-clock-checks/EVIDENCE.json). Det är inga nya simuleringar eller byggen och inga omförsök av tidigare M2a-prov.

## Identitet och laddning

Bitströmmar hämtades med autentiserad git från Core-grenen `bench/bitstreams-2026-10-20`, fryst commit `5a43c830a579b0e092c22ae29638380a62191132`. Källgrenen `bench/uart-check` frystes till `e53c7aa89ce2d7d7cf3460e9bf6b353987ff283d`.

- `m2u_uart27.fs`: 731 566 byte, SHA256 `6d68159b106feea4a16a77841f4440f614baa9064e4419168925a3ae76689f28`.
- `m2u_uart64.fs`: 738 086 byte, SHA256 `7cba51f0c41e9c996e14e4f585f564ea9f1fead6f9d264438bf55c0d90e048cf`.

Båda `.fs` matchade sina manifest, och samtliga 52 manifestinputs per bygge matchade källgrenens Gitblobbar. De sex övriga deklarerade artifacts per bygge fanns inte i bitströmsgrenen; detta är ingen oberoende fullständig bygg-/routegranskning. Källor och constraints visar bara kortklocka, S1, lysdioder och UART på stift 69; ingen SDRAM- eller videoväg används av dessa toppar.

Varje kontroll startades separat med `openFPGALoader -b tangnano20k --ftdi-serial 2025030317 -m`, rc0/DONE. Samma läshjälpare och mottagarinställningar användes. Råbytes som låg före laddningen sparades separat, och inget UART-payload skickades till kortet. Ingen flash skrevs. Efter båda proven återladdades den redan bekräftade rättade M0-bänkbilden till SRAM, rc0; samma bild finns kvar i flash sedan tidigare.

## Vad detta säger om M2a

**Detta är inte ett minnesresultat.** `rs=5`, `err=00000000` och resten av raden är fast testtext. Ingen SDRAM läses eller skrivs här, och klockfrekvenserna är nominella källvärden, inte uppmätta frekvenser.

Resultatet visar att en känd rad kan överföras genom UART-kedjan i båda dessa byggen. Det tidigare M2a-felets orsak är fortfarande inte fastställd. **Båda nya kontrollerna har IOREG=0; M2a-provet med förvrängd logg hade IOREG=1.** Rapportgenerator, I/O-register och övrig design skiljer sig också, så detta isolerar inte enbart M2a:s textlogik eller bevisar ett generellt PLL-fel.

Nästa separata uppgift bör granska M2a:s avsändarrad och skillnaderna mot dessa två kontroller. Ett prov med samma fasta rad och IOREG=1 kan vara en riktad nästa fråga, om käll-/bygggranskningen motiverar den. Ingen sådan körning eller firmwareändring gjordes här. Uppgift 47 i arbetsplanen är fortsatt öppen; det finns ännu inget accepterat `rs=5 err=0` från verklig minnesjämförelse eller fysisk S2-felinjektion.
