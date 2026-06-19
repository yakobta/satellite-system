# Project Instructions for ETRSS-1 Ground Station

## Code Standards
- Use Python 3.12+ syntax
- Add type hints to all function parameters and return values
- Include docstrings for all public functions, classes, and modules
- Use f-strings for string formatting
- Follow PEP 8 naming conventions and formatting

## Error Handling
- Always use try/except for file operations and network I/O
- Log errors with `logger.error()` and include context
- Never use bare `except:` blocks
- Gracefully handle `KeyboardInterrupt` for clean shutdown

## Satellite-Specific
- Use ETRSS-1 real parameters (NORAD 44880)
- Ground station at Entoto Observatory: 9.03°N, 38.74°E
- UDP port `5005` for telemetry reception
- Store all telemetry and health data in SQLite

## Commits
- Use emojis in commit messages:
  - `🚀` for features
  - `🐛` for fixes
- Write descriptive commit messages
- Keep commits focused and small
