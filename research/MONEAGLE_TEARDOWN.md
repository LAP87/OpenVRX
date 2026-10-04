# Eachine Moneagle — vad finns inuti (2026-10-01)

**Inget publicerat schema hittades.** Sökt på Moneagle-schema, teardown, kortnamn och OEM-tillverkare. Det som finns är en japansk recension med isärtagning och bilder ([drone4 del ②](https://drone4.blog.fc2.com/blog-entry-1687.html), 2020) samt tillverkarsidor. Bilderna är sparade lokalt för research i `research/raw/moneagle/drone4_imgs/` och får inte publiceras vidare (bloggen förbjuder återpublicering).

## Fynd

| Del | Vad bilderna visar | Säkerhet |
|---|---|---|
| Huvudkort | **LST-R022_V1.3**, datumkod 2031 (≈ vecka 31, 2020). Bloggen läste "I_ST-R002" men närbilden visar LST-R022. | Hög (läst på närbild) |
| **Videodekoder** | **TI TVP5150AM1** (32-stifts QFP, märkt "5150AM1 / 79T / CCN9") | Hög (läst på närbild) |
| DVR/display-SoC | 64-stifts LQFP, märkning ser ut som "DKN375A1-2013" — **oidentifierad** (suddig bild, inga sökträffar) | Låg |
| Minne | Winbond-krets bredvid SoC:n (modell ej läsbar) | Medel |
| Mottagare | Skärmad modul med kastellerade kanter vid SMA-kontakten; manualen: "Built-in Dual module and dual system", "Dual diversity receiver" | Medel; om den mixar eller bara växlar är okänt |
| Panel | 5" IPS 800×480 via **40-polig FPC** (typiskt parallellt RGB-gränssnitt för denna panelstorlek — ej verifierat) | Medel |
| Avlusning | Två 3-stifts footprints: **STK-DBG** och **SSD-DBG** (troligen UART eller programmering) | Märkning hög, funktion okänd |
| Övrigt | 1S 4000 mAh, DC 5–23 V in, microSD (DVR), högtalare på kontakt; flera kretsar under ledande avskärmningstejp | Hög |
| AV-kontakt | Manualen: "AV video input, Audio output" → **ingen videoutgång** | Hög |

Tillverkare: kortprefixet "LST" matchar Lst Co., Ltd (kinesisk FPV-tillverkare: LST-monitorer, LST-S2/S4 AIO-kameror). DMKR säljer i dag en "Moneagle" och listar **"AV Input, HDMI input"** — sannolikt en nyare revision än projektägarens Eachine-exemplar (ej verifierat).

## Evidensläge (förtydligat 2026-10-01 efter Astras granskning)

Fynden ovan gäller **den Moneagle som drone4 tog isär 2020** (kort LST-R022_V1.3). **projektägarens exemplar är inte kontrollerat** — kortrevision och dekoder kan skilja. Vilket utgångsformat TVP:n är konfigurerad för (inbäddad BT.656-synk eller separata synkstift) och om avtappning påverkar Moneagles egen bild är också overifierat. Foto- och mätlistan nedan avgör om spåret håller.

## Varför detta kan vara riktigt bra för projektet (om det bekräftas)

1. **Moneagle kan vara en färdig TVP5150AM1-utvecklingsplattform.** Samma dekoder som valts för rev A. Dekoderns digitala BT.656-utgång (8 databitar + 27 MHz klocka) finns på kortet. Man kan **lyssna passivt** på den bussen med en FPGA (t.ex. Tang Nano-kort) och utveckla bildbuffert, deinterlacing och HDMI-utgång mot riktig FPV-video innan vårt eget kort finns.
2. **Din ursprungliga idé — HDMI-utgång på Moneagle — blir möjlig** på det här sättet: inte via panelbussen, utan genom att avlyssna TVP5150AM1:s BT.656-utgång → FPGA → HDMI. Tio trådar (D0–D7, PCLK, GND), kort avstånd, seriemotstånd vid avtappningen.
3. **Enklaste uttaget av analog bild:** CVBS mellan mottagarmodulen och TVP5150AM1:s ingång (via kopplingskondensator) → extern AV→HDMI-konverterare.

Regler för avtappning (om vi gör det):
- FPGA:n får **aldrig driva** TVP5150:s I2C — det sköts av Moneagles SoC. Bara lyssna.
- Seriemotstånd ~47–100 Ω nära avtappningen, kort flatkabel, gemensam jord.
- Avsikten är **passiv** avlyssning utan kapade spår. Trådar och FPGA-ingångar belastar ändå 27 MHz-bussen (kapacitans); att Moneagles egen bild är opåverkad ska kontrolleras efter inkoppling.

## Foto- och mätlista för ditt exemplar

Ta isär enligt drone4: fyra skruvar i hörnen bak, försiktigt med snäpplås upp/ner och flatkablarna inuti.

**Makrobilder (rakt uppifrån, skarpt, gärna med linjal i bild):**
1. Hela kortet, båda sidor om möjligt (batteriet är lödd — lyft inte i kablarna).
2. **Den stora 64-stifts kretsen** — märkningen tydligt läsbar (flera vinklar mot ljuset).
3. TVP5150AM1 med omgivande komponenter och kristall (bekräfta 14,31818 MHz-kristall).
4. Winbond-kretsen (hela märkningen).
5. Under den grå avskärmningstejpen: lyft tejpen försiktigt i ena kanten och fotografera vad som finns under (troligen panel-/skalningskrets). Tryck tillbaka efteråt.
6. Mottagarmodulens skärmplåt och kastellerade kanter; båda SMA-kontakterna och vart de leder.
7. 40-poliga panel-FPC:ns tryck (artikelnummer på flexen) och båda vita flatkablarnas ändar.
8. STK-DBG och SSD-DBG.

**Mätningar (multimeter, utan ström först):**
- STK-DBG / SSD-DBG: vilket stift är GND? Med ström: spänning på övriga stift (3,3 V-nivå tyder på UART).
- Kontinuitet från mottagarmodulens videoutgång till TVP5150AM1:s AIP1A (stift 1 enligt TI-databladet — kontrolleras i WP5).

Med bilderna kan vi identifiera SoC:n, rita ett partiellt blockschema och välja avtappningspunkter.
