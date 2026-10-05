# AGENTS.md: OpenVRX brief for contributors and coding agents

## What this is

An analog 5.8 GHz FPV video receiver family: two receivers, two TVP5150AM1
decoders, an FPGA that pairs and mixes the two pictures line by line, HDMI
out. Stage: planned / early design. **Nothing has run on hardware.**

| Repo | Role |
|---|---|
| `OpenVRX` (this) | Hub: overview, research notes (`research/`, Swedish), bench notes (`docs/`), [REVIEW.md](REVIEW.md) |
| `OpenVRX-Core` | Gateware (Verilog, Tang Nano 20K / GW2AR-18), Python reference models, cocotb tests |
| `OpenVRX-Puck` | The puck product: rev A decoder-board schematic (SKiDL script), concept docs; Core as submodule in `core/` |

## Getting a working tree

```sh
git clone --recurse-submodules https://github.com/LAP87/OpenVRX-Puck
git clone https://github.com/LAP87/OpenVRX
cd OpenVRX-Puck/core
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# Icarus Verilog 12 on PATH, or built into core/.tools/iverilog/
.venv/bin/python -m pytest -q tests/latency mixer gateware/model gateware/sim gateware/tools   # 78 tests, ~12 min
gateware/build.sh m6_puck_proto
```

## Facts to rely on

- Milestone tops in Core: `m0` test pattern, `m1`/`m2` single decoder (M2 via
  SDRAM), `m4_dual_mix` (two decoders + mixer), `m6_puck_proto` (M4 + RX5808
  SPI + OLED menu + OSD + UART log). Status table: `gateware/README.md`.
- Video path: `chan_capture` -> async FIFO -> `mix_chan` -> `line_mixer` ->
  `fb_backend` (SDRAM triple buffer, or low-latency ring + `genlock_timing`).
- Mixer rule (integer): blend when |d|*256 < 38*max, switch when > 64*max of
  per-line HF energy; bad lines (sync errors, decoder unlocked, forced) lose.
  The line-level timing model is `gateware/model/line_mixer_ref.py`. Tests
  cover VBI, lag, loss, recovery and constant F; no full M4/M6 hardware acceptance.
- Pairing waits 4096 system cycles (63.2 us at 64.8 MHz). Channel expiry is
  262144 cycles (4.05 ms), including VBI. Whole lines only; stale output keys
  are dropped. A captured decoder fault survives recovery, and current faults
  also block queued lines. Epoch comparisons use an 8-bit modular counter.
- TVP5150AM1: XTAL1 absolute max 2.3 V (one crystal per decoder or a 1.8 V
  oscillator); init 00h=00, 03h=0Dh, 0Dh=47h; status 88h/89h; I2C address by
  YOUT7 strap; both decoders share an address, so each has its own SDA.
- RX5808 SPI: 25 bits LSB first, address 1, write bit, 20-bit synth register.
- Apicula 0.32: no `signed` arithmetic anywhere (miscompile risk);
  `gateware/tools/test_lvds_bank_inputs.py` must pass after any Apicula upgrade.
- Not published: the LT8618SX 1080p path (init sequence provenance unclear).
- Tang Nano 20K pins 52-56 are SSPI configuration pins (52/53 are also the
  HDMI DDC lines) and are not used. The RX5808 SPI DATA/SEL therefore leave on
  LED pins 19/20 (J6-17/J6-16). Shared-pin risks: `gateware/BRINGUP.md` section 5.
- Bring-up starts with M0 HDMI, then `m3_probe` (wiring check over USB-UART),
  a separate SDRAM acceptance test (still to be implemented), M4 A, M4 A+B, M6:
  `gateware/BRINGUP.md`.
- Formal proofs: `gateware/formal/run.sh`; every proof has a negative control
  that must give a counterexample from reset.

## How to work here

- Verify, do not assume: every RTL change gets a simulation against a model,
  and models get negative controls (a deliberately broken case must fail).
- Run one heavy job (simulation suite, place-and-route) at a time; the
  development machine has frozen under parallel builds.
- Keep numbers honest: say "simulated", "built" or "measured on hardware",
  never blur them. Update `gateware/README.md` status and test counts.
- Comments and code in English; long-form design notes are in Swedish.

## Writing anything a person will read

READMEs, issues, PR descriptions, review replies, Discord posts, commit
messages, menu and OSD text. Be pedantic about these; they must not read
like AI output.

- Say the one thing the reader needs, then stop. If a paragraph can be cut
  without losing a fact, cut it.
- Facts over adjectives. "Locks within one output line, 0.1-0.8 ms latency"
  instead of "robust, cutting-edge, ultra-low latency".
- No filler and no stock phrases: no "comprehensive", "seamless", "leverage",
  "it's worth noting", "in summary", "let's dive in", no closing recap of
  what was just said.
- No info dumps. Do not list everything you know; pick what matters for this
  reader and link the rest.
- No walls of text. Short paragraphs, a table when comparing, a list only when
  the items really are a list. Headings only where they help someone find
  something.
- Every claim is checkable: name the file, the test, the measurement or the
  datasheet page. Mark what is unverified as unverified.
- Same terms everywhere: a thing keeps one name across files and repos.
- Read it back as the person receiving it before you post. If it sounds like
  a press release or a chatbot, rewrite it.
- No sourcing (shops, prices, purchase links) in these repositories.
- Before a part goes into a schematic or BOM, check its lifecycle status
  (Active / NRND / EOL) and named successor at the manufacturer, and recheck
  the whole BOM before ordering boards. Parts go quietly obsolete (example from
  OpenDrone #proposals: Johanson 2450AT18A100E -> 2450AT18A0100001E). The
  TVP5150AM1 is the part rev A depends on most.
- Antennas for any on-board ESP32-C5 (C5VRX) must cover 5.8 GHz: it receives
  the video through its Wi-Fi radio. A 2.4 GHz-only chip antenna will not do.
- Do not commit datasheets, scraped web pages or third-party code without a
  licence that allows it; cite sources instead.

## Open work (see REVIEW.md for the risks)

- SDRAM timing model and memory-test top; buffer ownership across clocks;
  genlock minimum frame period; I2C timeout and decoder reinitialisation.
- Hardware bring-up: M0 -> M3 -> memory test -> M4 A -> M4 A+B -> M6.
  The original M2 top taps a Moneagle decoder and lacks module init/reset.
- Formal checks (SymbiYosys) of the CDC handshakes, async FIFO and genlock.
- Rev A schematic redrawn by hand in KiCad, then layout.
- RSSI (external I2C ADC or GW5A-25 internal ADC); GW5A-25 port; C5VRX
  (ESP32-C5) receiver comparison with the snow meter.
