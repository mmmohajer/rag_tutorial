from sqlalchemy import delete, select
from sqlalchemy.orm import Session, contains_eager

from app.providers.rag import Rag
from app.rag.constants import SYSTEM_MESSAGE
from app.rag.models import KbChunk, KbPage
from app.rag.schemas import KbChunkCreate, KbPageCreate


def list_pages(db: Session) -> list[KbPage]:
    return list(db.scalars(select(KbPage).order_by(KbPage.url)))


def create_page(db: Session, data: KbPageCreate) -> tuple[KbPage, bool]:
    existing = db.scalar(select(KbPage).where(KbPage.url == data.url))
    if existing is not None:
        return existing, False
    page = KbPage(url=data.url, title=data.title)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page, True


def delete_page(db: Session, page_id: int) -> None:
    db.execute(delete(KbPage).where(KbPage.id == page_id))
    db.commit()


def list_chunks(db: Session) -> list[KbChunk]:
    return list(
        db.scalars(
            select(KbChunk)
            .join(KbChunk.page)
            .options(contains_eager(KbChunk.page))
            .order_by(KbPage.url, KbChunk.chunk_number)
        ).unique()
    )


def create_chunk(db: Session, data: KbChunkCreate) -> KbChunk | None:
    page = db.get(KbPage, data.page_id)
    if page is None:
        return None
    chunk = KbChunk(
        page=page,
        chunk_number=data.chunk_number,
        chunk_text=data.chunk_text,
        embedding=Rag().build_embedding(data.chunk_text),
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def answer(
    db: Session,
    user_message: str,
    cosine_similarity_threshold: float = 0.3,
    limit: int = 5,
) -> str:
    rag = Rag()
    query_embedding = rag.build_embedding(user_message)
    max_distance = 1 - cosine_similarity_threshold
    chunks = db.scalars(
        select(KbChunk)
        .join(KbChunk.page)
        .options(contains_eager(KbChunk.page))
        .where(KbChunk.embedding.is_not(None))
        .where(KbChunk.embedding.cosine_distance(query_embedding) <= max_distance)
        .order_by(KbChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    ).unique().all()
    context = "\n\n".join(
        f"{chunk.page.title} ({chunk.page.url}) chunk {chunk.chunk_number}: {chunk.chunk_text}"
        for chunk in chunks
    )
    system_message = SYSTEM_MESSAGE.replace("{context}", context)
    return rag.generate_response(user_message, system_message)
