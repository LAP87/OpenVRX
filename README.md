# OpenVRX

OpenVRX is an open-source analog 5.8 GHz FPV **video receiver** family built
around an FPGA. Two receivers listen to the same channel, two video decoders
digitise both pictures, and the FPGA picks or blends the better signal **line
by line** before sending 720p DVI/HDMI to a display. The gateware is simulated
and builds. On a Tang Nano 20K with one TVP5150 module it has shown the test
pattern, passed the SDRAM memory test and, on 2026-10-22, put the first camera
picture on HDMI, received by an ESP32-C5 running C5VRX
([docs/BANK_2026-10-22.md](docs/BANK_2026-10-22.md)). **Two receivers and the
line mixer have not run on hardware yet.** A 1080p output for XR glasses is a
separate planned step.

This repository is the family hub. Boards and gateware live in their own
repositories.

## Family

| Repository | What | State |
|---|---|---|
| [OpenVRX-Core](https://github.com/LAP87/OpenVRX-Core) | FPGA gateware shared by every variant: BT.656 capture, line mixer, SDRAM or low-latency video path, HDMI/DVI out, UI, receiver control, models and tests | Simulated; bitstreams build; M0, M2a, M3, M4 and M6 loaded on a Tang Nano 20K with one decoder, first camera picture 2026-10-22; **the two-decoder mixer not yet tried** |
| [OpenVRX-Puck](https://github.com/LAP87/OpenVRX-Puck) | Ground "puck": two receivers, battery, two buttons and an OLED, HDMI out, antenna connectors. Sits on the ground or hangs from a lanyard. | Rev A decoder-board schematic (script, ERC clean); no layout |
| OpenVRX-Goggles | Same core inside goggles | Idea only, no repository yet |

## Why

The aim is an analog ground receiver with HDMI output and diversity decisions
for each video line. Digitising both receivers lets the FPGA select a line
or blend two similar lines. Whether this improves real RF reception, and how
much delay the complete camera-to-display chain adds, remain bench questions.

## Specifications (targets, not measured)

| | |
|---|---|
| Video in | 2x analog 5.8 GHz receivers (RX5808 with SPI mod; ESP32-C5 "C5VRX" under evaluation) |
| Decoders | 2x TVP5150AM1, BT.656, NTSC and PAL |
| Diversity | per-line select or blend, decided by per-line high-frequency "snow" energy and sync errors |
| FPGA | GW2AR-18 (Tang Nano 20K) for development; GW5A-25 considered |
| Output | 720p60 DVI/HDMI from the FPGA; 1080p60 via an HDMI transmitter planned |
| Latency, buffered mode | one to three fields (SDRAM triple buffer) |
| Internal low-latency path | about 0.1–0.8 ms in a scaled simulation after decoder line delivery; complete camera-to-display latency unmeasured |
| UI | 2 buttons, 128x32 OLED, on-screen display, UART measurement log |
| Power (Puck) | 2S Li-ion, USB-C PD in/out (planned) |

## Constraints

- Hobby budget, staged purchases; development on a Tang Nano 20K first.
- Fully open toolchain: Yosys, nextpnr-himbaechel, Apicula, Icarus Verilog, cocotb.
- The UI flags channels outside 5725-5875 MHz; the flag describes the channel table, not a tested RF transmitter.

## How this was made, and what is verified

Most of the design work so far (gateware, models, tests, the rev A schematic
script and the research notes) was done with AI assistance, directed and
reviewed by the project owner. Reference models and negative controls cover
individual modules and selected video cases; they do not validate the entire
M4/M6 receiver. SDRAM timing and buffer ownership, genlock's minimum frame
period and decoder recovery still need work. **On hardware so far: one
decoder and one receiver, not two; the bench notes are in `docs/BANK_*.md`.**
Running the bench from a computer: [docs/BENCH.md](docs/BENCH.md).
[REVIEW.md](REVIEW.md) lists what we are least sure about. Please try to
break it.

Detailed notes in `research/` and `docs/` are in Swedish for now. The work
plan is [docs/ARBETSPLAN.md](docs/ARBETSPLAN.md), the baseline before hardware
is the tag `v0.1-prehw` ([docs/RELEASE_v0.1-prehw.md](docs/RELEASE_v0.1-prehw.md)),
and [research/README.md](research/README.md) says which research notes are current.

The [component and research register](research/komponentregister/README.md)
tracks parts, alternatives, project references and their source evidence.

The [2026-10-06 handoff](docs/handoff/2026-10-06/README.md) records the
takeover snapshot, development changes, acceptance logs and next work.

## Contributing

Issues and pull requests are welcome in the board or core repository they
concern; family-wide questions belong here. Adversarial review is especially
welcome: see [REVIEW.md](REVIEW.md).

## License

Hardware and gateware are licensed under
[CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt), see [LICENSE](LICENSE).
