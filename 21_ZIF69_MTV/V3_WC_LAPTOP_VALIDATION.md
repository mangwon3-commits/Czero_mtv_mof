# Laptop v3 dry-working-capacity validation

**Received:** 2026-08-18 KST

**Archive SHA-256:** `09c5953e36696f44d440aab32a5472c2ca5f0178ccd67e6764e698019d0e3da3`
**Verification:** the attached archive and its `.sha256` file match exactly.

## Accepted contents

The archive contains only the intended result payload:

- `v3_wc/working_capacity.json`
- `wc_v3.log`
- `wc_v3_status.log`

The status record shows 24/24 completed at 09:11 KST.  The execution log
records the correct v3 input directory (`charged_v3`), six intended targets,
the four registered conditions, six workers, and 15,000 production cycles.
All six targets and all four condition loadings are present in the JSON.

## Important metadata correction

The raw JSON field `note` still says that `saIm100` is excluded by the water
termination rule.  That sentence is obsolete v1 wording: the result itself
contains a complete `saIm100` row, and corrected-geometry water v2 gave
58.5 +/- 2.2% retention against the unchanged 50% threshold.  The numerical
rows are accepted unchanged; this document corrects the interpretation without
rewriting the source result.

## Provisional dry-only finding

For TSA working capacity, saIm100 is 1.2976 +/- 0.0176 mol/kg and saIm075 is
1.1468 +/- 0.0173 mol/kg: a 6.1-sigma dry-TSA separation.  This is not a final
candidate recommendation until matching v3 water, humid working-capacity, and
stability gates are complete.  For VSA, the apparent differences are not all
above the 1.5-sigma ranking rule.

## Provenance rule

`working_capacity.json` is a byte-preserved copy of the laptop raw output.
The original archive remains outside the repository; its hash above identifies
the received evidence.  Do not silently edit numerical rows or reuse this file
after runner settings change.
