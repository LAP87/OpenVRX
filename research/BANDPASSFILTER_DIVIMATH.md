# Divimath SMA-bandpassfilter 5–6 GHz (tips, 2026-10-01)

Källor: [Mads Tech-recension (YouTube, 2026-10-01, 16 min)](https://www.youtube.com/watch?v=zfn4LiLCPos) — transkript i `research/raw/divimath/transcript.txt`; [Divimaths produktsida](https://www.divimath.com/products/divimath-sma-bandpass-filter-5-6ghz). Recensenten fick filtren gratis av Divimath (sägs i videon).

## Fakta

| | Värde | Källa |
|---|---|---|
| Pris | 39,99 USD för 4 st (≈ 10 USD/filter, ≈ 401 kr för paketet) | Divimath, 2026-10-01, i lager |
| Passband | 5–6 GHz | Divimath |
| Förlust i passbandet | ca 0,5–0,75 dB över 5,3–5,95 GHz; medel 0,65 dB enligt utvecklarna; specens max 1,5–1,7 dB | Divimath; recensionen |
| Dämpning utanför | 26 dB vid 2,4 GHz, minst 39 dB vid 1,25 GHz | Recensionen (från tillverkarens data, delvis visat på spektrumanalysator) |
| Montering | SMA i linje mellan antenn och mottagare; 90°-adapter rekommenderas | Divimath |
| Ursprung | Thailand, NDAA-kompatibel | Divimath |

## Vad det hjälper mot — och inte

- **Hjälper:** överstyrning/okänslighet i mottagarens ingångssteg från starka signaler *utanför* 5,8 GHz-bandet: egen radiolänk på 868/900 MHz eller 2,4 GHz med hög effekt nära mottagaren, 2,4 GHz-WiFi, mobilmaster.
- **Hjälper inte:** störningar *inne i* 5,8 GHz-bandet (5 GHz-WiFi, andra piloter, trådlösa kameror). Recensenten säger själv att man där kan göra lite.
- Kostnad: ≈ 0,65 dB mindre signal i passbandet — ungefär motsvarande en liten minskning av räckvidd; tillverkaren föreslår antenn med högre förstärkning om det märks.

## Relevans för projektet

- **Experiment 1:** valfritt. Om projektägarens radio (Jumper Bumblebee; ELRS-effekt och band ej dokumenterat här) körs med hög effekt nära mottagaren, eller vi flyger i WiFi-tät miljö, kan två filter (ett per antenn på SpeedyBee) ge ett tydligare test av mixningen. Testa A/B: samma flygning med och utan filter.
- **Rev A / eget mottagarkort:** argument för ett bandpassfilter (keramiskt/SAW) direkt i varje mottagares ingång om vi bygger egen RF-del. Billiga RX5808-moduler har begränsad selektivitet (allmänt känt i hobbyn, ej verifierat här).
- Frakt och moms till Sverige från Divimath: **ej kontrollerat.**
