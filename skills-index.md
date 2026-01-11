# Skills Index

Comprehensive index of all agent skills, organized by scope and tier.

## Core Skills (Universal)

Universal skills that work on any project.

### Tier 1: Existential Risk
*None currently - Tier 1 skills are typically project-specific*

### Tier 2: System Health

#### dependency-health-check
- **Purpose:** Scans dependencies for vulnerabilities and outdated packages
- **Scope:** core
- **Tier:** 2
- **Category:** security
- **When to invoke:** Before deployments, regularly (weekly/monthly)
- **When NOT to invoke:** For code quality issues (use code-quality-audit)
- **Maturity:** validated
- **Cost:** Low
- **Runtime:** 2-5min

#### architectural-drift-detector
- **Purpose:** Identifies when new code violates established patterns
- **Scope:** core
- **Tier:** 2
- **Category:** architecture
- **When to invoke:** Before major refactoring, when code quality degrades
- **When NOT to invoke:** For initial project setup (use project-structure-analyzer first)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 5-10min

#### adversarial-ui-tester
- **Purpose:** Tests UI from user perspective, finds UX issues
- **Scope:** core
- **Tier:** 2
- **Category:** testing
- **When to invoke:** Before releases, when UX concerns arise
- **When NOT to invoke:** For code quality issues (use code-quality-audit)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 5-15min

### Tier 3: Long-term Quality

#### test-coverage-gap-finder
- **Purpose:** Identifies critical code paths without test coverage
- **Scope:** core
- **Tier:** 3
- **Category:** testing
- **When to invoke:** Before releases, during quality audits
- **When NOT to invoke:** For test execution (use test runner)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 5-10min

#### bundle-size-analyzer
- **Purpose:** Identifies heavy dependencies and proposes tree-shaking opportunities
- **Scope:** core
- **Tier:** 3
- **Category:** performance
- **When to use:** When bundle size is a concern, before releases
- **When NOT to use:** For runtime performance (use performance-budget-guardian)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 3-7min

#### api-boundary-validator
- **Purpose:** Ensures no unintended external API calls (preserves local-first principle)
- **Scope:** core
- **Tier:** 3
- **Category:** api
- **When to invoke:** Before production deployments, when local-first principle is violated
- **When NOT to invoke:** For general security (use dependency-health-check)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### project-structure-analyzer
- **Purpose:** Maps codebase structure, creates dependency graphs
- **Scope:** core
- **Tier:** 3
- **Category:** analysis
- **When to invoke:** First time on project, before architecture-review
- **When NOT to invoke:** For code quality (use code-quality-audit)
- **Maturity:** validated
- **Cost:** Low
- **Runtime:** 1-3min

#### architecture-review
- **Purpose:** Reviews codebase architecture, identifies design patterns, detects issues
- **Scope:** core
- **Tier:** 3
- **Category:** architecture
- **When to invoke:** Before major refactoring, after project-structure-analyzer
- **When NOT to invoke:** For initial project setup, on every commit
- **Maturity:** validated
- **Cost:** Medium
- **Runtime:** 5-10min

#### failure-mode-simulator
- **Purpose:** Simulates stress-test failure modes and validates countermeasures
- **Scope:** core
- **Tier:** 3
- **Category:** failure-modes
- **When to invoke:** Periodically, before releases
- **When NOT to invoke:** For individual bug testing (use test runner)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 10-20min

#### ux-copy-neutrality-checker
- **Purpose:** Scans all UI text for prescriptive, judgmental, or celebratory language
- **Scope:** core
- **Tier:** 3
- **Category:** ux
- **When to invoke:** Before releases, during UX audits
- **When NOT to invoke:** For code quality (use code-quality-audit)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### documentation-drift-detector
- **Purpose:** Identifies when documentation has diverged from the reality it describes
- **Scope:** core
- **Tier:** 3
- **Category:** analysis
- **Tags:** documentation, drift, consistency, semantic, cross-surface
- **When to invoke:** After code changes, before releases, during documentation audits
- **When NOT to invoke:** When documentation doesn't exist yet (use documentation-generator)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 3-7min
- **Drift Types:** structural, behavioral, temporal, semantic

## Domain Skills (Technology-Specific)

Domain-specific skills organized by technology.

### React Apps
*None currently - domain skills will be added as patterns emerge*

## Project-Specific Skills (Prompt Library)

Skills specific to the Prompt Library project. These live in `.agent-skills/skills/project/` and are not part of the universal repo.

### Tier 1: Existential Risk

