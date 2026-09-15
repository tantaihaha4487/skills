# User-provided compact Thai report example

The user supplied `รายงาน-bioremediation-exxon-valdez-humanized.docx` on 2026-09-15 as an example of consistent Thai document formatting. Use this profile for reports requested in that style. Explicit requirements and current templates take precedence. The source DOCX remains outside the skill; these measurements allow reuse without depending on a Downloads path.

Source SHA-256: `4746cc579cfe21b6ef23a5af0be20c645d35c158b5878b95c101cb441ca598c5`.

## Measured layout

Values were inspected in DOCX styles, paragraph properties, and run formatting. Direct formatting overrides several style definitions.

| Element | Observed formatting |
| --- | --- |
| Page | A4 portrait; 2.54 cm margins on all sides |
| Title | 22 pt, bold, black, centered; single spacing; 8 pt after; source has approximately 2.85 pt before |
| Main section headings | 16 pt, bold, black; normally left-aligned; single spacing; 6 pt before and 2 pt after; keep with next paragraph |
| Body | 16 pt; justified; first-line indent approximately 1.25 cm; 1.05-line spacing; 0 pt before and 4 pt after |
| Lists | 1.05-line spacing; 0 pt before and 2 pt after; approximately 0.75 cm left and hanging indent |
| Table text | 14 pt; single spacing; 0 pt before/after; fixed-width tables approximately 15.92 cm wide |
| Caption style | 16 pt; centered; single spacing; 4 pt before and 2 pt after |
| Bibliography paragraphs | 16 pt; left-aligned; single spacing; 0 pt before/after; approximately 0.60 cm hanging indent |
| Footer | Centered Thai page label with PAGE field; footer distance approximately 1.25 cm; label 14 pt and page field 12 pt in the source |

All 30 BodyText paragraphs use the same paragraph layout. Headings have a few deliberate-looking alignment and spacing variations; inspect the relevant section before reproducing those exceptions. Do not impose a fixed number of sections or tables from this example on another report.

## Font handling

The source is not uniformly TH SarabunPSK: title, heading, and body runs generally specify `TH SarabunIT๙` for ASCII, high ANSI, and complex-script slots, with `TH SarabunPSK` in the East Asian slot. Normal specifies TH SarabunPSK, while Title and Heading styles retain Calibri/theme declarations underneath the direct formatting. Footer runs specify TH SarabunPSK.

The user explicitly rejected this font mixture after inspection and selected `TH SarabunPSK`. Reuse the measured layout with TH SarabunPSK throughout, including headers, footers, and page fields. Bind it to all four font slots in every used text style and generated run, and remove conflicting theme declarations. Do not reproduce the source's mixed bindings even for this example's layout. Use TH SarabunIT๙ throughout only when the user chooses it instead; if the choice is unclear or requirements conflict, ask first. Do not ask again when the user's selection is already explicit.

For PSK, use the separately sourced `assets/fonts/THSarabunPSK/` faces. For IT๙, use `assets/fonts/THSarabunIT9/`. The latter set also advertises a PSK family alias, so isolate the selected font files from the competing set during rendering. Verify actual exported faces; a shared family alias does not make the two sets interchangeable.

## Applying the example

Use reusable styles for recurring formatting. Preserve the compact paragraph rhythm and clear section hierarchy; adapt the outline to the new subject. Retain 16 pt body text and the measured margins when fitting content, and apply the pagination guidance in `document-structure-and-layout.md`.

This profile records document structure and formatting properties, not a visual certification. The source was not rendered during extraction. Verify Thai glyphs, font resolution, table wrapping, caption placement, and page breaks in each generated output. Do not use its scientific claims or bibliography as verified evidence for another document.
