# Minecraft Engineering Skills

Reusable Agent Skills for developing PaperMC plugins and Fabric Minecraft mods. The skills follow the standard `SKILL.md` layout and include their supporting references, scripts, and Codex UI metadata.

## Install with `npx skills`

Install both skills into the current project:

```bash
npx skills@latest add tantaihaha4487/skills --agent codex --skill '*' --yes
```

Install one skill by name:

```bash
npx skills@latest add tantaihaha4487/skills --skill papermc-plugin-development
npx skills@latest add tantaihaha4487/skills --skill fabric-mod-development
```

Use `--global` with `--agent codex` to install them into your user-level Codex skills directory.

## Included skills

- `papermc-plugin-development` — analyze, implement, debug, test, migrate, and maintain PaperMC plugins, including Folia-aware projects.
- `fabric-mod-development` — analyze, implement, debug, test, and migrate Fabric mods while preserving exact Minecraft and Loader compatibility.

Each skill is under [`skills/minecraft/`](skills/minecraft/) and is independently installable by its frontmatter name.

