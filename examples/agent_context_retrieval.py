#!/usr/bin/env python3
"""
Example: Using ctx-miner to retrieve context for LLM/Agent responses.

This example demonstrates how to:
1. Store conversation history in ctx-miner
2. Retrieve relevant context based on user queries
3. Format context for LLM/Agent consumption
"""

import asyncio
from loguru import logger

from ctx_miner import CtxMiner, ContextGenerator
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage
from ctx_miner.utils.helpers import load_config


async def simulate_customer_support_agent():
    """Simulate a customer support agent using ctx-miner for context retrieval."""

    # Load configuration
    config = load_config(group_id="customer_support_history", auto_build_indices=True)

    # Initialize ctx-miner
    miner = CtxMiner(config=config)
    context_generator = ContextGenerator(miner)

    try:
        # Step 1: Store historical conversations
        logger.info("📝 Storing historical customer conversations...")

        historical_conversations = [
            # Conversation 1: Technical issue
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user", content="My internet keeps disconnecting every few minutes"
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="I understand you're experiencing frequent disconnections. Let me help you troubleshoot. First, have you tried restarting your modem?",
                    ),
                    CtxMinerMessage(
                        role="user", content="Yes, I restarted it twice but the problem persists"
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="I see. This could be a line quality issue. I'll schedule a technician visit for you. They can check your connection and replace equipment if needed.",
                    ),
                ]
            ),
            # Conversation 2: Billing inquiry
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user", content="I was charged 20 dollars extra on my last bill"
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="Let me check your billing details. I can see the extra charge is for exceeding your data limit by 10GB last month.",
                    ),
                    CtxMinerMessage(
                        role="user",
                        content="I didn't know I had a data limit. What are my options?",
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="You can upgrade to our unlimited plan for an additional 15 dollars per month, or you can monitor your usage through our mobile app to stay within the limit.",
                    ),
                ]
            ),
            # Conversation 3: Service upgrade
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user", content="I want to upgrade to a faster internet plan"
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="Great! We have several options. Our most popular upgrade is the 200 Mbps plan for 79.99 dollars per month, or the 500 Mbps plan for 99.99 dollars per month.",
                    ),
                    CtxMinerMessage(role="user", content="What's included with the 500 Mbps plan?"),
                    CtxMinerMessage(
                        role="assistant",
                        content="The 500 Mbps plan includes unlimited data, free modem rental, and access to our premium support line. Installation is free if you sign a 12-month contract.",
                    ),
                ]
            ),
        ]

        # Add all historical conversations
        await miner.add_episodes(historical_conversations)
        logger.success("✅ Historical conversations stored successfully!")

        # Step 2: Simulate new customer queries and retrieve context
        logger.info("\n🤖 Simulating customer support agent with context retrieval...\n")

        # Test queries from new customers
        test_queries = [
            "I'm having connection issues",
            "Tell me about data limits and charges",
            "What internet plans do you offer?",
            "My bill seems higher than usual",
            "I need technical support",
        ]

        for query in test_queries:
            logger.info(f"👤 Customer: {query}")

            # Retrieve relevant context
            context = await context_generator.get_context_for_query(
                query=query, limit=5, format_for_llm=True
            )

            logger.info(f"📋 Retrieved Context:\n{context}\n")

            # Simulate agent response (in real scenario, this would be sent to LLM)
            logger.info("🤖 Agent: [Would use above context to generate appropriate response]\n")
            logger.info("-" * 80 + "\n")

        # Step 3: Advanced context retrieval with node search
        logger.info("🔍 Advanced search example: Finding specific entities...")

        # Search for specific nodes (entities)
        billing_nodes = await miner.search_nodes("billing", limit=3)
        technical_nodes = await miner.search_nodes("technical", limit=3)

        logger.info(f"Found {len(billing_nodes)} billing-related entities")
        logger.info(f"Found {len(technical_nodes)} technical-related entities")

        # Step 4: Get statistics
        stats = await miner.get_stats()
        logger.info("\n📊 Context Database Stats:")
        logger.info(f"Total episodes: {stats['episode_count']}")
        logger.info(f"Group ID: {stats['group_id']}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await miner.close()


async def create_llm_prompt_with_context():
    """Example of creating an LLM prompt with retrieved context."""

    config = load_config(group_id="product_knowledge_base", auto_build_indices=True)

    miner = CtxMiner(config=config)
    context_generator = ContextGenerator(miner)

    try:
        # Store product knowledge conversations
        product_conversations = [
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="user", content="What features does the Pro plan include?"
                    ),
                    CtxMinerMessage(
                        role="assistant",
                        content="The Pro plan includes: unlimited storage, priority support, advanced analytics, team collaboration tools, and API access.",
                    ),
                ]
            ),
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(role="user", content="How much does the Pro plan cost?"),
                    CtxMinerMessage(
                        role="assistant",
                        content="The Pro plan is 49 dollars per month when billed monthly, or 39 dollars per month when billed annually (saving you 120 dollars per year).",
                    ),
                ]
            ),
        ]

        await miner.add_episodes(product_conversations)

        # New customer query
        customer_query = "I'm interested in upgrading my account. What do I get with Pro?"

        # Retrieve context
        context = await context_generator.get_context_for_query(
            query=customer_query, limit=5, format_for_llm=True
        )

        # Create LLM prompt with context
        llm_prompt = f"""You are a helpful customer support agent. Use the following context to answer the customer's question.

{context}

Customer Question: {customer_query}

Please provide a helpful and accurate response based on the context provided."""

        logger.info("📝 Generated LLM Prompt:")
        logger.info(llm_prompt)
        logger.info(
            "\n💡 This prompt can now be sent to any LLM (OpenAI, Claude, etc.) for response generation"
        )

    finally:
        await miner.close()


async def main():
    """Run all examples."""
    logger.info("🚀 Starting ctx-miner Agent Context Retrieval Examples\n")

    # Example 1: Customer support agent simulation
    await simulate_customer_support_agent()

    # Example 2: Creating LLM prompts with context
    logger.info("\n" + "=" * 80 + "\n")
    await create_llm_prompt_with_context()

    logger.success("\n✅ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
