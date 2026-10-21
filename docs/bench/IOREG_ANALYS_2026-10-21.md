# Uppgift 47: vad som skiljer M2a:s UART från de läsbara kontrollerna

Fakta ur de routade netlistorna (`build/<topp>.pnr.json`, lästa med Core `gateware/tools/iob_regs.py`), inte ur hårdvara:

| Bygge | IOREG | Register i I/O-celler | varav med CE, SET eller RESET | UART-utgångens vippa |
|---|---|---|---|---|
| `m2u_uart27`, `m2u_uart64` | 0 | 0 | 0 | i logiken (DFFSE: CE + SET) |
| `m2u_uart64_ioreg1` | 1 | 1 | 1 | i I/O-cellen: IOLOGICO med CE, CLK, D0, SET |
| `m2a_memtest` | 1 | 50 | 49 | i I/O-cellen: IOLOGICO med CE, CLK, D0, SET |
| `m2a_memtest_ioreg0` | 0 | 0 | 0 | i logiken |
| `m4_dual_mix` | 1 | 69 | 52 | — |
| `m6_puck_proto` | 1 | 75 | 56 | — |

IOREG=1 ger nextpnr `--vopt ireg_in_iob oreg_in_iob ioreg_in_iob` (beslut 2, 2026-10-12). Det flyttar varje vippa intill en pad in i I/O-cellen, inte bara SDRAM:ens dataingångar: i M2a även UART:ens `txd` (synkron SET från reset, klockenable från bittakten), SDRAM:ens adress- och kommandoutgångar (CE, SET eller RESET) och de 32 DQ-ingångsregistren (CE). Bara knappen `key_i` hamnar där som en ren vippa (CLK, D, Q).

Bänken 2026-10-20: `m2u_uart27` och `m2u_uart64` (IOREG=0) gav 39 av 39 rader exakt; M2a (IOREG=1) gav 82-byterader i rätt takt med förvrängda bitar som inget baud-, polaritets- eller bitordningsfel återskapar ([UART_KLOCKPROV_2026-10-20.md](UART_KLOCKPROV_2026-10-20.md), [råcapturer](2026-10-20/uart/)). Den enda skillnaden i UART-vägen mellan de två fallen är var `txd`-vippan sitter och att den där har CE och SET.

Hypotes: I/O-cellens register, så som Apicula 0.32 / nextpnr 0.11.1 programmerar det, respekterar inte CE och/eller SET. Då är inte bara UART-raden fel utan också SDRAM:ens adress- och kommandosignaler och DQ-infångningen i alla IOREG=1-byggen, och inget minnesresultat från dem säger något.

Avgörande prov på kortet (bitströmmarna på Core-grenen `bench/bitstreams-2026-10-20`):

| Fil | Läsbar | Skräp |
|---|---|---|
| `m2u_uart64_ioreg1.fs` | CE/SET i I/O-cellen fungerar; felet är något annat i M2a | hypotesen stämmer |
| `m2a_memtest_ioreg0.fs` | minnestestet går att läsa utan I/O-cellregister; raderna visar om SDRAM:en läses rätt utan dem | felet sitter i M2a:s rapportlogik |

Om hypotesen stämmer är åtgärden i byggflödet, inte i RTL: IOREG=1 får bara packa vippor utan CE/SET/RESET (`iob_regs.py --strict` som grind i `build.sh`), och DQ-infångningen i `sdram_burst.v` skrivs om så att registret vid paden är en ren vippa (fånga varje klocka, kvalificera i nästa steg). Beslut 2 (I/O-register i cellerna) står kvar till sitt syfte, men kräver den omskrivningen. Inget av det görs innan provet har körts.
