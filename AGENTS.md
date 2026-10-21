# AGENTS.md: OpenVRX brief for contributors and coding agents

## What this is

An analog 5.8 GHz FPV video receiver family: two receivers, two TVP5150AM1
decoders, an FPGA that pairs and mixes the two pictures line by line, HDMI
out. Stage: early bring-up. **M0 test-pattern output and a corrected bounce have
run on a Tang Nano 20K (2026-10-20), including a user-confirmed flash power cycle.**
The flashed image was a private bench patch; the same fix is in Core main `b440ece` (task 46). SDRAM read point 5 is clean on the board
(2026-10-21) once the I/O-cell register option is off; that option is off by default in Core main `4aa41f2`. TVP/RF and the full receiver
remain unverified. Start with [the bench handoff](docs/bench/HANDOFF_CLAUDE_2026-10-20.md).

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
.venv/bin/python gateware/tools/run_suite.py --quick   # before every commit: the stored list of fast tests (about 4 min)
.venv/bin/python gateware/tools/run_suite.py           # before every merge: whole suite, one process per simulation test, ten at a time (about 20 min)
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
  errors, decoder unlocked, forced) lose. A pair is decided on the partner
  when the current channel has no line in the output field. A line without
  a partner is shown only from the current channel, or to fill a gap while
  the channels are in step. A line is stored only when its 360 words
  arrived in order since the last marker; a line bad on both receivers is
  left out unless the line before it was left out too (two or more in a row
  are shown: noise beats a still picture). No wall-clock timeout takes
  part. `sim/test_mixer.py` compares every decision and output word with
  `gateware/model/line_mixer_ref.py`, on fields with a real blanking
  interval.
- Field store: the buffer a frame shows is chosen in the SDRAM clock domain;
  a frame can show the field being written when the writer is far enough
  ahead. Compared with `gateware/model/fb_ref.py` in `sim/test_fb.py`.
  A line counts as stored only when its word 0 was taken in the same field:
  the line the writer joins in the middle after reset or LOW is not stored
  (Core 0da655d, C3 campaign seeds 1437/1445).
  A missing line with no line above it and no stored fallback line is
  written black (Y 16, Cb/Cr 128) without reading the SDRAM in BUF mode
  (review 2026-10-06, F3). Core #17 is fixed: LOW video requires a live
  genlock and a LOW trigger after joining the writer. Never initialized
  ring slots show black; initialized slots retain their older data.
- TVP5150AM1: XTAL1 absolute max 2.3 V (one crystal per decoder or a 1.8 V
  oscillator); init 00h=00, 04h=FCh, 0Dh=47h, 28h=00 (autoswitch), 02h=30h
  (TV default; M6 can request 20h/VCR for both decoders through the menu;
  compare both on the bench before fixing a choice), then 03h=0Dh last (03h is read back at every poll and the list
  is written again if it is wrong); status 88h/89h, 88h bit 4 (lost lock,
  cleared by the read) in the M6 log; I2C address by YOUT7 strap; both decoders share an address, so
  each has its own SDA. A poll round (88h, 89h, 03h) counts only as a
  whole: one NACK invalidates the decoder's status until the next whole
  round (review 2026-10-06, F2).
- I2C (`i2c_master.v`): one transaction writes up to 256 data bytes after
  the register address, and the master gives up when a slave stretches SCL
  longer than 10 ms (STRETCH_MAX), ending with NACK and `stuck`, so a
  held-low SCL cannot block the shared bus for good.
- The M6 log line carries, per channel, the snow value (mean line HF
  energy, the mixer's own metric) and a noise count (luma samples outside
  16-235 over the last 1024 lines). Whether that count separates receiver
  noise from picture content needs measurement on a real signal. The mixer
  does not use the noise count. The
  line also ends with a lost-lock flag per decoder. `tools/snowlog.py`
  reads the 85-byte line with the RSSI fields (2026-10-13), the 62-byte line with a
  T/V token and the legacy 60-/57-/43-byte forms.
- RX5808 SPI: 25 bits LSB first, address 1, write bit, 20-bit synth register.
- Apicula 0.32: no `signed` arithmetic anywhere (miscompile risk);
  `gateware/tools/test_lvds_bank_inputs.py` must pass after any Apicula upgrade.
- Not published: the LT8618SX 1080p path (init sequence provenance unclear).
- Decoder SCLK pins 77/80 are dedicated clock inputs (GCLKT) and carry no
  BUFG flag: with three BUFGs nextpnr left `clocks.clk_27` unroutable in M6
  for some seeds (Core `gateware/README.md`, "Klockroutningen, 2026-10-12").
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
  that must give a counterexample from reset. The CDC handshakes of
  `fb_backend.v` and `fb_display.v` are proven through `rtl/cdc_sync.v`;
  the low-latency trigger's line count crosses through `toggle_tx`, which
  holds the value from flip to flip and flips at most every 16 clocks.
  What the proofs do not cover (metastability, SDRAM latency for the line
  buffer, the low-latency ring, reset mid-run) is listed in
  `gateware/formal/README.md`.

## How to work here

