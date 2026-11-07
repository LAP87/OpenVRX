# One source-defined AVG16 field-acquisition experiment

These are exact task83 helpers. Read [the result and limits](../../../docs/IQ_AVG16_EXPERIMENT_2026-11-07.md): more rows were recovered, but no row met the unchanged pixel budget and many source-row labels are shifted. No default or producer changed.

`observe.py FROZEN_CORE INPUT_MANIFEST NEW_OUTPUT` reads a bound manifest with kind/node/codes/size/sha256 and parameters `{avg:16, comb:true, white_x8:20, boot_check:true}`. The actual model window length is saved. Source is frozen031bba0. It records16-byte entries, `<II` word entry-index/sample timestamps and V/active events. No IQ is regenerated.

The original positive used task81's exact saved seed2 gated codes. Only after the predeclared field gate passed was `mask_vertical.py POSITIVE_MANIFEST NEW_NEGATIVE_INPUT` run. It prepared one owned no-V copy, preserving all active-source bytes. That resulting input must be hash-bound before a separate first `observe.py` negative phase. There is no automatic next phase, alternative parameter or mutation after a miss.

Caller must supply source/Git/archive/runtime/helper/input identity checks, fresh actual ordinary quota/workstation gates and build.lock at each first phase. Max60s per model phase/120s total, no expansion or historical job/output reuse. Existing AVG8 baseline receipts are reused, not rerun. Native/FPGA/hardware and improved image quality are unaccepted.
