#!/usr/bin/env python3
"""
Example: Building a chatbot with persistent memory using ctx-miner.

This example shows how to:
1. Build a chatbot that remembers past conversations
2. Retrieve relevant context for each user query
3. Use context to provide personalized responses
4. Handle multi-turn conversations
"""

import asyncio
from typing import List
from datetime import datetime
from loguru import logger

# You would import your preferred LLM client here
# from openai import AsyncOpenAI

from ctx_miner import CtxMiner
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage
from ctx_miner.utils.helpers import load_config


class MemoryChatbot:
    """A chatbot that uses ctx-miner for persistent memory and context retrieval."""

    def __init__(self, user_id: str, miner: CtxMiner):
        self.user_id = user_id
        self.miner = miner
        self.current_session: List[CtxMinerMessage] = []

        # Initialize your LLM client here
        # self.llm_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def get_relevant_context(self, user_input: str, max_contexts: int = 5) -> str:
        """Retrieve relevant context from past conversations."""
        try:
            # Search for relevant past conversations
            results = await self.miner.search_context(
                query=user_input, limit=max_contexts * 2  # Get more results to filter
            )

            if not results:
                return ""

            # Format context for the LLM
            context_parts = []
            seen_facts = set()  # Avoid duplicate facts

            for result in results[:max_contexts]:
                fact = result.get("fact", "").strip()
                if fact and fact not in seen_facts:
                    seen_facts.add(fact)
                    context_parts.append(f"- {fact}")

            if context_parts:
                return "Relevant context from past conversations:\n" + "\n".join(context_parts)
            return ""

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

    async def generate_response(self, user_input: str, context: str) -> str:
        """
        Generate a response using the LLM with context.

        In a real implementation, this would call your LLM API.
        """
        # Build the prompt with context
        system_prompt = f"""You are a helpful assistant with access to conversation history.
Use the provided context to give personalized and consistent responses.
Remember previous interactions and build upon them.

{context}"""

        # Format current conversation
        conversation_history = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in self.current_session[-6:]]  # Last 3 exchanges
        )

        full_prompt = f"""{system_prompt}

Recent conversation:
{conversation_history}

User: {user_input}
Assistant:"""

        # In real implementation, you would call your LLM here:
        # response = await self.llm_client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_input}
        #     ]
        # )
        # return response.choices[0].message.content

        # For demo purposes, return a simulated response
        logger.debug(f"Generated prompt:\n{full_prompt}")
        return f"[Simulated response based on context about: {user_input}]"

    async def save_conversation_turn(self):
        """Save the current conversation turn to ctx-miner."""
        if len(self.current_session) >= 2:  # At least one exchange
            try:
                episode = CtxMinerEpisode(messages=self.current_session)
                await self.miner.add_episode(
                    episode=episode,
                    name=f"Session_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    description=f"Conversation session for user {self.user_id}",
                )
                logger.debug(f"Saved conversation turn with {len(self.current_session)} messages")
            except Exception as e:
                logger.error(f"Error saving conversation: {e}")

    async def chat(self, user_input: str) -> str:
        """
        Main chat method that handles user input and generates responses.

        Args:
            user_input: The user's message

        Returns:
            The assistant's response
        """
        # Add user message to current session
        self.current_session.append(CtxMinerMessage(role="user", content=user_input))

        # Retrieve relevant context from past conversations
        context = await self.get_relevant_context(user_input)

        if context:
            logger.info("📋 Retrieved context for response generation")

        # Generate response with context
        response = await self.generate_response(user_input, context)

        # Add assistant response to current session
        self.current_session.append(CtxMinerMessage(role="assistant", content=response))

        # Save conversation periodically (every 2 exchanges)
        if len(self.current_session) >= 4 and len(self.current_session) % 4 == 0:
            await self.save_conversation_turn()

        return response

    async def end_session(self):
        """Save any remaining conversation and close the session."""
        if self.current_session:
            await self.save_conversation_turn()
            self.current_session = []
            logger.info(f"Session ended for user {self.user_id}")


