# Guide: C5VRX direkt in i FPGA:n (digital kanal B), steg för steg

Skriven 2026-10-26 (Fable) på ägarens begäran: vad vi testar och vad som ska byggas och kopplas. Kortversionen av [körschemat](MANDAG_2026-10-26.md); det här räcker för att göra provet när det finns tid, i dag eller en annan dag.

## Vad vi testar

I dag går bilden C5VRX → sex motstånd (DAC) → TVP5150 → Tang → HDMI. Den digitala vägen hoppar över DAC och TVP: C5VRX:s sex databitar (D4–D9) och en 40 MHz-klocka (MTMS-paden, GPIO2) går rakt in i Tangs kontakt J5, och `cvbs_capture` i FPGA:n gör synkseparering och luma. Frågan: hur ren är bilden som C5VRX själv levererar när vår analogväg inte ligger emellan? Bilden är svartvit i det här steget (färg är uppgift 65). Dessutom bekräftar vi Twotoz PR #257 (klockan som byggval), så att han slår ihop den.

**Klart i förväg.** Två firmwarepaket: `bench-logs\c5vrx-clkout-2026-10-24\` (det frysta provet: `388d2d1` plus klockpatch; synkhjulet stängs av med `U`) och `bench-logs\c5vrx-pr257-clock-2026-10-26\` (Twotoz PR #257 med klockvalet på; inget synkhjul). Två bitströmmar: `6b845e8` (det frysta; hjärtslaget blinkar 4 Hz även när B fungerar) och `2fdc82e` (uppgift 69: B:s eget lås; hjärtslaget går till 1 Hz när B låser). Tang sitter i WSL och Fable laddar bitströmmarna.

**Material.** XIAO ESP32-C5 med antenn och USB-kabel; Tang Nano 20K på bänkkortet med HDMI-skärm och USB; kamera och sändare på C5:ans kanal; sju korta trådar (helst under 5 cm, upp till 10 cm går); lödkolv och tunn tråd till MTMS-paden; multimeter; lupp eller mobilkamera för paden.

## Steg för steg

1. **Flasha C5:an.** Sedan 2026-10-31 (v5.0.573, Twotoz PR #297 efter vår bekräftelse i #256) behövs inget eget bygge: Chrome, c5vrx.com, fliken C5VRX-5, **Full firmware** v5.0.573 eller senare. Starta med sändaren av, vänta ut kalibreringen, kör CALIBRATE i menyn. Sätt sedan EXPERIMENTAL → **Clock Pin D10** på; det gäller från nästa start och sparas. `T` visar klockans begärda och aktiva läge. *Äldre väg (de privata byggena från 10-24/10-26, klockan på MTMS-paden, bit 2 på D6): står i protokollet `DIGITAL_B_RESULTAT_2026-10-27.md`.*
2. **Ingen lödning behövs** med v5.0.573: klockan kommer på headerstiftet D10. (Den gamla vägen krävde en tråd på MTMS-paden på baksidan.)
3. **Koppla sex datatrådar och jord**, fortfarande strömlöst. Trådarna kan tas från kopplingsplattans rader där XIAO:ns stift redan sitter; DAC-motstånden får sitta kvar.

   | Från XIAO | Till Tang (stiftet tryckt på kortet) | Signal |
   |---|---|---|
   | D10 | 80 | klocka 40 MHz (Clock Pin D10 på) |
   | D4 | 76 | bit 0 |
   | D5 | 42 | bit 1 |
   | D3 | 41 | bit 2 (flyttad från D6 i v5.0.573; D6 lämnas lös) |
   | D7 | 48 | bit 3 |
   | D8 | 49 | bit 4 |
   | D9 | 86 | bit 5 |
   | GND | GND | jord |

   TVP-modulen får inte sitta på de stiften samtidigt (den hör till A:s plats, J6). Inga 5 V eller 3,3 V mellan korten, bara signaler och jord. Gå efter stiftnumren tryckta på Tang-kortet (det är FPGA-stiften), inte efter en räknad position i kontakten: på bänken 2026-10-28 visade sig det tredje stiftet i raden vara jord (0 Ω mot GND), och D4 satt där i två dagar. Tabellen står också i Core `gateware/BRINGUP.md`.
4. **Gör kanal A tyst för första provet.** Dra ur TVP-modulens matning (eller hela modulen). Bara RCA-kabeln räcker inte: en TVP5150 utan insignal frilöper och ger en helt platt blå ruta, och blandaren väljer den kanal vars rader har minst högfrekvent energi, så den platta rutan vinner mot B:s bild (grå ruta med svarta kanter i gråskala). Med bitströmmen `2fdc82e` kan A sitta kvar som ett andra prov: det blir det första A/B-provet.
5. **Ström på båda korten**, egen USB var. Säg till Fable, som laddar `6b845e8/m4_dual_mix_digin.fs`. De första tre sekunderna visar lysdiod 1 och 2 SDRAM-självtestet; därefter betyder lysdiod 2 "rader från B". Kameran på.
6. **Titta efter:** lysdiod 2 tänd; gråskalebild på HDMI med svarta kanter (4:3 i 720p); vifta med handen framför kameran, så att det är levande video och inte fryst fältminne. Låt det gå fem minuter: rullning, frysningar, svarta avbrott, förskjutning. Mobilbilder av skärmen till `bench-logs\2026-10-26-digital-b\`.
7. **Avbrott:** sändaren av 5 s och på igen, tre gånger. Hur lång tid till levande bild?
8. **Steg två:** samma koppling, flasha PR #257-paketet (steg 1, alternativet) och upprepa 6. Fungerar det skriver Fable utkastet till Twotoz, som ägaren skickar.
9. **Steg tre:** bitströmmen `2fdc82e`: lysdiod 0 ska gå från 4 Hz till 1 Hz när B låser. Med TVP A inkopplad igen, kamera i båda, är det första diversity-provet.

## Om det inte fungerar

| Tecken | Kolla först |
|---|---|
| Lysdiod 2 släckt | klocktråden (kontinuitet D10 → stift 80), att Clock Pin D10 är aktiv i `T` (kräver omstart efter valet), jorden, bitordningen (D4, D5, D3, D7, D8, D9 = bit 0…5), att C5:an tar emot kameran (`cn_db` i `T`) |
| Lysdiod 2 tänd men trasig eller ingen bild | bitordningen, trådlängden, att A verkligen är tyst |
| Inget alls, inte ens självtestet | Tangs ström, HDMI-kabeln; säg till så laddas bitströmmen om |

**Återställning.** Tangs bitström ligger bara i SRAM: dra ur USB och kortet startar från flashbilden. C5:an går tillbaka med "Full firmware" i webbflasharen. Inget i provet ändrar något permanent utom valet Clock Pin D10 i C5:an (stäng av det, starta om och flytta bit 2-tråden tillbaka till D6 för den gamla kopplingen).

**Fables del.** Tang i WSL, bitströmmarna, M6-loggen före och efter, protokollet i `docs/bench/`, utkastet till Twotoz.
