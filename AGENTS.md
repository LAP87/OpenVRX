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
.venv/bin/python -m pytest -q tests/latency mixer gateware/model gateware/sim gateware/tools   # 368 on Core main, runtime depends on the host
gateware/build.sh m6_puck_proto
```

## Facts to rely on

- Milestone tops in Core: `m0` test pattern, `m1`/`m2` single decoder (M2 via
  SDRAM), `m2a_memtest` (SDRAM memory test), `m3_probe` (wiring check),
  `m4_dual_mix` (two decoders + mixer), `m6_puck_proto` (M4 + RX5808 SPI +
  OLED menu + OSD + UART log). Status table: `gateware/README.md`.
- Video path: `chan_capture` -> async FIFO -> `mix_chan` -> `line_mixer` ->
  `fb_backend` (`fb_sdram` field store with four buffers, or low-latency
  ring + `genlock_timing`).
- Line numbers restart at vertical blanking (two timing codes with V = 1),
  not at the F bit: a TVP5150AM1 holds F at 1 for what it takes to be
  non-interlaced. Which field of an interlaced pair a field is comes from
  its arrival time (`field_phase.v`).
- Mixer: two lines pair when they carry the same line number and arrive
  within 15.8 us. A paired line is decided on per-line HF energy (integer:
  blend when |d|*256 < 38*max, switch when > 64*max); bad lines (sync
  errors, decoder unlocked, forced) lose. A line without a partner is shown
  only from the current channel, or to fill a gap while the channels are in
  step. No wall-clock timeout takes part. `sim/test_mixer.py` compares every
  decision and output word with `gateware/model/line_mixer_ref.py`, on
  fields with a real blanking interval.
- Field store: the buffer a frame shows is chosen in the SDRAM clock domain;
  a frame can show the field being written when the writer is far enough
  ahead. Compared with `gateware/model/fb_ref.py` in `sim/test_fb.py`.
  A missing first line can still cause an unwritten line to be fetched while
  video is active; the model shares this fallback policy. Reproduction and
  the other open capture/status bugs: `docs/reviews/2026-10-06/README.md`.
- TVP5150AM1: XTAL1 absolute max 2.3 V (one crystal per decoder or a 1.8 V
  oscillator); init 00h=00, 04h=FCh, 0Dh=47h, 28h=00 (autoswitch), 02h=20h
  (VCR mode), then 03h=0Dh last (03h is read back at every poll and the list
  is written again if it is wrong); status 88h/89h, 88h bit 4 (lost lock,
  cleared by the read) in the M6 log; I2C address by YOUT7 strap; both decoders share an address, so
  each has its own SDA.
- RX5808 SPI: 25 bits LSB first, address 1, write bit, 20-bit synth register.
- Apicula 0.32: no `signed` arithmetic anywhere (miscompile risk);
  `gateware/tools/test_lvds_bank_inputs.py` must pass after any Apicula upgrade.
- Not published: the LT8618SX 1080p path (init sequence provenance unclear).
- Tang Nano 20K pins 52-56 are SSPI configuration pins (52/53 are also the
  HDMI DDC lines) and are not used. The RX5808 SPI DATA/SEL therefore leave on
  LED pins 19/20 (J6-17/J6-16). Shared-pin risks: `gateware/BRINGUP.md` section 5.
- No single-ended output in the banks of the TMDS pairs (pins 25-42): Apicula
  then packs the TMDS clock pair differently. RESETB is on LED pin 18
  (J6-18). `gateware/tools/test_tmds_bank_outputs.py` guards it; run it after
  any Apicula upgrade.
- Bring-up order: M0, then `m3_probe` (wiring check over USB-UART), `m2a_memtest`
  (SDRAM phase and read sample point), M2, M4 with one decoder, M4 with both,
  M6: `gateware/BRINGUP.md`.
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

- Hardware bring-up on a Tang Nano 20K, in the order above. The measurements
  that simulation cannot replace are listed in `docs/ARBETSPLAN_2026-10-05.md`.
- The CDC handshakes of `fb_backend.v` are proven (`gateware/formal/run.sh`);
  what the proofs do not cover (metastability, SDRAM latency for the line
  buffer, the low-latency ring) is listed in `gateware/formal/README.md`.
- Rev A schematic redrawn by hand in KiCad, then layout.
- RSSI (external I2C ADC or GW5A-25 internal ADC); GW5A-25 port; C5VRX
  (ESP32-C5) receiver comparison with the snow meter.
