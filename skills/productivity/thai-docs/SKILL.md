---
name: thai-docs
description: Create, edit, and review Thai DOCX/PDF essays, reports, and official documents, with document-specific structure, consistent typography, template matching, and rendered layout checks.
license: MIT
metadata:
  hermes:
    tags: [DOCX, PDF, Thai, formal-documents, verification, A4, fonts, citations]
    related_skills: [pdf, docx]
---

# Thai documents: create, audit, and verify

Use this single skill for Thai essays, reports, academic audits, DOCX/PDF creation, citation-marker edits, and final artifact verification.

## Operating contract

- Inspect the actual source file before making claims about it.
- Preserve the original; create a derived output unless the user explicitly requests a verified in-place edit.
- Separate source-backed facts, author synthesis, proposed criteria, assignment requirements, and unknowns.
- Never invent citations, authors, dates, DOI, measurements, commands, or successful checks.
- For Hermes behavior, use `https://hermes-agent.nousresearch.com/docs` as the authoritative source and load `hermes-agent` first.
- Use `PASS`, `PASS WITH LIMITATIONS`, or `BLOCKED` as the final qualification status.
- Never claim PASS when a required artifact or check was skipped. Report the exact limitation or blocker.

## Portable environment discovery

Do not use machine-specific absolute paths from this skill. Resolve tools at runtime with `shutil.which` or equivalent. Accept explicit paths from the user. Use a temporary working directory for renders and manifests. Discover fonts with `fc-match`/`fc-list` and inspect the bundled fonts; use the requested family and report a limitation if unavailable. When no family is specified, use the default below. Do not silently substitute a different family for an explicit font requirement.

Useful tools depend on the task:

- Python 3 with `python-docx` for DOCX creation/inspection.
- A real DOCX renderer for page layout and DOCX→PDF conversion. Prefer LibreOffice when available. If it is absent, try an installed Microsoft Word automation path or another DOCX-capable converter that preserves the selected Thai font and document fields. Verify the alternative's output with the same PDF and visual checks; a text extractor or `python-docx` is not a page renderer. The `documents` skill's `render_docx.py` uses LibreOffice and is not an independent fallback.
- Poppler tools: `pdfinfo`, `pdffonts`, `pdftotext`, and `pdftoppm` for PDF checks and renders.
- Pillow only for contact sheets or image checks.

If the preferred executable is absent, discover the equivalent capability before stopping. If no trustworthy converter is available, still complete a DOCX-only task's structural checks and state `PASS WITH LIMITATIONS` for the unverified pagination and visual layout; use `BLOCKED` when the requested PDF or a required visual/page-number check cannot be produced. Name the missing capability and a portable installation option. Never claim that DOCX structure checks prove rendered layout.

## Select structure and layout

Before creating or restructuring a document, read [references/document-structure-and-layout.md](references/document-structure-and-layout.md). Choose the essay, report, or official-document guidance according to the requested deliverable. For a formatting-only edit, preserve content and section order.

For Thai government correspondence, read [references/government-correspondence-layout.md](references/government-correspondence-layout.md) for the external-letter (`หนังสือภายนอก`) rules and source scope. For an internal memorandum (`บันทึกข้อความ`, form `แบบที่ ๒๙`), also read [references/internal-government-memo-layout.md](references/internal-government-memo-layout.md). Apply each profile only to its document type, subject to explicit user requirements and any supplied, applicable institutional form. Do not transfer their heading, margin, or signature rules to essays and reports.

Resolve layout choices in this order: explicit user requirements, supplied institutional template or exemplar, existing document styles for edits, then the defaults below. Record the chosen values once and reuse them throughout generation and review. Ask only about missing requirements that materially affect the result, such as a mandatory page limit or institutional template.

For general reports without a required institutional format, read [references/compact-report-example.md](references/compact-report-example.md) and use its **Current preferred report layout** with the measured body rhythm. The later user preferences supersede the older measured heading/list/table values. For an existing report, apply this profile when creation or restyling is in scope; preserve the existing layout for a content-only edit. Keep essay and official-document profiles separate.

## Default formal Thai profile

These are fallback design choices, not a universal Thai institutional standard. Official documents follow their supplied form or institutional requirements.

- Paper: A4, 21 × 29.7 cm.
- Margins: top/bottom 2.54 cm and left/right 2.54 cm by default. A supplied exemplar or institutional requirement can override these; the government-correspondence references specify an asymmetric 3.00 cm left / 2.00 cm right layout for those forms.
- Document font: `TH SarabunPSK` is the user's selected default. Use one family throughout the document, including title, headings, body, tables, captions, bibliography, headers, footers, and page fields. Use `TH SarabunIT๙` instead when the user selects it. If the choice is unresolved or a template conflicts with this preference, ask the user to choose before generating; do not mix the two families or silently substitute one. An already explicit choice does not need reconfirmation. Thai digits alone do not require changing the family; verify glyph coverage.
- Body size: 16 pt unless the institutional template specifies another size.
- Title: centered, black, bold, normally 18 pt. Use 20–22 pt only when the exemplar or document hierarchy requires it.
- Headings: black, bold, left-aligned; use semantic Heading styles and a consistent hierarchy. Preserve the selected numbering scheme when sections are numbered. Essays normally have a title and unlabelled body paragraphs.
- Body alignment: justified with first-line indent around 1.25 cm unless the exemplar uses block paragraphs.
- Body line spacing: single (1.0) within each paragraph. Control the gap between paragraphs separately with `space_before`/`space_after`; do not increase within-paragraph line spacing to create paragraph separation.
- Tables and references: single-spaced, readable cell padding, stable column widths, and no decorative colors unless required by the template.
- Header/footer: preserve official identifiers, document title, revision/date fields, and page numbers when present. Keep author/student metadata in the footer only when requested.
- Avoid emoji, informal slang, visible drafting labels, Markdown markers, and decorative theme colors in formal Thai documents.

