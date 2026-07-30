# Compatibility and tooling

## Authority

Use current Iris documentation first:

- https://shaders.properties/current/
- https://irisshaders.dev/
- https://github.com/IrisShaders/ShaderDoc

Use shaderLABS for learning and templates:

- https://shaderlabs.org/wiki/Getting_Started
- https://shaderlabs.org/wiki/Rendering_Pipeline_(OptiFine,_ShadersMod)
- https://github.com/shaderLABS/Base-330

Use Iris examples for structure and idioms:

- https://github.com/IrisShaders/Iris-Example-Shaderpack
- https://github.com/IrisShaders/Aperture-Example-Pack

## Version discipline

Before implementation, record Minecraft, loader, Iris, Sodium, GPU/OpenGL, and relevant rendering mods. Iris currently documents Fabric support from 1.16.5+ and NeoForge support from 1.21.1+, with Forge unsupported; verify these statements against the current site before publishing a compatibility table.

Iris ships with or integrates with Sodium. Rendering-mod interactions are not universal: Nvidium disables itself with shaders, Distant Horizons and Voxy need explicit pack support, Canvas/Vulkan/OptiFine are incompatible, and Indium requirements depend on the Minecraft/Sodium version. Test the actual target matrix.

## Development setup

A plain text editor works. VS Code can use GLSL syntax highlighting and the `vscode-mcshader` language server for Minecraft-specific linting/includes, but availability and platform support vary. A known-good Base-330 pack is a better baseline than inventing an empty pack.

## Distribution

Keep licenses intact when adapting templates or examples. Do not copy OptiFine documentation verbatim. State whether the pack is Iris-only or also targets OptiFine, list tested Minecraft/Iris/Sodium versions, and package a ZIP whose root has the expected `shaders/` directory.
