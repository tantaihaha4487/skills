# Recipes and Particles

## Load this reference when

Use this file for server recipe registration/discovery or client-rendered particle effects. Keep authoritative game behavior separate from presentation.

## Recipe decisions

- Give every plugin recipe a stable plugin `NamespacedKey`.
- Select the typed recipe and ingredient-choice semantics required by the exact target.
- Check the result of registration and make repeated registration idempotent.
- Treat recipe availability and recipe-book discovery as separate state. When adding recipes after players join, use the supported update/discovery path and test client synchronization.
- Register and remove recipes on the correct server owner. Never call global `clearRecipes` or `resetRecipes` from a normal feature.
- Use exact choices only when metadata must match; material/item-type choices have broader semantics and have evolved across versions.

## Particle decisions

- Prefer `ParticleBuilder` for readable receiver, location, count, offset, data, and visibility configuration.
- Bound receiver set/radius, count, and frequency; particles consume packets and client render work.
- Check the target's required data type and the special semantics of `count == 0`, offsets, and `extra`.
- Use forced visibility sparingly because it extends range and bypasses normal client particle settings.
- Confine a mutable builder to one task/context. An async-safe `spawn` method does not make concurrent builder mutation safe.
- Treat particles as presentation only; never use client visibility as server authority or collision state.

## Traps

- Assuming registration automatically discovers a recipe for every online player.
- Removing recipes without considering player discovery state.
- Reusing a recipe key across incompatible meanings without migration.
- Broadcasting high-rate particles globally.
- Assuming every client renders the effect identically.

## Required evidence

For recipes, test registration result, craft match/non-match, discovery, late registration, removal, and restart. For particles, test exact data, receiver scope, count-zero behavior, distance/settings, packet/load impact, and task cancellation.

## Official sources

- [Recipes](https://docs.papermc.io/paper/dev/recipes/)
- [Particles](https://docs.papermc.io/paper/dev/particles/)
- [ParticleBuilder Javadocs](https://jd.papermc.io/paper/com/destroystokyo/paper/ParticleBuilder.html)