When a supplied DOCX or PDF exemplar exists, inspect it first and let measurable exemplar properties override these defaults.

## Bundled official Thai font set

The bundled font files were obtained from the Ubon Ratchathani University source URL:

`https://www.ubs.ubu.ac.th/font/THSarabun.rar`

Fonts are grouped by family under `assets/fonts/`: `THSarabunNew/`, `THSarabunIT9/`, `THNiramit/`, and the separately sourced `THSarabunPSK/`. The original installation guide is under `assets/guides/`. See [references/font-source.md](references/font-source.md) for provenance and internal family names. Retain the source URL and archive hash. Use only the font family and face verified by metadata; directory names do not override internal font metadata.

Before using a bundled font:

1. Inspect its internal family, full name, PostScript name, style, and glyph coverage with `fc-query` or `fc-scan`.
2. Bind the same selected family to `w:ascii`, `w:hAnsi`, `w:eastAsia`, and `w:cs` on every generated text run and all used text styles, including Normal, headings, captions, and footers. Remove competing theme font declarations. Regular, bold, italic, and bold-italic faces must belong to that family.
3. Set `w:szCs` and `w:lang` where supported for Thai complex-script consistency.
4. Verify the exported PDF with `pdffonts` and report the actual embedded face.
5. Do not install fonts system-wide as part of document generation. Use the bundled files through an explicit temporary font directory or the host's verified font installation.
6. If redistribution terms are unclear, preserve the source URL and archive checksum and report the limitation rather than claiming a license that was not verified.

## Formal Thai formatting verification

In addition to the general gates below, probe the final artifacts for:

- A4 page geometry and expected margins.
- Correct Thai family and face for title, headings, body, tables, and references.
- Consistent alignment and line spacing by section.
- Correct heading numbering when the selected profile uses it, and correct page numbering when present.
- No blank pages, orphan headings, clipped text, overlapping objects, broken glyphs, malformed URLs, or split figure captions.
- Preserve meaningful punctuation in quoted or supplied text; remove only accidental drafting artifacts.

## Workflow A — audit an existing report

1. Record source path, requested scope, language/register, layout constraints, citation rules, and conclusions that must remain conditional.
2. Read the complete source with line numbers. Inventory headings, paragraphs, tables, figures/captions, Q&A, checklists, and bibliography.
3. Build a structure and evidence map. A citation marker, URL, or bibliography entry is not proof that a claim is supported.
4. Mark repeated thesis statements, prompt-like framing, answer-key language, oversized tables, duplicated mechanisms, and flowcharts that repeat prose.
5. Inspect cited primary sources when accessible. Narrow site-specific findings; distinguish measured findings from recommendations and proposed operational thresholds.
6. Produce a concrete old-section→new-section map and paragraph-level actions: keep, merge, move, shorten, rename, or remove.
7. Preserve important caveats, the requested conclusion, and the requested document format.
8. State whether the audit is `PASS`, `PASS WITH LIMITATIONS`, or `BLOCKED`. An audit is read-only unless editing was explicitly requested.

Recommended audit headings in Thai:

1. ผลตรวจโดยรวม
2. แผนผังส่วนใหม่
3. ข้อเสนอแก้ระดับย่อหน้า
4. จุดซ้ำและวัสดุแบบใบงาน
5. ความเสี่ยงด้านการอ้างอิง
6. ไฟล์และสถานะการแก้ไข

## Workflow B — create or edit Thai DOCX/PDF

### Input and content gates

- Define the requested profile before generating: A4, margins, font family, body size, line spacing, title, headings, tables, figures, bibliography, and whether a cover/TOC is required.
- Keep final body text clean: no prompt labels, Markdown markers, reviewer notes, or role-play unless explicitly requested.
- For formal reports, use evidence→interpretation→decision. Label monitoring thresholds, stop criteria, and success criteria as author-proposed unless an inspected source defines them.
- For an explicit “remove all” request such as `.[2][14]`, remove `\[\d+\]` markers from the requested scope, including bibliography labels when “all” is stated. Preserve dates, years, measurements, percentages, ranges, section numbers, and chemical notation. Rebuild and verify both artifacts.

### Apply the selected layout

