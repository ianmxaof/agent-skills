---
name: ux-copy-neutrality-checker
category: ux
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - ux
  - copy
  - language
  - neutrality
  - text
  - user-friendly
  - errors
  - messages
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# UX Copy Neutrality Checker

## Purpose

Scans all UI text for prescriptive, judgmental, or celebratory language. Ensures observational language only, per philosophy requirements.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `3` - Long-term quality (language neutrality validation)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run ux-copy-neutrality-checker on [components/codebase]"
- "Check UI copy for neutrality"
- "Validate language neutrality"
- "Scan for prescriptive language"

### Situational Triggers

- Before releases
- After adding new UI copy
- When language concerns arise
- During UX review
- When philosophy violations suspected

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Extract all strings from React components
- Identify prescriptive patterns (`should`, `must`, `need to`)
- Identify celebration patterns (`Great!`, `Awesome!`, `You're improving!`)
- Identify judgment patterns (`best`, `better`, `optimal`)
- Propose neutral alternatives
- Consider context and intent

### What It Must Avoid

- Don't flag legitimate error messages
- Don't ignore context (some language may be acceptable)
- Don't suggest removing necessary information
- Don't assume all patterns are violations

### What It Must Prioritize

- Prescriptive language (High - violates neutrality)
- Celebration language (Medium - violates neutrality)
- Judgment language (Medium - violates neutrality)
- Observational alternatives (Low - suggestions)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive copy audit
- Before major release
- Initial language review

**Input:**
- All UI components
- Text strings
- Copy files

**Process:**
1. Extract all UI strings
2. Scan for prescriptive patterns
3. Identify celebration language
4. Find judgment patterns
5. Propose neutral alternatives
6. Generate comprehensive neutrality report

**Invocation Example:**
> "Run ux-copy-neutrality-checker in full-scan mode on all UI components"

### Incremental Mode

**When to Use:**
- After adding new copy
- When modifying UI text
- During feature development

**Input:**
- Changed UI components
- New text strings

**Process:**
1. Analyze new copy for violations
2. Check if neutrality is maintained
3. Verify language patterns
4. Report on neutrality status

**Invocation Example:**
> "Run ux-copy-neutrality-checker in incremental mode on new UI copy"

### Targeted Mode

**When to Use:**
- Reviewing specific component
- Validating single text string
- Focused neutrality check

**Input:**
- Specific component
- Targeted text string

**Process:**
1. Deep analysis of target copy
2. Check all neutrality aspects
3. Verify language patterns
4. Provide focused recommendations

**Invocation Example:**
> "Run ux-copy-neutrality-checker in targeted mode on CompletionWorkshop component"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General UX Issues**
- **Instead:** Use adversarial-ui-tester for broader UX concerns
- **Why:** This skill focuses specifically on language neutrality, not general UX.

**Anti-Pattern 2: Code Quality**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill validates copy language, not code quality.

### ⚠️ WARNING: Known Limitations

**Limitation:** May flag false positives for legitimate error messages
- **Mitigation:** Review context carefully. Error messages may need prescriptive language.
- **Confidence:** ~90% accuracy on pattern detection, context review needed

## Known Limitations

- May miss context-dependent language needs
- Cannot verify actual user experience
- Requires understanding of philosophy requirements
- May flag legitimate error messages

## Fallback Strategy

If this skill fails, try:

1. **Manual review**: Review UI copy manually against philosophy
2. **Philosophy rules**: Check `.cursor/rules/project-philosophy.mdc` for language requirements
3. **Targeted mode**: Focus on specific components
4. **User feedback**: Collect user feedback on language

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Components analyzed
   - Strings scanned
   - Analysis scope

2. **Findings**
   - Prescriptive language (High/Medium/Low)
   - Celebration language
   - Judgment language
   - Each finding includes location, pattern, and alternative

3. **Recommendations**
   - Language revisions (prioritized)
   - Neutral alternatives
   - Copy improvements
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered revisions
   - Copy updates
   - Component modifications

5. **Files to Modify/Create**
   - Component files with copy
   - Copy files
   - Language resource files

6. **Dependencies**
   - Philosophy rules referenced
   - Language guidelines

### Filename Convention

Reports must follow: `YYYY-MM-DD_ux-copy-neutrality-checker_target-component.md`

## Exit Conditions

### Success

- Copy neutrality validated
- Violations identified
- Alternatives proposed
- Handoff report generated

### Failure

- No UI components found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Copy neutrality check complete. Found [X] prescriptive patterns, [Y] celebration language. See report for neutral alternatives."
4. Indicate readiness for revisions

