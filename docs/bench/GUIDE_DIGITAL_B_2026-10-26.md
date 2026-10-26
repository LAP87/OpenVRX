# Guide: C5VRX direkt in i FPGA:n (digital kanal B), steg för steg

Skriven 2026-10-26 (Fable) på ägarens begäran: vad vi testar och vad som ska byggas och kopplas. Kortversionen av [körschemat](MANDAG_2026-10-26.md); det här räcker för att göra provet när det finns tid, i dag eller en annan dag.

## Vad vi testar

I dag går bilden C5VRX → sex motstånd (DAC) → TVP5150 → Tang → HDMI. Den digitala vägen hoppar över DAC och TVP: C5VRX:s sex databitar (D4–D9) och en 40 MHz-klocka (MTMS-paden, GPIO2) går rakt in i Tangs kontakt J5, och `cvbs_capture` i FPGA:n gör synkseparering och luma. Frågan: hur ren är bilden som C5VRX själv levererar när vår analogväg inte ligger emellan? Bilden är svartvit i det här steget (färg är uppgift 65). Dessutom bekräftar vi Twotoz PR #257 (klockan som byggval), så att han slår ihop den.

**Klart i förväg.** Två firmwarepaket: `bench-logs\c5vrx-clkout-2026-10-24\` (det frysta provet: `388d2d1` plus klockpatch; synkhjulet stängs av med `U`) och `bench-logs\c5vrx-pr257-clock-2026-10-26\` (Twotoz PR #257 med klockvalet på; inget synkhjul). Två bitströmmar: `6b845e8` (det frysta; hjärtslaget blinkar 4 Hz även när B fungerar) och `2fdc82e` (uppgift 69: B:s eget lås; hjärtslaget går till 1 Hz när B låser). Tang sitter i WSL och Fable laddar bitströmmarna.

**Material.** XIAO ESP32-C5 med antenn och USB-kabel; Tang Nano 20K på bänkkortet med HDMI-skärm och USB; kamera och sändare på C5:ans kanal; sju korta trådar (helst under 5 cm, upp till 10 cm går); lödkolv och tunn tråd till MTMS-paden; multimeter; lupp eller mobilkamera för paden.

## Steg för steg

1. **Flasha C5:an.** Chrome, c5vrx.com, fliken C5VRX-5, Local File: `c5vrx5.bin` ur `c5vrx-clkout-2026-10-24\` på adress `0x10000`. Starta om kortet. I konsolen: `T` (spara raden), sedan `U` tills FLYWHEEL står OFF (det sparas). Kameran kan vara av. Alternativet för steg två: `c5vrx5.bin` ur `c5vrx-pr257-clock-2026-10-26\` på samma adress; `T` visar då `SAMPLE_CLOCK` och inget `U` behövs.
2. **Löd klocktråden.** Strömlöst. MTMS-paden sitter på XIAO:ns baksida bland de små testpaddarna. Tunn tråd, lite tenn; kontrollera med multimetern att paden inte kortsluter mot grannpaden eller jord. Det är den enda lödningen.
3. **Koppla sex datatrådar och jord**, fortfarande strömlöst. Trådarna kan tas från kopplingsplattans rader där XIAO:ns stift redan sitter; DAC-motstånden får sitta kvar.

   | Från XIAO | Till Tang J5 | Signal |
   |---|---|---|
   | MTMS-pad (GPIO2) | J5-4 (PIN80) | klocka 40 MHz |
   | D4 | J5-3 (PIN76) | bit 0 |
   | D5 | J5-5 (PIN42) | bit 1 |
   | D6 | J5-6 (PIN41) | bit 2 |
   | D7 | J5-10 (PIN48) | bit 3 |
   | D8 | J5-12 (PIN49) | bit 4 |
   | D9 | J5-13 (PIN86) | bit 5 |
   | GND | J5-2 (GND) | jord |

   TVP-modulen får inte sitta på de stiften samtidigt (den hör till A:s plats, J6). Inga 5 V eller 3,3 V mellan korten, bara signaler och jord. Kontrollera J5:s numrering mot kortets schema innan du löder; tabellen står också i Core `gateware/BRINGUP.md`.
4. **Gör kanal A tyst för första provet.** Dra ur TVP-modulens matning, eller RCA-kabeln från DAC-noden. Då syns bara B. Med bitströmmen `2fdc82e` kan A sitta kvar som ett andra prov: det blir det första A/B-provet.
5. **Ström på båda korten**, egen USB var. Säg till Fable, som laddar `6b845e8/m4_dual_mix_digin.fs`. De första tre sekunderna visar lysdiod 1 och 2 SDRAM-självtestet; därefter betyder lysdiod 2 "rader från B". Kameran på.
6. **Titta efter:** lysdiod 2 tänd; gråskalebild på HDMI med svarta kanter (4:3 i 720p); vifta med handen framför kameran, så att det är levande video och inte fryst fältminne. Låt det gå fem minuter: rullning, frysningar, svarta avbrott, förskjutning. Mobilbilder av skärmen till `bench-logs\2026-10-26-digital-b\`.
7. **Avbrott:** sändaren av 5 s och på igen, tre gånger. Hur lång tid till levande bild?
8. **Steg två:** samma koppling, flasha PR #257-paketet (steg 1, alternativet) och upprepa 6. Fungerar det skriver Fable utkastet till Twotoz, som ägaren skickar.
9. **Steg tre:** bitströmmen `2fdc82e`: lysdiod 0 ska gå från 4 Hz till 1 Hz när B låser. Med TVP A inkopplad igen, kamera i båda, är det första diversity-provet.

## Om det inte fungerar

| Tecken | Kolla först |
|---|---|
| Lysdiod 2 släckt | klocktråden (kontinuitet MTMS → J5-4), jorden, bitordningen (D4 = bit 0 … D9 = bit 5), `T` i konsolen (klockan på, synkhjulet av), att C5:an tar emot kameran (`cn_db` i `T`) |
| Lysdiod 2 tänd men trasig eller ingen bild | bitordningen, trådlängden, att A verkligen är tyst |
| Inget alls, inte ens självtestet | Tangs ström, HDMI-kabeln; säg till så laddas bitströmmen om |

**Återställning.** Tangs bitström ligger bara i SRAM: dra ur USB och kortet startar från flashbilden. C5:an går tillbaka med "Full firmware" i webbflasharen. Inget i provet ändrar något permanent utom tråden på MTMS.

**Fables del.** Tang i WSL, bitströmmarna, M6-loggen före och efter, protokollet i `docs/bench/`, utkastet till Twotoz.
