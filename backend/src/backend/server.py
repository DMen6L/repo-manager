from fastapi import FastAPI

app = FastAPI(title="Repository Manager API")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/count")
def counter() -> dict[str, str]:
    return {"": ""}
