# Recipe Texture Validation

Use for Thai Minecraft guides with crafting recipes.

1. Download assets from the installed resource pack or an authoritative Minecraft asset repository; never assume a URL ending in `.png` returned an image.
2. Validate each file with `file` and PNG signature `89 50 4e 47 0d 0a 1a 0a`; reject HTML error pages.
3. Build one centered 3×3 card per recipe. Give every cell identical dimensions, keep blank slots, and place every icon into the same fixed inner canvas (for example 60×60 px with nearest-neighbor scaling for pixel art); proportional thumbnails make textures with different transparent padding appear unequal. Map display labels explicitly to verified filenames (`Pickaxe`, `End Crystal`, and `Obsidian` commonly differ from the source path).
4. Do not render the original Markdown/code-block recipe alongside the image card; it creates duplicate layouts. Suppress the code block when inserting the card.
5. Rebuild DOCX and PDF, inspect the affected page visually, check `pdfinfo` for A4, and inspect the DOCX zip for expected `word/media/*` count.
6. If syncing to an existing Google Doc, use Drive update with the original file ID, then fetch the Docs API representation and verify inline objects plus required text markers.

Known failure pattern: comparing a file header to a literal escaped string such as `b'\\\\x89PNG...'` makes every valid texture look missing. Use actual bytes: `b'\\x89PNG\\r\\n\\x1a\\n'`.
