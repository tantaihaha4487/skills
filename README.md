# Agent Skills

Reusable agent skills for practical engineering and collaboration. They are designed to be small, composable, and grounded in the target task's actual constraints.

## Quickstart

Install the skills into your project with the [skills.sh](https://skills.sh/) installer:

```bash
npx skills@latest add tantaihaha4487/skills
```

Select the skills and coding agents you want during installation. To install all skills for Codex automatically:

```bash
npx skills@latest add tantaihaha4487/skills --agent codex --skill '*' --yes
```

Install a single skill by name:

```bash
npx skills@latest add tantaihaha4487/skills --skill papermc-plugin-development
npx skills@latest add tantaihaha4487/skills --skill fabric-mod-development
npx skills@latest add tantaihaha4487/skills --skill iris-shader-development
npx skills@latest add tantaihaha4487/skills --skill thai-docs
```

Use `--global` with `--agent codex` to install them in your user-level Codex skills directory.

## Included skills

### PaperMC Plugin Development

[`papermc-plugin-development`](skills/minecraft/papermc-plugin-development/SKILL.md) helps analyze, design, implement, debug, test, migrate, and maintain PaperMC plugins, including Folia-compatible projects.

### Fabric Mod Development

[`fabric-mod-development`](skills/minecraft/fabric-mod-development/SKILL.md) helps analyze, implement, debug, test, and migrate Fabric Minecraft mods while preserving exact Minecraft, mappings, Loader, Loom, and Fabric API compatibility.

### Iris Shader Development

[`iris-shader-development`](skills/minecraft/iris-shader-development/SKILL.md) covers version-aware Minecraft shader-pack development for Iris with Sodium, including gbuffers, shadows, deferred/composite/final passes, shader properties, buffer formats, compatibility debugging, performance, and packaging.

### Thai Documentation

[`thai-docs`](skills/productivity/thai-docs/SKILL.md) combines Thai DOCX/PDF creation with rigorous verification: A4 and margin checks, Thai font binding and embedding, LibreOffice export, text extraction, citation checks, and rendered-page inspection.

## Engineering workflow

The engineering skills follow an evidence-first workflow:

1. Understand the repository and its instructions.
2. Analyze the existing architecture and resolved dependencies.
3. Plan around the correct lifecycle, API, and logical side.
4. Implement the smallest maintainable change.
5. Validate with focused tests, builds, and runtime checks.
6. Summarize the result with explicit evidence and remaining boundaries.

## License

MIT
