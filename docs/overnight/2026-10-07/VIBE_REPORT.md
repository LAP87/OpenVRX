# Vibe-rapport: navets dokumentationsgranskning, natten 7–8 oktober 2026

Paket R01 enligt [COORDINATION.md](COORDINATION.md) och
[WORKPLAN.md](WORKPLAN.md). Mistral Vibe CLI, påbörjad 2026-10-07 cirka
23:10 Europe/Stockholm, uppdaterad 2026-10-08 cirka 00:40. Basrevisioner
vid start: hub `4d43600`, Core `7cc4eda`, Puck `9d2fb57` (submodul
`82c4134`).

## Ägda filer och tillstånd

Ändrade av mig, ännu inte incheckade — root granskar och checkar in:

- `OpenVRX/REVIEW.md`
- `OpenVRX/AGENTS.md`
- denna rapport, `OpenVRX/docs/overnight/2026-10-07/VIBE_REPORT.md`

Inga andra filer har rörts. Inga Git-ändringar och inga tunga test- eller
byggjobb — det äger Codex under det gemensamma låset. Core-arbetskatalogen
hade Codex' stage:ade fuzz-ändringar under tiden; jag rörde dem inte.
Verifieringen är läsning av kod, tester och dokument vid git-commit
`7cc4eda` samt jämförelser mellan grenar. Ingenting är kört av mig.

## Verifierade påståenden

| Påstående | Var det står | Resultat |
|---|---|---|
| F1: ofullständig rad lagras inte, räknas som dålig | `rtl/mix_chan.v` (`complete = !w_broken && w_next == 360`), modell i `model/line_mixer_ref.py` | stämmer |
| F2: en pollrunda gäller bara hel | `rtl/tvp_ctrl.v` (NACK på 88h/89h/03h sätter `dev_err`, tömmer `status_valid`; giltig först efter hel runda med 03h=0Dh) | stämmer |
| F3: saknad första rad ger svart rad, ingen SDRAM-läsning | `rtl/fb_sdram.v` (`BLACK = 32'h10801080`, `f_blank`) | stämmer |
| LL-triggerns radantal hålls över klockdomänen | `rtl/cdc_sync.v` `toggle_tx` (GAP=16, värdet hålls mellan vändningar), `formal/toggle_tx_props.v`, `formal/README.md` punkt 3 märkt "Rättat 2026-10-07" | stämmer |
| I2C ger upp vid låst SCL | `rtl/i2c_master.v` (`STRETCH_MAX = 270_000`, 10 ms vid 27 MHz, avslut med NACK och `stuck`) | stämmer |
| Brusmått per rad och kanal | `rtl/noise_stats.v` (luma utanför 16–235, fönster 1024 rader, mixern använder det inte) | stämmer |
| Init-lista | `rtl/tvp_ctrl.v` (00h=00, 04h=FC, 0Dh=47, 28h=00, 02h=20, 03h sist) | stämmer |
| Dubbeldålig rad utelämnas en i taget | `rtl/line_mixer.v` (`omit = show && both_bad && (adm_new || !bad_last)`), modell och egenskapstest | stämmer |
| Par döms på partnern när aktuell kanal saknar rad i utfältet | `rtl/line_mixer.v` (`c_alt`), `test_mixer.py::test_returning_channel_starts_the_next_field` | stämmer |
| M6-logg: snö + brus + låsflagga i samma rad | `gateware/README.md` (60 byte; äldre 57- och 43-byte-rader läses också), `tools/snowlog.py` (tre format, CSV-kolumner) | stämmer |
| puck_ui: registrerad kanaltabell | `rtl/puck_ui.v` (`chan`-register, `freq_bcd` per kanal); byggt seeds 0–3: 109/116/127/115 MHz mot kravet 54 | stämmer (byggsiffror enligt README, ej ombyggda av mig) |
| bt656_rx: run-on-rad mättas inte runt | `rtl/bt656_rx.v` (`act_count` mättas vid 2047) | stämmer |
| CDC-bevis och vad de inte täcker | `gateware/formal/` (fifo, genlock, toggle, toggle_tx, level, linebuf) + `formal/README.md` ("Inte bevisat": metastabilitet, SDRAM-latens, LOW-ring, reset mitt i drift) | stämmer |
| Testantal | Core `README.md` och `gateware/README.md`: 396 | verifierat: baslinjen samlade 396 (395 passed, 1 xfailed) |

## Core #17, öppet

Efter byte `BUF` → `LOW`, och efter reset i `LOW`, kan `fb_display.v` visa
video så snart någon trigger har kommit (`ll_alive`), alltså även i bilder
som går på egen tid innan genlocken har låst, och de läser ringplatser som
inte skrivits sedan bytet. Tre orsaker sedda: genlocken ignorerar en tidig
trigger, fältet som ringskrivaren går med i mitt i ger en trigger, och
`ll_since` räknar vidare utanför `LOW`. Att ta bort de två sista räcker
inte (svep av bytestider i `tb_fb.v`). Det som återstår är en regel för när
`LOW` får visa video — ett beteendekontrakt, inte en lokal rättning.
`test_fb.py::test_low_after_switch_shows_whole_fields` är xfail (strict)
med ärendenumret, och kedjetestet räknar kända fynd mot #17 separat
(`known`). Rapporterat: 14 av 18 riktade switchfrön, plus frö 85 som startar
i `LOW` och har X på r/g/b i första hela bilden. Beskrivet öppet i både
`REVIEW.md` och `AGENTS.md`.

## Core #18, öppet (nytt under natten)

