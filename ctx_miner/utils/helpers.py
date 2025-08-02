"""Helper utilities for ctx-miner."""

import os
from dotenv import load_dotenv
from ctx_miner.core.schemas import (
    CtxMinerConfig,
    FalkorDBConfig,
    CtxMinerLLMConfig,
    EmbeddingConfig,
    CtxMinerEpisode,
)


def load_config(group_id: str, auto_build_indices: bool) -> CtxMinerConfig:
    """
    Load configuration from environment variables.

    Returns:
        Dict[str, Dict[str, Any]]: Configuration for FalkorDB, LLM, and Embedding
    """
    load_dotenv()

    return CtxMinerConfig(
        falkordb_config=FalkorDBConfig(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            username=os.getenv("FALKORDB_USERNAME"),
            password=os.getenv("FALKORDB_PASSWORD"),
            database=os.getenv("FALKORDB_DATABASE", "ctx_miner"),
        ),
        llm_config=CtxMinerLLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "32768")),
            small_model=os.getenv("LLM_SMALL_MODEL", "gpt-4.1-nano"),
        ),
        embedding_config=EmbeddingConfig(
            provider=os.getenv("EMBEDDING_PROVIDER", "openai"),
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            base_url=os.getenv("EMBEDDING_BASE_URL"),
            dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
        ),
        group_id=group_id,
        auto_build_indices=auto_build_indices,
    )


def format_episode(episode: CtxMinerEpisode) -> str:
    """
    Format a message to be used in the CtxMiner.
    """
    result = "\n".join([f"{message.role}: {message.content}" for message in episode.messages])
    print(result)
    return result
