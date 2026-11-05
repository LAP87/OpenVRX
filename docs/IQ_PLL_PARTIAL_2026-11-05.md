# IQ-PLL: första modellförsöket, 2026-11-05

Uppgift 74 / Core #28 är delvis genomförd och inte godkänd. Den nya privata heltalsmodellen jämfördes med ursprunglig fasdifferens på samma hashbundna IQ-indata. Core-bas `a6e3c2bb473ef18442ac32a06e81c9bbb615029c`. Ingen RTL ändrades.

FS 40 MHz, 60 rader, seed 1, deviation 2,8 MHz/V, kanal 12 MHz, video-LP 4,2 MHz. PLL: kp 3/8, ki 1/32, effekt-IIR 1/256, amplitudvikt högst 2. Fasdetektorns atan2-LUT är idealiserad; loopens steg använder heltal. Ingen efterhandsjustering av tidsläge. Ursprungliga SNR- och synkmått behölls.

| IQ-bitar/axel | C/N dB | SNR fasdifferens | SNR viktad PLL | Synkträffar fasdifferens | Synkträffar PLL |
|---|---|---|---|---|---|
| 4 | 4 | 5.62 | 9.33 | 0.000 | 0.000 |
| 4 | 8 | 10.59 | 12.93 | 0.034 | 0.017 |
| 4 | 12 | 14.78 | 16.31 | 0.186 | 0.085 |
| 7 | 4 | 5.15 | 9.92 | 0.000 | 0.000 |
| 7 | 8 | 11.34 | 13.68 | 0.068 | 0.034 |
| 7 | 12 | 15.65 | 17.44 | 0.305 | 0.068 |

Matrisen avslutades rc0 på 3,462 s med oförändrade bundna indata. Bättre luma-SNR är inte tillräckligt: kravet på minst lika bra synkträffar missades vid 8 och 12 dB för båda bitdjupen. Vid 4 dB var båda metoderna utan synkträffar. Det visar ingen mottagarkänslighet eller fungerande RF-kedja.

Riktad verifiering: 8 PASS och 2 FAIL på 1,37 s pytest (1,742 s driver). De sex ursprungliga IQ-testerna och två nya egenskaper passerade. Båda riktningarna i det nya fasramptestet missade gränsen TURN/10000: medelabsolutfel cirka 814 302 mot gränsen 429 497 i fasinkrementets heltalsenheter. Testet av fel looptecken nåddes därför inte; någon godkänd semantisk negativ kontroll påstås inte.

Originalkod, kontrakt, XML och loggar är bevarade privat i `private/notes/dev_2026-11-05/iq-results/`. Oberoende återläsning kontrollerade de båda jobbens hashbindningar och exakt tio XML-utfall. Inga signaler eller omkörningar. Ingen quick/fullsvit, Core-commit, Core-mainmerge eller hårdvaruacceptans.

Nästa motiverade steg är att granska fasrampens kvantiseringsfel och loopens tidsläge, innan ett separat experiment övervägs. Koefficienter och felgränser har inte ändrats efter utfallen. Detta är en sparad begränsning, inte en färdig PLL-leverans.
