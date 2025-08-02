# 🔍 ctx-miner

🚀 A Python library for context-aware conversational AI using graph databases. Built on top of [Graphiti Core](https://github.com/getzep/graphiti), ctx-miner provides an easy-to-use interface for storing, retrieving, and analyzing conversational context using graph-based knowledge representation.

## ✨ Features

- 🕸️ **Graph-based Context Storage**: Store conversations as interconnected knowledge graphs
- 🔎 **Semantic Search**: Find relevant context using hybrid search (semantic + BM25)
- 🤖 **Multiple LLM Support**: Configurable LLM providers (OpenAI, etc.)
- 🧮 **Flexible Embedding Models**: Support for various embedding providers
- 🗄️ **FalkorDB Integration**: Redis-based graph database backend
- ⚡ **Async/Await Support**: Built for high-performance async applications
- 🔒 **Type Safety**: Full type hints and Pydantic models

## 📦 Installation

### 🔧 Using uv (Recommended)

```bash
uv add ctx-miner
```

### 🐍 Using pip

```bash
pip install ctx-miner
```

### 💻 Development Installation

```bash
git clone https://github.com/hienhayho/ctx-miner.git
cd ctx-miner
uv sync
```

## 🚀 Quick Start

### 1. 🔐 Environment Setup

Run `falkor-db` with docker:

```bash
docker run \
    -it -d \
    --restart always \
    -p 6379:6379 \
    -p 3000:3000 \
    --name falkordb \
    falkordb/falkordb:latest
```

Create a `.env` file with your configuration:

```env
OPENAI_API_KEY=your_openai_api_key
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=
FALKORDB_PASSWORD=
```

### 2. 💡 Quick Usage

```python
import asyncio
from ctx_miner import CtxMiner
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage
from ctx_miner.utils.helpers import load_config

async def main():
    # Configure the library
    config = load_config(group_id="demo_conversation", auto_build_indices=True)
    
    # Initialize CtxMiner
    miner = CtxMiner(config=config)
    
    try:
        await miner.initialize()
        # Create a conversation episode
        episode = CtxMinerEpisode(
            messages=[
                CtxMinerMessage(role="user", content="Hello! I need help with my internet plan."),
                CtxMinerMessage(role="assistant", content="Hi! I'd be happy to help you with your internet plan. What specific questions do you have?"),
                CtxMinerMessage(role="user", content="What's the fastest speed you offer?"),
                CtxMinerMessage(role="assistant", content="Our fastest plan is Super200 with 200 Mbps download speed.")
            ]
        )
        
        # Add episode to the knowledge graph
        episode_uuid = await miner.add_episode(episode)
        print(f"Added episode: {episode_uuid}")
        
        # Search for relevant context
        results = await miner.search_context(
            query="internet speed plans",
            limit=5
        )
        
        print(f"Found {len(results)} relevant contexts:")
        for result in results:
            print(f"- {result['fact']}")
        
        # Get statistics
        stats = await miner.get_stats()
        print(f"Database contains {stats['episode_count']} episodes")
        
    finally:
        await miner.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## ⚙️ Configuration

### 🎛️ CtxMinerConfig

The main configuration object that combines all settings:

```python
from ctx_miner.core.schemas import CtxMinerConfig, FalkorDBConfig, CtxMinerLLMConfig, EmbeddingConfig

config = CtxMinerConfig(
    falkordb_config=FalkorDBConfig(
        host="localhost",
        port=6379,
        database="my_app",
        username="",  # Optional
        password=""   # Optional
    ),
    llm_config=CtxMinerLLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=8192
    ),
    embedding_config=EmbeddingConfig(
        provider="openai",
        model="text-embedding-3-small",
        dimensions=1536
    ),
    group_id="default",           # Logical grouping for conversations
    auto_build_indices=True       # Automatically create database indices
)
```

### 🌍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `FALKORDB_HOST` | FalkorDB host | localhost |
| `FALKORDB_PORT` | FalkorDB port | 6379 |
| `FALKORDB_USERNAME` | FalkorDB username | (empty) |
| `FALKORDB_PASSWORD` | FalkorDB password | (empty) |

## 📚 Core Concepts

### 📝 Episodes

Episodes are the fundamental units of conversation stored in the graph. Each episode contains a sequence of messages and gets processed to extract entities and relationships.

```python
from ctx_miner.core.schemas import CtxMinerEpisode, CtxMinerMessage

episode = CtxMinerEpisode(
    messages=[
        CtxMinerMessage(role="user", content="What are your business hours?"),
        CtxMinerMessage(role="assistant", content="We're open Monday-Friday, 9 AM to 6 PM EST.")
    ]
)
```

### 🔍 Search and Retrieval

ctx-miner provides multiple search methods:

1. **Context Search**: Find relevant facts and relationships
2. **Node Search**: Search for specific entities
3. **Graph-based Reranking**: Use graph distance for improved relevance

```python
# Basic context search
results = await miner.search_context("business hours", limit=10)

# Search with center node reranking
results = await miner.search_context(
    query="customer support",
    center_node_uuid="some-node-uuid",
    limit=5
)

# Direct node search
nodes = await miner.search_nodes("customer", limit=5)
```

## 🎯 Advanced Usage

### 📦 Batch Processing

```python
# Add multiple episodes efficiently
episodes = [
    CtxMinerEpisode(messages=[...]),
    CtxMinerEpisode(messages=[...]),
    # ... more episodes
]

uuids = await miner.add_episodes(episodes)
print(f"Added {len(uuids)} episodes")
```

### 🗂️ Episode Management

```python
# List episodes
episodes = await miner.list_episodes(limit=50, offset=0)

# Get specific episode
episode_data = await miner.get_episode(episode_uuid)

# Delete episode
success = await miner.delete_episode(episode_uuid)

# Clear all episodes in group
await miner.clear_all()
```

### 🔧 Custom Search Configuration

```python
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

# Use custom search configuration
custom_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
custom_config.limit = 20

results = await miner.search_nodes(
    query="customer preferences",
    search_config=custom_config
)
```

## 📋 Requirements

- 🐍 Python 3.8+
- 🗄️ FalkorDB instance (Redis with graph capabilities)
- 🔑 OpenAI API key (or other supported LLM provider)

## 📚 Dependencies

- 🕸️ `graphiti-core[falkordb]`: Graph-based knowledge management
- 📝 `loguru`: Structured logging
- ✅ `pydantic`: Data validation and serialization
- 📊 `tqdm`: Progress bars for batch operations
- 🔐 `python-dotenv`: Environment variable management

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 💬 Support

For issues and questions:

- 📁 Check the [examples](./examples/) directory
- 📖 Review the [documentation](./docs/)
- 🐛 Open an issue on GitHub
