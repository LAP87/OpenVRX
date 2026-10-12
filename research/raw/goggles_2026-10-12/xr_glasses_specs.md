# XR / AR display glasses with USB-C DisplayPort input: specs, input modes and chips (as of 2026-10-12)

Scope: wired display glasses that a project will feed from an HDMI connector (DVI-style TMDS, 1280x720 at 60 / 59.94 / 50 Hz, no audio, possibly no InfoFrames) through an HDMI-to-USB-C DisplayPort bridge. Prices carry date and currency. Shop names and shop links are left out on purpose; manufacturer store pages are linked.

Evidence tags: [M] manufacturer page or spec; [P] press or review; [U] user report; [E] EDID content posted by a user (shows what the sink advertises, not what it accepts); [T] teardown or physical inspection; [O] the owner's own notes in this repo; [R] retailer listing, price only; [S] known only from a search-engine excerpt because the page could not be opened or its body was cut off.

Access limits that shape the evidence:
- reddit.com is blocked in every tool available here. Reddit evidence is therefore only what the owner's note quotes ([XR_GLASOGON_KOMPATIBILITET.md, 2026-10-01](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)). Its raw folder `research/raw/xr/` is not in the checkout I could read.
- gitlab.freedesktop.org answers with a bot check, so the XREAL Air EDID in kernel issue 53 is known from search excerpts only. I did not try to get past the check.
- community.xreal.com did not resolve in DNS from here.
- The web-search quota ran out mid-session. Goovis, Rokid, ASUS and Lenovo Gen 1 got less coverage than XREAL, VITURE and RayNeo.

## 1. Which models accept 720p60, which only 1080p, and what does the EDID advertise?

