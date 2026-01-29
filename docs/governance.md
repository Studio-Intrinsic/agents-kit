# Governance

This document describes how the agents-kit library is maintained and evolved.

## Principles

1. **Quality over quantity**: Better to have 10 excellent skills than 100 mediocre ones
2. **Portability matters**: Skills should work across runtimes
3. **Compound knowledge**: Every session can improve the library
4. **Clear ownership**: Every pack has maintainers

## Pack Ownership

### Core Pack
- **Maintainers**: Core team
- **Approval**: Requires 2 approvals
- **Standards**: Highest bar, most stable

### Domain Packs (coding, extraction, etc.)
- **Maintainers**: Domain experts
- **Approval**: Requires 1 approval from maintainer
- **Standards**: High bar, can iterate faster

## Change Process

### Adding a New Skill

1. Create skill using `agents new skill <name>`
2. Write content following authoring guide
3. Add to pack.yaml skills list
4. Run validation: `agents validate`
5. Submit PR with:
   - Description of use case
   - Examples of expected input/output
   - Which pack it belongs to
6. Get review from pack maintainer
7. Merge after approval

### Updating a Skill

1. Edit the skill.md file
2. Bump version appropriately:
   - Patch: Typos, clarifications
   - Minor: New examples, expanded procedure
   - Major: Changed inputs/outputs, different behavior
3. Run validation
4. Submit PR with changelog
5. Review and merge

### Deprecating a Skill

1. Add `deprecated: true` to frontmatter
2. Add `deprecation_message` explaining alternative
3. Keep for 2 major versions before removal
4. Announce in changelog

## Version Policy

### Skill Versions
- Individual skills have their own versions
- Follow semantic versioning strictly
- Major version = breaking change

### Pack Versions
- Packs version independently of skills
- Pack version bumps when:
  - Skills are added/removed
  - Major skill updates occur
  - Pack configuration changes

### Lock File
- `agents.lock` pins exact versions
- Regenerate with `agents lock`
- Commit lock file to repo
- Update deliberately, not accidentally

## Release Process

1. Prepare release:
   ```bash
   agents validate
   agents test
   agents lock
   ```

2. Create release PR:
   - Update CHANGELOG.md
   - Bump pack versions as needed
   - Include migration notes if needed

3. Tag release:
   ```bash
   git tag v0.10.0
   git push origin v0.10.0
   ```

4. Announce:
   - Changelog summary
   - Notable changes
   - Migration steps if needed

## Quality Standards

### All Skills Must:
- [ ] Pass schema validation
- [ ] Have unique ID
- [ ] Include Intent section
- [ ] Include Procedure section
- [ ] Include at least one example
- [ ] Render successfully for all target runtimes

### Core Pack Skills Must Also:
- [ ] Have comprehensive examples
- [ ] Include Failure Modes section
- [ ] Be tested with golden outputs
- [ ] Have 2+ approvals

## Compounding Process

End of session:
```bash
agents compound
```

This reviews the session and proposes:
- New skills
- Updates to existing skills
- New patterns

Proposals go through normal PR process.

## Decision Making

### Consensus
- Most changes through PR review
- Maintainers have final say on their packs

### Escalation
- Disagreements go to core team
- Core team decides by majority

### RFC Process (for large changes)
- Write RFC document describing:
  - Problem statement
  - Proposed solution
  - Alternatives considered
  - Migration path
- Discuss in PR/issue
- Core team approves/rejects
- Implement after approval

## Code of Conduct

- Be constructive in reviews
- Assume good intent
- Focus on the work, not the person
- Help newcomers succeed
