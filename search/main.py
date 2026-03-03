from fastapi import FastAPI
from httpx import AsyncClient
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel

class SearchRequest(BaseModel):
    query_vector: list[float]


app = FastAPI()

@app.post("/search/compare")
async def compare_articles(request: SearchRequest):
    async with AsyncClient() as client:
        response = await client.get("http://localhost:8002/articles")
        articles = response.json()

    

    results = []

    for article_id, article in articles.items():
        
        score = cosine_similarity([request.query_vector], [article["vector"]])[0][0]


        results.append({
            "article_id": article_id,
            "title": article["title"],
            "score": float(score)
        })

    results.sort(key=lambda x: x["score"], reverse= True)


    return{
        "top_3_matches": results[:3]
    }
