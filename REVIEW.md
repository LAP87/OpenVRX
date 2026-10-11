# Invitation to adversarial review

OpenVRX has never run on hardware. Passing our own simulations is not enough:
the models and the RTL come from the same understanding, so a misread
datasheet can be wrong in both. We are asking
for people to **prove us wrong** before we spend money on boards.

The most useful replies are a concrete failure: "this breaks when X, because
Y, see datasheet page Z". Opinions are welcome too, but a broken case beats a
vague concern.

## How to check our work

```sh
git clone --recurse-submodules https://github.com/LAP87/OpenVRX-Puck
cd OpenVRX-Puck/core
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# Icarus Verilog 12 on PATH (or built into .tools/iverilog)
.venv/bin/python -m pytest -q tests/latency mixer gateware/model gateware/sim gateware/tools
gateware/build.sh m6_puck_proto          # bitstream for a Tang Nano 20K
```

## Where we would most like to be wrong

Ordered from "most likely broken" to "probably fine".

1. **Does line mixing actually help?** The selection rule (per-line HF energy,
   sync errors, hysteresis) was tuned on synthetic noise. Real receiver noise
   near the range limit may not look like that, and blending two decoders'
   lines may smear more than it helps. A count of luma samples outside
   16-235 has been logged in M6 since 2026-10-07; whether it separates
   receiver noise from picture content needs measurement on a real signal.
   (`OpenVRX-Core: gateware/rtl/line_mixer.v`,
   `mixer/`)
2. **Pairing lines from two decoders.** Each TVP5150 runs on its own crystal
   and clock; lines with the same number are paired within an arrival
   window after async FIFOs, and field counters decide output admission.
   The 2026-10-07 fuzz campaign (`gateware/sim/FUZZ_2026-10-07.md`)
   ran two disturbed streams through the whole chain in simulation and fixed
   what it broke: run-on lines, field phase measured from reset, a mixer
   rule that froze the output when a receiver returned, and pairs decided on
   a channel with no line in the output field. Core #17/#18 were fixed on
   2026-10-08. The accepted visible-boundary fix keeps the output-F
   transition pending across a field that emits no line, then applies it at
   the next visible output field; omitted fields do not each consume a toggle.
   Still unmeasured: the phase between two real decoders. (`mix_chan.v`, `line_mixer.v`)
3. **TVP5150AM1 bring-up.** Register values (00h, 04h, 0Dh, 28h, 02h, 03h)
   and status reads (88h/89h) come from the datasheet only. A poll round now
   counts only as a whole, and a slave holding SCL low times out after 10 ms;
   both are simulated against slave models. Pin strapping, reset timing, crystal
   load and the 2.3 V XTAL1 limit are in the rev A schematic. (`tvp_ctrl.v`,
   `i2c_master.v`, `OpenVRX-Puck: design/rev_a/`)
4. **SDRAM on the Tang Nano 20K.** The model is timing-aware (datasheet
   times, protocol checks, selectable read sample point) and `m2a_memtest`
   is built, but the DQ sampling phase and the clock phase are still checked
   against the model only, not the real embedded SDRAM. The memory test on
   the card decides. (`sdram_burst.v`, `clocks_sdram.v`, `top/m2a_memtest.v`)
5. **Clock-domain crossings.** The async FIFO and the `fb_backend.v` /
   `fb_display.v` handshakes have k-induction proofs and negative controls
   (`gateware/formal/run.sh`, `gateware/formal/README.md`). Toggle and level
   crossings use two free clocks; the sender uses one clock and the
   line-buffer-slot proof uses the display timing model. Not
   proven: metastability beyond two stages, SDRAM latency for the line
   buffer, the low-latency ring, reset mid-run. Are the proof's assumptions
   (registers start at reset, free clocks, 27-108 MHz against 74.25 MHz) the
   right ones?
6. **Low-latency mode.** The 720p output is genlocked to the input fields:
   frames alternate 750/751 lines (NTSC) and the first line waits for the
   input. Will real sinks (TVs, XR glasses, capture cards) accept a varying
   vertical total? The minimum frame duration is now bounded and proven.
   Core #17 now requires live genlock and a trigger before LOW video. Slots
   never completely initialized since reset show black; initialized slots
   retain older data. Real sink acceptance and all switch phases remain
   unmeasured.
   (`genlock_timing.v`, `fb_backend.v`, `fb_display.v`)
7. **Open-toolchain pitfalls.** Apicula has miscompiled signed comparisons in
   other projects (we removed all `signed` arithmetic), and newer Apicula packs
   single-ended inputs beside a true-LVDS output as LVDS receivers (we test
   that our version does not: `gateware/tools/test_lvds_bank_inputs.py`).
   What else bites on GW2AR-18?
8. **Shared pins on the Tang Nano 20K.** Every ordinary header GPIO is used.
   Some also reach other parts of the board (HDMI hot-plug and CEC, the BL616
   SPI bus, the LCD backlight driver, the WS2812). The list and the risks are in
   `OpenVRX-Core: gateware/BRINGUP.md`, section 5. Older board revisions (3921,
   3850) wire pins 71-76 and 86 to the BL616. RESETB left the TMDS bank for
   LED pin 18 on 2026-10-05, guarded by `tools/test_tmds_bank_outputs.py`.
   What did we miss?
9. **Self-interference.** An FPGA, SDRAM and HDMI a few centimetres from two
   5.8 GHz receivers. Pixel-clock harmonics land near some channels (5791.5
   MHz near F4 5800). Is the shielding and layout plan in
   `OpenVRX-Puck: design/PUCK_2027_KONCEPT.md` realistic?

