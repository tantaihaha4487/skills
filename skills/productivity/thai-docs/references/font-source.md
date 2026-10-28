# Thai font source record

## Source

- Publisher: Ubon Ratchathani University
- URL: https://www.ubs.ubu.ac.th/font/THSarabun.rar
- Local archive used for this skill update: `THSarabun.rar`
- SHA-256: `b1fd3202c78bd964301e908c7feadb668b60baf6831d3998c0aa9879a53716f9`

## Contents verified

The archive contains these families and face variants:

- TH Sarabun New: regular, bold, italic, bold italic
- TH SarabunIT๙ / TH SarabunPSK: regular, bold, italic, bold italic
- TH NiramitIT๙: regular, bold, italic
- TH Niramit AS-IT๙: bold italic
- Official installation guide PDF

## Additional local TH SarabunPSK source

A separately sourced local set is in `assets/fonts/THSarabunPSK/`. All four files were inspected with `fc-scan` and report the internal family `TH SarabunPSK`.

SHA-256 values:

- `THSarabunPSK.ttf`: `2936ea292bf2b82c572ed50837dc4a04170076b561bbfc5a9306037a989b470a`
- `THSarabunPSK-Bold.ttf`: `969fe7493a68f136dab33f51fabcbcaa44fe040582bec1a575e707f1850eb06c`
- `THSarabunPSK-Italic.ttf`: `9fd6e9672f5a78edf186591b8a9f376b8c27d0aac37875f818670a075995cec9`
- `THSarabunPSK-BoldItalic.ttf`: `d52e0c8a058afc18f45c50b90f48de5954a46c0868ac826932ba5248b128ffc0`

## Metadata verification

### Asset layout

- `assets/fonts/THSarabunNew/`: four TH Sarabun New faces from the archive.
- `assets/fonts/THSarabunIT9/`: four archive faces reporting both TH SarabunPSK and TH SarabunIT๙ family names.
- `assets/fonts/THNiramit/`: four archive faces reporting TH Niramit AS and TH NiramitIT๙ family names. Original filenames are preserved.
- `assets/fonts/THSarabunPSK/`: four separately sourced TH SarabunPSK faces listed above.
- `assets/guides/`: the original Thai installation guide PDF.

Eight byte-identical font copies from the archive's `F0nt/THSarabunIT·/` directory were removed after SHA-256 and byte comparisons. Every distinct font file is retained. The two SarabunPSK-labelled sets are distinct files; select only the intended set for a temporary font environment to avoid family-name collisions.

`fc-scan` reported these internal family names:

- `TH Sarabun New`
- `TH SarabunPSK`
- `TH SarabunIT๙`
- `TH Niramit AS`
- `TH NiramitIT๙`

The archive source page and installation guide were preserved as provenance. Redistribution terms were not independently established from a separate license file; follow the source publisher's terms and do not claim a license beyond the source evidence.

## Use policy

Select the family matching the requested institutional template or reference document. Never silently substitute a different family. Verify the exported PDF's embedded face with `pdffonts`.
