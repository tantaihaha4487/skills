---
name: bw-grid-pdf
description: Creates dense, print-ready reference/cheat sheets and study notes as landscape PDFs using a black-and-white grid layout — bold headers, light-weight body text, hairline dividers between cells, no color, no shadows, no decoration. Use this whenever the user wants a "cram sheet," "cheat sheet," "quick reference," "study note," "one-pager," or exam/interview prep PDF that needs to pack a lot of scannable information onto one or a few landscape pages. Works for any language, including Thai and other non-Latin scripts (auto-installs the right fonts). Trigger this even if the user just says "make this into a PDF I can print and study from" or "turn this into a landscape grid PDF" — those phrases describe this exact design. Do not use this for long-form documents, essays, or anything meant to be read top-to-bottom in prose (use the docx or pdf skill for that instead).
---

# B/W grid cram sheet PDF

A dense, scannable, print-friendly landscape PDF design: pure black-and-white,
content arranged in a grid of bordered cells, bold headers over light-weight
body text. Built for fitting a lot of "must-know" material onto as few pages
as possible without feeling cluttered — the whitespace and hairline rules do
the organizing instead of color.

Use this skill for cram sheets, cheat sheets, quick references, study notes,
onboarding one-pagers, and similar dense reference documents. Don't use it
for anything meant to be read as flowing prose (a report, an essay, a letter)
— that's the `docx` or `pdf` skill's job.

## Before you start

1. **Figure out the content first, in chat, before touching HTML.** Group the
   material into topic blocks (a block = one bordered cell = one clear idea,
   roughly 3-8 lines when rendered). Count the blocks. This tells you the
   grid size you need (see "Choosing the grid" below). Don't start writing
   HTML until you know roughly how many blocks you have and how dense the
   user wants it — ask if it's unclear whether they want 1 page (very dense)
   or several pages (more breathing room).

2. **Show a mockup before generating the real PDF**, unless the user has
   already approved a design in this conversation or explicitly says to skip
   this step. Use the Visualizer (`visualize:show_widget`, `mockup` module)
   to render one representative page/cell in-chat — white background, black
   text/borders only, actual sample content from the user's material (not
   lorem ipsum) — and get sign-off on layout, density, and font sizing
   before running the full pipeline. This design has a lot of small
   knobs (columns, rows, font sizes) and it's much cheaper to correct in a
   quick mockup than after a full weasyprint render.

3. Once approved, build the real PDF with the pipeline below.

## Design system

Reuse `assets/template.html` as the starting point — don't reinvent the CSS.
It already encodes all of the rules below.

- **Page**: `@page { size: 297mm 210mm; margin: 10-12mm; }` — A4 landscape.
  Adjust `size` for other paper (e.g. `279mm 216mm` for US Letter landscape).
- **Color**: pure `#000000` text/borders on `#ffffff`. No gray fills, no
  color, no shadows, no gradients. This is a print design — it must still
  read cleanly if photocopied.
- **Weight contrast is the whole hierarchy.** Headers are bold (700),
  body text is light (300). Don't add a third weight — the two-weight
  contrast is what makes the page scannable at a glance. If the user asks
  for "light for body," that means `font-weight: 300`, not just a smaller
  font size.
- **Grid layout**: CSS Grid (`display: grid`), one `<div class="col">` per
  cell, `border-right: 1px solid #000` between columns (skip it on the last
  column), a `border-bottom` between stacked rows. Every visible division on
  the page should be a hairline rule, never a gap alone — gaps alone read as
  accidental misalignment when printed.
- **Block anatomy inside a cell**: a `.block-title` (bold, ~10-13px, with a
  `border-bottom` under it) followed by `.body-text` (light, ~9-11px,
  `line-height: 1.4-1.7`). Optional `.trap-box` (bordered callout, for a
  warning/gotcha) and `<table>` (bold header row with a thicker
  `border-bottom`, light data rows with hairline row dividers) round out the
  vocabulary — reuse these classes verbatim rather than inventing new ones.
