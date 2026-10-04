# OpenVRX

OpenVRX is an open-source analog 5.8 GHz FPV **video receiver** family built
around an FPGA. Two receivers listen to the same channel, two video decoders
digitise both pictures, and the FPGA picks or blends the better signal **line
by line** before sending clean HDMI to goggles, XR glasses or a TV. Nothing
here has been built yet: the project is in the *planned / early design* stage.

This repository is the family hub. Boards and gateware live in their own
repositories.

## Family

| Repository | What | State |
|---|---|---|
| [OpenVRX-Core](https://github.com/LAP87/OpenVRX-Core) | FPGA gateware shared by every variant: BT.656 capture, line mixer, SDRAM or low-latency video path, HDMI/DVI out, UI, receiver control, models and tests | Simulated; bitstreams build; **not yet run on hardware** |
| [OpenVRX-Puck](https://github.com/LAP87/OpenVRX-Puck) | Ground "puck": two receivers, battery, two buttons and an OLED, HDMI out, antenna connectors. Sits on the ground or hangs from a lanyard. | Rev A decoder-board schematic (script, ERC clean); no layout |
| OpenVRX-Goggles | Same core inside goggles | Idea only, no repository yet |

## Why

Analog FPV is still the lowest-latency, cheapest and most robust video link,
but the receivers are old (RTC6715-era modules) and diversity is usually a
switch between whole pictures. Digitising both receivers lets an FPGA judge
every video line on its own and keep the cleaner one, or blend the two, while
adding almost no latency. The same FPGA can then drive modern displays
(HDMI, XR glasses) that analog receivers cannot. Commercial alternatives are
either closed goggles modules or screens; a portable, display-less analog
ground station with line mixing and HDMI out does not seem to exist.

## Specifications (targets, not measured)

| | |
|---|---|
| Video in | 2x analog 5.8 GHz receivers (RX5808 with SPI mod; ESP32-C5 "C5VRX" under evaluation) |
| Decoders | 2x TVP5150AM1, BT.656, NTSC and PAL |
| Diversity | per-line select or blend, decided by per-line high-frequency "snow" energy and sync errors |
| FPGA | GW2AR-18 (Tang Nano 20K) for development; GW5A-25 considered |
| Output | 720p60 DVI/HDMI from the FPGA; 1080p60 via an HDMI transmitter planned |
| Latency, buffered mode | one to three fields (SDRAM triple buffer) |
| Latency, low-latency mode | about 0.1 ms (top of picture) to 0.8 ms (bottom), output genlocked to the input |
| UI | 2 buttons, 128x32 OLED, on-screen display, UART measurement log |
| Power (Puck) | 2S Li-ion, USB-C PD in/out (planned) |

## Constraints

- Hobby budget, staged purchases; development on a Tang Nano 20K first.
- Fully open toolchain: Yosys, nextpnr-himbaechel, Apicula, Icarus Verilog, cocotb.
- Legal channels only: the UI flags channels outside the Swedish/EU 5725-5875 MHz band.

## How this was made, and what is verified

Most of the design work so far (gateware, models, tests, the rev A schematic
script and the research notes) was done with heavy AI assistance (Claude),
directed and reviewed by the project owner. Everything is checked in
simulation against independent Python models, but **no part has run on real
hardware yet**. Treat it as a well-tested proposal, not a proven design.
[REVIEW.md](REVIEW.md) lists what we are least sure about. Please try to
break it.

Detailed notes in `research/` and `docs/` are in Swedish for now.

## Contributing

Issues and pull requests are welcome in the board or core repository they
concern; family-wide questions belong here. Adversarial review is especially
welcome: see [REVIEW.md](REVIEW.md).

## License

Hardware and gateware are licensed under
[CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt), see [LICENSE](LICENSE).
