
# **Best Practice Guide for OEDISI Component Development**
- **Purpose:** Practical, repeatable steps for building a new OEDISI component.
- **Audience:** Component developers and integrators working with the `oedisi` framework.

**Repository & Project Setup**
- **Prefer location:** Create the new component inside the `oedisi-example` repository. Keeping components together simplifies testing, version control, and CI/integration workflows.
	- **If adding to `oedisi-example`:** Create a top-level directory `oedisi-example/<component-name>/` and follow the recommended layout.
	- **Required docs:** Add `LICENSE.md` and `CONTRIBUTORS.json` that describe commit/PR expectations and how to run tests locally.
- **Alternate location:** For independently versioned components, create a dedicated repository under the `openEDI` organization. Note this increases CI and release maintenance overhead and is NOT the prefered approach
- **Prohibited:** Avoid private or internal-only repositories, since those complicate shared CI and community review.

**Recommended Component Layout**
- `component/` — source package (python module, go module, etc.).
- `tests/unit/` — unit tests for core logic.
- `tests/integration/` — system-level tests that run the component with other federates or a minimal orchestrator.
- `examples/` — example configs, `component_definition.json`, `input_mapping.json`, sample data.
- `Dockerfile` / `docker-compose.yml` — for replicable integration test runs.
- `README.md` — usage, configuration, and quickstart (also update central docs).

**Scaffolding Steps**

- Create the directory under `oedisi-example/` and initialize git (or create a repository under `openEDI` if appropriate).
- Add `.gitignore`, `LICENSE.md`, and `README.md`.
- Scaffold a minimal package in `component/` with a clear entry point, configuration loader, and a simple run loop that can be exercised by tests.
- Add `component_definition.json` describing inputs/outputs and include an example `input_mapping.json` in `examples/`.

**Testing Strategy**

- Unit tests: Keep logic pure and unit-testable. Use `pytest` (or the project standard). Put tests in `tests/unit/`.
- Mock dependencies: Abstract external systems (HELICS, databases) with adapter interfaces so unit tests can use fast mocks.
- Integration tests: Put end-to-end tests in `tests/integration/`. Use a local HELICS broker or `docker-compose` to run multiple federates for system tests.
- Test data & fixtures: Store small representative datasets in `examples/` or `tests/fixtures/` so CI runs quickly.

**Continuous Integration**

- GitHub Actions: Create workflows to run unit tests on each PR and a separate workflow/job for integration tests (nightly or on-demand if they are long-running).
- Integration job config: Use `services`, `docker-compose`, or reusable workflows to bring up HELICS and dependent services.
- Dependency caching: Cache dependencies to speed up CI runs.

**Documentation & Discovery**

- Live docs: Keep `best_practice_guide.md` and the component `README.md` up to date as you add features.
- Component metadata: Maintain `component_definition.json` to reflect actual inputs, outputs, and configuration.
- Examples: Provide at least one runnable example in `examples/` demonstrating a typical run and expected outputs.

**Collaboration & Avoiding Silos**

- Don't build in a silo: Avoid side-loading models or making large, undocumented changes in a single component. That hides requirements from core maintainers and duplicates effort.
- Start minimal: Implement a small, well-documented component that demonstrates the required inputs/outputs and includes a `component_definition.json`. Use this artifact to propose core API or schema changes.
- Communicate early: Open an issue or RFC in the appropriate `openEDI` repo describing the change, expected APIs, and link to the minimal example so reviewers can run and test it.
- Design for extensibility: Prefer plug-ins or optional configuration over hard-coded changes. Provide fallbacks so the component can run even if core features are not yet available.

**Release & Contribution Workflow**

- Use semantic or conventional commits to help automate changelogs.
- Use PR templates and require at least one reviewer for new components or breaking changes.
- PR checklist: unit tests pass, integration smoke-tested (if applicable), docs updated, and `component_definition.json` validated.

**Checklist (Quick Start)**

- Create component scaffold under `oedisi-example/<component-name>/`.
- Add `component_definition.json` and an example `helics_config.json` in `examples/`.
- Implement unit tests in `tests/unit/` and run them locally.
- Add an integration test in `tests/integration/` and provide `docker-compose.yml` to run it.
- Update the component `README.md` and this `best_practice_guide.md` with usage and test instructions.

**Example commands**

Run unit tests:

```bash
pytest tests/unit
```

Run integration locally (example using docker-compose):

```bash
docker-compose -f docker-compose.yml up --build
```

**Where to document changes**

- Update the component `README.md` for usage and configuration examples.
- Update this file: `oedisi-example/best_practice_guide.md` with lessons learned and new steps.

