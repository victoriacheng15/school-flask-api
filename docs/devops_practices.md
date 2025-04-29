# DevOps Practices

This repository implements automated code quality and documentation checks using GitHub Actions workflows. The system enforces consistent formatting and style across the codebase.

## Workflows

### Python Formatting with Ruff

The **Ruff Formatting Workflow** automatically checks and corrects Python code formatting using [Ruff](https://github.com/astral-sh/ruff) when changes are proposed to the main branch.

**Trigger Conditions:**
- Activates on pull requests targeting the `main` branch
- Processes files matching:
  - `app.py` (main application file)
  - Any files in the `db/` directory

**Workflow Steps:**
1. **Checkout code:** Retrieves the PR branch code using `actions/checkout@v4`
2. **Setup Python:** Configures Python 3.12 environment
3. **Install dependencies:** Executes `make install` to prepare the environment
4. **Run formatting:** Applies Ruff formatting via `make format`
5. **Commit changes:** Automatically commits and pushes formatting changes when needed:
   - Uses GitHub Actions bot identity for commits
   - Creates descriptive "ci: auto-format code with Ruff" commit messages
   - Only pushes when actual formatting changes exist

### Documentation Linting with Markdownlint

The **Markdownlint Workflow** ensures consistent documentation formatting using [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) for all files in the `docs/` directory.

**Trigger Conditions:**
- On pull requests modifying `docs/*.md` files
- On direct pushes to `docs/*.md` files
- Can be manually triggered via GitHub Actions UI (`workflow_dispatch`)

**Workflow Steps:**
1. **Checkout code:** Retrieves repository content using `actions/checkout@v4`
2. **Install linter:** Globally installs `markdownlint-cli` via npm
3. **Run linting:** Executes automatic fixes on all Markdown files in `docs/`:
   - Applies style corrections
   - Reports remaining issues

## Development Practices

### Contribution Flow:
1. Create feature branches from `main`
2. Open pull requests for all changes
3. Automated checks will:
   - Format Python files in `app.py` and `db/`
   - Lint and fix Markdown documentation in `docs/`
4. Address any unresolved linting issues before merging

### Quality Enforcement:
- Python files maintain consistent style via Ruff
- Database code follows standardized formatting
- Documentation adheres to Markdown best practices
- All fixes applied automatically when possible