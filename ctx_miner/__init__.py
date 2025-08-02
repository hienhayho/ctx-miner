"""ctx-miner: A library for context-aware conversational AI using graph databases."""

from ctx_miner.core.ctx_miner import CtxMiner
from ctx_miner.managers.falkordb_manager import FalkorDBManager
from ctx_miner.managers.llm_manager import LLMManager
from ctx_miner.managers.embedding_manager import EmbeddingManager
from ctx_miner.core.context_generator import ContextGenerator
from ctx_miner.utils.logger import setup_logger

__version__ = "0.1.0"
__all__ = [
    "CtxMiner",
    "FalkorDBManager",
    "LLMManager",
    "EmbeddingManager",
    "setup_logger",
    "ContextGenerator",
]
