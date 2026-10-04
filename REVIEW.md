# Invitation to adversarial review

OpenVRX has never run on hardware. Everything below passes our own
simulations, and that is the problem: the models and the RTL come from the
same understanding, so a misread datasheet is wrong in both. We are asking
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
   lines may smear more than it helps. (`OpenVRX-Core: gateware/rtl/line_mixer.v`,
   `mixer/`)
2. **Pairing lines from two decoders.** Each TVP5150 runs on its own crystal
   and clock; lines are paired by (field, line number) after async FIFOs. What
   happens when one decoder slips a line, loses vertical sync, or two fields
   disagree? (`mix_chan.v`, `line_mixer.v`)
3. **TVP5150AM1 bring-up.** Register values (00h, 03h, 0Dh) and status reads
   (88h/89h) come from the datasheet only. Pin strapping, reset timing, crystal
   load and the 2.3 V XTAL1 limit are in the rev A schematic. (`tvp_ctrl.v`,
   `OpenVRX-Puck: design/rev_a/`)
4. **SDRAM on the Tang Nano 20K.** Controller timing and clock phase were
   checked against a behavioural model, not the real embedded SDRAM.
   (`sdram_burst.v`, `clocks_sdram.v`)
5. **Clock-domain crossings.** The Gray-code async FIFO is now proven by
   k-induction with two free clocks (no overflow/underflow, data integrity),
   with negative controls (`gateware/formal/run.sh`). The toggle handshakes in
   `fb_backend.v` are still only simulated. Are the proof's assumptions
   (registers start at reset, free clocks) the right ones?
6. **Low-latency mode.** The 720p output is genlocked to the input fields:
   frames alternate 750/751 lines (NTSC) and the first line waits for the
   input. Will real sinks (TVs, XR glasses, capture cards) accept a varying
   vertical total? (`genlock_timing.v`, `fb_backend.v`)
7. **Open-toolchain pitfalls.** Apicula has miscompiled signed comparisons in
   other projects (we removed all `signed` arithmetic), and newer Apicula packs
   single-ended inputs beside a true-LVDS output as LVDS receivers (we test
   that our version does not: `gateware/tools/test_lvds_bank_inputs.py`).
   What else bites on GW2AR-18?
8. **Shared pins on the Tang Nano 20K.** Every ordinary header GPIO is used.
   Some also reach other parts of the board (HDMI hot-plug and CEC, the BL616
   SPI bus, the LCD backlight driver, the WS2812). The list and the risks are in
   `OpenVRX-Core: gateware/BRINGUP.md`, section 5. Older board revisions (3921,
   3850) wire pins 71-76 and 86 to the BL616. What did we miss?
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

## How to report

Open an issue in the repository the problem concerns (or in this hub if it
cuts across), with the file and line, the case that breaks, and how you know.