Use the selected profile above and the structure/layout reference; do not introduce a second set of defaults. Define reusable Title, Heading, Normal, Caption, and table/reference styles as needed. Set paragraph spacing and indentation through styles rather than empty paragraphs, spaces, or tabs. Apply the font bindings from the bundled-font section to generated text, including tables, headers, and footers. Remove inherited theme borders/colors when a plain black academic style is requested.

For edits, modify the existing document when practical; rebuilding from extracted text can discard numbering, fields, section breaks, and other layout information.

### Build and export gates

1. For new documents, build from source-of-truth Markdown or structured input with a deterministic generator. For existing documents, retain their structure and change only the requested content or formatting in the derived copy.
2. Validate the DOCX package and inspect OOXML for A4 dimensions, margins, headings, tables, figures, footer PAGE fields, font bindings, and forbidden draft markers.
3. Render the exact output DOCX with an available DOCX-capable engine, using an explicit output directory. Record the engine and version. Prefer LibreOffice when installed; if unavailable, verify that the alternative preserves Thai text, fonts, fields, tables, and page geometry before relying on it.
4. Inspect the exact PDF with `pdfinfo`, `pdffonts`, and `pdftotext`.
5. Render every PDF page and create a contact sheet. Inspect all pages for balance, unexpected blanks, and section flow. Inspect the first page, changed pages, dense tables, every figure/caption pair, appendix, and final bibliography page at readable resolution. Correct layout defects using the reference's pagination guidance, then export and review again.
6. Maintain an internal evidence manifest with source/output paths, tool versions when relevant, validation output, PDF geometry/page count, font result, text probes, citation probes, render coverage, visual-review scope, and hashes when integrity matters. Redact secrets. Give the user the finished document by default; surface the manifest only when requested or when a specific limitation affects use of the result.
7. After every substantive edit, rerun all applicable gates. Do not carry forward a previous PASS.

## Cross-machine reproducibility

For the same semantic result on another machine, pin or record Python, `python-docx`, the DOCX renderer/converter, Poppler, and Thai font family/file hash. Keep source Markdown and generator deterministic, use explicit locale/UTF-8, stable sorting, explicit output paths, and no timestamps in content. The bundled checker records artifact hashes and page geometry but cannot promise pixel-identical pagination across renderer/font builds. If the environment differs or a requested font is unavailable, classify the result as `PASS WITH LIMITATIONS` and report the exact difference; never silently substitute a font or claim byte-identical output.

## Qualification status

- **PASS** — requested artifacts exist and all applicable DOCX, PDF, text, font, and visual checks passed.
- **PASS WITH LIMITATIONS** — artifacts pass available checks, but a named limitation remains, such as no Microsoft Word cross-check, unavailable original source, unavailable metadata, or representative rather than independent visual review.
- **BLOCKED** — a required source, requested artifact, conversion, validation, or visual check failed or was not possible after checking available alternatives.

## Portable verification command

Use the bundled checker after producing a DOCX/PDF pair:

```bash
python scripts/verify_thai_docs.py --docx output.docx --pdf output.pdf --render-dir /tmp/thai-docs-render
```

The checker exits nonzero for a failed required check, emits JSON evidence, and never assumes a fixed home directory. Use `--required-font FAMILY` when a font requirement is explicit and `--forbid-numeric-markers` only when the task requires removing those markers. It renders into a fresh subdirectory of `--render-dir` and reports that path. Its PASS covers automated checks only; inspect the page images before claiming visual PASS. When no converter is available for a DOCX-only task, omit `--pdf` for a structural `PASS WITH LIMITATIONS` result.

## Pitfalls

- Clean text extraction does not prove visual correctness.
- A font name in DOCX does not prove that the requested face is embedded in PDF.
- A URL or citation marker does not prove evidence support.
- Falling concentration does not by itself prove biodegradation; weathering, dilution, transport, and redistribution may contribute.
- Do not claim pixel-perfect reference matching unless the reference and rendered output were actually compared.
- Pagination can differ between DOCX renderers; report the engine used and any required cross-renderer check that was not performed.
- Do not delete scientific digits when removing bracketed citation markers.

## Bundled references

- `references/font-source.md` — source URL, archive hash, verified families, metadata, and redistribution caveat.
- `references/numeric-citation-marker-removal-and-verification.md` — exact citation-marker scope and probes.
- `references/thai-essay-layout-notes.md` — historical personal essay preferences; read only when the current request calls for that style.
- [references/document-structure-and-layout.md](references/document-structure-and-layout.md) — structure by document type, reusable styles, template inspection, and pagination fixes; read for creation or layout changes.
- [references/government-correspondence-layout.md](references/government-correspondence-layout.md) — OBEC-linked guidance for Thai external letters and body-paragraph rules shared with internal memoranda; read for those correspondence types.
- [references/internal-government-memo-layout.md](references/internal-government-memo-layout.md) — source-backed layout for the `บันทึกข้อความ` (`แบบที่ ๒๙`) internal-government-memo form; read when that form is requested.
- Other reference files cover essay style and image/recipe workflows; load them only when the task needs those variants.
