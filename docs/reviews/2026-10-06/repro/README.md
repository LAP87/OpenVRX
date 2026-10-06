# Reproduktioner för granskningen 2026-10-06

Kör från mappen som innehåller `OpenVRX` och `OpenVRX-Core`. Core behöver Git-historiken för `e5585ba`, Icarus Verilog och sin Python-miljö (`pytest` behövs när den befintliga FB-testhjälparen importeras).

```sh
OpenVRX-Core/.venv/bin/python OpenVRX/docs/reviews/2026-10-06/repro/run.py --core OpenVRX-Core
```

Körningen är seriell, använder frysta källfiler från Git och lämnar resultat i en unik ignorerad `repro/build/review-*/`-mapp. Hela körningen inklusive tre fältminnessimuleringar tar omkring en minut på granskningsdatorn. `--skip-fb` kör bara de små Icarus-fixturerna.

För kontrollen mot morgonens Core-version behöver även den commiten finnas lokalt:

```sh
git -C OpenVRX-Core fetch origin codex/handoff-2026-10-06
OpenVRX-Core/.venv/bin/python OpenVRX/docs/reviews/2026-10-06/repro/run.py --core OpenVRX-Core --control-ref 1a1e5c7fb7b8f9a991e27cd70f871a923f42ce7b
```

`--ref` väljer en annan Core-commit. Formal-grenens snapshot `53e5ab2da0002ee19d4b8160f46590e6628b1c3f` kan också användas; runnern tar med den extraherade `cdc_sync.v` när den finns. Ingen gren behöver checkas ut eller ändras.

| Fixtur | Vad den kontrollerar |
|---|---|
| `short_active.v` | Fyra hela BT.656-rader, sedan 359-ordsrad med korrekt EAV-avstånd; ringens sista ord blir gammalt |
| `tvp_partial_nack.v` + `i2c_completion_stub.v` | Riktig TVP-styr-FSM; hel positiv poll, sedan 88h-NACK med efterföljande ACK |
| `ll_payload.v` | Riktig LOW-backend; payload 3 mottas som 2 utan paus, som 3 med paus |
| `i2c_held_low.v` | Riktig I²C-master; frigiven SCL ger avslut, fast låg SCL stannar |
| `genlock.v` | Den rättade minsta bildperioden, resetvärden borttagna från mätningen |
| Repots `test_fb.py`-hjälpare | Hela fält som kontroll; borttagen första rad med RT av/på; aktiv video får okända line-buffer-ord |

Exit 0 betyder **observationerna reproducerade**, inklusive kända fel. Fixturerna ska inte användas som gröna acceptanstester för en rättad version. Gör då en regression med ett korrekt facit och en avsiktligt felaktig variant som fälls.

De skalade fältfallen prövar RTL-sekvenser utan fysisk kamera, RF, kabel eller skärm. I²C-stubben prövar pollhantering efter transaktionsresultat. Den är inte en bussmodell och ersätter ingen elektrisk verifiering.
