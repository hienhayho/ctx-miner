"""Example of using ctx-miner with conversation format messages."""

import asyncio
from ctx_miner import CtxMiner
from ctx_miner.utils.helpers import load_config
from ctx_miner.utils.logger import setup_logger
from loguru import logger
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage

group_id = "conversation_format_demo"


async def run_simple_conversation(miner: CtxMiner) -> None:
    # Example 1: Simple conversation
    logger.info("Example 1: Simple conversation format")
    logger.info("-" * 50)

    simple_conversation = [
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="What's the weather like today?"),
                CtxMinerMessage(
                    role="assistant",
                    content="I'd be happy to help you check the weather. Could you please tell me your location?",
                ),
            ],
        ),
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="I'm in San Francisco"),
                CtxMinerMessage(
                    role="assistant",
                    content="In San Francisco today, it's partly cloudy with temperatures around 65°F (18°C). There's a light breeze from the west at about 10 mph. It's a typical pleasant San Francisco day!",
                ),
            ],
        ),
    ]

    # Add the conversation
    uuids = await miner.add_episodes(simple_conversation)
    logger.success(f"Added {len(uuids)} messages")

    # Search the conversation
    results = await miner.search_context("San Francisco weather", limit=3)
    logger.info("Search results for 'San Francisco weather':")
    for result in results:
        logger.info(f"  - {result['fact'][:100]}...")


async def run_customer_service_and_check_cross_conversation_search(miner: CtxMiner) -> None:
    # Example 2: Multi-turn customer service conversation
    logger.info("Example 2: Multi-turn customer service")
    logger.info("-" * 50)

    customer_service = [
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="I'd like to upgrade my current plan"),
                CtxMinerMessage(
                    role="assistant",
                    content="I'd be happy to help you upgrade your plan! Could you tell me which plan you're currently on?",
                ),
            ],
        ),
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="I'm on the Basic 50Mbps plan"),
                CtxMinerMessage(
                    role="assistant",
                    content="Great! From the Basic 50Mbps plan, you can upgrade to: 1) Standard 100Mbps for $10 more/month, 2) Premium 200Mbps for $20 more/month, or 3) Ultra 500Mbps for $40 more/month. All upgrades include free installation.",
                ),
            ],
        ),
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="What's included with the Premium 200Mbps?"),
                CtxMinerMessage(
                    role="assistant",
                    content="The Premium 200Mbps plan includes: • 200Mbps download/upload speeds • Free WiFi 6 router • No data caps • Free antivirus software • Priority customer support • Streaming bundle discount (20% off FPT Play). Would you like to proceed with this upgrade?",
                ),
            ],
        ),
        CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="Yes, let's go with the Premium plan"),
                CtxMinerMessage(
                    role="assistant",
                    content="Excellent choice! I'll process your upgrade to Premium 200Mbps. Your new monthly rate will be $79.99 (increased from $59.99). The upgrade will be active within 24 hours, and we'll ship your new WiFi 6 router today. You'll receive a confirmation email shortly. Is there anything else I can help you with?",
                ),
            ],
        ),
    ]

    # Add with custom prefix
    cs_uuids = await miner.add_episodes(customer_service)
    logger.success(f"Added {len(cs_uuids)} customer service messages")

    # Example 3: Searching across all conversations
    logger.info("Example 3: Cross-conversation search")
    logger.info("-" * 50)

    # Search for internet/network related issues
    network_results = await miner.search_context("internet WiFi speed plan", limit=5)
    logger.info("Network-related search results:")
    for result in network_results:
        logger.info(f"  - {result['fact'][:100]}...")

    # Search for upgrade/pricing information
    pricing_results = await miner.search_context("upgrade premium price plan", limit=5)
    logger.info("Pricing/upgrade search results:")
    for result in pricing_results:
        logger.info(f"  - {result['fact'][:100]}...")

    # Get statistics
    logger.info("Conversation statistics:")
    stats = await miner.get_stats()
    logger.info(f"  - Total episodes: {stats['episode_count']}")
    logger.info(f"  - Group ID: {stats['group_id']}")

    # List recent episodes
    logger.info("Recent episodes:")
    episodes = await miner.list_episodes(limit=6)
    for ep in episodes:
        logger.info(f"  - {ep['name']}: {ep['content'][:80]}...")


async def main():
    setup_logger(level="INFO")

    config = load_config(group_id=group_id, auto_build_indices=True)
    miner = CtxMiner(config=config)

    try:
        await miner.initialize()

        await run_simple_conversation(miner)
        await run_customer_service_and_check_cross_conversation_search(miner)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await miner.close()
        logger.success("CtxMiner closed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
