from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.rag.schemas import KbChunkCreate, KbChunkRead, KbPageCreate, KbPageRead, RagAnswer, RagQuery
from app.rag.services import answer, create_chunk, create_page, delete_page, list_chunks, list_pages

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/pages", response_model=list[KbPageRead])
def get_pages(db: Session = Depends(get_db)) -> list[KbPageRead]:
    return list_pages(db)


@router.post("/pages", response_model=KbPageRead)
def post_page(
    payload: KbPageCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> KbPageRead:
    page, created = create_page(db, payload)
    response.status_code = 201 if created else 200
    return page


@router.delete("/pages/{page_id}", status_code=204)
def remove_page(page_id: int, db: Session = Depends(get_db)) -> None:
    delete_page(db, page_id)


@router.get("/chunks", response_model=list[KbChunkRead])
def get_chunks(db: Session = Depends(get_db)) -> list[KbChunkRead]:
    return list_chunks(db)


@router.post("/chunks", response_model=KbChunkRead, status_code=201)
def post_chunk(payload: KbChunkCreate, db: Session = Depends(get_db)) -> KbChunkRead:
    chunk = create_chunk(db, payload)
    if chunk is None:
        raise HTTPException(status_code=404, detail="page not found")
    return chunk


@router.post("/ask", response_model=RagAnswer)
def ask(payload: RagQuery, db: Session = Depends(get_db)) -> RagAnswer:
    return RagAnswer(response=answer(db, payload.user_message))
