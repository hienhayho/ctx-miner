"""LLM Manager for handling language model configurations."""

from typing import Dict, Any
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from dotenv import load_dotenv
from loguru import logger
from ctx_miner.core.schemas import CtxMinerLLMConfig

load_dotenv()


class LLMManager:
    """Manages LLM configurations and providers."""

    def __init__(
        self,
        config: CtxMinerLLMConfig,
    ):
        """
        Initialize LLM Manager.

        Args:
            provider: LLM provider (default: "openai")
            model: Model name (default: provider's default model)
            base_url: Base URL for API calls (optional)
            temperature: Temperature for generation
            max_tokens: Maximum tokens for generation
            **kwargs: Additional provider-specific parameters
        """
        self.config = config
        logger.info(f"LLM Manager initialized with config: {self.config}")

    def get_llm_config(self) -> LLMConfig:
        """
        Get LLM configuration for Graphiti.

        Returns:
            LLMConfig: Configuration object for Graphiti
        """
        return LLMConfig(
            model=self.config.model,
            base_url=self.config.base_url,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            small_model=self.config.small_model,
        )

    def get_llm_instance(self) -> Any:
        """
        Get LLM instance for Graphiti.

        Returns:
            LLM instance for the configured provider
        """
        config = self.get_llm_config()

        if self.config.provider == "openai":
            return OpenAIClient(config=config, max_tokens=self.config.max_tokens or 8192)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def update_config(self, **kwargs):
        """
        Update LLM configuration.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            setattr(self.config, key, value)

    def get_info(self) -> Dict[str, Any]:
        """
        Get current LLM configuration info.

        Returns:
            Dict[str, Any]: Configuration details
        """
        return {
            "provider": self.config.provider,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