## What we know is not verified

- No hardware has been built or powered.
- The rev A schematic is generated from a script (SKiDL), ERC-clean and
  checked against the gateware pin plan, but has no layout, no SI/PI review
  and no KiCad project yet.
- The 1080p path through an LT8618SX is not published: its init sequence is
  derived from a vendor driver whose provenance we have not cleared.
- Power design (2S, USB-C PD in/out) is a concept only.
- Decoder recovery is simulated only: re-init of a reset decoder, whole poll
  rounds and the SCL-stretch timeout are tested against slave models.
  Power-loss recovery of a real TVP5150AM1, and whether the lost-lock flag
  (88h bit 4) says anything the H/V lock bits do not, are unmeasured.
- Current Core main `a1247ab` (C2 branch `509fc95`, verified source `c3fda21`)
  has an accepted frozen suite of 604 passes in 39 files and 157 unchanged
  source hashes. Fresh M0 seed 0, M4 seed 0 and M6 seed 2 pass 75 MHz on all
  clocks; four TMDS pairs match M0. Puck main `f2e7d53` pins it, with two
  pin-contract tests passed. This is simulation and source-bound build
  evidence; older B/C3 results remain historical.
- Core #17/#18's existing regressions pass under the owner's 2026-10-08
  trigger and output-F decisions. The accepted F-boundary behavior retains
  one pending output-F transition through fields with no emitted line and
  applies it at the next visible output field; it does not toggle once for
  every admitted or omitted field. The decoder F-bit remains distinct.
- OVN-F1's visible seed-126 phase gap did not recur on Fable's `e113cf6`.
  Accepted C3 fixed the remaining scaled fallback/read-start and virgin
  ring-read findings; its strict replay passes with 216 checked lines.
  This does not verify all LOW -> BUF phases. Historical FAIL reports stay
  in [LOW_BUF_FINDING.md](docs/overnight/2026-10-07/LOW_BUF_FINDING.md).
- The latest 260-seed campaign stopped after 200 seeds: 199 PASS, 1 FAIL,
  and 60 not run. Seed 1345 has 72 checked lines against 144 required;
  triage found only one complete eligible frame before source input ended.
  A longer stimulus would be a new contract. This campaign is not accepted and no RTL
  or hardware failure is established by that coverage count alone.
- A separate seed1345 probe appends four clean fields to the byte-identical
  original stimulus. It passes 360 lines; using the old source end on that same
  trace counts 72. Wrong data/source mappings in the first added frame fail.
  This is one new scenario, not acceptance of the failed campaign or a
  general suffix for PAL/full geometry/all classes. See current STATUS evidence.
- C2's menu and two-decoder reconciliation are integrated after the full
  suite and fresh builds. In-flight values and SDA selection are frozen;
  NACK retries retain paired-poll fairness. The 62-byte UART row records
  requested TV/VCR, not a register readback. Real filter quality remains
  unmeasured. The original draft, first focused failures and nine old-guard
  negative controls are preserved; see
  [STATUS.md](docs/overnight/2026-10-08/STATUS.md) for receipts and history.

## Historical local corrections, 2026-10-05

Core's 78-test suite includes line loss, long VBI, lagging/forced channels,
return after missing fields, constant F and negative controls. RESETB/SPI
roles on LED3/4/5 are explicit and checked by Puck before export. These checks
address reproduced mixer and handoff defects; real decoder phase, integrated
backend behaviour and RF mixing benefit remain open.

## Historical local corrections, 2026-10-07

Merged into Core `main` `7cc4eda` by the night worker. The frozen baseline
suite run of that revision passed: 395 passed, 1 xfailed (the #17 test) in
1:25:56, so the 396-test count is verified. Build numbers below are reported.
Nothing has run on hardware.

- The three night branches are merged: the per-line noise metric (luma
  samples outside 16-235, logged in M6 next to the snow values),
  multi-byte I2C writes, and the formal CDC proofs of `fb_backend.v`.
- The 2026-10-06 review's F1, F2 and F3 are fixed: incomplete lines are not
  stored (`mix_chan.v`), a poll round counts only as a whole (`tvp_ctrl.v`),
  and a missing first line falls back to a black line instead of unwritten
  SDRAM (`fb_sdram.v`). Each has a regression test with a negative control.
- The low-latency trigger's line count is held across its clock-domain
  crossing (`cdc_sync.v` `toggle_tx`), and `i2c_master.v` gives up when SCL
  is stretched longer than 10 ms.
- The M6 menu's channel-table lookup is registered; the 27 MHz domain
  routes at 109-127 MHz across seeds 0-3 against its 54 MHz requirement
  (built, `gateware/README.md`).
- The fuzz campaign through the whole picture chain
  (`gateware/sim/FUZZ_2026-10-07.md`) fixed run-on BT.656 lines, field
  phase measured from reset, X written to SDRAM when the writer starts
  mid-line, a noise counter restarted by a short line, and a mixer rule that
  froze the output when a receiver returned. Open: Core #17 and Core #18.
  Later test/log changes remain on `fuzz/chain-2026-10-07` under separate
  review; the overnight status records which ones have been accepted.
- Core reports 396 tests; the previous handoff said 394. The baseline run
  decided: 396 (395 passed, 1 xfailed).

## How to report

Open an issue in the repository the problem concerns (or in this hub if it
cuts across), with the file and line, the case that breaks, and how you know.
