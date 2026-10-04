from pathlib import Path

from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Repository Manager API")
CASES_DIR = Path(__file__).resolve().parents[2] / "cases"


def _case_directory(case_name: str) -> Path:
    case_directory = (CASES_DIR / case_name).resolve()

    if case_directory.parent != CASES_DIR.resolve() or not case_directory.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case '{case_name}' was not found",
        )

    return case_directory


def _python_files(case_directory: Path) -> list[Path]:
    return sorted(path for path in case_directory.rglob("*.py") if path.is_file())


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def root() -> dict[str, str]:
    return {"status": "ready"}


@app.get(
    "/healthz",
    status_code=status.HTTP_200_OK,
)
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/cases",
    status_code=status.HTTP_200_OK,
)
def list_cases() -> dict[str, list[str]]:
    cases = (
        sorted(path.name for path in CASES_DIR.iterdir() if path.is_dir())
        if CASES_DIR.is_dir()
        else []
    )

    return {"cases": cases}


@app.get(
    "/cases/{case_name}",
    status_code=status.HTTP_200_OK,
)
def get_case(case_name: str) -> dict[str, object]:
    case_directory = _case_directory(case_name)
    files = _python_files(case_directory)

    return {
        "name": case_name,
        "files": [
            {
                "path": path.relative_to(case_directory).as_posix(),
                "content": path.read_text(encoding="utf-8"),
            }
            for path in files
        ],
    }


@app.get(
    "/cases/{case_name}/summary",
    status_code=status.HTTP_200_OK,
)
def get_case_summary(case_name: str) -> dict[str, object]:
    case_directory = _case_directory(case_name)
    files = _python_files(case_directory)

    return {
        "name": case_name,
        "python_files": len(files),
        "modules": [
            path.relative_to(case_directory).with_suffix("").as_posix()
            for path in files
        ],
    }
