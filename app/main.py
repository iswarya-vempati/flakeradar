from fastapi import FastAPI

app = FastAPI(title = "Flakeradar")


@app.get("/health")
def health():
    return {"status": "ok"}