---
name: thai-docs
description: Create and rigorously verify Thai DOCX/PDF documents with correct fonts, A4 layout, LibreOffice export, and evidence-grounded checks.
license: MIT
metadata:
  hermes:
    tags: [DOCX, PDF, LibreOffice, Thai, Essay, Font, python-docx, NixOS]
---

# Thai DOCX & PDF Workflow

## Trigger
User asks for a Thai document — essay (เรียงความ), report (รายงาน), letter (จดหมาย), official document, or any `.docx`/`.pdf` output in Thai.

## Step 1 — Confirm Inputs, Font & Format

When the document must include user-supplied pictures, acquire and validate every image **before** drafting or generating the DOCX:

1. Resolve a temporary-hosting page to its direct download URL if needed.
2. Download the image bytes and verify the MIME type/dimensions (for example with `file` and `identify`).
3. Only proceed when all required images are locally available and renderable.
4. If a source cannot be retrieved, ask the user to upload the images directly in chat; do not produce a purportedly finished image-comparison document with missing or substitute pictures.

Ask or detect:
- **Font**: TH NiramitIT๙, TH SarabunPSK, Kanit, or other. These are installed on Hermes/NixOS:
  - `TH NiramitIT๙` → `/usr/local/share/fonts/t/TH_NiramitIT๙.ttf`
  - `TH SarabunPSK` → check via `fc-list | grep -i sarabun`
  - `Kanit` → `~/.local/share/fonts/Kanit-Regular.ttf`
- **Size**: Default 16pt for body text (standard Thai academic)
- **Line spacing**: Default 1.5
- **Margins**: A4 (21×29.7 cm) with 2.54 cm top/bottom, 3.0 cm left/right

## Step 2 — Thai Essay Structure (if essay)

| Section | Thai | Content |
|---|---|---|
| Title | หัวข้อ | Center, 20-22pt bold |
| Subtitle | คำขยาย | Center, 14pt italic, optional |
| Introduction | คำนำ | 1 paragraph, hook + context + thesis |
| Body | เนื้อเรื่อง | 2-4 subsections, each with 1-2 paragraphs |
| Conclusion | สรุป | 1 paragraph, recap + closing thought |

For the user's Thai essays, prefer clean prose in the final document: do **not** leave visible note markers, bracketed labels, markdown headings, or draft annotations inside the body unless the user explicitly asks for them. If the prompt mentions an essay skill or a school-style format, keep the output as a normal essay page, not a meta-outline.

## Step 3 — python-docx Script Template

### Font Embedding (Critical — Thai fonts won't render without east-asia XML)

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

FONT_NAME = 'TH NiramitIT๙'  # actual PostScript name

def set_font(run, size=16, bold=False, italic=False):
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    # ⚠️ MUST set east-asia font or Thai glyphs render as boxes
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = run._element.makeelement(qn('w:rFonts'), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), FONT_NAME)
    rFonts.set(qn('w:ascii'), FONT_NAME)
    rFonts.set(qn('w:hAnsi'), FONT_NAME)
