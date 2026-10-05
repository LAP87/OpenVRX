"""Review experiment E7 (copy into gateware/sim/): can the SDRAM writer be given the buffer
the display is showing? Same DUT, clocks and stimulus as sim/test_m2.py::m2_end_to_end
(tb_m2, unmodified RTL); the only knob is REVIEW_DELAY_NS, a delay before the BT.656
stream starts, which slides the input fields against the free-running output frames.

Invariant of a triple buffer: the buffer being written (fb_sdram.cur_buf) is never the
buffer on screen (fb_display.display_buf). Every pixel clock where they are equal (after
the first three publications) is logged to build/review_tb3_<delay>.txt together with the
publication and frame-start times.
"""
import os
import sys
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge, Timer
from cocotb.utils import get_sim_time

HERE = Path(__file__).resolve().parent
GW = HERE.parent
PROJECT = GW.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(GW / 'model'))
import test_m2 as m2  # noqa: E402

V_TOTAL = 40
NFIELDS = 8


def val(sig):
    """int(sig.value), or None while the signal is still X/Z (right after reset)."""
    try:
        return int(sig.value)
    except (ValueError, TypeError):
        return None


@cocotb.test()
async def triple_buffer_invariant(dut):
    delay = int(os.environ.get('REVIEW_DELAY_NS', '0'))
    # 37 ns: field period 888.9 us > frame period 884.4 us (like 59.94 Hz into 60 Hz).
    # REVIEW_TVP_PS = 36800: field period 884.1 us < frame period (a source faster than the output).
    cocotb.start_soon(Clock(dut.tvp_clk, int(os.environ.get('REVIEW_TVP_PS', '37000')), unit='ps').start())
    cocotb.start_soon(Clock(dut.sd_clk, 15.4, unit='ns').start())
    cocotb.start_soon(Clock(dut.pix_clk, 13.4, unit='ns').start())
    dut.rst.value = 1
    dut.ll_mode.value = 0
    dut.tvp_d.value = 0x80
    await Timer(500, unit='ns')
    dut.rst.value = 0
    while not dut.sdram_ready.value:
        await RisingEdge(dut.sd_clk)
    if delay:
        await Timer(delay, unit='ns')

    fb, disp, tim = dut.core.backend.fb, dut.core.backend.disp, dut.core.backend.timing
    pubs, frames, bad = [], [], []

    async def watch_sd():
        while True:
            await RisingEdge(dut.sd_clk)
            await ReadOnly()
            if val(fb.pub_valid) == 1:
                pubs.append((get_sim_time('ns'), val(fb.pub_buf), val(fb.cur_buf)))

    async def watch_pix():
        while True:
            await RisingEdge(dut.pix_clk)
            await ReadOnly()
            y, x, shown, writing, hv = val(tim.y), val(tim.x), val(disp.display_buf), val(fb.cur_buf), val(disp.have_video)
            if None in (y, x, shown, writing, hv):
                continue
            if y == V_TOTAL - 1 and x == 1:               # display_buf was latched at x == 0
                frames.append((get_sim_time('ns'), shown))
            if len(pubs) >= 3 and hv and shown == writing:
                bad.append((get_sim_time('ns'), shown, y))
    cocotb.start_soon(watch_sd())
    cocotb.start_soon(watch_pix())

    for fld in range(NFIELDS):
        for b in m2.field_stream(fld):
            await FallingEdge(dut.tvp_clk)
            dut.tvp_d.value = b

    out = HERE / 'build' / f'review_tb3_{delay}.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as fh:
        fh.write(f'delay {delay}\n')
        for t, pb, cb in pubs:
            nxt = [f for f, _ in frames if f >= t]
            prv = [f for f, _ in frames if f < t]
            fh.write(f'pub {t:.1f} published {pb} writer_then {cb} next_frame_in {nxt[0] - t if nxt else -1:.1f} '
                     f'prev_frame_ago {t - prv[-1] if prv else -1:.1f}\n')
        for t, db in frames:
            fh.write(f'frame {t:.1f} shows {db}\n')
        fh.write(f'violations {len(bad)}\n')
        if bad:
            first, last = bad[0], bad[-1]
            rows = sorted({y for _, _, y in bad})
            fh.write(f'first {first[0]:.1f} buf {first[1]} row {first[2]}; last {last[0]:.1f} row {last[2]}; '
                     f'rows {rows[0]}..{rows[-1]} ({len(rows)} rows)\n')


def run(delay):
    from cocotb_tools.runner import get_runner
    iverilog_bin = PROJECT / '.tools' / 'iverilog' / 'bin'
    if iverilog_bin.exists():
        os.environ['PATH'] = f'{iverilog_bin}{os.pathsep}' + os.environ['PATH']
    os.environ['REVIEW_DELAY_NS'] = str(delay)
    r = get_runner('icarus')
    build = HERE / 'build' / 'tb_m2_review_tb3'
    rtl = [GW / 'rtl' / n for n in ('bt656_rx.v', 'word_packer.v', 'async_fifo.v', 'sdram_burst.v',
                                    'fb_sdram.v', 'dual_clock_ram.v', 'genlock_timing.v', 'ycbcr2rgb.v',
                                    'fb_display.v', 'fb_backend.v', 'm2_core.v')]
    r.build(sources=rtl + [HERE / 'sdram_model.v', HERE / 'tb_m2.v'], hdl_toplevel='tb_m2',
            build_dir=build, always=False, timescale=('1ns', '1ps'))
    r.test(hdl_toplevel='tb_m2', test_module='test_review_tb3', test_dir=HERE, build_dir=build,
           testcase='triple_buffer_invariant')
    return (HERE / 'build' / f'review_tb3_{delay}.txt').read_text()


def closest(txt):
    """(distance in ns, line) of the publication nearest to a frame start; negative = just after it."""
    best = None
    for l in txt.splitlines():
        if not l.startswith('pub'):
            continue
        q = l.split()
        nxt, prv = float(q[7]), float(q[9])
        d = nxt if (nxt >= 0 and (prv < 0 or nxt <= prv)) else -prv
        if best is None or abs(d) < abs(best[0]):
            best = (d, l)
    return best


def sweep(tvp_ps, label):
    os.environ['REVIEW_TVP_PS'] = str(tvp_ps)
    # pass 1: no delay, learn how far each publication is from the next frame start
    base = run(0)
    gaps = [float(l.split()[7]) for l in base.splitlines() if l.startswith('pub')][3:6]
    print(f'{label}: pass 1, no delay: publication -> next frame start (ns) for publications 3..5: {gaps}',
          '|', [l for l in base.splitlines() if l.startswith('violations')])
    # pass 2: slide the stream so that one publication lands on a frame start, +-4 byte periods around it
    target = min(g for g in gaps if g >= 160)
    for n in range(-4, 5):
        d = int(round(target + n * 37))
        txt = run(d)
        v = [l for l in txt.splitlines() if l.startswith(('violations', 'first'))]
        dist, line = closest(txt)
        print(f'{label}: delay {d:7d} ns: nearest publication {dist:+8.1f} ns from a frame start | {" | ".join(v)}')


if __name__ == '__main__':
    which = sys.argv[1:] or ['slow', 'fast']
    if 'slow' in which:
        sweep(37000, 'input slower than output')
    if 'fast' in which:
        sweep(36800, 'input faster than output')
