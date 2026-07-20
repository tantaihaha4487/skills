# Testing and validation

## Contents

[Scope](#load-this-reference-when) · [Sequence](#minimum-validation-sequence) · [Evidence matrix](#evidence-matrix) · [Artifact](#inspect-the-artifact) · [Runtime](#runtime-scenarios) · [Threading](#threading-validation-questions) · [Traps](#traps) · [Reporting](#completion-report)

## Load this reference when

Load this file before implementing a nontrivial change and again before declaring it complete. Use it to select evidence proportionate to the change's lifecycle, threading, persistence, compatibility, and artifact risk.

## Follow repository-native validation

Paper does not mandate a unit-test framework or repository layout. Use the checked-in Gradle or Maven wrapper and existing formatting, static-analysis, unit, integration, run-server, and CI tasks. Do not introduce a new framework merely to satisfy a generic checklist.

Pure Java domain logic can be proven with unit tests. Plugin loading, descriptors, commands, events, scheduler context, world access, persistence, and shutdown require a real Paper runtime or an existing integration harness that proves the same contract.

## Minimum validation sequence

1. Run the narrowest compile or test gate that gives fast feedback.
2. Run existing check and test tasks for affected modules.
3. Review compiler warnings and deprecations; do not hide them.
4. Run the production build or packaging task.
5. Inspect the exact JAR intended for deployment.
6. Start a clean temporary server on the target Java and Paper version.
7. Exercise changed registration, behavior, failure, disable, and restart paths.
8. Expand to the declared version and Folia matrix when compatibility is affected.

Do not use server /reload as a substitute for disable and restart.

## Evidence matrix

| Change surface | Required evidence |
| --- | --- |
| Build or dependency | Wrapper resolution, affected module compilation, production artifact, JAR class and dependency inspection |
| Descriptor | Root descriptor, resolved placeholders, referenced classes, clean load, dependency scenarios |
| Lifecycle | Clean enable, partial-failure handling where relevant, clean disable, restart |
| Command | Registration, syntax/help, permissions, success and invalid-input paths |
| Event | Listener registration, expected event path, cancellation or priority semantics relevant to the feature |
| Configuration | Default creation, existing-file load, invalid-value behavior, save, plugin-specific reload if supported |
| Scheduler or async | Proof of callback context, no blocking tick-owning thread, correct re-entry before Bukkit mutation |
| Database or external I/O | Failure handling, bounded/background execution, flush and close on disable |
| Persistence | Write, restart, read, corrupt or missing data behavior when relevant |
| Optional plugin integration | Provider present, absent, and disabled or unavailable behavior |
| NMS or mappings | Exact target compilation, class loading, feature path on every claimed adapter |
| Folia | Separate Folia startup and affected region/global/entity scheduler paths |
| Release | Version agreement, artifact identity, target matrix, publication result |

## Inspect the artifact

Inspect the deployable JAR rather than trusting source layout:

- intended descriptor or descriptors at the JAR root;
- no unresolved resource placeholders;
- named main, bootstrap, and loader classes;
- no bundled Paper or Bukkit API;
- expected shaded libraries and relocation;
- merged META-INF services when required;
- no duplicate unintended descriptors;
- expected configuration and localization resources;
- correct mapping form for target-specific internal artifacts.

## Runtime scenarios

Use a clean test server or the repository's official run task. Capture:

- server and Java versions;
- complete startup section for the plugin;
- assertions or commands proving the changed path;
- relevant warnings, exceptions, and stack traces;
- disable and process-exit behavior;
- restart and persisted-state behavior.

For stack traces, identify the first plugin-owned frame and preserve the full causal chain. Do not dismiss warnings merely because the server remains running.

When the plugin declares a range, test at least the minimum and newest supported boundary. When it declares folia-supported, Paper success is not Folia evidence.

## Threading validation questions

- What execution context invokes each changed callback?
- Does any path perform file, network, database, or expensive computation on a tick-owning thread?
- Does background work access Bukkit objects?
- How does background work return to the correct main, global, region, or entity scheduler?
- What happens when the plugin disables while work is queued?
- Are captured entity, world, inventory, or player references still valid when the continuation runs?

If the code cannot answer these from API contracts and tests, do not mark it safe.

## Traps

- Stopping after compile or unit tests.
- Running a system Gradle or Maven version instead of the wrapper.
- Testing a development JAR while publishing a different task's output.
- Ignoring deprecation warnings.
- Validating only a warm server with old config or dependencies present.
- Treating a mock API as proof of scheduler, classloader, or lifecycle behavior.
- Testing only the newest server while claiming a compatibility range.
- Treating Paper runtime success as Folia compatibility.
- Calling plugin-specific config reload proof of server reload support.

## Completion report

Report:

- commands and tasks run;
- artifact path and identity inspected;
- runtime versions used;
- behavior and failure paths exercised;
- warnings or known gaps;
- untested compatibility claims;
- whether Folia was applicable and, if so, tested.

State readiness narrowly. A successful build is build evidence, not runtime acceptance.

## Official sources

- [Paper debugging](https://docs.papermc.io/paper/dev/debugging/)
- [Paper project setup and run task](https://docs.papermc.io/paper/dev/project-setup/)
- [Reading stacktraces](https://docs.papermc.io/paper/dev/reading-stacktraces/)
- [How plugins work](https://docs.papermc.io/paper/dev/how-do-plugins-work/)
- [plugin.yml](https://docs.papermc.io/paper/dev/plugin-yml/)
- [Supporting Folia](https://docs.papermc.io/paper/dev/folia-support/)
- [Official paperweight example CI](https://github.com/PaperMC/paperweight-test-plugin/blob/master/.github/workflows/build.yml)
