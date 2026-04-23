## Summary

Describe what this PR changes and why.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Documentation update
- [ ] New component

## Component Impact

List affected components:

-

## Required Checks

- [ ] Linting passes
- [ ] Formatting checks pass
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)

## New Component Requirements

Complete this section if this PR adds a new component.

- [ ] Component directory follows existing structure and conventions in `docs/component-structure.md`
- [ ] `component_definition.json` is included and valid
- [ ] `README.md` is included and documents usage
- [ ] `Dockerfile` is included
- [ ] `.gitmodules` is updated for the new component submodule
- [ ] Unit test workflow added: `.github/workflows/unit-test-<component>.yml`
- [ ] Component verification workflow added: `.github/workflows/verify-components-<component>.yml`
- [ ] Dockerfile verification workflow added: `.github/workflows/verify-dockerfiles-<component>.yml`
- [ ] New wiring diagram added to `scenarios/` (for example, `<component>_system.json`)
- [ ] Integration test added and uses the new wiring diagram in `scenarios/`
- [ ] Any required updates to root workflows are included and do not duplicate runs

## Validation Evidence

Include command output or links to CI runs.

```bash
# Example commands
pytest -v
```

## Checklist

- [ ] I updated documentation and badges as needed
- [ ] I confirmed CI workflows and file paths are correct
- [ ] I verified there are no unrelated changes in this PR
