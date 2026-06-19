# UDP Telemetry Skill

## Purpose

Handle real-time satellite telemetry reception and processing over UDP.

## Inputs

- UDP host: `0.0.0.0`
- UDP port: `5005`
- Buffer size: `65536` bytes
- Telemetry format: JSON payload per packet

## Workflow

1. **Create UDP socket**
   - Use `socket.socket(socket.AF_INET, socket.SOCK_DGRAM)`
   - Bind to `("0.0.0.0", 5005)` to listen on all interfaces
   - Configure socket buffer size and timeout as needed

2. **Receive telemetry packets**
   - Use `sock.recvfrom(65536)` to receive up to 65 KB per packet
   - Handle `socket.timeout` gracefully for intermittent data
   - Log packet receipt and source address

3. **Decode packet payload**
   - Decode bytes to string with `data.decode()`
   - Parse JSON with `json.loads()`
   - Validate expected telemetry fields and types

4. **Validate telemetry data**
   - Check required keys such as `satellite_id`, `timestamp`, `battery`, `position`
   - Ensure numeric values are within reasonable ranges
   - Reject malformed or corrupted packets with warnings

5. **Process and store telemetry**
   - Convert telemetry into structured objects
   - Detect anomalies before database insertion
   - Store valid telemetry records in the database

6. **Handle errors and retries**
   - Catch `socket.error`, `ValueError`, and JSON decode errors
   - Log errors with context, but continue listening
   - Avoid crashing on a single bad packet

## Code Pattern

```python
import socket
import json
import logging

logger = logging.getLogger(__name__)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))

while True:
    try:
        data, addr = sock.recvfrom(65536)
        logger.debug(f"Received {len(data)} bytes from {addr}")
        telemetry = json.loads(data.decode())
        # Validate and process telemetry here
    except socket.timeout:
        logger.debug("UDP receive timeout, waiting for next packet")
        continue
    except (ValueError, json.JSONDecodeError) as exc:
        logger.warning(f"Invalid telemetry packet from {addr}: {exc}")
        continue
    except socket.error as exc:
        logger.error(f"UDP socket error: {exc}")
        break
```

## Decision Points

- Use UDP for low-latency telemetry in real time
- Use JSON decoding when the payload is textual
- Add binary parsing if telemetry format changes
- Apply validation before any database write

## Quality Checks

- Confirm socket binds successfully on the expected port
- Ensure `recvfrom` uses a sufficient buffer size
- Validate packet payloads before deserialization
- Log warnings for malformed telemetry, not failures
- Keep the receive loop resilient to temporary network issues

## Outcome

A reusable UDP telemetry workflow that receives real-time satellite telemetry, validates payloads, handles network errors gracefully, and prepares data for processing or storage.
