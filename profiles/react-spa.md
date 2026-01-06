# React SPA Profile

## Overview

Recommended skill sequences and configurations for React Single Page Application (SPA) projects.

## Project Characteristics

- **Type**: React Single Page Application
- **Stack**: React, JavaScript/TypeScript, build tools (Webpack/Vite)
- **Structure**: Component-based, client-side routing
- **Common Concerns**: Component organization, bundle size, performance, accessibility

## Recommended Skill Sequence

### Initial Assessment (First Time)

1. **project-structure-analyzer** (full-scan)
   - Maps component hierarchy
   - Identifies routing structure
   - Creates dependency graph

2. **architecture-review** (full-scan)
   - Reviews component architecture
   - Checks state management patterns
   - Evaluates routing structure
   - Focus: Component hierarchy, state management, routing

3. **adversarial-ui-tester** (full-scan)
   - Tests UI components
   - Checks accessibility
   - Identifies UX issues
   - Focus: Component usability, accessibility, user flows

4. **dependency-health-check** (full-scan)
   - Checks React and dependency versions
   - Identifies security vulnerabilities
   - Focus: React ecosystem dependencies

### Regular Maintenance (Weekly/Monthly)

1. **dependency-health-check** (incremental)
   - Check for dependency updates
   - Security vulnerability scanning

2. **adversarial-ui-tester** (incremental)
   - Test changed UI components
   - Verify accessibility maintained

### Before Major Release

1. **project-structure-analyzer** (full-scan)
   - Verify structure hasn't degraded

2. **architecture-review** (full-scan)
   - Comprehensive architecture check
   - Focus: Scalability, maintainability

3. **adversarial-ui-tester** (full-scan)
   - Full UI/UX audit
   - Accessibility compliance check

4. **dependency-health-check** (full-scan)
   - Security audit
   - Update recommendations

## Skill-Specific Configurations

### project-structure-analyzer

**Focus Areas:**
- Component directory structure
- Routing configuration
- State management setup
- Build configuration

**Key Outputs:**
- Component hierarchy map
- Route structure
- Dependency graph (components, utilities, services)

### architecture-review

**Focus Areas:**
- Component composition patterns
- State management architecture (Redux, Context, etc.)
- Routing architecture
- Code splitting strategy
- Performance patterns

**Key Concerns:**
- Component coupling
- Prop drilling
- State management complexity
- Bundle size optimization

### adversarial-ui-tester

**Focus Areas:**
- Component accessibility (ARIA, keyboard navigation)
- User flow and navigation
- Error states and edge cases
- Form validation and feedback
- Responsive design

**Key Concerns:**
- WCAG compliance
- Mobile usability
- Error handling
- Loading states

### dependency-health-check

**Focus Areas:**
- React version and ecosystem
- Build tools (Webpack, Vite, etc.)
- UI libraries (Material-UI, Ant Design, etc.)
- Testing libraries
- Security vulnerabilities

## Common Issues for React SPAs

### Component Architecture

- **Issue**: Prop drilling, tight coupling
- **Skills**: architecture-review
- **Focus**: Component composition, state management

### Performance

- **Issue**: Large bundle size, slow initial load
- **Skills**: architecture-review (code splitting), dependency-health-check (bundle analysis)
- **Focus**: Code splitting, lazy loading, dependency optimization

### Accessibility

- **Issue**: Missing ARIA labels, keyboard navigation
- **Skills**: adversarial-ui-tester
- **Focus**: WCAG compliance, keyboard navigation, screen reader support

### State Management

- **Issue**: Complex state, prop drilling
- **Skills**: architecture-review
- **Focus**: State management patterns, Context vs Redux decisions

## Skill Chain Recommendations

### Quick Health Check

```yaml
skills:
  - dependency-health-check (incremental)
  - adversarial-ui-tester (incremental on changed components)
```

### Comprehensive Audit

Use `skill-chains/full-codebase-audit-v1.yaml` with React-specific focus areas.

## Execution Tips

### For Large React Apps

- Use **targeted mode** for specific feature modules
- Break analysis into component trees
- Focus on high-traffic routes first

### For Component Libraries

- Use **adversarial-ui-tester** extensively
- Focus on API design and accessibility
- Check component composition patterns

### For Performance-Critical Apps

- Use **architecture-review** with performance focus
- Check code splitting implementation
- Analyze bundle composition

## Expected Outcomes

After running recommended skills, you should have:

1. **Structure Map**: Clear component hierarchy and organization
2. **Architecture Assessment**: Component patterns, state management evaluation
3. **UX Issues**: Accessibility problems, usability concerns
4. **Dependency Health**: Security vulnerabilities, outdated packages
5. **Actionable Recommendations**: Prioritized improvements with implementation steps

## Next Steps

After skill execution:

1. Review handoff reports
2. Prioritize recommendations (Critical/High first)
3. Implement fixes in Cursor
4. Re-run skills to validate improvements

