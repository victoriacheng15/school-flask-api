# DevOps Practices

This repository implements automated code quality and documentation checks using GitHub Actions workflows. The system enforces consistent formatting and style across the codebase.

## Workflows

### CI Workflow: Format, Test, and Coverage

The CI workflow automatically formats, tests, and measures code coverage for pull requests targeting the `main` branch.

**Trigger Conditions:**
- On pull requests targeting the `main` branch.
- When changes are made to files in: `run.py`, `db/`, `app/`, or `tests/`.

**Workflow Jobs:**

The workflow runs the following jobs in sequence:

1.  **`format`**:
    - Checks out the code.
    - Sets up Python 3.12.
    - Installs dependencies (`make install`).
    - Formats code using Ruff (`make format`).
    - Commits and pushes any changes.

2.  **`test`**:
    - Waits for the `format` job to succeed.
    - Checks out the code.
    - Sets up Python 3.12.
    - Installs dependencies (`make install`).
    - Sets up the database (`make setup-db`).
    - Runs tests (`make test`).

3.  **`coverage`**:
    - Waits for the `test` job to succeed.
    - Checks out the code.
    - Sets up Python 3.12.
    - Installs dependencies (`make install`).
    - Sets up the database (`make setup-db`).
    - Calculates test coverage (`make coverage`).
    - Posts a coverage summary to the pull request.

### Documentation Linting with Markdownlint

The **Markdownlint Workflow** ensures consistent documentation formatting using [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) for all files in the `docs/` directory.

**Trigger Conditions:**
- On pull requests modifying `docs/*.md` files.
- On direct pushes to `docs/*.md` files.
- Can be manually triggered via GitHub Actions UI (`workflow_dispatch`).

**Workflow Steps:**
1.  **Checkout code:** Retrieves repository content using `actions/checkout@v4`.
2.  **Install linter:** Globally installs `markdownlint-cli` via npm.
3.  **Run linting:** Executes automatic fixes on all Markdown files in `docs/`.

## Development Practices

### Contribution Flow:
1.  Create feature branches from `main`.
2.  Open pull requests for all changes.
3.  Automated checks will:
    - Format Python files.
    - Run tests and calculate code coverage.
    - Lint and fix Markdown documentation in `docs/`.
4.  Address any unresolved linting issues or test failures before merging.

### Quality Enforcement:
- Python files maintain consistent style via Ruff.
- All code is automatically tested, and coverage is reported.
- Documentation adheres to Markdown best practices.
- All fixes are applied automatically when possible.