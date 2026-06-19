# SQLite Database Skill

## Purpose

Define telemetry storage schema and establish a reliable SQLite workflow for satellite data.

## Schema for Telemetry

```sql
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    packet_id INTEGER,
    latitude REAL,
    longitude REAL,
    battery_level REAL,
    temperature REAL,
    signal_strength REAL
);
```

## Workflow

1. **Open or create the database**
   - Use `sqlite3.connect(path, timeout=30)`
   - Create tables if they do not exist

2. **Use transactions for inserts**
   - Wrap inserts in `BEGIN` / `COMMIT`
   - Roll back on failure

3. **Prepare statements**
   - Use parameterized SQL to avoid injection
   - Keep schema aligned with telemetry object fields

4. **Validate telemetry before insert**
   - Confirm timestamp and numeric fields are present
   - Ensure latitude and longitude are in valid ranges
   - Log invalid records instead of storing them

5. **Query efficiently**
   - Use indexed timestamp fields for time-range queries
   - Filter by packet_id, signal_strength, or anomaly markers

6. **Backup and retention**
   - Copy the database file periodically if configured
   - Remove old data based on retention policy if needed

## Decision Points

- Use SQLite when the telemetry volume is moderate and local storage is sufficient
- Use a file-based schema for portability and ease of deployment
- Add indices for time-based queries and anomaly analysis
- Use JSON or structured columns only if schema flexibility is required

## Quality Checks

- Confirm table creation SQL matches code structures
- Ensure inserts use typed values, not raw strings
- Validate error handling around `sqlite3.DatabaseError`
- Log failures to write telemetry and retry if possible

## Outcome

A clear SQLite telemetry storage skill that defines schema, insertion best practices, validation, and retention handling for ground station data.
