# Skill Lifecycle

This document defines how skills earn or lose trust over time through explicit lifecycle stages.

## Core Principle

> **Skills are not static. They evolve based on real-world performance.**

The lifecycle model ensures:
- New skills are treated with appropriate caution
- Proven skills get routing priority
- Unused or ineffective skills fade naturally
- Retirement happens explicitly, not by accident

## Lifecycle Stages

```
experimental → validated → preferred → default → legacy → deprecated
     ↑                                              ↓
     └──────────────── (revival if needed) ────────┘
```

| Stage | Meaning | Router Weight | Typical Duration |
|-------|---------|---------------|------------------|
| **experimental** | New, untested | 0.7x | 2-4 weeks |
| **validated** | Works, available | 1.0x | Ongoing |
| **preferred** | Strong track record | 1.1x | Ongoing |
| **default** | First choice for domain | 1.2x | Ongoing |
| **legacy** | Superseded but functional | 0.5x | 1-3 months |
| **deprecated** | Scheduled for removal | 0.1x (warn) | 1 month max |

## Stage Definitions

### Experimental

**Meaning:** New skill, not yet proven in real use.

**Characteristics:**
- Created recently
- Limited usage data
- May have rough edges
- Not fully trusted

**Router Behavior:**
- Weight: 0.7x (deprioritized)
- Only selected if explicitly requested or best match
- Includes "experimental" warning in selection trace

**Transition Out:**
- → `validated`: After 3+ successful uses with >50% actionable rate
- → `deprecated`: If abandoned or fundamentally flawed

### Validated

**Meaning:** Proven to work, available for normal routing.

**Characteristics:**
- Has real usage data
- Known strengths and weaknesses
- Stable behavior
- Trusted for routine use

**Router Behavior:**
- Weight: 1.0x (baseline)
- Normal routing priority
- No special handling

**Transition Out:**
- → `preferred`: After 10+ uses with >70% actionable rate
- → `legacy`: If superseded by better skill
- → `deprecated`: If no use in 90+ days

### Preferred

**Meaning:** Strong track record, routing priority.

**Characteristics:**
- Consistently high-quality output
- Low false positive rate
- Used across multiple projects/contexts
- Refinement-layer rarely overrides

**Router Behavior:**
- Weight: 1.1x (boosted)
- Selected before validated skills for same domain
- Trusted for high-stakes analysis

**Transition Out:**
- → `default`: After 25+ uses with consistent performance
- → `validated`: If performance degrades
- → `legacy`: If superseded

### Default

**Meaning:** First choice for its domain, highest trust.

**Characteristics:**
- Go-to skill for its domain
- Extensive usage history
- No significant weaknesses
- Minimal refinement-layer overrides

**Router Behavior:**
- Weight: 1.2x (highest boost)
- Auto-selected for domain unless overridden
- Maximum routing priority

**Transition Out:**
- → `preferred`: If performance degrades
- → `legacy`: If superseded by significantly better skill

### Legacy

**Meaning:** Superseded but still functional, use discouraged.

**Characteristics:**
- Has been replaced by better skill
- Still works if needed
- Not actively maintained
- Scheduled for eventual deprecation

**Router Behavior:**
- Weight: 0.5x (deprioritized)
- Only selected if replacement unavailable
- Includes deprecation notice in selection trace

**Transition Out:**
- → `deprecated`: After 90 days with no use
- → `validated`: If revived and modernized (rare)

### Deprecated

**Meaning:** Scheduled for removal, should not be used.

**Characteristics:**
- No longer maintained
- May have known issues
- Replacement available
- Will be removed soon

**Router Behavior:**
- Weight: 0.1x (almost never selected)
- Emits warning if selected
- Suggests replacement skill

**Transition Out:**
- → Removed from system
- → `experimental` (if completely rewritten)

## Promotion Signals

### experimental → validated

**Criteria (ALL required):**
- [ ] 3+ successful uses
- [ ] Actionable rate > 50%
- [ ] No critical failures
- [ ] At least 2 weeks since creation

**Manual trigger:** Maintainer can promote after review

### validated → preferred

**Criteria (ALL required):**
- [ ] 10+ uses across 2+ projects
- [ ] Actionable rate > 70%
- [ ] Override rate < 15%
- [ ] No significant weaknesses identified

**Manual trigger:** Promotion review after sustained performance

### preferred → default

**Criteria (ALL required):**
- [ ] 25+ uses
- [ ] Consistent performance for 3+ months
- [ ] No better alternative for domain
- [ ] Maintainer approval

