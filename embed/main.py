from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from sentence_transformers import SentenceTransformer

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading embedding model")
    app.state.model = SentenceTransformer("BAAI/bge-large-en-v1.5", local_files_only=True)  # local_files_only used bcz i was getting some SSL error while dowloading the model, so this here helps to get the model from cache
    print("model loded")
    yield
    print("shutting down")

class EmbedRequest(BaseModel):
    text: list[str]


app = FastAPI(lifespan=lifespan)



@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "embed"
    }


@app.post("/embedding")
async def embedding(data: EmbedRequest):
    model = app.state.model
    embeddings = await run_in_threadpool(model.encode, data.text)
    return {"embeddings": embeddings.tolist()}
    



