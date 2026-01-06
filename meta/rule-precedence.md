# Rule Precedence

## Overview

This document defines the resolution hierarchy when skills provide contradictory advice or recommendations conflict.

## Precedence Hierarchy

### Level 1: Security (Highest Priority)

Security recommendations override all other considerations.

**Examples:**
- Security vulnerability fixes override performance optimizations
- Authentication requirements override UX convenience
- Data protection overrides feature speed

**Skills:** `dependency-health-check`, security-focused skills

### Level 2: Data Integrity

Protecting data correctness and preventing data loss.

**Examples:**
- Transaction safety overrides performance
- Backup requirements override storage costs
- Validation rules override user experience

### Level 3: Architecture & Design

Structural decisions that affect long-term maintainability.

**Examples:**
- Architectural patterns override quick fixes
- Design principles override immediate convenience
- Scalability concerns override short-term speed

**Skills:** `architecture-review`, design-focused skills

### Level 4: Performance

Performance optimizations and efficiency improvements.

**Examples:**
- Performance fixes override code style
- Efficiency gains override minor complexity
- Resource usage overrides convenience

### Level 5: Code Quality

Code maintainability, readability, and best practices.

**Examples:**
- Code quality improvements override style preferences
- Maintainability overrides personal preferences
- Best practices override shortcuts

**Skills:** `code-quality-audit`, code review skills

### Level 6: Documentation & Style (Lowest Priority)

Documentation, naming conventions, and style preferences.

**Examples:**
- Documentation improvements are lowest priority
- Style preferences can be overridden by all above levels
- Naming conventions are flexible

**Skills:** `documentation-generator`, style-focused skills

## Conflict Resolution Process

### Step 1: Identify Conflict Type

Determine which precedence levels are in conflict:
- Security vs. Performance → Security wins
- Architecture vs. Code Quality → Architecture wins
- Performance vs. Documentation → Performance wins

### Step 2: Check Context

Some conflicts may be valid tradeoffs:
- Document the tradeoff in handoff report
- Provide both options with context
- Let implementer decide based on project needs

### Step 3: Escalate if Needed

If conflict cannot be resolved:
- Flag for human review
- Provide both recommendations with full context
- Explain why automatic resolution isn't possible

## Special Cases

### User Experience vs. Security

**Resolution:** Security wins, but recommend UX improvements that maintain security.

**Example:**
- ❌ "Remove authentication for faster login"
- ✅ "Implement secure, fast authentication (e.g., OAuth with session caching)"

### Performance vs. Maintainability

**Resolution:** Context-dependent. Document tradeoff.

**Example:**
- For critical path: Performance may win
- For non-critical code: Maintainability wins
- Provide both options with impact analysis

### Breaking Changes vs. Technical Debt

**Resolution:** Depends on project phase and risk tolerance.

**Example:**
- Pre-1.0 projects: Breaking changes acceptable
- Production systems: Technical debt management preferred
- Document risk assessment

## Implementation in Skills

Skills should:
1. **Acknowledge conflicts explicitly**
   - "This recommendation conflicts with [other skill]'s recommendation"
   - "Per rule precedence, this takes priority because..."

2. **Document tradeoffs**
   - Explain why one recommendation overrides another
   - Provide alternative approaches when possible

3. **Reference this document**
   - "Per `meta/rule-precedence.md`, security recommendations override performance"

## Examples

### Example 1: Security Override

**Conflict:**
- `dependency-health-check`: "Update vulnerable dependency (may break API compatibility)"
- `architecture-review`: "Maintain current API for stability"

**Resolution:** Update dependency (Security > Architecture)
**Handoff Note:** "Security vulnerability requires immediate update. Plan API migration path."

### Example 2: Architecture Override

**Conflict:**
- `architecture-review`: "Refactor to microservices for scalability"
- `code-quality-audit`: "Current monolith is well-structured, no refactor needed"

**Resolution:** Consider refactoring (Architecture > Code Quality)
**Handoff Note:** "Architectural scalability concerns justify refactor despite good code quality."

### Example 3: Valid Tradeoff

**Conflict:**
- `performance-analyzer`: "Add caching layer (increases complexity)"
- `code-quality-audit`: "Reduce complexity, remove caching"

**Resolution:** Document tradeoff, provide both options
**Handoff Note:** "Performance vs. complexity tradeoff. Recommend caching for high-traffic endpoints only."