**Manual trigger:** Deliberate decision after review

## Demotion Signals

### Any → legacy

**Triggers (ANY):**
- Superseded by better skill (explicit)
- Not used in 90 days (automatic)
- Maintainer decision

### legacy → deprecated

**Triggers (ANY):**
- Not used in 90 days after legacy status
- Critical issues discovered
- Maintainer decision

### Performance-based demotion

**preferred → validated:**
- Actionable rate drops below 60%
- Override rate exceeds 25%

**validated → experimental:**
- Major issues discovered
- Needs fundamental rework

## Trust Score Calculation

Each skill maintains a trust score (0.0 - 1.0):

```
trust_score = (
    0.4 * actionable_rate +
    0.3 * (1 - false_positive_rate) +
    0.2 * (1 - override_rate) +
    0.1 * recency_factor
)
```

**Components:**
- `actionable_rate`: Findings that led to changes (0.0-1.0)
- `false_positive_rate`: Findings that were wrong (0.0-1.0)
- `override_rate`: How often Agent B overrides (0.0-1.0)
- `recency_factor`: Recent use bonus (0.0-1.0)

**Score Interpretation:**
- 0.8+ : Strong candidate for promotion
- 0.6-0.8 : Healthy skill
- 0.4-0.6 : Needs attention
- <0.4 : Candidate for demotion

## Router Weight Calculation

Final routing weight combines lifecycle stage and trust score:

```
routing_weight = lifecycle_weight * (0.5 + 0.5 * trust_score)
```

**Example:**
- Preferred skill (1.1x) with trust 0.8 → 1.1 * (0.5 + 0.4) = 0.99
- Experimental skill (0.7x) with trust 0.6 → 0.7 * (0.5 + 0.3) = 0.56

## Metadata Structure

Each skill's lifecycle data is stored in `meta/skill-trust-scores.yaml`:

```yaml
adversarial-ui-tester:
  lifecycle: preferred
  trust_score: 0.85
  last_updated: 2026-01-08
  
  # Usage metrics
  usage_count: 47
  last_used: 2026-01-07
  projects_used_in: 3
  
  # Performance metrics
  metrics:
    actionable_rate: 0.78
    false_positive_rate: 0.12
    override_rate: 0.08
  
  # Qualitative data
  strengths:
    - "Early flaw detection"
    - "Accessibility gaps"
  weaknesses:
    - "Over-flags on low-risk UI"
  
  # Pairing data
  pairs_well_with:
    - refinement-layer
    - ux-copy-neutrality-checker
  
  # History
  lifecycle_history:
    - stage: experimental
      date: 2025-11-01
    - stage: validated
      date: 2025-11-15
    - stage: preferred
      date: 2025-12-20
```

## Integration Points

### Skill Router

The skill-router uses lifecycle data to:
1. Weight skill candidates during selection
2. Apply trust score modifiers
3. Warn about legacy/deprecated skills

### Skill Effectiveness Analyzer

Updates lifecycle data by:
1. Tracking usage metrics
2. Calculating actionable rates
3. Proposing promotions/demotions

### Column Router

Uses lifecycle to:
1. Select default skills for risk tiers
2. Avoid experimental skills for critical changes
3. Prefer default skills for high-stakes analysis

## Maintenance

### Weekly Review

Check for:
- Skills with declining metrics
- Skills not used in 30+ days
- Promotion candidates (high performers)

### Monthly Review

Check for:
- Lifecycle transitions needed
- Deprecated skills to remove
- New skills to evaluate

### Quarterly Review

Check for:
- Overall skill library health
- Redundant skills to merge
- Domain coverage gaps

## Anti-Patterns

### Don't Do This

- **Auto-deprecating without review:** Always human-verify deprecation
- **Promoting too fast:** Let skills prove themselves
- **Ignoring metrics:** Trust scores exist for a reason
- **Keeping zombies:** Remove deprecated skills promptly

### Do This Instead

- **Gradual promotion:** experimental → validated → preferred → default
- **Evidence-based demotion:** Use metrics, not feelings
- **Explicit replacement:** When deprecating, name the replacement
- **Regular pruning:** Keep the library focused

## See Also

- `meta/skill-trust-scores.yaml` - Skill lifecycle data
- `skills/meta/skill-router.md` - Uses lifecycle for routing
- `skills/meta/skill-effectiveness-analyzer.md` - Updates metrics
- `meta/promotion-criteria.md` - Detailed promotion rules