### Takeaway
No manufacturer documents 720p input for any of these glasses and no report of a working 720p connection turned up. The one full XREAL Air EDID seen holds only three 1080p timings, the VITURE Beast EDID has a native 1080p60 timing (the rest unpublished), and where a sub-1080p mode was forced (XREAL Air 2023, VITURE Beast 2026, VITURE Pro XR and XREAL XBX per the owner's note) the result was glitching, a scrambled picture, a rainbow screen or no signal.

### Cited Findings

#### What the glasses advertise (EDID)
- XREAL Air and Air 2 Pro, in a Linux kernel issue about the missing non-desktop flag: vendor ID MRG, product IDs 0x3132 (Air) and 0x3135 (Air 2 Pro), and the issue says neither EDID has a DisplayID 2.0 block. The decode shown is of one Air unit, name "Air": three detailed timings only, 1920x1080 at 60, 90 and 120 Hz, with the same porch and sync values in all three and a 297 MHz pixel clock at 120 Hz; no range-limits descriptor; base-block image size 12 x 7 cm against 1920 x 1080 mm in the first timing. The Air 2 Pro timings were not seen. [E][S] — [freedesktop drm/misc/kernel issue 53](https://gitlab.freedesktop.org/drm/misc/kernel/-/issues/53)
- The owner's earlier read of the same Air EDID: 148.5 / 222.75 / 297 MHz, each 2200x1125 total (CEA 1080p60 blanking), no established timings. [O] — [UTGANG_OCH_LATENS_2026-10-05.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/UTGANG_OCH_LATENS_2026-10-05.md)
- A forum poster diagnosed Nreal glasses as lacking the CTA-861 extension, which is where VIC lists such as 720p60 normally sit. [U][S] — [XREAL community thread](https://community.xreal.com/t/getting-it-to-work-with-ubuntu-laptop/1268)
- VITURE Beast, EDID read through the NVIDIA driver's I2C-over-AUX adapter, posted 2026-07-08: 256 bytes (base block + CTA-861 extension), name "VITURE Beast", native DTD 1920x1080 at 60 Hz, 148.5 MHz. edid-decode flags image-size misuse, an unknown display descriptor type 0x18 and more native DTDs than DTDs in the CTA block. USB ID 35ca:1201. The CTA video data block and any further DTDs were not posted. [E][U] — [NVIDIA developer forum](https://forums.developer.nvidia.com/t/unable-to-read-edid-for-viture-beast-xr-glasses-usb-c-dp-alt-mode-but-every-userspace-i2c-over-aux-read-through-the-drivers-own-i2c-adapter-suc/376114)
- A VITURE user in the intofpv "fpv glasses POC" thread found 720p missing from the glasses' EDID (HDMI to USB-C through the VITURE Pro Mobile Dock, digital HD source). [U][O] — [DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md); [XR_GLASOGON_KOMPATIBILITET.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)
- Not found at all: an EDID dump for XREAL Air 2 Ultra, One, One Pro, 1S, ROG XREAL R1 or xbx a01; VITURE One, One Lite, Pro XR, Luma family or Pro 2; any Rokid, RayNeo, Lenovo, ASUS, TCL, INMO or Goovis model.

#### What the makers say about input modes
- XREAL One series: connects to "any device that supports DP video output"; the overview lists no resolution or refresh table. [M] — [XREAL tutorials, One series](https://tutorials.xreal.com/docs/glasses/one-series)
- XREAL xbx a01: 2D 1920x1080, 3D 3840x1080, up to 120 Hz; its "Stabilization" feature needs a 120 Hz source; audio goes over DP by default. [M] — [spec](https://tutorials.xreal.com/docs/glasses/xbxa01/spec); [FAQ](https://tutorials.xreal.com/docs/glasses/xbxa01/faq)
- XREAL docs table (Air to 1S): 1920x1080 per eye, 1S 1920x1200; the refresh column is headed "MR space", so it describes the spatial-rendering rates, not the list of accepted input timings. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- VITURE: Pro, One and Pro 2 are 1080p per eye; Luma family and Beast are up to 1920x1200 per eye; native 3D is full side-by-side 3840x1080. VITURE's own USB-C-to-glasses adapter outputs 1920x1080 at 60 Hz and 3840x1080 at 60 Hz only. VITURE advises 1920x1080 at 120 Hz for Pro on Steam Deck and 1080p for Luma. On phones the 3D (3840x1080) mode needs a source that can output 4K or more. [M] — [Pro/One](https://www.viture.com/academy/xr-glasses/pro-one-series); [Luma](https://www.viture.com/academy/xr-glasses/luma-series); [Pro 2](https://www.viture.com/academy/xr-glasses/pro-2)
- VITURE Beast: the on-screen menu offers 1080p and 1200p; the USB-C charging adapter supports Default mode at 60 Hz only (no 3D, UltraWide, 120 Hz or 1200p on Beast). [M] — [Beast](https://www.viture.com/academy/xr-glasses/the-beast)
- RayNeo: 2D 1920x1080, 3D 3840x1080; 3D works only at 60 Hz; the Air 3s support pages state no source-resolution requirement. RayNeo's FAQ for Air 2 / NXTWEAR S advises setting the source to 1080. [M] — [Air 3s refresh rate](https://www.rayneo.com/pages/service-air3s-refresh-rate); [FAQ Air 2](https://www.rayneo.com/pages/faq-air-2)
- RayNeo's own HDMI adapter XRAC-ADA01OS is listed with video output 4K30, 2K30 and 1080p120; no 720p entry. [M][S] — [manuals.plus listing](https://manuals.plus/asin/B0FFSCSZ8V)
- TCL NXTWEAR AIR: 2D 1920x1080, 3D 3840x1080, 60 Hz; the page gives no supported input timings. [M] — [TCL Sweden spec page](https://www.tcl.com/se/sv/glasses/tcl-nxtwear-air/specifications)
- ASUS AirVision M1: the spec page lists USB-C and a 72 Hz panel but no DisplayPort version or input modes. [M] — [ASUS tech spec](https://www.asus.com/displays-desktops/glasses/airvision/asus-airvision-m1/techspec/)
- Lenovo Legion Glasses Gen 1: 1920x1080, USB-C 3.2 with DP 1.2; Lenovo's support page also lists a compatibility whitelist document. [M][S] — [Lenovo support](https://support.lenovo.com/ph/en/accessories/acc500321-legion-glasses-overview-and-service-parts)
- For contrast, the HDZero Goggle takes exactly 1920x1080 or 1280x720 over HDMI and sorts the frame rate into 50 / 60 / 100 classes. [O] — [UTGANG_OCH_LATENS_2026-10-05.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/UTGANG_OCH_LATENS_2026-10-05.md)

#### What happens on a mode the glasses do not take
- Nreal Air on Arch/GNOME with an unreadable EDID (2023-09-06): only low 4:3 modes were offered, and each one gave flickering colours or glitching. [U] — [Purism forum](https://forums.puri.sm/t/librem-5-ar-heaset/19681)
- VITURE Beast with no EDID read (2026-07-08): the driver fell back to 1024x768, 800x600 and 640x480, and the poster reports a scrambled picture on the 1080p panel. [U][E] — [NVIDIA developer forum](https://forums.developer.nvidia.com/t/unable-to-read-edid-for-viture-beast-xr-glasses-usb-c-dp-alt-mode-but-every-userspace-i2c-over-aux-read-through-the-drivers-own-i2c-adapter-suc/376114)
- VITURE Pro XR shows a "rainbow screen" at 720p; XREAL XBX shows "no signal" at 720p (Reddit reports quoted by the owner, originals not re-checked). [U][O] — [XR_GLASOGON_KOMPATIBILITET.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)
- Nintendo Switch 2 (launch coverage, article date not seen): an XREAL representative said Nintendo changed the console's video "timing sequence", so XREAL One glasses, even behind the XREAL Hub, fail to recognise the signal. A summary of the same article says its tests with XREAL One Pro, RayNeo Air 3S and Rokid Max 2 gave blank screens, also through HDMI-to-USB-C cables and third-party docks. [P][S] — [TechRadar](https://www.techradar.com/gaming/virtual-reality-gaming/xreal-already-working-on-a-solution-to-nintendo-switch-2s-devastating-lack-of-ar-glasses-support)
- VITURE says its USB-C XR Charging Adapter Ultra supports Switch 2, Steam Deck and ROG Ally; it does not say what the adapter changes. [M] — [Luma series](https://www.viture.com/academy/xr-glasses/luma-series)
- XREAL's black-screen page: a DP-detection failure shows the warning "Device may not support video output"; a glasses unit left in Anchor mode can also look black because the screen is not in front of the eyes. [M] — [XREAL black screen](https://tutorials.xreal.com/docs/glasses/one-series/troubleshooting/blackscreen)
- Adapters that replace the glasses' EDID with their own are described on XREAL's forum and give an offset picture (via the owner's note). [U][O] — [UTGANG_OCH_LATENS_2026-10-05.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/UTGANG_OCH_LATENS_2026-10-05.md)

#### Non-1080p60 modes that are documented as working
- 3840x1080 at 60 Hz: VITURE adapter output list; RayNeo, TCL and XREAL xbx a01 list it as the 3D resolution. [M] — [VITURE Pro/One](https://www.viture.com/academy/xr-glasses/pro-one-series); [RayNeo Air 3s Pro](https://www.rayneo.com/products/air-3s-joydock); [TCL AIR](https://www.tcl.com/se/sv/glasses/tcl-nxtwear-air/specifications); [xbx a01](https://tutorials.xreal.com/docs/glasses/xbxa01/spec)
- 1920x1080 at 72 / 90 / 120 Hz on XREAL (docs table, MR space), 60 / 90 / 120 Hz on VITURE Pro and Pro 2, 60 / 120 Hz on RayNeo. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses); [VITURE Pro 2](https://www.viture.com/academy/xr-glasses/pro-2); [RayNeo refresh rate](https://www.rayneo.com/pages/service-air3s-refresh-rate)
- 1920x1200 on VITURE Luma family, Beast and XREAL 1S. [M] — [Luma series](https://www.viture.com/academy/xr-glasses/luma-series); [XREAL One-series spec](https://tutorials.xreal.com/docs/glasses/one-series/spec)
- XREAL One Pro firmware of 2026-07-22 adds official 90 fps input for the 21:9 UltraWide layout. [P] — [iPhone in Canada](https://www.iphoneincanada.ca/2026/07/23/xreal-one-pro-firmware-update-adds-90fps-ultrawide-mode-and-better-controls/)

#### Status at a glance (720p60 and 50 Hz)

| Model | 720p60 | 50 Hz | Basis (sources in the bullets above) |
|---|---|---|---|
| XREAL Air | not advertised; 4:3 fallback modes glitch | not advertised | EDID with three 1080p timings; 2023 user report |
| XREAL xbx a01 (probably the owner's "XBX") | no signal | not documented | user report via owner's note |
| XREAL Air 2, Air 2 Pro, Air 2 Ultra, One, One Pro, 1S, ROG R1 | not documented, untested | not documented | Air 2 Pro EDID timings not seen; Switch 2 timing failure on One |
| VITURE Pro XR | rainbow screen | not documented | user report via owner's note |
| VITURE Beast | not advertised in the native DTD; VESA fallbacks scrambled | not documented | EDID and user report, 2026-07-08 |
| VITURE, model not stated (Pro Mobile Dock path) | 720p missing from the EDID | not documented | intofpv user via owner's note |
| VITURE One, One Lite, Luma family, Pro 2 | not documented, untested | not documented | no EDID or user report found |
| Rokid, RayNeo, Lenovo, ASUS, TCL, INMO, Goovis | not documented, untested | not documented | makers publish the native resolution only (RayNeo and TCL also 3840x1080 SBS) |

### Inferences
- Treat 720p60 as unsupported on every model until a unit takes it on a bench. The only direct evidence is negative (XREAL Air, VITURE Beast, VITURE Pro XR, XREAL XBX); the other models are untested, not proven to fail.
- The three XREAL Air timings share one blanking set and differ only in pixel clock. That pattern fits a glasses front end that follows the input pixel clock into the panel without a frame store, and it would explain scrambled output on every non-native mode. No teardown confirms it.
- "XBX" in the owner's note is probably the xbx a01 (XREAL's entry-level glasses, SeeYa panel); the note does not give a model number.
- The safest feed is CEA 1080p60 (2200x1125 total, 148.5 MHz) with constant line count. A line count that alternates 750 / 751 is an extra risk: DisplayPort carries the total line count in its stream attributes and nothing found says how any glasses treat a change from frame to frame.

### Gaps
- Original Reddit and XREAL-forum posts behind the three 720p reports were not re-read.
- CTA video data block of the VITURE Beast and full EDIDs of One / Pro XR / Luma / Pro 2 / Rokid / RayNeo / Lenovo / TCL / ASUS were not found.
- No bench result for 720p on Rokid, RayNeo, Lenovo, TCL, ASUS or Goovis.
- Whether the XREAL X1 or the RayNeo Vision 4000 scales an accepted-but-non-native input is not documented.

## 2. Is any model documented to accept 50 Hz (or other non-60 rates)?

### Takeaway
No. Documented rates are 60 / 72 / 90 / 120 Hz families (240 Hz on ROG XREAL R1 with Frame rate Boost), and no EDID seen contains a 50 Hz timing.

### Cited Findings

#### Refresh rates by maker
- XREAL docs table ("MR space" column): Air 60 and 72 Hz; Air 2, Air 2 Pro, Air 2 Ultra, One, One Pro, 1S: 60, 72, 90, 120 Hz. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- XREAL 1S spec page: "Fixed 90 Hz, up to 120 Hz"; One and One Pro: highest 120 Hz. [M] — [XREAL tutorials spec](https://tutorials.xreal.com/docs/glasses/one-series/spec)
- XREAL Air EDID (one decoded unit): 60, 90, 120 Hz (no 72 Hz entry, unlike the docs table). [E][S] — [freedesktop issue 53](https://gitlab.freedesktop.org/drm/misc/kernel/-/issues/53)
- XREAL Hub: up to 120 Hz passthrough. [M] — [XREAL EU store, Hub](https://eu.shop.xreal.com/products/xreal-hub)
- XREAL xbx a01: up to 120 Hz. ROG XREAL R1: 120 Hz, or 240 Hz with Frame rate Boost on. [M] — [xbx a01 spec](https://tutorials.xreal.com/docs/glasses/xbxa01/spec); [ASUS ROG spec](https://rog.asus.com/us/glasses/rog-xreal-r1/spec/)
- XREAL One Pro firmware 2026-07-22: official 90 fps input for the 21:9 UltraWide layout. [P] — [iPhone in Canada](https://www.iphoneincanada.ca/2026/07/23/xreal-one-pro-firmware-update-adds-90fps-ultrawide-mode-and-better-controls/)
- VITURE Pro and Pro 2: 120 / 90 / 60 Hz; One and One Lite: 60 Hz; Luma family and Beast: up to 120 Hz (120 / 90 / 60 listed); Neckband, One Mobile Dock and Pro Mobile Dock: 60 Hz only; the USB-C charging adapter: 60 Hz only. [M] — [Pro/One](https://www.viture.com/academy/xr-glasses/pro-one-series); [Luma](https://www.viture.com/academy/xr-glasses/luma-series); [Beast](https://www.viture.com/academy/xr-glasses/the-beast); [Pro 2](https://www.viture.com/academy/xr-glasses/pro-2)
- RayNeo Air 3s: 60 Hz default, 120 Hz selectable on the left temple or in the OS, 3D mode 60 Hz only. GT and GT Max: 2D 120 Hz, 3D 60 Hz. Air 4 Pro: up to 120 Hz. [M] — [refresh-rate page](https://www.rayneo.com/pages/service-air3s-refresh-rate); [GT](https://www.rayneo.com/products/rayneo-gt-ar-glasses); [Air 4 Pro](https://www.rayneo.com/products/rayneo-air-4-pro-ar-smart-glasses)
- Lenovo Legion Glasses: Gen 1 60 Hz, Gen 2 60 / 90 / 120 Hz. [P] — [Mixed](https://mixed-news.com/en/lenovo-legion-glasses-2-new-ar-glasses-with-gaming-focus-coming-in-february-for-399)
- TCL NXTWEAR AIR 60 Hz; NXTWEAR S+ 60 / 120 Hz (Japanese spec page); a US retailer text says a double click switches 60 / 120 Hz. [M][R] — [TCL AIR](https://www.tcl.com/se/sv/glasses/tcl-nxtwear-air/specifications)
- ASUS AirVision M1: 72 Hz. [M] — [ASUS tech spec](https://www.asus.com/displays-desktops/glasses/airvision/asus-airvision-m1/techspec/)
- Rokid Max: 120 Hz (press reports citing Rokid); Max 2: 120 Hz. [P][S] — [Auganix](https://www.auganix.org/?p=13845); [New Atlas](https://newatlas.com/wearables/rokid-max-ar-glasses/); [The Gadgeteer on Max 2](https://the-gadgeteer.com/?p=511195)
- Goovis G3 Max: up to 120 Hz. [M] — [Goovis store, G3 Max](https://www.goovis.com/products/goovis-g3max)

### Inferences
- Every listed rate is a multiple of 24 or 30 (72 = 3 x 24, 90, 120). No list contains 50 or 100 Hz, so a 50 Hz feed is outside every documented set.
- If the glasses follow the pixel clock the way the Air EDID suggests (section 1), 1080p50 on the same 148.5 MHz clock with 2640x1125 total would be the nearest relative of those timings. Untested.
- A 50 Hz source is safer converted to 60 Hz or 59.94 Hz before the bridge, at the cost of the conversion latency.

### Gaps
- No source found for 50 Hz, PAL or 1080p50 input on XREAL, VITURE, Rokid, RayNeo, Lenovo, TCL or ASUS glasses. A search-engine excerpt of a Reddit mirror mentions 1920x1200 at 48 Hz for movies on a Rokid model; unverified and not used above.
- No data on how far a 59.94 Hz (1000/1001) pixel clock is tolerated.

## 3. Which chips sit between USB-C DP and the panels, and do they scale or pass through?

### Takeaway
No teardown, FCC photo or firmware dump found names the DisplayPort receiver or DP-to-panel bridge in any of these glasses. Named parts are XREAL's in-house X1 coprocessor, RayNeo's Vision 4000 display processor, the panels (Sony or SeeYa), and on the adapter side Lontium LT6711A (HDMI 2.0 to DP 1.2, no scaler in its feature list) and VIA Labs VL171.

### Cited Findings

#### Inside the glasses
- XREAL X1: described by XREAL as an in-house spatial co-processing chip built into the One series; it creates the spatial display and 3DoF tracking; motion-to-photon latency 3 ms at 120 Hz. [M][P] — [CGMagazine, 2024-12-04](https://www.cgmagonline.com/news/xreal-unveils-xreal-one-series/); [Mixed](https://mixed-news.com/en/xreal-introduces-new-ar-glasses-with-native-3dof-tracking-larger-field-of-view-and-in-house-x1-chip/)
- MoguraVR reported on 2024-09-09, drawing on a 2024-09-04 post by XREAL's CEO, that X1 is not a wholly original design but a customised version of an existing chipset; no detailed specs were published then. [P] — [MoguraVR](https://www.moguravr.com/xreal-chipset/)
- Yole Group sells a report on the XREAL X1 processor based on a teardown of the XREAL One Pro (TSMC advanced node, self-designed SoC); findings are not public. [P][S] — [Yole Group](https://www.yolegroup.com/product/report/xreal---x1-processor-mcu/)
- Counterpoint Research published a teardown and BoM analysis of the XREAL Air 2 on 2024-04-23; subscription only. [P] — [Counterpoint](https://www.counterpointresearch.com/report/bom-analysis-for-xreal-air2)
- A comment on a Lemmy-hosted post (the search excerpt calls it Reddit-sourced) says teardowns of the XREAL Air show an MCU, a GPIO expander, a 6DoF chip and the displays with their drivers. No part numbers. [U][S] — [Lemmy post](https://campfyre.nickwebster.dev/post/156950/917696)
- RayNeo Vision 4000: display chip for colour tuning and real-time SDR-to-HDR, developed with Pixelworks according to RayNeo's blog, in GT and GT Max; the Air 4 Pro page names Vision 4000 AI SDR-to-HDR upscaling. RayNeo Zone 360 is the 3DoF chip in GT and GT Max. X3 Pro runs a Snapdragon AR1 Gen 1. The blog describes only panel and optics for Air 2s, Air 3s and Air 3s Pro. [M] — [RayNeo blog](https://www.rayneo.com/blogs/news/rayneo-wired-vs-wireless-models-explained); [Air 4 Pro](https://www.rayneo.com/products/rayneo-air-4-pro-ar-smart-glasses); [GT](https://www.rayneo.com/products/rayneo-gt-ar-glasses)
- Panel makers: Sony 0.55-inch (XREAL One Pro, ROG XREAL R1), Sony 0.68-inch (XREAL One, 1S), 0.49-inch micro-OLED in the ASUS AirVision M1 (ASUS's global page names no maker; a search excerpt of its US and NZ pages says Sony), Sony 1080p (Rokid Max); SeeYa 0.6-inch (RayNeo Air 3s Pro, Air 4 Pro, GT, GT Max; XREAL xbx a01). [M] — [XREAL spec](https://tutorials.xreal.com/docs/glasses/one-series/spec); [ASUS ROG](https://rog.asus.com/us/glasses/rog-xreal-r1/spec/); [ASUS M1](https://www.asus.com/displays-desktops/glasses/airvision/asus-airvision-m1/techspec/); [Rokid Max](https://www.businesswire.com/news/home/20230321005671/en/Rokid-Unveils-Rokid-Max-AR-Glasses-With-Premium-MAX-Theater-Experience); [RayNeo bundle page](https://www.rayneo.com/products/air-3s-joydock); [xbx a01](https://tutorials.xreal.com/docs/glasses/xbxa01/spec)
- Sony's public micro-OLED list for AR/VR headsets shows MIPI D-PHY (with DSC) or LVDS interfaces: ECX350F 0.44-type Full HD (MIPI + DSC), ECX343FN WUXGA (LVDS), ECX344A 1.3-type 3.5K4K (MIPI + DSC). The 0.55 / 0.68-inch 1080p and 1200p parts used in glasses are not on that list. [M] — [Sony Semiconductor](https://www.sony-semicon.com/en/products/microdisplay/oled.html)
- An example of a DP-to-MIPI bridge, not a confirmed part of any glasses: Lontium LT7911D takes DP 1.2 / eDP / Type-C and outputs dual MIPI DSI/CSI up to 12 Gbit/s, has an EDID buffer, and can map the left and right halves of 3D video to two panels; a USB-C-to-MIPI micro-OLED dev adapter pairs it with a GD32F103 MCU. [M][S] — [display module vendor](https://www.displaymodule.com/products/type-c-to-mipi-adapter-for-micro-oled-one); [CSDN write-up](https://damodev.csdn.net/6aa3c6be1a35784c8420d55c.html)
- No XR-glasses teardown appears in ChargerLAB's current index or in an iFixit search. [T] — [ChargerLAB teardown list](https://www.chargerlab.com/?s=xreal)

#### HDMI-to-USB-C side
- Lontium LT6711 brief rev 1.1 (A = QFN64, B = BGA81): HDMI 2.0 receiver (HDCP 1.4 / 2.2, up to 4Kx2K at 60 Hz, 8-bit, SCDC), DP 1.2 / eDP 1.4 transmitter (4 lanes at 1.62 / 2.7 / 5.4 Gbit/s, up to 4Kx2K60, HDCP 1.3), USB Type-C R1.2 with DP Alt Mode and PD 3.0, built-in pattern generator and OSD, 27 MHz crystal, 1 W at 4K60, application list "Mobile systems, VR/AR". The brief lists no frame buffer, scaler, timing converter or EDID feature. [M]
- A teardown of an HDMI-to-USB-C DisplayPort adapter bought for AR glasses found an LT6711A and points to the open-hardware melonHD design. [T] — [Everyday Thing, Substack](https://everydaything.substack.com/p/an-hdmi-to-usbc-display-port-converter)
- melonHD: LT6711A with custom firmware, HDMI 2.0 input (480p to 2160p per its feature line), DP 1.2 Alt Mode output, requests 5 / 9 / 12 / 15 V on the downstream port by pin strap, HPD stays low during a power-only contract, powered from downstream VBUS. [M] — [melonHD thread](https://bitbuilt.net/forums/threads/melonhd.6782/)
- Delock's HDMI-to-USB-C adapter (item 63251) lists LT6711A, up to 4K60 and HDCP 1.4 / 2.2. [M][S] — [Delock](https://www.delock.com/produkt/63251/merkmale.html)
- RayNeo's own USB-C adapter XRAC-CHA01OS (USB-C in, not HDMI) uses a VIA Labs VL171 DP/USB demultiplexer, an M3TEK MT3935A buck converter and an ETA6280S2F current limiter. [T] — [ChargerLAB](https://www.chargerlab.com/teardown-of-rayneo-air-3s-pro-original-usb-c-adapter-xrac-cha01os/)

### Inferences
- The LT6711A is a protocol converter, not a scaler: the DP stream should carry the HDMI input's timing unchanged, so the glasses see the project's timing 1:1. This agrees with the owner's earlier hypothesis ([H] in UTGANG_OCH_LATENS); the brief only shows that no scaler is listed, not that none exists.
- X1 and Vision 4000 are frame-processing parts, so those models could in principle resample an accepted input. Whether they accept a non-native one is a separate question; no document covers it.
- A DP-to-MIPI or DP-to-LVDS stage must exist in every model whose panel has only those interfaces; which vendor's chip does it is unknown for all of them.

### Gaps
- Part numbers of the DP receiver / bridge in every model; FCC internal-photo filings were not reached; Yole and Counterpoint reports are paywalled.
- Whether LT6711A presents its own EDID to the HDMI source or forwards the glasses' (the brief is silent; the owner's note reports adapters that substitute their own).
- LT6711A behaviour on DVI-style input without InfoFrames, and on a line count that alternates between 750 and 751.

## 4. Which models are plain 2D "monitor" devices, and which need a phone app or host software?

### Takeaway
Per their makers (for Lenovo, per a retailer text), XREAL, VITURE, RayNeo, TCL, Lenovo and Goovis glasses show a plain picture from any DisplayPort-capable USB-C source without an app; software or firmware matters for 3DoF / 6DoF, UltraWide and 3D modes, and updates. INMO Air 3, RayNeo X3 Pro and iO, and Rokid with Station 2 are Android devices rather than monitors.

### Cited Findings
- XREAL One series: no battery, plug and play, any DP video source; native 3DoF in the glasses (X1) with Anchor and Follow modes; firmware through a browser update page. The XRLinuxDriver project tells users of One, One Pro and 1S to disable stabiliser / anchor features on the glasses. [M] — [XREAL tutorials, One series](https://tutorials.xreal.com/docs/glasses/one-series); [XREAL FAQ](https://tutorials.xreal.com/docs/glasses/one-series/faq); [XRLinuxDriver README](https://github.com/wheaney/XRLinuxDriver)
- XREAL xbx a01: "Stabilization" is optional and available only with 120 Hz output; display presets Standard / Cinema / Eye Care. [M] — [xbx a01 FAQ](https://tutorials.xreal.com/docs/glasses/xbxa01/faq); [xbx a01](https://tutorials.xreal.com/docs/glasses/xbxa01)
- XREAL Air to Air 2 Pro: no cameras or tracking beyond the IMU in the docs table; Air 2 Ultra has 6DoF through dual grayscale cameras. A Hacker News user says the Air works as a plain 1080p display by default. [M][U] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses); [Hacker News, 2024-11-25](https://news.ycombinator.com/item?id=42232741)
- VITURE: works with "any USB-C device capable of video and power output"; refresh rate is set in the OS; 2D / 3D is a long-press on the glasses; the SpaceWalker app is optional (3DoF, multi-screen, ultrawide); Beast cycles Anchor / Smooth Follow / 0DoF with R1; Luma-series 6DoF and hand gestures are advertised together with the Pro Neckband and Mac / Windows setups. [M] — [Pro/One](https://www.viture.com/academy/xr-glasses/pro-one-series); [Beast](https://www.viture.com/academy/xr-glasses/the-beast); [Luma](https://www.viture.com/luma)
- RayNeo Air 4 Pro: basic viewing needs no Wi-Fi or app, the RayNeo Air Series App is optional, and the glasses do not support 3DoF. GT and GT Max add native 3DoF (Pinned / Steady / Follow). RayNeo's wired models have no battery and no standalone function. [M] — [Air 4 Pro](https://www.rayneo.com/products/rayneo-air-4-pro-ar-smart-glasses); [GT](https://www.rayneo.com/products/rayneo-gt-ar-glasses); [RayNeo blog](https://www.rayneo.com/blogs/news/rayneo-wired-vs-wireless-models-explained)
- TCL NXTWEAR S+: needs a USB-C source with DP; the 3D function does not work on non-DP Android or iPhone, which can only mirror. [M] — [TCL FAQ](https://www.tcl.com/gulf/en/support/faq/18335)
- Rokid: the Rokid AR app is optional (file transfer); AR Spatial pairs the glasses with Station 2 (8 GB / 128 GB, Wi-Fi 6, 5,000 mAh, YodaOS; press describes YodaOS as an Android variant). [M][P][S] — [Rokid Max 2 store page](https://global.rokid.com/products/rokid-max-2-ar-glasses); [Rokid AR Spatial](https://global.rokid.com/products/rokid-ar-spatial); [The Gadgeteer](https://the-gadgeteer.com/?p=511195); [Mixed](https://mixed-news.com/en/rokids-new-ar-glasses-dont-need-a-phone/)
- Lenovo Legion Glasses: a Dutch / Belgian e-tailer text says Gen 1 behaves like a monitor over USB-C with no software; Gen 2 has a 2D / 3D toggle and received a free 3D-mode update for games (whether Lenovo software is needed for it is not stated). [R][P][S] — retailer listing, link withheld; [Notebookcheck](https://www.notebookcheck.net/Legion-Glasses-2-with-3D-Mode-Lenovo-reveals-free-3D-mode-update-with-over-20-games-supported.1105592.0.html); [GSMGoTech](https://www.gsmgotech.com/2026/04/lenovo-legion-glasses-2-just-got.html)
- ASUS AirVision M1: 3DoF head tracking and presets Office / Theater / Game / Standard / Low blue light. [M] — [ASUS tech spec](https://www.asus.com/displays-desktops/glasses/airvision/asus-airvision-m1/techspec/)
- INMO Air 3: standalone Android 14 on a Snapdragon, 660 mAh battery; USB-C video input is not stated. [M] — [INMO Air3 spec summary](https://smhn.info/202512-inmo-air3-spec)
- Goovis G3 Max / G3X / G3X Pro: single USB-C cable for sources with USB-C video output, HDMI only through Goovis' HC2.0 adapter. [M] — [Goovis G3 Max](https://www.goovis.com/products/goovis-g3max); [G3X](https://www.goovis.com/products/goovis-g3x)

### Inferences
- For a fixed, head-locked FPV picture the simplest candidates are glasses without head tracking (XREAL Air family, RayNeo Air series, Lenovo, TCL AIR / S, Goovis). X1 and VITURE glasses need Anchor / Follow switched off or 0DoF chosen.
- A 720p60 feed would not meet XREAL's 120 Hz condition for the xbx a01 "Stabilization", which is only an observation about that feature, not about whether the glasses show the picture.

### Gaps
- Whether Air 2 Ultra works as a monitor without Nebula / SDK software, and what the default tracking mode of Rokid Max / Max 2 is, was not found.
- ASUS' software requirement (AirVision app or not) is not on its spec page.

## 5. Latency of the glasses themselves

### Takeaway
No independent measurement of any glasses' input-to-photon latency was found. XREAL quotes 3 ms motion-to-photon for the One series and ROG R1, which is head-tracking latency; users report 45 to 60 ms for a full chain with an HDMI-to-USB-C adapter.

### Cited Findings
- XREAL One and One Pro: motion-to-photon 3 ms (manufacturer figure, at 120 Hz). [M] — [XREAL tutorials spec](https://tutorials.xreal.com/docs/glasses/one-series/spec); [Mixed](https://mixed-news.com/en/xreal-introduces-new-ar-glasses-with-native-3dof-tracking-larger-field-of-view-and-in-house-x1-chip/)
- ROG XREAL R1: motion-to-photon 3 ms, panel response 0.01 ms. [M] — [ASUS ROG](https://rog.asus.com/us/glasses/rog-xreal-r1/spec/)
- VITURE markets "wired, latency-free connections" with no number. [M] — [VITURE Switch page](https://www.viture.com/en-SG/blog/nintendo-switch-up-the-way-you-play)
- User chain figures (no method described): 45 to 55 ms at 1080p60 with VITURE Pro XR + Caddx Ascent VRX + the same type of HDMI adapter; about 60 ms in the intofpv thread (VITURE, digital HD source). [U][O] — [XR_GLASOGON_KOMPATIBILITET.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)
- A different device for scale: an IntoFPV user measured 37 +/- 4 ms on the HDMI input of Skyzone Cobra X V2 box goggles with a Raspberry Pi test source and a 240 fps camera, and blamed the portrait-native panel's rotation step. [U][S] — [IntoFPV thread](https://intofpv.com/archive/index.php/thread-22188.html)
- A Hacker News user calls the RayNeo Air 2 "no latency" at 60 or 120 Hz; no measurement. [U] — [Hacker News, 2024-11-25](https://news.ycombinator.com/item?id=42232741)

### Inferences
- The glasses' own share of the 45 to 60 ms is unknown; the adapter's share (LT6711A conversion) is also unpublished. Only a camera or photodiode test of the actual chain separates them.

### Gaps
- No glasses latency measured by a third party; no LT6711A latency figure.

## 6. HDMI-to-USB-C adapters: what makers list, power, EDID

### Takeaway
Makers publish short mode lists for their adapters: RayNeo 4K30 / 2K30 / 1080p120, VITURE 1080p60 and 3840x1080p60. The glasses draw about 5 V at 1 A through the adapter, and the adapter-plus-glasses pair has already failed on a console that changed its timing.

### Cited Findings
- RayNeo HDMI Adapter: USD 64 on the RayNeo store (2026-10-12); the store page lists no modes; the XRAC-ADA01OS listing gives 4K30, 2K30 and 1080p120 output and no HDR10; RayNeo's support FAQ says the glasses, Pocket TV and the HDMI adapter support HDCP. [M][S] — [RayNeo HDMI adapter](https://www.rayneo.com/products/rayneo-hdmi-c); [manuals.plus](https://manuals.plus/asin/B0FFSCSZ8V); [RayNeo FAQ Air 3](https://www.rayneo.com/pages/support-faq-air3)
- RayNeo: for an HDMI source the adapter combines the video signal with a separate power input; the Air 3s support page says an HDMI source needs the adapter and that the adapter should be "fully charged". [M] — [RayNeo blog](https://www.rayneo.com/blogs/news/rayneo-wired-vs-wireless-models-explained); [RayNeo, laptop / PC](https://www.rayneo.com/pages/service-air3s-laptop-pc)
- VITURE: the HDMI XR Adapter is a Lightning design (needs Apple's Lightning Digital AV Adapter; third-party ones may fail; not for Beast; works with all models except Luma Ultra); the USB-C XR Charging Adapter outputs 1080p60 and 3840x1080p60; the Adapter Ultra supports Switch 2, Steam Deck and ROG Ally with up to 65 W passthrough; PlayStation and Xbox need the Pro Mobile Dock; the Mobile Dock Mini is USD 99 (2026-10-12; page shows release date 8.6.2026, i.e. August 2026 in US format). [M] — [Pro/One](https://www.viture.com/academy/xr-glasses/pro-one-series); [Luma](https://www.viture.com/academy/xr-glasses/luma-series); [Pro 2](https://www.viture.com/academy/xr-glasses/pro-2); [Mobile Dock Mini](https://www.viture.com/mobile-dock-mini)
- XREAL names no HDMI adapter: its PlayStation / Xbox page says to use an adapter that converts HDMI to DP and supplies power. The XREAL Hub (EUR 49.90 at the XREAL EU store, 2026-10-12) is a power and passthrough hub with 45 W charging and up to 120 Hz passthrough, listed for the Air family; the page mentions no HDMI input. [M] — [XREAL PS / Xbox page](https://tutorials.xreal.com/docs/glasses/one-series/troubleshooting/ps-xbox-connect); [XREAL EU store, Hub](https://eu.shop.xreal.com/products/xreal-hub)
- The owner's note quotes XREAL's One-series page: devices with an HDMI port connect through an HDMI-to-USB-C adapter, which needs DP and 5 V at 1 A; the glasses have no battery. [O] — [XR_GLASOGON_KOMPATIBILITET.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)
- XREAL xbx a01 draws 5 V / 1 A. [M] — [xbx a01 spec](https://tutorials.xreal.com/docs/glasses/xbxa01/spec)
- Delock's LT6711A adapter note advises connecting a USB power cable if the picture flickers. [M][S] — [Delock](https://www.delock.com/produkt/63251/merkmale.html)
- Timing sensitivity at the adapter-plus-glasses level: see the Switch 2 item in section 1. [P][S] — [TechRadar](https://www.techradar.com/gaming/virtual-reality-gaming/xreal-already-working-on-a-solution-to-nintendo-switch-2s-devastating-lack-of-ar-glasses-support)

### Inferences
- A bridge cannot make glasses accept a timing they refuse. If 720p-class sources must reach these glasses, the only route found is an upscaler to 1080p60 ahead of the bridge, which matches the owner's earlier conclusion.
- Power is an interface requirement: the adapter must supply 5 V near 1 A to the glasses on its own USB-C port, from a separate input.

### Gaps
- EDID source of the adapters (own or forwarded) and their latency are unpublished.
- Mode lists for the VITURE Pro Mobile Dock and RayNeo JoyDock HDMI input were not retrievable.

## 7. Per-product fact sheets (display, rates, input, chips, price)

### Takeaway
The wired field splits into 1080p-per-eye glasses (XREAL Air / One family, VITURE Pro / Pro 2, RayNeo, Lenovo, ASUS, TCL, Rokid Max) and 1200p-per-eye glasses (VITURE Luma / Beast, XREAL 1S, possibly Rokid Max 2), all fed by USB-C DP Alt Mode. No maker publishes a DP version, a lane count, a 720p mode or a 50 Hz mode; new prices run from about USD 249 (Rokid Max 2 on sale 2026-10-12, Lenovo Legion Glasses 2 in April 2026) to 9,995 SEK (2026-10-12) / USD 849.99 (May 2026) (ROG XREAL R1).

Common to the wired display models below (not INMO Air 3, RayNeo X3 Pro or Rokid Station 2): input is USB-C with DisplayPort Alt Mode, no built-in battery in the glasses (Goovis: not stated), power from the source. DP version and lane count are not published for any of them except Lenovo Gen 1 (DP 1.2).

### Cited Findings

#### XREAL Air (older)
- 1920x1080 per eye, 46 degree FOV, about 77 g, MR-space rates 60 and 72 Hz, no cameras. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- Sony micro-OLED, 1080p; USB-C for power and DP Alt Mode; no compute unit; accelerometer, gyroscope, magnetometer and proximity sensors. [P][S] — [GSMArena review](https://m.gsmarena.com/xreal_air_ar_glasses_and_xreal_beam_review-amp-59478.php)
- EDID: 1920x1080 at 60 / 90 / 120 Hz only (section 1). A retailer spec sheet states 120 Hz in 2D and 90 Hz in the 3840x1080 3D mode. [E][S][R]
- Price today: not found.

#### XREAL Air 2 and Air 2 Pro (older)
- 1920x1080 per eye, 46 degree FOV, about 72 g (Air 2) and 75 g (Air 2 Pro), MR-space rates 60 / 72 / 90 / 120 Hz. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- Retailer spec sheets: Sony micro-OLED, up to 120 Hz, up to 500 nits; consoles and Lightning devices need the XREAL Beam. [R] — Estonian e-tailer, seen 2026-10-12, link withheld
- Air 2 Pro EDID carries product ID 0x3135 and no DisplayID 2.0 block; its timings were not seen. [E][S] — [freedesktop issue 53](https://gitlab.freedesktop.org/drm/misc/kernel/-/issues/53)
- Listed for the XREAL Hub. [M] — [XREAL EU store, Hub](https://eu.shop.xreal.com/products/xreal-hub)
- Price 2026-10-12: Air 2 Pro EUR 469, Air 2 EUR 339. [R] — Estonian drone / electronics e-tailer, link withheld

#### XREAL Air 2 Ultra (older)
- 1920x1080 per eye, 52 degree FOV, about 80 g, MR-space rates 60 / 72 / 90 / 120 Hz, 6DoF through dual grayscale cameras, no RGB camera. [M] — [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- EDID, price, monitor-only use without Nebula / SDK: not found.

#### XREAL One (announced 2024-12-04)
- Sony 0.68-inch micro-OLED, 1920x1080 per eye, 50 degree FOV, up to 120 Hz, 600 nits perceived peak, 84 g (docs.xreal.com says 82 g), XREAL X1 chip, motion-to-photon 3 ms, Optic Engine 3.0, 3-mode electrochromic dimming, software IPD. [M] — [XREAL spec](https://tutorials.xreal.com/docs/glasses/one-series/spec); [XREAL EU store](https://eu.shop.xreal.com/products/xreal-one)
- Display modes in launch coverage: Air Casting, Body Anchor, Smooth Follow; 147-inch spatial screen, up to 310 inches in ultra-wide. [P] — [Mixed](https://mixed-news.com/en/xreal-introduces-new-ar-glasses-with-native-3dof-tracking-larger-field-of-view-and-in-house-x1-chip/)
- Price: EUR 399.00 incl. tax (regular EUR 549.00) at the XREAL EU store, 2026-10-12; pre-order prices 2024-12-04 were USD 499 / GBP 449 / EUR 549. [M][P] — [XREAL EU store](https://eu.shop.xreal.com/products/xreal-one); [CGMagazine](https://www.cgmagonline.com/news/xreal-unveils-xreal-one-series/)

#### XREAL One Pro (scheduled for March 2025 at announcement)
- Sony 0.55-inch micro-OLED, 1920x1080 per eye, 57 degree FOV, up to 120 Hz, 700 nits, 87 g, X1 chip, Optic Engine 4.0; sizes M (IPD 57-66 mm) and L (66-75 mm). [M] — [XREAL EU store](https://eu.shop.xreal.com/products/xreal-one-pro)
- Firmware of 2026-07-22 adds official 90 fps input in UltraWide and fixes REAL 3D black screens, dropped frames and tearing. [P] — [iPhone in Canada](https://www.iphoneincanada.ca/2026/07/23/xreal-one-pro-firmware-update-adds-90fps-ultrawide-mode-and-better-controls/)
- Price: EUR 599.00 (regular EUR 689.00) at the XREAL EU store on 2026-10-12; pre-order prices 2024-12-04 were USD 599 / GBP 549 / EUR 649. [M][P] — [XREAL EU store](https://eu.shop.xreal.com/products/xreal-one-pro); [CGMagazine](https://www.cgmagonline.com/news/xreal-unveils-xreal-one-series/)
- Other price snapshots seen 2026-10-12: Estonian e-tailer EUR 647.30; Danish price-comparison lowest DKK 4,622; Norwegian price-comparison lowest NOK 7,118. A Swedish tech site says XREAL cut the US price to USD 599 permanently in August 2026. [R][S] — retailer and comparison pages, links withheld; [tech-insider.org (sv)](https://tech-insider.org/sv/?p=2753)

#### XREAL 1S (launched about January 2026)
- Reported by the press in January 2026 together with the XREAL Neo power hub. [P][S] — [Ubergizmo](https://www.ubergizmo.com/2026/01/xreal-1s-glasses-and-neo-power-hub)
- Sony 0.68-inch micro-OLED, 1920x1200 per eye (3840x1200 binocular), 52 degree FOV, 700 nits, up to 120 Hz (spec page: "Fixed 90 Hz, up to 120 Hz"), 82 g (docs.xreal.com), X1 spatial chip with native 3DoF, 108 % sRGB, contrast 100,000:1. [M] — [XREAL spec](https://tutorials.xreal.com/docs/glasses/one-series/spec); [XREAL EU store](https://eu.shop.xreal.com/products/xreal-1s); [docs.xreal.com](https://docs.xreal.com/XREALDevices/XREAL%20Glasses)
- Price: EUR 499.00 incl. tax at the XREAL EU store, 2026-10-12; Austrian price-comparison site lowest EUR 449.90 across 7 offers, data stamped 2026-10-12 16:52. [M][R] — [XREAL EU store](https://eu.shop.xreal.com/products/xreal-1s); comparison site, link withheld

#### ROG XREAL R1 (pre-orders May 2026)
- ASUS spec: Sony 0.55-inch micro-OLED, 1920x1080 per eye, 120 Hz or 240 Hz with Frame rate Boost, panel response 0.01 ms, motion-to-photon 3 ms, 700 nits max, 106 % sRGB, 57 degree FOV, 40 PPD, one USB-C port (DP Alt Mode). ROG Control Dock: DisplayPort x1, HDMI x2, USB-C DP front port, HDR10. The page does not name a chip; press says X1. [M][P][S] — [ASUS ROG spec](https://rog.asus.com/us/glasses/rog-xreal-r1/spec/); [Road to VR](https://roadtovr.com/rog-xreal-r1-pre-orders-now-live-240hz-microoled-gaming-glasses-priced-at-850/)
- XREAL's doc: native 3DoF, Anchor and Follow modes, three-level electrochromic dimming, Instant 3D, Switch needs the ROG Control Dock. [M] — [XREAL R1 doc](https://tutorials.xreal.com/docs/glasses/r1)
- Price: USD 849.99 at pre-order (May 2026); 9,995 SEK at a Swedish PC e-tailer on 2026-10-12. [P][R] — Road to VR (above); retailer, link withheld

#### XREAL xbx a01 (entry-level; launch date not found)
- SeeYa 0.6-inch micro-OLED, 2D 1920x1080 / 3D 3840x1080, up to 120 Hz, 50 degree FOV, 1600 nits eye / 6000 nits screen brightness, 62 g (56 g without the front frame), HDR10 and AI-HDR, 5 V / 1 A, IPD 54.5-74.5 mm; chip and price not listed. [M] — [xbx a01 spec](https://tutorials.xreal.com/docs/glasses/xbxa01/spec)
- Needs a DP video source; DP audio by default. [M] — [xbx a01 FAQ](https://tutorials.xreal.com/docs/glasses/xbxa01/faq)
- XRLinuxDriver lists it as "xbx a01+", unofficial SDK, needing testing. [M] — [XRLinuxDriver README](https://github.com/wheaney/XRLinuxDriver)

#### XREAL accessories
- XREAL Eye: EUR 119.00 (2026-10-12), camera module for the One series (the EU page's title calls it an eye-tracking module; launch coverage describes a 1.5 g, up to 12 MP camera); needs the Beam Pro for mixed-reality video. [M][P] — [XREAL EU store, Eye](https://eu.shop.xreal.com/products/xreal-eye); [Mixed](https://mixed-news.com/en/xreal-introduces-new-ar-glasses-with-native-3dof-tracking-larger-field-of-view-and-in-house-x1-chip/)
- XREAL Hub: EUR 49.90 (2026-10-12), 45 W charging, up to 120 Hz passthrough, for the Air family. [M] — [XREAL EU store, Hub](https://eu.shop.xreal.com/products/xreal-hub)

#### VITURE One and One Lite (older; One Lite shipping from 2024-02)
- 1080p per eye, 60 Hz only, about 55 PPD, 43 degree FOV, 1,800 nits, contrast 50,000:1, 120-inch virtual screen, IPD 57.5-69.5 mm; native full SBS 3840x1080. [M] — [VITURE Pro/One page](https://www.viture.com/academy/xr-glasses/pro-one-series)
- One Lite price at launch 2024-02: USD 349; one source gives 38.4 degree FOV and 78 g, conflicting with VITURE's 43 degrees. [P][S] — [MacTech](https://www.mactech.com/2024/02/07/viture-one-lite-xr-glasses-are-now-shipping-and-compatible-with-apple-spatial-video/amp/); [Reality Atlas](https://www.reality-atlas.com/hardware/vitureonelite)
- Neckband and One Mobile Dock support 60 Hz only. [M] — [VITURE Pro/One page](https://www.viture.com/academy/xr-glasses/pro-one-series)

#### VITURE Pro XR (announced 2024-05-23; older)
- 1080p per eye, 120 / 90 / 60 Hz, about 49 PPD, 46 degree FOV, 4,000 nits, contrast 100,000:1, 135-inch screen, electrochromic dimming. [M] — [VITURE Pro/One page](https://www.viture.com/academy/xr-glasses/pro-one-series)
- Listed at USD 549, shown discounted to USD 459 at the time of the 2024-05-23 report; 78 g. [P][S] — [Notebookcheck](https://www.notebookcheck.net/Viture-unveils-Viture-Pro-XR-glasses-with-120-Hz-refresh-rate-electrochromic-dimming-and-Harman-sound.840640.0.html)
- Field reports: "rainbow screen" at 720p; 45 to 55 ms chain latency at 1080p60 with an HDMI-to-USB-C adapter. [U][O] — [XR_GLASOGON_KOMPATIBILITET.md](file:///C:/Users/lenny/Desktop/Dr%C3%B6nare/OpenVRX/OpenVRX/research/XR_GLASOGON_KOMPATIBILITET.md)

#### VITURE Luma, Luma Pro, Luma Ultra, Luma Cyber (Luma Ultra launched 2025-08-27)
- Up to 1920x1200 per eye (3840x1200 combined), up to 120 Hz, 108 % sRGB, 3D supported. FOV 50 degrees (Luma) and 52 degrees (Pro, Ultra, Cyber); brightness 1,000 nits (Luma, Pro) and 1,500 nits (Ultra, Cyber); virtual screen 146 / 152 inches. [M] — [VITURE Luma page](https://www.viture.com/academy/xr-glasses/luma-series)
- Luma Ultra: one RGB and two depth cameras, native 6DoF and hand gestures; press quotes about 1,250 nits and 83 g; birdbath optics, Sony micro-OLED. Needs the Adapter Ultra; the HDMI XR Adapter does not support it. [M][P][S] — [VITURE Luma](https://www.viture.com/luma); [Road to VR](https://roadtovr.com/viture-luma-ultra-ar-glasses-release-oled)
- Luma Cyber is the VITURE x Cyberpunk 2077 edition; its price is not shown on VITURE's Luma page. [M] — [VITURE Luma page](https://www.viture.com/academy/xr-glasses/luma-series)
- Prices 2026-10-12 on VITURE's site (USD): Luma 399, Luma Pro 499, Luma Ultra 599. Luma Ultra launched 2025-08-27 at USD 599. [M][P][S] — [VITURE](https://www.viture.com/); [iDevice](https://idevice.com/smart-glasses/viture-luma-ultra/roadmap?view=price)
- EU snapshots seen through search on 2026-10-12: Luma Pro best price EUR 485.91 on a French comparison page stamped 2026-07-02, EUR 550.52 to 589.90 at German / Italian / Swiss / Lithuanian / Slovenian e-tailers; Luma Ultra EUR 639 (Dutch e-tailer, open-box class listing) and EUR 646.90 gross (Polish e-tailer). [R][S] — retailer pages, links withheld

#### VITURE Beast and Phantom Beast (launch date not verified; 1200p firmware from April 2026)
- Up to 1920x1200 per eye, up to 120 Hz, 58 degree FOV, up to 1,250 nits perceived, contrast at least 100,000:1, 174 inches at 4 m, 9-level electrochromic dimming, built-in 3DoF (VisionPair). Display modes Default / UltraWide / 3D / Side; positioning Anchor / Smooth Follow / 0DoF. [M] — [VITURE Beast page](https://www.viture.com/academy/xr-glasses/the-beast)
- Launched at 1080p; 1200p arrived with firmware dated 2026-04-27 or later (units calibrated for 1200p cannot run older firmware); a German review from April 2026 reported that the 120 Hz setting was not saved. [M][P][S] — [VITURE Beast page](https://www.viture.com/academy/xr-glasses/the-beast); [Android Central](https://www.androidcentral.com/wearables/viture-beast-abxylute-s9v-launch)
- On 2026-07-08 its EDID still showed a native 1920x1080 at 60 Hz timing (section 1). [E][U] — [NVIDIA developer forum](https://forums.developer.nvidia.com/t/unable-to-read-edid-for-viture-beast-xr-glasses-usb-c-dp-alt-mode-but-every-userspace-i2c-over-aux-read-through-the-drivers-own-i2c-adapter-suc/376114)
- Price: USD 549 (Beast) and USD 599 (Phantom Beast, pre-order) on VITURE's site, 2026-10-12; EUR 599 at a Dutch / German / Belgian e-tailer. [M][R][S] — [VITURE](https://www.viture.com/); retailer, link withheld; launch coverage: [Road to VR](https://roadtovr.com/vitures-widest-field-of-view-ar-glasses-are-now-available-at-amazon-best-buy/)

#### VITURE Pro 2 (August 2026)
- Sony micro-OLED, 1920x1080 per eye (3840x1080 combined), 120 / 90 / 60 Hz, 50 degree FOV, 1,600 nits, 63 g, 146 inches at 4 m, 43 PPD, diopter 0 to -5.0 D. Switch and Switch 2 need a VITURE dock or adapter; PlayStation and Xbox need the Pro Mobile Dock. [M] — [VITURE Pro 2 page](https://www.viture.com/academy/xr-glasses/pro-2); [VITURE Pro 2 product page](https://www.viture.com/pro2)
- Price: USD 299 (VITURE site 2026-10-12; USD 378 with the Mobile Dock Mini); Japan JPY 49,880 incl. tax from 2026-08-20. XRLinuxDriver lists it as "Pro 2 XR". [M][P][S] — [VITURE](https://www.viture.com/); [The Gadgeteer, 2026-08-06](https://the-gadgeteer.com/2026/08/06/viture-pro-2-xr-glasses/); [MoguraVR](https://moguravr.com/viture-pro-2-xr-glasses-release)

#### Rokid Max (global press release 2023-03-21; older)
- Sony Semiconductor panel, 1920x1080 per eye, 600-nit peak, 120 Hz, 50 degree FOV, 215-inch screen at 6 m. [M][P][S] — [Business Wire](https://www.businesswire.com/news/home/20230321005671/en/Rokid-Unveils-Rokid-Max-AR-Glasses-With-Premium-MAX-Theater-Experience); [New Atlas](https://newatlas.com/wearables/rokid-max-ar-glasses/)
- XRLinuxDriver lists "Rokid Max, Air" as supported through an official, closed-source SDK. [M] — [XRLinuxDriver README](https://github.com/wheaney/XRLinuxDriver)

#### Rokid Max 2 and AR Spatial
- 120 Hz, 600 nits, 50 degree FOV, 75 g, built-in 0 to -6 D correction. Resolution is stated as 1920x1200 by The Gadgeteer and as 1920x1080 per eye by retailer listings (unresolved). [P][R] — [The Gadgeteer, 2026-06-17](https://the-gadgeteer.com/?p=511195)
- Price at Rokid's global store on 2026-10-12: Max 2 USD 249.00 (regular USD 429.00), AR Spatial USD 399.00 (regular USD 598.00); MSRP USD 449 with street price about USD 399 in June 2026. [M][P] — [Rokid Max 2](https://global.rokid.com/products/rokid-max-2-ar-glasses); [Rokid AR Spatial](https://global.rokid.com/products/rokid-ar-spatial); [The Gadgeteer](https://the-gadgeteer.com/?p=511195)
- AR Spatial is the glasses plus Station 2 (8 GB / 128 GB, Wi-Fi 6, Bluetooth 5.2, 5,000 mAh at 18 W). [M] — [Rokid AR Spatial](https://global.rokid.com/products/rokid-ar-spatial)
- Switch 2 test gave a blank screen (section 1). [P][S] — [TechRadar](https://www.techradar.com/gaming/virtual-reality-gaming/xreal-already-working-on-a-solution-to-nintendo-switch-2s-devastating-lack-of-ar-glasses-support)
- Rokid Max Pro: not on Rokid's global store page (2026-10-12), no spec found. [M] — [Rokid global store](https://global.rokid.com/)

#### RayNeo Air 2 and Air 2s (older)
- Sony micro-OLED, 1920x1080 per eye, 120 Hz, configurable to 60 or 120 Hz; the Air 2s adds refresh-rate, Whisper and colour settings on the glasses. [R][U][M] — Israeli retailer page, link withheld; [Hacker News](https://news.ycombinator.com/item?id=42232741); [RayNeo FAQ Air 3](https://www.rayneo.com/pages/support-faq-air3)
- RayNeo FAQ (Air 2 / NXTWEAR S / S+): needs USB-C with DP; 3D works only on a direct DP connection, 2D only through an adapter; the Joydock needs current firmware. [M] — [RayNeo FAQ Air 2](https://www.rayneo.com/pages/faq-air-2)
- Not listed on RayNeo's store page on 2026-10-12. [M] — [RayNeo store](https://www.rayneo.com/)

#### RayNeo Air 3s and Air 3s Pro (launch date not verified)
- Air 3s: RayNeo "5th-gen" HueView micro-OLED, 1080p, 120 Hz (60 Hz default), 46 degree FOV, 650 nits, 76 g; USD 269.00 on RayNeo's store, 2026-10-12. [M] — [RayNeo Air 3s](https://www.rayneo.com/products/rayneo-air-3s-xr-glasses)
- Air 3s Pro: 0.6-inch SeeYa micro-OLED, 2D 1920x1080 / 3D 3840x1080, 46 degree FOV (Tom's Hardware: 47), 76 g, brightness listed as 650 nits in the sidebar and 1,200 nits in the text of the same page; USD 279.00 sale (regular from USD 299.00) on 2026-10-12. [M][P][S] — [RayNeo bundle page](https://www.rayneo.com/products/air-3s-joydock); [RayNeo store](https://www.rayneo.com/); [Tom's Hardware](https://www.tomshardware.com/peripherals/wearable-tech/rayneo-air-3s-pro-ar-glasses-review)
- 3D mode is switched by pressing the volume button on the left temple and the brightness button on the right one together, and it shuts off when the cable is unplugged. [M] — [RayNeo 2D / 3D page](https://www.rayneo.com/pages/service-air3s-2d-3d-mode)
- Switch 2 test gave a blank screen on the Air 3S. [P][S] — [TechRadar](https://www.techradar.com/gaming/virtual-reality-gaming/xreal-already-working-on-a-solution-to-nintendo-switch-2s-devastating-lack-of-ar-glasses-support)

#### RayNeo Air 4 Pro (CES 2026)
- 0.6-inch SeeYa micro-OLED, Full HD, up to 120 Hz, 46 degree FOV, up to 1,200 nits, contrast 200,000:1, 98 % DCI-P3, 76 g; HDR10 needs both device and content to output HDR; Vision 4000 does AI SDR-to-HDR upscaling; no 3DoF; basic viewing needs no app. [M] — [RayNeo Air 4 Pro](https://www.rayneo.com/products/rayneo-air-4-pro-ar-smart-glasses)
- Price: USD 299.00 on RayNeo's store, 2026-10-12; with HDMI adapter USD 339, with JoyDock USD 349. Launch reporting dates the CES debut to January 2026; sales start dates differ by source. [M][P][S] — [RayNeo store](https://www.rayneo.com/); [Android Authority](https://www.androidauthority.com/rayneo-air-4-pro-launch-3630910/)

#### RayNeo GT and GT Max (marked NEW on the store; date not found)
- GT: 0.6-inch SeeYa micro-OLED, 1920x1080, 2D 120 Hz / 3D 60 Hz, 46 degree FOV, 336 nits pinned / 1,200 nits unpinned, Vision 4000 + Zone 360 3DoF, 68 g, USD 329.00 (2026-10-12). GT Max: 59 degree FOV, 78 g, up to 1,200 nits, USD 429.00 (2026-10-12). Dolby Vision only with the Pocket TV Pro. [M] — [RayNeo GT](https://www.rayneo.com/products/rayneo-gt-ar-glasses); [RayNeo GT Max](https://www.rayneo.com/products/rayneo-gt-max-ar-glasses)

#### RayNeo X3 Pro
- Standalone AI + AR glasses with a Snapdragon AR1 Gen 1; USD 1,299.00 on RayNeo's store 2026-10-12. Not a monitor. [M] — [RayNeo blog](https://www.rayneo.com/blogs/news/rayneo-wired-vs-wireless-models-explained); [RayNeo store](https://www.rayneo.com/)

#### Lenovo Legion Glasses Gen 1 (older) and Gen 2 (February 2025)
- Gen 1: 1920x1080 per eye, 60 Hz, 270 nits, 96 g, USB-C 3.2 with DP 1.2; a compatibility whitelist exists. [P][M][S] — [Mixed](https://mixed-news.com/en/lenovo-legion-glasses-2-new-ar-glasses-with-gaming-focus-coming-in-february-for-399); [Lenovo support](https://support.lenovo.com/ph/en/accessories/acc500321-legion-glasses-overview-and-service-parts)
- Gen 2: micro-OLED 1920x1080 per eye, 60 / 90 / 120 Hz, 800 nits, 43.5 degree FOV (retail data feeds give 38.5), 65 g, contrast 200,000:1, 126-inch virtual screen, 2D / 3D toggle; plugs into Legion Go and any USB-C source with DP. Panel maker not found. [P][R] — [Mixed](https://mixed-news.com/en/lenovo-legion-glasses-2-new-ar-glasses-with-gaming-focus-coming-in-february-for-399); [GSMGoTech](https://www.gsmgotech.com/2026/04/lenovo-legion-glasses-2-just-got.html)
- Price Gen 2: USD 399.99 at launch (CES 2025), USD 329.99 in June 2025, USD 249.99 at a large online marketplace and at Lenovo's own store in an article dated 2026-04-12; SGD 425 at a Singapore e-tailer (2026-10-12); JPY 55,000 at the Japan launch (2025-10-24). EU price not found. [P][R][S] — [GSMGoTech](https://www.gsmgotech.com/2026/04/lenovo-legion-glasses-2-just-got.html); [BCN Retail](https://www.bcnretail.com/topics_detail8/20251022_565436.html)
- A Dutch / Belgian e-tailer's text says Gen 1 behaves like a monitor over USB-C with no software. [R][S] — retailer listing, link withheld

#### ASUS AirVision M1 (shown at CES 2024 per press)
- Micro-OLED 0.49-inch, 1920x1080 per eye, 72 Hz, 1,100 nits, 95 % DCI-P3, 58 PPD, FOV listed as 38 (axis not stated), freeform lens, 60 % transparency, 3DoF, 80 g net weight, USB-C. A press report from CES 2024 gives 57 degrees as a viewing angle (unresolved). Price not on the page. [M][P][S] — [ASUS tech spec](https://www.asus.com/displays-desktops/glasses/airvision/asus-airvision-m1/techspec/); [Rozetked](https://rozetked.me/news/31955-asus-airvision-m1)

#### TCL NXTWEAR AIR (January 2022), S (older) and S+ (November 2023)
- AIR: micro-OLED, 2D 1920x1080 / 3D 3840x1080, 60 Hz, 47 degree FOV, 140 inches at 4 m, 75 g, three sensors, ports listed as "USB Type-C" and "HDMI port" (unclear where the HDMI port sits), no battery, 3DoF. [M] — [TCL Sweden spec page](https://www.tcl.com/se/sv/glasses/tcl-nxtwear-air/specifications); [TCL EU spec page](https://tcl.com/eu/en/glasses/tcl-nxtwear-air/specifications)
- S+: micro-OLED 1920x1080, 60 / 120 Hz, 49 degree FOV, 600 nits, 87 g, USB-C with DP; released in Japan 2023-11-22. The original S ran at 60 Hz, 400 nits, 89 g. Launch price USD 399 / GBP 399 / AUD 699. [M][P][S] — [TechRadar](https://techradar.com/computing/virtual-reality-augmented-reality/tcl-has-launched-a-new-pair-of-ar-glasses-with-120hz-oled-screens)
- The TCL FAQ: DP-capable USB-C source required, adapters needed otherwise, 3D not usable on non-DP Android or iPhone. [M] — [TCL FAQ](https://www.tcl.com/gulf/en/support/faq/18335)

#### INMO Air 3 (shipping planned for January 2026)
- Standalone Android 14 glasses with a Sony micro-OLED and a waveguide, 1920x1080, 36 degree diagonal FOV, Snapdragon 8-core, 8 GB / 128 GB, 660 mAh, about 135 g; MSRP USD 1,099 (December 2025), pre-order USD 999, Kickstarter early buyers USD 899 (another source says USD 799 after cashback); shipping planned for January 2026. USB-C video input is not stated. [M][P] — [INMO Air3 spec summary](https://smhn.info/202512-inmo-air3-spec); [INMO store](https://www.inmoxr.com/products/inmo-air3-ar-glasses-all-in-one-full-color-waveguide)

#### Goovis G3 Max, G3X, G3X Pro
- G3 Max: dual 2.5K micro-OLED, up to 120 Hz, 65 degree FOV, 45 PPD, 95 % DCI-P3, 300 g; USB-C video output for the single-cable connection, HDMI only through the HC2.0 adapter; SBS 3D formats. USD 1,199.00 at Goovis' US store and EUR 1,099 (regular EUR 1,500) at its EU store on 2026-10-12. [M] — [Goovis G3 Max](https://www.goovis.com/products/goovis-g3max); [Goovis EU](https://goovis.eu/)
- G3X and G3X Pro: dual 1080p Sony micro-OLED, 190 g, same USB-C / HC2.0 connection; G3X USD 599 (regular USD 799) and EUR 599; G3X Pro USD 699 (regular USD 899) and EUR 699 (2026-10-12). [M] — [Goovis G3X](https://www.goovis.com/products/goovis-g3x); [G3X Pro](https://www.goovis.com/products/goovis-g3x-pro); [Goovis EU](https://goovis.eu/)

#### Sony
- Sony Semiconductor Solutions supplies micro-OLED panels (ECX series) to several makers above; no Sony-branded consumer USB-C DP display glasses turned up. Panel interfaces in Sony's public AR/VR list are MIPI D-PHY or LVDS (section 3). [M] — [Sony Semiconductor](https://www.sony-semicon.com/en/products/microdisplay/oled.html)

### Inferences
- Cheapest new units for a bench test by current list or sale price (2026-10-12): Rokid Max 2 (USD 249 sale), Lenovo Legion Glasses 2 (USD 249.99, April 2026), RayNeo Air 3s (USD 269), Air 3s Pro (USD 279), Air 4 Pro (USD 299), VITURE Pro 2 (USD 299), XREAL One (EUR 399 sale). Models with a named processing chip are XREAL One / One Pro / 1S / ROG R1 (X1) and RayNeo Air 4 Pro / GT / GT Max (Vision 4000); the cheapest of them are XREAL One (EUR 399 sale, 2026-10-12) and RayNeo Air 4 Pro (USD 299, 2026-10-12).
- Two classes are worth testing against 720p60: glasses with a processor in the path (XREAL X1 family, RayNeo Vision 4000) and glasses that look like pure bridges (Air / Air 2, RayNeo Air 3s, Lenovo, Rokid). A positive result on either class would change the advice to feed 1080p60.
- Source disagreements to carry into any table: One weight 82 vs 84 g; VITURE One FOV 43 vs 38.4 degrees; Luma Ultra 1,250 vs 1,500 nits; Rokid Max 2 1920x1200 vs 1920x1080; RayNeo Air 3s Pro 650 vs 1,200 nits; Lenovo Gen 2 FOV 43.5 vs 38.5 degrees; ASUS FOV 38 vs 57.

### Gaps
- DP version and lane count: not published for any model except Lenovo Gen 1 (DP 1.2).
- XREAL Air 2 Ultra price, EDID and non-app use; XREAL Air price today; VITURE One and Pro XR EU prices; Rokid Max Pro; ASUS AirVision M1 price; Lenovo Gen 1 FOV and price; Lenovo Gen 2 EU price.
- Swedish retail prices: only the ROG XREAL R1 (9,995 SEK, 2026-10-12) was found; the other models are priced in USD (maker stores) or EUR (EU snapshots).
- XREAL Aura (Android XR puck, reported as not yet shipping), Epson Moverio BT-40 / BT-45, Huawei Vision Glass, Vufine+ and Sony HMZ-T3W were not researched.
- Rokid Max launch price: search excerpts of launch coverage disagreed (USD 399, 439 pre-sale, 599 list); not resolved.
- Goovis G3 Max panel resolution in pixels (the page says only "2.5K").
