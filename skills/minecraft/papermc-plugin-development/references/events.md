# Events

Use this reference after locating listener registration, lifecycle ownership, and the target event's Javadocs.

## Use when

- Add, alter, cancel, emit, or dynamically register an event.
- Handle chat or another event that may fire asynchronously.

## Prefer

- Register `Listener` instances during enable through `PluginManager` unless repository lifecycle abstractions say otherwise.
- Select priority deliberately: later priorities observe mutations made by earlier handlers.
- Use `MONITOR` only for observation, never mutation.
- Use `ignoreCancelled` only when cancelled events truly require no handling.
- Re-read mutable event properties after dispatch because another plugin may change them.
- Give custom events a shared static `HandlerList`, instance `getHandlers()`, and static `getHandlerList()`.
- Prefer `AsyncChatEvent` with `ChatRenderer`; use viewer-unaware rendering when every viewer receives identical output.

## Avoid and pitfalls

- Do not assume cancellation stops remaining listeners.
- Do not mutate at `MONITOR` or overwrite another plugin's result without an explicit interoperability policy.
- Do not keep slow I/O, expensive allocation, or unbounded iteration in a tick-thread handler.
- Do not call world or entity APIs from asynchronous chat handling.
- Do not assume all instances of an event are synchronous; inspect its Javadocs and `isAsynchronous()`.
- Do not dynamically unregister handlers as ordinary control flow; tie it to an owned lifecycle.

## Thread, client, and version boundary

- A handler executes on the event's firing thread. Apply the shared threading/Folia policy before touching game state.
- Asynchronous events may run concurrently and out of order.
- Chat delivery waits for async listeners even though the server tick thread is not blocked.
- Adventure chat renderers replace legacy string-formatting patterns; confirm availability on the target API.

## Validation evidence

- Prove priority and cancellation behavior with the relevant event state, not only listener invocation.
- Test synchronous and asynchronous paths where the event supports both.
- Confirm listeners register once and owned dynamic handlers unregister during teardown.
- For custom events, test cancellation return values and mutations made by another listener.

## Official sources

- [Event listeners](https://docs.papermc.io/paper/dev/event-listeners/)
- [Custom events](https://docs.papermc.io/paper/dev/custom-events/)
- [Handler lists](https://docs.papermc.io/paper/dev/handler-lists/)
- [Chat events](https://docs.papermc.io/paper/dev/chat-events/)
- [`Event` Javadocs (current index; select the repository target)](https://jd.papermc.io/paper/org/bukkit/event/Event.html)
