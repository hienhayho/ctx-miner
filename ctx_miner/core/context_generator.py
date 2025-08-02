from typing import List, Dict, Any

from ctx_miner.core.ctx_miner import CtxMiner


class ContextGenerator:
    """Manager for handling conversation context retrieval for LLMs/Agents."""

    def __init__(self, miner: CtxMiner):
        self.miner = miner

    async def format_context_for_llm(
        self, search_results: List[Dict[str, Any]], max_contexts: int = 5
    ) -> str:
        """
        Format search results into a context string for LLM consumption.

        Args:
            search_results: Raw search results from ctx-miner
            max_contexts: Maximum number of contexts to include

        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant context found."

        context_parts = ["Relevant conversation context:"]

        # Take only the most relevant results
        for i, result in enumerate(search_results[:max_contexts], 1):
            fact = result.get("fact", "")
            created_at = result.get("created_at", "")

            # Format each context item
            context_parts.append(f"\n{i}. {fact}")
            if created_at:
                context_parts.append(f"   (From: {created_at})")

        return "\n".join(context_parts)

    async def get_context_for_query(
        self, query: str, limit: int = 10, format_for_llm: bool = True
    ) -> str:
        """
        Retrieve relevant context for a given query.

        Args:
            query: The user's query or topic
            limit: Maximum number of results to retrieve
            format_for_llm: Whether to format results for LLM consumption

        Returns:
            Context string ready for LLM/Agent use
        """
        # Search for relevant context
        results = await self.miner.search_context(query=query, limit=limit)

        if format_for_llm:
            return await self.format_context_for_llm(results)
        else:
            # Return raw results for custom processing
            return str(results)
