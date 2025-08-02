# ctx-miner Documentation

A powerful library for context-aware conversational AI using graph databases. ctx-miner leverages Graphiti Core and FalkorDB to build and query knowledge graphs from conversational data.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Installation

```bash
# Using uv (recommended)
uv add ctx-miner

# Or using pip
pip install ctx-miner
```

### Requirements

- Python 3.11+
- FalkorDB (Redis with graph module)
- OpenAI API key (for default LLM/embedding providers)

## Quick Start

```python
import asyncio
from ctx_miner import CtxMiner

async def main():
    # Initialize with default configuration
    miner = CtxMiner()
    
    try:
        # Initialize the miner
        await miner.initialize()
        
        # Add conversation messages
        await miner.add_message(
            content="User: What's the weather like?\nAssistant: I can help you check the weather. What's your location?",
            description="Weather inquiry conversation"
        )
        
        # Search for relevant context
        results = await miner.search_context("weather location", limit=5)
        for result in results:
            print(result['fact'])
            
    finally:
        await miner.close()

asyncio.run(main())
```

## Core Concepts

### Episodes

Episodes are the fundamental units of information in ctx-miner. Each episode represents a piece of conversation or context that can be:
- A single message
- A conversation turn
- A complete dialogue
- Structured data (JSON)

### Knowledge Graph

ctx-miner automatically:
- Extracts entities from conversations
- Identifies relationships between entities
- Builds a searchable knowledge graph
- Maintains temporal context

### Search Capabilities

- **Hybrid Search**: Combines semantic similarity and text retrieval (BM25)
- **Graph-based Reranking**: Uses graph distance for contextual relevance
- **Node Search**: Direct entity and concept search

## API Reference

### CtxMiner Class

The main class for managing conversational context.

#### Initialization

```python
CtxMiner(
    falkordb_config: Optional[Dict[str, Any]] = None,
    llm_config: Optional[Dict[str, Any]] = None,
    embedding_config: Optional[Dict[str, Any]] = None,
    group_id: str = "default",
    auto_build_indices: bool = True
)
```

**Parameters:**
- `falkordb_config`: Database configuration
- `llm_config`: Language model configuration
- `embedding_config`: Embedding model configuration
- `group_id`: Identifier for grouping conversations
- `auto_build_indices`: Whether to build database indices automatically

#### Methods

##### `async initialize()`
Initialize the CtxMiner instance and build indices.

##### `async add_message(content, name=None, description=None, episode_type=EpisodeType.message, metadata=None)`
Add a message/episode to the context graph.

**Parameters:**
- `content`: Message content (string or dictionary)
- `name`: Optional name for the episode
- `description`: Optional description
- `episode_type`: Type of episode
- `metadata`: Additional metadata

**Returns:** UUID of created episode

##### `async add_messages(messages, name_prefix="Conversation", metadata=None)`
Add multiple messages from a conversation format.

**Parameters:**
- `messages`: List of message dictionaries with 'role' and 'content' keys
- `name_prefix`: Prefix for episode names (default: "Conversation")
- `metadata`: Additional metadata to store with each episode

**Returns:** List of UUIDs of created episodes

**Example:**
```python
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
]
uuids = await miner.add_messages(messages)
```

##### `async search_context(query, limit=10, center_node_uuid=None, search_type="hybrid", include_episode_content=False)`
Search for relevant context based on query.

**Parameters:**
- `query`: Search query
- `limit`: Maximum results
- `center_node_uuid`: Optional UUID for graph-based reranking
- `search_type`: Type of search
- `include_episode_content`: Include full episode content

**Returns:** List of search results

##### `async search_nodes(query, limit=5, search_config=None)`
Search for nodes directly using advanced configuration.

##### `async get_episode(episode_uuid)`
Get a specific episode by UUID.

##### `async delete_episode(episode_uuid)`
Delete an episode by UUID.

##### `async list_episodes(limit=100, offset=0)`
List all episodes in the current group.

##### `async clear_all()`
Clear all episodes in the current group.

##### `async get_stats()`
Get statistics about the context graph.

##### `async close()`
Close all connections and cleanup resources.

### FalkorDBManager

Manages FalkorDB connections and database operations.

```python
from ctx_miner import FalkorDBManager

db_manager = FalkorDBManager(
    host="localhost",
    port=6379,
    username=None,
    password=None,
    database="ctx_miner"
)

# Check connection
connected = await db_manager.check_connection()

# List databases
databases = await db_manager.list_databases()

# Create database
await db_manager.create_database("new_db")
```

### LLMManager

Manages language model configurations.

```python
from ctx_miner import LLMManager

# List available providers and models
providers = LLMManager.list_providers()
models = LLMManager.list_models("openai")

# Create manager
llm_manager = LLMManager(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=1000
)

# Get configuration info
info = llm_manager.get_info()
```

### EmbeddingManager

Manages embedding model configurations.

