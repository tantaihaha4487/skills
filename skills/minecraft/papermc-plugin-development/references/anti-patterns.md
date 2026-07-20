# Anti-pattern routing

## Load this reference when

Load this file during planning and review to detect a wrong direction. Follow the linked governing reference for the actual decision and validation rules; do not use this file as a substitute.

## Stop and reroute

| Warning sign | Governing concern |
| --- | --- |
| Inventing a package layout, manager layer, or dependency-injection framework | [Project architecture](project-architecture.md) |
| Editing generated resources or assuming the plain JAR is deployable | [Project architecture](project-architecture.md) |
| Bundling Paper, Bukkit, or another runtime plugin API | [Project architecture](project-architecture.md) and [Plugin descriptors](plugin-descriptors.md) |
| Calling server APIs in the JavaPlugin constructor or assuming onLoad readiness | [Plugin lifecycle](plugin-lifecycle.md) |
| Expanding static plugin access or leaving owned threads, pools, or closeables alive | [Plugin lifecycle](plugin-lifecycle.md) |
| Treating reloadConfig or server reload as lifecycle reconstruction | [Plugin lifecycle](plugin-lifecycle.md) |
| Adopting paper-plugin.yml by default or duplicating command metadata | [Plugin descriptors](plugin-descriptors.md) |
| Mismatching hard, soft, ordering, or classpath dependency declarations | [Plugin descriptors](plugin-descriptors.md) |
| Declaring Folia support to suppress warnings | [Plugin descriptors](plugin-descriptors.md) and [Testing](testing-validation.md) |
| Blocking a tick-owning thread with file, network, database, or unbounded work | [Performance](performance.md) |
| Accessing mutable Bukkit state from arbitrary async work | [Performance](performance.md) and [Testing](testing-validation.md) |
| Adding caches, polling, reflection, or utilities before measuring or reusing project code | [Performance](performance.md) |
| Reaching for NMS when a public API exists | [paperweight and internals](paperweight-internals.md) |
| Spreading mappings or reflection strings through feature code | [paperweight and internals](paperweight-internals.md) |
| Suppressing deprecations or broadening compatibility without a target matrix | [Migration and release](migration-release.md) |
| Guessing from a partial stacktrace or changing code before reproducing | [Debugging](debugging.md) |
| Stopping after compilation or testing a different JAR than the release artifact | [Testing](testing-validation.md) |

## Review rule

When a warning sign appears, pause implementation, state the violated assumption, load the governing reference, and revise the plan. If repository evidence justifies an exception, document that evidence and add validation proportional to the risk.

Prefer official Paper APIs and repository-local abstractions. Community convention is not authority when it conflicts with Paper's contracts or the existing project.

## Official policy anchors

- [Paper development documentation](https://docs.papermc.io/paper/dev/)
- [How plugins work](https://docs.papermc.io/paper/dev/how-do-plugins-work/)
- [Paper scheduling](https://docs.papermc.io/paper/dev/scheduler/)
- [Minecraft internals](https://docs.papermc.io/paper/dev/internals/)
- [Paper profiling](https://docs.papermc.io/paper/profiling/)
- [Paper roadmap and deprecations](https://docs.papermc.io/paper/dev/roadmap/)
