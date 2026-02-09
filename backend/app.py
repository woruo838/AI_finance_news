from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.news import build_digest, fetch_news, summarize

app = FastAPI(title="AI Finance News")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/api/news")
async def api_news(limit: int = 20) -> dict[str, object]:
    items = fetch_news(limit=limit)
    return {
        "count": len(items),
        "items": [
            {
                **item,
                "summary": summarize(item.get("description", "")),
            }
            for item in items
        ],
    }


@app.get("/api/digest")
async def api_digest(limit: int = 10) -> dict[str, object]:
    return build_digest(limit=limit)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/app")
async def app_shell() -> FileResponse:
    return FileResponse("frontend/index.html")
