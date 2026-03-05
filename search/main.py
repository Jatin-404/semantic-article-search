from fastapi import FastAPI
from httpx import AsyncClient
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path                                    #  used this instead of jsut loadenv 
                                                            #  bcz my env files are in apps folder not in
env_path = Path(__file__).resolve().parent / ".env"         # root dir so whule running from root dir
load_dotenv(dotenv_path=env_path)                           # it searches for env in root dir and this fixes this prob
from shared.logger import setup_logger

logger = setup_logger("search")



STORE_URL = os.getenv("STORE_URL")


class SearchRequest(BaseModel):
    query_vector: list[float]


app = FastAPI()

@app.post("/search/compare")
async def compare_articles(request: SearchRequest):
    async with AsyncClient() as client:
        logger.info("search service connecting with store service")
        response = await client.get(f"{STORE_URL}/articles")
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
