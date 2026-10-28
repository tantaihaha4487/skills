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

Use for Thai essays, reports, academic audits, DOCX/PDF creation, citation-marker edits, and final artifact verification.

## Operating contract

- Inspect the actual source file before making claims about it.
- Preserve the original; create a derived output unless the user explicitly requests a verified in-place edit.
- Separate source-backed facts, author synthesis, proposed criteria, assignment requirements, and unknowns.
- Never invent citations, authors, dates, DOI, measurements, commands, or successful checks.
- For Hermes behavior, consult `https://hermes-agent.nousresearch.com/docs` directly.
- Never claim PASS when a required artifact or check was skipped. Report the exact limitation or blocker.

## Portable environment discovery

Do not use machine-specific absolute paths from this skill. Resolve tools at runtime with `shutil.which` or equivalent; accept explicit user paths. Use a temporary directory for renders/manifests. Discover fonts with `fc-match`/`fc-list` and inspect the bundled fonts. If an explicit family is unavailable, stop and ask; never silently substitute. Without a specified family, follow the applicable template or default below.

Useful tools:

- Python 3 with `python-docx` for DOCX creation/inspection.
- A real DOCX renderer for page layout and DOCX→PDF conversion. Prefer LibreOffice when available. If it is absent, try an installed Microsoft Word automation path or another DOCX-capable converter that preserves the selected Thai font and document fields. Verify the alternative's output with the same PDF and visual checks; a text extractor or `python-docx` is not a page renderer. The `documents` skill's `render_docx.py` uses LibreOffice and is not an independent fallback.
- Poppler tools: `pdfinfo`, `pdffonts`, `pdftotext`, and `pdftoppm` for PDF checks and renders.
- Pillow only for contact sheets or image checks.

If the preferred executable is absent, discover the equivalent capability before stopping. If no trustworthy converter is available, still complete a DOCX-only task's structural checks and state `PASS WITH LIMITATIONS` for the unverified pagination and visual layout; use `BLOCKED` when the requested PDF or a required visual/page-number check cannot be produced. Name the missing capability and a portable installation option. Never claim that DOCX structure checks prove rendered layout.

## Select structure and layout

Before creating or restructuring a document, read [references/document-structure-and-layout.md](references/document-structure-and-layout.md). Choose the essay, report, or official-document guidance according to the requested deliverable. For a formatting-only edit, preserve content and section order.

For Thai government correspondence, read the [external-letter profile](references/government-correspondence-layout.md) for `หนังสือภายนอก` and the [internal-memo profile](references/internal-government-memo-layout.md) for `บันทึกข้อความ` (form `แบบที่ ๒๙`). Apply each only to its document type; explicit requirements and applicable supplied forms take precedence. Do not transfer their rules to essays or reports.

Resolve choices in order: explicit requirements, mandatory templates, existing edit styles, then defaults. If requirements conflict with a mandatory template, ask before generating; otherwise follow the applicable template or exemplar before existing styles/defaults. Record choices once; ask only about unresolved material requirements such as a page limit.

For general report creation or restyling without a required institutional format, read [references/compact-report-example.md](references/compact-report-example.md) and use its **Current preferred report layout** with measured body rhythm. For content-only edits, preserve the existing layout. Keep essay and official-document profiles separate.

## Default formal Thai profile

These are fallback design choices, not a universal Thai institutional standard. Official documents follow their supplied form or institutional requirements.

- Paper: A4, 21 × 29.7 cm.
- Margins: top/bottom 2.54 cm and left/right 2.54 cm by default. A supplied exemplar or institutional requirement can override these; the government-correspondence references specify an asymmetric 3.00 cm left / 2.00 cm right layout for those forms.
- Document font: default to `TH SarabunPSK`; use `TH SarabunIT๙` when explicitly selected. An applicable template supplies the family when none is specified. Keep one family throughout all text and styles. If an explicit family conflicts with a mandatory template or is unavailable, ask before generating; never silently substitute. Thai digits alone do not require changing the family; verify glyph coverage.
- Body size: 16 pt unless the institutional template specifies another size.
- Title: centered, black, bold, normally 18 pt. Use 20–22 pt only when the exemplar or document hierarchy requires it.
- Headings: black, bold, left-aligned; use semantic Heading styles and a consistent hierarchy. Preserve the selected numbering scheme when sections are numbered. Essays normally have a title and unlabelled body paragraphs.
- Body alignment: justified with first-line indent around 1.25 cm unless the exemplar uses block paragraphs.
- Body line spacing: single (1.0) within each paragraph. Control the gap between paragraphs separately with `space_before`/`space_after`; do not increase within-paragraph line spacing to create paragraph separation.
- Tables and references: single-spaced, readable cell padding, stable column widths, and no decorative colors unless required by the template.
- Header/footer: preserve official identifiers, document title, revision/date fields, and page numbers when present. Keep author/student metadata in the footer only when requested.
- Avoid emoji, informal slang, visible drafting labels, Markdown markers, and decorative theme colors in formal Thai documents.

Inspect supplied DOCX/PDF exemplars first; let measurable properties override these defaults.

