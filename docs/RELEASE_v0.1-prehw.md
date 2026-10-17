# v0.1-prehw: baslinjen före hårdvaran (2026-10-17)

Den annoterade taggen `v0.1-prehw` finns i alla tre repona. Ett bänkresultat hänvisar till den ("M0 ur v0.1-prehw på skärm X"), inte till "main i oktober". Det finns inga GitHub-releaser och inga bitströmmar att ladda ner: bygg ur taggen och jämför med tabellen under "Byggt".

| Repo | Taggen pekar på | Innehåll |
|---|---|---|
| OpenVRX-Core | `ff2efce` | gateware, modeller, test, `gateware/BRINGUP.md` |
| OpenVRX-Puck | `c80ed57` | rev A-schemat (SKiDL) och KiCad-projektet utan routning; `core/` pekar på `ff2efce` |
| OpenVRX (navet) | sammanslagningen som för in det här dokumentet på `main` | planer, underlag, [MATPROTOKOLL.md](MATPROTOKOLL.md) |

**Inget är kört på hårdvara.** Simulerat betyder mot en modell eller ett facit i Core-sviten. Byggt betyder syntes och place-and-route med yosys, nextpnr-himbaechel och Apicula, med timing efter routning; det säger ingenting om elektriska marginaler på kortet.

## Simulerat