```

### A4 Page Setup

```python
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(3.0)
```

### Paragraph Helpers

```python
def add_body_para(doc, text, first_indent=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = p.paragraph_format
    if first_indent:
        pf.first_line_indent = Cm(1.5)
    pf.space_before = Pt(2)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    run = p.add_run(text)
    set_font(run, size=16)
```

### Default Style

Also set on `doc.styles['Normal']` so any text the user adds later inherits correctly:

```python
style = doc.styles['Normal']
style.font.name = FONT_NAME
style.font.size = Pt(16)
rPr = style.element.get_or_add_rPr()
rFonts = rPr.find(qn('w:rFonts'))
if rFonts is None:
    rFonts = style.element.makeelement(qn('w:rFonts'), {})
    rPr.insert(0, rFonts)
rFonts.set(qn('w:eastAsia'), FONT_NAME)
rFonts.set(qn('w:ascii'), FONT_NAME)
rFonts.set(qn('w:hAnsi'), FONT_NAME)
```

## Conditional profile: LangTake-style Thai reports

Use this profile only when the user asks for a Thai document to “look like LangTake” or another named reference. It changes the visual profile, not the user's explicit structure: retain requests such as no cover, no table of contents, and continuous numbering.

1. Inspect the real reference first when available (DOCX/ODT/PDF or screenshots). Compare representative rendered pages and OOXML/style metadata; do not claim an exact match from a prose description alone.
2. For the verified LangTake-like profile, use A4 with 2.54 cm margins on all sides, a centered black title around 22 pt bold, black 16 pt bold numbered headings aligned left, and 16 pt justified body text with about 1.25 cm first-line indent. Use compact 1.0–1.15 line spacing (1.05 is a practical default), modest heading spacing, and single spacing in tables/references. Keep the title and headings black and use simple light-gray tables unless the reference clearly uses color.
3. Do not trust built-in Word styles. `Title` can inject a theme-blue bottom border and `Heading 1`/`Caption` can inject theme-blue text. Explicitly set run/style color to `000000`; remove inherited `w:pBdr`; bind `w:rFonts` for `ascii`, `hAnsi`, `eastAsia`, and `cs`; and set `w:szCs`/`w:lang` for Thai complex-script consistency.
4. Treat figures as visual units: keep a process diagram and its `แผนภาพที่ ...` caption on the same page. Add a deliberate page break before a long figure or bibliography when automatic pagination would split the unit or orphan a heading, but never create a blank spacer page.
5. Verify the exported artifacts, not just the generator: run `docx_validate.py`, inspect OOXML margins/line spacing/style colors/font triplets, convert with LibreOffice, check A4 and page count with `pdfinfo`, embedded faces with `pdffonts`, required headings/URLs with `pdftotext`, and rasterize every page plus a contact sheet. Inspect the first page, tables, every figure/caption pair, changed page boundaries, and the final references page.

## Step 4 — Convert DOCX to PDF

```bash
libreoffice --headless --convert-to pdf "your_file.docx"
```

- On NixOS, `/usr/bin/libreoffice` is available.
- The PDF lands alongside the DOCX with the same basename.
- If the DOCX has Thai filenames, LibreOffice handles them fine.

## Step 5 — Verify, Then Send to Chat

After conversion, verify the real deliverables before replying:

```bash
pdfinfo "your_file.pdf" | grep -E 'Pages|Page size'
pdftotext "your_file.pdf" - | tail -n 12
pdftoppm -png -r 150 -singlefile "your_file.pdf" preview
```

Confirm that the PDF is A4, Thai text extracts normally, and the footer is present. For a visual layout check, inspect the rendered `preview.png`; this catches clipped footer text, font substitution, and awkward page breaks that text extraction misses. For short Thai academic writing that asks for an author footer, include **name, student ID, faculty, and programme/major** on one centered footer line; keep it at roughly 12 pt so it fits cleanly.

Include `MEDIA:` paths in your reply or use `send_message` with the target. Send both DOCX (editable) and PDF (ready) unless the user only asked for one.

## Evidence-grounded Thai research reports

Use this workflow when a Thai report must answer a supplied brief and support factual claims with authoritative or peer-reviewed evidence:

1. **Read the primary brief first.** Fetch the user-provided document or URL directly, preserve a local evidence copy, and enumerate the exact deliverables, thresholds, and question count. Do not infer what “from item 3 onward” means from a summary; verify the document's own headings and task text.
2. **Build a source ledger before drafting.** Register the brief when it is cited and add official sources (EPA, NOAA, USGS, regulators, standards bodies) plus peer-reviewed studies. Fetch each selected page/PDF, save its text under the working cache, and attach verbatim quotes with `sources.py quote`; never cite a page that was only seen in a search-result snippet.
3. **Draft a Markdown source of truth.** Put numeric markers such as `[n]` immediately after factual claims, distinguish measured findings from the team's recommendations, state when a result is site- or experiment-specific, and avoid promising scientific certainty that the evidence cannot support. Keep factual provenance dense; target at least 75% cited prose for research reports.
4. **Generate the bibliography from the ledger.** Include a `Sources:` marker in the Markdown, then run `sources.py render --style plain --replace-in <draft.md>`. Run `sources.py verify --evidence --min-coverage 0.75 --strict <draft.md>` and fix every failure. If strict mode flags more than three citations in one sentence, consolidate to the smallest set of sources that directly supports that sentence rather than ignoring the warning.
5. **Honor explicit report formatting over generic essay defaults.** If the brief requests a numbered header structure, no cover, and no table of contents, preserve those requirements even when the document skill normally favors a prose essay. For a long report, keep headings numbered continuously, use real DOCX tables for comparison/monitoring matrices, and render process diagrams as actual flow boxes rather than leaving raw arrow text.
6. **Verify the deliverables, not just the generator.** After DOCX creation, run package validation and text extraction. After LibreOffice conversion, check A4 dimensions with `pdfinfo`/`pdf_read.py --meta`, confirm embedded fonts with `pdffonts`, confirm Thai text and required headings with `pdftotext`, and render a contact sheet plus representative detail pages. A clean text extract does not prove that a table or flowchart is visually usable.

See `references/evidence-grounded-thai-report-workflow.md` for the reusable checklist, citation-ledger patterns, and the evidence notes captured from the Exxon Valdez case.

## Layout preferences from this user

When creating Thai school essays for Thanachot, use this default formula unless the user says otherwise:

- **Paper**: A4
- **Margins**: top/bottom 2.54 cm, left/right 3.0 cm
- **Font**: TH SarabunPSK
- **Title**: 18 pt, bold, centered
- **Body**: 16 pt, justified
- **First-line indent**: about 1.25 cm
- **Line spacing for Thanachot's numbered reports**: Use 1.5-line spacing for body prose and numbered lists with 0 pt before/after. Use single spacing inside tables and references. Keep spacing before/after only on section headings and the title so paragraph gaps are not accidentally added on top of 1.5 lines.
- **Footer**: author/student information only

Additional preferences:
- Keep the essay as clean prose only; do not show outline labels or meta notes in the final body unless explicitly requested.
- For short school essays, prefer **3 coherent paragraphs** and expand the existing paragraphs rather than fragmenting into many short ones.
- If the user asks for a specific word count or "write new and expand," grow the existing paragraphs in place instead of adding lots of new paragraphs.
- Keep author/student information in the footer rather than inside the title block.
- Keep the title separate from author metadata; do not merge the name into the heading.
- For "one page" requests, tune spacing and paragraph density first, then trim only if needed; avoid deleting an entire section unless unavoidable.
- For photo-comparison reports, use concise formal descriptions: one short sentence per comparison point unless the user asks for a detailed analysis. Do not repeat the same before/after observation in the introduction and conclusion.
- When a user asks to reduce descriptive text, preserve the numbered comparison headings and factual distinctions, but rewrite each item to its essential visual finding; re-export both DOCX and PDF and verify the revised pagination.

## Session-specific formatting notes

See `references/session-layout-notes.md` for the exact formatting observed in a real Thai essay DOCX from this session (margins, paragraph spacing, font binding, and PDF font embedding verification).

## Player guides, branding, live configuration, and recipe visuals

For Minecraft player guides that contain crafting recipes, prefer actual item images over monospaced text grids. Render each recipe as a centered 3×3 card with fixed-size equal cells; preserve blank cells so the grid never shifts. Suppress the original text code block when inserting the image so the recipe is not duplicated. Reuse verified local or authoritative Minecraft assets, and place every icon into the same fixed inner canvas (for example 60×60 px with nearest-neighbor scaling) because proportional thumbnails make 16×16 and 160×160 textures appear different sizes. Explicitly map display labels such as `Obsidian`, `Pickaxe`, and `End Crystal` to verified filenames. Insert the card image directly into the DOCX rather than relying on Markdown image syntax that a simple converter may drop. Validate the actual PNG signature, not a double-escaped string, and reject HTML error pages saved as `.png`. After rebuilding, verify the DOCX contains the expected number of `word/media/*` images, the PDF remains A4, and the updated Google Doc exposes the expected `inlineObjects` count. Inspect the rendered page visually before claiming completion.

When updating an existing Google Doc, select the intended account-scoped credentials explicitly, verify authentication before writing, upload the regenerated DOCX while preserving the document ID, then fetch the document through the Docs API and verify both text markers and inline object count. Return the verified `webViewLink`, not a guessed URL, and do not claim completion from the upload response alone.


For public game/server guides, apply an audience gate before drafting: keep normal player paths, player commands, compatibility, schedules, and troubleshooting; remove administrator commands, internal paths, monitoring/dependency inventories, and implementation details. Derive manual contents lists from the current headings so removed admin sections cannot survive in a stale TOC.

When the guide mirrors live configuration, normalize storage units into game/UI units before editing either the server or the document. Read config comments or source first, then state both units where ambiguity is likely (for example, whole hearts versus Minecraft health points). Never turn an informal “40 units” request directly into `40` whole hearts without checking what the field counts.

When a user supplies a logo, resolve the exact requested near-duplicate filename, validate the image, sample its palette, preserve aspect ratio, and inspect both the cover and a full-document contact sheet. If updating an existing Google Doc, preserve its ID with Drive `files.update` and verify required/stale text, font family, themed colors, and `inlineObjects` through the Docs API.

See `references/player-guide-branding-and-unit-validation.md` for the verified audience, unit-mapping, logo-theme, and existing-Google-Doc update checklist.

## Recipe and Texture Tables

For Minecraft player guides, render crafting recipes as centered 3×3 image cards rather than leaving a monospaced text grid beside the image. Keep fixed-size square cells, preserve empty slots, preserve texture aspect ratio, and insert the card directly into the DOCX. Validate every asset before embedding: check the PNG signature with `b'\\x89PNG\\r\\n\\x1a\\n'`, open it with Pillow, and reject HTML error pages saved as `.png`. Map each display label to the exact item/block texture and cross-check every generated card against the authoritative recipe source/config; `diamond_block` is not `diamond`, and similar item/block pairs must never share an approximate asset. Inspect all recipe cards, not only the one named in the request. For Thai titles or fallback labels rendered into PNGs, never use `ImageFont.load_default()`; load a known Thai-capable installed TTF with Pillow (for example Kanit-Regular). After rebuilding, inspect the rendered PDF and count `word/media/*`; a successful DOCX build alone does not prove that textures are visible. Use a clearly styled fallback only when the exact texture is unavailable, and do not present a red placeholder as a real Minecraft texture. When updating an existing Google Doc, preserve its ID and verify the resulting `inlineObjects` count through the Docs API.

See `references/recipe-texture-validation.md` for the reproducible texture-card and PDF verification checklist.

When generating recipe cards with Pillow, never use `ImageFont.load_default()` for Thai labels or titles: it produces missing-glyph boxes. Load a known Thai-capable installed TTF (for example Kanit-Regular) explicitly with `ImageFont.truetype`, and use a separate smaller Thai-capable font for fallback labels. Before presenting the card, visually inspect the PNG itself and compare its grid against the authoritative recipe/config (not a hand-copied approximation); for configurable mods, derive the displayed pattern and ingredient mapping from the same source used by the runtime where practical. Include the actual update date consistently in the source Markdown and generated cover, then verify the new date via extracted PDF text.

## Numeric citation-marker removal

When a user explicitly asks to remove markers such as `[2][14]`, distinguish bracketed citation markers from ordinary scientific numbers. Remove all `\[\d+\]` markers from the requested scope, including bibliography labels only when the user says “all”; preserve dates, measurements, years, percentages, section numbers, and result ranges. Rebuild the DOCX/PDF, assert the generated artifacts contain no remaining numeric bracket markers, confirm required facts/URLs remain, and re-render changed pages to catch orphaned punctuation or spacing. Do not invent replacement citations or claim that numbered traceability remains after removal. See `references/numeric-citation-marker-removal-and-verification.md` for the exact procedure and verification probes.

## Verified repair path for an existing DOCX

When an attached DOCX needs a formatting or compatibility repair but direct `python-docx` tooling is unavailable, preserve the original in a separate directory, then use LibreOffice headless to round-trip the source into a new DOCX (`--convert-to docx`) and export that new artifact to PDF. This is a compatibility-normalization step, not permission to overwrite the source. Verify the regenerated PDF with `pdfinfo`, `pdffonts`, and `pdftotext`; render every page with `pdftoppm` and inspect a contact sheet. For verification renders, create a fresh subdirectory rather than deleting an existing preview directory, since destructive cleanup may require approval. Report the new DOCX/PDF paths and hashes only after the checks pass.

## Pitfalls

- **Namesake software projects in feature guides**: When documenting installed mods/plugins or other software, inspect the exact installed artifact metadata (for example `fabric.mod.json`, manifest, or package metadata), live config, and local source before using web documentation. Project names can collide; bind every command table and source URL to the installed author/project/version rather than the most popular similarly named project.
- **Literal pipes inside Markdown tables**: A command such as `<classic|slim>` can be split into extra cells by simple Markdown-to-DOCX parsers. Escape the pipe, use a parser that understands escaped delimiters, or rewrite it as `(classic หรือ slim)`. Render and inspect the affected table after conversion—text extraction alone may still contain all words while the visual columns are wrong.
- **Inline HTML and long endpoints in Markdown tables**: Simple Markdown-to-DOCX converters may drop text after `<br>` or wrap long hostnames across lines with an inserted visual hyphen. Avoid inline HTML inside table cells; use semicolons or native paragraph breaks generated by the converter. Assert endpoint components in extracted text, but also render the affected page and inspect whether the complete hostname/IP and port remain unambiguous.
- **Post-edit visual verification**: After any substantive content correction, regenerate both DOCX and PDF, render the edited page at readable resolution, and inspect it directly. For long documents, also create a low-resolution contact sheet of every page to catch blank pages, orphaned headings, clipped tables, and inconsistent spacing. Verify A4/page count and confirm the requested font is embedded with `pdffonts`.
- **Missing east-asia font binding**: The single most common failure. Without `w:eastAsia` on the run XML, LibreOffice renders all Thai text as `[]` boxes regardless of the font name set on the run. Always set east-asia on every run AND the Normal style.
- **Family alias vs. PostScript name**: Verify the installed family before generating with `fc-match -v 'TH SarabunPSK'` and `fc-query --format='%{family} %{fullname} %{postscriptname}\\n' <font-file>`. The DOCX must use the family name (`TH SarabunPSK`), while `pdffonts` may report the file's internal PostScript name (for example `THSarabunIT๙`) even when it is the correct family. Confirm the PDF contains only the requested family and its bold/italic faces.
- **Unsupported symbols and fallback fonts**: TH SarabunPSK may not contain Unicode arrows or other symbols. Check glyph coverage before inserting symbols; use a vector/PNG graphic or a supported character instead of allowing LibreOffice to introduce an unrelated fallback font. Re-run `pdffonts` after conversion.
- **Wrong font PostScript name**: Check via `fc-list | grep -i <fontname>` — the `:style=` part tells you the exact PS name to use in python-docx. TH SarabunPSK usually appears as `TH SarabunPSK`.
- **Visible draft markers**: Do not leave labels like `[คำนำ]`, markdown headings, or reviewer notes in the final essay body unless the user explicitly asked for an outline.
- **Author name in the heading**: If the user wants a formal school essay, keep the heading as title only; place name/ID in footer or a faint bottom-right block.
- **Too many paragraphs**: Prefer enlarging paragraph content over adding more paragraphs when the user wants length without fragmentation.
- **User asks for one page**: Tighten spacing and trim transitions rather than removing a whole structural section unless necessary; preserve the three-part structure and keep the conclusion brief.
- **LibreOffice not installed**: Check with `which libreoffice`. On NixOS, if missing: `nix-shell -p libreoffice` or ensure it's in environment.systemPackages.
- **DOCX with complex Thai content (tables, images)**: LibreOffice may paginate differently than Word. Preview the PDF after conversion.
- **Very long essays (>4 pages)**: Consider breaking content into sections in the Python script for readability.

See `references/essay-style-user-preferences.md` for the current Thai essay style preferences and the clean-output requirement. See `references/essay-layout-session-notes.md` for the no-visible-headings layout used in this session. See `references/thai-essay-layout-notes.md` for this session's layout decisions.

## Related Skills

- `thai-text-image-render` — for Thai text in images/PIL (same font concern, different output)
- `powerpoint` — similar workflow for .pptx

## Integrated verification and documentation accuracy


# Thai documentation verification and question style

## When to Use

Use for Thai DOCX/PDF reports, attached documents, Hermes documentation, configuration, CLI, troubleshooting, or any user-facing clarification that depends on document or official documentation accuracy.

## Verify source documents

1. Treat attached document files, including `.docx` and `.pdf`, as sources that must be inspected directly before making claims about their contents. Preserve the original filename and file type; do not replace a source with a guessed rewrite.
2. For existing Thai reports, inspect the editable DOCX and the exported PDF. Compare extracted text, headings, tables, figures/captions, references, metadata, and rendered pages.
3. Preserve the original artifact before editing. Save a new output unless the user explicitly requests an in-place replacement and a recoverable backup exists.
4. Do not invent facts, citations, authors, dates, DOIs, measurements, or successful verification results. If metadata is unavailable, label it as unavailable or use a safe no-date form.

## Verify Hermes documentation

1. For Hermes behavior, configuration, CLI, tools, skills, providers, or gateway features, treat `https://hermes-agent.nousresearch.com/docs` as authoritative.
2. Load `hermes-agent` before acting on Hermes-specific requests.
3. Check relevant official documentation with `web_extract` or `web_search` when behavior or exact commands may have changed.
4. Prefer primary documentation over memory or stale skill text. If they disagree, follow the official docs and mention the discrepancy briefly.
5. After changes or troubleshooting, verify with live CLI or tool output.
6. Never invent commands, options, URLs, or successful results.

## Thai DOCX/PDF verification checklist

1. Run the document validator and confirm the DOCX opens successfully.
2. Inspect OOXML for A4 dimensions, margins, heading order, table/figure structure, page fields, inherited borders/colors, and Thai font bindings: `ascii`, `hAnsi`, `eastAsia`, `szCs`, and `w:lang`.
3. Convert with LibreOffice and check `pdfinfo` for page count, A4 geometry, rotation, metadata, and file size.
4. Check `pdffonts` and confirm the requested Thai font faces are embedded.
5. Extract PDF text with `pdftotext` and probe required headings, citations, URLs, dates, measurements, and forbidden draft markers.
6. Render every page and create a contact sheet. Inspect the first page, changed pages, tables, figures/captions, appendix, and references page for blank pages, orphan headings, clipping, overlap, broken Thai characters, malformed URLs, and awkward pagination.
7. After any content or formatting change, rebuild both DOCX and PDF and repeat the checks. Do not report success from the source Markdown or generator output alone.
8. For citation changes, use an exact text search over both DOCX-extracted text and PDF-extracted text. Confirm that only the requested citation markers changed and that factual numbers such as dates, quantities, percentages, and years remain.

## Question punctuation

1. Never use the `?` character in questions directed to the user.
2. Rewrite questions as polite prompts or statements ending with a period, for example `Please provide the file path.` or `Please choose the provider.`
3. Apply this to clarifying prompts, confirmations, and rhetorical questions.
4. Keep wording concise and natural.



