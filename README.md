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

k8s/                       # Deployment, Service, and ConfigMap
argocd/
└── application.yaml        # Argo CD follows main/k8s

.github/workflows/
├── ci.yml                  # Tests, builds, scans, and publishes the image
└── m5.yml                  # Tests GitOps in a throwaway kind cluster
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

## GitOps deployment

Argo CD 3.5.3 deploys the plain YAML files in `k8s/` from the `main` branch of
`https://github.com/DMen6L/repo-manager`. The Application is named `repo-manager`,
lives in the `argocd` namespace, and deploys the service into the existing M4
namespace, `m4`.

The Application enables automated sync, `prune: true`, and `selfHeal: true`.
Argo CD restores the replica count from Git, recreates a deleted Service, and
removes managed resources that are removed from Git. Change the manifests in
Git and merge a pull request to change the running service.

The `app-secret` Secret is created separately in the destination namespace and
is never committed or managed by Argo CD. This service reads its
`FORWARDED_ALLOW_IPS` key as Uvicorn's trusted proxy allowlist. For a cluster
without a trusted ingress proxy, create it with:

```bash
kubectl -n m4 create secret generic app-secret \
  --from-literal=FORWARDED_ALLOW_IPS=127.0.0.1,::1
```

After installing the lab's pinned, checksum-verified Argo CD 3.5.3 and merging
the Application into `main`, hand the M4 resources over to Argo CD. The
destination namespace and its Secret must already exist. These commands briefly
remove the manually deployed service; Argo CD recreates it from Git:

```bash
kubectl -n m4 delete -f k8s/
kubectl apply -f argocd/application.yaml
kubectl -n argocd get application repo-manager -w
```

Wait for `Synced` and `Healthy`. In another terminal, inspect the application:

```bash
kubectl -n m4 get deployment,service,pods
kubectl -n m4 port-forward service/repo-manager 8080:80
```

Then `curl http://localhost:8080/healthz` should return `{"status":"ok"}`.
To request a Git refresh immediately:

```bash
kubectl -n argocd annotate application repo-manager \
  argocd.argoproj.io/refresh=normal --overwrite
```

CI continues to build, scan, and publish images to GHCR. It has no credentials
for the application cluster and never deploys to it. A deployment changes only
the full commit-SHA image tag in `k8s/deployment.yaml`, after that commit's
publish job succeeds.

The `M5 check` workflow runs the official grader on pushes to `m5` and `main`,
on pull requests to `main`, and through manual dispatch. It checks out the
actual pushed commit with full history, verifies the tool and grader downloads,
and runs Kubernetes 1.36.4 with Argo CD 3.5.3 inside its own temporary cluster.
The Actions summary and annotations show each checkpoint and the final score.
This test cluster is separate from the application cluster.

The published image is `linux/amd64`. Run the live grader using the GitHub
Actions workflow on Intel runners when developing on an Apple M-series Mac.
For local static checks from the repository root, use the project Python
environment, which includes PyYAML:

```bash
curl -fsSLo /tmp/mark_m5.py https://raw.githubusercontent.com/inf345/inf345-week10-lab/090e437fc490e4887cd8fd1a39bc18bb2fc036fc/mark_m5.py
echo "6b81a9b6906663721eaf0e5e25a1ff9243c84ba0a0809cfda2f6c7bd04451e16  /tmp/mark_m5.py" | shasum -a 256 -c -
backend/.venv/bin/python /tmp/mark_m5.py --path .
```

The grader stays outside the repository and is never committed. The live
grader reads the committed files from GitHub, so commit and push changes before
running it. A passing live run reports `SCORE: 100/100`.

## Rollback

Argo CD deploys what is on the `main` branch, from the `k8s` folder.
To roll back, undo the commit that deployed the bad image with a new commit:

```bash
git switch main
git pull --ff-only
git log --oneline -- k8s/deployment.yaml
git revert COMMIT_SHA
git push origin main
```

Replace `COMMIT_SHA` with the image-bump commit shown in the log. If reverting
a pull request's merge commit, use `git revert -m 1 MERGE_COMMIT_SHA`; for a
squash merge or a normal image-bump commit, use `git revert COMMIT_SHA`.
If `main` requires pull requests, push the revert on a new branch and merge
that pull request instead.

Argo CD deploys the previous version within about three minutes after the
revert reaches `main`. To check immediately, request a refresh and watch the
rollout:

```bash
kubectl -n argocd annotate application repo-manager \
  argocd.argoproj.io/refresh=normal --overwrite
kubectl -n m4 rollout status deployment/repo-manager --timeout=180s
kubectl -n m4 get deployment repo-manager -o jsonpath='{..image}'
```

Do not use `kubectl rollout undo`: self-heal would put the bad version back
because Git still names that image. Keep both the image bump and its revert in
history so the deployment and rollback have an audit trail.

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
