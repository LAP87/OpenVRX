# Capture sample-provenance observation

These are the exact task79 observer and primary validator. They do not fix or certify Capture timing. Read [the stopped result](../../../docs/CAPTURE_PIXEL_PROVENANCE_2026-11-07.md) before interpreting a successful arithmetic check.

Use a separate read-only Core checkout at `031bba053943ee04ce303ae75b5e701746169c97`, verify its Git/archive/source bytes, and copy these scripts to a new scratch directory. The original caller bound that source identity externally; the observer is not a standalone Git acceptance gate. Never overwrite an old experiment directory or restart historical jobs.

After the ordinary quota, workstation and build-lock gates, a separately authorized reproduction is:

```sh
python3 -B observe.py /absolute/path/to/frozen-core /absolute/path/to/new-output
python3 -B -c 'import oracle; print(oracle.validate_packet("/absolute/path/to/new-output"))'
```

Python stdlib only. The original model phase took 4.824 s with a 120 s timeout; no automatic time expansion. The source is rectangular 4/20/60 code video, not an IQ/RF or actual C5-quality model. The validator tests values and observed dependencies; it does not independently prove the DUT control schedule. Do not interpret it as a replacement for the original failed root timing check.
