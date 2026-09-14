---
name: thai-docs
description: Create and verify Thai DOCX/PDF reports end to end with portable evidence gates.
license: MIT
metadata:
  hermes:
    tags: [DOCX, PDF, Thai, verification, A4, fonts, citations]
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

Do not use machine-specific absolute paths from this skill. Resolve tools at runtime with `shutil.which` or equivalent. Accept explicit paths from the user. Use a temporary working directory for renders and manifests. Discover fonts with `fc-match`/`fc-list`; prefer the requested family, then report a limitation if unavailable. Do not bundle or silently substitute a font unless the user approves.

Required tools depend on the task:

- Python 3 with `python-docx` for DOCX creation/inspection.
- LibreOffice for DOCX→PDF conversion.
- Poppler tools: `pdfinfo`, `pdffonts`, `pdftotext`, and `pdftoppm` for PDF checks and renders.
- Pillow only for contact sheets or image checks.

If a required tool is absent, return `BLOCKED` with the missing executable and a portable installation hint; do not fake the result.

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

### Portable Thai layout defaults

Use explicit values from the request first. Otherwise use:

- A4: 21 × 29.7 cm.
- Margins: 2.54 cm on all sides for compact academic reports; use 3.0 cm left/right only when the requested school profile requires it.
- Font: requested installed Thai family, commonly `TH SarabunPSK`.
- Body: 16 pt, justified; first-line indent about 1.25–1.5 cm.
- Standard essay line spacing: 1.5. Compact LangTake-style reports: approximately 1.05–1.15.
- Title: centered, black, bold, approximately 18–22 pt.
- Tables and bibliography: single-spaced, thin borders, readable wrapping.
- Keep each figure and caption together; avoid blank spacer pages.

Bind Thai fonts explicitly on every run and the Normal style: `w:ascii`, `w:hAnsi`, `w:eastAsia`, `w:cs`, `w:szCs`, and `w:lang` where supported. Remove inherited theme borders/colors when a plain black academic style is requested.

### Build and export gates

1. Build from a source-of-truth Markdown or structured input with a deterministic generator.
2. Validate the DOCX package and inspect OOXML for A4 dimensions, margins, headings, tables, figures, footer PAGE fields, font bindings, and forbidden draft markers.
3. Convert the exact output DOCX with LibreOffice, using an explicit output directory.
4. Inspect the exact PDF with `pdfinfo`, `pdffonts`, and `pdftotext`.
5. Render every PDF page and create a contact sheet. Inspect the first page, changed pages, dense tables, every figure/caption pair, appendix, and final bibliography page.
6. Maintain an evidence manifest with source/output paths, tool versions when relevant, validation output, PDF geometry/page count, font result, text probes, citation probes, render coverage, visual-review scope, and hashes when integrity matters. Redact secrets.
7. After every substantive edit, rerun all applicable gates. Do not carry forward a previous PASS.

## Cross-machine reproducibility

For the same semantic result on another machine, pin or record Python, `python-docx`, LibreOffice, Poppler, renderer, and Thai font family/file hash. Keep source Markdown and generator deterministic, use explicit locale/UTF-8, stable sorting, explicit output paths, and no timestamps in content. The bundled checker records artifact hashes and page geometry but cannot promise pixel-identical pagination across different LibreOffice/font builds. If the environment differs or a requested font is unavailable, classify the result as `PASS WITH LIMITATIONS` and report the exact difference; never silently substitute a font or claim byte-identical output.

## Qualification status

- **PASS** — requested artifacts exist and all applicable DOCX, PDF, text, font, and visual checks passed.
- **PASS WITH LIMITATIONS** — artifacts pass available checks, but a named limitation remains, such as no Microsoft Word cross-check, unavailable original source, unavailable metadata, or representative rather than independent visual review.
- **BLOCKED** — a required source, dependency, conversion, validation, or visual check failed or was not possible.

## Question style

Do not use `?` in questions directed to the user. Use concise prompts ending in a period, such as `Please provide the source file.`

## Portable verification command

Use the bundled checker after producing a DOCX/PDF pair:

```bash
python scripts/verify_thai_docs.py --docx output.docx --pdf output.pdf --render-dir /tmp/thai-docs-render
```

The checker exits nonzero for a failed required check, emits JSON evidence, never assumes a fixed home directory, and reports unavailable optional checks separately. Use `--required-font FAMILY` when a font requirement is explicit.

## Pitfalls

- Clean text extraction does not prove visual correctness.
- A font name in DOCX does not prove that the requested face is embedded in PDF.
- A URL or citation marker does not prove evidence support.
- Falling concentration does not by itself prove biodegradation; weathering, dilution, transport, and redistribution may contribute.
- Do not claim pixel-perfect reference matching unless the reference and rendered output were actually compared.
- LibreOffice pagination can differ from Microsoft Word; report this limitation when Word was not tested.
- Do not delete scientific digits when removing bracketed citation markers.

## Bundled references

- `references/numeric-citation-marker-removal-and-verification.md` — exact citation-marker scope and probes.
- `references/thai-essay-layout-notes.md` — concise Thai essay layout defaults.
- Other reference files cover essay style and image/recipe workflows; load them only when the task needs those variants.
