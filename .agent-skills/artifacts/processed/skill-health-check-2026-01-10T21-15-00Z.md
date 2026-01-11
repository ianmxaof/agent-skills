skill: skill-health-check
scope: core
status: processed
timestamp: 2026-01-10T21:15:00Z
intended-consumer: cursor
priority: critical
column: self-analysis
refinement-layer: generic
agent-a-coverage: 68 findings
agent-b-output: 8 findings
target: skills//.md
---
Summary
- TEMPLATE, validator, and many skills are out of sync on required metadata fields, sections, scopes, and execution modes.
- A referenced core security skill (dependency-health-check) is missing, creating broken cross-skill references.
- Lifecycle, promotion, and prerequisite metadata are inconsistently populated across both meta and domain skills.
- Meta-governance skills treat "meta" scope and custom execution modes as first-class concepts that TEMPLATE and health-check do not formally support.
- Non-skill markdown files live under skills/, and there is no type/index metadata to distinguish them from true skills.

Detailed Findings
Finding 1: Missing dependency-health-check skill and broken references
Severity: critical
Issue: Multiple skills reference a security/dependency-health-check skill that does not exist on disk, leaving those guidance paths and examples unresolved.
Impact: Consumers following anti-pattern guidance or examples will be directed to a non-existent skill; automated routing or prerequisite resolution will silently fail or mislead.
Files Affected: At least skills/api/api-boundary-validator.md, skills/analysis/documentation-drift-detector.md, and any other skills referencing skills/security/dependency-health-check.md.
Recommendation: Either (a) add skills/security/dependency-health-check.md with the expected behavior and metadata, or (b) remove or rewrite all references to this skill and adjust anti-pattern guidance accordingly.

Finding 2: TEMPLATE and skill-health-check drift from actual metadata usage
Severity: high
Issue: TEMPLATE.md and skills/meta/skill-health-check.md both prescribe a richer, stricter set of front-matter fields and required sections (e.g., lifecycle, domain, derived-from, promotion-candidate, Scope and Classification, Tags section) than most skills actually implement.
Impact: Any strict automation aligned with TEMPLATE or skill-health-check will flag large portions of the skills tree as non-compliant, even though they function in practice; "passes health-check" does not mean "TEMPLATE-compliant".
Files Affected: TEMPLATE.md, skills/meta/skill-health-check.md, and most skills under skills/api/, skills/architecture/, skills/database/, skills/failure-modes/, skills/performance/, skills/testing/, skills/ux/, skills/variants/, skills/rac/, skills/security/, skills/state/, skills/philosophy/.
Recommendation: Decide on the canonical metadata contract (fields and sections), update TEMPLATE.md and skills/meta/skill-health-check.md to match it, and then gradually normalize existing skills to that contract or explicitly document allowed exceptions.