```python
from ctx_miner import EmbeddingManager

# Create manager
embedding_manager = EmbeddingManager(
    provider="openai",
    model="text-embedding-3-small"
)

# Get model dimensions
dimensions = embedding_manager.get_model_dimensions()
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# FalkorDB Configuration
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=your_username
FALKORDB_PASSWORD=your_password
FALKORDB_DATABASE=ctx_miner

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
OPENAI_API_KEY=your_openai_api_key

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
```

### Using Configuration Helper

```python
from ctx_miner.utils.helpers import load_config_from_env

config = load_config_from_env()
miner = CtxMiner(
    falkordb_config=config["falkordb"],
    llm_config=config["llm"],
    embedding_config=config["embedding"]
)
```

### Manual Configuration

```python
miner = CtxMiner(
    falkordb_config={
        "host": "localhost",
        "port": 6379,
        "database": "my_ctx_db"
    },
    llm_config={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.1
    },
    embedding_config={
        "provider": "openai",
        "model": "text-embedding-3-large"
    }
)
```

## Examples

### Basic Conversation Management

```python
# Method 1: Add conversation turns individually
conversation = [
    "User: What are your business hours?",
    "Assistant: We're open Monday-Friday 9AM-6PM, and Saturday 10AM-4PM.",
    "User: Are you open on holidays?",
    "Assistant: We're closed on major holidays, but open with reduced hours on some minor holidays."
]

for i, turn in enumerate(conversation):
    await miner.add_message(
        content=turn,
        name=f"BusinessHours_Turn_{i+1}"
    )

# Method 2: Add messages using conversation format (recommended)
messages = [
    {"role": "user", "content": "What are your business hours?"},
    {"role": "assistant", "content": "We're open Monday-Friday 9AM-6PM, and Saturday 10AM-4PM."},
    {"role": "user", "content": "Are you open on holidays?"},
    {"role": "assistant", "content": "We're closed on major holidays, but open with reduced hours on some minor holidays."}
]

uuids = await miner.add_messages(messages, name_prefix="BusinessHours")

# Search for business hours
results = await miner.search_context("holidays open hours")
```

### Multi-topic Conversations

```python
# Using conversation format with metadata
pricing_conversation = [
    {"role": "user", "content": "What pricing plans do you offer?"},
    {"role": "assistant", "content": "We have three main plans: Basic ($29/month), Standard ($49/month), and Premium ($79/month)."}
]

support_conversation = [
    {"role": "user", "content": "My internet connection keeps dropping"},
    {"role": "assistant", "content": "I'm sorry to hear about the connection issues. Let me help you troubleshoot this problem."}
]

# Add conversations with different metadata
await miner.add_messages(
    pricing_conversation,
    name_prefix="Pricing",
    metadata={"topic": "pricing", "intent": "inquiry"}
)

await miner.add_messages(
    support_conversation,
    name_prefix="TechSupport",
    metadata={"topic": "support", "priority": "high"}
)

# Topic-specific search
pricing_results = await miner.search_context("pricing plans")
support_results = await miner.search_context("technical issue")
```

### Advanced Search with Reranking

```python
# Initial search
results = await miner.search_context("product features", limit=10)

if results:
    # Use top result as center for reranking
    center_uuid = results[0]["source_node_uuid"]
    
    # Rerank based on graph distance
    reranked = await miner.search_context(
        "advanced features",
        center_node_uuid=center_uuid,
        limit=5
    )
```

### Node-based Search

```python
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

# Search for specific entities
node_results = await miner.search_nodes(
    "customer service agent",
    limit=10
)

# Custom search configuration
custom_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
custom_config.limit = 20
custom_config.include_metadata = True

advanced_results = await miner.search_nodes(
    "technical documentation",
    search_config=custom_config
)
```

## Best Practices

### 1. Episode Organization

- Use descriptive names for episodes
- Add meaningful descriptions for complex conversations
- Use metadata to categorize and filter content
- Group related conversations using group_id

### 2. Search Optimization

- Use specific, descriptive search queries
- Leverage center_node_uuid for contextual searches
- Adjust limit based on your needs
- Consider using node search for entity-focused queries

### 3. Performance

- Close connections properly using `async with` or `finally` blocks
- Batch episode additions when possible
- Use appropriate search limits
- Consider caching frequently accessed results

### 4. Error Handling

```python
try:
    await miner.initialize()
    # Your operations
except ConnectionError:
    print("Failed to connect to database")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    await miner.close()
```

### 5. Production Deployment

- Use environment variables for sensitive configuration
- Enable logging for debugging
- Monitor database performance
- Implement connection pooling for high-traffic applications
- Regular backup of FalkorDB data

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify FalkorDB is running
   - Check host/port configuration
   - Ensure authentication credentials are correct

2. **API Key Errors**
   - Set OPENAI_API_KEY environment variable
   - Verify API key is valid and has sufficient credits

3. **Search Returns No Results**
   - Ensure episodes are added to the correct group_id
   - Try broader search terms
   - Verify indices are built (auto_build_indices=True)

4. **Performance Issues**
   - Reduce search result limits
   - Use more specific search queries
   - Consider upgrading FalkorDB resources

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.