async def simulate_multi_session_chatbot():
    """Simulate a chatbot with multiple sessions showing memory persistence."""

    # Configure ctx-miner
    config = load_config(group_id="chatbot_memory_demo", auto_build_indices=True)

    miner = CtxMiner(config=config)

    try:
        # Simulate User 1 - First Session
        logger.info("👤 User1 - Session 1: Initial conversation")
        user1_bot = MemoryChatbot("user_001", miner)

        conversations = [
            "Hi! My name is Alice and I love hiking",
            "What are some good hiking trails for beginners?",
            "I prefer trails with waterfalls",
            "Thanks for the suggestions!",
        ]

        for user_input in conversations:
            logger.info(f"User: {user_input}")
            response = await user1_bot.chat(user_input)
            logger.info(f"Bot: {response}\n")

        await user1_bot.end_session()

        # Simulate User 1 - Second Session (Later)
        logger.info("\n👤 User1 - Session 2: Bot should remember Alice")
        user1_bot_new = MemoryChatbot("user_001", miner)

        # The bot should remember Alice likes hiking and waterfalls
        new_queries = [
            "Do you remember what I told you about my interests?",
            "Can you recommend more advanced trails now?",
            "What equipment do I need for longer hikes?",
        ]

        for user_input in new_queries:
            logger.info(f"User: {user_input}")
            response = await user1_bot_new.chat(user_input)
            logger.info(f"Bot: {response}\n")

        await user1_bot_new.end_session()

        # Simulate User 2 - Different User
        logger.info("\n👤 User2 - Different user with different interests")
        user2_bot = MemoryChatbot("user_002", miner)

        user2_conversations = [
            "Hello! I'm Bob and I'm interested in cooking",
            "What are some easy recipes for beginners?",
            "I especially like Italian food",
        ]

        for user_input in user2_conversations:
            logger.info(f"User: {user_input}")
            response = await user2_bot.chat(user_input)
            logger.info(f"Bot: {response}\n")

        await user2_bot.end_session()

        # Get stats
        stats = await miner.get_stats()
        logger.info(f"\n📊 Memory Stats: {stats['episode_count']} conversation episodes stored")

    finally:
        await miner.close()


async def demonstrate_context_retrieval_for_agent():
    """
    Demonstrate how to retrieve and format context for an external agent/LLM.
    This is useful when you want to use ctx-miner purely as a context provider.
    """

    config = load_config(group_id="agent_context_demo", auto_build_indices=True)

    miner = CtxMiner(config=config)

    try:
        # Store some domain-specific knowledge
        knowledge_episodes = [
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(
                        role="system",
                        content="Company policy: Refunds are available within 30 days of purchase",
                    ),
                    CtxMinerMessage(
                        role="system",
                        content="Company policy: Shipping is free for orders over $50",
                    ),
                ]
            ),
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(role="user", content="How do I return a product?"),
                    CtxMinerMessage(
                        role="assistant",
                        content="To return a product: 1) Log into your account, 2) Go to order history, 3) Click 'Return Item', 4) Print the shipping label, 5) Drop off at any post office",
                    ),
                ]
            ),
            CtxMinerEpisode(
                messages=[
                    CtxMinerMessage(role="user", content="Is express shipping available?"),
                    CtxMinerMessage(
                        role="assistant",
                        content="Yes, we offer express shipping for $15 (2-3 days) and overnight shipping for $25",
                    ),
                ]
            ),
        ]

        await miner.add_episodes(knowledge_episodes)

        # Function to get context for agent
        async def get_agent_context(query: str) -> dict:
            """Get structured context for an agent."""
            # Search for relevant information
            results = await miner.search_context(query=query, limit=5)

            # Also search for relevant nodes
            nodes = await miner.search_nodes(query=query, limit=3)

            # Format for agent consumption
            return {
                "query": query,
                "relevant_facts": [r.get("fact", "") for r in results if r.get("fact")],
                "relevant_entities": [
                    {"name": n.get("name", ""), "summary": n.get("summary", "")} for n in nodes
                ],
                "context_string": "\n".join(
                    [f"- {r.get('fact', '')}" for r in results[:3] if r.get("fact")]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        # Example queries an agent might ask
        agent_queries = [
            "What is the refund policy?",
            "How much does shipping cost?",
            "How to handle product returns?",
        ]

        logger.info("🤖 Agent Context Retrieval Examples:\n")

        for query in agent_queries:
            context = await get_agent_context(query)

            logger.info(f"Query: '{query}'")
            logger.info(f"Context String:\n{context['context_string']}")
            logger.info(f"Found {len(context['relevant_facts'])} relevant facts")
            logger.info(f"Found {len(context['relevant_entities'])} relevant entities\n")

            # This context can now be passed to any LLM/Agent
            # Example prompt construction:
            agent_prompt = f"""Answer the following question using the provided context.

Context:
{context['context_string']}

Question: {query}

Answer:"""

            logger.debug(f"Agent prompt ready for LLM:\n{agent_prompt}\n")
            logger.info("-" * 50 + "\n")

    finally:
        await miner.close()


async def main():
    """Run all chatbot examples."""
    logger.info("🚀 Starting ctx-miner Chatbot Examples\n")

    # Example 1: Multi-session chatbot with memory
    await simulate_multi_session_chatbot()

    logger.info("\n" + "=" * 80 + "\n")

    # Example 2: Context retrieval for external agents
    await demonstrate_context_retrieval_for_agent()

    logger.success("\n✅ All chatbot examples completed!")


if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO",
    )

    asyncio.run(main())
