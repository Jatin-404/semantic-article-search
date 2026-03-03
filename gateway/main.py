from fastapi import FastAPI
import uuid
from pydantic import BaseModel
from httpx import AsyncClient
import asyncio

class RequestArticle(BaseModel):
    title: str
    content: str

class RequestQuery(BaseModel):
    text: str


app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "gateway"
    }

async def ingest_one(data: RequestArticle):
    article_id = str(uuid.uuid4())

    for_embed = {
        "text": [data.content]
    }


    async with AsyncClient() as client:
        embed_response = await client.post("http://localhost:8001/embedding", json=for_embed)
        embeddings = embed_response.json()["embeddings"][0]  #embeddings is a list of vectors (one per text), [0] gets the first one since we only sent one text.


        to_store = {
        "article_id": article_id,
        "title": data.title,
        "content": data.content,
        "vector": embeddings
        }

        store_response = await client.post("http://localhost:8002/articles/store", json=to_store)
        return store_response.json()



@app.post("/articles")
async def add_article(data: list[RequestArticle]):
        tasks = [ingest_one(article) for article in data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # results = []
        # for article in data:
        #      result = await ingest_one(article)
        #      results.append(result)
        return results


@app.post("/search")
async def search_query(data: RequestQuery):
    query = data.text

    async with AsyncClient() as client:
        embed_response = await client.post("http://localhost:8001/embedding", json={"text": [query]})
        embeddings = embed_response.json()["embeddings"][0]  #embeddings is a list of vectors (one per text), [0] gets the first one since we only sent one text.

        for_search = {
            "query_vector": embeddings
        }
        call_response = await client.post("http://localhost:8003/search/compare", json=for_search)

        return call_response.json()




    


