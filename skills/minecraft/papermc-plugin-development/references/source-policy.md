# Source and Freshness Policy

Load this reference before making version-sensitive API or build decisions. The bundled references preserve decision rules, not a frozen copy of Paper's documentation.

## Establish the target first

Record the repository's Minecraft/Paper version or range, Java toolchain, Paper API coordinate, mappings model, Adventure version when pinned, and Folia claim. Treat an unresolved target as a blocking unknown for API signatures and compatibility claims.

## Use authoritative sources in this order

1. Use the repository's contracts, build files, descriptors, compatibility policy, and generated-resource configuration to establish intent.
2. Use the current [Paper developer documentation](https://docs.papermc.io/paper/dev/) for supported workflows and conceptual guidance.
3. Use the [Javadocs for the exact target Paper version](https://jd.papermc.io/paper/) for signatures, annotations, nullability, threading notes, experimental status, deprecations, and replacements.
4. Use Paper-owned repositories such as [Paper](https://github.com/PaperMC/Paper), [paperweight-test-plugin](https://github.com/PaperMC/paperweight-test-plugin), and [Folia](https://github.com/PaperMC/Folia) for source-level behavior and official examples.
5. Use [PaperMC news](https://papermc.io/news/) and the [roadmap](https://docs.papermc.io/paper/dev/roadmap/) for migrations and announced removals.

When official sources disagree, prefer the source scoped to the exact target and record the discrepancy and access date. Do not generalize a current Javadoc statement backward to older targets.

## Keep volatile facts live

Re-check rather than memorize:

- dependency coordinates, build numbers, beta/stable status, and Java requirements;
- experimental APIs and annotations;
- bundled libraries and runtime mappings;
- deprecated and scheduled-for-removal APIs;
- Folia scheduler behavior and support restrictions;
- client protocol, registry, recipe, and data-component behavior.

Use the reference files to decide what must be checked. Never copy their example version into a project without matching the repository's target.

## Handle gaps

Use community material only when the official sources do not answer a necessary question. Label it as non-authoritative, corroborate it with code or a runtime test, and never let it override an official contract. Do not introduce a community framework merely because it is popular.

## Report evidence

For a version-sensitive change, include the target version, official pages or Javadocs consulted, the build/runtime evidence obtained, and any claims that remain unverified. Prefer links to the exact class or guide over generic search results.

