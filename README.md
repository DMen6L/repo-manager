# Repository Manager

## What it does

An AI-powered repository management and visualization platform for understanding unfamiliar codebases, exploring architecture, organizing development tasks, and planning changes with repository-aware assistance.

The project is being developed incrementally. The current version is a small FastAPI service with hardcoded Python repository cases. Repository parsing, graph visualization, task management, and AI features will be added on top of this foundation.

## Current scope

The current backend can:

- Start as an HTTP service.
- Report its health through `/healthz`.
- List available example repositories.
- Return the source files in an example repository.
- Return a basic file and module summary.
- Run an automated test suite through a project script.

The current implementation does not yet use a database, frontend, LLM integration, GitHub authentication, or background workers.

## Technology

- Python 3.12+
- FastAPI
- Uvicorn
- `uv` for dependency and environment management
- Pytest for automated tests

## Repository structure

```text
backend/
├── cases/                  # Small example repositories used by the API
├── src/backend/
│   └── server.py           # FastAPI application and current endpoints
├── tests/                  # Backend tests
├── pyproject.toml
└── uv.lock

scripts/
├── run.sh                  # Starts the API service
├── test.sh                 # Runs tests and prints TESTS: n/n
└── count_tests.py          # Counts test results from the JUnit report

.github/workflows/
└── ci.yml                  # GitHub Actions test workflow
```

## Requirements

- Python 3.12 or newer
- `uv`
- Bash

## Installation

From the repository root:

```bash
cd backend
uv sync
cd ..
```

## Running the service

The service uses port `8080` by default:

```bash
./scripts/run.sh
```

To use a different port:

```bash
PORT=9090 ./scripts/run.sh
```

The API will be available at:

```text
http://127.0.0.1:8080
```

The interactive API documentation is available at `/docs`.

## How to test it

Run the test suite from the repository root:

```bash
./scripts/test.sh
```

The script prints a normalized result such as:

```text
TESTS: 6/6
```

It exits with code `0` when all tests pass and a non-zero code when tests fail.

## Continuous integration

GitHub Actions runs the test workflow for pull requests and for pushes to
`main`. The workflow:

1. Checks out the repository.
2. Sets up Python 3.12 and `uv`.
3. Restores the `uv` dependency cache using `backend/uv.lock` as the cache key.
4. Installs the locked dependencies with `uv sync --locked`.
5. Runs `scripts/test.sh`.

The dependency cache speeds up later workflow runs while changing
`backend/uv.lock` automatically creates a new cache entry. The workflow uses
read-only repository permissions and pins its third-party actions to known
versions or commits.

To reproduce the CI test locally:

```bash
uv sync --directory backend --locked
./scripts/test.sh
```

The expected successful output is:

```text
TESTS: 6/6
```

## Current API

### Health check

```text
GET /healthz
```

Returns:

```json
{"status": "ok"}
```

### List example cases

```text
GET /cases
```

### Get an example case

```text
GET /cases/basic_project
```

Returns the example's Python files and their source contents.

### Get an example summary

```text
GET /cases/basic_project/summary
```

Returns the number of Python files and the module names currently detected from the fixture files.

## Product roadmap

The planned product will grow through these stages:

1. Analyze local Python repositories with Python AST.
2. Identify files, modules, classes, functions, imports, and relationships.
3. Store and expose the repository graph through the backend API.
4. Build an interactive React and React Flow architecture view.
5. Add tasks linked to repository files and graph components.
6. Add evidence-grounded repository questions and implementation plans.
7. Add commits, branches, GitHub integration, authentication, deployment, and monitoring.

The parser and graph representation are the foundation for the visualization, task management, retrieval, and AI features.
