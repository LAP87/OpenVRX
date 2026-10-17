"""HD-1 and the HDMI packet check: tmds_link.v's symbol stream (Core sim/tb_hdmi.v, run through
sim/test_hdmi.py's run()) decoded again by a decoder written for this review, separately from
Core's test_hdmi.py. Tables as HDMI 1.4 gives them, in the q[9:0] notation of tmds_encoder.v
(control 00 = 1101010100): TERC4 (table 5-18), video and data island guard bands (5.2.2.1,
5.2.3.3), preambles (table 5-2: video CTL0 = 1, island CTL0 = CTL2 = 1). The BCH parity is
computed with the shift register of hdl-util/hdmi (src/packet_assembler.sv, another open
implementation): s = (s >> 1) ^ (0x83 if (s ^ bit) & 1 else 0), bit 0 first, parity after the
data. The AVI InfoFrame fields are read as CTA-861 version 2.

Modes: HDMI with RGB_FULL = 1 (the build option), hz50 changing every second frame (VIC 4 and
19); HDMI with RGB_FULL = 0; DVI (HDMI = 0).

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core python review2_hdmi_independent.py
"""
import os
import sys
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
sys.path.insert(0, str(CORE / 'gateware' / 'sim'))
import test_hdmi  # noqa: E402  (only its run(): build and simulate tb_hdmi.v)

CTL = {0b00: 0b1101010100, 0b01: 0b0010101011, 0b10: 0b0101010100, 0b11: 0b1010101011}   # {c1, c0}
TERC4 = {0x0: 0b1010011100, 0x1: 0b1001100011, 0x2: 0b1011100100, 0x3: 0b1011100010,
         0x4: 0b0101110001, 0x5: 0b0100011110, 0x6: 0b0110001110, 0x7: 0b0100111100,
         0x8: 0b1011001100, 0x9: 0b0100111001, 0xA: 0b0110011100, 0xB: 0b1011000110,
         0xC: 0b1010001110, 0xD: 0b1001110001, 0xE: 0b0101100011, 0xF: 0b1011000011}
TERC4_D = {v: k for k, v in TERC4.items()}
GB_VIDEO_0_2, GB_VIDEO_1, GB_ISLAND_1_2 = 0b1011001100, 0b0100110011, 0b0100110011
DELAY = 11      # tmds_link.v HDMI: 10 clocks of lead-in plus the encoder register


def ecc(bits):
    s = 0
    for b in bits:
        s = (s >> 1) ^ (0x83 if (s ^ b) & 1 else 0)
    return [s >> k & 1 for k in range(8)]


