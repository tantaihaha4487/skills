# Database usage

## Scope

Use this reference when plugin data exceeds simple configuration or flat-file needs. Preserve an
existing repository's storage abstraction, schema conventions, and migration mechanism.

## Choose storage from workload

- Keep small operator-edited settings in configuration, not a database.
- Consider a file database such as SQLite for smaller single-server datasets and simple operation.
- Consider a standalone SQL service when data size, concurrent access, multiple server instances,
  operations, or scalability justify the deployment cost.
- Decide SQL versus another model from query and consistency requirements, not trend or habit.

Paper's database guide notes that its SQLite JDBC driver is bundled and that HikariCP is not.
Treat bundled libraries as target-version-sensitive: verify the selected Paper documentation and
runtime before omitting a dependency. If a library is not supplied, follow the repository's
established library-loader or shading/relocation strategy; never copy a version from an example.

## Use a split-phase data path

1. On the valid game-state owner, capture immutable identifiers and values.
2. Submit acquisition and SQL work to a bounded database executor or configured connection pool.
3. Apply timeouts and return connections, statements, and result sets with try-with-resources.
4. Map rows to immutable DTOs before leaving the data layer.
5. Return to the entity/region/global owner, re-resolve targets, and reject stale results.

Never execute connection setup, migrations, queries, writes, retries, or pool waits on a tick or
region thread. Never block that thread on a future. Make saturation and database-unavailable
behavior explicit: bounded queue, failure message, retry policy, or feature disablement.

## Integrity and lifecycle

- Use prepared statements for all values; do not concatenate player or operator input into SQL.
- Keep credentials out of logs and source control, following existing secret/config conventions.
- Version schemas. Make migrations ordered, transactional where supported, and safe to resume or
  fail without falsely advancing the schema version.
- Define transaction boundaries around domain invariants, not individual helper calls.
- Reject new work during disable, stop producers, allow only bounded completion, then close the
  datasource/pool and executor. Report close failures through the plugin logger.

## Hazards to reject

- A global long-lived raw `Connection` with no reconnect or ownership policy.
- One connection per event, or an unbounded pool/executor that moves lag into the database.
- SQL string concatenation, leaked JDBC resources, swallowed exceptions, or infinite retries.
- Applying a late query result to a player/entity that left, moved owner, or changed state.
- Destructive or non-idempotent schema changes without a tested backup/upgrade path.

## Validation evidence

- Test empty creation, existing schema, each supported upgrade path, restart, and partial failure.
- Test unavailable database, acquisition/query timeout, pool exhaustion, malformed credentials,
  disable during work, and recovery behavior.
- Verify prepared statements and try-with-resources at every JDBC boundary.
- Confirm gameplay callbacks remain responsive and no pool/executor thread survives shutdown.

## Official sources

- [Using databases](https://docs.papermc.io/paper/dev/using-databases/)
- [Plugin lifecycle](https://docs.papermc.io/paper/dev/how-do-plugins-work/)
- [Scheduling and blocking-I/O guidance](https://docs.papermc.io/paper/dev/scheduler/)
