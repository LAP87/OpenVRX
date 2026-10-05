"""Review experiment E6 (copy into gateware/sim/): low-latency mode with fields whose active
line counts alternate by one, as BT.656 NTSC does (244 / 243). Same DUT and clocks as
sim/test_m2.py::m2_low_latency (tb_m2, unmodified RTL); only the stimulus differs:
even fields have 12 active lines, odd fields 11.

fb_display takes `lines` for the frame from the PREVIOUS field (fb_backend: s_ll_lines).
Question: what is on the bottom output rows when an 11-line field is shown with lines = 12?
The result is written to build/review_ll.txt.
"""
import os
import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge, Timer

HERE = Path(__file__).resolve().parent
GW = HERE.parent
PROJECT = GW.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(GW / 'model'))
import bt656  # noqa: E402
import test_m2 as m2  # noqa: E402

VBI, V_ACTIVE, LINE_BYTES = 2, 36, 1716
OUT = HERE / 'build' / 'review_ll.txt'


def val(sig):
    """int(sig.value), or None while the signal is still X/Z (right after reset)."""
    try:
        return int(sig.value)
    except (ValueError, TypeError):
        return None


def nlines(field):
    return 12 if field % 2 == 0 else 11


def field_stream(field):
    f = field & 1
    data = bytearray()
    for i in range(VBI + nlines(field)):
        v = 1 if i < VBI else 0
        act = bt656.blanking(1440) if v else m2.active_bytes(field, i - VBI)
        data += bytes([0xFF, 0, 0, bt656.xy(f, v, 1)]) + bt656.blanking(LINE_BYTES - 1440 - 8)
        data += bytes([0xFF, 0, 0, bt656.xy(f, v, 0)]) + act
    return bytes(data)


def px(field, src, x):
    sx = ((x - 160) * 3) // 4
    cb, _, cr = m2.sample(field, src, sx & ~1)
    _, y, _ = m2.sample(field, src, sx)
    return m2.to_rgb(y, cb, cr)


@cocotb.test()
async def ll_alternating_fields(dut):
    cocotb.start_soon(Clock(dut.tvp_clk, 37, unit='ns').start())
    cocotb.start_soon(Clock(dut.sd_clk, 15.4, unit='ns').start())
    cocotb.start_soon(Clock(dut.pix_clk, 13.4, unit='ns').start())
    dut.rst.value = 1
    dut.ll_mode.value = 1
    dut.tvp_d.value = 0x80
    await Timer(500, unit='ns')
    dut.rst.value = 0

    from cocotb.utils import get_sim_time
    line1_done = {}                           # field -> time its line 1 had been sent
    end_of_line1 = (VBI + 2) * LINE_BYTES

    async def feed(nfields):
        for fld in range(nfields):
            for i, b in enumerate(field_stream(fld)):
                await FallingEdge(dut.tvp_clk)
                dut.tvp_d.value = b
                if i == end_of_line1:
                    line1_done[fld] = get_sim_time('ns')
    feeder = cocotb.start_soon(feed(9))

    frames = []                               # [start time, fb_display.lines, {row: [(x, rgb)]}]

    async def watch():
        out_y, x, cur = 0, 0, None
        while True:
            await RisingEdge(dut.pix_clk)
            await ReadOnly()
            ty, tx = val(dut.core.backend.timing.y), val(dut.core.backend.timing.x)
            if ty is None or tx is None:
                continue                          # still X right after reset
            if ty == 0 and tx == 0:
                cur = [get_sim_time('ns'), None, {}]
                frames.append(cur)
                out_y, x = 0, 0
            if cur is not None and val(dut.de) == 1:
                if cur[1] is None:
                    cur[1] = val(dut.core.backend.disp.lines)
                if x in (221, 465, 709, 953):
                    cur[2].setdefault(out_y, []).append((x, (val(dut.r), val(dut.g), val(dut.b))))   # None: RAM not written yet
                x += 1
                if x == 1280:
                    x, out_y = 0, out_y + 1
    cocotb.start_soon(watch())
    await feeder
    await Timer(200_000, unit='ns')

    report = []
    for start, lines_used, rows in frames:
        shown = max((f for f, t in line1_done.items() if t <= start), default=None)
        if shown not in (5, 6) or len(rows) < V_ACTIVE:
            continue
        report.append(f'frame showing field {shown} ({nlines(shown)} active lines; previous field had '
                      f'{nlines(shown - 1)}): fb_display.lines = {lines_used}')
        for oy in (0, 29, 30, 32, 33, 34, 35):
            got = [q for _, q in rows[oy]]
            who = []
            for f in (shown, shown - 1, shown - 2):
                for sl in range(12):
                    if got == [px(f, sl, xx) for xx, _ in rows[oy]]:
                        who.append(f'field {f} line {sl}')
            report.append(f'   output row {oy:2d}: shows {who or "no line of fields " + str((shown - 2, shown))}')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    nl = chr(10)
    OUT.write_text(nl.join(report) + nl)
    dut._log.info(nl + nl.join(report))


def test_review_ll():
    from cocotb_tools.runner import get_runner
    iverilog_bin = PROJECT / '.tools' / 'iverilog' / 'bin'
    if iverilog_bin.exists():
        os.environ['PATH'] = f'{iverilog_bin}{os.pathsep}' + os.environ['PATH']
    r = get_runner('icarus')
    build = HERE / 'build' / 'tb_m2_review_ll'
    rtl = [GW / 'rtl' / n for n in ('bt656_rx.v', 'word_packer.v', 'async_fifo.v', 'sdram_burst.v',
                                    'fb_sdram.v', 'dual_clock_ram.v', 'genlock_timing.v', 'ycbcr2rgb.v',
                                    'fb_display.v', 'fb_backend.v', 'm2_core.v')]
    r.build(sources=rtl + [HERE / 'sdram_model.v', HERE / 'tb_m2.v'], hdl_toplevel='tb_m2',
            build_dir=build, always=True, timescale=('1ns', '1ps'))
    r.test(hdl_toplevel='tb_m2', test_module='test_review_ll', test_dir=HERE, build_dir=build,
           testcase='ll_alternating_fields')
