---
name: project-structure-analyzer
category: analysis
version: 1.0.0
maturity: validated
estimated-cost: low
typical-runtime: 1-3min
complexity-level: simple
requires-deep-analysis: false
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Project Structure Analyzer

## Purpose

Maps the codebase structure, identifies key components, creates dependency graphs, and provides a foundation for other skills to build upon. This is a foundational skill that should often run before other analysis skills.

## When to Invoke

### Explicit Trigger Phrases

- "Run project-structure-analyzer on this codebase"
- "Map the project structure"
- "Analyze the codebase organization"
- "Create a dependency graph"

### Situational Triggers

- Before running architecture-review (needs codebase map)
- When starting work on unfamiliar codebase
- After major structural changes
- When onboarding to a new project

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or better
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Start with high-level structure (directories, main modules)
- Identify entry points (main files, index files, config files)
- Map dependencies between modules
- Identify technology stack and frameworks
- Note architectural patterns (MVC, microservices, monolith, etc.)

### What It Must Avoid

- Don't analyze code quality (that's for code-review skills)
- Don't make architectural recommendations (that's for architecture-review)
- Don't read every file in detail (focus on structure)
- Don't assume structure without evidence

### What It Must Prioritize

- Directory structure and organization
- Dependency relationships
- Entry points and main modules
- Technology stack identification
- Key architectural boundaries

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- First time analyzing codebase
- After major restructuring
- When comprehensive map needed

**Input:**
- Entire codebase directory structure
- Package files (package.json, requirements.txt, etc.)
- Configuration files
- Main entry points

**Process:**
1. Scan directory structure
2. Identify technology stack from config files
3. Map main modules and components
4. Create dependency graph
5. Identify architectural patterns

**Invocation Example:**
> "Run project-structure-analyzer in full-scan mode on the entire project"

### Incremental Mode

**When to Use:**
- After adding new modules
- When structure changes detected
- For continuous monitoring

**Input:**
- Git diff showing new directories/files
- Changed configuration files
- New dependencies added

**Process:**
1. Identify what changed in structure
2. Update dependency graph for new modules
3. Check if architectural boundaries shifted
4. Report on structural changes

**Invocation Example:**
> "Run project-structure-analyzer in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Analyzing specific module or directory
- Understanding one component in detail
- Focused exploration

**Input:**
- Specific directory path
- Module boundaries

**Process:**
1. Deep dive into specified directory
2. Map internal structure
3. Identify dependencies (internal and external)
4. Document module boundaries

**Invocation Example:**
> "Run project-structure-analyzer in targeted mode on src/auth/ directory"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality Analysis**
- **Instead:** Use `code-quality-audit` or similar code-review skills
- **Why:** This skill focuses on structure, not code quality. It doesn't analyze code content in detail.

**Anti-Pattern 2: Architectural Recommendations**
- **Instead:** Use `architecture-review` after running this skill
- **Why:** This skill maps what exists, it doesn't recommend improvements. Architecture-review uses this output to make recommendations.

**Anti-Pattern 3: Running on Every Small Change**
- **Instead:** Use incremental mode only when structure actually changes
- **Why:** Low cost but unnecessary if only code content changed, not structure. Save for structural changes.

### ⚠️ WARNING: Known Limitations

**Limitation:** May miss implicit dependencies in dynamic languages
- **Mitigation:** Check runtime dependency analysis tools for JavaScript/Python projects
- **Confidence:** ~85% accuracy on static analysis, ~60% on dynamic dependencies

**Limitation:** May not detect micro-frontend boundaries clearly
- **Mitigation:** Look for build configuration and deployment patterns
- **Confidence:** ~70% accuracy on micro-frontend detection

## Known Limitations

- Struggles with very large monorepos (> 100k files) - may need to focus on key modules
- Dynamic imports in JavaScript may not be fully detected
- Implicit dependencies in Python (imports via strings) may be missed
- Binary files and generated code are not analyzed
- Build-time dependencies vs runtime dependencies may be conflated

## Fallback Strategy

If this skill fails, try:

1. **Manual structure review**: Use file explorer and README files
2. **Use build tools**: Check webpack.config, tsconfig.json for structure hints
3. **Check documentation**: README, ARCHITECTURE.md may have structure info
4. **Run in targeted mode**: Break into smaller modules and analyze separately

## Output Contract

### Handoff Report Structure

The handoff report MUST include these sections:

1. **Context Summary**
   - Codebase overview (size, type, technology stack)
   - Analysis scope (what was analyzed)
   - Key assumptions about structure

2. **Findings**
   - Directory structure map
   - Main modules and components identified
   - Dependency graph (visual or textual)
   - Entry points discovered
   - Architectural patterns detected
   - Technology stack summary

3. **Recommendations**
   - None typically (this is a mapping skill)
   - May note obvious structural issues if found

4. **Implementation Steps**
   - N/A (this skill doesn't modify code)

5. **Files to Modify/Create**
   - N/A (this skill doesn't modify code)
   - May suggest creating ARCHITECTURE.md if missing

6. **Dependencies**
   - Technology stack identified
   - Key frameworks and libraries
   - Build tools detected

### Filename Convention

Reports must follow: `YYYY-MM-DD_project-structure-analyzer_target-component.md`

Examples:
- `2024-01-05_project-structure-analyzer_full-project.md`
- `2024-01-05_project-structure-analyzer_backend-module.md`

### Context Preservation Strategy

For large codebases, structure the report as:

1. **Executive Summary** (high-level structure)
2. **Detailed Structure Map** (can be in separate file if very large)
3. **Dependency Graph** (visual or textual)
4. **Technology Stack** (summary)

If report exceeds 4000 tokens:
- Keep summary and high-level structure in main report
- Move detailed directory tree to separate file
- Link to detailed analysis

## Exit Conditions

### Success

- Codebase structure mapped
- Dependency graph created
- Technology stack identified
- Handoff report generated per protocol
- Report saved with proper filename

### Failure

- Missing critical files (package.json, etc.) - should fail with clear error
- Unreadable codebase structure - document what was found
- Timeout on very large codebase - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Codebase structure mapped. Found [X] main modules, [Y] dependencies. See report for details."
4. Indicate this output can be used by other skills (architecture-review, etc.)

## Examples

### Example 1: Full Project Analysis

**Scenario:** Analyzing a React + Node.js full-stack application

**Expected Output:**
- Structure map showing frontend/backend separation
- Dependency graph showing React components and API routes
- Technology stack: React, Node.js, Express, etc.
- Entry points: src/index.js, server/index.js
- Architectural pattern: Client-server separation

### Example 2: Targeted Module Analysis

**Scenario:** Analyzing just the authentication module

**Expected Output:**
- Structure of auth module (files, subdirectories)
- Dependencies: what auth module imports
- Dependents: what imports from auth module
- Entry points: auth/index.js, auth/routes.js
- Internal structure and organization

