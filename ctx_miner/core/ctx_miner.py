"""Main CtxMiner class for managing conversational context."""

import asyncio
from tqdm import tqdm
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType, EpisodicNode
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
from graphiti_core.search.search_config import SearchConfig
from loguru import logger

from ctx_miner.utils import format_episode
from ctx_miner.core.schemas import CtxMinerConfig, CtxMinerEpisode
from ctx_miner.managers.falkordb_manager import FalkorDBManager
from ctx_miner.managers.llm_manager import LLMManager
from ctx_miner.managers.embedding_manager import EmbeddingManager


class CtxMiner:
    """Main class for managing conversational context with graph database."""

    def __init__(
        self,
        config: CtxMinerConfig,
    ):
        """
        Initialize CtxMiner.

        Args:
            config: CtxMiner configuration
        """
        self.config = config

        # Initialize managers
        self.db_manager = FalkorDBManager(config=self.config.falkordb_config)
        self.llm_manager = LLMManager(config=self.config.llm_config)
        self.embedding_manager = EmbeddingManager(config=self.config.embedding_config)

        # Graphiti instance will be initialized on first use
        self._graphiti: Optional[Graphiti] = None
        self._initialized = False

        asyncio.create_task(self.initialize())

    async def initialize(self):
        """Initialize the CtxMiner instance and build indices if needed."""
        if self._initialized:
            return

        # Check database connection
        if not await self.db_manager.check_connection():
            raise ConnectionError("Failed to connect to FalkorDB")

        # Create database if it doesn't exist
        if not await self.db_manager.database_exists():
            logger.info(f"Creating database: {self.db_manager.config.database}")
            await self.db_manager.create_database()

        # Initialize Graphiti
        driver = self.db_manager.get_driver()
        llm = self.llm_manager.get_llm_instance()
        embedder = self.embedding_manager.get_embedder_instance()

        self._graphiti = Graphiti(graph_driver=driver, llm_client=llm, embedder=embedder)

        # Build indices if requested
        if self.config.auto_build_indices:
            try:
                await self._graphiti.build_indices_and_constraints()
                logger.info("Successfully built indices and constraints")
            except Exception as e:
                logger.warning(f"Could not build indices (might already exist): {e}")

        self._initialized = True

    async def add_episode(
        self,
        episode: CtxMinerEpisode,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Add a message/episode to the context graph.

        Args:
            episode: CtxMinerEpisode object
            description: Optional description of the episode

        Returns:
            str: UUID of the created episode
        """

        # Generate a default name if not provided
        if not name:
            name = f"Message_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Generate default description if not provided
        if not description:
            description = (
                f"Episode added on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
            )

        # Add episode to graph
        result = await self._graphiti.add_episode(
            name=name,
            episode_body=format_episode(episode),
            source=EpisodeType.message,
            source_description=description,
            reference_time=datetime.now(timezone.utc),
            group_id=self.config.group_id,
        )

        logger.info(f"Added episode: {name}")
        return result.episode.uuid

    async def add_episodes(
        self,
        episodes: List[CtxMinerEpisode],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> List[str]:
        """
        Add multiple messages from a conversation format.

        Args:
            episodes: List of CtxMinerMessage objects
            description: Optional description of the episode

        Returns:
            List[str]: List of UUIDs of created episodes

        Example:
            episodes = [
                CtxMinerEpisode(
                    messages=[
                        CtxMinerMessage(role="user", content="Hello!"),
                        CtxMinerMessage(role="assistant", content="Hi! How can I help you?"),
                    ]
                )
            ]
            uuids = await miner.add_episodes(episodes)
        """
        await self.initialize()

        uuids = []
        for i, episode in tqdm(
            enumerate(episodes), total=len(episodes), desc="Adding episodes ..."
        ):
            # Validate message format
            if not isinstance(episode, CtxMinerEpisode):
                raise ValueError(f"Episode at index {i} must be a CtxMinerEpisode object")

            # Add episode to graph
            uuid = await self.add_episode(episode, name=name, description=description)
            uuids.append(uuid)

        logger.info(f"Added {len(episodes)} episodes to conversation")
        return uuids

    async def search_context(
        self,
        query: str,
        limit: int = 10,
        center_node_uuid: Optional[str] = None,
        include_episode_content: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant context based on query.

        Args:
            query: Search query
            limit: Maximum number of results
            center_node_uuid: Optional UUID for graph-based reranking
            include_episode_content: Whether to include full episode content

        Returns:
            List[Dict[str, Any]]: Search results
        """

        # Perform search
        if center_node_uuid:
            # Search with center node reranking
            results = await self._graphiti.search(
                query=query,
                center_node_uuid=center_node_uuid,
                group_ids=[self.config.group_id],
                num_results=limit,
            )
        else:
            # Basic search
            results = await self._graphiti.search(
                query=query, group_ids=[self.config.group_id], num_results=limit
            )

        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "uuid": result.uuid,
                "fact": result.fact,
                "source_node_uuid": result.source_node_uuid,
                "target_node_uuid": result.target_node_uuid,
                "created_at": (result.created_at.isoformat() if result.created_at else None),
            }

            # Add optional fields if they exist
            if hasattr(result, "valid_at") and result.valid_at:
                formatted_result["valid_at"] = result.valid_at.isoformat()
            if hasattr(result, "invalid_at") and result.invalid_at:
                formatted_result["invalid_at"] = result.invalid_at.isoformat()

            # Include episode content if requested
            if include_episode_content and hasattr(result, "episodes"):
                formatted_result["episodes"] = [
                    {
                        "uuid": ep.uuid,
                        "name": ep.name,
                        "content": ep.content if hasattr(ep, "content") else None,
                    }
                    for ep in result.episodes
                ]

            formatted_results.append(formatted_result)

        return formatted_results

    async def search_nodes(
        self, query: str, limit: int = 5, search_config: Optional[SearchConfig] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for nodes directly using advanced search configuration.

        Args:
            query: Search query
            limit: Maximum number of results
            search_config: Optional custom search configuration

        Returns:
            List[Dict[str, Any]]: Node search results
        """

        # Use default config if not provided
        if not search_config:
            search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
            search_config.limit = limit

        # Execute node search
        results = await self._graphiti._search(
            query=query, config=search_config, group_ids=[self.config.group_id]
        )

        # Format node results
        formatted_results = []
        for node in results.nodes:
            formatted_result = {
                "uuid": node.uuid,
                "name": node.name,
                "summary": node.summary,
                "labels": list(node.labels),
                "created_at": node.created_at.isoformat() if node.created_at else None,
            }

            if hasattr(node, "attributes") and node.attributes:
                formatted_result["attributes"] = node.attributes

            formatted_results.append(formatted_result)

        return formatted_results

    async def get_episode(self, episode_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific episode by UUID.

        Args:
            episode_uuid: UUID of the episode

        Returns:
            Optional[Dict[str, Any]]: Episode data if found
        """

        try:
            episode = await EpisodicNode.get_by_uuid(
                driver=self.db_manager.get_driver(),
                uuid=episode_uuid,
            )
            if episode:
                return {
                    "uuid": episode.uuid,
                    "name": episode.name,
                    "content": episode.content,
                    "source": episode.source,
                    "source_description": episode.source_description,
                    "created_at": (episode.created_at.isoformat() if episode.created_at else None),
                    "valid_at": (episode.valid_at.isoformat() if episode.valid_at else None),
                    "invalid_at": (episode.invalid_at.isoformat() if episode.invalid_at else None),
                }
        except Exception as e:
            logger.error(f"Error getting episode {episode_uuid}: {e}")

        return None

    async def delete_episode(self, episode_uuid: str) -> bool:
        """
        Delete an episode by UUID.

        Args:
            episode_uuid: UUID of the episode to delete

        Returns:
            bool: True if deleted successfully
        """

        try:
            await self._graphiti.remove_episode(episode_uuid)
            logger.info(f"Deleted episode: {episode_uuid}")
            return True
        except Exception as e:
            logger.error(f"Error deleting episode {episode_uuid}: {e}")
            return False

    async def list_episodes(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all episodes in the current group.

        Args:
            limit: Maximum number of episodes to return
            offset: Number of episodes to skip

        Returns:
            List[Dict[str, Any]]: List of episodes
        """

        # Get all episodes for the group
        episodes = await self._graphiti.retrieve_episodes(
            reference_time=datetime.now(timezone.utc),
            group_ids=[self.config.group_id],
            last_n=limit + offset,  # Get more to handle offset
        )

        # Apply offset manually
        episodes = episodes[offset : offset + limit] if episodes else []

        # Format episodes
        formatted_episodes = []
        for episode in episodes:
            formatted_episodes.append(
                {
                    "uuid": episode.uuid,
                    "name": episode.name,
                    "content": (
                        episode.content[:200] + "..."
                        if len(episode.content) > 200
                        else episode.content
                    ),
                    "source": episode.source,
                    "created_at": (episode.created_at.isoformat() if episode.created_at else None),
                }
            )

        return formatted_episodes

    async def clear_all(self) -> bool:
        """
        Clear all episodes in the current group.

        Returns:
            bool: True if cleared successfully
        """

        try:
            # Get all episodes
            episodes = await self._graphiti.retrieve_episodes(
                reference_time=datetime.now(timezone.utc),
                group_ids=[self.config.group_id],
                last_n=10000,  # Large number to get all episodes
            )

            # Delete each episode
            for episode in episodes:
                await self._graphiti.remove_episode(episode.uuid)

            logger.info(f"Cleared {len(episodes)} episodes from group {self.config.group_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing episodes: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current context graph.

        Returns:
            Dict[str, Any]: Statistics
        """

        try:
            # Get episode count
            episodes = await self._graphiti.retrieve_episodes(
                reference_time=datetime.now(timezone.utc),
                group_ids=[self.config.group_id],
                last_n=10000,  # Large number to get all episodes
            )

            # Get database info
            db_info = await self.db_manager.get_connection_info()

            return {
                "group_id": self.config.group_id,
                "episode_count": len(episodes),
                "database": db_info,
                "llm": self.llm_manager.get_info(),
                "embedding": self.embedding_manager.get_info(),
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e), "group_id": self.config.group_id}

    async def close(self):
        """Close all connections and cleanup resources."""
        if self._graphiti:
            await self._graphiti.close()

        await self.db_manager.close()

        self._initialized = False
        logger.info("CtxMiner closed successfully")