#### philosophy-compliance-enforcer
- **Purpose:** Validates features don't violate app's core philosophical invariants
- **Scope:** project
- **Tier:** 1
- **Category:** philosophy
- **When to invoke:** Before implementing new features, during code review
- **When NOT to invoke:** For code quality (use code-quality-audit)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### privacy-tier-auditor
- **Purpose:** Ensures Privacy Absolutism is enforced at every data access point
- **Scope:** project
- **Tier:** 1
- **Category:** security
- **When to invoke:** Before deployments, when adding new features
- **When NOT to invoke:** For general security (use dependency-health-check)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### performance-budget-guardian
- **Purpose:** Enforces TTI <300ms and identifies performance regressions
- **Scope:** project
- **Tier:** 1
- **Category:** performance
- **When to invoke:** Before deployments, when performance concerns arise
- **When NOT to invoke:** For bundle size (use bundle-size-analyzer)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### state-invariant-validator
- **Purpose:** Ensures state transitions follow defined rules
- **Scope:** project
- **Tier:** 1
- **Category:** state
- **When to invoke:** Before adding new state transitions, when modifying state logic
- **When NOT to invoke:** For general state management (use architecture-review)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### capture-surface-focus-auditor
- **Purpose:** Validates capture surface auto-focuses and stays focused
- **Scope:** project
- **Tier:** 1
- **Category:** performance
- **When to invoke:** Before deployments, when focus issues occur
- **When NOT to invoke:** For general performance (use performance-budget-guardian)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

### Tier 2: System Health

#### database-migration-safety-checker
- **Purpose:** Reviews Dexie schema migrations for backwards compatibility
- **Scope:** project
- **Tier:** 2
- **Category:** database
- **When to invoke:** Before running migrations, when modifying schema
- **When NOT to invoke:** For general database design (use architecture-review)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### rac-accuracy-evaluator
- **Purpose:** Tests RAC completion quality (precision/recall of suggestions)
- **Scope:** project
- **Tier:** 2
- **Category:** rac
- **When to invoke:** Periodically, when RAC quality concerns arise
- **When NOT to invoke:** For general testing (use test-coverage-gap-finder)
- **Maturity:** draft
- **Cost:** Medium
- **Runtime:** 5-10min

#### variant-tree-explosion-detector
- **Purpose:** Identifies prompts with pathological variant counts
- **Scope:** project
- **Tier:** 2
- **Category:** variants
- **When to invoke:** Periodically, when performance degrades
- **When NOT to invoke:** For general performance (use performance-budget-guardian)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

#### toast-notification-spam-detector
- **Purpose:** Ensures toast notifications are sparse and opt-in
- **Scope:** project
- **Tier:** 2
- **Category:** notifications
- **When to invoke:** Before releases, when notification concerns arise
- **When NOT to invoke:** For general UX (use ux-copy-neutrality-checker)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

## Meta Skills

Skills for managing and validating the skill system itself.

### skill-effectiveness-analyzer
- **Purpose:** Validates that skills are actually useful, tracks usage, proposes improvements
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** Periodically (monthly/quarterly), when skill usage is low
- **When NOT to invoke:** For skill definition validation (use skill-health-check)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min

### skill-health-check
- **Purpose:** Validates skill definition quality and structure
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** Before committing skills, when creating new skills
- **When NOT to invoke:** For skill effectiveness (use skill-effectiveness-analyzer)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 1-2min

### handoff-quality-validator
- **Purpose:** Validates handoff reports meet protocol requirements
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** After any skill execution, to validate output
- **When NOT to invoke:** For skill definition validation (use skill-health-check)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 1-2min

### skill-map-validator
- **Purpose:** Validates skill maps reference existing skills
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** After creating/modifying skill-map.yaml, before deploying workflows
- **When NOT to invoke:** For skill definition validation (use skill-health-check)
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 1-3min

### skill-router
- **Purpose:** Resolves user intent to the most appropriate skill
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** When using intent-based skill resolution (Mode B)
- **When NOT to invoke:** When you know exactly which skill to use (Mode A)
- **Maturity:** hardened
- **Cost:** Low
- **Runtime:** <1min

### skill-gap-detector
- **Purpose:** Proposes new skills or refinements when routing fails
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **When to invoke:** When skill-router fails to match, when existing skills are inadequate
- **When NOT to invoke:** For normal skill execution
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 1-3min

