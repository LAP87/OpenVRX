# Read-only profiles of existing task75 raw

`analyse.py` is the exact primary stdlib reader used in task80. It does not import or run a receiver model. See [the result and limits](../../../docs/IQ_NOISY_PIXEL_PROFILES_2026-11-07.md).

The caller supplies a reviewed manifest with `source_commit` and a `cases` list. Every case has `id`, `name`, `metadata` (an absolute path to the original phase's results.json) and `raw` (the absolute original entries.bin path). The metadata must contain the original raw SHA/size and case metrics; byte mismatches are rejected. The original caller additionally bound the manifest, source/runtime/helper and input bytes in an external launch contract.

Run only under the ordinary quota/workstation/build-lock gates, with original raw and a new output directory:

```sh
python3 -B analyse.py /absolute/path/to/reviewed-selection.json /absolute/path/to/new-output
```

Do not regenerate missing original IQ/codes or reuse historical output directories. Profiles over surviving rows are diagnostic; they do not certify source timing, cause, recovered video, native or hardware performance. Histogram quantiles use nearest rank. The published JSON omits full histograms; exact full histograms and all original bytes remain in the private source-bound packet.
