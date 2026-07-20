# Debugging decisions

## Load this reference when

Load this file for exceptions, failed startup, missing registrations, incorrect behavior, classloading failures, shutdown faults, or an unexplained runtime regression.

## Preserve evidence first

1. Record the server, Java, plugin artifact, configuration, dependencies, and reproduction steps.
2. Reproduce on the repository's intended run task or a clean target Paper server.
3. Preserve the full log and causal stacktrace before changing code.
4. Identify the first plugin-owned frame and trace each caused-by section to the root exception.
5. Form a falsifiable hypothesis, add the smallest observation needed, and rerun the same path.

Do not infer the cause from the final exception name alone. Context from earlier startup messages, suppressed exceptions, and dependency failures can be decisive.

## Choose the right instrument

- Use the plugin logger so output carries plugin identity; remove temporary noise after diagnosis.
- Use configurable debug logging for state transitions that may need repeat observation.
- Attach a remote debugger or use the repository's direct run-server setup for control-flow and state inspection.
- Use spark, not ad hoc timestamps, when the symptom is performance-related.
- Use thread dumps for hangs or watchdog incidents and inspect what the affected thread is waiting on.
- Use the JVM fast-throw diagnostic option only when repeated optimized exceptions omit needed stacktraces.

## Isolate by failure class

- **Load failure:** inspect the final JAR, root descriptor, named entrypoints, Java version, classpath, mappings, and hard dependencies.
- **Registration failure:** prove lifecycle phase and command, listener, service, or registry registration.
- **Behavior failure:** reduce to one command, event, scheduler callback, or persistence transition.
- **Compatibility failure:** reproduce on the exact claimed target and compare target Javadocs or mappings.
- **Interaction failure:** test required and optional plugins deliberately; use controlled removal or binary isolation when necessary.
- **Shutdown failure:** inspect queued work, owned threads, pools, closeables, and incomplete initialization.

Do not use server reload as a debugging shortcut. Restart with the actual built artifact so lifecycle and classloading evidence remain trustworthy.

## Completion evidence

Report the reproduction, root cause, supporting frame or state observation, changed artifact, and post-fix run. Separate confirmed causes from remaining hypotheses and retain the full validation result.

## Official sources

- [Debugging Paper plugins](https://docs.papermc.io/paper/dev/debugging/)
- [Reading stacktraces](https://docs.papermc.io/paper/dev/reading-stacktraces/)
- [Paper profiling](https://docs.papermc.io/paper/profiling/)
- [Paper basic troubleshooting](https://docs.papermc.io/paper/basic-troubleshooting/)
- [Paper project setup and run task](https://docs.papermc.io/paper/dev/project-setup/)
