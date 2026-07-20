# Plugin Messaging and Services

## Load this reference when

Use this file for custom payloads through clients/proxies or interoperability through Bukkit's service registry. These solve different problems: messaging transports bytes over a player connection; services expose an in-process provider interface.

## Plugin messaging decisions

- Register incoming and outgoing namespaced channels during plugin initialization and unregister owned channels during shutdown.
- Define an explicit binary protocol: version, field order/types, maximum lengths, and invalid-message behavior.
- Treat every incoming byte as untrusted. Validate channel, subchannel, size, count, identifiers, and permissions before mutation.
- Copy and parse bounded data promptly. Perform external I/O asynchronously, then return to the correct owner before accessing game state.
- Remember that plugin messages piggyback on a connected player. With no suitable player, there is no delivery path; this is not a durable server-to-server bus.
- Add acknowledgement, retry, or a different transport when delivery matters.
- Preserve the documented special `BungeeCord` channel mapping when interoperating with that proxy protocol.

Client or proxy support must agree on the channel and payload. A server plugin cannot make an unmodified client understand a custom protocol.

## ServicesManager decisions

- Put the shared interface in the established compile-only API boundary.
- Register a provider with its owning plugin and priority.
- Call `load` once and handle null; do not call `isProvidedFor` followed by `load`, because availability can change between calls.
- Match required/optional provider behavior in the plugin descriptor.
- Release acquired references and owned resources on disable. Do not reach through another plugin's classloader or internals when a supported service/API exists.

## Traps

- Sending before channel registration or without an eligible player.
- Trusting lengths or identities from a proxy/client payload.
- Doing database or network work in the message callback.
- Assuming delivery, ordering, durability, or client support not defined by the protocol.
- Bundling another plugin's API or treating an optional service as non-null.

## Required evidence

Test valid, malformed, oversized, unauthorized, version-mismatched, no-player, disconnect, proxy/client present/absent, provider present/absent, priority selection, disable, and restart paths.

## Official sources

- [Plugin messaging](https://docs.papermc.io/paper/dev/plugin-messaging/)
- [Messenger Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/messaging/Messenger.html)
- [ServicesManager Javadocs](https://jd.papermc.io/paper/org/bukkit/plugin/ServicesManager.html)