## Bundled official Thai font set

Bundled fonts are under `assets/fonts/`, with the original installation guide under `assets/guides/`. When using one, read [references/font-source.md](references/font-source.md) for the source URL, archive hash, and verified family names. Use only metadata-verified faces; directory names do not override internal metadata.

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

For an existing-report audit, read [references/report-audit-workflow.md](references/report-audit-workflow.md).

## Workflow B — create or edit Thai DOCX/PDF

### Input and content gates

- Define the requested profile before generating: A4, margins, font family, body size, line spacing, title, headings, tables, figures, bibliography, and whether a cover/TOC is required.
- Keep final body text clean: no prompt labels, Markdown markers, reviewer notes, or role-play unless explicitly requested.
- For formal reports, use evidence→interpretation→decision. Label monitoring thresholds, stop criteria, and success criteria as author-proposed unless an inspected source defines them.
- For bracketed numeric-citation removal, read [references/numeric-citation-marker-removal-and-verification.md](references/numeric-citation-marker-removal-and-verification.md) and apply its scope and verification rules.

### Apply the selected layout

Use the selected profile and structure/layout reference; do not add a second set of defaults. Define reusable Title, Heading, Normal, Caption, and table/reference styles as needed. Set paragraph spacing and indentation through styles rather than empty paragraphs, spaces, or tabs. Apply the bundled-font bindings to text, tables, headers and footers. Remove inherited theme borders/colors when a plain black academic style is requested.

Rebuilding from extracted text can discard numbering, fields, section breaks, and other layout information.

### Build and export gates

1. For new documents, build from source-of-truth Markdown or structured input with a deterministic generator. For existing documents, retain their structure and change only requested content or formatting in the derived copy.
2. Validate the DOCX package and inspect OOXML for A4 dimensions, margins, headings, tables, figures, footer PAGE fields, font bindings, and forbidden draft markers.
3. Render the exact output DOCX with an available DOCX-capable engine, using an explicit output directory. Record the engine and version. Prefer LibreOffice when installed; if unavailable, verify that the alternative preserves Thai text, fonts, fields, tables, and page geometry before relying on it.
4. Inspect the exact PDF with `pdfinfo`, `pdffonts`, and `pdftotext`.
5. Render every PDF page and create a contact sheet. Inspect all pages for balance, unexpected blanks, and section flow. Inspect the first page, changed pages, dense tables, every figure/caption pair, appendix, and final bibliography page at readable resolution. Correct layout defects using the reference's pagination guidance, then export and review again.
6. Maintain an internal evidence manifest with source/output paths, relevant tool versions, validation output, PDF geometry/page count, font result, text probes, citation probes, render coverage, visual-review scope, and hashes when integrity matters. Redact secrets. Give the user the finished document by default; surface the manifest only when requested or when a specific limitation affects use of the result.
7. After every substantive edit, rerun all applicable gates. Do not carry forward a previous PASS.

## Cross-machine reproducibility

For portability or another-machine parity, read [references/cross-machine-reproducibility.md](references/cross-machine-reproducibility.md). Never claim pixel-identical output across different renderer or font builds.

## Qualification status

Treat user-requested or workflow-required checks as required.

- **PASS** — every requested artifact and required check passed, with no unresolved limitation.
- **PASS WITH LIMITATIONS** — requested artifacts exist, but a non-required renderer or explicitly waived check remains unavailable; name the limitation.
- **BLOCKED** — a requested artifact, required source, conversion, validation, or visual check failed or remains unavailable after checking alternatives.

## Portable verification command

Use the bundled checker after producing a DOCX/PDF pair:

```bash
python scripts/verify_thai_docs.py --docx output.docx --pdf output.pdf --render-dir render
```

The checker emits JSON with `checks.visual_review="UNVERIFIED"` and exits nonzero on required-check failure. Use `--allow-landscape` only for intentional A4 landscape/mixed sections; non-A4 still fails. Use `--required-font FAMILY` only for explicit font requirements and `--forbid-numeric-markers` only when removing markers. It renders to fresh `--render-dir` output, but rendering is not human inspection; inspect page images before visual PASS. For DOCX-only tasks without a converter, omit `--pdf` for structural `PASS WITH LIMITATIONS`.

## Pitfalls

- Text extraction and DOCX font names do not prove visual correctness or the requested face's PDF embedding.
- A URL or citation marker does not prove evidence support.
- Falling concentration does not by itself prove biodegradation; weathering, dilution, transport, and redistribution may contribute.
- Do not claim pixel-perfect reference matching without comparing the reference and render. Pagination can differ between DOCX renderers; report the engine and any required cross-renderer check not performed.
- Do not delete scientific digits when removing bracketed citation markers.

## Conditional references

- For a captured essay style, read the applicable `references/thai-essay-layout-notes.md`, `references/essay-layout-session-notes.md`, or `references/essay-style-user-preferences.md`.
- For player guides, read `references/player-guide-branding-and-unit-validation.md`; for recipe textures, read `references/recipe-texture-validation.md`.
- Use `references/example-essay.md` only as a sample or validation fixture.