def to_bytes(bits):
    return [sum(bits[8 * i + k] << k for k in range(8)) for i in range(len(bits) // 8)]


def decode(rows, hdmi=True):
    n = len(rows)
    sym = [(r[5], r[6], r[7]) for r in rows]
    res = dict(islands=[], island_faults=[], video_lines=0, video_lead_faults=0, terc4_in_dvi=0, guard_in_dvi=0)
    i = 0
    while i < n - 44:
        s0, s1, s2 = sym[i]
        if hdmi and s1 == CTL[0b01] and s2 == CTL[0b01]:          # island preamble
            k = i
            while k < n and sym[k][1] == CTL[0b01] and sym[k][2] == CTL[0b01]:
                k += 1
            faults = []
            if k - i != 8:
                faults.append(f'preamble {k - i} clocks')
            gb = [sym[k + j] for j in (0, 1, 34, 35)]
            for j, (g0, g1, g2) in zip((0, 1, 34, 35), gb):
                d0 = TERC4_D.get(g0)
                if g1 != GB_ISLAND_1_2 or g2 != GB_ISLAND_1_2 or d0 is None or d0 >> 2 != 0b11:
                    faults.append(f'guard band at {j}')
            hdr, sub = [], [[] for _ in range(4)]
            for j in range(32):
                c0, c1, c2 = sym[k + 2 + j]
                d0, d1, d2 = TERC4_D.get(c0), TERC4_D.get(c1), TERC4_D.get(c2)
                if None in (d0, d1, d2):
                    faults.append(f'not TERC4 at packet clock {j}')
                    break
                if (d0 >> 3) != (j != 0):
                    faults.append(f'ch0 bit 3 at packet clock {j}')
                hdr.append(d0 >> 2 & 1)
                for q in range(4):
                    sub[q] += [d1 >> q & 1, d2 >> q & 1]
            if len(hdr) == 32:
                if ecc(hdr[:24]) != hdr[24:]:
                    faults.append('header BCH')
                for q in range(4):
                    if ecc(sub[q][:56]) != sub[q][56:]:
                        faults.append(f'subpacket {q} BCH')
                hb = to_bytes(hdr[:24])
                pb = sum((to_bytes(sub[q][:56]) for q in range(4)), [])
                res['islands'].append(dict(at=i, hb=hb, pb=pb[:6], sum=(sum(hb) + sum(pb)) & 0xFF,
                                           hz50=rows[max(0, i - DELAY)][3]))
            res['island_faults'] += faults
            i = k + 36
            continue
        if hdmi and s1 == CTL[0b01] and s2 == CTL[0b00]:          # video preamble
            k = i
            while k < n and sym[k][1] == CTL[0b01] and sym[k][2] == CTL[0b00]:
                k += 1
            g = sym[k:k + 2]
            if k - i != 8 or any(x != (GB_VIDEO_0_2, GB_VIDEO_1, GB_VIDEO_0_2) for x in g):
                res['video_lead_faults'] += 1
            res['video_lines'] += 1
            i = k + 2
            continue
        if not hdmi and i >= 1 and not rows[i - 1][0]:       # DVI: one clock behind; blanking carries control codes only
            res['terc4_in_dvi'] += not (s0 in CTL.values() and s1 == CTL[0] and s2 == CTL[0])
            res['guard_in_dvi'] += (s0, s1, s2) == (GB_VIDEO_0_2, GB_VIDEO_1, GB_VIDEO_0_2)
        i += 1
    return res


def avi(island):
    hb, pb = island['hb'], island['pb']
    return dict(header=bytes(hb).hex(), checksum_ok=island['sum'] == 0, Y=pb[1] >> 5 & 3, A0=pb[1] >> 4 & 1,
                M=pb[2] >> 4 & 3, R=pb[2] & 15, Q=pb[3] >> 2 & 3, VIC=pb[4], PB5=pb[5], hz50=island['hz50'])


def main():
    ok = True
    for name, params in (('review2_hdmi_full', {}), ('review2_hdmi_limited', {'RGB_FULL': 0}), ('review2_dvi', {'HDMI': 0})):
        rows = test_hdmi.run(name, **params)
        r = decode(rows, hdmi=params.get('HDMI', 1) == 1)
        print(f'{name}: {len(rows)} clocks')
        if params.get('HDMI', 1) == 1:
            print(f'  active lines with lead-in: {r["video_lines"]}, wrong preamble/guard band: {r["video_lead_faults"]}')
            print(f'  data islands: {len(r["islands"])}, faults: {r["island_faults"] or "none"}')
            vics = set()
            for isl in r['islands']:
                a = avi(isl)
                vics.add((a['hz50'], a['VIC']))
                ok &= a['header'] == '82020d' and a['checksum_ok'] and a['Y'] == 0 and a['A0'] == 1 and a['M'] == 2 \
                    and a['R'] == 8 and a['PB5'] == 0 and a['VIC'] == (19 if a['hz50'] else 4)
            print(f'  AVI: {avi(r["islands"][0])}; (hz50, VIC) seen: {sorted(vics)}')
            ok &= not r['island_faults'] and r['video_lead_faults'] == 0 and len(r['islands']) >= 3
        else:
            print(f'  blanking clocks with anything but control codes: {r["terc4_in_dvi"]}, video guard bands: {r["guard_in_dvi"]}')
            ok &= r['terc4_in_dvi'] == 0 and r['guard_in_dvi'] == 0
    print('Q (PB3 bits 3:2) is printed above per mode; RGB_FULL changes nothing but PB3 in tmds_link.v '
          '(read from the source), and ycbcr2rgb.v puts out full range either way.')
    print('packets, guard bands and preambles as above' if ok else 'a check above failed')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