Mixern startar ett nytt utfält när den aktuella mottagaren tystnar och den
andra tar över ur takt (`line_mixer.v`: "numbering owner changed out of
step"). Nedströms ser fältminnet och LOW-skrivaren en fältstart bara när
F-biten ändras eller radnumret går ner. Startar det nya utfältet på en rad
ovanför den sista med samma F-bit markeras ingenting: fältminnet tar då
två utfält för ett och fyller raderna mellan med raden ovanför och sedan
fältet före. Med icke-sammanflätad källa (TVP5150AM1 håller F = 1) gör
varje övertagande i ett fälts nedre del detta. Reproducerat i simulering:
xfail `test_mixer.py::test_new_output_field_is_seen_downstream` (RTL och
modell överens) och kampanjrunde d3 frö 150 (PAL; kamerafält 4 och 6
lagrade som ett fält). Rättningen är ett ägarbeslut om vad mixerns F-bit
betyder. Beskrivet öppet i både `REVIEW.md` och `AGENTS.md`.

## Fuzz-grenens kvarlämnade sex commits

`origin/fuzz/chain-2026-10-07` ligger sex commits före `main` (kontroll
2026-10-08 cirka 00:40): `cb2c10f`, `619a8ac`, `3ad2c2b`, `a84fc80`,
`e0aecd1`, `ec06c56`. Alla rör enbart test-, modell- och loggfiler — ingen
RTL. Innehåll: `density`/`fields` per omgång (`cb2c10f`), checksumskillnader
kopplade till den rad som faktiskt visas (`3ad2c2b`), att ett kamerafält
ingen levererade i takt inte räknas för en rads ålder (`a84fc80`), logg för
rundorna d1 igen/d2/r4/l1 (`e0aecd1`) och #18 som känt fel i testerna
(`ec06c56`). Grenens logg tillför: r3 (88 gröna, inga nya fynd), d1 (fynd 6 =
pair-join, redan rättat av `aaa3df1` på main), f1 (full geometri; ett
`bench/few_lines` är testets egen gräns, plus #17), d1 igen (grönt efter
rättningen), d2 (frö 126: halvskriven läsning i en bild utan video efter
`LOW` → `BUF`; omkört som känt #17), r4 (frö 385 föll först på en
kontrollrättning, omkört grönt) och l1 (25 fält per frö, 25 gröna, inga nya
fynd). Kampanjen kör fortfarande; fler commits kan tillkomma.

En öppen orakelfråga följer med: d2 frö 126 — efter `LOW` → `BUF` lever
fältminnets lagrad-bitar i block-RAM kvar, så en rad kan läsas halvskriven
medan skrivaren skriver om den; bilderna har ingen video, så inget syns.
`3ad2c2b` kopplar checksumkontrollen till den rad som visas, vilket adresserar
att oraklet tidigare kunde fälla på en SDRAM-läsning som aldrig visas
(`test_fuzz_chain.py:474-480` före ändringen). Detta är underlag för Codex'
R03, inte ett godkännande att merga.

## Test- och byggproveniens

- Core rapporterar 396 test på `7cc4eda`; överlämningen nämnde 394. Root's
  frysta baslinjekörning avgjorde: 396 (se nedan).
- Byggproveniens enligt `gateware/README.md`: M0/M2/M2s/M3 ombyggda
  2026-10-07 ur `f13581c`; M6 ur `330cc9a` (seedtabellen ur `a5b934f`);
  M4 ur `2a23e05`; M1/M1s/M2a ur `62a69be`. M4- och M6-byggena är alltså
  äldre än de två senaste mixerfixarna (`2e0926c`, `aaa3df1`) och
  bekräftar inte byggen av dem.
- Puck `main` `9d2fb57` har submodulen `core/` på `82c4134`, äldre än Core
  `main`. Synkning ägs av root.

## Baslinje, klar

Codex körde den frysta sviten av `7cc4eda` under det gemensamma låset
(logg: `private/notes/overnight_2026-10-07/baseline-suite.log`, arkiv:
samma mapp, `baseline-core-7cc4eda.tar`). Slutresultat 2026-10-08 00:28:

```text
395 passed, 1 xfailed in 5156.04s (1:25:56)
```

Sviten är grön på `7cc4eda`. Xfail är #17-testet
(`test_low_after_switch_shows_whole_fields`, strict), väntat. Testantalet
är därmed verifierat till 396 — samma som båda Core-README anger, inte 394
som överlämningen nämnde. `REVIEW.md` och `AGENTS.md` är uppdaterade med
resultatet.

## Överlämning till root

1. Granska mina tre filer mot `7cc4eda` och checka in dem om de godkänns.
2. Testantalet är avgjort (396, verifierat av baslinjen) — ingen åtgärd.
3. R02–R08 ägs av Codex/Luna enligt `WORKPLAN.md`; denna rapport är mitt
   enda andra bidrag.

## Codex/root: rättelse 2026-10-08 05:33

Påståendet ovan att frö 126:s LOW → BUF-bild saknar video är motbevisat.
En uppspelning med samma kamera-/kontrollfiler och enbart extra
observationsloggning visar video i BUF före första publicerade BUF-fältet.
Alla 72 provtagna aktiva rader har RGB skild från blankbilden. Den
ursprungliga strikta checksumkontrollen behålls. Se
[fyndet och nästa rättningspaket](LOW_BUF_FINDING.md) samt råvärden i
[evidence](evidence/transition-probe-126.json).

Rapportens tidigare beskrivning bevaras som daterad överlämning; den
utgör inte godkännande av `3ad2c2b`. Opus har senare sammanfogat
nattgrenen till fjärrens `main` `0e0bf49`; root granskar den nya
integrationsbasen innan egna ändringar checkas in och pushas.
