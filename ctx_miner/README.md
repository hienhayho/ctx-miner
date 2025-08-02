# ctx-miner

A powerful library for context-aware conversational AI using graph databases.

## Features

- 🚀 **Graph-based Context Storage**: Automatically build knowledge graphs from conversations
- 🔍 **Advanced Search**: Hybrid search combining semantic and text retrieval
- 🧠 **Smart Context Retrieval**: Graph-based reranking for contextual relevance
- 🔧 **Flexible Configuration**: Support for multiple LLM and embedding providers
- 📊 **FalkorDB Integration**: Fast, scalable graph database backend
- 🎯 **Episode Management**: Organize conversations with metadata and grouping

## Installation

```bash
uv add ctx-miner
```

## Quick Start

```python
import asyncio
from ctx_miner import CtxMiner

async def main():
    # Initialize ctx-miner
    miner = CtxMiner()
    
    try:
        await miner.initialize()
        
        # Add conversation using message format
        messages = [
            {"role": "user", "content": "What's the weather like today?"},
            {"role": "assistant", "content": "I'd be happy to help. What's your location?"}
        ]
        
        uuids = await miner.add_messages(messages)
        
        # Search for context
        results = await miner.search_context("weather location")
        for result in results:
            print(result['fact'])
            
    finally:
        await miner.close()

asyncio.run(main())
```

## Documentation

See [DOCUMENTATION.md](../DOCUMENTATION.md) for comprehensive documentation.

## Examples

Check the `examples/` directory for:
- Basic usage
- Advanced features
- Custom provider configuration

## Requirements

- Python 3.11+
- FalkorDB
- OpenAI API key (for default configuration)

## License

MIT