### refinement-layer
- **Purpose:** Agent B meta-skill for 2-agent column pattern - compresses and validates output
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, refinement, compression, validation, signal-processing, column-pattern
- **When to invoke:** As Agent B in a column pattern after Agent A produces raw output
- **When NOT to invoke:** For single-skill execution, as Agent A
- **Maturity:** stable
- **Cost:** Low
- **Runtime:** 2-5min
- **Modes:** generic, domain-aware, effectiveness

### column-router
- **Purpose:** Decides how much cognitive scrutiny a change deserves before running agents
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, governance, attention, risk-assessment, column-planning
- **When to invoke:** Before starting any integration task, to plan appropriate analysis depth
- **When NOT to invoke:** When you already know exactly what analysis is needed
- **Maturity:** experimental
- **Cost:** Low
- **Runtime:** 1-2min
- **Outputs:** Column plan with risk tier, recommended columns, refinement strictness

### strategic-governor
- **Purpose:** Prevents over-analysis and under-analysis based on risk tier and findings
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, governance, throttle, escalate, attention, oversight
- **When to invoke:** After column-router (validate), after each column (monitor), before synthesis (final)
- **When NOT to invoke:** For trivial changes, when manually overriding analysis depth
- **Maturity:** experimental
- **Cost:** Low
- **Runtime:** <1min
- **Actions:** approve, throttle, escalate, halt

### readiness-certifier
- **Purpose:** Produces canonical "ship/no-ship" readiness certificates with evidence and confidence scores
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, certification, readiness, ship-decision, governance, production
- **When to invoke:** Before releases, after completing skill chains, when making ship decisions
- **When NOT to invoke:** When analysis is still in progress, for trivial changes
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min
- **Verdicts:** READY, CONDITIONAL, BLOCKED

### health-assessor
- **Purpose:** Autonomously assesses project health and identifies areas needing attention without being told what to look for
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, health, autonomous, intentless, triage, assessment, attention
- **When to invoke:** Starting work sessions, when unsure where to focus, for general health checks
- **When NOT to invoke:** When you know exactly what to analyze, when running predefined skill chains
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 2-5min
- **Modes:** intentless, surface-focused, change-triggered

### change-amplification-detector
- **Purpose:** Detects when small changes have disproportionate downstream impact (high-leverage changes)
- **Scope:** meta
- **Tier:** meta
- **Category:** meta
- **Tags:** meta, change-impact, amplification, risk-detection, governance, cascade
- **When to invoke:** Before modifying governance files, templates, or protocols
- **When NOT to invoke:** For isolated changes, documentation-only changes
- **Maturity:** draft
- **Cost:** Low
- **Runtime:** 1-3min
- **Modes:** change-analysis, pre-change

## Quick Reference

### By Tier
- **Tier 1:** philosophy-compliance-enforcer, privacy-tier-auditor, performance-budget-guardian, state-invariant-validator, capture-surface-focus-auditor
- **Tier 2:** dependency-health-check, architectural-drift-detector, adversarial-ui-tester, database-migration-safety-checker, rac-accuracy-evaluator, variant-tree-explosion-detector, toast-notification-spam-detector, change-amplification-detector
- **Tier 3:** test-coverage-gap-finder, bundle-size-analyzer, api-boundary-validator, project-structure-analyzer, architecture-review, failure-mode-simulator, ux-copy-neutrality-checker, documentation-drift-detector
- **Meta:** skill-effectiveness-analyzer, skill-health-check, handoff-quality-validator, skill-map-validator, skill-router, skill-gap-detector, refinement-layer, column-router, strategic-governor, readiness-certifier, health-assessor, change-amplification-detector

### By Scope
- **Core:** All universal skills (11 skills, including documentation-drift-detector)
- **Domain:** Technology-specific skills (0 currently)
- **Project:** Prompt Library-specific skills (9 skills)
- **Meta:** Skill management and governance skills (12 skills)

### By Function
- **Routing:** skill-router, column-router
- **Governance:** strategic-governor, readiness-certifier
- **Validation:** skill-health-check, handoff-quality-validator, skill-map-validator
- **Analysis:** skill-effectiveness-analyzer, skill-gap-detector, documentation-drift-detector
- **Column Pattern:** refinement-layer
- **Autonomous Attention:** health-assessor, change-amplification-detector, readiness-certifier

## See Also

- `SKILL-SELECTOR.md` - Decision tree for choosing skills
- `meta/skill-scope-policy.md` - Scope classification and promotion paths
- `docs/agent-invocation-guide.md` - How to use skills
- `TEMPLATE.md` - Creating new skills

