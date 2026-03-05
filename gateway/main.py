from fastapi import FastAPI, BackgroundTasks
import uuid
from pydantic import BaseModel
from httpx import AsyncClient
import asyncio


jobs = {}


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

async def ingest_one(data: RequestArticle, job_id: str):
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
    
async def process_articles(data: list[RequestArticle], job_id: str):
    jobs[job_id] = {"status":"processing"}
    tasks = [ingest_one(article, job_id=job_id) for article in data]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # results = []
    # for article in data:
    #      result = await ingest_one(article)
    #      results.append(result)
    jobs[job_id] = {"status":"completed", "results": results}
    return results



@app.post("/articles")
async def add_article(data: list[RequestArticle], background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(process_articles, data, job_id)
    return{
        "job_id": job_id,
        "status": "request accepted"
    }

@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    if job_id not in jobs:
        return {"error":"Job id not in jobs"}

    job = jobs[job_id]

    response = {
        "job_id": job_id,
        "status": job["status"]
    }
    return response



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




    


