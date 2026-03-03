from fastapi import FastAPI
from pydantic import BaseModel


class RecieveArticle(BaseModel):
    article_id: str
    title: str
    content: str
    vector: list[float]


app = FastAPI()

articles = {}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "store"
    }


@app.get("/articles")
async def get_articles():
    return articles

@app.post("/articles/store")
async def post_article(data: RecieveArticle):
    articles[data.article_id] = data.model_dump()
    return {
        "status": "stored",
        "article_id": data.article_id
    }