- **Header bar**: one per page, bold title (~16-19px) + light metadata
  (page number, source, date) right-aligned, separated from the body by a
  `2-2.5px solid #000` rule — thicker than the internal hairlines so the
  eye immediately finds the page title.

## Choosing the grid

Match grid shape to how much content you have and how many pages the user
wants. Rough capacity per cell at these font sizes is 3-8 short lines —
use this to reverse-engineer the grid from the block count, not the other
way around.

| Blocks of content | Pages wanted | Grid shape |
|---|---|---|
| ~8-12 | 1 page, roomy | 1 row × 3-4 columns |
| ~12-20 | 1 page, dense | 2 rows × 4 columns |
| ~10-16 | 2 pages | 1 row × 4 columns, per page |
| 20+ | multiple pages | one `<div class="page">` per topic group, 3-4 col grid each |

When asked to compress an existing multi-page version into fewer pages,
don't just shrink the font past ~8px body / ~10px header — instead add more
columns per row, or stack a second `.row` within the page (see
`template.html` for the two-row pattern). Font sizes below 8px stop being
legibly printable even though they render fine on screen.

## Fonts and non-Latin scripts

The sandbox doesn't ship Thai (or many other non-Latin) fonts by default.
Before rendering, check what's available and install if needed:

```bash
fc-list | grep -i thai   # swap "thai" for the relevant script
```

If nothing relevant comes back:

```bash
apt-get install -y fonts-thai-tlwg fonts-noto   # Thai
# or, generically, fonts-noto-cjk (CJK), fonts-noto (broad coverage)
```

`Noto Sans Thai` (and most Noto families) ship Regular and Bold weights,
which is exactly the two-weight contrast this design needs — set
`font-family: 'Noto Sans Thai', sans-serif` (with an appropriate fallback
chain for the target script) in `body`, and let `font-weight: 700` / `300`
do the rest. Always rasterize a preview page (see below) to confirm the
script actually renders — silently falling back to a tofu/box font is the
most common failure mode here.

## Rendering pipeline

```bash
pip install weasyprint --break-system-packages -q   # if not already installed
python3 -c "
from weasyprint import HTML
HTML('note.html').write_pdf('/mnt/user-data/outputs/output.pdf')
"
```

Then **always** visually QA before presenting to the user — don't skip this,
text overlap and overflow in dense grids are easy to introduce and easy to
miss by reading the HTML alone:

```bash
pip install pdf2image --break-system-packages -q
apt-get install -y poppler-utils -q
python3 -c "
from pdf2image import convert_from_path
imgs = convert_from_path('/mnt/user-data/outputs/output.pdf', dpi=110)
for i, im in enumerate(imgs):
    im.save(f'/home/claude/preview_{i+1}.png')
"
```

View each `preview_N.png` with the `view` tool. Check for: text overflowing
a cell's height, tables wider than their column, a page that's mostly empty
(font/grid too generous — tighten it) or visibly cramped (loosen it), and
that bold/light contrast is actually visible at the rendered size. Iterate
on `note.html` and re-render until every page looks clean, then present the
final PDF with `present_files`.

## Common mistakes to avoid

- **Flexbox column layouts for multi-column text** can cause overlap in
  weasyprint. Use CSS Grid (`display: grid`) for the column structure, not
  `display: flex` with `flex-direction: column` on the parent.
- **Don't use a third font weight or any color** to add emphasis — that
  breaks the two-weight, black-and-white system. Use a `.trap-box` border or
  a `⚠` glyph in a bold label instead.
- **Don't shrink font size indefinitely to force a page count.** Below
  ~8px the sheet stops being printable/legible. If content doesn't fit at a
  readable size, add columns/rows or add another page instead, and say so.
- **Check the rendered preview, not just the HTML source**, before telling
  the user it's done — weasyprint's text-wrapping and table-sizing behavior
  is genuinely hard to predict from markup alone.
