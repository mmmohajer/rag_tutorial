from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KbPageCreate(BaseModel):
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)


class KbPageRead(BaseModel):
    id: int
    url: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KbChunkCreate(BaseModel):
    page_id: int = Field(ge=1)
    chunk_number: int = Field(ge=1)
    chunk_text: str


class KbChunkRead(BaseModel):
    id: int
    page_id: int
    chunk_number: int
    chunk_text: str
    created_at: datetime
    updated_at: datetime
    embedding: list[float] | None = None
    page: KbPageRead

    model_config = ConfigDict(from_attributes=True)


class RagQuery(BaseModel):
    user_message: str = Field(min_length=1)


class RagAnswer(BaseModel):
    response: str
