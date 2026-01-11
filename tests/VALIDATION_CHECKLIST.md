# Validation Checklist

This checklist provides a reusable process for validating and refining the tag taxonomy when needed.

## When to Use This Checklist

- After adding new skills that might overlap with existing ones
- When routing behavior becomes inconsistent or surprising
- When tag taxonomy needs refinement based on real usage
- Periodically (e.g., quarterly) to ensure taxonomy remains stable

## Validation Process

### Phase 1: Testing

- [ ] Run 5-7 real intents through skill-router
- [ ] Review resolution traces for each intent
- [ ] Document observations in `routing-observations.md`
- [ ] Identify tag conflicts and surprising matches

### Phase 2: Analysis

- [ ] Analyze observations to identify patterns
- [ ] Identify skills that always come second (tag overlap)
- [ ] Identify surprising matches (tags too broad)
- [ ] Identify missing discriminators (tags too narrow)
- [ ] Document confusing tag pairs

### Phase 3: Refinement

- [ ] Refine tags based on observations (one deliberate pass)
- [ ] Remove weak/duplicate tags
- [ ] Add missing discriminators
- [ ] Rename ambiguous tags
- [ ] Ensure 4-6 tags per skill (optimal range)

### Phase 4: Documentation

- [ ] Document taxonomy in `meta/tag-taxonomy.md`
- [ ] Update tag guidelines in `TEMPLATE.md` if patterns emerge
- [ ] Lock as stable
- [ ] Document decision to lock taxonomy (date + reason)

## Success Criteria

- All test intents route to expected skills with confidence >= 0.7
- No surprising matches or tag conflicts
- Clear discrimination between similar skills
- Tag taxonomy is documented and stable

## Notes

- Tag refinement should be **one deliberate pass**, not continuous
- After refinement, treat tags as **stable API**
- Only change tags via skill-gap-detector or effectiveness analysis after locking
- This is a **hardening process**, not feature expansion

## Related Documents

- `routing-validation.md` - Test intents for validation
- `routing-observations.md` - Template for recording observations
- `meta/tag-taxonomy.md` - Final tag taxonomy documentation

