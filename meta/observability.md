# Observability

## Overview

This document defines the execution logging format and privacy policy for agent skill observability.

## Purpose

Execution logging enables:
- Understanding which skills are actually being used
- Identifying skills that fail most often
- Validating typical-runtime estimates
- Data-driven decisions about skill improvement and retirement
- Identifying effective skill chains

## Privacy Policy

### What We Log

**Execution Metadata (Safe to Log):**
- Skill name and version
- Timestamp of execution
- Success/failure status
- Runtime duration (seconds)
- Error type/category (if failed)
- Execution mode used (full/incremental/targeted)
- Skill chain identifier (if part of a chain)

### What We Never Log

**Sensitive Data (Never Logged):**
- ❌ Code content
- ❌ File paths or directory structures
- ❌ Project names or identifiers
- ❌ User information
- ❌ API keys or secrets
- ❌ Handoff report content
- ❌ Specific findings or recommendations

### Privacy Guarantee

Logs contain **zero project-specific or code-specific information**. They are purely metadata about skill execution.

## Log Format

### JSON Structure

```json
{
  "timestamp": "2024-01-05T14:23:45Z",
  "skill": {
    "name": "architecture-review",
    "version": "1.2.0",
    "category": "architecture"
  },
  "execution": {
    "mode": "full-scan",
    "duration_seconds": 127,
    "status": "success",
    "chain_id": "full-codebase-audit-v1"
  },
  "error": null
}
```

### Error Log Format

```json
{
  "timestamp": "2024-01-05T14:23:45Z",
  "skill": {
    "name": "dependency-health-check",
    "version": "1.0.0",
    "category": "security"
  },
  "execution": {
    "mode": "incremental",
    "duration_seconds": 5,
    "status": "failure",
    "chain_id": null
  },
  "error": {
    "type": "prerequisite_missing",
    "message": "Required file package.json not found",
    "category": "configuration_error"
  }
}
```

### Log File Naming

Logs are stored in `.skill-usage/` directory:

```
.skill-usage/
├── 2024-01-05.jsonl    # One line per execution
├── 2024-01-06.jsonl
└── README.md
```

Format: `YYYY-MM-DD.jsonl` (JSON Lines format, one execution per line)

## Opt-In Mechanism

### Default: Disabled

Logging is **disabled by default**. Users must explicitly enable it.

### Enable Logging

**Environment Variable:**
```bash
export AGENT_SKILLS_LOGGING=true
```

**Warp Agent Configuration:**
```yaml
environment:
  AGENT_SKILLS_LOGGING: "true"
```

**Check in Skill:**
Skills should check for this environment variable before logging.

## Error Categories

Standard error categories for consistent tracking:

- `prerequisite_missing`: Required skill or file not found
- `timeout`: Execution exceeded maximum time
- `context_limit`: Hit token/context limits
- `validation_error`: Handoff report failed validation
- `execution_error`: General execution failure
- `configuration_error`: Invalid configuration or settings

## Usage Analytics

### Metrics to Track

1. **Usage Frequency**
   - Which skills are used most/least
   - Trends over time
   - Seasonal patterns

2. **Success Rates**
   - Overall success rate per skill
   - Failure rate trends
   - Error type distribution

3. **Performance**
   - Average runtime vs. estimated runtime
   - Runtime distribution
   - Performance regressions

4. **Skill Chains**
   - Most common chain combinations
   - Chain success rates
   - Effective patterns

## Implementation Notes

### For Skill Authors

Skills should log execution metadata when `AGENT_SKILLS_LOGGING=true`:

```python
# Pseudo-code example
if os.getenv('AGENT_SKILLS_LOGGING') == 'true':
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "skill": {"name": "skill-name", "version": "1.0.0"},
        "execution": {
            "mode": execution_mode,
            "duration_seconds": elapsed_time,
            "status": "success" if success else "failure"
        }
    }
    append_to_log(log_entry)
```

### Log Rotation

- Daily log files (one file per day)
- Compress logs older than 30 days
- Archive logs older than 1 year

## Data Retention

- **Active logs**: 30 days (uncompressed)
- **Archived logs**: 1 year (compressed)
- **Aggregated analytics**: Indefinite (anonymized)

## Access Control

- Logs are local to the project (`.skill-usage/` is git-ignored)
- Users control their own logging
- No remote transmission of logs
- Users can delete logs at any time

## Benefits

This observability framework enables:

1. **Skill Improvement**
   - Identify skills with high failure rates
   - Find performance bottlenecks
   - Discover common error patterns

2. **Retirement Decisions**
   - Identify unused skills (candidates for retirement)
   - Track skill usage trends
   - Data-driven deprecation

3. **Validation**
   - Validate estimated runtimes
   - Verify skill prerequisites
   - Test skill chains

4. **Documentation**
   - Real-world usage data
   - Actual performance metrics
   - Common patterns

