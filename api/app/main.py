from fastapi import FastAPI

from app.rag.router import router as rag_router

app = FastAPI()
app.include_router(rag_router)


@app.get("/")
def root():
    return {"success": True}
