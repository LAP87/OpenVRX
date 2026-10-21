# Mottagare att få tag på nu: priser och tillgång (2026-10-21)

Underlag till [docs/design/2026-10-21/MOTTAGARE_ALTERNATIV.md](../docs/design/2026-10-21/MOTTAGARE_ALTERNATIV.md). Allt är läst 2026-10-21 med ett amerikanskt sökverktyg; EU-butiker kan saknas i träffarna. Butiker nämns inte och annonser länkas inte (inköpsregeln); sök på modellnamnet. **[S]** = sökutdrag eller annonstext, inte en öppnad tillverkarsida; **[T]** = tillverkaren; **[K]** = projektets kod eller dokument; **[R]** = vårt resonemang. Inget är beställt.

## RX5808 (modul, SPI)

| Vad | Pris 2026-10-21 | Tillgång | Belägg |
|---|---|---|---|
| Annons, Kina-lager | ca 37 EUR | ej angiven | [S] |
| Annons, Kina-lager (DIYMORE-märkt) | 50,99 USD | ej angiven | [S] |
| Två annonser, SPI-läge | 21,56 och 48,70 USD | ej angiven | [S] |
| Annons, USA-lager | 26,99 USD | "Last items in stock", sidan uppdaterad 2026-09-13 | [S] |
| Fyrpack, SPI-läge, Kina-lager | ca 79 USD för fyra | ej angiven | [S] |
| "Repurposed": moduler lödda ur ny FPV-utrustning, rengjorda och provade på 5 V, "SPI Mod: Yes" | 17,99 USD | slutsåld | [S], säljarens produktsida |
| Grossistannonser, minsta order 1–2 st | ca 5–45 USD | ej angiven | [S] |

Jämfört med tidigare noter: 9–13 EUR i annonser december 2025 ([MOTTAGARE_3G3_5G8_2026-10-18.md](MOTTAGARE_3G3_5G8_2026-10-18.md)) och Bardwells "omkring 40 USD" 2026 ([RF-underlaget, tillägget](RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md)). Dagens annonser ligger mest på 20–50 USD per modul. En listning långt under det, från en säljare som inte skickar, stämmer med ägarens misstanke om ett gammalt eller felaktigt pris, men det är inte kontrollerat [R]. Att någon säljer moduler lödda ur annan utrustning tyder på knapphet, men ett enstaka fall bevisar ingen marknadsbrist [R].

Annonserna anger olika band (5725–5865 MHz med 8 kanaler mot 5645–5945 MHz) [S]. Läs SPI-revisionen och SAW-filtrets märkning på de moduler som kommer ([RF-underlaget](RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md), avsnitt 1).

## Färdiga mottagare och monitorer med AV-ut

| Enhet | Pris 2026-10-21 | Vad som är intressant | Belägg |
|---|---|---|---|
| RC832S (Skyzone), 48 kanaler | 79,99 USD | två AV-uttag, sparar kanalen; gamla 32-kanalers RC832 säljs fortfarande | [S] |
| RC832-HD (Skyzone) | ej inhämtat | AV-ut 3,5 mm, 1,0 Vpp typ, 75 Ω; mini-HDMI uppskalad till 720p/1080p; 6–24 V; AV-utgången ca 20 ms mot HDMI ca 40 ms enligt en återförsäljare | [S] |
| RX5808-PRO-PLUS-OSD (Realacc), goggle-modul | 49,00 EUR | en mottagare, inte två | [S] |
| DIY RX5808-diversitykort med OLED | ej inhämtat | två RX5808, automatisk växling, AV-ut; bygger på rx5808-pro-diversity | [S] |
| FlySight Black Pearl, 7 tum | ej inhämtat | **RX1 AV OUT, RX2 AV OUT och DIV AV OUT**, "Can receive 2 different channels at the same time", 7–28 V; listad "In Stock" av en återförsäljare; PAL som standard | [S] |
| Eachine LCD5802D, 7 tum | ej inhämtat | en AV-utgång och en AV-ingång; växlar till den starkare mottagaren, alltså en ström | [S] |

## SDR för ett datorprov

| Kort | Pris 2026-10-21 | Belägg |
|---|---|---|
| HackRF One | 299 EUR (kampanj, ordinarie 339 EUR) och 321,90 EUR inkl. moms hos två europeiska återförsäljare, båda "in stock" | [S] |
| AntSDR E200 (AD9361) | se [SDR_5G8_MOTTAGNING_2026-10-19.md](SDR_5G8_MOTTAGNING_2026-10-19.md) (priser 2026-10-19) | [T] |

## Läget hos tillverkare och projekt

- **RichWave** 2026-10-21: tabellen Analog Wireless Audio/Video listar RTC6701, RTC6711, RTC6705, **RTC6715**, RTC67033, RTC67133, RTC6706S och RTC6716S, plus PA-kretsarna RTC75401–RTC76408. Ingen rad har statusmärke (New, NRND, EOL) [T] ([tabellen](https://www.richwave.com.tw/en/page_prd_new.aspx?Id=8)). Oförändrat mot 2026-10-17.
- **C5VRX** 2026-10-21: `main` på `59dcfce` (11:42 UTC), senaste release `c5vrx5-v5.0.363` (10:29 UTC), tidigare samma vecka 5.0.332 och 5.0.322 (2026-10-20); 356 stjärnor [K] ([releaser](https://github.com/Twotoz/C5VRX/releases)). PR #230 (2026-10-20) anger att bilden försvinner vid ca −92 dBm stillastående och −88 till −90 dBm vid gång, brusgolv −96,7 dBm i 12,9 MHz, brusfaktor ca 6 dB; FINDINGS (PR #226) kalibrerar mot Wi-Fi-radions egen RSSI, inte mot en extern källa [K]. Ingen dämparjämförelse mot RX5808 är publicerad [K].
- **Seeed XIAO ESP32-C5**: wikin anger dual-band Wi-Fi 2,4/5 GHz, U.FL-kontakt, röd laddningslysdiod och gul användarlysdiod (GPIO27), men ingen strömförbrukning och inte antennens band [T] ([wiki](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/)).

## Ej verifierat

- Leveranstider till Sverige för någon av annonserna.
- Att RC832HD:n som blad 15 nämner (2026-10-12) har kommit.
- FlySight Black Pearls utgångar och nivåer ur ett tillverkardokument; om den fortfarande tillverkas.
- Priser på RC832-HD, Black Pearl och DIY-diversitykorten.
