"""Embedding Manager for handling embedding model configurations."""

from typing import Dict, Any
from graphiti_core.embedder import OpenAIEmbedder, OpenAIEmbedderConfig
from loguru import logger
from ctx_miner.core.schemas import EmbeddingConfig


class EmbeddingManager:
    """Manages embedding model configurations and providers."""

    def __init__(
        self,
        config: EmbeddingConfig,
    ):
        """
        Initialize Embedding Manager.

        Args:
            provider: Embedding provider (default: "openai")
            model: Model name (default: "text-embedding-3-small")
            base_url: Base URL for API calls (optional)
            dimensions: Embedding dimensions (optional, uses model default)
            **kwargs: Additional provider-specific parameters
        """
        self.config = config
        logger.info(f"Embedding Manager initialized with config: {self.config}")

    def get_embedder_config(self):
        """
        Get embedder configuration for Graphiti.
        """
        if self.config.provider == "openai":
            return OpenAIEmbedderConfig(
                embedding_model=self.config.model,
                embedding_dim=self.config.dimensions,
                base_url=self.config.base_url,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def get_embedder_instance(self) -> Any:
        """
        Get embedder instance for Graphiti.

        Returns:
            Embedder instance for the configured provider
        """
        config = self.get_embedder_config()

        if self.config.provider == "openai":
            return OpenAIEmbedder(config=config)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def update_config(self, **kwargs):
        """
        Update embedding configuration.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            setattr(self.config, key, value)

    def get_info(self) -> Dict[str, Any]:
        """
        Get current embedding configuration info.

        Returns:
            Dict[str, Any]: Configuration details
        """
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "dimensions": self.config.dimensions,
            "base_url": self.config.base_url,
        }