Core-sviten på `d3d9753`, samma källor som taggen: 772 test, 769 gröna och 3 strikta xfail för öppna fynd (Core #21–#23), en process per simuleringstest, ingen delad byggkatalog. I sviten ingår de formella bevisen (tio bevis och sjutton negativa kontroller som ska ge motexempel; vad de inte täcker står i Core `gateware/formal/README.md`). Störningskampanjen kördes separat: 2 032 frön genom hela kedjan, nio fynd, alla rättade (Core `gateware/sim/FUZZ_2026-10-07.md`). Puck på `c80ed57`: 6 test gröna mot Core `ff2efce`, ERC utan fel, 126 delar.

| Block | Simulerat mot | Avgörs först på bänken |
|---|---|---|
| BT.656-mottagning, radnumrering | `model/bt656.py` (`test_bt656_rx.py`) | riktiga TVP5150AM1: lås, fältfas, vad de gör utan signal (MATPROTOKOLL blad 3, 4) |
| Dekoderstyrning och I2C | I2C-slavmodeller, `model/i2c_ref.py` (`test_tvp_ctrl.py`, `test_i2c_master.py`) | om registervärdena ur databladet ger bild; TV mot VCR (blad 12, 13) |
| Mixern | `model/line_mixer_ref.py`, varje beslut och ord (`test_mixer.py`); störda strömmar genom hela kedjan (`test_fuzz_chain.py`) | om radvalet hjälper på riktig radio (blad 6, 11, 15) |
| Fältminnet `BUF` i SDRAM | `model/fb_ref.py` och en SDRAM-modell med timing (`test_fb.py`, `test_sdram.py`) | SDRAM-fas och läspunkt (M2a, blad 2); bild via fältminnet (blad 5) |
| `LOW` och genlocken | `model/ll_ring_ref.py`, formella bevis (`test_genlock.py`, `test_ll_ring.py`) | vad skärmar, goggles och glasögon tar (blad 10, 14, 16) |
| DVI och HDMI-läget | TMDS- och paketavkodare i Python (`test_video.py`, `test_hdmi.py`) | bild på en skärm (blad 1); ingen skärm har sett HDMI-läget |
| RSSI, SCAN, sparade inställningar | ADS1115-modell, `rssi_ref.py`, `chan_scan_ref.py`, flashmodell med `flash_store_ref.py` | trösklarna för RSSI, skanning på riktiga kanaler, skrivning i kortets flash (blad 17–19) |
| Meny, OLED, OSD, RX5808-SPI | `model/vtx_channels.py`, OLED-bilden ur I2C-skrivningarna (`test_puck_ui.py`, `test_osd.py`) | menyn på kortet; om omskrivning av RX5808 stör bilden (blad 7) |

## Byggt ur taggen

Uppstartsordningens fem toppar (Core `gateware/BRINGUP.md` avsnitt 2) med standardval, byggda 2026-10-17 ur en ren utcheckning av `ff2efce`; manifestet bredvid varje bitström anger commit, byggindata och verktygsversioner. Verktyg: yowasp-yosys 0.69.0.0.post1233, yowasp-nextpnr-himbaechel-gowin 0.11.1.0.post826, Apicula 0.32. Alla klockor över kravet 75 MHz efter routning; I/O-registren i I/O-cellerna för M2a, M4 och M6; M6 packad med `--mspi_as_gpio`; HDMI-paren i M4 och M6 packas som i M0 (`tools/tmds_fuses.py`).

| Steg | Topp | Seed | LUT4 | BSRAM | Lägsta klocka, MHz | SHA-256 för bitströmmen |
|---|---|---:|---:|---:|---|---|
| M0 | `m0_testpattern` | 0 | 787 | 0 | 158,18 (pixel) | `dcc860e389311c8799b7cfd51dbe928d161c3a66881382942292ec91123d76c3` |
| M3 | `m3_probe` | 0 | 2 690 | 0 | 119,35 (dekoder A:s klocka) | `11ce8ed4dff41ea304797c0f3199f3f29ea8e0220b4bcfe7207dbccbf88a524d` |
| M2a | `m2a_memtest` | 0 | 2 373 | 0 | 81,84 (SDRAM) | `0a58ea6c343733af65df18a32135bac38916215a297763140ae110efa86819b6` |
| M4 | `m4_dual_mix` | 0 | 5 810 | 29 | 115,06 (pixel) | `225892051890657aedc06b61c0d5a48324313823fa69ed6b48aec4b9f4c739a4` |
| M6 | `m6_puck_proto` | 2 | 13 259 | 29 | 91,70 (SDRAM) | `948ccb0c46e5e41c70260438855c33fc6c2f35ce18bb866c216d4266b9ed4fb0` |

Varje topp byggdes två gånger ur taggen med samma bitström, och M4 och M6 är bit för bit lika med byggena ur granskningens sammanslagning `8a71a0a` (samma byggindata och verktyg).

Bygg och kontrollera på samma sätt:

```sh
git clone --recurse-submodules --branch v0.1-prehw https://github.com/LAP87/OpenVRX-Puck
cd OpenVRX-Puck/core
python -m venv .venv && .venv/bin/pip install -r requirements.txt
gateware/build.sh m0_testpattern
.venv/bin/python gateware/tools/build_manifest.py verify gateware/build/m0_testpattern.build.json --root .
```

Med samma verktygsversioner och seed bör bitströmmen bli densamma som i tabellen; jämför med `sha256sum gateware/build/m0_testpattern.fs`. Med andra versioner blir placeringen en annan, och då gäller timingrapporten i det egna manifestet.

Inte byggda ur taggen: M1, M1s, M2 och M2s (Moneagle-vägen, inte i uppstartsordningen) och byggvalen `HDMI=1` och `VINTERP=1`. Deras senaste byggen och siffror står i Core `gateware/README.md`, "Status".

## Inte provat

Allt på hårdvara, i den ordning `BRINGUP.md` tar det: M0 på skärmar, M3-proben med båda dekodrarna, minnestestet M2a, M4 med en och sedan två dekodrar, M6 med meny, logg, RSSI, SCAN och sparade inställningar. Mätbladen är [MATPROTOKOLL.md](MATPROTOKOLL.md) blad 1–19 och materialet [MATERIAL_UPPSTART.md](MATERIAL_UPPSTART.md). Därtill, utan att vara ett eget steg:

- HDMI-läget (`HDMI=1`) mot en riktig skärm, och om skärmen tar fullt omfång (Core #23).
- Flashens datablad (XTX) är inte läst; kommandona kommer ur openFPGALoaders källkod och Sipeeds schema.
- RX5808-modulernas RSSI-omfång och utgångsimpedans.
- Rev A-kortet: inte routat, inte beställt.

## Öppna beslut

| Fråga | Läge | Var |
|---|---|---|
| Ett eller två bildlägen (`BUF`, `LOW`) | Båda behålls tills bänken talat; inget nytt byggs bara för `LOW` (ägarens svar 2026-10-12) | [BESLUT_2026-10-12.md](BESLUT_2026-10-12.md) punkt 1 |
| 1080p för XR-glasögon | Senare, när glasögon finns; M0 in i bryggan och glasögonen blir första mätningen | beslut 6, navet #1, [UTGANG_1080P_2026-10.md](../research/UTGANG_1080P_2026-10.md) |
| Testskärmar och glasögon att köpa | Rapportens smala och fulla uppsättning är obesvarade | [ARBETSPLAN_HEMMA_2026-10-12.md](ARBETSPLAN_HEMMA_2026-10-12.md) punkt 5 |
| Rev A: beställning | Efter M4 på moduler. Routningen är inte påbörjad; temperaturklass, PLL-filter och de andra anteckningarna i Puck #3 väntar på nästa schemavarv | BESLUT, "Redan avgjort"; Puck #3 |
| RSSI-varningens marginal | Marginal eller hysteres mellan mottagarna; trösklarna sätts på bänken | Core #21 |
| HDMI-läget och omfånget | Efter bänken: mät gråskalan med DVI och HDMI och läs skärmarnas EDID; tar en viktig skärm inte fullt omfång, sänd begränsat omfång. EDID läses inte av kortet (DDC ligger på konfigurationsstift) | Core #23 |

Två öppna fynd ur granskningen 2026-10-14 är inte ägarens beslut utan arbete: att SCAN avgör lika rena kanaler på tabellordning (Core #22) och att radbuffertbeviset inte täcker `VINTERP` (Core #24).