Finding 3: Execution modes inconsistent with canonical set
Severity: high
Issue: Many domain skills use subsets of the canonical execution-modes (full-scan, incremental, targeted), while several meta skills define entirely custom modes (e.g., change-analysis, assessment, intentless) that do not fit the validator's allowed set or lack matching narrative sections.
Impact: Execution behavior is ambiguous for both humans and tools; validators cannot reliably verify that front-matter execution-modes align with the documented Execution Mode Implementation, and meta skills in particular cannot be cleanly classified.
Files Affected: skills/meta/change-amplification-detector.md, skills/meta/column-router.md, skills/meta/health-assessor.md, other skills/meta/*.md, and domain skills like skills/failure-modes/failure-mode-simulator.md that omit one or more canonical modes.
Recommendation: Clarify whether execution-modes is a closed enum or an extensible scheme; either (a) require all skills (including meta) to map onto the canonical full-scan/incremental/targeted set with matching body sections, or (b) formally extend TEMPLATE and skill-health-check to support custom mode names with clear type/semantics.

Finding 4: Lifecycle and promotion metadata are inconsistently applied
Severity: high
Issue: Many skills either omit lifecycle entirely or use it without the supporting promotion metadata (derived-from, promotion-candidate), and the health-check skill itself does not model lifecycle despite TEMPLATE describing it as required.
Impact: There is no reliable, machine-readable view of which skills are experimental vs preferred vs deprecated, nor of how skills relate via promotion paths; governance and automation around promotion/demotion are weakened.
Files Affected: Most domain skills (e.g., skills/api/api-boundary-validator.md, skills/architecture/architectural-drift-detector.md, skills/database/database-migration-safety-checker.md, skills/failure-modes/failure-mode-simulator.md, performance/testing/UX/state/philosophy/variants skills) and several meta skills (e.g., skills/meta/column-router.md, skills/meta/readiness-certifier.md, skills/meta/skill-gap-detector.md).
Recommendation: Establish a clear rule for lifecycle and promotion fields (which skills must carry them and how), update skills/meta/skill-health-check.md to enforce that rule, and then add or normalize lifecycle/derived-from/promotion-candidate across affected skills.

Finding 5: Scope/meta taxonomy is under-specified
Severity: high
Issue: TEMPLATE allows scope: core|domain|project, but many governance skills use scope: meta and define behavior at a meta-governance layer; this meta scope is not formally recognized in TEMPLATE or in the validator.
Impact: Meta skills that orchestrate or govern other skills appear non-compliant under the current template, and tools that assume the three-scope taxonomy cannot accurately classify or filter them.
Files Affected: skills/meta/skill-health-check.md, skills/meta/change-amplification-detector.md, skills/meta/column-router.md, skills/meta/health-assessor.md, and other skills/meta/*.md.
Recommendation: Either extend TEMPLATE and skill-health-check to support scope: meta (with its own expectations), or define an explicit alternative template for meta skills and ensure tools treat that as a first-class category.

Finding 6: Required narrative sections are only partially enforced
Severity: medium
Issue: While most skills include Purpose, When to Invoke, Behavioral Rules, and an Execution Mode Implementation section, some required sections from the health-check and TEMPLATE (e.g., Fallback Strategy, Exit Conditions, Scope and Classification, Tags for Intent Resolution, Context Received) are missing or inconsistently labeled across the tree.
Impact: Readers and tools cannot rely on a uniform shape for skill docs; certain failure paths, limitations, or chaining expectations may be undocumented or hard to locate even when conceptually present.
Files Affected: skills/meta/skill-health-check.md, several large meta skills (e.g., skills/meta/health-assessor.md), and a subset of domain skills across skills/analysis/, skills/architecture/, skills/performance/, skills/testing/, skills/ux/, and related directories.
Recommendation: Clarify which narrative sections are truly mandatory vs optional, align the checklist in skills/meta/skill-health-check.md with that decision, and then standardize headings across skills to make those sections discoverable and validator-friendly.

Finding 7: Prerequisite and cross-skill dependency metadata are incomplete
Severity: medium
Issue: Many skills either leave prerequisites: [] despite depending on other skills or project files, or encode dependencies only in prose (e.g., "Instead: Use dependency-health-check"), while others provide well-structured prerequisites; there is no consistent standard for when and how dependencies must be declared.
Impact: Automated resolvers and orchestrators cannot reliably determine which skills or files are required before running a given skill, and broken or missing dependencies (like dependency-health-check) are not surfaced systematically.
Files Affected: skills/analysis/documentation-drift-detector.md, skills/architecture/architectural-drift-detector.md, skills/database/database-migration-safety-checker.md, skills/meta/column-router.md, skills/meta/health-assessor.md, skills/api/api-boundary-validator.md, and other skills that mention other skills only in narrative text.
Recommendation: Define a clear prerequisite schema and policy in TEMPLATE and skill-health-check (including how to reference other skills vs files), and retrofit skills so that all real dependencies are captured there rather than solely in narrative sections.

Finding 8: Non-skill documents and lack of type/index metadata confuse validation
Severity: medium
Issue: The skills/ tree contains markdown files that are not skill definitions (e.g., skills/architecture/CHANGELOG.md), and there is no machine-readable field that distinguishes skill definitions from other docs or a centralized index mapping skill names to files.
Impact: Any validator that naively treats skills/**/*.md as skills will flag non-skill docs as invalid; conversely, it cannot easily detect missing skills, orphaned docs, or broken skill references.
Files Affected: skills/architecture/CHANGELOG.md and any other non-skill markdown files under skills/, plus the implicit absence of a global skill index (e.g., a dedicated skills index separate from existing skill-map.yaml).
Recommendation: Introduce a type marker in front matter (e.g., type: skill-definition vs type: changelog) and/or a central skill index file, and update skill-health-check to ignore non-skill types and to validate that all referenced skills exist in the index.

Risks / Edge Cases
- Passing skill-health-check today does not guarantee TEMPLATE compliance, which may mislead maintainers about true documentation and metadata health.
- Meta skills are at highest risk of being marked invalid by strict validators due to scope: meta and custom execution modes, despite being central to governance.
- Broken or future-focused references (e.g., dependency-health-check, other named-but-absent skills) can accumulate silently without a central index, increasing drift over time.
- Subset execution-modes (e.g., skills that intentionally do not support incremental) may be incorrectly treated as errors if validation assumes all three modes must always exist.

Recommendations
- First, reconcile TEMPLATE.md and skills/meta/skill-health-check.md with actual, desired practice (including meta scope and execution-modes semantics) before touching individual skills.
- Next, address the missing dependency-health-check skill or scrub its references so that anti-pattern guidance is never pointing to a non-existent capability.
- Then, normalize lifecycle and prerequisite metadata across skills, starting with Tier 1/Tier 2 and meta-governance skills where governance impact is highest.
- Finally, introduce minimal type/index metadata so that future validators and routers can reliably distinguish skills from other docs and verify cross-skill references.

Files / Surfaces Involved
- TEMPLATE.md (source of canonical skill structure).
- skills/meta/skill-health-check.md (validator skill and meta-policy owner).
- skills/meta/*.md (meta-governance and routing skills, especially those using scope: meta and custom execution-modes).
- Domain skill trees: skills/api/, skills/architecture/, skills/database/, skills/failure-modes/, skills/performance/, skills/testing/, skills/ux/, skills/rac/, skills/security/, skills/state/, skills/philosophy/, skills/variants/.
- Non-skill docs under skills/ (e.g., skills/architecture/CHANGELOG.md) and any future READMEs or similar.

Handoff Notes for Cursor
- Prioritize a small design pass on TEMPLATE.md and skills/meta/skill-health-check.md to lock in the canonical metadata fields, scopes (including meta), and execution-mode semantics.
- Treat the missing dependency-health-check skill and its references as a blocking issue for security- and API-related governance flows.
- Plan a phased metadata normalization effort (lifecycle, prerequisites, type markers) starting with meta and Tier 1/Tier 2 skills, using automated checks where possible.
- Defer full per-skill narrative polishing (e.g., expanding Examples sections) until the structural and metadata contract is stable, to avoid double work.
