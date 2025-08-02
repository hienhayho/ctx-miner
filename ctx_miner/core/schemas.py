from uuid import uuid4
from typing import List
from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    provider: str | None = Field(None, description="The provider of the embedding")
    model: str | None = Field(None, description="The model of the embedding")
    base_url: str | None = Field(None, description="The base URL of the embedding")
    dimensions: int | None = Field(None, description="The dimensions of the embedding")


class FalkorDBConfig(BaseModel):
    host: str = Field(..., description="The host of the FalkorDB database")
    port: int = Field(..., description="The port of the FalkorDB database")
    username: str | None = Field(None, description="The username of the FalkorDB database")
    password: str | None = Field(None, description="The password of the FalkorDB database")
    database: str | None = Field(None, description="The database of the FalkorDB database")


class CtxMinerLLMConfig(BaseModel):
    provider: str | None = Field(None, description="The provider of the LLM")
    api_key: str | None = Field(None, description="The API key of the LLM")
    model: str | None = Field(None, description="The model of the LLM")
    base_url: str | None = Field(None, description="The base URL of the LLM")
    temperature: float | None = Field(None, description="The temperature of the LLM")
    max_tokens: int | None = Field(None, description="The maximum number of tokens of the LLM")
    small_model: str | None = Field(None, description="The small model of the LLM")


class CtxMinerConfig(BaseModel):
    falkordb_config: FalkorDBConfig = Field(
        ..., description="The configuration of the FalkorDB database"
    )
    llm_config: CtxMinerLLMConfig = Field(
        CtxMinerLLMConfig(), description="The configuration of the LLM"
    )
    embedding_config: EmbeddingConfig = Field(
        EmbeddingConfig(), description="The configuration of the embedding"
    )
    group_id: str = Field(str(uuid4()), description="The group ID of the conversation")
    auto_build_indices: bool = Field(
        True, description="Whether to auto build indices of the CtxMiner"
    )

    class Config:
        arbitrary_types_allowed = True


class CtxMinerMessage(BaseModel):
    role: str = Field(..., description="The role of the message")
    content: str = Field(..., description="The content of the message")


class CtxMinerEpisode(BaseModel):
    messages: List[CtxMinerMessage]