- Verify, do not assume: every RTL change gets a simulation against a model,
  and models get negative controls (a deliberately broken case must fail).
- Before every commit in Core run the quick suite
  (`gateware/tools/run_suite.py --quick`: the tests named in
  `gateware/tools/quick_tests.txt`, chosen by measured time, about four
  minutes). Before every merge to `main` run the full suite (`run_suite.py`
  without `--quick`) on the commit being merged, and the builds the change
  touches. When `--quick` refuses because the list names a test that is no
  longer collected, write a new list from the last full run with
  `run_suite.py --pick-quick 300`.
- Run one heavy job at a time under the shared build lock: one suite run,
  quick or full (`gateware/tools/run_suite.py`, which runs its own processes
  ten at a time and fails when two tests share a build directory), or one
  place-and-route.
  The development machine has frozen under parallel builds.
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
- No sourcing in these repositories: no shop names, shop links, prices or
  stock status in design files, BOMs or plans. Manufacturer part numbers,
  distributor part numbers used as identifiers (LCSC C-numbers) and links to
  the manufacturer's product page or datasheet are fine. A research note may
  quote a price if it says the date (owner's decision 2026-10-12).
- Licence: everything here is CERN-OHL-S-2.0, the same as the OpenDrone-hw
  repositories (owner's decision 2026-10-12). Take code from elsewhere only
  under a compatible permissive licence (Apache-2.0, MIT, BSD, CERN-OHL),
  never GPL, and name the source in the file header (see rtl/sdram_burst.v).
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

- The plan: [docs/ARBETSPLAN.md](docs/ARBETSPLAN.md) is the only living one
  (state, rules, the owner's decisions with dates, open tasks, what needs the
  board). The dated plans and night passes in `docs/` are history.
- The baseline before hardware is the tag `v0.1-prehw` in all three
  repositories (Core `ff2efce`, Puck `c80ed57` pinning it):
  [docs/RELEASE_v0.1-prehw.md](docs/RELEASE_v0.1-prehw.md).
- Hardware bring-up on a Tang Nano 20K, in the order above. The measurements
  that simulation cannot replace are the sheets of `docs/MATPROTOKOLL.md`.
- Which top is built from which commit, and the figures after routing, are in
  the status of Core `README.md` and `gateware/README.md`. Earlier receipts
  (C1, C2, C3, recovery rounds) are in [STATUS.md](docs/overnight/2026-10-08/STATUS.md).
- Core #17/#18 were fixed under the owner's 2026-10-08 decisions. The
  mixer output F bit changes when the next visible output field consumes
  a pending boundary; it is not the decoder's F bit. The existing takeover
  regression and LOW startup tests
  are strict passing tests, not pending xfails.
- The accepted visible-field boundary fix keeps the output-F transition
  pending across a field that emits no line and applies it at the next
  visible output field. An empty or omitted field does not consume its own
  toggle. The decoder's F bit remains separate; this is not hardware evidence.
- OVN-F1's historical seed-126 window is fixed in the tested replay.
  Accepted C3 also fixes the scaled fallback/read-start oracle and rejects
  reads from never initialized LOW ring slots. Strict read checksums and
  display-coverage thresholds remain. All LOW -> BUF phases and hardware
  behaviour are still unverified; see the dated evidence in
  [LOW_BUF_FINDING.md](docs/overnight/2026-10-07/LOW_BUF_FINDING.md).
- The C3 260-seed campaign is complete (2026-10-12): 257 seeds pass with
  their original stimulus (199 on `db0035f`, 58 on `0da655d`), three (1345,
  1434, 1444) pass once four clean fields follow it (`--recovery-fields 4`),
  the 144-line threshold unchanged. The remaining 60 found one RTL fault in
  the field store, fixed in `0da655d`. Log: Core
  `gateware/sim/FUZZ_2026-10-07.md`. Seed 1249's old failure is preserved
  history, with a separately accepted checker correction.
- C2's TV/VCR filter menu is integrated. The two decoders reconcile the
  requested value after paired polls, retaining an in-flight value/SDA lane
  and retrying after NACK. The OLED/OSD and 62-byte UART row show the requested
  mode, not a register readback. Focused verification passed 56 tests and two
  subtests; nine old BUS/parser guards fail for the expected semantic reasons.
  TV/VCR picture quality and lock behaviour on a real signal are unmeasured.
- Build verification, campaign changes and remaining branch research are
  recorded in `docs/overnight/2026-10-08/STATUS.md`. Branch
  results do not establish acceptance of main. Verify the build manifest
  against the sources and artifacts before flashing.
- I/O registers in the I/O cells: the default for M2, M2s, M2a, M4 and M6
  since 2026-10-12 (owner's decision; `IOREG=0/1` overrides). All 32 DQ input
  registers sit in the cells, the DQ outputs and the SDRAM clock do not. The
  memory test on the board decides phase and read point.
- Rev A schematic redrawn by hand in KiCad, then layout.
- RSSI (external I2C ADC or GW5A-25 internal ADC); GW5A-25 port; C5VRX
  (ESP32-C5) receiver comparison with the snow meter.
