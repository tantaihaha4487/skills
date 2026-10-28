---
name: bw-grid-pdf
description: Create dense, printable landscape PDFs for cram sheets, cheat sheets, quick references, study notes, one-pagers, and exam/interview prep. Use this when asked for a PDF to print and study from or a landscape grid PDF, including Thai and other scripts; use a document skill for long-form prose.
---

# B/W grid cram sheet PDF

A dense, scannable, print-friendly landscape PDF: a pure black-and-white grid
of bordered cells, bold headers, and light body text. Fit must-know material onto
as few pages as possible without clutter; whitespace and hairline rules organize it.

For flowing prose (reports, essays, letters), use `docx` or `pdf` instead.

## Before you start

1. **Figure out content in chat before touching HTML.** Group it into topic
   blocks (one bordered cell = one clear idea, roughly 3-8 rendered lines);
   count them to choose the grid size below. Don't write HTML until block count
   and desired density are roughly clear; ask whether they want 1 very dense
   page or several with more breathing room if unclear.

2. **Show a mockup before generating the PDF** unless the user approved a design
   in this conversation or explicitly says to skip. Use Visualizer
   (`visualize:show_widget`, `mockup` module) to render one representative
   page/cell in chat — white background, black text/borders only, actual sample
   content from the user's material (not lorem ipsum) — and get sign-off on
   layout, density, and font size before the pipeline.

   If Visualizer is unavailable while approval is required, report
   `BLOCKED: mockup approval required` and wait for explicit approval or skip;
   either clears the gate.

3. Once approved, build the real PDF with the pipeline below.

## Design system

Reuse `assets/template.html` as the starting point; it encodes these rules.

- **Page**: `@page { size: 297mm 210mm; margin: 10mm 12mm; }` — A4 landscape.
  Adjust `size` for other paper (e.g. `279mm 216mm` for US Letter landscape).
- **Color**: pure `#000000` text/borders on `#ffffff`. No gray fills, no
  color, no shadows, no gradients. Keep it legible when photocopied.
- **Weight contrast is the whole hierarchy.** Headers are bold (700),
  body text is light (300). Don't add a third weight — the two-weight
  contrast is what makes the page scannable at a glance. If the user asks
  for "light for body," that means `font-weight: 300`, not just a smaller
  font size.
- **Grid layout**: CSS Grid (`display: grid`), one `<div class="col">` per
  cell, `border-right: 1px solid #000` between columns (skip it on the last
  column), a `border-bottom` between stacked rows. Every visible division should be a hairline rule; gaps alone misalign in print.
- **Block anatomy inside a cell**: a `.block-title` (bold, ~10-13px, with a
  `border-bottom` under it) followed by `.body-text` (light, ~9-11px,
  `line-height: 1.4-1.7`). Optional `.trap-box` (bordered callout, for a
  warning/gotcha) and `<table>` (bold header row with a thicker
  `border-bottom`, light data rows with hairline row dividers). Use these classes verbatim.
- **Header bar**: one per page, bold title (~16-19px) + light metadata
  (page number, source, date) right-aligned, separated from the body by a
  `2-2.5px solid #000` rule — thicker than the internal hairlines.

## Choosing the grid

Use one topic block per cell. A standard 2-row × 4-column page holds up to 8 blocks;
use one row for 3-4 blocks and a third row only when rendered text remains readable.
Add a page when blocks exceed available cells or a cell overflows. Do not merge blocks or
shrink body text below ~8px to meet a page target. The template supports repeated
`.row` elements.
## Fonts and non-Latin scripts

Before rendering, check coverage for the requested script:

```bash
fc-list | grep -i thai   # replace "thai" with the relevant script
```

Use an installed, bundled, or user-provided font with verified glyph coverage;
set it as the `body` family and register a local file with `@font-face` as needed.
Do not silently fall back to tofu or install fonts system-wide during generation.
If none is suitable, report the limitation before claiming a successful render.

## Rendering pipeline

```bash
# Use project or isolated Python environment; do not override the host package manager.
python3 -c "
from weasyprint import HTML
HTML('note.html').write_pdf('output.pdf')
"
```

If WeasyPrint or an equivalent project/isolated PDF renderer is unavailable,
report `BLOCKED: renderer unavailable`. Do not claim or deliver an unrendered
PDF.

Always visually QA before presenting; HTML can hide dense-grid overlap and overflow:

```bash
# Use pdf2image and Poppler from the selected project/isolated environment.
python3 -c "
from pdf2image import convert_from_path
imgs = convert_from_path('output.pdf', dpi=110)
for i, im in enumerate(imgs):
    im.save(f'preview_{i+1}.png')
"
```

Rasterize every PDF page with `pdf2image`/Poppler or an available equivalent
and inspect each with an image viewer. A browser or HTML screenshot is
not PDF visual proof. If the PDF exists but rasterization or image inspection
is unavailable, report `RENDERED: visual QA untested` and name the missing
capability. Claim `PASS` only after every page is rasterized and inspected;
report `FAIL: visual QA` for defects and iterate. Check for: text overflowing
a cell's height, tables wider than their column, a page that's mostly empty
(font/grid too generous — tighten it) or visibly cramped (loosen it), and
that bold/light contrast is actually visible at the rendered size. Iterate
on `note.html` and re-render until every page looks clean, then present the
final PDF using the current environment's supported file-delivery method.

## Common mistake

- For multi-column text, use CSS Grid to avoid WeasyPrint overlap; don’t combine `display: flex` and `flex-direction: column`. The template’s `.page`/`.grid` stack page content/rows with flex; `.row` Grid owns columns.
