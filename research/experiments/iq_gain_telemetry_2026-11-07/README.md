# New seed2 IQ/Capture telemetry

Exact helpers from task81, for frozen Core `031bba053943ee04ce303ae75b5e701746169c97`. Read [the result and limits](../../../docs/IQ_GAIN_TELEMETRY_2026-11-07.md). The fixed mapping is a diagnostic at observed sample times, not a replacement video oracle. PLL produced no entries in this case.

The caller must verify source/archive, actual runtime/dependencies, ordinary quota and workstation/build.lock gates separately before **each** first phase. Use new output directories, max59s for generation and120s per observation, max300s total. Review each completed phase before starting another. Never rerun historical jobs or overwrite raw data.

The original private generator failed on argument unpacking before creating data. `generate_remaining_v2.py` is the exact separately bound helper that generated the arrays once. It additionally needs the original seed1 CN12 results.json solely to reject accidental reuse of that IQ hash.

```sh
python -B generate_remaining_v2.py /absolute/frozen-core /absolute/new-source /absolute/original-seed1-results.json
```

After a successful source review, start one observation at a time with the same saved source packet:

```sh
python -B observe.py /absolute/frozen-core /absolute/new-source adjacent /absolute/new-adjacent
```

Review it and obtain a new quota receipt before the independent PLL phase:

```sh
python -B observe.py /absolute/frozen-core /absolute/new-source gated /absolute/new-gated
```

Generation uses the existing NumPy; observation uses stdlib and unchanged Capture. Trace records are little-endian `<IiHHHHHHB`: current sample, partner sample (-1 doubles current), field, line, pixel index, blank, sync, gain, actual Y. Entries use the original packet's16-byte `<BBHIII` layout. Actual arrays/raw and all failed preparation artifacts remain private and hash-bound.
