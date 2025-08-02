"""Basic usage example for ctx-miner."""

import asyncio
from ctx_miner import CtxMiner
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage
from ctx_miner.utils.helpers import load_config
from ctx_miner.utils.logger import setup_logger
from loguru import logger


async def main():
    # Set up logging
    setup_logger(level="INFO")

    # Load configuration from environment
    config = load_config(group_id="demo_conversation", auto_build_indices=True)

    # Initialize CtxMiner
    miner = CtxMiner(config=config)

    try:
        # Add some conversation messages
        logger.info("Adding conversation messages...")

        episodes = [
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user",
                        content="Hi, I'm looking for a good Italian restaurant nearby.",
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="I'd be happy to help you find a great Italian restaurant! To give you the best recommendations, could you tell me which area or neighborhood you're in?",
                    ),
                ]
            ),
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user",
                        content="I'm in downtown Manhattan, near Union Square.",
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="Great! Union Square has some excellent Italian options. I highly recommend L'Artusi for modern Italian cuisine, or Joe's Pizza for authentic New York-style pizza. Would you prefer fine dining or something more casual?",
                    ),
                ]
            ),
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user",
                        content="Something casual would be perfect. What's Joe's Pizza like?",
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="Joe's Pizza is a New York institution! They serve classic thin-crust pizza with perfectly charred edges. It's usually busy but worth the wait. They also have great garlic knots. It's located on Carmine Street, about a 10-minute walk from Union Square.",
                    ),
                ]
            ),
        ]

        # Add all messages using the new add_episodes method
        episode_uuids = await miner.add_episodes(episodes, description="Restaurant Chat")
        logger.success(f"Added {len(episode_uuids)} conversation messages")

        # Search for relevant context
        logger.info("Searching for context...")

        # Basic search
        query = "Italian food recommendations"
        results = await miner.search_context(query, limit=5)
        logger.info(f"Results for '{query}':")
        for result in results:
            logger.info(f"  - {result['fact'][:80]}...")

        # Search with center node (using first result as center)
        if results:
            center_uuid = results[0]["source_node_uuid"]
            reranked_results = await miner.search_context(
                query="pizza place location", center_node_uuid=center_uuid, limit=3
            )
            logger.info("Reranked results around context node:")
            for result in reranked_results:
                logger.info(f"  - {result['fact'][:80]}...")

        # Node search
        logger.info("Searching for nodes...")
        node_results = await miner.search_nodes("restaurant", limit=3)
        for node in node_results:
            logger.info(f"  - Node: {node['name']}")
            logger.info(f"    Summary: {node['summary'][:100]}...")

        # Get statistics
        logger.info("Context graph statistics:")
        stats = await miner.get_stats()
        logger.info(f"  - Group ID: {stats['group_id']}")
        logger.info(f"  - Total episodes: {stats['episode_count']}")
        logger.info(f"  - LLM: {stats['llm']['provider']} - {stats['llm']['model']}")
        logger.info(
            f"  - Embedding: {stats['embedding']['provider']} - {stats['embedding']['model']}"
        )

        # List episodes
        logger.info("All episodes:")
        episodes = await miner.list_episodes(limit=10)
        for ep in episodes:
            logger.info(f"  - {ep['name']}: {ep['content'][:60]}...")

    finally:
        # Always close the miner
        await miner.close()
        logger.success("CtxMiner closed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
