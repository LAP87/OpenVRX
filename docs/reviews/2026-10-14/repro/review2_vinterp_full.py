"""VI-1: which two source lines and which weight fb_display.v (VINTERP = 1, buffer mode) uses for
every output line, in the full 720-line geometry (Core's sim/test_fb.py checks VINTERP on a small
picture). genlock_timing.v free-running (lock = 0, the same as video_timing.v) with a short line
drives fb_display.v; the testbench logs src_cur, src_b_cur and w_cur at x = 3 of every active
line. One frame per (field line count, upper or lower field); the publication and frame_low
change during the vertical blanking before it.

Expected, from the mapping in fb_display.v's header: output line j sits at source position
p = (j + 1/2) * lines / 720 - 1/4 (upper field) or - 3/4 (lower field). Above line 0 (p < 0) the
line shown is 0, unblended. Otherwise s = floor(p), and the weight of line s + 1 is frac(p) in
eighths rounded half up; at the last line s + 1 is clamped to s, so the weight does not matter.
Compared as (first line, second line, weight) with weight 0 meaning "first line alone".

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core python review2_vinterp_full.py
"""
import os
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
RTL = CORE / 'gateware' / 'rtl'
WORK = CORE / 'gateware' / 'sim' / 'build' / 'review2_vinterp_full'
CASES = [(lines, low) for lines in (240, 242, 243, 244, 287, 288) for low in (0, 1)]

TB = r'''
`timescale 1ns/1ps
`default_nettype none
module tb;
    reg clk = 0, rst = 1;
    always #5 clk = ~clk;
    wire [11:0] x, y;
    wire de, hs, vs, fs, trg;
    genlock_timing #(.H_ACTIVE(64), .H_FP(4), .H_SYNC(4), .H_BP(8)) t (
        .clk(clk), .rst(rst), .lock(1'b0), .trig(1'b0), .h_alt(1'b0),
        .x(x), .y(y), .de(de), .hsync(hs), .vsync(vs), .frame_start(fs), .triggered(trg));
    reg        pub_t = 0, flow = 0;
    reg  [9:0] pub_l = 240;
    wire       ft, ff; wire [9:0] fl; wire [1:0] fsl; wire [12:0] ra; wire [10:0] rb;
    wire [7:0] r, g, b, yo, cbo, cro; wire deo, hso, vso, hv;
    fb_display #(.V_TOTAL(750), .V_ACTIVE(720), .H_WIN0(0), .H_WIN(48), .VINTERP(1)) dut (
        .clk(clk), .rst(rst), .x(x), .y(y), .de(de), .hsync(hs), .vsync(vs),
        .pub_toggle(pub_t), .pub_lines(pub_l), .frame_low(flow),
        .fetch_toggle(ft), .fetch_line(fl), .fetch_slot(fsl), .fetch_first(ff),
        .ll(1'b0), .ll_lines(10'd0), .ll_alive(1'b0), .ll_triggered(1'b0), .ll_low(1'b0),
        .lb_raddr(ra), .lb_rdata(32'd0), .lb_raddr_b(rb), .lb_rdata_b(32'd0),
        .r(r), .g(g), .b(b), .yo(yo), .cbo(cbo), .cro(cro), .de_o(deo), .hs_o(hso), .vs_o(vso), .have_video(hv));
    integer f, k, frame = -1, n_case;
    reg [10:0] lines_v [0:63];
    reg        low_v   [0:63];
    initial begin
        $readmemh("cases.hex", lines_v);
        $readmemh("lows.hex", low_v);
        f = $fopen("log.txt", "w");
        #100 rst = 0;
    end
    // publish the next case during the blanking (y = 730), before the frame start at y = 749
    always @(posedge clk) begin
        if (!rst && x == 0 && y == 730) begin
            frame = frame + 1;
            if (frame == N) begin $fclose(f); $finish; end
            pub_l <= lines_v[frame]; pub_t <= ~pub_t; flow <= low_v[frame];
        end
        if (!rst && frame >= 0 && x == 3 && y < 720)
            $fwrite(f, "%0d %0d %0d %0d %0d\n", frame, y, dut.src_cur, dut.src_b_cur, dut.w_cur);
    end
    parameter N = 1;
endmodule
'''


def expected(lines, low, j):
    p = Fraction(2 * j + 1, 2) * lines / 720 - Fraction(3 if low else 1, 4)
    if p < 0:
        return (0, 0, 0)
    s = min(int(p), lines - 1)
    frac = p - int(p)
    w = min(8, int(frac * 8 + Fraction(1, 2)))
    b = min(s + 1, lines - 1)
    return (s, s, 0) if w == 0 or b == s else (s, b, w)


def got(s, b, w):
    return (s, s, 0) if w == 0 or b == s else (s, b, w)


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    (WORK / 'tb.v').write_text(TB)
    (WORK / 'cases.hex').write_text(''.join(f'{l:x}\n' for l, _ in CASES))
    (WORK / 'lows.hex').write_text(''.join(f'{w:x}\n' for _, w in CASES))
    subprocess.run(['iverilog', '-g2012', '-o', 'sim.vvp', '-s', 'tb', f'-Ptb.N={len(CASES)}',
                    str(RTL / 'genlock_timing.v'), str(RTL / 'fb_display.v'), str(RTL / 'cdc_sync.v'),
                    str(RTL / 'vblend.v'), str(RTL / 'ycbcr2rgb.v'), 'tb.v'], cwd=WORK, check=True)
    subprocess.run(['vvp', '-n', 'sim.vvp'], cwd=WORK, check=True, capture_output=True)
    rows = [tuple(map(int, l.split())) for l in (WORK / 'log.txt').read_text().splitlines()]
    bad = 0
    # the frame after each publication shows that case (the scaler takes the count at the frame start)
    for k, (lines, low) in enumerate(CASES):
        fr = [r for r in rows if r[0] == k]
        assert len(fr) == 720, (k, len(fr))
        diff = [(j, got(*r[2:]), expected(lines, low, j)) for j, r in enumerate(fr) if got(*r[2:]) != expected(lines, low, j)]
        bad += len(diff)
        first = [got(*r[2:]) for r in fr[:3]]
        last = [got(*r[2:]) for r in fr[-3:]]
        print(f'lines {lines} {"lower" if low else "upper"}: output lines 0-2 {first}, 717-719 {last}; '
              f'{len(diff)} of 720 differ from the mapping{": " + str(diff[:3]) if diff else ""}')
    print('VINTERP weights as the mapping says, first and last lines included' if bad == 0 else f'{bad} lines differ')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
